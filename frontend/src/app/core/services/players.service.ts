import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import {
  PlayerDetail,
  PlayersListResponse,
} from '../../shared/models/player.model';

@Injectable({ providedIn: 'root' })
export class PlayersService {
  private readonly base = '/analytics/players';

  constructor(private http: HttpClient) {}

  getList(limit = 50): Observable<PlayersListResponse> {
    const params = new HttpParams().set('limit', String(limit));
    return this.http.get<PlayersListResponse>(this.base, { params });
  }

  getById(id: string): Observable<PlayerDetail> {
    return this.http.get<PlayerDetail>(`${this.base}/${id}`);
  }
}
