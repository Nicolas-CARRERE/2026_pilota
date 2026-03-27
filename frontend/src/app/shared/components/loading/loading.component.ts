import { Component } from '@angular/core';

@Component({
  selector: 'app-loading',
  standalone: true,
  template: `
    <div class="loading-spinner" aria-live="polite">
      <div class="spinner"></div>
      <span class="loading-text">Chargement…</span>
    </div>
  `,
  styles: [`
    :host { display: block; }
    .loading-spinner {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 1rem;
      min-height: 120px;
      color: var(--pelota-gray-700);
    }
    .spinner {
      width: 24px;
      height: 24px;
      border: 3px solid var(--pelota-gray-200);
      border-top-color: var(--pelota-green);
      border-radius: 50%;
      animation: spin 0.8s linear infinite;
    }
    @keyframes spin {
      to { transform: rotate(360deg); }
    }
    .loading-text {
      font-size: 0.95rem;
    }
  `],
})
export class LoadingComponent {}
