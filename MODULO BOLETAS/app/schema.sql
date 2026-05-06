CREATE TABLE IF NOT EXISTS employees (
  id SERIAL PRIMARY KEY,
  ci VARCHAR(20) NOT NULL UNIQUE,
  first_name VARCHAR(100) NOT NULL,
  last_name VARCHAR(100) NOT NULL,
  email VARCHAR(255) UNIQUE,
  phone VARCHAR(30),
  hire_date DATE NOT NULL DEFAULT CURRENT_DATE,
  status VARCHAR(20) NOT NULL DEFAULT 'Activo'
    CHECK (status IN ('Activo', 'Baja', 'Suspendido'))
);

CREATE TABLE IF NOT EXISTS payment_concepts (
  id SERIAL PRIMARY KEY,
  name VARCHAR(120) NOT NULL UNIQUE,
  type VARCHAR(20) NOT NULL CHECK (type IN ('Ingreso', 'Egreso'))
);

CREATE TABLE IF NOT EXISTS pay_slips (
  id SERIAL PRIMARY KEY,
  employee_id INTEGER NOT NULL REFERENCES employees(id),
  period_month SMALLINT NOT NULL CHECK (period_month BETWEEN 1 AND 12),
  period_year INTEGER NOT NULL CHECK (period_year >= 2000),
  payment_date DATE NOT NULL DEFAULT CURRENT_DATE,
  total_net NUMERIC(12, 2) NOT NULL DEFAULT 0,
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  UNIQUE (employee_id, period_month, period_year)
);

CREATE TABLE IF NOT EXISTS pay_slip_details (
  id SERIAL PRIMARY KEY,
  pay_slip_id INTEGER NOT NULL REFERENCES pay_slips(id) ON DELETE CASCADE,
  concept_id INTEGER NOT NULL REFERENCES payment_concepts(id),
  amount NUMERIC(12, 2) NOT NULL CHECK (amount >= 0),
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_pay_slips_employee_period
  ON pay_slips (employee_id, period_year, period_month);

CREATE INDEX IF NOT EXISTS idx_pay_slip_details_payslip
  ON pay_slip_details (pay_slip_id);

CREATE INDEX IF NOT EXISTS idx_pay_slip_details_concept
  ON pay_slip_details (concept_id);

