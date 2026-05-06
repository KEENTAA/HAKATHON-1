import { ChangeDetectionStrategy, Component, inject, OnInit, signal } from '@angular/core';
import { CurrencyPipe } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { CardModule } from 'primeng/card';
import { TableModule } from 'primeng/table';
import { ButtonModule } from 'primeng/button';
import { InputTextModule } from 'primeng/inputtext';
import { DropdownModule } from 'primeng/dropdown';
import { MessageModule } from 'primeng/message';
import { DialogModule } from 'primeng/dialog';
import { TagModule } from 'primeng/tag';
import { ContratosService } from '../../core/services/contratos-service';
import {
  ContractCreate,
  ContractListResponse,
  ContractResponse,
  ContractTypeResponse,
} from '../../core/models/contract.model';

@Component({
  selector: 'arca-contratos',
  imports: [
    CurrencyPipe,
    FormsModule,
    CardModule,
    TableModule,
    ButtonModule,
    InputTextModule,
    DropdownModule,
    MessageModule,
    DialogModule,
    TagModule,
  ],
  templateUrl: './contratos.html',
  styleUrl: './contratos.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class Contratos implements OnInit {
  private svc = inject(ContratosService);

  contracts = signal<ContractListResponse[]>([]);
  tipos = signal<ContractTypeResponse[]>([]);
  selectedContract = signal<ContractResponse | null>(null);
  loading = signal(false);
  error = signal<string | null>(null);
  success = signal<string | null>(null);
  showGenDialog = signal(false);
  selectedTipo = signal<ContractTypeResponse | null>(null);

  form: ContractCreate = {
    employee_id: 0,
    contract_type_id: 0,
    salary: 0,
    start_date: '',
    end_date: '',
    job_title: '',
    department: '',
  };

  async ngOnInit() {
    await this.loadTipos();
  }

  async loadByEmployee(employeeId: number) {
    if (!employeeId) return;
    this.loading.set(true);
    this.error.set(null);
    try {
      const data = await this.svc.getByEmployee(employeeId);
      this.contracts.set(data);
    } catch (e: any) {
      this.error.set(e.message || 'Error al cargar contratos');
    } finally {
      this.loading.set(false);
    }
  }

  async loadTipos() {
    try {
      const data = await this.svc.getTipos();
      this.tipos.set(data);
    } catch {
      // Endpoint auxiliar, puede fallar sin romper la UI
    }
  }

  async viewContract(id: number) {
    this.loading.set(true);
    this.error.set(null);
    try {
      const c = await this.svc.getById(id);
      this.selectedContract.set(c);
    } catch (e: any) {
      this.error.set(e.message || 'Error al obtener contrato');
    } finally {
      this.loading.set(false);
    }
  }

  async updateStatus(id: number, status: string) {
    this.loading.set(true);
    this.error.set(null);
    try {
      await this.svc.updateStatus(id, { status });
      this.success.set(`Estado actualizado a ${status}`);
      const c = this.selectedContract();
      if (c && c.id === id) {
        c.status = status;
        this.selectedContract.set({ ...c });
      }
      this.contracts.set(this.contracts().map(x => x.id === id ? { ...x, status } : x));
    } catch (e: any) {
      this.error.set(e.message || 'Error al actualizar estado');
    } finally {
      this.loading.set(false);
    }
  }

  openGenerateDialog() {
    this.form = { employee_id: 0, contract_type_id: 0, salary: 0, start_date: '', end_date: '', job_title: '', department: '' };
    this.selectedTipo.set(null);
    this.error.set(null);
    this.showGenDialog.set(true);
  }

  async generateContract() {
    if (!this.form.contract_type_id) {
      this.error.set('Selecciona un tipo de contrato');
      return;
    }
    this.loading.set(true);
    this.error.set(null);
    try {
      await this.svc.generate(this.form);
      this.success.set('Contrato generado exitosamente');
      this.showGenDialog.set(false);
      if (this.form.employee_id) this.loadByEmployee(this.form.employee_id);
    } catch (e: any) {
      this.error.set(e.error?.detail || e.message || 'Error al generar contrato');
    } finally {
      this.loading.set(false);
    }
  }

  onTipoChange(tipo: ContractTypeResponse) {
    this.selectedTipo.set(tipo);
    this.form.contract_type_id = tipo.id;
  }

  statusSeverity(status: string): 'success' | 'warning' | 'danger' {
    if (status === 'Activo') return 'success';
    if (status === 'Vencido') return 'danger';
    return 'warning';
  }
}
