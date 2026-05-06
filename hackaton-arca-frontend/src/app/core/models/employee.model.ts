export interface Department {
  id: number;
  name: string;
  description?: string;
}

export type NewDepartment = Omit<Department, 'id'>;

export interface Position {
  id: number;
  name: string;
  description?: string;
  department_id?: number;
}

export type NewPosition = Omit<Position, 'id'>;

export interface Employee {
  id: number;
  ci: string;
  name: string;
  email: string;
  phone?: string;
  position?: string;
  department_id?: number;
  department?: string;
  status: string;
  hire_date: string;
  end_date?: string;
}

export type NewEmployee = Omit<Employee, 'id'>;

export interface EmployeeCount {
  count: number;
}
