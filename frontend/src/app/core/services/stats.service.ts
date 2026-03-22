import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface SummaryStats {
  total_games: number;
  total_players: number;
  total_clubs: number;
  total_competitions: number;
  total_disciplines: number;
}

export interface PlayerStats {
  id: string;
  first_name: string;
  last_name: string;
  nickname?: string;
  games_played: number;
  wins: number;
  losses: number;
}

export interface ClubStats {
  id: string;
  name: string;
  short_name?: string;
  games_played: number;
  wins: number;
}

export interface CompetitionStats {
  competition_id: string;
  competition_name: string;
  games_count: number;
}

export interface DisciplineStats {
  discipline_id: string;
  discipline_name: string;
  games_count: number;
}

export interface TimelineStats {
  month: string;
  games_count: number;
}

export interface StatsFilters {
  competition?: string;
  discipline?: string;
  season?: number;
  club?: string;
  player?: string;
  date_from?: string;
  date_to?: string;
  phase?: string;
}

@Injectable({ providedIn: 'root' })
export class StatsService {
  private readonly base = '/stats';

  constructor(private readonly http: HttpClient) {}

  getSummary(filters?: StatsFilters): Observable<SummaryStats> {
    const params = this.buildParams(filters);
    return this.http.get<SummaryStats>(`${this.base}/summary`, { params });
  }

  getTopPlayers(limit = 20, filters?: StatsFilters): Observable<{ players: PlayerStats[] }> {
    const params = this.buildParams(filters).set('limit', limit.toString());
    return this.http.get<{ players: PlayerStats[] }>(`${this.base}/players`, { params });
  }

  getTopClubs(limit = 20, filters?: StatsFilters): Observable<{ clubs: ClubStats[] }> {
    const params = this.buildParams(filters).set('limit', limit.toString());
    return this.http.get<{ clubs: ClubStats[] }>(`${this.base}/clubs`, { params });
  }

  getCompetitionStats(filters?: StatsFilters): Observable<{ competitions: CompetitionStats[] }> {
    const params = this.buildParams(filters);
    return this.http.get<{ competitions: CompetitionStats[] }>(`${this.base}/competitions`, { params });
  }

  getDisciplineStats(filters?: StatsFilters): Observable<{ disciplines: DisciplineStats[] }> {
    const params = this.buildParams(filters);
    return this.http.get<{ disciplines: DisciplineStats[] }>(`${this.base}/disciplines`, { params });
  }

  getTimelineStats(filters?: StatsFilters): Observable<{ timeline: TimelineStats[] }> {
    const params = this.buildParams(filters);
    return this.http.get<{ timeline: TimelineStats[] }>(`${this.base}/timeline`, { params });
  }

  private buildParams(filters?: StatsFilters): HttpParams {
    let params = new HttpParams();
    if (!filters) return params;

    if (filters.competition) params = params.set('competition', filters.competition);
    if (filters.discipline) params = params.set('discipline', filters.discipline);
    if (filters.season) params = params.set('season', filters.season.toString());
    if (filters.club) params = params.set('club', filters.club);
    if (filters.player) params = params.set('player', filters.player);
    if (filters.date_from) params = params.set('date_from', filters.date_from);
    if (filters.date_to) params = params.set('date_to', filters.date_to);
    if (filters.phase) params = params.set('phase', filters.phase);

    return params;
  }
}
