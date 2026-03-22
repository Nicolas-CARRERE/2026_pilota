import { Component, EventEmitter, Input, Output, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { DashboardFilters } from '../../core/services/filter.service';
import { CompetitionsService } from '../../core/services/competitions.service';
import { PlayersService } from '../../core/services/players.service';
import { CompetitionListItem } from '../../shared/models/competition.model';
import { PlayerStatsListItem } from '../../shared/models/player.model';

@Component({
  selector: 'app-filter-panel',
  standalone: true,
  imports: [FormsModule],
  templateUrl: './filter-panel.component.html',
  styleUrl: './filter-panel.component.scss',
})
export class FilterPanelComponent implements OnInit {
  @Input() filters: DashboardFilters = {};
  @Output() filtersChange = new EventEmitter<DashboardFilters>();

  competitions: CompetitionListItem[] = [];
  players: PlayerStatsListItem[] = [];
  phaseOptions = [
    { value: '', label: 'Toutes' },
    { value: 'Poules', label: 'Poules' },
    { value: 'Barrage', label: 'Barrage' },
    { value: '1/4 finale', label: '1/4 finale' },
    { value: '1/2 finale', label: '1/2 finale' },
    { value: 'Finale', label: 'Finale' },
  ];

  currentFilters: DashboardFilters = {};

  constructor(
    private competitionsService: CompetitionsService,
    private playersService: PlayersService,
  ) {}

  ngOnInit(): void {
    this.currentFilters = { ...this.filters };
    this.loadOptions();
  }

  loadOptions(): void {
    this.competitionsService.getList({ limit: 200 }).subscribe((res) => {
      this.competitions = res.competitions ?? [];
    });
    this.playersService.getList(200).subscribe((res) => {
      this.players = res.players ?? [];
    });
  }

  onFilterChange(key: keyof DashboardFilters, value: string | number | undefined): void {
    this.currentFilters = { ...this.currentFilters, [key]: value || undefined };
    this.filtersChange.emit(this.currentFilters);
  }

  resetFilters(): void {
    this.currentFilters = {};
    this.filtersChange.emit(this.currentFilters);
  }
}
