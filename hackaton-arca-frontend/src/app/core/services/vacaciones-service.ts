import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { VacationBalance, VacationRequest, type NewVacationRequest } from '@core/models/vacation.model';
import { environment } from '@env/environments';

@Injectable({ providedIn: 'root' })
export class VacacionesService {
  private http = inject(HttpClient);
  private apiUrl = environment.apiUrl;

  getBalance(employeeId: number): Observable<VacationBalance> {
    return this.http.get<VacationBalance>(`${this.apiUrl}/vacations/balance/${employeeId}`);
  }

  request(request: NewVacationRequest): Observable<VacationRequest> {
    return this.http.post<VacationRequest>(`${this.apiUrl}/vacations/request`, request);
  }

  approve(requestId: number, status: 'APPROVED' | 'REJECTED'): Observable<VacationRequest> {
    return this.http.patch<VacationRequest>(`${this.apiUrl}/vacations/approve/${requestId}`, { status });
  }
}
