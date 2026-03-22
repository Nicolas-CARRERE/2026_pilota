import { Component, OnInit } from '@angular/core';
import { BaseChartDirective } from 'ng2-charts';
import { ChartConfiguration, ChartData, ChartType } from 'chart.js';
import { StatsService, ClubStats } from '../../core/services/stats.service';
import { DashboardFilterService, DashboardFilters } from '../../core/services/filter.service';

@Component({
  selector: 'app-top-clubs',
  standalone: true,
  imports: [BaseChartDirective],
  templateUrl: './top-clubs.component.html',
  styleUrl: './top-clubs.component.scss',
})
export class TopClubsComponent implements OnInit {
  clubs: ClubStats[] = [];
  loading = false;

  public barChartOptions: ChartConfiguration<'bar'>['options'] = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: { callbacks: { label: (ctx) => `${ctx.parsed.y} games` } },
    },
  };

  public barChartType: ChartType = 'bar';
  public barChartData: ChartData<'bar'> = { labels: [], datasets: [{ data: [], label: 'Games Played' }] };

  constructor(private statsService: StatsService, private filterService: DashboardFilterService) {}

  ngOnInit(): void {
    this.filterService.getFilters().subscribe((filters: DashboardFilters) => this.loadClubs(filters));
  }

  loadClubs(filters: DashboardFilters): void {
    this.loading = true;
    this.statsService.getTopClubs(10, filters).subscribe({
      next: (response) => {
        this.clubs = response.clubs;
        this.barChartData.labels = response.clubs.map((c) => c.short_name || c.name);
        this.barChartData.datasets[0].data = response.clubs.map((c) => c.games_played);
        this.loading = false;
      },
      error: () => { this.loading = false; },
    });
  }
}
