import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import {
  CompetitionDetail,
  CompetitionsListResponse,
} from '../../shared/models/competition.model';

export interface CompetitionsListParams {
  disciplineId?: string;
  organizerId?: string;
  status?: string;
  year?: number;
  limit?: number;
  offset?: number;
}

@Injectable({ providedIn: 'root' })
export class CompetitionsService {
  private readonly base = '/competitions';

  constructor(private readonly http: HttpClient) {}

  getList(
    params: CompetitionsListParams = {},
  ): Observable<CompetitionsListResponse> {
    let httpParams = new HttpParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== '' && value !== null) {
        httpParams = httpParams.set(key, String(value));
      }
    });
    return this.http.get<CompetitionsListResponse>(this.base, {
      params: httpParams,
    });
  }

  getById(id: string): Observable<CompetitionDetail> {
    return this.http.get<CompetitionDetail>(`${this.base}/${id}`);
  }
}
