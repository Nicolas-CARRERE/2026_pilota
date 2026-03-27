import { Component, Input, Output, EventEmitter, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { CompetitionsService } from '../../../core/services/competitions.service';
import { CompetitionListItem } from '../../../shared/models/competition.model';

export interface FilterOption {
  value: string;
  label: string;
}

export interface FilterConfig {
  showCompetition?: boolean;
  showDiscipline?: boolean;
  showSeason?: boolean;
  showPhase?: boolean;
  showDateRange?: boolean;
  showStatus?: boolean;
  compact?: boolean;
}

@Component({
  selector: 'app-filter',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './filter.component.html',
  styleUrl: './filter.component.scss',
})
export class FilterComponent implements OnInit {
  @Input() config: FilterConfig = {};
  @Input() filters: Record<string, any> = {};
  @Output() filtersChange = new EventEmitter<Record<string, any>>();

  competitions: CompetitionListItem[] = [];
  loading = false;

  @Input() disciplineOptions: FilterOption[] = [
    { value: '', label: 'Toutes' },
    { value: 'main-nue', label: 'Main Nue' },
    { value: 'chistera', label: 'Chistera' },
    { value: 'paleta', label: 'Paleta' },
    { value: 'gros-paleta', label: 'Gros Paleta' },
    { value: 'pala-corta', label: 'Pala Corta' },
  ];

  @Input() phaseOptions: FilterOption[] = [
    { value: '', label: 'Toutes' },
    { value: 'poules', label: 'Poules' },
    { value: 'barrage', label: 'Barrage' },
    { value: 'quart', label: '1/4 finale' },
    { value: 'demi', label: '1/2 finale' },
    { value: 'finale', label: 'Finale' },
  ];

  @Input() statusOptions: FilterOption[] = [
    { value: '', label: 'Tous' },
    { value: 'cancelled', label: 'Annulé' },
    { value: 'in_progress', label: 'En cours' },
    { value: 'scheduled', label: 'Programmé' },
    { value: 'postponed', label: 'Reporté' },
    { value: 'completed', label: 'Terminé' },
  ];

  constructor(private competitionsService: CompetitionsService) {}

  ngOnInit(): void {
    if (this.config.showCompetition) {
      this.competitionsService.getList({ limit: 200 }).subscribe({
        next: (res) => {
          this.competitions = res.competitions;
        },
      });
    }
  }

  onFilterChange(key: string, value: any): void {
    const updated = { ...this.filters, [key]: value };
    this.filtersChange.emit(updated);
  }

  resetFilters(): void {
    const reset: Record<string, any> = {};
    this.filters = reset;
    this.filtersChange.emit(reset);
  }
}
