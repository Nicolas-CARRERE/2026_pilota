import { Component, Input, OnInit } from '@angular/core';
import { StatsService, SummaryStats } from '../../../core/services/stats.service';
import { DashboardFilters } from '../../../core/services/filter.service';
import { AsyncPipe } from '@angular/common';

@Component({
  selector: 'app-stats-summary',
  standalone: true,
  imports: [AsyncPipe],
  templateUrl: './stats-summary.component.html',
  styleUrl: './stats-summary.component.scss',
})
export class StatsSummaryComponent implements OnInit {
  @Input() filters: DashboardFilters = {};
  stats: SummaryStats = {
    total_games: 0,
    total_players: 0,
    total_clubs: 0,
    total_competitions: 0,
    total_disciplines: 0,
  };
  loading = true;
  error: string | null = null;

  constructor(private statsService: StatsService) {}

  ngOnInit(): void {
    this.loadStats();
  }

  loadStats(): void {
    this.loading = true;
    this.error = null;
    this.statsService.getSummary(this.filters).subscribe({
      next: (data) => {
        this.stats = data;
        this.loading = false;
      },
      error: (err) => {
        this.error = err?.message ?? 'Erreur de chargement';
        this.loading = false;
      },
    });
  }
}
