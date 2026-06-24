# StudyPlanner

[![Architecture Diagram](architecture_diagram_1782336040043.png)](architecture_diagram_1782336040043.png)

[![Workflow Diagram](workflow_diagram_1782336255641.png)](workflow_diagram_1782336255641.png)

---

## Overview
StudyPlanner is a web application that helps students organize their study tasks, schedule sessions, and receive notifications. It provides a clean UI, RESTful API backend, and integrates with a PostgreSQL database.

## Architecture
- **Frontend**: React (or any modern UI framework) – communicates with the backend via JSON APIs.
- **Backend**: Python FastAPI – handles authentication, task management, and scheduling.
- **Database**: PostgreSQL – stores users, tasks, schedules.
- **Auth Service**: OAuth2/JWT based authentication.
- **Scheduler**: Background worker (e.g., Celery) that sends reminder notifications.

## Installation
```bash
# Clone the repo (once created)
git clone https://github.com/mridul-tiwari-hub/studyplanner.git
cd studyplanner
# Create a virtual environment
python -m venv .venv
.venv\\Scripts\\activate  # on Windows
# Install dependencies
pip install -r requirements.txt
```

## Usage
1. Start the backend server:
```bash
uvicorn app:app --reload
```
2. Open the frontend (if separate) and point it to the backend URL.
3. Create an account, log in, and start adding study tasks.

## Development Guide
- **Running Tests**: `pytest`
- **Code Formatting**: `black .` and `isort .`
- **Database Migrations**: Use Alembic (`alembic upgrade head`)
- **Adding Features**: Follow the existing folder structure (`backend/`, `frontend/`).

## Contributing
Contributions are welcome! Please fork the repository, create a feature branch, and submit a pull request.

## License
This project is licensed under the MIT License.
