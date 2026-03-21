export interface PlayerRef {
  id: string;
  firstName: string;
  lastName: string;
  nickname?: string | null;
  license?: string | null;
}

export interface GameScoreRef {
  id: string;
  rawScore: string;
}

export interface CompetitionRef {
  id: string;
  status?: string;
  phase?: string | null;
  organizer?: { id: string; name: string; shortName?: string | null };
  discipline?: { id: string; name: string };
}

export interface GameListItem {
  id: string;
  startDate: string;
  endDate?: string | null;
  status: string;
  phase?: string | null;
  player1: PlayerRef;
  player2: PlayerRef;
  winner?: PlayerRef | null;
  competition: CompetitionRef;
  gameScores: GameScoreRef[];
  sidePlayers?: Array<{ side: number; displayOrder?: number | null; player: PlayerRef }>;
}

export interface GameDetail extends GameListItem {
  competition: CompetitionRef & { organizer?: { id: string; name: string }; discipline?: { id: string; name: string } };
  court?: { id: string; name: string; city: string } | null;
}

export interface GamesListResponse {
  games: GameListItem[];
  total: number;
  limit: number;
  offset: number;
}

export interface GamesNextResponse {
  games: GameListItem[];
}
