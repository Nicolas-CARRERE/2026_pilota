export interface TeamClub {
  id: string;
  name: string;
  shortName?: string | null;
}

export interface TeamDiscipline {
  id: string;
  name: string;
}

export interface TeamPlayerRef {
  id: string;
  firstName: string;
  lastName: string;
  nickname?: string | null;
  license?: string | null;
}

export interface TeamListItem {
  id: string;
  name: string;
  shortName?: string | null;
  number?: number | null;
  club?: TeamClub | null;
  discipline: TeamDiscipline;
  _count?: { teamPlayers: number };
}

export interface TeamsListResponse {
  teams: TeamListItem[];
  total: number;
  limit: number;
  offset: number;
}

export interface TeamDetail extends TeamListItem {
  teamPlayers: Array<{ player: TeamPlayerRef; role?: string | null }>;
  recentGames?: Array<{
    id: string;
    startDate: string;
    phase?: string | null;
    player1: { id: string; firstName: string; lastName: string; nickname?: string | null };
    player2: { id: string; firstName: string; lastName: string; nickname?: string | null };
    winner?: { id: string } | null;
    /** True if the team won this game (winner is one of the team's players). */
    won?: boolean;
    competition?: { id: string; phase?: string | null };
    gameScores: Array<{ id: string; rawScore: string }>;
    sidePlayers?: Array<{ side: number; displayOrder?: number | null; player: { id: string; firstName: string; lastName: string; nickname?: string | null } }>;
  }>;
}
