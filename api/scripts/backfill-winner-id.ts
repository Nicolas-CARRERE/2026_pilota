/**
 * One-shot backfill: set Game.winnerId for games that have scoreComplete and
 * a rawScore but winnerId null. Uses getWinnerFromRawScore from ingest.
 *
 * Run from api dir: npx tsx scripts/backfill-winner-id.ts
 */

import { PrismaClient } from "@prisma/client";
import { getWinnerFromRawScore } from "../src/services/ingest-scraped-games";

const prisma = new PrismaClient();

async function main(): Promise<void> {
  const games = await prisma.game.findMany({
    where: {
      scoreComplete: true,
      winnerId: null,
    },
    select: {
      id: true,
      player1Id: true,
      player2Id: true,
      gameScores: {
        take: 1,
        orderBy: { id: "asc" },
        select: { rawScore: true },
      },
    },
  });

  let updated = 0;
  let skipped = 0;

  for (const game of games) {
    const rawScore = game.gameScores[0]?.rawScore;
    if (!rawScore) {
      skipped += 1;
      continue;
    }
    const winnerSide = getWinnerFromRawScore(rawScore);
    const winnerId =
      winnerSide === 1 ? game.player1Id : winnerSide === 2 ? game.player2Id : null;
    if (winnerId === null) {
      skipped += 1;
      continue;
    }
    await prisma.game.update({
      where: { id: game.id },
      data: { winnerId },
    });
    updated += 1;
  }

  console.log(`Backfill complete: ${updated} updated, ${skipped} skipped (no score or tie).`);
}

main()
  .then(() => prisma.$disconnect())
  .catch((e) => {
    console.error(e);
    prisma.$disconnect();
    process.exit(1);
  });
