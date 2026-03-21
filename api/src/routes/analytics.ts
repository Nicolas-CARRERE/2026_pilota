/**
 * Analytics and filter routes for the frontend.
 */

import { Router, Request, Response } from "express";
import { PrismaClient } from "@prisma/client";

const router = Router();
const prisma = new PrismaClient();

type PlayerStatsMap = Record<string, { gamesPlayed: number; wins: number }>;

/**
 * Build per-player stats from games: participation (player1/player2/sidePlayers)
 * and wins (each player on winning side counts as one win).
 */
function buildPlayerStatsFromGames(
  games: Array<{
    player1Id: string;
    player2Id: string;
    winnerId: string | null;
    sidePlayers: Array<{ playerId: string; side: number }>;
  }>,
): PlayerStatsMap {
  const map: PlayerStatsMap = {};
  for (const g of games) {
    const side1 = new Set<string>([g.player1Id]);
    const side2 = new Set<string>([g.player2Id]);
    for (const sp of g.sidePlayers) {
      if (sp.side === 1) side1.add(sp.playerId);
      else if (sp.side === 2) side2.add(sp.playerId);
    }
    const participants = new Set<string>([...side1, ...side2]);
    const winningSide =
      g.winnerId === g.player1Id ? 1 : g.winnerId === g.player2Id ? 2 : null;
    const winners =
      winningSide === 1 ? side1 : winningSide === 2 ? side2 : new Set<string>();

    for (const pid of participants) {
      if (!map[pid]) map[pid] = { gamesPlayed: 0, wins: 0 };
      map[pid].gamesPlayed += 1;
      if (winners.has(pid)) map[pid].wins += 1;
    }
  }
  return map;
}

/**
 * GET /analytics/players
 * Player stats: games played, wins, losses. Participation via player1/player2/sidePlayers;
 * in 2v2, every player on the winning side gets a win.
 */
router.get("/players", async (request: Request, response: Response) => {
  try {
    const { limit = "50" } = request.query as Record<string, string>;
    const take = Math.min(100, Math.max(1, parseInt(limit, 10) || 50));

    const [players, games] = await Promise.all([
      prisma.player.findMany({
        take,
        select: {
          id: true,
          firstName: true,
          lastName: true,
          nickname: true,
        },
        orderBy: [{ lastName: "asc" }, { firstName: "asc" }],
      }),
      prisma.game.findMany({
        select: {
          player1Id: true,
          player2Id: true,
          winnerId: true,
          sidePlayers: { select: { playerId: true, side: true } },
        },
      }),
    ]);

    const statsMap = buildPlayerStatsFromGames(games);

    const list = players.map((p) => {
      const s = statsMap[p.id] ?? { gamesPlayed: 0, wins: 0 };
      return {
        id: p.id,
        firstName: p.firstName,
        lastName: p.lastName,
        nickname: p.nickname,
        gamesPlayed: s.gamesPlayed,
        wins: s.wins,
        losses: s.gamesPlayed - s.wins,
      };
    });

    response.json({ players: list });
  } catch (error) {
    const message = error instanceof Error ? error.message : "Unknown error";
    response.status(500).json({ error: "Failed to get player stats", message });
  }
});

function playerDisplayName(p: {
  firstName: string;
  lastName: string;
  nickname?: string | null;
}): string {
  return p.nickname?.trim() ? p.nickname.trim() : `${p.firstName} ${p.lastName}`;
}

/**
 * Build opponents label (other side) for a game from the perspective of the given player.
 */
function opponentsLabelForPlayer(
  game: {
    player1: { firstName: string; lastName: string; nickname?: string | null };
    player2: { firstName: string; lastName: string; nickname?: string | null };
    sidePlayers: Array<{
      side: number;
      displayOrder?: number | null;
      player: { firstName: string; lastName: string; nickname?: string | null };
    }>;
  },
  playerSide: 1 | 2,
): string {
  if (game.sidePlayers && game.sidePlayers.length > 0) {
    const other = game.sidePlayers
      .filter((sp) => sp.side === playerSide)
      .sort((a, b) => (a.displayOrder ?? 0) - (b.displayOrder ?? 0));
    const names = other.map((sp) => playerDisplayName(sp.player));
    return names.length ? names.join(" – ") : "–";
  }
  return playerSide === 1
    ? playerDisplayName(game.player1)
    : playerDisplayName(game.player2);
}

/**
 * GET /analytics/players/:id
 * Single player stats and recent games. Participation includes sidePlayers.
 * Totals use same logic as GET /analytics/players. Each recent game has won and opponentsLabel.
 */
router.get("/players/:id", async (request: Request, response: Response) => {
  const { id } = request.params;
  try {
    const [player, games] = await Promise.all([
      prisma.player.findUnique({
        where: { id },
        select: {
          id: true,
          firstName: true,
          lastName: true,
          nickname: true,
        },
      }),
      prisma.game.findMany({
        where: {
          OR: [
            { player1Id: id },
            { player2Id: id },
            { sidePlayers: { some: { playerId: id } } },
          ],
        },
        orderBy: { startDate: "desc" },
        include: {
          player1: { select: { firstName: true, lastName: true, nickname: true } },
          player2: { select: { firstName: true, lastName: true, nickname: true } },
          winner: { select: { id: true } },
          competition: { select: { id: true, phase: true } },
          gameScores: { select: { rawScore: true } },
          sidePlayers: {
            select: {
              side: true,
              displayOrder: true,
              player: {
                select: { id: true, firstName: true, lastName: true, nickname: true },
              },
            },
            orderBy: [{ side: "asc" }, { displayOrder: "asc" }],
          },
        },
      }),
    ]);

    if (!player) {
      response.status(404).json({ error: "Player not found" });
      return;
    }

    const statsMap = buildPlayerStatsFromGames(
      games.map((g) => ({
        player1Id: g.player1Id,
        player2Id: g.player2Id,
        winnerId: g.winnerId,
        sidePlayers: g.sidePlayers.map((sp) => ({
          playerId: sp.player.id,
          side: sp.side,
        })),
      })),
    );
    const stats = statsMap[id] ?? { gamesPlayed: 0, wins: 0 };

    const recentGames = games.slice(0, 15).map((g) => {
      const side1Ids = new Set<string>([g.player1Id]);
      const side2Ids = new Set<string>([g.player2Id]);
      for (const sp of g.sidePlayers) {
        if (sp.side === 1) side1Ids.add(sp.player.id);
        else if (sp.side === 2) side2Ids.add(sp.player.id);
      }
      const playerSide: 1 | 2 = side1Ids.has(id) ? 1 : 2;
      const winningSide =
        g.winnerId === g.player1Id ? 1 : g.winnerId === g.player2Id ? 2 : null;
      const won =
        winningSide !== null &&
        (winningSide === 1 ? side1Ids.has(id) : side2Ids.has(id));
      const opponentsLabel = opponentsLabelForPlayer(
        {
          player1: g.player1,
          player2: g.player2,
          sidePlayers: g.sidePlayers.map((sp) => ({
            side: sp.side,
            displayOrder: sp.displayOrder,
            player: sp.player,
          })),
        },
        playerSide === 1 ? 2 : 1,
      );

      return {
        id: g.id,
        startDate: g.startDate,
        phase: g.phase,
        competition: g.competition,
        player1: g.player1,
        player2: g.player2,
        gameScores: g.gameScores,
        sidePlayers: g.sidePlayers.map((sp) => ({
          side: sp.side,
          displayOrder: sp.displayOrder,
          player: sp.player,
        })),
        won,
        opponentsLabel,
      };
    });

    response.json({
      ...player,
      gamesPlayed: stats.gamesPlayed,
      wins: stats.wins,
      losses: stats.gamesPlayed - stats.wins,
      recentGames,
    });
  } catch (error) {
    const message = error instanceof Error ? error.message : "Unknown error";
    response.status(500).json({ error: "Failed to get player", message });
  }
});

type FilterOptionRow = {
  kind: string;
  value: string;
  label: string;
  parentValue?: string;
};

/**
 * GET /filters
 * Available filter options from ScrapedFilterOption and ScrapedSpecialty (by source).
 * Specialties are one-to-many with competition; parentValue is the competition form value.
 */
router.get("/filters", async (request: Request, response: Response) => {
  try {
    const { sourceId } = request.query as Record<string, string | undefined>;
    const where = sourceId ? { sourceId } : {};
    const [options, specialties] = await Promise.all([
      prisma.scrapedFilterOption.findMany({
        where,
        include: { source: { select: { id: true, name: true } } },
        orderBy: [{ sourceId: "asc" }, { kind: "asc" }, { label: "asc" }],
      }),
      prisma.scrapedSpecialty.findMany({
        where,
        include: {
          source: { select: { id: true, name: true } },
          competitionOption: { select: { value: true } },
        },
        orderBy: [{ sourceId: "asc" }, { label: "asc" }],
      }),
    ]);
    const bySource: Record<
      string,
      { source: { id: string; name: string }; options: FilterOptionRow[] }
    > = {};
    for (const opt of options) {
      const sid = opt.sourceId;
      if (!bySource[sid]) bySource[sid] = { source: opt.source, options: [] };
      bySource[sid].options.push({
        kind: opt.kind,
        value: opt.value,
        label: opt.label,
      });
    }
    for (const spec of specialties) {
      const sid = spec.sourceId;
      if (!bySource[sid]) bySource[sid] = { source: spec.source, options: [] };
      bySource[sid].options.push({
        kind: "specialty",
        value: spec.value,
        label: spec.label,
        parentValue: spec.competitionOption.value,
      });
    }
    response.json({ filters: Object.values(bySource) });
  } catch (error) {
    const message = error instanceof Error ? error.message : "Unknown error";
    response.status(500).json({ error: "Failed to get filters", message });
  }
});

export const analyticsRouter = router;
