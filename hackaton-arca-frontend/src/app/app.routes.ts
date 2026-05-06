import { Routes } from '@angular/router';
import { Layout } from './core/layout/layout';

export const routes: Routes = [
  {
    path: '',
    component: Layout,
    children: [
      { path: 'boletas', loadComponent: () => import('./features/boletas/boletas').then(m => m.Boletas) },
      { path: 'contratos', loadComponent: () => import('./features/contratos/contratos').then(m => m.Contratos) },
      { path: 'personal', loadComponent: () => import('./features/personal/personal').then(m => m.Personal) },
      { path: 'vacaciones', loadComponent: () => import('./features/vacaciones/vacaciones').then(m => m.Vacaciones) },
      { path: '', redirectTo: 'boletas', pathMatch: 'full' },
    ],
  },
];
