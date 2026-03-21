import { Component, OnInit } from '@angular/core';
import { RouterLink } from '@angular/router';
import { PlayersService } from '../../../core/services/players.service';
import { PlayerStatsListItem } from '../../../shared/models/player.model';
import { LoadingComponent } from '../../../shared/components/loading/loading.component';

@Component({
  selector: 'app-player-list',
  standalone: true,
  imports: [RouterLink, LoadingComponent],
  templateUrl: './player-list.component.html',
  styleUrl: './player-list.component.scss',
})
export class PlayerListComponent implements OnInit {
  players: PlayerStatsListItem[] = [];
  loading = true;
  error: string | null = null;

  constructor(private playersService: PlayersService) {}

  ngOnInit(): void {
    this.playersService.getList(100).subscribe({
      next: (res) => {
        this.players = res.players ?? [];
        this.loading = false;
      },
      error: (err) => {
        this.error = err?.message ?? 'Erreur lors du chargement';
        this.loading = false;
      },
    });
  }

  displayName(p: PlayerStatsListItem): string {
    return p.nickname?.trim() ? p.nickname : `${p.firstName} ${p.lastName}`;
  }
}
