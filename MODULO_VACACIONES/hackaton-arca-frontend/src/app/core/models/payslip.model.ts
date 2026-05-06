export interface PaymentConcept {
  id: number;
  name: string;
  amount: number;
  type: 'earning' | 'deduction';
}

export type NewConcept = Omit<PaymentConcept, 'id'>;

export interface PaySlip {
  id: number;
  employee_id: number;
  period_month: number;
  period_year: number;
  concepts: PaymentConcept[];
  total_earnings: number;
  total_deductions: number;
  net_amount: number;
  created_at?: string;
}

export type NewPaySlip = Omit<PaySlip, 'id' | 'created_at'>;
