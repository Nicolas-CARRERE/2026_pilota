import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import {
  TeamDetail,
  TeamsListResponse,
} from '../../shared/models/team.model';

export interface TeamsListParams {
  clubId?: string;
  disciplineId?: string;
  limit?: number;
  offset?: number;
}

@Injectable({ providedIn: 'root' })
export class TeamsService {
  private readonly base = '/teams';

  constructor(private http: HttpClient) {}

  getList(params: TeamsListParams = {}): Observable<TeamsListResponse> {
    let httpParams = new HttpParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== '' && value !== null) {
        httpParams = httpParams.set(key, String(value));
      }
    });
    return this.http.get<TeamsListResponse>(this.base, { params: httpParams });
  }

  getById(id: string): Observable<TeamDetail> {
    return this.http.get<TeamDetail>(`${this.base}/${id}`);
  }
}
