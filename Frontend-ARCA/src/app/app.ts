import { CommonModule } from '@angular/common';
import { HttpClientModule, HttpErrorResponse } from '@angular/common/http';
import { HttpClientModule } from '@angular/common/http';
import { Component, OnInit, WritableSignal, computed, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { firstValueFrom, forkJoin } from 'rxjs';
import { ArcaApiService } from './arca-api.service';
import {
  Contract,
  ContractGeneratePayload,
  ContractType,
  Department,
  DepartmentPayload,
  Employee,
  EmployeePayload,
  EmployeeUpdatePayload,
  MicroserviceHealth,
  PaySlip,
  PaySlipGeneratePayload,
  PaymentConcept,
  Position,
  PositionPayload,
  ServiceCard,
  VacationBalance,
  VacationEligibility,
  VacationRequest,
  VacationRequestPayload,
  VacationReviewPayload,
} from './arca-api.models';

type SectionKey = 'overview' | 'personal' | 'vacations' | 'contracts' | 'payroll';

interface DetailRowDraft {
  concept_id: number;
  amount: number;
}

interface SectionLink {
  id: SectionKey;
  label: string;
  hint: string;
}

@Component({
  selector: 'app-root',
  imports: [CommonModule, FormsModule, HttpClientModule],
  templateUrl: './app.html',
  styleUrl: './app.scss'
})
export class App implements OnInit {
  protected readonly title = signal('Frontend-ARCA');
  protected readonly activeSection = signal<SectionKey>('overview');
  protected readonly loading = signal(false);
  protected readonly banner = signal('Control center listo para orquestar los cuatro microservicios.');
  protected readonly errorMessage = signal('');
  protected readonly workflowTrace = signal('Pulsa "Ejecutar demo integral" para validar el flujo completo.');
  protected readonly personalTrace = signal('Sin acciones de personal todavía.');
  protected readonly vacationsTrace = signal('Sin acciones de vacaciones todavía.');
  protected readonly contractsTrace = signal('Sin acciones de contratos todavía.');
  protected readonly payrollTrace = signal('Sin acciones de boletas todavía.');

  protected readonly serviceCards = signal<ServiceCard[]>([
    {
      name: 'Personal',
      baseUrl: 'http://localhost:8000',
      docsUrl: 'http://localhost:8000/docs',
      status: 'loading',
      detail: 'Verificando disponibilidad del maestro de personal...',
    },
    {
      name: 'Vacaciones',
      baseUrl: 'http://localhost:8002',
      docsUrl: 'http://localhost:8002/docs',
      status: 'loading',
      detail: 'Verificando cálculo de antigüedad y solicitudes...',
    },
    {
      name: 'Contratos',
      baseUrl: 'http://localhost:8003',
      docsUrl: 'http://localhost:8003/docs',
      status: 'loading',
      detail: 'Verificando generación de contratos...',
    },
    {
      name: 'Boletas',
      baseUrl: 'http://localhost:8004',
      docsUrl: 'http://localhost:8004/docs',
      status: 'loading',
      detail: 'Verificando persistencia de boletas...',
    },
  ]);

  protected readonly sections: SectionLink[] = [
    { id: 'overview', label: 'Resumen', hint: 'Estado global y demo' },
    { id: 'personal', label: 'Personal', hint: 'Áreas, cargos y funcionarios' },
    { id: 'vacations', label: 'Vacaciones', hint: 'Balance, elegibilidad y solicitudes' },
    { id: 'contracts', label: 'Contratos', hint: 'Tipos y contratos generados' },
    { id: 'payroll', label: 'Boletas', hint: 'Conceptos, cabeceras y detalle' },
  ];

  protected readonly departments = signal<Department[]>([]);
  protected readonly positions = signal<Position[]>([]);
  protected readonly employees = signal<Employee[]>([]);
  protected readonly contractTypes = signal<ContractType[]>([]);
  protected readonly paymentConcepts = signal<PaymentConcept[]>([]);

  protected readonly summaryTiles = computed(() => {
    const servicesOnline = this.serviceCards().filter((service) => service.status === 'online').length;
    return [
      { label: 'Microservicios vivos', value: `${servicesOnline}/4` },
      { label: 'Departamentos', value: `${this.departments().length}` },
      { label: 'Cargos', value: `${this.positions().length}` },
      { label: 'Funcionarios', value: `${this.employees().length}` },
      { label: 'Tipos contrato', value: `${this.contractTypes().length}` },
      { label: 'Conceptos pago', value: `${this.paymentConcepts().length}` },
    ];
  });

  protected departmentCreate: DepartmentPayload = {
    name: '',
    description: '',
  };

  protected departmentUpdate = {
    id: 0,
    name: '',
    description: '',
  };

  protected departmentDeleteId = 0;

  protected positionCreate: PositionPayload = {
    name: '',
    base_salary: 0,
  };

  protected positionUpdate = {
    id: 0,
    name: '',
    base_salary: 0,
  };

  protected positionDeleteId = 0;

  protected employeeCreate: EmployeePayload = {
    ci: '',
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
    hire_date: new Date().toISOString().slice(0, 10),
    current_salary: 0,
    department_id: 0,
    position_id: 0,
  };

  protected employeeUpdate: EmployeeUpdatePayload & { id: number } = {
    id: 0,
    current_salary: 0,
    department_id: 0,
    position_id: 0,
    status: 'ACTIVO',
  };

  protected employeeDeleteId = 0;
  protected employeeLookupId = 0;
  protected employeeLookupCi = '';
  protected employeesByDepartmentId = 0;
  protected employeeCountFilters = {
    status: '',
    department_id: 0,
  };

  protected vacationLookupEmployeeId = 0;
  protected vacationRequestForm: VacationRequestPayload = {
    employee_id: 0,
    start_date: this.addDays(new Date(), 30),
    end_date: this.addDays(new Date(), 39),
    notes: '',
  };
  protected vacationRequestId = 0;
  protected vacationReview: VacationReviewPayload = {
    notes: '',
  };
  protected vacationStatusFilter = '';
  protected vacationListEmployeeId = 0;

  protected contractGenerateForm: ContractGeneratePayload = {
    employee_id: 0,
    contract_type_id: null,
    start_date: new Date().toISOString().slice(0, 10),
    salary: 0,
    trial_period_days: 90,
    end_date: null,
  };
  protected contractLookupId = 0;
  protected contractListEmployeeId = 0;
  protected contractStatusFilter = '';

  protected paySlipGenerateForm: PaySlipGeneratePayload = {
    employee_id: 0,
    period_month: new Date().getMonth() + 1,
    period_year: new Date().getFullYear(),
    payment_date: new Date().toISOString().slice(0, 10),
    details: [],
    include_salary_concept: true,
  };
  protected paySlipLookupId = 0;
  protected paySlipListEmployeeId = 0;
  protected paySlipAliasEmployeeId = 0;

  constructor(private readonly api: ArcaApiService) {
    this.paySlipGenerateForm.details = [{ concept_id: 0, amount: 0 }];
  }

  async ngOnInit(): Promise<void> {
    await this.bootstrap();
  }

  protected async bootstrap(): Promise<void> {
    this.loading.set(true);
    this.banner.set('Conectando con Personal, Vacaciones, Contratos y Boletas...');
    this.errorMessage.set('');

    try {
      const health$ = forkJoin(this.api.healthChecks());
      const [health, catalogs] = await Promise.all([
        firstValueFrom(health$),
        firstValueFrom(
          forkJoin({
            departments: this.api.listDepartments(),
            positions: this.api.listPositions(),
            employees: this.api.listEmployees({ limit: 25 }),
            contractTypes: this.api.listContractTypes(),
            paymentConcepts: this.api.listPaymentConcepts(),
          })
        ),
      ]);

      this.serviceCards.set([
        this.toServiceCard('Personal', 'http://localhost:8000', 'http://localhost:8000/docs', health['personal']),
        this.toServiceCard('Vacaciones', 'http://localhost:8002', 'http://localhost:8002/docs', health['vacaciones']),
        this.toServiceCard('Contratos', 'http://localhost:8003', 'http://localhost:8003/docs', health['contratos']),
        this.toServiceCard('Boletas', 'http://localhost:8004', 'http://localhost:8004/docs', health['payroll']),
      ]);

      this.departments.set(catalogs.departments);
      this.positions.set(catalogs.positions);
      this.employees.set(catalogs.employees);
      this.contractTypes.set(catalogs.contractTypes);
      this.paymentConcepts.set(catalogs.paymentConcepts);

      this.syncCatalogDefaults();
      this.banner.set('Todos los microservicios respondieron correctamente.');
      this.workflowTrace.set(
        JSON.stringify(
          {
            health,
            counts: {
              departments: catalogs.departments.length,
              positions: catalogs.positions.length,
              employees: catalogs.employees.length,
              contractTypes: catalogs.contractTypes.length,
              paymentConcepts: catalogs.paymentConcepts.length,
            },
          },
          null,
          2
        )
      );
    } catch (error) {
      this.errorMessage.set(this.describeError(error));
      this.banner.set('Uno o más microservicios no respondieron. Revisa los contenedores.');
    } finally {
      this.loading.set(false);
    }
  }

  protected setSection(section: SectionKey): void {
    this.activeSection.set(section);
  }

  protected async refreshCatalogs(): Promise<void> {
    const catalogs = await firstValueFrom(
      forkJoin({
        departments: this.api.listDepartments(),
        positions: this.api.listPositions(),
        employees: this.api.listEmployees({ limit: 25 }),
        contractTypes: this.api.listContractTypes(),
        paymentConcepts: this.api.listPaymentConcepts(),
      })
    );

    this.departments.set(catalogs.departments);
    this.positions.set(catalogs.positions);
    this.employees.set(catalogs.employees);
    this.contractTypes.set(catalogs.contractTypes);
    this.paymentConcepts.set(catalogs.paymentConcepts);
    this.syncCatalogDefaults();
  }

  protected async runDemoWorkflow(): Promise<void> {
    this.loading.set(true);
    this.errorMessage.set('');
    this.banner.set('Ejecutando demo integral desde la GUI...');

    try {
      const uniqueSuffix = String(Date.now()).slice(-6);
      const demoDepartment = await firstValueFrom(
        this.api.createDepartment({
          name: `Tecnologia Demo ${uniqueSuffix}`,
          description: 'Departamento creado desde el frontend para la demostracion integral',
        })
      );
      const demoPosition = await firstValueFrom(
        this.api.createPosition({
          name: `Analista Demo ${uniqueSuffix}`,
          base_salary: 5800,
        })
      );
      const demoEmployee = await firstValueFrom(
        this.api.createEmployee({
          ci: `CI-${uniqueSuffix}`,
          first_name: 'Demo',
          last_name: 'ARCA',
          email: `demo-${uniqueSuffix}@arca.local`,
          phone: '70000000',
          hire_date: '2023-04-01',
          current_salary: 6200,
          department_id: demoDepartment.id,
          position_id: demoPosition.id,
        })
      );
      const balance = await firstValueFrom(this.api.getVacationBalance(demoEmployee.id));
      const eligibility = await firstValueFrom(this.api.getVacationEligibility(demoEmployee.id));
      const vacationRequest = await firstValueFrom(
        this.api.createVacationRequest({
          employee_id: demoEmployee.id,
          start_date: this.addDays(new Date(), 30),
          end_date: this.addDays(new Date(), 39),
          notes: 'Solicitud creada desde demo integral',
        })
      );
      const approvedRequest = await firstValueFrom(
        this.api.approveVacationRequest(vacationRequest.id, { notes: 'Aprobado desde demo integral' })
      );
      const contractType = this.contractTypes().find((item) => item.name === 'Indefinido') ?? null;
      const contract = await firstValueFrom(
        this.api.generateContract({
          employee_id: demoEmployee.id,
          contract_type_id: contractType?.id ?? null,
          start_date: '2026-05-05',
          salary: 6200,
          trial_period_days: 90,
          end_date: null,
        })
      );
      const salaryConcept = this.paymentConcepts().find((item) => item.name === 'Sueldo Básico') ?? this.paymentConcepts()[0];
      const discountConcept = this.paymentConcepts().find((item) => item.type === 'Egreso') ?? this.paymentConcepts()[0];
      const paySlip = await firstValueFrom(
        this.api.generatePaySlip({
          employee_id: demoEmployee.id,
          period_month: new Date().getMonth() + 1,
          period_year: new Date().getFullYear(),
          payment_date: new Date().toISOString().slice(0, 10),
          include_salary_concept: true,
          details: discountConcept
            ? [
                {
                  concept_id: discountConcept.id,
                  amount: 300,
                },
              ]
            : [],
        })
      );

      this.workflowTrace.set(
        JSON.stringify(
          {
            department: demoDepartment,
            position: demoPosition,
            employee: demoEmployee,
            vacation: {
              balance,
              eligibility,
              request: approvedRequest,
            },
            contract,
            paySlip,
            salaryConcept: salaryConcept?.name ?? 'N/A',
            discountConcept: discountConcept?.name ?? 'N/A',
          },
          null,
          2
        )
      );
      this.banner.set('Demo integral completada: Personal, Vacaciones, Contratos y Boletas funcionando juntos.');
      await this.refreshCatalogs();
      await this.syncSectionLookups(demoEmployee.id, vacationRequest.id, contract.contract.id, paySlip.payslip.id);
    } catch (error) {
      const message = this.describeError(error);
      this.errorMessage.set(message);
      this.workflowTrace.set(message);
      this.banner.set('La demo integral falló. Revisa el servicio que devolvió el error.');
    } finally {
      this.loading.set(false);
    }
  }

  protected async createDepartment(): Promise<void> {
    await this.captureAction(
      this.personalTrace,
      'Área creada',
      () => firstValueFrom(this.api.createDepartment(this.departmentCreate)),
      async () => this.refreshCatalogs(),
      () => this.resetDepartmentCreate()
    );
  }

  protected async updateDepartment(): Promise<void> {
    await this.captureAction(
      this.personalTrace,
      'Área actualizada',
      () => firstValueFrom(this.api.updateDepartment(this.departmentUpdate.id, this.cleanDepartmentPayload(this.departmentUpdate))),
      async () => this.refreshCatalogs(),
      undefined
    );
  }

  protected async deleteDepartment(): Promise<void> {
    await this.captureAction(
      this.personalTrace,
      'Área eliminada',
      () => firstValueFrom(this.api.deleteDepartment(this.departmentDeleteId)),
      async () => this.refreshCatalogs(),
      () => (this.departmentDeleteId = 0)
    );
  }

  protected async createPosition(): Promise<void> {
    await this.captureAction(
      this.personalTrace,
      'Cargo creado',
      () => firstValueFrom(this.api.createPosition(this.positionCreate)),
      async () => this.refreshCatalogs(),
      () => this.resetPositionCreate()
    );
  }

  protected async updatePosition(): Promise<void> {
    await this.captureAction(
      this.personalTrace,
      'Cargo actualizado',
      () => firstValueFrom(this.api.updatePosition(this.positionUpdate.id, this.cleanPositionPayload(this.positionUpdate))),
      async () => this.refreshCatalogs(),
      undefined
    );
  }

  protected async deletePosition(): Promise<void> {
    await this.captureAction(
      this.personalTrace,
      'Cargo eliminado',
      () => firstValueFrom(this.api.deletePosition(this.positionDeleteId)),
      async () => this.refreshCatalogs(),
      () => (this.positionDeleteId = 0)
    );
  }

  protected async createEmployee(): Promise<void> {
    await this.captureAction(
      this.personalTrace,
      'Funcionario creado',
      () => firstValueFrom(this.api.createEmployee(this.employeeCreate)),
      async () => this.refreshCatalogs(),
      () => this.resetEmployeeCreate()
    );
  }

  protected async updateEmployee(): Promise<void> {
    const { id, ...payload } = this.employeeUpdate;
    await this.captureAction(
      this.personalTrace,
      'Funcionario actualizado',
      () => firstValueFrom(this.api.updateEmployee(id, this.cleanEmployeeUpdatePayload(payload))),
      async () => this.refreshCatalogs(),
      undefined
    );
  }

  protected async deactivateEmployee(): Promise<void> {
    await this.captureAction(
      this.personalTrace,
      'Funcionario dado de baja',
      () => firstValueFrom(this.api.deactivateEmployee(this.employeeDeleteId)),
      async () => this.refreshCatalogs(),
      () => (this.employeeDeleteId = 0)
    );
  }

  protected async deleteEmployee(): Promise<void> {
    await this.captureAction(
      this.personalTrace,
      'Funcionario eliminado',
      () => firstValueFrom(this.api.deleteEmployee(this.employeeDeleteId)),
      async () => this.refreshCatalogs(),
      () => (this.employeeDeleteId = 0)
    );
  }

  protected async lookupEmployeeById(): Promise<void> {
    await this.captureAction(
      this.personalTrace,
      'Consulta por ID completada',
      () => firstValueFrom(this.api.getEmployee(this.employeeLookupId)),
      undefined,
      undefined
    );
  }

  protected async lookupEmployeeByCi(): Promise<void> {
    await this.captureAction(
      this.personalTrace,
      'Consulta por CI completada',
      () => firstValueFrom(this.api.getEmployeeByCi(this.employeeLookupCi)),
      undefined,
      undefined
    );
  }

  protected async listEmployeesByDepartment(): Promise<void> {
    await this.captureAction(
      this.personalTrace,
      'Listado por departamento completado',
      () => firstValueFrom(this.api.listEmployeesByDepartment(this.employeesByDepartmentId)),
      undefined,
      undefined
    );
  }

  protected async countEmployees(): Promise<void> {
    await this.captureAction(
      this.personalTrace,
      'Conteo de funcionarios completado',
      () => firstValueFrom(this.api.countEmployees(this.employeeCountFiltersToQuery())),
      undefined,
      undefined
    );
  }

  protected async getVacationBalance(): Promise<void> {
    await this.captureAction(
      this.vacationsTrace,
      'Balance de vacaciones consultado',
      () => firstValueFrom(this.api.getVacationBalance(this.vacationLookupEmployeeId)),
      undefined,
      undefined
    );
  }

  protected async getVacationEligibility(): Promise<void> {
    await this.captureAction(
      this.vacationsTrace,
      'Elegibilidad de vacaciones consultada',
      () => firstValueFrom(this.api.getVacationEligibility(this.vacationLookupEmployeeId)),
      undefined,
      undefined
    );
  }

  protected async createVacationRequest(): Promise<void> {
    await this.captureAction(
      this.vacationsTrace,
      'Solicitud de vacaciones creada',
      () => firstValueFrom(this.api.createVacationRequest(this.vacationRequestForm)),
      undefined,
      undefined
    );
  }

  protected async approveVacationRequest(): Promise<void> {
    await this.captureAction(
      this.vacationsTrace,
      'Solicitud aprobada',
      () => firstValueFrom(this.api.approveVacationRequest(this.vacationRequestId, this.vacationReview)),
      undefined,
      undefined
    );
  }

  protected async rejectVacationRequest(): Promise<void> {
    await this.captureAction(
      this.vacationsTrace,
      'Solicitud rechazada',
      () => firstValueFrom(this.api.rejectVacationRequest(this.vacationRequestId, this.vacationReview)),
      undefined,
      undefined
    );
  }

  protected async listVacationRequests(): Promise<void> {
    await this.captureAction(
      this.vacationsTrace,
      'Listado de vacaciones completado',
      () => firstValueFrom(this.api.listVacationRequestsByEmployee(this.vacationListEmployeeId, this.vacationListFilters())),
      undefined,
      undefined
    );
  }

  protected async lookupVacationRequest(): Promise<void> {
    await this.captureAction(
      this.vacationsTrace,
      'Solicitud individual consultada',
      () => firstValueFrom(this.api.getVacationRequest(this.vacationRequestId)),
      undefined,
      undefined
    );
  }

  protected async generateContract(): Promise<void> {
    await this.captureAction(
      this.contractsTrace,
      'Contrato generado',
      () => firstValueFrom(this.api.generateContract(this.contractGenerateForm)),
      async () => this.refreshCatalogs(),
      undefined
    );
  }

  protected async lookupContractById(): Promise<void> {
    await this.captureAction(
      this.contractsTrace,
      'Contrato consultado',
      () => firstValueFrom(this.api.getContract(this.contractLookupId)),
      undefined,
      undefined
    );
  }

  protected async listContractsByEmployee(): Promise<void> {
    await this.captureAction(
      this.contractsTrace,
      'Contratos por funcionario listados',
      () => firstValueFrom(this.api.listContractsByEmployee(this.contractListEmployeeId, this.contractListFilters())),
      undefined,
      undefined
    );
  }

  protected async generatePaySlip(): Promise<void> {
    await this.captureAction(
      this.payrollTrace,
      'Boleta generada',
      () => firstValueFrom(this.api.generatePaySlip(this.paySlipGenerateForm)),
      async () => this.refreshCatalogs(),
      undefined
    );
  }

  protected async lookupPaySlipById(): Promise<void> {
    await this.captureAction(
      this.payrollTrace,
      'Boleta consultada',
      () => firstValueFrom(this.api.getPaySlip(this.paySlipLookupId)),
      undefined,
      undefined
    );
  }

  protected async listPaySlipsByEmployee(): Promise<void> {
    await this.captureAction(
      this.payrollTrace,
      'Boletas por funcionario listadas',
      () => firstValueFrom(this.api.listPaySlipsByEmployee(this.paySlipListEmployeeId, this.paySlipListFilters())),
      undefined,
      undefined
    );
  }

  protected async listPaySlipsByEmployeeAlias(): Promise<void> {
    await this.captureAction(
      this.payrollTrace,
      'Alias de boletas por funcionario consultado',
      () => firstValueFrom(this.api.listPaySlipsByEmployeeAlias(this.paySlipAliasEmployeeId, this.paySlipListFilters())),
      undefined,
      undefined
    );
  }

  protected addPayrollDetail(): void {
    this.paySlipGenerateForm.details = [...this.paySlipGenerateForm.details, { concept_id: 0, amount: 0 }];
  }

  protected removePayrollDetail(index: number): void {
    this.paySlipGenerateForm.details = this.paySlipGenerateForm.details.filter((_, currentIndex) => currentIndex !== index);
    if (this.paySlipGenerateForm.details.length === 0) {
      this.paySlipGenerateForm.details = [{ concept_id: 0, amount: 0 }];
    }
  }

  protected trackByIndex(index: number): number {
    return index;
  }

  protected serviceLabel(service: ServiceCard): string {
    return service.status === 'online' ? 'ONLINE' : service.status === 'loading' ? 'CARGANDO' : 'OFFLINE';
  }

  protected summaryHint(service: ServiceCard): string {
    return `${service.baseUrl} · ${service.detail}`;
  }

  private async captureAction<T>(
    trace: WritableSignal<string>,
    successLabel: string,
    action: () => Promise<T>,
    after?: () => Promise<void>,
    reset?: () => void
  ): Promise<T | void> {
    this.errorMessage.set('');
    this.loading.set(true);

    try {
      const result = await action();
      trace.set(this.prettyPrint(result ?? successLabel));
      this.banner.set(successLabel);
      if (after) {
        await after();
      }
      if (reset) {
        reset();
      }
      return result;
    } catch (error) {
      const message = this.describeError(error);
      trace.set(message);
      this.errorMessage.set(message);
      this.banner.set(`${successLabel} falló.`);
    } finally {
      this.loading.set(false);
    }
  }

  private async syncSectionLookups(employeeId: number, vacationRequestId: number, contractId: number, paySlipId: number): Promise<void> {
    this.vacationLookupEmployeeId = employeeId;
    this.vacationRequestForm.employee_id = employeeId;
    this.vacationListEmployeeId = employeeId;
    this.contractGenerateForm.employee_id = employeeId;
    this.contractLookupId = contractId;
    this.contractListEmployeeId = employeeId;
    this.paySlipGenerateForm.employee_id = employeeId;
    this.paySlipLookupId = paySlipId;
    this.paySlipListEmployeeId = employeeId;
    this.paySlipAliasEmployeeId = employeeId;
    this.employeeLookupId = employeeId;
    this.employeeLookupCi = '';
    this.vacationRequestId = vacationRequestId;
  }

  private toServiceCard(
    name: string,
    baseUrl: string,
    docsUrl: string,
    health: MicroserviceHealth
  ): ServiceCard {
    return {
      name,
      baseUrl,
      docsUrl,
      status: health.status === 'healthy' ? 'online' : 'offline',
      detail: `${health.service} · ${health.database} · v${health.version}`,
    };
  }

  private prettyPrint(value: unknown): string {
    return typeof value === 'string' ? value : JSON.stringify(value, null, 2);
  }

  private describeError(error: unknown): string {
    if (error instanceof HttpErrorResponse) {
      if (typeof error.error === 'string') {
        return `${error.status} ${error.statusText}: ${error.error}`;
      }

      if (error.error?.detail) {
        return `${error.status} ${error.statusText}: ${error.error.detail}`;
      }

      return `${error.status} ${error.statusText}: ${error.message}`;
    }

    if (error instanceof Error) {
      return error.message;
    }

    return 'Error desconocido al consumir el backend.';
  }

  private cleanDepartmentPayload(payload: DepartmentPayload | { name: string; description?: string | null }): DepartmentPayload {
    return {
      name: payload.name.trim(),
      description: payload.description?.trim() || null,
    };
  }

  private cleanPositionPayload(payload: PositionPayload | { name: string; base_salary: number }): PositionPayload {
    return {
      name: payload.name.trim(),
      base_salary: Number(payload.base_salary),
    };
  }

  private cleanEmployeeUpdatePayload(payload: EmployeeUpdatePayload): EmployeeUpdatePayload {
    return {
      ...payload,
      first_name: payload.first_name?.trim() || undefined,
      last_name: payload.last_name?.trim() || undefined,
      email: payload.email?.trim() || undefined,
      phone: payload.phone?.trim() || null,
      status: payload.status?.trim() || undefined,
    };
  }

  private employeeCountFiltersToQuery(): { status?: string; department_id?: number } {
    return {
      status: this.employeeCountFilters.status.trim() || undefined,
      department_id: this.employeeCountFilters.department_id || undefined,
    };
  }

  private vacationListFilters(): { status?: string; skip?: number; limit?: number } {
    return {
      status: this.vacationStatusFilter.trim() || undefined,
      skip: 0,
      limit: 25,
    };
  }

  private contractListFilters(): { status?: string; skip?: number; limit?: number } {
    return {
      status: this.contractStatusFilter.trim() || undefined,
      skip: 0,
      limit: 25,
    };
  }

  private paySlipListFilters(): { skip?: number; limit?: number } {
    return {
      skip: 0,
      limit: 25,
    };
  }

  private resetDepartmentCreate(): void {
    this.departmentCreate = { name: '', description: '' };
  }

  private resetPositionCreate(): void {
    this.positionCreate = { name: '', base_salary: 0 };
  }

  private resetEmployeeCreate(): void {
    this.employeeCreate = {
      ci: '',
      first_name: '',
      last_name: '',
      email: '',
      phone: '',
      hire_date: new Date().toISOString().slice(0, 10),
      current_salary: 0,
      department_id: this.departments()[0]?.id ?? 0,
      position_id: this.positions()[0]?.id ?? 0,
    };
  }

  private syncCatalogDefaults(): void {
    if (!this.departmentCreate.department_id) {
      this.employeeCreate.department_id = this.departments()[0]?.id ?? this.employeeCreate.department_id;
    }
    if (!this.employeeCreate.position_id) {
      this.employeeCreate.position_id = this.positions()[0]?.id ?? this.employeeCreate.position_id;
    }
    if (!this.contractGenerateForm.contract_type_id && this.contractTypes().length > 0) {
      this.contractGenerateForm.contract_type_id = null;
    }
    if (!this.paySlipGenerateForm.details.length) {
      this.paySlipGenerateForm.details = [{ concept_id: this.paymentConcepts()[0]?.id ?? 0, amount: 0 }];
    } else if (this.paySlipGenerateForm.details[0].concept_id === 0) {
      this.paySlipGenerateForm.details[0].concept_id = this.paymentConcepts()[0]?.id ?? 0;
    }
  }

  private addDays(date: Date, daysToAdd: number): string {
    const current = new Date(date);
    current.setDate(current.getDate() + daysToAdd);
    return current.toISOString().slice(0, 10);
  }
}
