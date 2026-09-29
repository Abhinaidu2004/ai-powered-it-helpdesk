# AI-Powered IT Help Desk System

An AI-powered IT Help Desk platform for managing IT support tickets, users, assignments, ticket workflows, and intelligent support recommendations.

## Features

* Role-based authentication and authorization
* Employee, Agent, and Admin dashboards
* Ticket creation, tracking, assignment, and resolution
* Ticket comments and history tracking
* Priority and category management
* AI-based ticket classification
* AI-based ticket summarization
* Automated solution recommendations
* Semantic search using embeddings
* RAG-based solution generation
* RESTful APIs using FastAPI
* MySQL database integration
* JWT authentication
* Role-based API security

## Tech Stack

### Backend

* Python
* FastAPI
* REST APIs
* JWT
* MySQL

### Frontend

* HTML
* CSS
* JavaScript

### AI / Machine Learning

* Scikit-learn
* TF-IDF
* Logistic Regression
* Transformers
* Sentence Transformers
* Embeddings
* RAG
* Ollama / Llama 3

### Tools

* Git
* GitHub
* VS Code

## System Architecture

```text
                    AI-Powered IT Help Desk
                              |
        +---------------------+---------------------+
        |                     |                     |
     Frontend              Backend               AI Layer
 HTML/CSS/JavaScript       FastAPI              Classification
        |                     |                  Summarization
        |                     |                  Embeddings
        |                     |                  RAG / LLM
        |                     |
        +---------------------+
                              |
                           MySQL
                              |
                    Users / Tickets /
                    Comments / History
```

## User Roles

### Employee

* Create tickets
* View own tickets
* Add comments
* Track ticket status
* View AI recommendations

### Agent

* View assigned tickets
* Update ticket status
* Work on assigned issues
* Add comments
* Resolve tickets

### Admin

* View all tickets
* Assign tickets to agents
* Manage users
* Monitor ticket workflows
* Access administrative functions

## AI Features

### Ticket Classification

The system analyzes the ticket title and description and predicts:

* Category
* Priority

Categories include:

* Network
* Hardware
* Software
* Account

### Ticket Summarization

Long ticket descriptions can be summarized using a transformer-based model.

### Solution Recommendations

The system analyzes the issue and provides possible troubleshooting solutions.

### Semantic Search

Sentence embeddings are used to identify tickets with similar meanings rather than relying only on exact keywords.

### RAG

Relevant resolved tickets are retrieved and used as context for generating more useful IT support solutions.

## Security

The application includes:

* JWT authentication
* Password hashing
* Role-based authorization
* Protected API endpoints
* Ticket ownership validation
* Agent assignment validation
* Unauthorized-access testing

## Project Structure

```text
IT-Helpdesk/
│
├── backend/
│   ├── main.py
│   ├── ai_classifier.py
│   ├── ai_embeddings.py
│   ├── ai_rag.py
│   ├── ai_similarity.py
│   ├── ai_solutions.py
│   └── ai_summarizer.py
│
├── frontend/
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── agent-dashboard.html
│   ├── admin-dashboard.html
│   ├── create-ticket.html
│   ├── ticket.html
│   ├── app.js
│   └── style.css
│
├── requirements.txt
├── .gitignore
└── README.md
```

## Installation

Clone the repository:

```bash
git clone https://github.com/Abhinaidu2004/ai-powered-it-helpdesk.git
cd ai-powered-it-helpdesk
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate it on Windows:

```powershell
.\venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file inside `backend/` and configure the database and application secrets.

Example:

```env
SECRET_KEY=your-secret-key
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your-mysql-password
DB_NAME=it_helpdesk
```

Start the FastAPI server:

```bash
cd backend
uvicorn main:app --reload
```

API documentation will be available at:

```text
http://127.0.0.1:8000/docs
```

## Database

The project uses MySQL.

Database:

```text
it_helpdesk
```

Main tables:

```text
users
tickets
ticket_comments
ticket_history
```

## Future Improvements

* Cloud deployment
* Production database
* Email notifications
* Advanced analytics
* Automated ticket assignment
* Improved AI model training
* Monitoring and logging
* Docker support
* CI/CD pipeline

## Author

**SAI KRISHNA NATHI**

Python Developer | Backend Development | SQL | AI/NLP

````

### Step 2 — Save and check Git

After saving `README.md`, run:

```powershell
git status
````

You should see something similar to:

```text
Untracked files:
    README.md
```

Then run:

```powershell
git add README.md
git commit -m "Add project README"
git push
```

### Step 3

Send me the output of:

```powershell
git status
```

Then we'll verify the README on GitHub and move to **screenshots + GitHub portfolio polish**.
