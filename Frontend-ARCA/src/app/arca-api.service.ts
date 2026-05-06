import { inject, Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import {
  Contract,
  ContractGeneratePayload,
  ContractGenerateResult,
  ContractListResult,
  ContractType,
  Department,
  DepartmentPayload,
  Employee,
  EmployeePayload,
  EmployeeUpdatePayload,
  MicroserviceHealth,
  PaySlipGeneratePayload,
  PaySlipGenerateResult,
  PaySlipListResult,
  PaySlip,
  PaymentConcept,
  Position,
  PositionPayload,
  VacationBalance,
  VacationEligibility,
  VacationRequest,
  VacationRequestList,
  VacationRequestPayload,
  VacationReviewPayload,
} from './arca-api.models';

@Injectable({ providedIn: 'root' })
export class ArcaApiService {
  private readonly http = inject(HttpClient);
  private readonly personalBase = 'http://localhost:8000';
  private readonly vacationsBase = 'http://localhost:8002';
  private readonly contractsBase = 'http://localhost:8003';
  private readonly payrollBase = 'http://localhost:8004';

  healthChecks(): Record<string, Observable<MicroserviceHealth>> {
    return {
      personal: this.http.get<ServiceHealth>(`${this.personalBase}/health`),
      vacations: this.http.get<ServiceHealth>(`${this.vacationsBase}/health`),
      contracts: this.http.get<ServiceHealth>(`${this.contractsBase}/health`),
      payroll: this.http.get<ServiceHealth>(`${this.payrollBase}/health`),
    };
  }

  // Personal
  listDepartments(): Observable<Department[]> {
    return this.http.get<Department[]>(`${this.personalBase}/departments`);
  }

  createDepartment(payload: DepartmentPayload): Observable<Department> {
    return this.http.post<Department>(`${this.personalBase}/departments`, payload);
  }

  updateDepartment(id: number, payload: DepartmentPayload): Observable<Department> {
    return this.http.put<Department>(`${this.personalBase}/departments/${id}`, payload);
  }

  deleteDepartment(id: number): Observable<{ message: string }> {
    return this.http.delete<{ message: string }>(`${this.personalBase}/departments/${id}`);
  }

  listPositions(): Observable<Position[]> {
    return this.http.get<Position[]>(`${this.personalBase}/positions`);
  }

  createPosition(payload: PositionPayload): Observable<Position> {
    return this.http.post<Position>(`${this.personalBase}/positions`, payload);
  }

  updatePosition(id: number, payload: PositionPayload): Observable<Position> {
    return this.http.put<Position>(`${this.personalBase}/positions/${id}`, payload);
  }

  deletePosition(id: number): Observable<{ message: string }> {
    return this.http.delete<{ message: string }>(`${this.personalBase}/positions/${id}`);
  }

  listEmployees(params: { skip?: number; limit?: number; status?: string; department_id?: number } = {}): Observable<Employee[]> {
    return this.http.get<Employee[]>(`${this.personalBase}/employees`, { params: this.createParams(params) });
  }

  getEmployee(id: number): Observable<Employee> {
    return this.http.get<Employee>(`${this.personalBase}/employees/${id}`);
  }

  getEmployeeByCi(ci: string): Observable<Employee> {
    return this.http.get<Employee>(`${this.personalBase}/employees/by-ci/${encodeURIComponent(ci)}`);
  }

  createEmployee(payload: EmployeePayload): Observable<Employee> {
    return this.http.post<Employee>(`${this.personalBase}/employees`, payload);
  }

  updateEmployee(id: number, payload: EmployeeUpdatePayload): Observable<Employee> {
    return this.http.put<Employee>(`${this.personalBase}/employees/${id}`, payload);
  }

  deactivateEmployee(id: number): Observable<Employee> {
    return this.http.patch<Employee>(`${this.personalBase}/employees/${id}/deactivate`, {});
  }

  deleteEmployee(id: number): Observable<{ message: string }> {
    return this.http.delete<{ message: string }>(`${this.personalBase}/employees/${id}`);
  }

  listEmployeesByDepartment(departmentId: number): Observable<Employee[]> {
    return this.http.get<Employee[]>(`${this.personalBase}/employees/department/${departmentId}/list`);
  }

  countEmployees(params: { status?: string; department_id?: number } = {}): Observable<{ total: number }> {
    return this.http.get<{ total: number }>(`${this.personalBase}/employees/count`, { params: this.createParams(params) });
  }

  // Vacations
  getVacationBalance(employeeId: number): Observable<VacationBalance> {
    return this.http.get<VacationBalance>(`${this.vacationsBase}/vacations/employees/${employeeId}/balance`);
  }

  getVacationEligibility(employeeId: number): Observable<VacationEligibility> {
    return this.http.get<VacationEligibility>(`${this.vacationsBase}/vacations/employees/${employeeId}/eligibility`);
  }

  createVacationRequest(payload: VacationRequestPayload): Observable<VacationRequest> {
    return this.http.post<VacationRequest>(`${this.vacationsBase}/vacations/requests`, payload);
  }

  listVacationRequests(params: { employee_id?: number; status?: string; skip?: number; limit?: number } = {}): Observable<VacationRequestList> {
    return this.http.get<VacationRequestList>(`${this.vacationsBase}/vacations/requests`, { params: this.createParams(params) });
  }

  getVacationRequest(requestId: number): Observable<VacationRequest> {
    return this.http.get<VacationRequest>(`${this.vacationsBase}/vacations/requests/${requestId}`);
  }

  approveVacationRequest(requestId: number, payload: VacationReviewPayload = {}): Observable<VacationRequest> {
    return this.http.post<VacationRequest>(`${this.vacationsBase}/vacations/requests/${requestId}/approve`, payload);
  }

  rejectVacationRequest(requestId: number, payload: VacationReviewPayload = {}): Observable<VacationRequest> {
    return this.http.post<VacationRequest>(`${this.vacationsBase}/vacations/requests/${requestId}/reject`, payload);
  }

  listVacationRequestsByEmployee(employeeId: number, params: { status?: string; skip?: number; limit?: number } = {}): Observable<VacationRequestList> {
    return this.http.get<VacationRequestList>(`${this.vacationsBase}/vacations/employees/${employeeId}/requests`, { params: this.createParams(params) });
  }

  // Contracts
  listContractTypes(): Observable<ContractType[]> {
    return this.http.get<ContractType[]>(`${this.contractsBase}/contratos/types`);
  }

  generateContract(payload: ContractGeneratePayload): Observable<ContractGenerateResult> {
    return this.http.post<ContractGenerateResult>(`${this.contractsBase}/contratos/generate`, payload);
  }

  getContract(contractId: number): Observable<Contract> {
    return this.http.get<Contract>(`${this.contractsBase}/contratos/${contractId}`);
  }

  listContractsByEmployee(employeeId: number, params: { status?: string; skip?: number; limit?: number } = {}): Observable<ContractListResult> {
    return this.http.get<ContractListResult>(`${this.contractsBase}/contratos/employees/${employeeId}`, { params: this.createParams(params) });
  }

  // Payroll
  listPaymentConcepts(): Observable<PaymentConcept[]> {
    return this.http.get<PaymentConcept[]>(`${this.payrollBase}/boletas/concepts`);
  }

  generatePaySlip(payload: PaySlipGeneratePayload): Observable<PaySlipGenerateResult> {
    return this.http.post<PaySlipGenerateResult>(`${this.payrollBase}/boletas/generate`, payload);
  }

  getPaySlip(paySlipId: number): Observable<PaySlip> {
    return this.http.get<PaySlip>(`${this.payrollBase}/boletas/slips/${paySlipId}`);
  }

  listPaySlipsByEmployee(employeeId: number, params: { skip?: number; limit?: number } = {}): Observable<PaySlipListResult> {
    return this.http.get<PaySlipListResult>(`${this.payrollBase}/boletas/${employeeId}`, { params: this.createParams(params) });
  }

  listPaySlipsByEmployeeAlias(employeeId: number, params: { skip?: number; limit?: number } = {}): Observable<PaySlipListResult> {
    return this.http.get<PaySlipListResult>(`${this.payrollBase}/boletas/${employeeId}/slips`, { params: this.createParams(params) });
  }

  private createParams(values: Record<string, string | number | boolean | null | undefined>): HttpParams {
    let params = new HttpParams();
    for (const [key, value] of Object.entries(values)) {
      if (value !== null && value !== undefined && value !== '') {
        params = params.set(key, String(value));
      }
    }
    return params;
  }
}
