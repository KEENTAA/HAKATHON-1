export interface ContractCreate {
  employee_id: number;
  contract_type_id: number;
  salary: number;
  start_date: string;
  end_date: string;
  job_title: string;
  department: string;
}

export interface ContractResponse {
  id: number;
  employee_id: number;
  contract_type_id: number;
  document_text: string;
  status: string;
  salary: number;
  start_date: string;
  end_date: string;
  job_title: string;
  department: string;
  created_at: string;
  updated_at: string;
}

export interface ContractListResponse {
  id: number;
  employee_id: number;
  contract_type_id: number;
  status: string;
  salary: number;
  start_date: string;
  end_date: string;
  job_title: string;
}

export interface ContractUpdateStatus {
  status: string;
}

export interface ContractTypeResponse {
  id: number;
  name: string;
  description: string;
  duration_months: number;
}
