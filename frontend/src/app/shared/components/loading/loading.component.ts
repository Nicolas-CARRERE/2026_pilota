import { Component } from '@angular/core';

@Component({
  selector: 'app-loading',
  standalone: true,
  template: `<div class="loading-spinner" aria-live="polite">Chargement…</div>`,
  styles: [`:host { display: block; }`],
})
export class LoadingComponent {}
