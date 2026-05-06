export interface MicroserviceHealth {
  status: string;
  service: string;
  version: string;
  database: string;
  modules: string[];
}

export interface ServiceCard {
  name: string;
  baseUrl: string;
  docsUrl: string;
  status: 'online' | 'offline' | 'loading';
  detail: string;
}

export interface Department {
  id: number;
  name: string;
  description?: string | null;
  created_at?: string;
  updated_at?: string;
}

export interface DepartmentPayload {
  name: string;
  description?: string | null;
}

export interface Position {
  id: number;
  name: string;
  base_salary: number;
  created_at?: string;
  updated_at?: string;
}

export interface PositionPayload {
  name: string;
  base_salary: number;
}

export interface EmployeeDepartment {
  id: number;
  name: string;
  description?: string | null;
}

export interface EmployeePosition {
  id: number;
  name: string;
  base_salary: number;
}

export interface Employee {
  id: number;
  ci: string;
  first_name: string;
  last_name: string;
  email: string;
  phone?: string | null;
  hire_date: string;
  current_salary: number;
  status: 'ACTIVO' | 'BAJA' | 'SUSPENDIDO' | string;
  department_id: number;
  position_id: number;
  department?: EmployeeDepartment;
  position?: EmployeePosition;
  created_at?: string;
  updated_at?: string;
}

export interface EmployeePayload {
  ci: string;
  first_name: string;
  last_name: string;
  email: string;
  phone?: string | null;
  hire_date: string;
  current_salary: number;
  department_id: number;
  position_id: number;
}

export interface EmployeeUpdatePayload {
  first_name?: string;
  last_name?: string;
  email?: string;
  phone?: string | null;
  current_salary?: number;
  department_id?: number;
  position_id?: number;
  status?: string;
}

export interface VacationEmployeeSummary {
  id: number;
  first_name: string;
  last_name: string;
  hire_date: string;
  status: string;
  current_salary: number;
}

export interface VacationBalance {
  employee_id: number;
  total_days_earned: number;
  days_used: number;
  employee: VacationEmployeeSummary;
  years_completed: number;
  days_available: number;
  eligible: boolean;
  last_update: string;
}

export interface VacationEligibility {
  employee: VacationEmployeeSummary;
  years_completed: number;
  total_days_earned: number;
  days_used: number;
  days_available: number;
  eligible: boolean;
  message: string;
}

export interface VacationRequestPayload {
  employee_id: number;
  start_date: string;
  end_date: string;
  notes?: string | null;
}

export interface VacationReviewPayload {
  notes?: string | null;
}

export interface VacationRequest {
  id: number;
  employee_id: number;
  start_date: string;
  end_date: string;
  days_requested: number;
  status: 'Pendiente' | 'Aprobado' | 'Rechazado' | string;
  notes?: string | null;
  requested_at: string;
  reviewed_at?: string | null;
  created_at: string;
  updated_at: string;
}

export interface VacationRequestList {
  items: VacationRequest[];
  total: number;
}

export interface ContractType {
  id: number;
  name: string;
}

export interface ContractGeneratePayload {
  employee_id: number;
  contract_type_id?: number | null;
  start_date: string;
  salary: number;
  trial_period_days: number;
  end_date?: string | null;
}

export interface Contract {
  id: number;
  employee_id: number;
  contract_type_id: number;
  start_date: string;
  end_date?: string | null;
  salary: string | number;
  trial_period_days: number;
  status: string;
  generated_document: string;
}

export interface ContractGenerateResult {
  contract: Contract;
  employee: VacationEmployeeSummary;
  contract_type: ContractType;
  document: string;
}

export interface ContractListResult {
  items: Contract[];
  total: number;
}

export interface PaymentConcept {
  id: number;
  name: string;
  type: 'Ingreso' | 'Egreso' | string;
}

export interface PaySlipDetailPayload {
  concept_id: number;
  amount: number;
}

export interface PaySlipGeneratePayload {
  employee_id: number;
  period_month: number;
  period_year: number;
  payment_date: string;
  details: PaySlipDetailPayload[];
  include_salary_concept: boolean;
}

export interface PaySlipDetail {
  id: number;
  pay_slip_id: number;
  concept_id: number;
  amount: string | number;
  concept: PaymentConcept;
}

export interface PaySlip {
  id: number;
  employee_id: number;
  period_month: number;
  period_year: number;
  payment_date: string;
  total_net: string | number;
  status: string;
  generated_document: string;
  created_at: string;
  updated_at: string;
  details: PaySlipDetail[];
}

export interface PaySlipGenerateResult {
  payslip: PaySlip;
  employee: VacationEmployeeSummary;
  document: string;
}

export interface PaySlipSingleResult extends PaySlip {}

export interface PaySlipListResult {
  items: PaySlip[];
  total: number;
}
