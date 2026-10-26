# Wallet Data Pipeline

**Python · PostgreSQL · pandas · SQL · ETL · REST API**

A Python-based ETL pipeline that extracts financial transactions from a Spring Boot Digital Wallet API, validates and transforms the data, and loads it into PostgreSQL for analytical processing.

The project focuses on **incremental data extraction, data quality, idempotent loading, and reliable transaction processing**.

## Features

- **REST API Integration** — Extracts wallet transactions from a Spring Boot REST API using JWT authentication and pagination.
- **Data Validation** — Validates incoming transaction records and separates invalid data.
- **Data Transformation** — Processes monetary values, timestamps, and transaction information before loading.
- **Incremental ETL** — Uses checkpoints and configurable overlap windows to process new data without repeatedly extracting the entire history.
- **Idempotent Loading** — Prevents duplicate records using PostgreSQL conflict handling.
- **Transactional Loading** — Ensures database changes are committed consistently.
- **Execution Tracking** — Records pipeline execution status, failures, and processing statistics.
- **Concurrency Control** — Prevents overlapping executions for the same wallet and data source.

## Tech Stack

| Technology | Purpose |
|---|---|
| Python | ETL application and pipeline orchestration |
| pandas | Data processing and transformation |
| PostgreSQL | Analytical data storage |
| SQL | Database operations and conflict handling |
| REST API | Communication with Spring Digital Wallet |
| JWT | Authenticated data extraction |

## Architecture

The pipeline follows the traditional **Extract, Transform, Load (ETL)** approach.

```text
Spring Digital Wallet
       |
       | REST API + JWT
       v
    Extraction
       |
       v
    Validation
       |
       v
  Transformation
       |
       v
 PostgreSQL Database
       |
       v
 Analytical Processing
```

### Extract

The pipeline authenticates with Spring Digital Wallet and retrieves transaction records through paginated REST API requests.

### Transform

Extracted records are validated and converted into a consistent format suitable for analytical storage. Invalid records are tracked separately.

### Load

Valid records are inserted into PostgreSQL using parameterized SQL statements and conflict handling to prevent duplication.

## Reliability & Data Consistency

The application includes several mechanisms designed to make repeated ETL executions reliable:

- **Incremental checkpoints** track the progress of successful data extraction.
- **Overlap windows** allow previously processed time ranges to be revisited.
- **Idempotent inserts** prevent duplicate transaction records.
- **Database transactions** protect related loading operations.
- **Run-level locking** prevents simultaneous processing of the same source and wallet.
- **Execution history** tracks successful and failed runs.

Each execution records processing statistics, including:

- Fetched records
- Valid records
- Rejected records
- Inserted records
- Skipped records

## Project Structure

```text
wallet-data-pipeline/
├── pipeline/             # ETL components
├── sql/                  # Database SQL scripts
├── tests/                # Automated tests
├── main.py               # Pipeline entry point
├── .env.example          # Environment configuration example
├── requirements.txt      # Application dependencies
└── requirements-dev.txt  # Development dependencies
```

## Getting Started

### Prerequisites

- Python
- PostgreSQL
- Running Spring Digital Wallet API
- A valid Digital Wallet user account

### 1. Clone the repository

```bash
git clone https://github.com/AdrianVittig/wallet-data-pipeline.git
cd wallet-data-pipeline
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

For development dependencies:

```bash
pip install -r requirements-dev.txt
```

### 4. Configure the environment

Copy `.env.example` to `.env` and configure the API and PostgreSQL connection settings.

```env
WALLET_API_URL=http://localhost:8084
WALLET_EMAIL=
WALLET_PASSWORD=

PIPELINE_OVERLAP_MINUTES=5

ANALYTICS_DB_HOST=localhost
ANALYTICS_DB_PORT=5432
ANALYTICS_DB_NAME=wallet_analytics
ANALYTICS_DB_USER=wallet_pipeline
ANALYTICS_DB_PASSWORD=
```

Create the analytics database and apply the SQL initialization scripts from the `sql/` directory before running the pipeline.

### 5. Run the pipeline

For incremental processing:

```bash
python main.py
```

For a full-history extraction:

```bash
python main.py --full-history
```

### 6. Run tests

```bash
python -m pytest
```

## Related Project

**[Spring Digital Wallet](https://github.com/AdrianVittig/spring-digital_wallet)**

The Java/Spring Boot backend application that provides wallet management, authentication, money transfers, and transaction history through REST APIs.

Together, these projects demonstrate backend development, API integration, database management, and data engineering using Java and Python.

## Project Status

**In active development.**

The current focus is reliable transaction extraction, validation, incremental processing, and analytical storage.

## Author

**Adrian Vitig**

[GitHub](https://github.com/AdrianVittig) · [LinkedIn](https://www.linkedin.com/in/adrianvitig/)