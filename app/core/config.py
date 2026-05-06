import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = "Microservicio de Vacaciones - ARCA"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/vacaciones_db")

settings = Settings()