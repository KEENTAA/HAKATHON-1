import { ChangeDetectionStrategy, Component, inject, OnInit, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { CardModule } from 'primeng/card';
import { TableModule } from 'primeng/table';
import { ButtonModule } from 'primeng/button';
import { InputTextModule } from 'primeng/inputtext';
import { MessageModule } from 'primeng/message';
import { DialogModule } from 'primeng/dialog';
import { TabsModule } from 'primeng/tabs';
import { TagModule } from 'primeng/tag';
import { PersonalService } from '../../core/services/personal-service';
import { Department, Employee, Position } from '../../core/models/employee.model';

@Component({
  selector: 'arca-personal',
  imports: [
    FormsModule,
    CardModule,
    TableModule,
    ButtonModule,
    InputTextModule,
    MessageModule,
    DialogModule,
    TabsModule,
    TagModule,
  ],
  templateUrl: './personal.html',
  styleUrl: './personal.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class Personal implements OnInit {
  private svc = inject(PersonalService);

  activeTab = signal(0);
  loading = signal(false);
  error = signal<string | null>(null);

  departments = signal<Department[]>([]);
  positions = signal<Position[]>([]);
  employees = signal<Employee[]>([]);
  employeeCount = signal<number>(0);

  showDeptDialog = signal(false);
  showPosDialog = signal(false);
  showEmpDialog = signal(false);
  editingItem = signal<any>(null);

  deptForm = { name: '', description: '' };
  posForm = { name: '', description: '', department_id: 0 };
  empForm = { ci: '', name: '', email: '', phone: '', department_id: 0, status: 'active' as string, hire_date: '' };

  async ngOnInit() {
    await this.loadAll();
  }

  async loadAll() {
    this.loading.set(true);
    try {
      const [depts, pos, emps, count] = await Promise.all([
        this.svc.listDepartments(),
        this.svc.listPositions(),
        this.svc.listEmployees(),
        this.svc.countEmployees(),
      ]);
      this.departments.set(depts);
      this.positions.set(pos);
      this.employees.set(emps);
      this.employeeCount.set(count.count);
    } catch (e: any) {
      this.error.set(e.message || 'Error al cargar datos');
    } finally {
      this.loading.set(false);
    }
  }

  // ===== DEPARTMENTS =====
  openDeptDialog(item?: Department) {
    if (item) {
      this.deptForm = { name: item.name, description: item.description || '' };
      this.editingItem.set(item);
    } else {
      this.deptForm = { name: '', description: '' };
      this.editingItem.set(null);
    }
    this.showDeptDialog.set(true);
  }

  async saveDept() {
    this.loading.set(true);
    try {
      const item = this.editingItem();
      if (item) {
        await this.svc.updateDepartment(item.id, this.deptForm);
      } else {
        await this.svc.createDepartment(this.deptForm);
      }
      this.showDeptDialog.set(false);
      await this.loadAll();
    } catch (e: any) {
      this.error.set(e.message || 'Error al guardar departamento');
    } finally {
      this.loading.set(false);
    }
  }

  async deleteDept(id: number) {
    this.loading.set(true);
    try {
      await this.svc.deleteDepartment(id);
      await this.loadAll();
    } catch (e: any) {
      this.error.set(e.message || 'Error al eliminar');
    } finally {
      this.loading.set(false);
    }
  }

  // ===== POSITIONS =====
  openPosDialog(item?: Position) {
    if (item) {
      this.posForm = { name: item.name, description: item.description || '', department_id: item.department_id || 0 };
      this.editingItem.set(item);
    } else {
      this.posForm = { name: '', description: '', department_id: 0 };
      this.editingItem.set(null);
    }
    this.showPosDialog.set(true);
  }

  async savePos() {
    this.loading.set(true);
    try {
      const item = this.editingItem();
      const dto: any = { ...this.posForm };
      if (!dto.department_id) delete dto.department_id;
      if (item) {
        await this.svc.updatePosition(item.id, dto);
      } else {
        await this.svc.createPosition(dto);
      }
      this.showPosDialog.set(false);
      await this.loadAll();
    } catch (e: any) {
      this.error.set(e.message || 'Error al guardar posición');
    } finally {
      this.loading.set(false);
    }
  }

  async deletePos(id: number) {
    this.loading.set(true);
    try {
      await this.svc.deletePosition(id);
      await this.loadAll();
    } catch (e: any) {
      this.error.set(e.message || 'Error al eliminar');
    } finally {
      this.loading.set(false);
    }
  }

  // ===== EMPLOYEES =====
  openEmpDialog(item?: Employee) {
    if (item) {
      this.empForm = {
        ci: item.ci, name: item.name, email: item.email, phone: item.phone || '',
        department_id: item.department_id || 0, status: item.status, hire_date: item.hire_date,
      };
      this.editingItem.set(item);
    } else {
      this.empForm = { ci: '', name: '', email: '', phone: '', department_id: 0, status: 'active', hire_date: '' };
      this.editingItem.set(null);
    }
    this.showEmpDialog.set(true);
  }

  async saveEmp() {
    this.loading.set(true);
    try {
      const item = this.editingItem();
      if (item) {
        await this.svc.updateEmployee(item.id, this.empForm);
      } else {
        await this.svc.createEmployee(this.empForm);
      }
      this.showEmpDialog.set(false);
      await this.loadAll();
    } catch (e: any) {
      this.error.set(e.message || 'Error al guardar empleado');
    } finally {
      this.loading.set(false);
    }
  }

  async deactivate(id: number) {
    this.loading.set(true);
    try {
      await this.svc.deactivateEmployee(id);
      await this.loadAll();
    } catch (e: any) {
      this.error.set(e.message || 'Error al dar de baja');
    } finally {
      this.loading.set(false);
    }
  }

  async deleteEmp(id: number) {
    this.loading.set(true);
    try {
      await this.svc.deleteEmployee(id);
      await this.loadAll();
    } catch (e: any) {
      this.error.set(e.message || 'Error al eliminar');
    } finally {
      this.loading.set(false);
    }
  }

  async loadByDept(deptId: number) {
    this.loading.set(true);
    try {
      const emps = await this.svc.listByDepartment(deptId);
      this.employees.set(emps);
    } catch (e: any) {
      this.error.set(e.message || 'Error al cargar empleados');
    } finally {
      this.loading.set(false);
    }
  }

  deptName(id?: number): string {
    if (!id) return '—';
    return this.departments().find(d => d.id === id)?.name || `#${id}`;
  }
}
