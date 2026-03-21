export interface PlayerLike {
  firstName: string;
  lastName: string;
  nickname?: string | null;
}

/** Minimal game shape for versus formatting (e.g. list items, recentGames). */
export interface GameLike {
  player1: PlayerLike;
  player2: PlayerLike;
  sidePlayers?: Array<{ side: number; displayOrder?: number | null; player: PlayerLike }>;
}

/**
 * Returns display name for a player (nickname if set, otherwise "FirstName LastName").
 */
export function playerDisplayName(p: PlayerLike): string {
  return (p.nickname?.trim()) ? p.nickname.trim() : `${p.firstName} ${p.lastName}`;
}

export interface GameSidesLabels {
  side1: string;
  side2: string;
}

/**
 * Formats a game as two side labels (for 2v2: "A - B" and "C - D").
 * Uses sidePlayers when present, otherwise falls back to player1 vs player2.
 */
export function formatGameSides(game: GameLike): GameSidesLabels {
  const side1Parts: string[] = [];
  const side2Parts: string[] = [];
  if (game.sidePlayers && game.sidePlayers.length > 0) {
    const list1 = game.sidePlayers.filter((sp) => sp.side === 1).sort((a, b) => (a.displayOrder ?? 0) - (b.displayOrder ?? 0));
    const list2 = game.sidePlayers.filter((sp) => sp.side === 2).sort((a, b) => (a.displayOrder ?? 0) - (b.displayOrder ?? 0));
    list1.forEach((sp) => side1Parts.push(playerDisplayName(sp.player)));
    list2.forEach((sp) => side2Parts.push(playerDisplayName(sp.player)));
  }
  if (side1Parts.length === 0) side1Parts.push(playerDisplayName(game.player1));
  if (side2Parts.length === 0) side2Parts.push(playerDisplayName(game.player2));
  return {
    side1: side1Parts.join(' - '),
    side2: side2Parts.join(' - '),
  };
}

/**
 * Returns a single string "Side1 – Side2" for list display.
 */
export function formatGameVersus(game: GameLike): string {
  const { side1, side2 } = formatGameSides(game);
  return `${side1} – ${side2}`;
}
