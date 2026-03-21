import { Component, OnInit } from '@angular/core';
import { RouterLink } from '@angular/router';
import { GamesService } from '../../core/services/games.service';
import { GameListItem } from '../../shared/models/game.model';
import { formatGameVersus } from '../../shared/utils/game-format';
import { FormatDatePipe } from '../../shared/pipes/format-date.pipe';
import { LoadingComponent } from '../../shared/components/loading/loading.component';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [RouterLink, FormatDatePipe, LoadingComponent],
  templateUrl: './home.component.html',
  styleUrl: './home.component.scss',
})
export class HomeComponent implements OnInit {
  nextGames: GameListItem[] = [];
  loading = true;
  error: string | null = null;

  constructor(private gamesService: GamesService) {}

  ngOnInit(): void {
    this.gamesService.getNext().subscribe({
      next: (res) => {
        this.nextGames = res.games ?? [];
        this.loading = false;
      },
      error: (err) => {
        this.error = err?.message ?? 'Erreur lors du chargement';
        this.loading = false;
      },
    });
  }

  formatVersus(game: GameListItem): string {
    return formatGameVersus(game);
  }

  scoreDisplay(scores: Array<{ rawScore: string }>): string {
    if (!scores?.length) return '–';
    return scores.map((s) => s.rawScore).join(', ');
  }
}
