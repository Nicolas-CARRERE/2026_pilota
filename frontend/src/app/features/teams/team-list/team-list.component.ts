import { Component, OnInit } from '@angular/core';
import { RouterLink } from '@angular/router';
import { TeamsService } from '../../../core/services/teams.service';
import { TeamListItem } from '../../../shared/models/team.model';
import { LoadingComponent } from '../../../shared/components/loading/loading.component';
import { FilterComponent, FilterConfig } from '../../../shared/components/filter/filter.component';

@Component({
  selector: 'app-team-list',
  standalone: true,
  imports: [RouterLink, LoadingComponent, FilterComponent],
  templateUrl: './team-list.component.html',
  styleUrl: './team-list.component.scss',
})
export class TeamListComponent implements OnInit {
  teams: TeamListItem[] = [];
  total = 0;
  loading = true;
  error: string | null = null;
  filters: Record<string, any> = {};
  filterConfig: FilterConfig = { showCompetition: true, compact: true };

  constructor(private teamsService: TeamsService) {}

  ngOnInit(): void {
    this.loadTeams();
  }

  applyFilters(newFilters: Record<string, any>): void {
    this.filters = { ...this.filters, ...newFilters };
    this.loadTeams();
  }

  loadTeams(): void {
    this.loading = true;
    this.teamsService.getList({ limit: 200 }).subscribe({
      next: (res) => {
        this.teams = res.teams ?? [];
        this.total = res.total ?? 0;
        this.loading = false;
      },
      error: (err) => {
        this.error = err?.message ?? 'Erreur lors du chargement';
        this.loading = false;
      },
    });
  }
}
