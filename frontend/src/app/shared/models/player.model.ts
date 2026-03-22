export interface PlayerStatsListItem {
  id: string;
  first_name: string;
  last_name: string;
  firstName?: string;
  lastName?: string;
  nickname?: string;
  license?: string;
  gamesPlayed?: number;
  wins?: number;
  losses?: number;
}

export interface PlayerDetail extends PlayerStatsListItem {
  bio?: string;
  birth_date?: string;
  nationality?: string;
}

export interface PlayerDetailGame {
  id: string;
  date: string;
  competition: string;
  result: string;
}
