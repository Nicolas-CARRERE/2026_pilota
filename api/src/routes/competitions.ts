/**
 * Competition (championship) routes for the frontend.
 */

import { Router, Request, Response } from "express";
import { PrismaClient } from "@prisma/client";

const router = Router();
const prisma = new PrismaClient();

/**
 * GET /competitions
 * List competitions with pagination and optional filters.
 */
router.get("/", async (request: Request, response: Response) => {
  try {
    const {
      disciplineId,
      organizerId,
      status,
      year,
      limit = "50",
      offset = "0",
    } = request.query as Record<string, string | undefined>;

    const where: Record<string, unknown> = {};
    if (disciplineId) where.disciplineId = disciplineId;
    if (organizerId) where.organizerId = organizerId;
    if (status) where.status = status;
    if (year) {
      const yearNum = parseInt(year, 10);
      if (!Number.isNaN(yearNum)) {
        const yearRow = await prisma.competitionYear.findFirst({
          where: { year: yearNum },
          select: { id: true },
        });
        if (yearRow) where.yearId = yearRow.id;
      }
    }

    const take = Math.min(100, Math.max(1, parseInt(limit, 10) || 50));
    const skip = Math.max(0, parseInt(offset, 10) || 0);

    const [competitions, total] = await Promise.all([
      prisma.competition.findMany({
        where,
        include: {
          organizer: { select: { id: true, name: true, shortName: true } },
          discipline: { select: { id: true, name: true } },
          year: { select: { id: true, year: true, isCurrent: true } },
          series: { select: { id: true, code: true, name: true } },
          _count: { select: { games: true } },
        },
        orderBy: [{ startDate: "desc" }],
        take,
        skip,
      }),
      prisma.competition.count({ where }),
    ]);

    response.json({
      competitions,
      total,
      limit: take,
      offset: skip,
    });
  } catch (error) {
    const message = error instanceof Error ? error.message : "Unknown error";
    response.status(500).json({ error: "Failed to list competitions", message });
  }
});

/**
 * GET /competitions/:id
 * Single competition with recent games.
 */
router.get("/:id", async (request: Request, response: Response) => {
  const { id } = request.params;
  try {
    const competition = await prisma.competition.findUnique({
      where: { id },
      include: {
        organizer: true,
        discipline: true,
        year: true,
        series: true,
        ageCategory: { select: { id: true, name: true } },
        gender: { select: { id: true, name: true, code: true } },
        _count: { select: { games: true } },
      },
    });
    if (!competition) {
      response.status(404).json({ error: "Competition not found" });
      return;
    }

    const recentGames = await prisma.game.findMany({
      where: { competitionId: id },
      include: {
        player1: { select: { id: true, firstName: true, lastName: true, nickname: true } },
        player2: { select: { id: true, firstName: true, lastName: true, nickname: true } },
        winner: { select: { id: true } },
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

    response.json({
      ...competition,
      recentGames,
    });
  } catch (error) {
    const message = error instanceof Error ? error.message : "Unknown error";
    response.status(500).json({ error: "Failed to get competition", message });
  }
});

export const competitionsRouter = router;
