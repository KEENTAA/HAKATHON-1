import { ChangeDetectionStrategy, Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { TableModule } from 'primeng/table';
import { ButtonModule } from 'primeng/button';
import { InputTextModule } from 'primeng/inputtext';
import { InputNumberModule } from 'primeng/inputnumber';
import { CardModule } from 'primeng/card';
import { MessageModule } from 'primeng/message';
import { VacacionesService } from '@core/services/vacaciones-service';
import { VacationBalance, VacationRequest } from '@core/models/vacation.model';

@Component({
  selector: 'arca-vacaciones',
  imports: [
    FormsModule,
    TableModule,
    ButtonModule,
    InputTextModule,
    InputNumberModule,
    CardModule,
    MessageModule,
  ],
  templateUrl: './vacaciones.html',
  styleUrl: './vacaciones.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class Vacaciones {
  private service = inject(VacacionesService);

  balance = signal<VacationBalance | null>(null);
  requests = signal<VacationRequest[]>([]);
  loading = signal(false);
  error = signal<string | null>(null);
  success = signal<string | null>(null);

  employeeId = signal<number | null>(null);

  startDate = signal('');
  endDate = signal('');
  description = signal('');

  ngOnInit() {
    this.loadBalance(1);
  }

  loadBalance(id: number) {
    this.employeeId.set(id);
    this.loading.set(true);
    this.service.getBalance(id).subscribe({
      next: (data) => {
        this.balance.set(data);
        this.loading.set(false);
      },
      error: (err) => {
        this.error.set('Error al consultar balance');
        this.loading.set(false);
      },
    });
  }

  submitRequest() {
    this.error.set(null);
    this.success.set(null);
    const id = this.employeeId();
    if (!id) return;

    this.loading.set(true);
    this.service.request({
      employee_id: id,
      start_date: this.startDate(),
      end_date: this.endDate(),
      description: this.description(),
    }).subscribe({
      next: (data) => {
        this.success.set(`Solicitud creada (ID: ${data.id}) — ${data.total_days} días`);
        this.requests.update(reqs => [...reqs, data]);
        this.loadBalance(id);
        this.loading.set(false);
      },
      error: (err) => {
        if (err.status === 403) {
          this.error.set('No ratificado: antigüedad insuficiente');
        } else {
          this.error.set('Error al solicitar vacaciones');
        }
        this.loading.set(false);
      },
    });
  }

  approveRequest(id: number) {
    this.loading.set(true);
    this.service.approve(id, 'APPROVED').subscribe({
      next: (data) => {
        this.requests.update(reqs =>
          reqs.map(r => r.id === id ? data : r)
        );
        this.success.set(`Solicitud #${id} aprobada`);
        this.loadBalance(data.employee_id);
        this.loading.set(false);
      },
      error: () => {
        this.error.set('Error al aprobar solicitud');
        this.loading.set(false);
      },
    });
  }
}
