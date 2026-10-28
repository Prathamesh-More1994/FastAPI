\# TodoApp — FastAPI Portfolio Project



A production-oriented Todo application built with \*\*FastAPI\*\*, \*\*SQLAlchemy\*\*, \*\*PostgreSQL\*\*, \*\*Docker\*\*, and \*\*AWS\*\*.



This project started as a simple FastAPI Todo application and was progressively refactored into a layered architecture with configuration management, authentication, database migrations, automated testing, containerization, AWS deployment, and CI/CD.



\## Features



\- User registration and authentication

\- Cookie-based JWT authentication

\- Password hashing with bcrypt

\- Role-based access for admin functionality

\- Todo CRUD operations

\- Todo ownership enforcement

\- Pydantic request/response validation

\- SQLAlchemy ORM

\- PostgreSQL database

\- Alembic database migrations

\- Centralized application configuration

\- Repository/service architecture

\- Automated tests with pytest

\- 98% test coverage

\- Dockerized application

\- Nginx reverse proxy

\- AWS EC2 deployment

\- AWS RDS PostgreSQL

\- GitHub Actions CI/CD

\- Production-style environment variable configuration

\- Health-check endpoint



\## Architecture



The application follows a layered architecture:



```text

Client

&#x20; │

&#x20; ▼

Router

&#x20; │

&#x20; ▼

Service

&#x20; │

&#x20; ▼

Repository

&#x20; │

&#x20; ▼

SQLAlchemy

&#x20; │

&#x20; ▼

PostgreSQL

```



\### Responsibilities



\*\*Routers\*\*

\- Handle HTTP requests and responses

\- Validate incoming request data

\- Handle authentication and authorization

\- Return appropriate HTTP errors



\*\*Services\*\*

\- Contain application/business logic

\- Coordinate operations between routers and repositories



\*\*Repositories\*\*

\- Handle database persistence and queries

\- Keep database operations separate from business logic



\*\*Models\*\*

\- Define SQLAlchemy database models



\*\*Schemas\*\*

\- Define API request and response contracts using Pydantic



\*\*Core\*\*

\- Application configuration

\- Security and authentication utilities



\## Project Structure



```text

TodoApp/

├── main.py

│

├── core/

│   ├── config.py

│   └── security.py

│

├── database/

│   ├── database.py

│   └── dependencies.py

│

├── models/

│   ├── user.py

│   └── todo.py

│

├── repositories/

│   ├── admin\_repository.py

│   └── todo\_repository.py

│

├── routers/

│   ├── admin.py

│   ├── auth.py

│   ├── todos.py

│   └── users.py

│

├── schemas/

│   ├── auth.py

│   ├── todo.py

│   └── user.py

│

├── services/

│   ├── admin\_service.py

│   └── todo\_service.py

│

├── templates/

├── static/

│

├── alembic/

│   └── versions/

│

└── test/

&#x20;   ├── test\_admin.py

&#x20;   ├── test\_auth.py

&#x20;   ├── test\_main.py

&#x20;   ├── test\_todos.py

&#x20;   ├── test\_todo\_repository.py

&#x20;   ├── test\_todo\_service.py

&#x20;   └── test\_users.py

```



\## Technology Stack



| Technology | Purpose |

|---|---|

| Python | Application language |

| FastAPI | Web framework / REST API |

| SQLAlchemy | ORM and database access |

| Pydantic | Request/response validation |

| PostgreSQL | Production database |

| SQLite | Test database |

| Alembic | Database migrations |

| pytest | Automated testing |

| Docker | Application containerization |

| Nginx | Reverse proxy |

| AWS EC2 | Application hosting |

| AWS RDS | Managed PostgreSQL database |

| GitHub Actions | CI/CD |



\## Authentication \& Security



Authentication uses JWT access tokens stored in an \*\*HttpOnly cookie\*\*.



Passwords are hashed using bcrypt and are never returned through API response schemas.



Application secrets and database credentials are supplied through environment variables rather than being hardcoded into the application.



The repository excludes `.env` files from version control.



Example environment configuration:



```env

DATABASE\_URL=

SECRET\_KEY=

ALGORITHM=HS256

ACCESS\_TOKEN\_EXPIRE\_MINUTES=20

COOKIE\_SECURE=false

```



For production HTTPS deployments, `COOKIE\_SECURE` should be enabled.



\## Database Migrations



Alembic is used to manage database schema changes.



The application does not rely on SQLAlchemy `create\_all()` during startup. Database schema changes are applied through migrations.



To upgrade the database:



```bash

alembic -c alembic.ini upgrade head

```



\## Testing



The project uses pytest for automated testing.



Run the test suite with:



```bash

pytest

```



The current test suite achieves approximately \*\*98% coverage\*\*.



Dependency consistency is also checked with:



```bash

pip check

```



\## Running Locally



\### 1. Clone the repository



```bash

git clone https://github.com/Prathamesh-More1994/FastAPI.git

cd FastAPI

```



\### 2. Create a virtual environment



```bash

python -m venv .venv

```



Activate it on Windows:



```powershell

.venv\\Scripts\\Activate.ps1

```



\### 3. Install dependencies



```bash

pip install -r requirements.txt

```



\### 4. Configure environment variables



Create a `.env` file based on `.env.example`:



```env

DATABASE\_URL=

SECRET\_KEY=

ALGORITHM=HS256

ACCESS\_TOKEN\_EXPIRE\_MINUTES=20

COOKIE\_SECURE=false

```



Do not commit `.env` to Git.



\### 5. Run database migrations



```bash

alembic -c alembic.ini upgrade head

```



\### 6. Start the application



```bash

uvicorn TodoApp.main:app --reload

```



The application will be available at:



```text

http://127.0.0.1:8000

```



FastAPI interactive documentation:



```text

http://127.0.0.1:8000/docs

```



Health check:



```text

http://127.0.0.1:8000/healthy

```



\## Docker



Build the image:



```bash

docker build -t todoapp:latest .

```



Run the container:



```bash

docker run -d \\

&#x20; --name todoapp \\

&#x20; --env-file .env \\

&#x20; -p 8000:8000 \\

&#x20; todoapp:latest

```



The container exposes FastAPI on port `8000`.



\## AWS Deployment



The deployed architecture is:



```text

&#x20;                   Internet

&#x20;                      │

&#x20;                      ▼

&#x20;               AWS EC2 :80

&#x20;                      │

&#x20;                      ▼

&#x20;                   Nginx

&#x20;                      │

&#x20;                      ▼

&#x20;            Docker / FastAPI :8000

&#x20;                      │

&#x20;                      ▼

&#x20;             AWS RDS PostgreSQL

&#x20;                      :5432

```



The application is hosted on an AWS EC2 instance running Docker.



PostgreSQL is hosted using AWS RDS.



Nginx acts as the reverse proxy and forwards HTTP traffic to the FastAPI container.



Database access is restricted so that PostgreSQL is not directly exposed to the public internet.



\## CI/CD



GitHub Actions runs the CI/CD pipeline whenever changes are pushed to `main`.



```text

Developer

&#x20;   │

&#x20;   ▼

Git commit

&#x20;   │

&#x20;   ▼

GitHub

&#x20;   │

&#x20;   ▼

Run tests

&#x20;   │

&#x20;   ├── pytest

&#x20;   └── pip check

&#x20;   │

&#x20;   ▼

SSH to EC2

&#x20;   │

&#x20;   ▼

git pull

&#x20;   │

&#x20;   ▼

Docker build

&#x20;   │

&#x20;   ▼

Alembic migration

&#x20;   │

&#x20;   ▼

Restart application container

&#x20;   │

&#x20;   ▼

Health check

```



Deployment only runs after the test job succeeds.



The EC2 server stores its runtime environment configuration separately from the Git repository.



\## Engineering Decisions



\### Layered architecture



Business logic and database operations are separated from HTTP routing. This makes the application easier to test and maintain.



\### Environment-based configuration



Database credentials and application secrets are supplied through environment variables instead of being hardcoded.



\### Alembic migrations



Database schema changes are version-controlled and reproducible instead of being created automatically at application startup.



\### Docker



The application runs in a reproducible Python environment independent of the host Python installation.



\### Automated testing



Tests run before deployment through GitHub Actions, preventing a deployment when the test suite fails.



\### AWS separation



The application and database are separated:



```text

EC2 → FastAPI application

RDS → PostgreSQL database

```



This avoids running the production database directly inside the application container.



\## What This Project Demonstrates



This project demonstrates practical experience with:



\- FastAPI application development

\- REST API design

\- SQLAlchemy and PostgreSQL

\- Authentication and authorization

\- JWT and cookie-based authentication

\- Pydantic validation

\- Layered application architecture

\- Repository/service separation

\- Automated testing

\- Test coverage

\- Database migrations

\- Docker

\- Nginx

\- AWS EC2

\- AWS RDS

\- GitHub Actions

\- CI/CD

\- Environment and secret management

\- Production-oriented deployment practices



\## Project Status



The application is deployed on AWS and uses an automated GitHub Actions deployment pipeline.



Further improvements can include HTTPS/domain configuration, more advanced deployment strategies, and additional application features.

