import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import {
  GameDetail,
  GamesListResponse,
  GamesNextResponse,
} from '../../shared/models/game.model';

export interface GamesListParams {
  sourceId?: string;
  status?: string;
  dateFrom?: string;
  dateTo?: string;
  competitionId?: string;
  playerId?: string;
  phase?: string;
  limit?: number;
  offset?: number;
}

@Injectable({ providedIn: 'root' })
export class GamesService {
  private readonly base = '/games';

  constructor(private readonly http: HttpClient) {}

  getList(params: GamesListParams = {}): Observable<GamesListResponse> {
    let httpParams = new HttpParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== '' && value !== null) {
        httpParams = httpParams.set(key, String(value));
      }
    });
    return this.http.get<GamesListResponse>(this.base, { params: httpParams });
  }

  getNext(): Observable<GamesNextResponse> {
    return this.http.get<GamesNextResponse>(`${this.base}/next`);
  }

  getById(id: string): Observable<GameDetail> {
    return this.http.get<GameDetail>(`${this.base}/${id}`);
  }

  /** Filter options derived from data (e.g. distinct phases). For UX: hide or badge filters with 0–1 option. */
  getFilterOptions(): Observable<{
    phases: Array<{ value: string; label: string }>;
  }> {
    return this.http.get<{ phases: Array<{ value: string; label: string }> }>(
      `${this.base}/filter-options`,
    );
  }
}
