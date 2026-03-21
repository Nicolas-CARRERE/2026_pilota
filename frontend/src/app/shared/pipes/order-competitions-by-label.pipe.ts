import { Pipe, PipeTransform } from '@angular/core';
import { CompetitionListItem } from '../models/competition.model';

/**
 * Pure pipe: returns competitions sorted by display label
 * "year – discipline.name (organizer.name)" for French alphabetical order.
 */
@Pipe({ name: 'orderCompetitionsByLabel', standalone: true })
export class OrderCompetitionsByLabelPipe implements PipeTransform {
  transform(
    items: CompetitionListItem[] | null | undefined
  ): CompetitionListItem[] {
    if (!items?.length) return [];
    const label = (c: CompetitionListItem) =>
      `${c.year.year} – ${c.discipline.name} (${c.organizer.name})`;
    return [...items].sort((a, b) =>
      label(a).localeCompare(label(b), 'fr', { sensitivity: 'base' })
    );
  }
}
