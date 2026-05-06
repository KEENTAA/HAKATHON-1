export interface VacationBalance {
  days_earned: number;
  days_used: number;
  days_available: number;
}

export interface VacationRequest {
  id: number;
  employee_id: number;
  start_date: string;
  end_date: string;
  description?: string;
  total_days: number;
  status: 'PENDING' | 'APPROVED' | 'REJECTED';
  created_at?: string;
}

export type NewVacationRequest = Omit<VacationRequest, 'id' | 'total_days' | 'status' | 'created_at'>;
