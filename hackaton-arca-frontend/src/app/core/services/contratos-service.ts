import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { firstValueFrom } from 'rxjs';
import {
  ContractCreate,
  ContractListResponse,
  ContractResponse,
  ContractTypeResponse,
  ContractUpdateStatus,
} from '../models/contract.model';
import { environment } from '@env/environments';

@Injectable({ providedIn: 'root' })
export class ContratosService {
  private http = inject(HttpClient);
  private baseUrl = environment.apiUrl;

  async generate(dto: ContractCreate): Promise<ContractResponse> {
    return firstValueFrom(
      this.http.post<ContractResponse>(`${this.baseUrl}/contratos/generate`, dto),
    );
  }

  async getByEmployee(employeeId: number): Promise<ContractListResponse[]> {
    return firstValueFrom(
      this.http.get<ContractListResponse[]>(`${this.baseUrl}/contratos/empleado/${employeeId}`),
    );
  }

  async getById(id: number): Promise<ContractResponse> {
    return firstValueFrom(this.http.get<ContractResponse>(`${this.baseUrl}/contratos/${id}`));
  }

  async updateStatus(id: number, dto: ContractUpdateStatus): Promise<ContractResponse> {
    return firstValueFrom(
      this.http.put<ContractResponse>(`${this.baseUrl}/contratos/${id}/status`, dto),
    );
  }

  async getTipos(): Promise<ContractTypeResponse[]> {
    return firstValueFrom(this.http.get<ContractTypeResponse[]>(`${this.baseUrl}/contratos/tipos`));
  }
}
