import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { PlayerStatsListItem, PlayerDetail } from '../../shared/models/player.model';

@Injectable({ providedIn: 'root' })
export class PlayersService {
  private readonly base = '/players';

  constructor(private readonly http: HttpClient) {}

  getList(limit = 50): Observable<{ players: PlayerStatsListItem[]; total: number }> {
    return this.http.get<{ players: PlayerStatsListItem[]; total: number }>(`${this.base}?limit=${limit}`);
  }

  getById(id: string): Observable<PlayerDetail> {
    return this.http.get<PlayerDetail>(`${this.base}/${id}`);
  }
}
