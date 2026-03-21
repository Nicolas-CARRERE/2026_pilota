export interface CompetitionOrganizer {
  id: string;
  name: string;
  shortName?: string | null;
}

export interface CompetitionDiscipline {
  id: string;
  name: string;
}

export interface CompetitionYear {
  id: string;
  year: number;
  isCurrent?: boolean;
}

export interface CompetitionListItem {
  id: string;
  startDate: string;
  endDate?: string | null;
  status: string;
  phase?: string | null;
  location?: string | null;
  country?: string | null;
  organizer: CompetitionOrganizer;
  discipline: CompetitionDiscipline;
  year: CompetitionYear;
  series?: { id: string; code: string; name: string } | null;
  _count?: { games: number };
}

export interface CompetitionsListResponse {
  competitions: CompetitionListItem[];
  total: number;
  limit: number;
  offset: number;
}

export interface CompetitionDetail extends CompetitionListItem {
  recentGames?: Array<{
    id: string;
    startDate: string;
    player1: { id: string; firstName: string; lastName: string; nickname?: string | null };
    player2: { id: string; firstName: string; lastName: string; nickname?: string | null };
    winner?: { id: string } | null;
    gameScores: Array<{ id: string; rawScore: string }>;
    sidePlayers?: Array<{ side: number; displayOrder?: number | null; player: { id: string; firstName: string; lastName: string; nickname?: string | null } }>;
  }>;
}
