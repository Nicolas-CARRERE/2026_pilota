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
import { FormsModule } from '@angular/forms';

/** Fallback phase options aligned with CTPB/FFPB when API returns none. */
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
    FormsModule,
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
  competitions: CompetitionListItem[] = [];
  players: PlayerStatsListItem[] = [];
  /** Phase options from API (distinct Game.phase) or fallback. */
  phaseOptions: { value: string; label: string }[] = [...DEFAULT_PHASE_OPTIONS];
  filters: GamesListParams = { limit: 20, offset: 0 };

  constructor(
    private gamesService: GamesService,
    private competitionsService: CompetitionsService,
    private playersService: PlayersService,
  ) {}

  ngOnInit(): void {
    this.loadFilters();
    this.loadGames();
  }

  /** Status filter options sorted by label (French). */
  readonly statusOptions: { value: string; label: string }[] = [
    { value: '', label: 'Tous' },
    { value: 'cancelled', label: 'Annulé' },
    { value: 'in_progress', label: 'En cours' },
    { value: 'scheduled', label: 'Programmé' },
    { value: 'postponed', label: 'Reporté' },
    { value: 'completed', label: 'Terminé' },
  ].sort((a, b) => (a.label === 'Tous' ? -1 : b.label === 'Tous' ? 1 : a.label.localeCompare(b.label)));

  /** Show competition as dropdown (multiple options). */
  get showCompetitionSelect(): boolean {
    return this.competitions.length > 1;
  }
  /** Single competition to show as badge when only one. */
  get singleCompetition(): CompetitionListItem | null {
    return this.competitions.length === 1 ? this.competitions[0] : null;
  }
  /** Show player as dropdown (multiple options). */
  get showPlayerSelect(): boolean {
    return this.players.length > 1;
  }
  /** Single player to show as badge when only one. */
  get singlePlayer(): PlayerStatsListItem | null {
    return this.players.length === 1 ? this.players[0] : null;
  }
  /** Show phase as dropdown (multiple options). */
  get showPhaseSelect(): boolean {
    return this.phaseOptions.length > 1;
  }
  /** Single phase to show as badge when only one (and it's not "Toutes"). */
  get singlePhase(): { value: string; label: string } | null {
    const withValues = this.phaseOptions.filter((o) => o.value !== '');
    return withValues.length === 1 ? withValues[0]! : null;
  }

  loadFilters(): void {
    this.competitionsService.getList({ limit: 200 }).subscribe((res) => {
      this.competitions = res.competitions ?? [];
    });
    this.playersService.getList(200).subscribe((res) => {
      this.players = res.players ?? [];
    });
    this.gamesService.getFilterOptions().subscribe({
      next: (res) => {
        const fromApi = res.phases ?? [];
        this.phaseOptions =
          fromApi.length > 0
            ? [{ value: '', label: 'Toutes' }, ...fromApi]
            : DEFAULT_PHASE_OPTIONS;
      },
      error: () => {
        this.phaseOptions = [...DEFAULT_PHASE_OPTIONS];
      },
    });
  }

  loadGames(): void {
    this.loading = true;
    this.error = null;
    this.gamesService.getList(this.filters).subscribe({
      next: (res) => {
        this.games = res.games ?? [];
        this.total = res.total ?? 0;
        this.limit = res.limit ?? this.limit;
        this.offset = res.offset ?? 0;
        this.loading = false;
      },
      error: (err) => {
        this.error = err?.message ?? 'Erreur lors du chargement';
        this.loading = false;
      },
    });
  }

  applyFilters(): void {
    this.filters.offset = 0;
    this.loadGames();
  }

  pagePrev(): void {
    this.offset = Math.max(0, this.offset - this.limit);
    this.filters.offset = this.offset;
    this.loadGames();
  }

  pageNext(): void {
    if (this.offset + this.limit < this.total) {
      this.offset += this.limit;
      this.filters.offset = this.offset;
      this.loadGames();
    }
  }

  formatVersus(game: GameListItem): string {
    return formatGameVersus(game);
  }

  scoreDisplay(scores: Array<{ rawScore: string }>): string {
    if (!scores?.length) return '–';
    return scores.map((s) => s.rawScore).join(', ');
  }
}
