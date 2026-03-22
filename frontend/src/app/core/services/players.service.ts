import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
export interface PlayerStatsListItem { id: string; first_name: string; last_name: string; nickname?: string; license?: string; }
@Injectable({ providedIn: 'root' })
export class PlayersService {
  private readonly base = '/players';
  constructor(private readonly http: HttpClient) {}
  getList(limit = 50): Observable<{ players: PlayerStatsListItem[]; total: number }> {
    return this.http.get<{ players: PlayerStatsListItem[]; total: number }>(`${this.base}?limit=${limit}`);
  }
}
