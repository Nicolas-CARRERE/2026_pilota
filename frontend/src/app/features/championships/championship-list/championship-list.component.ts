import { Component, OnInit } from '@angular/core';
import { RouterLink } from '@angular/router';
import { CompetitionsService } from '../../../core/services/competitions.service';
import { CompetitionListItem } from '../../../shared/models/competition.model';
import { FormatDatePipe } from '../../../shared/pipes/format-date.pipe';
import { LoadingComponent } from '../../../shared/components/loading/loading.component';
import { FilterComponent, FilterConfig } from '../../../shared/components/filter/filter.component';

@Component({
  selector: 'app-championship-list',
  standalone: true,
  imports: [RouterLink, FormatDatePipe, LoadingComponent, FilterComponent],
  templateUrl: './championship-list.component.html',
  styleUrl: './championship-list.component.scss',
})
export class ChampionshipListComponent implements OnInit {
  competitions: CompetitionListItem[] = [];
  total = 0;
  loading = true;
  error: string | null = null;
  filters: Record<string, any> = {};
  filterConfig: FilterConfig = { showDiscipline: true, showSeason: true, compact: true };

  constructor(private competitionsService: CompetitionsService) {}

  ngOnInit(): void {
    this.loadCompetitions();
  }

  applyFilters(newFilters: Record<string, any>): void {
    this.filters = { ...this.filters, ...newFilters };
    this.loadCompetitions();
  }

  loadCompetitions(): void {
    this.loading = true;
    this.competitionsService.getList({ limit: 200 }).subscribe({
      next: (res) => {
        this.competitions = res.competitions ?? [];
        this.total = res.total ?? 0;
        this.loading = false;
      },
      error: (err) => {
        this.error = err?.message ?? 'Erreur lors du chargement';
        this.loading = false;
      },
    });
  }

  title(c: CompetitionListItem): string {
    const y = c.year?.year;
    const d = c.discipline?.name;
    const o = c.organizer?.name;
    const parts = [y, d, o].filter(Boolean);
    return parts.length ? parts.join(' – ') : c.id;
  }
}
