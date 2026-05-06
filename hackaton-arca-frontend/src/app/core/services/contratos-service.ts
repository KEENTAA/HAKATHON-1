import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { firstValueFrom } from 'rxjs';
import { environment } from '../../environments/environments';
import {
  ContractResponse,
  ContractType,
  GenerateContractRequest,
} from '../models/contract.model';

@Injectable({ providedIn: 'root' })
export class ContratosService {
  private http = inject(HttpClient);
  private baseUrl = environment.apiUrl;

  async generate(dto: GenerateContractRequest): Promise<ContractResponse> {
    return firstValueFrom(
      this.http.post<ContractResponse>(`${this.baseUrl}/contratos/generate`, dto)
    );
  }

  async getByEmployee(employeeId: number): Promise<ContractResponse[]> {
    return firstValueFrom(
      this.http.get<ContractResponse[]>(`${this.baseUrl}/contratos/empleado/${employeeId}`)
    );
  }

  async getById(id: number): Promise<ContractResponse> {
    return firstValueFrom(
      this.http.get<ContractResponse>(`${this.baseUrl}/contratos/${id}`)
    );
  }

  async updateStatus(id: number, status: string): Promise<ContractResponse> {
    return firstValueFrom(
      this.http.put<ContractResponse>(`${this.baseUrl}/contratos/${id}/status`, { status })
    );
  }

  async getTipos(): Promise<ContractType[]> {
    return firstValueFrom(
      this.http.get<ContractType[]>(`${this.baseUrl}/contratos/tipos`)
    );
  }
}
