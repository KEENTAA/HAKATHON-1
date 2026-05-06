import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { firstValueFrom } from 'rxjs';
import {
  Department,
  NewDepartment,
  Position,
  NewPosition,
  Employee,
  NewEmployee,
  EmployeeCount,
} from '../models/employee.model';
import { environment } from '@env/environments';

@Injectable({ providedIn: 'root' })
export class PersonalService {
  private http = inject(HttpClient);
  private base = environment.apiUrl;

  // Health
  async health(): Promise<any> {
    return firstValueFrom(this.http.get(`${this.base}/health`));
  }

  // ===== DEPARTMENTS =====
  async listDepartments(skip = 0, limit = 50): Promise<Department[]> {
    const params = new HttpParams().set('skip', skip).set('limit', limit);
    return firstValueFrom(this.http.get<Department[]>(`${this.base}/departments/`, { params }));
  }

  async getDepartment(id: number): Promise<Department> {
    return firstValueFrom(this.http.get<Department>(`${this.base}/departments/${id}`));
  }

  async createDepartment(dto: NewDepartment): Promise<Department> {
    return firstValueFrom(this.http.post<Department>(`${this.base}/departments/`, dto));
  }

  async updateDepartment(id: number, dto: Partial<NewDepartment>): Promise<Department> {
    return firstValueFrom(this.http.put<Department>(`${this.base}/departments/${id}`, dto));
  }

  async deleteDepartment(id: number): Promise<void> {
    return firstValueFrom(this.http.delete<void>(`${this.base}/departments/${id}`));
  }

  // ===== POSITIONS =====
  async listPositions(skip = 0, limit = 50): Promise<Position[]> {
    const params = new HttpParams().set('skip', skip).set('limit', limit);
    return firstValueFrom(this.http.get<Position[]>(`${this.base}/positions/`, { params }));
  }

  async getPosition(id: number): Promise<Position> {
    return firstValueFrom(this.http.get<Position>(`${this.base}/positions/${id}`));
  }

  async createPosition(dto: NewPosition): Promise<Position> {
    return firstValueFrom(this.http.post<Position>(`${this.base}/positions/`, dto));
  }

  async updatePosition(id: number, dto: Partial<NewPosition>): Promise<Position> {
    return firstValueFrom(this.http.put<Position>(`${this.base}/positions/${id}`, dto));
  }

  async deletePosition(id: number): Promise<void> {
    return firstValueFrom(this.http.delete<void>(`${this.base}/positions/${id}`));
  }

  // ===== EMPLOYEES =====
  async listEmployees(opts?: {
    skip?: number;
    limit?: number;
    status?: string;
    department_id?: number;
  }): Promise<Employee[]> {
    let params = new HttpParams();
    if (opts?.skip) params = params.set('skip', opts.skip);
    if (opts?.limit) params = params.set('limit', opts.limit);
    if (opts?.status) params = params.set('status', opts.status);
    if (opts?.department_id) params = params.set('department_id', opts.department_id);
    return firstValueFrom(this.http.get<Employee[]>(`${this.base}/employees/`, { params }));
  }

  async countEmployees(opts?: { status?: string; department_id?: number }): Promise<EmployeeCount> {
    let params = new HttpParams();
    if (opts?.status) params = params.set('status', opts.status);
    if (opts?.department_id) params = params.set('department_id', opts.department_id);
    return firstValueFrom(this.http.get<EmployeeCount>(`${this.base}/employees/count`, { params }));
  }

  async getEmployee(id: number): Promise<Employee> {
    return firstValueFrom(this.http.get<Employee>(`${this.base}/employees/${id}`));
  }

  async getByCI(ci: string): Promise<Employee> {
    return firstValueFrom(this.http.get<Employee>(`${this.base}/employees/by-ci/${ci}`));
  }

  async createEmployee(dto: NewEmployee): Promise<Employee> {
    return firstValueFrom(this.http.post<Employee>(`${this.base}/employees/`, dto));
  }

  async updateEmployee(id: number, dto: Partial<NewEmployee>): Promise<Employee> {
    return firstValueFrom(this.http.put<Employee>(`${this.base}/employees/${id}`, dto));
  }

  async deleteEmployee(id: number): Promise<void> {
    return firstValueFrom(this.http.delete<void>(`${this.base}/employees/${id}`));
  }

  async deactivateEmployee(id: number): Promise<void> {
    return firstValueFrom(this.http.patch<void>(`${this.base}/employees/${id}/deactivate`, {}));
  }

  async listByDepartment(deptId: number): Promise<Employee[]> {
    return firstValueFrom(
      this.http.get<Employee[]>(`${this.base}/employees/department/${deptId}/list`),
    );
  }
}
