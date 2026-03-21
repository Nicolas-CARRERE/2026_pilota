import { Pipe, PipeTransform } from '@angular/core';

/** Minimal shape for sorting by lastName then firstName (no index signature). */
type SortableByName = {
  firstName?: string | null;
  lastName?: string | null;
};

/**
 * Pure pipe: returns a new array sorted by lastName then firstName (French alphabetical).
 */
@Pipe({ name: 'orderPlayersByName', standalone: true })
export class OrderPlayersByNamePipe implements PipeTransform {
  transform<T extends SortableByName>(items: T[] | null | undefined): T[] {
    if (!items?.length) return [];
    const key = (p: T) =>
      `${(p.lastName ?? '').trim()} ${(p.firstName ?? '').trim()}`;
    return [...items].sort((a, b) =>
      key(a).localeCompare(key(b), 'fr', { sensitivity: 'base' })
    );
  }
}
