# AI-Powered IT Help Desk

An AI-powered IT support and ticket management system designed to help employees report technical issues and assist support teams with intelligent ticket analysis and troubleshooting.

## 🌐 Live Demo

The application is deployed and available online:

* **Frontend:** https://ai-powered-it-helpdesk-01.onrender.com
* **Backend API:** https://ai-powered-it-helpdesk-n0ua.onrender.com
* **API Documentation:** https://ai-powered-it-helpdesk-n0ua.onrender.com/docs

> **Note:** The application is hosted on Render's free tier, so the backend may take a few seconds to start after a period of inactivity.

## 🚀 Features

* 🔐 **JWT Authentication & Role-Based Access**

  * Employee, Agent, and Admin roles
  * Secure login and protected API endpoints

* 🎫 **Ticket Management**

  * Create and track IT support tickets
  * View ticket details, status, priority, and category
  * Add comments and maintain ticket history
  * Record ticket resolutions

* 🤖 **AI-Powered Assistance**

  * Automatic ticket classification
  * Priority prediction
  * Ticket summarization
  * Solution recommendations
  * Similar ticket search
  * Semantic search
  * RAG-based troubleshooting assistance

* 🗄️ **Database Management**

  * MySQL database
  * Stores users, tickets, comments, resolutions, and ticket history

* 🌐 **Deployment**

  * Frontend and backend deployed using Render
  * Source code managed with Git and GitHub

## 🛠️ Technology Stack

| Layer           | Technologies                               |
| --------------- | ------------------------------------------ |
| Frontend        | HTML, CSS, JavaScript                      |
| Backend         | Python, FastAPI                            |
| Database        | MySQL                                      |
| Authentication  | JWT                                        |
| AI/NLP          | Python, Embeddings, Similarity Search, RAG |
| Version Control | Git, GitHub                                |
| Deployment      | Render                                     |

## 🏗️ Architecture

```text
                    ┌─────────────────────┐
                    │       Employee      │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │      Frontend       │
                    │  HTML/CSS/JavaScript│
                    └──────────┬──────────┘
                               │ REST API
                               ▼
                    ┌─────────────────────┐
                    │       FastAPI       │
                    │       Backend       │
                    └──────┬────────┬─────┘
                           │        │
                 ┌─────────┘        └─────────┐
                 ▼                            ▼
        ┌─────────────────┐          ┌─────────────────┐
        │      MySQL      │          │    AI Layer     │
        │     Database    │          │                 │
        └─────────────────┘          │ Classification  │
                                     │ Summarization   │
                                     │ Recommendations │
                                     │ Similarity      │
                                     │ Semantic Search │
                                     │ RAG             │
                                     └─────────────────┘
```

## ⚙️ AI Workflow

When an employee creates a ticket:

```text
New Ticket
    │
    ▼
AI Classification
    │
    ├── Category
    └── Priority
    │
    ▼
AI Summarization
    │
    ▼
Solution Recommendation
    │
    ▼
Similar / Semantic Ticket Search
    │
    ▼
RAG-Based Assistance
    │
    ▼
Support Resolution
```

The system can use previously resolved tickets as a knowledge source to identify related issues and provide troubleshooting information.

## 🔑 Authentication & Roles

### Employee

* Create tickets
* View submitted tickets
* Add comments
* Use AI assistance

### Agent

* View support tickets
* Update ticket status
* Add resolutions
* Use AI-powered troubleshooting

### Admin

* Manage users and system access
* Monitor tickets
* Access administrative functionality

## 🗄️ Database

The MySQL database stores information such as:

* Users
* Tickets
* Ticket comments
* Ticket status
* Ticket priority
* Ticket category
* Ticket resolutions
* Ticket history

## 📂 Project Structure

```text
IT-Helpdesk/
│
├── backend/
│   ├── main.py
│   ├── ai_classifier.py
│   ├── ai_summarizer.py
│   ├── ai_solutions.py
│   ├── ai_similarity.py
│   ├── ai_embeddings.py
│   ├── ai_rag.py
│   ├── database.py
│   └── requirements.txt
│
├── frontend/
│   ├── index.html
│   ├── login.html
│   ├── dashboard.html
│   ├── ticket.html
│   ├── admin-dashboard.html
│   ├── agent-dashboard.html
│   ├── app.js
│   └── style.css
│
├── .python-version
└── README.md
```

## 🚀 Local Setup

### 1. Clone the Repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd IT-Helpdesk
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

Activate it on Windows:

```powershell
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r backend/requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file inside the `backend` directory:

```env
DB_HOST=localhost
DB_USER=your_username
DB_PASSWORD=your_password
DB_NAME=it_helpdesk
SECRET_KEY=your_secret_key
```

### 5. Start the FastAPI Backend

```bash
cd backend
uvicorn main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

FastAPI documentation:

```text
http://127.0.0.1:8000/docs
```

### 6. Run the Frontend

Open the frontend using a local development server or serve the `frontend` directory through your preferred web server.

## 🔒 Security

* JWT-based authentication
* Password hashing
* Protected API endpoints
* Role-based authorization
* Environment variables for sensitive configuration
* CORS configuration for the deployed frontend

## 📌 Future Improvements

* AI-powered automatic ticket routing
* Real-time notifications
* Advanced analytics dashboard
* Vector database for scalable semantic search
* Improved RAG knowledge base
* Automated agent assignment
* Email and notification integration

## 🎯 Project Purpose

This project was developed as a practical full-stack application to demonstrate skills in:

* Python backend development
* REST API development
* FastAPI
* MySQL database management
* JWT authentication
* Role-based access control
* AI/NLP integration
* Semantic search and RAG
* Frontend development
* Git/GitHub
* Cloud deployment

## 👨‍💻 Author

**Saikrishna Nathi**

> Full-Stack Python project focused on AI-assisted IT support and intelligent ticket management.

## 📄 License

This project is intended for educational and portfolio purposes.
