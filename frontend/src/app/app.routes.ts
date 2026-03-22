import { Routes } from '@angular/router';

export const routes: Routes = [
  { path: '', loadComponent: () => import('./features/home/home.component').then(m => m.HomeComponent) },
  {
    path: 'games',
    children: [
      { path: '', loadComponent: () => import('./features/games/game-list/game-list.component').then(m => m.GameListComponent) },
      { path: ':id', loadComponent: () => import('./features/games/game-detail/game-detail.component').then(m => m.GameDetailComponent) },
    ],
  },
  {
    path: 'players',
    children: [
      { path: '', loadComponent: () => import('./features/players/player-list/player-list.component').then(m => m.PlayerListComponent) },
      { path: ':id', loadComponent: () => import('./features/players/player-detail/player-detail.component').then(m => m.PlayerDetailComponent) },
    ],
  },
  {
    path: 'teams',
    children: [
      { path: '', loadComponent: () => import('./features/teams/team-list/team-list.component').then(m => m.TeamListComponent) },
      { path: ':id', loadComponent: () => import('./features/teams/team-detail/team-detail.component').then(m => m.TeamDetailComponent) },
    ],
  },
  {
    path: 'championships',
    children: [
      { path: '', loadComponent: () => import('./features/championships/championship-list/championship-list.component').then(m => m.ChampionshipListComponent) },
      { path: ':id', loadComponent: () => import('./features/championships/championship-detail/championship-detail.component').then(m => m.ChampionshipDetailComponent) },
    ],
  },
  { path: 'dashboard', loadComponent: () => import('./dashboard/dashboard.component').then(m => m.DashboardComponent) },
  { path: '**', redirectTo: '' },
];
