import { Component, OnInit } from '@angular/core';
import { RouterLink } from '@angular/router';
import { TeamsService } from '../../../core/services/teams.service';
import { TeamListItem } from '../../../shared/models/team.model';
import { LoadingComponent } from '../../../shared/components/loading/loading.component';

@Component({
  selector: 'app-team-list',
  standalone: true,
  imports: [RouterLink, LoadingComponent],
  templateUrl: './team-list.component.html',
  styleUrl: './team-list.component.scss',
})
export class TeamListComponent implements OnInit {
  teams: TeamListItem[] = [];
  total = 0;
  loading = true;
  error: string | null = null;

  constructor(private teamsService: TeamsService) {}

  ngOnInit(): void {
    this.teamsService.getList({ limit: 100 }).subscribe({
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
