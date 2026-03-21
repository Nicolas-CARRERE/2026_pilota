/**
 * Team routes for the frontend.
 */

import { Router, Request, Response } from "express";
import { PrismaClient } from "@prisma/client";

const router = Router();
const prisma = new PrismaClient();

/**
 * GET /teams
 * List teams with pagination and optional filters.
 */
router.get("/", async (request: Request, response: Response) => {
  try {
    const {
      clubId,
      disciplineId,
      limit = "50",
      offset = "0",
    } = request.query as Record<string, string | undefined>;

    const where: Record<string, unknown> = {};
    if (clubId) where.clubId = clubId;
    if (disciplineId) where.disciplineId = disciplineId;

    const take = Math.min(100, Math.max(1, parseInt(limit, 10) || 50));
    const skip = Math.max(0, parseInt(offset, 10) || 0);

    const [teams, total] = await Promise.all([
      prisma.team.findMany({
        where,
        include: {
          club: { select: { id: true, name: true, shortName: true } },
          discipline: { select: { id: true, name: true } },
          _count: { select: { teamPlayers: true } },
        },
        orderBy: { name: "asc" },
        take,
        skip,
      }),
      prisma.team.count({ where }),
    ]);

    response.json({
      teams,
      total,
      limit: take,
      offset: skip,
    });
  } catch (error) {
    const message = error instanceof Error ? error.message : "Unknown error";
    response.status(500).json({ error: "Failed to list teams", message });
  }
});

/**
 * GET /teams/:id
 * Single team with players and recent games involving any team player.
 */
router.get("/:id", async (request: Request, response: Response) => {
  const { id } = request.params;
  try {
    const team = await prisma.team.findUnique({
      where: { id },
      include: {
        club: true,
        discipline: true,
        teamPlayers: {
          include: {
            player: {
              select: {
                id: true,
                firstName: true,
                lastName: true,
                nickname: true,
                license: true,
              },
            },
          },
        },
      },
    });
    if (!team) {
      response.status(404).json({ error: "Team not found" });
      return;
    }

    const playerIds = team.teamPlayers.map((tp) => tp.playerId);
    if (playerIds.length === 0) {
      response.json({ ...team, recentGames: [] });
      return;
    }

    const recentGamesRaw = await prisma.game.findMany({
      where: {
        OR: [
          { player1Id: { in: playerIds } },
          { player2Id: { in: playerIds } },
        ],
      },
      include: {
        player1: { select: { id: true, firstName: true, lastName: true, nickname: true } },
        player2: { select: { id: true, firstName: true, lastName: true, nickname: true } },
        winner: { select: { id: true } },
        competition: { select: { id: true, phase: true } },
        gameScores: { select: { id: true, rawScore: true } },
        sidePlayers: {
          select: {
            side: true,
            displayOrder: true,
            player: { select: { id: true, firstName: true, lastName: true, nickname: true } },
          },
          orderBy: [{ side: "asc" }, { displayOrder: "asc" }],
        },
      },
      orderBy: { startDate: "desc" },
      take: 20,
    });

    const playerIdSet = new Set(playerIds);
    const recentGames = recentGamesRaw.map((g) => ({
      ...g,
      won:
        g.winner != null && playerIdSet.has(g.winner.id),
    }));

    response.json({
      ...team,
      recentGames,
    });
  } catch (error) {
    const message = error instanceof Error ? error.message : "Unknown error";
    response.status(500).json({ error: "Failed to get team", message });
  }
});

export const teamsRouter = router;
