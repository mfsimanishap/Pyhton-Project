# Income Tax Calculator

A web-based Indian Income Tax Calculator developed using Python, FastAPI, Streamlit, SQLAlchemy, and SQLite.

The application allows users to register, log in, calculate income tax under the Old and New Tax Regimes, compare tax liabilities, and view their previous tax calculations.

## Features

- User registration and login.
- Password hashing for secure password storage.
- JWT-based authentication.
- Income tax calculation under the Old Tax Regime.
- Income tax calculation under the New Tax Regime.
- Comparison of both tax regimes.
- HRA exemption calculation.
- Section 80C deduction calculation.
- Automatic identification of the lower calculated tax liability.
- User-specific tax calculation history.
- REST API using FastAPI.
- Interactive frontend using Streamlit.
- SQLite database integration using SQLAlchemy.
- Database migrations using Alembic.
- Docker containerization.
- Automated testing with pytest.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Backend programming language |
| FastAPI | REST API development |
| Streamlit | Frontend user interface |
| Pydantic | Data validation |
| SQLAlchemy | Database ORM |
| SQLite | Database |
| Alembic | Database migrations |
| PyJWT | JWT authentication |
| pwdlib | Password hashing |
| pytest | Automated testing |
| pytest-cov | Test coverage |
| Ruff | Linting and formatting |
| MyPy | Static type checking |
| Docker | Application containerization |

## Project Structure

```text
tax-calculator/
│
├── app/
│   ├── api/
│   │   └── routes/
│   │       ├── auth.py
│   │       └── tax.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   ├── token.py
│   │   └── dependencies.py
│   │
│   ├── database/
│   │   ├── base.py
│   │   ├── connection.py
│   │   └── dependencies.py
│   │
│   ├── models/
│   │   ├── user.py
│   │   └── tax_calculation.py
│   │
│   ├── schemas/
│   ├── services/
│   └── main.py
│
├── frontend/
│   ├── app.py
│   └── Dockerfile
│
├── migrations/
│
├── tests/
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── pyproject.toml
├── alembic.ini
└── README.md
```

## Prerequisites

Install the following before running the application:

- Python 3.12 or later
- pip
- Docker Desktop (optional)
- Git (optional)

## Local Installation and Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd tax-calculator
```

### 2. Create a Virtual Environment

For Windows PowerShell:

```powershell
python -m venv .venv
```

### 3. Activate the Virtual Environment

```powershell
.venv\Scripts\Activate.ps1
```

### 4. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 5. Configure Environment Variables

Create a `.env` file in the project root.

Example:

```env
SECRET_KEY=your-strong-secret-key
DATABASE_PATH=tax_calculator.db
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
LOG_LEVEL=INFO
```

Use a strong, randomly generated secret key. Do not commit `.env` files to version control.
The application writes logs to the console. Set `LOG_LEVEL` to `DEBUG`, `INFO`,
`WARNING`, `ERROR`, or `CRITICAL` to control verbosity.

### 6. Run Database Migrations

```powershell
alembic upgrade head
```

### 7. Start the FastAPI Backend

```powershell
uvicorn app.main:app --reload
```

Backend URL:

```text
http://127.0.0.1:8000
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

### 8. Start the Streamlit Frontend

Open another terminal, activate the virtual environment, and execute:

```powershell
streamlit run frontend/app.py
```

Frontend URL:

```text
http://localhost:8501
```

## Running with Docker

Docker Compose runs the backend and frontend services together.

### Build and Start Containers

```powershell
docker compose up --build -d
```

### Check Running Containers

```powershell
docker compose ps
```

### View Backend Logs

```powershell
docker compose logs --tail=100 backend
```

### View Frontend Logs

```powershell
docker compose logs --tail=100 frontend
```

### Stop Containers

```powershell
docker compose down
```

### Start Existing Containers

```powershell
docker compose up -d
```

### Database Persistence

The application uses a Docker named volume to persist SQLite database data.

Database location inside the backend container:

```text
/app/data/tax_calculator.db
```

The Docker Compose configuration mounts a named volume:

```yaml
volumes:
  tax-calculator-data:
```

The database remains available when containers are stopped or removed using `docker compose down`.

**Important:** Avoid using `docker compose down -v` unless you intentionally want to delete the database volume and its stored data.

## Authentication

The application implements JWT-based authentication.

### User Registration

Users can create an account using:

- Name
- Email
- Password

Passwords are hashed before being stored in the database.

### User Login

Users authenticate using their registered email and password.

After successful authentication, the backend generates an access token.

### Protected API Endpoints

Protected endpoints require a valid JWT access token in the Authorization header.

```http
Authorization: Bearer <access-token>
```

The backend validates the token and identifies the authenticated user before allowing access to protected resources.

## API Endpoints

| Method | Endpoint | Description | Authentication |
|---|---|---|---|
| POST | `/auth/register` | Register a new user | No |
| POST | `/auth/login` | Authenticate user and generate token | No |
| GET | `/auth/me` | Retrieve current user information | Yes |
| POST | `/tax/calculate` | Calculate income tax | Yes |
| GET | `/tax/history` | Retrieve user's calculation history | Yes |

For complete request and response details, access the FastAPI Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

## Tax Calculation Logic

The application implements simplified tax calculations for the Old and New Tax Regimes.

### Old Tax Regime

| Taxable Income | Tax Rate |
|---|---:|
| Up to Rs. 2,50,000 | 0% |
| Rs. 2,50,001 - Rs. 5,00,000 | 5% |
| Rs. 5,00,001 - Rs. 10,00,000 | 20% |
| Above Rs. 10,00,000 | 30% |

### New Tax Regime

| Taxable Income | Tax Rate |
|---|---:|
| Up to Rs. 4,00,000 | 0% |
| Rs. 4,00,001 - Rs. 8,00,000 | 5% |
| Rs. 8,00,001 - Rs. 12,00,000 | 10% |
| Rs. 12,00,001 - Rs. 16,00,000 | 15% |
| Rs. 16,00,001 - Rs. 20,00,000 | 20% |
| Rs. 20,00,001 - Rs. 24,00,000 | 25% |
| Above Rs. 24,00,000 | 30% |

### Other Calculation Rules

- Standard deduction under the Old Regime: Rs. 50,000.
- Standard deduction under the New Regime: Rs. 75,000.
- Section 80C deduction limit: Rs. 1,50,000 under the Old Regime.
- HRA exemption is calculated using a simplified formula.
- Health and Education Cess: 4%.
- The application can compare both regimes and identify the lower calculated tax liability.

**Disclaimer:** The tax calculation rules are simplified for learning and demonstration purposes. This application is not a substitute for current Indian income tax laws or professional tax advice. Tax slabs, deductions, and exemptions may change between financial years.

## Database Design

The application uses SQLite with SQLAlchemy ORM.

### Users Table

Stores registered user information:

- User ID
- Name
- Email
- Hashed password
- Created date

### Tax Calculations Table

Stores individual tax calculation records:

- Calculation ID
- User ID
- Request data
- Result data
- Created date

Each calculation is associated with the authenticated user.

### Database Migrations

Alembic manages database schema changes.

Run migrations:

```powershell
alembic upgrade head
```

Create a new migration:

```powershell
alembic revision --autogenerate -m "migration description"
```

## Testing

Run all tests:

```powershell
python -m pytest
```

Run tests with coverage:

```powershell
python -m pytest --cov=app --cov-report=term-missing
```

## Code Quality

### Ruff Linting

```powershell
ruff check .
```

### Ruff Formatting

```powershell
ruff format .
```

### MyPy Type Checking

```powershell
mypy app
```

These tools help maintain code quality, consistent formatting, and static type safety.

## Security Considerations

- Passwords are hashed before being stored.
- JWT authentication protects sensitive API endpoints.
- User calculation history is associated with the authenticated user.
- Strong secret keys should be configured for production.
- Environment variables should be used for sensitive configuration.
- HTTPS should be enabled in production.
- Database backups should be maintained.

## Future Improvements

- Financial-year-specific tax calculations.
- Additional tax deductions and exemptions.
- Improved tax calculation accuracy.
- Downloadable tax reports.
- Dashboard analytics.
- Production deployment and monitoring.

## Project Purpose

This project demonstrates practical Python development, REST API development, authentication, database integration, automated testing, code quality tools, and Docker-based deployment.

It is intended as a learning and portfolio project for demonstrating backend and full-stack Python development skills.
