export interface FilterOptionRow {
  kind: string;
  value: string;
  label: string;
  parentValue?: string;
}

export interface FilterSource {
  id: string;
  name: string;
}

export interface FiltersBySource {
  source: FilterSource;
  options: FilterOptionRow[];
}

export interface FiltersResponse {
  filters: FiltersBySource[];
}
