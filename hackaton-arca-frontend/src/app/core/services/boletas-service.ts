import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { PaySlip, PaymentConcept, NewPaySlip, NewConcept } from '@core/models/payslip.model';
import { environment } from '@env/environments';

@Injectable({ providedIn: 'root' })
export class BoletasService {
  private http = inject(HttpClient);
  private apiUrl = environment.apiUrl;

  list(params: {
    employee_id?: number;
    period_month?: number;
    period_year?: number;
  }): Observable<PaySlip[]> {
    return this.http.get<PaySlip[]>(`${this.apiUrl}/pay-slips`, { params });
  }

  getById(id: number): Observable<PaySlip> {
    return this.http.get<PaySlip>(`${this.apiUrl}/pay-slips/${id}`);
  }

  create(paySlip: NewPaySlip): Observable<PaySlip> {
    return this.http.post<PaySlip>(`${this.apiUrl}/pay-slips`, paySlip);
  }

  getConcepts(): Observable<PaymentConcept[]> {
    return this.http.get<PaymentConcept[]>(`${this.apiUrl}/payment-concepts`);
  }

  createConcept(concept: NewConcept): Observable<PaymentConcept> {
    return this.http.post<PaymentConcept>(`${this.apiUrl}/payment-concepts`, concept);
  }
}
