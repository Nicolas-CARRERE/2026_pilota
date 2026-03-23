import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { CompetitionListItem, CompetitionDetail, CompetitionsListResponse } from '../../shared/models/competition.model';

@Injectable({ providedIn: 'root' })
export class CompetitionsService {
  private readonly base = '/competitions';

  constructor(private readonly http: HttpClient) {}

  getList(params?: { limit?: number; offset?: number }): Observable<CompetitionsListResponse> {
    let httpParams = new HttpParams();
    if (params?.limit) httpParams = httpParams.set('limit', params.limit.toString());
    if (params?.offset) httpParams = httpParams.set('offset', params.offset.toString());
    return this.http.get<CompetitionsListResponse>(this.base, { params: httpParams });
  }

  getById(id: string): Observable<CompetitionDetail> {
    return this.http.get<CompetitionDetail>(`${this.base}/${id}`);
  }
}
