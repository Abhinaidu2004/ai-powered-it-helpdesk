from fastapi import FastAPI, HTTPException, Depends # type: ignore
from fastapi.middleware.cors import CORSMiddleware # type: ignore
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm # type: ignore
from jose import jwt, JWTError # type: ignore
from pydantic import BaseModel # type: ignore
import mysql.connector # type: ignore
from passlib.context import CryptContext # type: ignore
from jose import jwt # type: ignore
from ai_classifier import predict_ticket
from ai_summarizer import summarize_ticket
from ai_solutions import recommend_solution
from ai_similarity import find_similar_tickets
from ai_embeddings import find_semantic_similarity
from ai_rag import generate_solution
from dotenv import load_dotenv
import os
from typing import Optional

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


#MySQL Connection
def get_db_connection():
    ca_cert = os.getenv("AIVEN_CA_CERT")

    if ca_cert:
        ca_path = "/tmp/aiven-ca.pem"

        with open(ca_path, "w") as f:
            f.write(ca_cert)
    else:
        ca_path = "ca.pem"

    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        ssl_ca=ca_path
    )


# Ticket data model
class Ticket(BaseModel):
    title: str
    description: str
    user_id: int

class TicketUpdate(BaseModel):
    title: str
    description: str
    priority: str
    status: str
    resolution: Optional[str] = None

class TicketAssignment(BaseModel):
    assigned_to: int

class StatusUpdate(BaseModel):
    status: str
    resolution: Optional[str] = None

class UserRegister(BaseModel):
    name: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class RoleUpdate(BaseModel):
    role: str

class CommentCreate(BaseModel):
    comment: str

class AIClassificationRequest(BaseModel):
    title: str
    description: str

class AISummaryRequest(BaseModel):
    title: str
    description: str

class AISolutionRequest(BaseModel):
    title: str
    description: str

class AISimilarRequest(BaseModel):
    title: str
    description: str

class AIRAGRequest(BaseModel):
    title: str
    description: str

@app.post("/register")
def register_user(user: UserRegister):

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    # Check if email already exists
    cursor.execute(
        "SELECT id FROM users WHERE email = %s",
        (user.email,)
    )

    existing_user = cursor.fetchone()

    if existing_user:
        cursor.close()
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    # Hash the password
    hashed_password = pwd_context.hash(user.password)

    # Insert user into database
    cursor.execute(
        """
        INSERT INTO users
        (name, email, password_hash, role)
        VALUES (%s, %s, %s, %s)
        """,
        (
            user.name,
            user.email,
            hashed_password,
            "employee"
        )
    )

    db.commit()
    cursor.close()

    return {
        "message": "User registered successfully"
    }

@app.post("/login")
def login_user(
    form_data: OAuth2PasswordRequestForm = Depends()
):

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    # Find user by email
    cursor.execute(
        "SELECT * FROM users WHERE email = %s",
        (form_data.username,)
    )

    existing_user = cursor.fetchone()

    if existing_user is None:
        cursor.close()
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    # Verify password
    password_correct = pwd_context.verify(
        form_data.password,
        existing_user["password_hash"]
    )

    if not password_correct:
        cursor.close()
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    # Create JWT token
    token_data = {
        "user_id": existing_user["id"],
        "role": existing_user["role"]
    }

    access_token = jwt.encode(
        token_data,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    cursor.close()

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": existing_user["id"],
        "role": existing_user["role"]
        }

# Home
@app.get("/")
def home():
    return {
        "message": "IT Help Desk API is running"
    }

def get_current_user(token: str = Depends(oauth2_scheme)):

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        user_id = payload.get("user_id")
        role = payload.get("role")

        if user_id is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )

        return {
            "user_id": user_id,
            "role": role
        }

    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

def require_role(allowed_roles: list):

    def role_checker(
        current_user: dict = Depends(get_current_user)
    ):

        if current_user["role"] not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to perform this action"
            )

        return current_user

    return role_checker 

@app.get("/admin/users")
def get_all_users(
    current_user: dict = Depends(require_role(["admin"]))
):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT id, name, email, role, created_at
        FROM users
        """
    )

    users = cursor.fetchall()

    cursor.close()

    return users  

@app.put("/admin/users/{user_id}/role")
def update_user_role(
    user_id: int,
    data: RoleUpdate,
    current_user: dict = Depends(require_role(["admin"]))
):

    if data.role not in ["employee", "agent", "admin"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid role"
        )
    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute(
        "SELECT id FROM users WHERE id = %s",
        (user_id,)
    )

    existing_user = cursor.fetchone()

    if existing_user is None:
        cursor.close()
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    cursor.execute(
        "UPDATE users SET role = %s WHERE id = %s",
        (data.role, user_id)
    )

    db.commit()
    cursor.close()

    return {
        "message": "User role updated successfully"
    }

# Get all tickets
@app.get("/tickets")
def get_tickets(
    current_user: dict = Depends(get_current_user)
):

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    user_id = current_user["user_id"]
    role = current_user["role"]

    if role == "admin":

        cursor.execute("""
            SELECT *
            FROM tickets
        """)

    elif role == "agent":

        cursor.execute("""
            SELECT *
            FROM tickets
            WHERE assigned_to = %s
        """, (user_id,))

    elif role == "employee":

        cursor.execute("""
            SELECT *
            FROM tickets
            WHERE user_id = %s
        """, (user_id,))

    else:

        cursor.close()
        db.close()

        raise HTTPException(
            status_code=403,
            detail="Invalid user role"
        )

    tickets = cursor.fetchall()

    cursor.close()
    db.close()

    return tickets

# Create ticket
@app.post("/tickets")
def create_ticket(ticket: Ticket):

    ticket_text = ticket.title + " " + ticket.description

    # AI classification
    ai_category, ai_priority = predict_ticket(ticket_text)

    # AI solution recommendation
    solution = recommend_solution(ticket_text)

    db = get_db_connection()
    cursor = db.cursor()

    sql = """
    INSERT INTO tickets
    (
        title,
        description,
        priority,
        category,
        user_id,
        recommended_solution
    )
    VALUES (%s, %s, %s, %s, %s, %s)
    """

    values = (
        ticket.title,
        ticket.description,
        ai_priority,
        ai_category,
        ticket.user_id,
        solution
    )

    cursor.execute(sql, values)

    db.commit()

    cursor.close()
    db.close()

    return {
        "message": "Ticket created successfully",
        "category": ai_category,
        "priority": ai_priority,
        "recommended_solution": solution
    }

@app.get("/users")
def get_users():

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT id, name, email, role FROM users")

    users = cursor.fetchall()

    cursor.close()

    return users

@app.get("/debug")
def debug():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT DATABASE() AS database_name")
    database = cursor.fetchone()

    cursor.execute("SELECT id, name FROM users WHERE id = 1")
    user = cursor.fetchone()

    cursor.close()

    return {
        "database": database,
        "user": user
    }

@app.get("/tickets/{ticket_id}")
def get_ticket(
    ticket_id: int,
    current_user: dict = Depends(get_current_user)
):

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM tickets WHERE id = %s",
        (ticket_id,)
    )

    ticket = cursor.fetchone()

    if ticket is None:
        cursor.close()
        db.close()
        raise HTTPException(
            status_code=404,
            detail="Ticket not found"
        )

    user_id = current_user["user_id"]
    role = current_user["role"]

    # Employee can view only their own tickets
    if role == "employee":

        if ticket["user_id"] != user_id:
            cursor.close()
            db.close()
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to view this ticket"
            )

    # Agent can view only tickets assigned to them
    elif role == "agent":

        if ticket["assigned_to"] != user_id:
            cursor.close()
            db.close()
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to view this ticket"
            )

    # Admin can view all tickets
    elif role == "admin":
        pass

    else:
        cursor.close()
        db.close()
        raise HTTPException(
            status_code=403,
            detail="Invalid user role"
        )

    cursor.close()
    db.close()

    return ticket

@app.put("/tickets/{ticket_id}")
def update_ticket(
    ticket_id: int,
    ticket: TicketUpdate,
    current_user: dict = Depends(get_current_user)
):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT id, user_id, assigned_to, title, description, priority, status
        FROM tickets
        WHERE id = %s
        """,
        (ticket_id,)
    )

    existing_ticket = cursor.fetchone()

    if existing_ticket is None:
        cursor.close()
        db.close()

        raise HTTPException(
            status_code=404,
            detail="Ticket not found"
        )

    # -------------------------
    # Authorization
    # -------------------------

    if current_user["role"] == "admin":
        pass

    elif current_user["role"] == "agent":

        if existing_ticket["assigned_to"] != current_user["user_id"]:
            cursor.close()
            db.close()

            raise HTTPException(
                status_code=403,
                detail="You can only update tickets assigned to you"
            )

    elif current_user["role"] == "employee":

        if existing_ticket["user_id"] != current_user["user_id"]:
            cursor.close()
            db.close()

            raise HTTPException(
                status_code=403,
                detail="You can only update your own tickets"
            )

    else:
        cursor.close()
        db.close()

        raise HTTPException(
            status_code=403,
            detail="Invalid user role"
        )

    # -------------------------
    # Update ticket
    # -------------------------

    sql = """
        UPDATE tickets
        SET title = %s,
            description = %s,
            priority = %s,
            status = %s,
            resolution = %s
        WHERE id = %s
    """

    values = (
        ticket.title,
        ticket.description,
        ticket.priority,
        ticket.status,
        ticket.resolution,
        ticket_id
    )

    cursor.execute(sql, values)

    db.commit()

    cursor.close()
    db.close()

    return {
        "message": "Ticket updated successfully"
    }

@app.delete("/tickets/{ticket_id}")
def delete_ticket(
    ticket_id: int,
    current_user: dict = Depends(get_current_user)
):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT id, user_id, assigned_to
        FROM tickets
        WHERE id = %s
        """,
        (ticket_id,)
    )

    existing_ticket = cursor.fetchone()

    if existing_ticket is None:
        cursor.close()
        db.close()
        raise HTTPException(
            status_code=404,
            detail="Ticket not found"
        )

    # Authorization
    if current_user["role"] == "admin":
        pass

    elif current_user["role"] == "agent":
        if existing_ticket["assigned_to"] != current_user["user_id"]:
            cursor.close()
            db.close()
            raise HTTPException(
                status_code=403,
                detail="You can only delete tickets assigned to you"
            )

    elif current_user["role"] == "employee":
        if existing_ticket["user_id"] != current_user["user_id"]:
            cursor.close()
            db.close()
            raise HTTPException(
                status_code=403,
                detail="You can only delete your own tickets"
            )

    else:
        cursor.close()
        db.close()
        raise HTTPException(
            status_code=403,
            detail="Invalid user role"
        )

    # Delete history
    cursor.execute(
        """
        DELETE FROM ticket_history
        WHERE ticket_id = %s
        """,
        (ticket_id,)
    )

    # Delete comments
    cursor.execute(
        """
        DELETE FROM ticket_comments
        WHERE ticket_id = %s
        """,
        (ticket_id,)
    )

    # Delete ticket
    cursor.execute(
        """
        DELETE FROM tickets
        WHERE id = %s
        """,
        (ticket_id,)
    )

    db.commit()

    cursor.close()
    db.close()

    return {
        "message": "Ticket deleted successfully"
    }
    
@app.put("/tickets/{ticket_id}/assign")
def assign_ticket(
    ticket_id: int,
    data: TicketAssignment,
    current_user: dict = Depends(require_role(["admin"]))
):

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    # Check ticket
    cursor.execute(
        "SELECT id, assigned_to FROM tickets WHERE id = %s",
        (ticket_id,)
    )

    ticket = cursor.fetchone()

    if ticket is None:
        cursor.close()
        db.close()

        raise HTTPException(
            status_code=404,
            detail="Ticket not found"
        )

    # Check selected agent
    cursor.execute(
        """
        SELECT id, name, role
        FROM users
        WHERE id = %s
        """,
        (data.assigned_to,)
    )

    agent = cursor.fetchone()

    if agent is None:
        cursor.close()
        db.close()

        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    if agent["role"] != "agent":
        cursor.close()
        db.close()

        raise HTTPException(
            status_code=400,
            detail="Ticket can only be assigned to an agent"
        )

    old_agent = ticket["assigned_to"]

    # Update assignment
    cursor.execute(
        """
        UPDATE tickets
        SET assigned_to = %s
        WHERE id = %s
        """,
        (data.assigned_to, ticket_id)
    )

    # Add history record
    cursor.execute(
        """
        INSERT INTO ticket_history
        (ticket_id, user_id, action, old_value, new_value)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (
            ticket_id,
            current_user["user_id"],
            "Ticket Assigned",
            str(old_agent) if old_agent else "Unassigned",
            agent["name"]
        )
    )

    db.commit()

    cursor.close()
    db.close()

    return {
        "message": "Ticket assigned successfully",
        "assigned_to": agent["name"]
    }

@app.put("/tickets/{ticket_id}/status")
def update_ticket_status(
    ticket_id: int,
    data: StatusUpdate,
    current_user: dict = Depends(get_current_user)
):

    allowed_statuses = [
        "Open",
        "In Progress",
        "Resolved",
        "Closed"
    ]

    if data.status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail="Invalid status"
        )

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    # Get ticket
    cursor.execute(
        """
        SELECT id, user_id, assigned_to, status, resolution
        FROM tickets
        WHERE id = %s
        """,
        (ticket_id,)
    )

    ticket = cursor.fetchone()

    if ticket is None:
        cursor.close()
        db.close()

        raise HTTPException(
            status_code=404,
            detail="Ticket not found"
        )

    # Admin can update any ticket
    if current_user["role"] == "admin":
        pass

    # Agent can update only assigned tickets
    elif current_user["role"] == "agent":

        if ticket["assigned_to"] != current_user["user_id"]:

            cursor.close()
            db.close()

            raise HTTPException(
                status_code=403,
                detail="You can only update tickets assigned to you"
            )

    # Employee can update only their own tickets
    elif current_user["role"] == "employee":

        if ticket["user_id"] != current_user["user_id"]:

            cursor.close()
            db.close()

            raise HTTPException(
                status_code=403,
                detail="You can only update your own tickets"
            )

    # Update status and resolution
    cursor.execute(
        """
        UPDATE tickets
        SET status = %s,
            resolution = %s
        WHERE id = %s
        """,
        (
            data.status,
            data.resolution,
            ticket_id
        )
    )

    # Record status change
    if ticket["status"] != data.status:

        cursor.execute(
            """
            INSERT INTO ticket_history
            (
                ticket_id,
                user_id,
                action,
                old_value,
                new_value
            )
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                ticket_id,
                current_user["user_id"],
                "Status Changed",
                ticket["status"],
                data.status
            )
        )

    # Record resolution change
    if ticket["resolution"] != data.resolution:

        cursor.execute(
            """
            INSERT INTO ticket_history
            (
                ticket_id,
                user_id,
                action,
                old_value,
                new_value
            )
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                ticket_id,
                current_user["user_id"],
                "Resolution Updated",
                ticket["resolution"],
                data.resolution
            )
        )

    db.commit()

    cursor.close()
    db.close()

    return {
        "message": "Ticket status and resolution updated successfully",
        "status": data.status,
        "resolution": data.resolution
    }

@app.get("/tickets/{ticket_id}/history")
def get_ticket_history(
    ticket_id: int,
    current_user: dict = Depends(get_current_user)
):
    
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    # Check if ticket exists
    cursor.execute(
        "SELECT id, user_id, assigned_to FROM tickets WHERE id = %s",
        (ticket_id,)
    )

    ticket = cursor.fetchone()

    if ticket is None:
        cursor.close()
        raise HTTPException(
            status_code=404,
            detail="Ticket not found"
        )

    # Check permissions
    if current_user["role"] == "admin":
        pass

    elif current_user["role"] == "agent":

        if ticket["assigned_to"] != current_user["user_id"]:
            cursor.close()
            raise HTTPException(
                status_code=403,
                detail="You can only view history of tickets assigned to you"
            )

    elif current_user["role"] == "employee":

        if ticket["user_id"] != current_user["user_id"]:
            cursor.close()
            raise HTTPException(
                status_code=403,
                detail="You can only view history of your own tickets"
            )

    # Get history
    cursor.execute(
        """
        SELECT
            ticket_history.id,
            ticket_history.ticket_id,
            users.name,
            ticket_history.action,
            ticket_history.old_value,
            ticket_history.new_value,
            ticket_history.created_at
        FROM ticket_history
        JOIN users
            ON ticket_history.user_id = users.id
        WHERE ticket_history.ticket_id = %s
        ORDER BY ticket_history.created_at ASC
        """,
        (ticket_id,)
    )

    history = cursor.fetchall()

    cursor.close()

    return history

@app.post("/tickets/{ticket_id}/comments")
def add_comment(
    ticket_id: int,
    data: CommentCreate,
    current_user: dict = Depends(get_current_user)
):

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    # Check if ticket exists
    cursor.execute(
        """
        SELECT id, user_id, assigned_to
        FROM tickets
        WHERE id = %s
        """,
        (ticket_id,)
    )

    ticket = cursor.fetchone()

    if ticket is None:
        cursor.close()
        raise HTTPException(
            status_code=404,
            detail="Ticket not found"
        )

    # Check permissions
    if current_user["role"] == "admin":
        pass

    elif current_user["role"] == "agent":

        if ticket["assigned_to"] != current_user["user_id"]:
            cursor.close()
            raise HTTPException(
                status_code=403,
                detail="You can only comment on tickets assigned to you"
            )

    elif current_user["role"] == "employee":

        if ticket["user_id"] != current_user["user_id"]:
            cursor.close()
            raise HTTPException(
                status_code=403,
                detail="You can only comment on your own tickets"
            )

    # Insert comment
    cursor.execute(
    """
    INSERT INTO ticket_comments
    (ticket_id, user_id, comment)
    VALUES (%s, %s, %s)
    """,
    (
        ticket_id,
        current_user["user_id"],
        data.comment
    )
)

# Record comment in ticket history
    cursor.execute(
        """
        INSERT INTO ticket_history
        (ticket_id, user_id, action, old_value, new_value)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (
            ticket_id,
            current_user["user_id"],
            "Comment Added",
            None,
            data.comment
        )
    )

    db.commit()
    cursor.close()

    return {
        "message": "Comment added successfully"
    }

@app.get("/tickets/{ticket_id}/comments")
def get_comments(
    ticket_id: int,
    current_user: dict = Depends(get_current_user)
):

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    # Check if ticket exists
    cursor.execute(
        """
        SELECT id, user_id, assigned_to
        FROM tickets
        WHERE id = %s
        """,
        (ticket_id,)
    )

    ticket = cursor.fetchone()

    if ticket is None:
        cursor.close()
        raise HTTPException(
            status_code=404,
            detail="Ticket not found"
        )

    # Check permissions
    if current_user["role"] == "admin":
        pass

    elif current_user["role"] == "agent":

        if ticket["assigned_to"] != current_user["user_id"]:
            cursor.close()
            raise HTTPException(
                status_code=403,
                detail="You can only view comments of tickets assigned to you"
            )

    elif current_user["role"] == "employee":

        if ticket["user_id"] != current_user["user_id"]:
            cursor.close()
            raise HTTPException(
                status_code=403,
                detail="You can only view comments of your own tickets"
            )

    # Get comments
    cursor.execute(
        """
        SELECT
            ticket_comments.id,
            ticket_comments.ticket_id,
            users.name,
            ticket_comments.comment,
            ticket_comments.created_at
        FROM ticket_comments
        JOIN users
            ON ticket_comments.user_id = users.id
        WHERE ticket_comments.ticket_id = %s
        ORDER BY ticket_comments.created_at ASC
        """,
        (ticket_id,)
    )

    comments = cursor.fetchall()

    cursor.close()

    return comments

@app.get("/dashboard/stats")
def dashboard_stats(
    current_user: dict = Depends(get_current_user)
):

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    # Admin → all tickets
    if current_user["role"] == "admin":

        cursor.execute(
            """
            SELECT
                COUNT(*) AS total_tickets,
                SUM(status = 'Open') AS open_tickets,
                SUM(status = 'In Progress') AS in_progress_tickets,
                SUM(status = 'Resolved') AS resolved_tickets,
                SUM(status = 'Closed') AS closed_tickets
            FROM tickets
            """
        )

    # Agent → assigned tickets
    elif current_user["role"] == "agent":

        cursor.execute(
            """
            SELECT
                COUNT(*) AS total_tickets,
                SUM(status = 'Open') AS open_tickets,
                SUM(status = 'In Progress') AS in_progress_tickets,
                SUM(status = 'Resolved') AS resolved_tickets,
                SUM(status = 'Closed') AS closed_tickets
            FROM tickets
            WHERE assigned_to = %s
            """,
            (current_user["user_id"],)
        )

    # Employee → own tickets
    else:

        cursor.execute(
            """
            SELECT
                COUNT(*) AS total_tickets,
                SUM(status = 'Open') AS open_tickets,
                SUM(status = 'In Progress') AS in_progress_tickets,
                SUM(status = 'Resolved') AS resolved_tickets,
                SUM(status = 'Closed') AS closed_tickets
            FROM tickets
            WHERE user_id = %s
            """,
            (current_user["user_id"],)
        )

    stats = cursor.fetchone()

    cursor.close()

    return stats

@app.get("/dashboard/priority")
def dashboard_priority(
    current_user: dict = Depends(get_current_user)
):

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    # Admin → all tickets
    if current_user["role"] == "admin":

        cursor.execute(
            """
            SELECT
                priority,
                COUNT(*) AS total_tickets
            FROM tickets
            GROUP BY priority
            ORDER BY total_tickets DESC
            """
        )

    # Agent → assigned tickets
    elif current_user["role"] == "agent":

        cursor.execute(
            """
            SELECT
                priority,
                COUNT(*) AS total_tickets
            FROM tickets
            WHERE assigned_to = %s
            GROUP BY priority
            ORDER BY total_tickets DESC
            """,
            (current_user["user_id"],)
        )

    # Employee → own tickets
    else:

        cursor.execute(
            """
            SELECT
                priority,
                COUNT(*) AS total_tickets
            FROM tickets
            WHERE user_id = %s
            GROUP BY priority
            ORDER BY total_tickets DESC
            """,
            (current_user["user_id"],)
        )

    priority_data = cursor.fetchall()

    cursor.close()

    return priority_data

@app.get("/dashboard/status")
def dashboard_status(
    current_user: dict = Depends(get_current_user)
):

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    # Admin → all tickets
    if current_user["role"] == "admin":

        cursor.execute(
            """
            SELECT
                status,
                COUNT(*) AS total_tickets
            FROM tickets
            GROUP BY status
            ORDER BY total_tickets DESC
            """
        )

    # Agent → assigned tickets
    elif current_user["role"] == "agent":

        cursor.execute(
            """
            SELECT
                status,
                COUNT(*) AS total_tickets
            FROM tickets
            WHERE assigned_to = %s
            GROUP BY status
            ORDER BY total_tickets DESC
            """,
            (current_user["user_id"],)
        )

    # Employee → own tickets
    else:

        cursor.execute(
            """
            SELECT
                status,
                COUNT(*) AS total_tickets
            FROM tickets
            WHERE user_id = %s
            GROUP BY status
            ORDER BY total_tickets DESC
            """,
            (current_user["user_id"],)
        )

    status_data = cursor.fetchall()

    cursor.close()

    return status_data

@app.get("/dashboard/agents")
def dashboard_agents(
    current_user: dict = Depends(require_role(["admin"]))
):

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT
            users.id AS agent_id,
            users.name AS agent_name,
            COUNT(tickets.id) AS total_tickets
        FROM users
        LEFT JOIN tickets
            ON users.id = tickets.assigned_to
        WHERE users.role = 'agent'
        GROUP BY users.id, users.name
        ORDER BY total_tickets DESC
        """
    )

    agents = cursor.fetchall()

    cursor.close()

    return agents

@app.get("/dashboard")
def dashboard(
    current_user: dict = Depends(get_current_user)
):

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    # Admin → all tickets
    if current_user["role"] == "admin":

        cursor.execute(
            """
            SELECT
                COUNT(*) AS total_tickets,
                SUM(status = 'Open') AS open_tickets,
                SUM(status = 'In Progress') AS in_progress_tickets,
                SUM(status = 'Resolved') AS resolved_tickets,
                SUM(status = 'Closed') AS closed_tickets
            FROM tickets
            """
        )

    # Agent → assigned tickets
    elif current_user["role"] == "agent":

        cursor.execute(
            """
            SELECT
                COUNT(*) AS total_tickets,
                SUM(status = 'Open') AS open_tickets,
                SUM(status = 'In Progress') AS in_progress_tickets,
                SUM(status = 'Resolved') AS resolved_tickets,
                SUM(status = 'Closed') AS closed_tickets
            FROM tickets
            WHERE assigned_to = %s
            """,
            (current_user["user_id"],)
        )

    # Employee → own tickets
    else:

        cursor.execute(
            """
            SELECT
                COUNT(*) AS total_tickets,
                SUM(status = 'Open') AS open_tickets,
                SUM(status = 'In Progress') AS in_progress_tickets,
                SUM(status = 'Resolved') AS resolved_tickets,
                SUM(status = 'Closed') AS closed_tickets
            FROM tickets
            WHERE user_id = %s
            """,
            (current_user["user_id"],)
        )

    stats = cursor.fetchone()

    cursor.close()

    return {
        "role": current_user["role"],
        "statistics": stats
    }

@app.get("/analytics/priority")
def analytics_priority(
    current_user: dict = Depends(require_role(["admin"]))
):

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT
            priority,
            COUNT(*) AS total_tickets
        FROM tickets
        GROUP BY priority
        ORDER BY total_tickets DESC
        """
    )

    result = cursor.fetchall()

    cursor.close()

    return result

@app.get("/analytics/agents")
def analytics_agents(
    current_user: dict = Depends(require_role(["admin"]))
):

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT
            users.id AS agent_id,
            users.name AS agent_name,
            COUNT(tickets.id) AS total_tickets
        FROM users
        LEFT JOIN tickets
            ON users.id = tickets.assigned_to
        WHERE users.role = 'agent'
        GROUP BY users.id, users.name
        ORDER BY total_tickets DESC
        """
    )

    result = cursor.fetchall()

    cursor.close()

    return result

@app.get("/analytics/status")
def analytics_status(
    current_user: dict = Depends(require_role(["admin"]))
):

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT
            status,
            COUNT(*) AS total_tickets
        FROM tickets
        GROUP BY status
        HAVING COUNT(*) > 0
        ORDER BY total_tickets DESC
        """
    )

    result = cursor.fetchall()

    cursor.close()

    return result

@app.get("/analytics/high-priority")
def high_priority_tickets(
    current_user: dict = Depends(require_role(["admin"]))
):

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT
            id,
            title,
            priority,
            status,
            created_at
        FROM tickets
        WHERE priority = 'High'
        AND status NOT IN ('Resolved', 'Closed')
        ORDER BY created_at ASC
        """
    )

    result = cursor.fetchall()

    cursor.close()

    return result

@app.get("/analytics/categories")
def analytics_categories(
    current_user: dict = Depends(require_role(["admin"]))
):

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT
            category,
            COUNT(*) AS total_tickets
        FROM tickets
        GROUP BY category
        ORDER BY total_tickets DESC
        """
    )

    result = cursor.fetchall()

    cursor.close()

    return result

@app.post("/ai/classify")
def classify_ticket(data: AIClassificationRequest):

    ticket_text = data.title + " " + data.description

    category, priority = predict_ticket(ticket_text)

    return {
        "category": category,
        "priority": priority
    }

@app.post("/ai/summarize")
def summarize_ticket_api(data: AISummaryRequest):

    ticket_text = data.title + " " + data.description

    summary = summarize_ticket(ticket_text)

    return {
        "summary": summary
    }

@app.post("/ai/recommend")
def recommend_ticket_solution(data: AISolutionRequest):

    ticket_text = data.title + " " + data.description

    solution = recommend_solution(ticket_text)

    return {
        "solution": solution
    }

@app.post("/ai/similar")
def find_similar_ticket_api(data: AISimilarRequest):

    ticket_text = data.title + " " + data.description

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
    SELECT
        id,
        title,
        description,
        priority,
        category,
        resolution
    FROM tickets
    WHERE status = 'Resolved'
      AND resolution IS NOT NULL
    """)    

    tickets = cursor.fetchall()

    cursor.close()

    previous_tickets = []

    previous_tickets = tickets

    results = find_similar_tickets(
        ticket_text,
        previous_tickets
    )

    return {
        "similar_tickets": results
    }

@app.post("/ai/semantic-search")
def semantic_search(data: AISimilarRequest):

    ticket_text = data.title + " " + data.description

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            id,
            title,
            description,
            priority,
            category,
            resolution
        FROM tickets
        WHERE status = 'Resolved'
          AND resolution IS NOT NULL
    """)

    tickets = cursor.fetchall()

    cursor.close()

    results = find_semantic_similarity(
        ticket_text,
        tickets
    )

    return {
        "semantic_results": results
    }

@app.post("/ai/rag")
def rag_solution(data: AIRAGRequest):

    ticket_text = data.title + " " + data.description

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            id,
            title,
            description,
            priority,
            category,
            resolution
        FROM tickets
        WHERE status = 'Resolved'
          AND resolution IS NOT NULL
    """)

    tickets = cursor.fetchall()
    cursor.close()

    # Find similar resolved tickets
    similar_tickets = find_semantic_similarity(
    ticket_text,
    tickets,
    top_n=3
    )

    similar_tickets = [
        ticket
        for ticket in similar_tickets
        if ticket["similarity"] >= 0.40
    ]

    # Build context for Llama 3
    context = ""

    for ticket in similar_tickets:
        context += f"""
Ticket ID: {ticket['ticket_id']}
Title: {ticket['title']}
Description: {ticket['description']}
Category: {ticket['category']}
Priority: {ticket['priority']}
Resolution: {ticket['resolution']}
Similarity: {ticket['similarity']}

"""

    # Generate AI solution
    solution = generate_solution(
        ticket_text,
        context
    )

    return {
        "ticket": {
            "title": data.title,
            "description": data.description
        },
        "similar_tickets": similar_tickets,
        "ai_solution": solution
    }