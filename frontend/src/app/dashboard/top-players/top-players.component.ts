import { Component, Input, OnInit } from '@angular/core';
import { StatsService, PlayerStats } from '../../../core/services/stats.service';
import { DashboardFilters } from '../../../core/services/filter.service';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-top-players',
  standalone: true,
  imports: [RouterLink],
  templateUrl: './top-players.component.html',
  styleUrl: './top-players.component.scss',
})
export class TopPlayersComponent implements OnInit {
  @Input() filters: DashboardFilters = {};
  players: PlayerStats[] = [];
  loading = true;
  error: string | null = null;

  constructor(private statsService: StatsService) {}

  ngOnInit(): void {
    this.loadPlayers();
  }

  loadPlayers(): void {
    this.loading = true;
    this.error = null;
    this.statsService.getTopPlayers(10, this.filters).subscribe({
      next: (data) => {
        this.players = data.players;
        this.loading = false;
      },
      error: (err) => {
        this.error = err?.message ?? 'Erreur de chargement';
        this.loading = false;
      },
    });
  }

  displayName(player: PlayerStats): string {
    return player.nickname || `${player.first_name} ${player.last_name}`;
  }
}
