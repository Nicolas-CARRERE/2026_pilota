export interface CompetitionListItem {
  id: string;
  name: string;
  year?: { year: number } | number;
  discipline?: { name: string } | { discipline_id: string };
  discipline_id?: string;
  organizer?: { name: string };
  status?: string;
  _count?: { games: number };
}

export interface CompetitionDetail extends CompetitionListItem {
  description?: string;
  start_date?: string;
  end_date?: string;
  location?: string;
}
