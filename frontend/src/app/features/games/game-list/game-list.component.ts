import { Component, OnInit } from '@angular/core';
import { RouterLink } from '@angular/router';
import { GamesService, GamesListParams } from '../../../core/services/games.service';
import { GameListItem } from '../../../shared/models/game.model';
import { formatGameVersus } from '../../../shared/utils/game-format';
import { CompetitionsService } from '../../../core/services/competitions.service';
import { PlayersService } from '../../../core/services/players.service';
import { CompetitionListItem } from '../../../shared/models/competition.model';
import { PlayerStatsListItem } from '../../../shared/models/player.model';
import { FormatDatePipe } from '../../../shared/pipes/format-date.pipe';
import { OrderCompetitionsByLabelPipe } from '../../../shared/pipes/order-competitions-by-label.pipe';
import { OrderPlayersByNamePipe } from '../../../shared/pipes/order-players-by-name.pipe';
import { LoadingComponent } from '../../../shared/components/loading/loading.component';
import { FilterComponent, FilterConfig } from '../../../shared/components/filter/filter.component';

const DEFAULT_PHASE_OPTIONS: { value: string; label: string }[] = [
  { value: '', label: 'Toutes' },
  { value: 'Poules', label: 'Poules' },
  { value: 'Barrage', label: 'Barrage' },
  { value: '1/4 finale', label: '1/4 finale' },
  { value: '1/2 finale', label: '1/2 finale' },
  { value: 'Finale', label: 'Finale' },
];

@Component({
  selector: 'app-game-list',
  standalone: true,
  imports: [
    RouterLink,
    FormatDatePipe,
    OrderCompetitionsByLabelPipe,
    OrderPlayersByNamePipe,
    LoadingComponent,
    FilterComponent,
  ],
  templateUrl: './game-list.component.html',
  styleUrl: './game-list.component.scss',
})
export class GameListComponent implements OnInit {
  games: GameListItem[] = [];
  total = 0;
  limit = 20;
  offset = 0;
  loading = true;
  error: string | null = null;
  filters: GamesListParams = { limit: 20, offset: 0 };
  filterConfig: FilterConfig = { showCompetition: true, showPhase: true, showStatus: true, compact: true };

  phaseOptions: { value: string; label: string }[] = [...DEFAULT_PHASE_OPTIONS];

  constructor(
    private gamesService: GamesService,
    private competitionsService: CompetitionsService,
    private playersService: PlayersService,
  ) {}

  ngOnInit(): void {
    this.loadGames();
  }

  readonly statusOptions: { value: string; label: string }[] = [
    { value: '', label: 'Tous' },
    { value: 'cancelled', label: 'Annulé' },
    { value: 'in_progress', label: 'En cours' },
    { value: 'scheduled', label: 'Programmé' },
    { value: 'postponed', label: 'Reporté' },
    { value: 'completed', label: 'Terminé' },
  ].sort((a, b) => (a.label === 'Tous' ? -1 : b.label === 'Tous' ? 1 : a.label.localeCompare(b.label)));

  applyFilters(newFilters: Record<string, any>): void {
    this.filters = { ...this.filters, ...newFilters };
    this.offset = 0;
    this.loadGames();
  }

  loadGames(): void {
    this.loading = true;
    this.gamesService.getList(this.filters).subscribe({
      next: (res) => {
        this.games = res.games;
        this.total = res.total;
        this.loading = false;
      },
      error: (err) => {
        this.error = err.message || 'Erreur lors du chargement';
        this.loading = false;
      },
    });
  }

  formatVersus(g: GameListItem): string {
    return formatGameVersus(g);
  }

  scoreDisplay(scores: Array<{ rawScore: string }>): string {
    if (!scores || scores.length === 0) return '';
    return scores.map((s) => s.rawScore).join(' - ');
  }

  pagePrev(): void {
    this.offset = Math.max(0, this.offset - this.limit);
    this.loadGames();
  }

  pageNext(): void {
    this.offset = this.offset + this.limit;
    this.loadGames();
  }
}
