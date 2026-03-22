import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup } from '@angular/forms';
import { DashboardFilterService, DashboardFilters } from '../../core/services/filter.service';
import { CompetitionsService } from '../../core/services/competitions.service';
import { PlayersService } from '../../core/services/players.service';
import { CompetitionListItem } from '../../shared/models/competition.model';
import { PlayerStatsListItem } from '../../shared/models/player.model';

@Component({
  selector: 'app-filter-panel',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './filter-panel.component.html',
  styleUrl: './filter-panel.component.scss',
})
export class FilterPanelComponent implements OnInit {
  filterForm: FormGroup;
  competitions: CompetitionListItem[] = [];
  players: PlayerStatsListItem[] = [];
  disciplines = [
    { id: 'main-nue', name: 'Main Nue' },
    { id: 'chistera', name: 'Chistera' },
    { id: 'paleta', name: 'Paleta' },
  ];

  constructor(
    private fb: FormBuilder,
    private filterService: DashboardFilterService,
    private competitionsService: CompetitionsService,
    private playersService: PlayersService,
  ) {
    this.filterForm = this.fb.group({
      competition: [null],
      discipline: [null],
      season: [null],
      phase: [null],
    });
  }

  ngOnInit(): void {
    this.competitionsService.getList({ limit: 200 }).subscribe({
      next: (res: { competitions: CompetitionListItem[] }) => {
        this.competitions = res.competitions;
      },
    });
    this.playersService.getList(200).subscribe({
      next: (res: { players: PlayerStatsListItem[] }) => {
        this.players = res.players;
      },
    });
  }

  applyFilters(): void {
    const filters: DashboardFilters = this.filterForm.value;
    this.filterService.updateFilters(filters);
  }

  resetFilters(): void {
    this.filterForm.reset();
    this.filterService.resetFilters();
  }
}
