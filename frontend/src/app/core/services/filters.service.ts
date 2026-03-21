import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { FiltersResponse } from '../../shared/models/filter.model';

@Injectable({ providedIn: 'root' })
export class FiltersService {
  private readonly base = '/analytics/filters';

  constructor(private readonly http: HttpClient) {}

  getFilters(sourceId?: string): Observable<FiltersResponse> {
    const params = sourceId
      ? new HttpParams().set('sourceId', sourceId)
      : undefined;
    return this.http.get<FiltersResponse>(this.base, { params });
  }
}
