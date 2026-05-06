import { ChangeDetectionStrategy, Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { MenubarModule } from 'primeng/menubar';
import { MenuItem } from 'primeng/api';

@Component({
  selector: 'arca-layout',
  imports: [RouterOutlet, MenubarModule],
  templateUrl: './layout.html',
  styleUrl: './layout.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class Layout {
  items: MenuItem[] = [
    { label: 'Boletas', icon: 'pi pi-file', routerLink: ['/boletas'] },
    { label: 'Contratos', icon: 'pi pi-id-card', routerLink: ['/contratos'] },
    { label: 'Personal', icon: 'pi pi-users', routerLink: ['/personal'] },
    { label: 'Vacaciones', icon: 'pi pi-sun', routerLink: ['/vacaciones'] },
  ];
}
