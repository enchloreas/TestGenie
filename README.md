# TestGenie

TestGenie is a FastAPI-based backend application designed to manage, store, and automate test cases. It uses SQLAlchemy for database interactions and Pydantic for request validation.

TestGenie helps QA engineers generate, manage, and integrate test cases from user stories and change requests.  
It provides seamless integration with Jira and GitHub Actions for CI/CD automation.

![Build Status](https://github.com/your-username/TestGenie/actions/workflows/ci.yml/badge.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## Table of Contents
- [Introduction](#testgenie)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Features

- Create, update, and list test cases
- SQLite/PostgreSQL support
- Ready for CI/CD and Docker deployment

## Tech Stack

- FastAPI
- SQLAlchemy
- Pydantic
- Pytest

## Project Structure

```
TestGenie/
├── app/                 # Main application code
│   ├── __init__.py      # Initialize app
│   ├── models.py        # Database models (SQLAlchemy)
│   ├── schemas.py       # Pydantic models for request validation
│   ├── crud.py          # CRUD operations
│   ├── main.py          # FastAPI app initialization
├── migrations/          # Database migrations (Alembic)
├── tests/               # Unit tests for the application
│   ├── test_main.py     # Example test file
├── .gitignore           # Files and directories to ignore in Git
├── requirements.txt     # Python dependencies
├── README.md            # Project documentation
└── venv/                # Virtual environment (not committed)
```

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/TestGenie.git
   cd TestGenie
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up the database:
   ```bash
   alembic upgrade head
   ```

5. Run the application:
   ```bash
   uvicorn app.main:app --reload
   ```

6. Access the API documentation at `http://127.0.0.1:8000/docs`.

## Usage

- To create test cases, use the `/testcases` endpoint.
- Integrate with Jira by configuring your `.env` file with Jira credentials.
- Automate CI/CD pipelines using the provided GitHub Actions workflows.

## Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bugfix:
   ```bash
   git checkout -b feature-name
   ```
3. Commit your changes and push to your fork.
4. Submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.