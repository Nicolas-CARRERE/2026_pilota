import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
export interface CompetitionListItem { id: string; name: string; year?: number; discipline_id?: string; }
@Injectable({ providedIn: 'root' })
export class CompetitionsService {
  private readonly base = '/competitions';
  constructor(private readonly http: HttpClient) {}
  getList(params?: { limit?: number; offset?: number }): Observable<{ competitions: CompetitionListItem[]; total: number }> {
    let httpParams = new HttpParams();
    if (params?.limit) httpParams = httpParams.set('limit', params.limit.toString());
    if (params?.offset) httpParams = httpParams.set('offset', params.offset.toString());
    return this.http.get<{ competitions: CompetitionListItem[]; total: number }>(this.base, { params: httpParams });
  }
}
