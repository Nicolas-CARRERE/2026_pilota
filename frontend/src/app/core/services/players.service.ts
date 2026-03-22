import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { PlayerStatsListItem, PlayerDetail, PlayersListResponse } from '../../shared/models/player.model';

@Injectable({ providedIn: 'root' })
export class PlayersService {
  private readonly base = '/players';

  constructor(private readonly http: HttpClient) {}

  getList(limit = 50): Observable<PlayersListResponse> {
    return this.http.get<PlayersListResponse>(`${this.base}?limit=${limit}`);
  }

  getById(id: string): Observable<PlayerDetail> {
    return this.http.get<PlayerDetail>(`${this.base}/${id}`);
  }
}
