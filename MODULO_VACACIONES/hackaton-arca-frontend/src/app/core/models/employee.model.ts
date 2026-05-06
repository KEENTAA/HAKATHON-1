export interface Employee {
  id: number;
  name?: string;
  email?: string;
  position?: string;
}

export type NewEmployee = Omit<Employee, 'id'>;
