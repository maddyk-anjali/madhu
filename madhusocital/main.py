from multiprocessing import connection
from venv import create
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import psycopg2
import hashlib
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from datetime import date
from typing import Optional
from pydantic import BaseModel, EmailStr
from fastapi import File, UploadFile
import psycopg2
import base64
from typing import Optional
from datetime import date
from starlette.middleware.sessions import SessionMiddleware
from Models import *
from typing import List
from pydantic import BaseModel, condecimal, constr
from typing import Optional


# PS C:\Users\madhu\Desktop\Socital\Socital\app> uvicorn teest:app --reload 
# Database Configuration

create_database()
create_user_table()
create_vaccine_table()
create_mother_card_request()
create_mother_card_table()
create_distribution_history_table()
create_mother_checkup_history_table()

# send_trimester_reminders()
send_vaccination_reminders()

# FastAPI setup
app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="your_secret_key")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# Updated render_home_page to show or hide user details
def get_all_users():
    """
    Fetch all users from the database.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users;")
        users = cursor.fetchall()

        cursor.close()
        conn.close()

        return users
    except Exception as e:
        print(f"Error fetching users: {e}")
        return []

@app.get("/", response_class=HTMLResponse)
async def render_home_page(request: Request):
    user = request.session.get("user")  # Get logged-in user's data from session
    users = print(get_all_users())
    # Fetch all users from DB

    return templates.TemplateResponse(
        "users/index.html",
        {"request": request, "user": user["username"] if user else None, "users": users}
    )

@app.post("/signup", response_class=JSONResponse)
async def signup(username: str = Form(...), email: str = Form(...), password: str = Form(...), confirm_password: str = Form(...)):
    """
    Handle signup submissions.
    """
    if password != confirm_password:
        print(f"Passwords do not match for username '{username}'.")
        return {"success": False, "message": "Passwords do not match"}

    try:
        user_id = insert_user(username, email, password)
        return {"success": True, "message": "Account created successfully!"}
    except Exception as e:
        return {"success": False, "message": f"User Already Exists: {str(e)}"}

# Login: Add user to session-based active users
@app.post("/login", response_class=JSONResponse)
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    user = check_user_credentials(username, password)
    if user:
        user_id = user[0]  # Assuming the first element in `user` tuple is the user ID
        request.session["user"] = {"username": username, "userid": user_id}
        print(f"User '{username}' (ID: {user_id}) logged in successfully.")
        return {"success": True, "message": "Login successful!", "username": user[1], "userid": user_id}
    else:
        print(f"Failed login attempt for username '{username}'.")
        return {"success": False, "message": "Invalid credentials. Please try again."}



# Logout: Remove user from active users
@app.post("/logout")
async def logout(request: Request):
    active_users = set(request.session.get("active_users", []))  # Ensure it's a set
    user = request.session.get("user")

    if user:
        active_users.discard(user.get("username"))  # Remove user from active users
        request.session["active_users"] = list(active_users)  # Convert back to list for session storage


    request.session.clear()
    return {"success": True, "message": "Logged out successfully!"}



app.add_middleware(
    SessionMiddleware,
    secret_key="your_secret_key",  # Change this to a random secure string
    session_cookie="my_session",
    max_age=3600,  # 1 hour session duration
    same_site="lax",
    https_only=False  # Change to True if using HTTPS
)

@app.get("/session-check")
async def session_check(request: Request):
    return {"session": request.session}


# Update the home route to pass session user data
@app.get("/", response_class=HTMLResponse)
async def render_home_page(request: Request):
    user = request.session.get("user")
    return templates.TemplateResponse(
        "users/index.html",
        {"request": request, "user": user["username"] if user else None}
    )
    
# Define the route for the mother page
@app.get("/mother", response_class=HTMLResponse)
async def mother_page(request: Request):
    user = request.session.get("user")  # Get the logged-in user's data from the session
    
    if not user:
        print("No active user. Redirecting to login page.")
        return HTMLResponse(
            """
            <script>
                alert("Login first to visit this page!");
                window.location.href = "/login"; // Redirect to login page
            </script>
            """,
            status_code=200
        )  # Shows an alert and redirects
     
    print(f"Active user: {user['username']}")  # Print active user in the terminal
    
    return templates.TemplateResponse(
        "users/mother.html",
        {"request": request, "user": user["username"]}
    )

# Define the route for the child page
@app.get("/child", response_class=HTMLResponse)
async def child_page(request: Request):
    user = request.session.get("user")  # Get the logged-in user's data from the session
    if user:
        print(f"Active user: {user['username']}")  # Print active user in the terminal
    else:
        print("No active user.")  # Print message when no user is logged in
    return templates.TemplateResponse(
        "users/child.html",
        {"request": request, "user": user["username"] if user else None}
    )

###################### Histroy Work #######################
@app.get("/vaccine_history", response_class=HTMLResponse)
async def vaccine_history_page(request: Request):
    user = request.session.get("user")  # Get the logged-in user's data from the session
    if user:
        print(f"Active user: {user['username']}")  # Print active user in the terminal
    else:
        print("No active user.")  # Print message when no user is logged in
    return templates.TemplateResponse(
        "users/vaccine_history.html",
        {"request": request, "user": user["username"] if user else None}
    )


@app.get("/nutrition_history", response_class=HTMLResponse)
async def nutrition_history_page(request: Request):
    user = request.session.get("user")  # Get the logged-in user's data from the session
    if user:
        print(f"Active user: {user['username']}")  # Print active user in the terminal
    else:
        print("No active user.")  # Print message when no user is logged in
    return templates.TemplateResponse(
        "users/nutrition_history.html",
        {"request": request, "user": user["username"] if user else None}
    )

@app.get("/checkup_history", response_class=HTMLResponse)
async def checkup_history_page(request: Request):
    user = request.session.get("user")  # Get the logged-in user's data from the session
    if user:
        print(f"Active user: {user['username']}")  # Print active user in the terminal
    else:
        print("No active user.")  # Print message when no user is logged in
    return templates.TemplateResponse(
        "users/checkup_history.html",
        {"request": request, "user": user["username"] if user else None}
    )

@app.get("/distribution", response_class=HTMLResponse)
async def vaccine_history_page(request: Request):
    user = request.session.get("user")  # Get the logged-in user's data from the session
    if user:
        print(f"Active user: {user['username']}")  # Print active user in the terminal
    else:
        print("No active user.")  # Print message when no user is logged in
    return templates.TemplateResponse(
        "anganwadi/distribution.html",
        {"request": request, "user": user["username"] if user else None}
    )

@app.get("/mother_checkup_history", response_class=HTMLResponse)
async def vaccine_history_page(request: Request):
    user = request.session.get("user")  # Get the logged-in user's data from the session
    if user:
        print(f"Active user: {user['username']}")  # Print active user in the terminal
    else:
        print("No active user.")  # Print message when no user is logged in
    return templates.TemplateResponse(
        "anganwadi/mother_checkup_history.html",
        {"request": request, "user": user["username"] if user else None}
    )


# Pydantic Model for Distribution Entry
class DistributionEntry(BaseModel):
    user_id: int
    type: str  # 'Vaccine' or 'Nutrition'
    item_name: str
    quantity: str
    unit: str
    distribution_date: str  # Format: YYYY-MM-DD
    status: str  # Upcoming, Distributed, Today, Missed

@app.post("/add_distribution")
def add_distribution(data: DistributionEntry):
    """
    Add a new distribution record to the distribution_history table.
    """
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        staff_id = 1  # Assuming staff_id is always 1 for this example
        # Insert into history table
        cur.execute("""
            INSERT INTO distribution_history 
            (user_id, staff_id, type, item_name, quantity, unit, distribution_date, status, action_date) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
        """, (data.user_id, staff_id, data.type, data.item_name, data.quantity, 
              data.unit, data.distribution_date, data.status))

        conn.commit()
        return {"message": "Distribution record added successfully."}

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error adding distribution record: {str(e)}")

    finally:
        cur.close()
        conn.close()
##################### Dont Come Above ###########################
####################I wont Come Above ###################################

# Insert API
@app.post("/distribution/add")
def add_distribution(entry: DistributionEntry):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        staff_id = 1  # Assuming staff_id is always 1 for this example
        insert_query = """
        INSERT INTO distribution_history 
        (mother_id, staff_id, type, item_name, quantity, unit, distribution_date, status, action_date)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
        """
        cursor.execute(insert_query, (
            entry.mother_id,
            staff_id,
            entry.type,
            entry.item_name,
            entry.quantity,
            entry.unit,
            entry.distribution_date,
            entry.status
        ))

        conn.commit()
        cursor.close()
        conn.close()
        return {"message": "Distribution record added successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@app.get("/distribution", response_class=HTMLResponse)
async def vaccine_history_page(request: Request):
    user = request.session.get("user")  # Get the logged-in user's data from the session
    if user:
        print(f"Active user: {user['username']}")  # Print active user in the terminal
    else:
        print("No active user.")  # Print message when no user is logged in
    return templates.TemplateResponse(
        "users/vaccine_distribution_history.html",
        {"request": request, "user": user["username"] if user else None}
    )

@app.get("/vaccine_distribution_history", response_model=List[dict])
async def get_vaccine_distribution_history(request: Request):
    """
    Fetch vaccine distribution history for authorized users.
    """
    # Check if the user is logged in
    user = request.session.get("user")
    print(user)

    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized access. Please log in.")

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Fetch vaccine distribution history
        cursor.execute("""
            SELECT item_name, quantity, distribution_date, status
            FROM distribution_history
            WHERE type = 'Vaccine' AND user_id = %s
            ORDER BY distribution_date DESC
        """, (user["userid"],))
        records = cursor.fetchall()

        # Fetch column names
        columns = [desc[0] for desc in cursor.description]

        # Convert records to a list of dictionaries
        history = [dict(zip(columns, row)) for row in records]

        return history

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching vaccine distribution history: {str(e)}")

    finally:
        cursor.close()
        conn.close()

@app.get("/nutrition_distribution_history", response_model=List[dict])
async def get_nutrition_distribution_history(request: Request):
    """
    Fetch nutrition distribution history for authorized users.
    """
    # Check if the user is logged in
    user = request.session.get("user")  # Get the logged-in user's data from the session
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized access. Please log in.")
    print(user)
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Fetch nutrition distribution history
        cursor.execute("""
            SELECT item_name, quantity, distribution_date, status
            FROM distribution_history
            WHERE type = 'Nutrition' AND user_id = %s
            ORDER BY distribution_date DESC
        """, (user["userid"],))
        records = cursor.fetchall()

        # Fetch column names
        columns = [desc[0] for desc in cursor.description]

        # Convert records to a list of dictionaries
        history = [dict(zip(columns, row)) for row in records]

        return history

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching nutrition distribution history: {str(e)}")

    finally:
        cursor.close()
        conn.close()

# Define the route for the tools page
@app.get("/tools", response_class=HTMLResponse)
async def tools_page(request: Request):
    user = request.session.get("user")  # Get the logged-in user's data from the session
    if user:
        print(f"Active user: {user['username']}")  # Print active user in the terminal
    else:
        print("No active user.")  # Print message when no user is logged in
    return templates.TemplateResponse(
        "users/tools.html",
        {"request": request, "user": user["username"] if user else None}
    )

# Define the route for the login page
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    user = request.session.get("user")  # Get the logged-in user's data from the session
    if user:
        print(f"Active user: {user['username']}")  # Print active user in the terminal
    else:
        print("No active user.")  # Print message when no user is logged in
    return templates.TemplateResponse(
        "users/login.html",
        {"request": request, "user": user["username"] if user else None}
    )

# Define the route for the vaccine page
@app.get("/vaccine", response_class=HTMLResponse)
async def vaccine_page(request: Request):
    user = request.session.get("user")  # Get the logged-in user's data from the session
    if user:
        print(f"Active user: {user['username']}")  # Print active user in the terminal
    else:
        print("No active user.")  # Print message when no user is logged in
    return templates.TemplateResponse(
        "users/vaccine.html",
        {"request": request, "user": user["username"] if user else None}
    )

@app.get("/cnutrition", response_class=HTMLResponse)
async def cnutrition_page(request: Request):
    user = request.session.get("user")  # Get the logged-in user's data from the session
    if user:
        print(f"Active user: {user['username']}")  # Print active user in the terminal
    else:
        print("No active user.")  # Print message when no user is logged in
    return templates.TemplateResponse(
        "users/cnutrition.html",
        {"request": request, "user": user["username"] if user else None}
    )

@app.get("/mnutrition", response_class=HTMLResponse)
async def mnutrition_page(request: Request):
    user = request.session.get("user")  # Get the logged-in user's data from the session
    if user:
        print(f"Active user: {user['username']}")  # Print active user in the terminal
    else:
        print("No active user.")  # Print message when no user is logged in
    return templates.TemplateResponse(
        "users/mnutrition.html",
        {"request": request, "user": user["username"] if user else None}
    )


@app.get("/about", response_class=HTMLResponse)
async def about_page(request: Request):
    user = request.session.get("user")  # Get the logged-in user's data from the session
    if user:
        print(f"Active user: {user['username']}")  # Print active user in the terminal
    else:
        print("No active user.")  # Print message when no user is logged in
    return templates.TemplateResponse(
        "users/about.html",
        {"request": request, "user": user["username"] if user else None}
    )

@app.get("/available", response_class=HTMLResponse)
async def available_page(request: Request):
    user = request.session.get("user")  # Get the logged-in user's data from the session
    if user:
        print(f"Active user: {user['username']}")  # Print active user in the terminal
    else:
        print("No active user.")  # Print message when no user is logged in
    return templates.TemplateResponse(
        "users/available.html",
        {"request": request, "user": user["username"] if user else None}
    )

@app.get("/tutorials", response_class=HTMLResponse)
async def tutorials_page(request: Request):
    user = request.session.get("user")  # Get the logged-in user's data from the session
    if user:
        print(f"Active user: {user['username']}")  # Print active user in the terminal
    else:
        print("No active user.")  # Print message when no user is logged in
    return templates.TemplateResponse(
        "users/tutorials.html",
        {"request": request, "user": user["username"] if user else None}
    )

@app.get("/health", response_class=HTMLResponse)
async def health_page(request: Request):
    user = request.session.get("user")  # Get the logged-in user's data from the session
    if user:
        print(f"Active user: {user['username']}")  # Print active user in the terminal
    else:
        print("No active user.")  # Print message when no user is logged in
    return templates.TemplateResponse(
        "users/health.html",
        {"request": request, "user": user["username"] if user else None}
    )

@app.get("/growth", response_class=HTMLResponse)
async def growth_page(request: Request):
    user = request.session.get("user")  # Get the logged-in user's data from the session
    if user:
        print(f"Active user: {user['username']}")  # Print active user in the terminal
    else:
        print("No active user.")  # Print message when no user is logged in
    return templates.TemplateResponse(
        "users/growth.html",
        {"request": request, "user": user["username"] if user else None}
    )

@app.get("/feeding", response_class=HTMLResponse)
async def feeding_page(request: Request):
    user = request.session.get("user")  # Get the logged-in user's data from the session
    if user:
        print(f"Active user: {user['username']}")  # Print active user in the terminal
    else:
        print("No active user.")  # Print message when no user is logged in
    return templates.TemplateResponse(
        "users/feeding.html",
        {"request": request, "user": user["username"] if user else None}
    )
@app.get("/program", response_class=HTMLResponse)
async def program_page(request: Request):
    user = request.session.get("user")  # Get the logged-in user's data from the session
    if user:
        print(f"Active user: {user['username']}")  # Print active user in the terminal
    else:
        print("No active user.")  # Print message when no user is logged in
    return templates.TemplateResponse(
        "users/program.html",
        {"request": request, "user": user["username"] if user else None}
    )


@app.get("/PG1", response_class=HTMLResponse)
async def PG1_page(request: Request):
    user = request.session.get("user")  # Get the logged-in user's data from the session
    if user:
        print(f"Active user: {user['username']}")  # Print active user in the terminal
    else:
        print("No active user.")  # Print message when no user is logged in
    return templates.TemplateResponse(
        "users/PG1.html",
        {"request": request, "user": user["username"] if user else None}
    )

@app.get("/PG2", response_class=HTMLResponse)
async def PG2_page(request: Request):
    user = request.session.get("user")  # Get the logged-in user's data from the session
    if user:
        print(f"Active user: {user['username']}")  # Print active user in the terminal
    else:
        print("No active user.")  # Print message when no user is logged in
    return templates.TemplateResponse(
        "users/PG2.html",
        {"request": request, "user": user["username"] if user else None}
    )

@app.get("/PG3", response_class=HTMLResponse)
async def PG3_page(request: Request):
    user = request.session.get("user")  # Get the logged-in user's data from the session
    if user:
        print(f"Active user: {user['username']}")  # Print active user in the terminal
    else:
        print("No active user.")  # Print message when no user is logged in
    return templates.TemplateResponse(
        "users/PG3.html",
        {"request": request, "user": user["username"] if user else None}
    )

@app.get("/PG4", response_class=HTMLResponse)
async def PG4_page(request: Request):
    user = request.session.get("user")  # Get the logged-in user's data from the session
    if user:
        print(f"Active user: {user['username']}")  # Print active user in the terminal
    else:
        print("No active user.")  # Print message when no user is logged in
    return templates.TemplateResponse(
        "users/PG4.html",
        {"request": request, "user": user["username"] if user else None}
    )

@app.get("/duedate", response_class=HTMLResponse)
async def duedate_page(request: Request):
    user = request.session.get("user")  # Get the logged-in user's data from the session
    if user:
        print(f"Active user: {user['username']}")  # Print active user in the terminal
    else:
        print("No active user.")  # Print message when no user is logged in
    return templates.TemplateResponse(
        "users/duedate.html",
        {"request": request, "user": user["username"] if user else None}
    )

@app.get("/mnutrition", response_class=HTMLResponse)
async def mnutrition_page(request: Request):
    user = request.session.get("user")  # Get the logged-in user's data from the session
    if user:
        print(f"Active user: {user['username']}")  # Print active user in the terminal
    else:
        print("No active user.")  # Print message when no user is logged in
    return templates.TemplateResponse(
        "users/mnutrition.html",
        {"request": request, "user": user["username"] if user else None}
    )

@app.get("/pregnancy", response_class=HTMLResponse)
async def pregnancy_page(request: Request):
    user = request.session.get("user")  # Get the logged-in user's data from the session
    if user:
        print(f"Active user: {user['username']}")  # Print active user in the terminal
    else:
        print("No active user.")  # Print message when no user is logged in
    return templates.TemplateResponse(
        "users/pregnancy.html",
        {"request": request, "user": user["username"] if user else None}
    )

@app.get("/reminders", response_class=HTMLResponse)
async def reminders_page(request: Request):
    user = request.session.get("user")  # Get the logged-in user's data from the session
    if user:
        print(f"Active user: {user['username']}")  # Print active user in the terminal
    else:
        print("No active user.")  # Print message when no user is logged in
    return templates.TemplateResponse(
        "users/reminders.html",
        {"request": request, "user": user["username"] if user else None}
    )
from pydantic import BaseModel

# Pydantic model for user data update
class UserUpdate(BaseModel):
    username: str
    email: str
    password: str

# GET request to render the user update page
@app.get("/update", response_class=HTMLResponse)
async def update_page(request: Request):
    user = request.session.get("user")  # Get the logged-in user's data from the session
    if user:
        print(f"Active user: {user['username']}")  # Print active user in the terminal
        
        # Fetch user details from the database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT username, email FROM users WHERE username = %s", (user['username'],))
        user_data = cursor.fetchone()
        conn.close()

        if not user_data:
            return RedirectResponse("/", status_code=302)
    else:
        return RedirectResponse("/", status_code=302)

    return templates.TemplateResponse(
        "users/update.html",
        {"request": request, "user": {"username": user_data[0], "email": user_data[1]}}
    )


# POST request to update user details
@app.post("/update-user")
async def update_user(user: UserUpdate):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Hash the password before updating it
        hashed_password = hashlib.sha256(user.password.encode()).hexdigest()

        # Update user details in the database
        cursor.execute("""
            UPDATE users
            SET username = %s, email = %s, password = %s
            WHERE email = %s
        """, (user.username, user.email, hashed_password, user.email))
        conn.commit()

        cursor.close()
        conn.close()

        return {"message": "User details updated successfully!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



# ADMIN VIEW STARTS FROM HERE #

from fastapi import FastAPI, Request, Form, Depends

# Dummy admin credentials (Replace with database authentication)
ADMIN_CREDENTIALS = {"username": "admin", "password": "admin123"}


def get_current_admin(request: Request):
    """Check if admin is logged in; otherwise, redirect to login."""
    admin = request.session.get("admin")
    if not admin:
        print("No active admin. Redirecting to login page.")
        return RedirectResponse(url="/admin/login", status_code=302)  # Redirect to login
    print(f"Active Admin: {admin}")  # Print the logged-in admin
    return admin


@app.get("/admin/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Render the Admin Login Page."""
    user = request.session.get("admin")
    if user:
        return RedirectResponse(url="/admin/dashboard", status_code=303)
    
    return templates.TemplateResponse("admin/login.html", {"request": request})


@app.post("/admin/login")
async def admin_login(request: Request, username: str = Form(...), password: str = Form(...)):
    """Handle Admin Login."""
    if username == ADMIN_CREDENTIALS["username"] and password == ADMIN_CREDENTIALS["password"]:
        request.session["admin"] = username  # Store admin in session
        print(f"Admin {username} logged in successfully.")
        return RedirectResponse(url="/admin/dashboard", status_code=303)
    
    print("Invalid login attempt.")
    return templates.TemplateResponse("admin/login.html", {"request": request, "error": "Invalid credentials"})

@app.get("/admin/logout")
async def admin_logout(request: Request):
    """Log out the admin and redirect to login page."""
    print("Admin logged out.")
    request.session.clear()  # Clear session
    return RedirectResponse(url="/admin/login", status_code=302)

@app.get("/admin/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    admin = get_current_admin(request)
    if isinstance(admin, RedirectResponse):
        return admin  # Redirect if not logged in

    return templates.TemplateResponse("admin/index.html", {"request": request, "user": admin})


create_nutrition_table()
@app.get("/admin/nutrition", response_class=HTMLResponse)
async def nutrition_page(request: Request):
    admin = get_current_admin(request)
    if isinstance(admin, RedirectResponse):
        return admin  # Redirect if not logged in

    return templates.TemplateResponse("admin/nutrition.html", {"request": request, "user": admin})

# Pydantic model for request body validation
class NutritionRequest(BaseModel):
    nutrition_name: str
    quantity: str
    unit: str
    nutritional_value: str
    distribution_date: date
    anganwadi_center: str

# Endpoint to insert data
@app.post("/admin/add-nutrition")
def add_nutrition(nutrition: NutritionRequest):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Insert the nutrition record into the database
        cursor.execute("""
            INSERT INTO nutrition 
            (nutrition_name, quantity, unit, nutritional_value, distribution_date, anganwadi_center, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW())
        """, (
            nutrition.nutrition_name,
            nutrition.quantity,
            nutrition.unit,
            nutrition.nutritional_value,
            nutrition.distribution_date,
            nutrition.anganwadi_center
        ))

        # Fetch names and Anganwadi center information for approved mothers
        cursor.execute("""
            SELECT mother_name, anganwadi_name, email 
            FROM mother_card_registration 
            WHERE status = 'Approved' AND anganwadi_name = %s
        """, (nutrition.anganwadi_center,))
        approved_mothers = cursor.fetchall()

        # Send email notifications
        for mother in approved_mothers:
            mother_name = mother[0]
            anganwadi_name = mother[1]
            email = mother[2]

            subject = "Nutrition Collection Notification"
            body = f"""
            Dear {mother_name},

            This is to inform you that the following nutrition items have been added for distribution at your Anganwadi center: {anganwadi_name}.

            Nutrition Details:
            - Name: {nutrition.nutrition_name}
            - Quantity: {nutrition.quantity}
            - Unit: {nutrition.unit}

            Please visit the center to collect the items on: {nutrition.distribution_date} .

            Best regards,
            Child Care Team
            """
            send_email(email, subject, body)

        conn.commit()
        return {"message": "Nutrition record added successfully and email notifications sent!"}

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        cursor.close()
        conn.close()

        
@app.get("/admin/get-nutrition")
def get_nutrition():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch column names
    cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'nutrition'")
    columns = [col[0] for col in cursor.fetchall()]

    # Fetch data from the database
    cursor.execute("SELECT * FROM nutrition ORDER BY distribution_date DESC")
    nutrition_data = cursor.fetchall()
    conn.close()

    # Convert tuples to dictionaries
    nutrition_list = [dict(zip(columns, row)) for row in nutrition_data]

    # Debugging: Print the response structure

    return {"nutrition": nutrition_list}

@app.delete("/admin/delete-nutrition/{nutrition_id}")
def delete_nutrition(nutrition_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM nutrition WHERE nutrition_id = %s", (nutrition_id,))
    conn.commit()
    conn.close()

    return {"message": "Nutrition record deleted successfully"}

# Model for update request
class NutritionUpdate(BaseModel):
    nutrition_name: str
    quantity: str
    unit: str
    nutritional_value: str
    distribution_date: str
    anganwadi_center: str
@app.put("/admin/update-nutrition/{nutrition_id}")
def update_nutrition(nutrition_id: int, nutrition: NutritionUpdate):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE nutrition 
        SET nutrition_name = %s, quantity = %s, unit = %s, nutritional_value = %s, distribution_date = %s, anganwadi_center = %s, updated_at = NOW()
        WHERE nutrition_id = %s
    """, (
        nutrition.nutrition_name,
        nutrition.quantity,
        nutrition.unit,
        nutrition.nutritional_value,
        nutrition.distribution_date,
        nutrition.anganwadi_center,
        nutrition_id
    ))

    if cursor.rowcount == 0:
        conn.rollback()
        conn.close()
        raise HTTPException(status_code=404, detail="Nutrition record not found")

    conn.commit()
    conn.close()

    return {"message": "Nutrition record updated successfully"}


@app.get("/admin/patient", response_class=HTMLResponse)
async def patient_page(request: Request):
    
    admin = get_current_admin(request)
    if isinstance(admin, RedirectResponse):
        return admin  

    return templates.TemplateResponse("admin/patient.html", {"request": request, "user": admin})


@app.get("/admin/appointment", response_class=HTMLResponse)
async def appointment_page(request: Request):
    admin = get_current_admin(request)
    if isinstance(admin, RedirectResponse):
        return admin  

    return templates.TemplateResponse("admin/appointment.html", {"request": request, "user": admin})


@app.get("/admin/parent", response_class=HTMLResponse)
async def parent_page(request: Request):
    admin = get_current_admin(request)
    if isinstance(admin, RedirectResponse):
        return admin  
    return templates.TemplateResponse("admin/parent.html", {"request": request, "user": admin})


@app.get("/admin/vaccines", response_class=HTMLResponse)
async def vaccine_page(request: Request):
    admin = get_current_admin(request)
    if isinstance(admin, RedirectResponse):
        return admin  

    return templates.TemplateResponse("admin/vaccines.html", {"request": request, "user": admin})


@app.get("/admin/notification", response_class=HTMLResponse)
async def notification_page(request: Request):
    admin = get_current_admin(request)
    if isinstance(admin, RedirectResponse):
        return admin  

    return templates.TemplateResponse("admin/notification.html", {"request": request, "user": admin})


@app.get("/admin/mother", response_class=HTMLResponse)
async def mother_page(request: Request):
    admin = get_current_admin(request)
    if isinstance(admin, RedirectResponse):
        return admin  

    return templates.TemplateResponse("admin/mother.html", {"request": request, "user": admin})


@app.get("/admin/mothercard", response_class=HTMLResponse)
async def mother_card_page(request: Request):
    admin = get_current_admin(request)
    if isinstance(admin, RedirectResponse):
        return admin  

    return templates.TemplateResponse("admin/mothercard.html", {"request": request, "user": admin})



@app.get("/admin/add_staff", response_class=HTMLResponse)
async def add_staff(request: Request):
    admin = get_current_admin(request)
    if isinstance(admin, RedirectResponse):
        return admin  

    return templates.TemplateResponse("admin/add_staff.html", {"request": request, "user": admin})

create_staff_table()
# Pydantic model for request validation
# Pydantic Model for Staff
class Staff(BaseModel):
    name: str
    role: str
    phone: str
    email: str
    assigned_center: str
    address: str
    joining_date: str
    status: str
    password: str
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@app.post("/admin/add-staff")
def add_staff(staff: Staff):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Hash the default password "staff"
        hashed_password = pwd_context.hash("staff")

        # SQL Query to insert data
        cursor.execute("""
            INSERT INTO anganwadi_staff (name, role, phone, email, assigned_center, address, joining_date, status, password)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING staff_id;
        """, (staff.name, staff.role, staff.phone, staff.email, staff.assigned_center, staff.address, staff.joining_date, staff.status, hashed_password))

        staff_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()

        return {"message": "Staff added successfully", "staff_id": staff_id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
# Fetch all staff members
@app.get("/admin/get-staff")
def get_staff():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM anganwadi_staff")
    staff = cursor.fetchall()
    cursor.close()
    conn.close()
    return {"staff": staff}



from fastapi import FastAPI, HTTPException, Depends
from typing import List
import datetime
import psycopg2


# Endpoint 1: Retrieve all pending mother card registrations for admin review
@app.get("/admin/mothercard_requests")
def get_mothercard_requests():
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        query = """
            SELECT id, mother_name, husband_name, aadhar_number, phone_number, email, 
                   address, anganwadi_name, district, taluk, status, verified_by, verification_date
            FROM mother_card_registration
        """
        cursor.execute(query)
        records = cursor.fetchall()

        # If no records are found
        if not records:
            return {"message": "No pending mother card requests found."}

        # Formatting the response
        result = [
            {
                "id": row[0],
                "mother_name": row[1],
                "husband_name": row[2],
                "aadhar_number": row[3],
                "phone_number": row[4],
                "email": row[5],
                "address": row[6],
                "anganwadi_name": row[7],
                "district": row[8],
                "taluk": row[9],
                "status": row[10],
                "verified_by": row[11],
                "verification_date": row[12]
            }
            for row in records
        ]
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        cursor.close()
        conn.close()


from typing import Literal

# Enum validation for status
ValidStatus = Literal["Pending", "Approved", "Rejected"]

# Request Model
class StatusUpdate(BaseModel):
    status: ValidStatus

@app.patch("/api/update_status/{id}")
async def update_status(id: int, update_data: StatusUpdate):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Check if the ID exists
        cursor.execute("SELECT id FROM mother_card_registration WHERE id = %s;", (id,))
        record = cursor.fetchone()
        if not record:
            raise HTTPException(status_code=404, detail="Mother Card Request not found")

        # Update Query
        cursor.execute(
            """
            UPDATE mother_card_registration
            SET status = %s, verification_date = NOW()
            WHERE id = %s
            RETURNING id, status;
            """,
            (update_data.status, id)
        )

        conn.commit()
        updated_record = cursor.fetchone()
        return {"message": "Status updated successfully", "id": updated_record[0], "status": updated_record[1]}

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        cursor.close()
        conn.close()

# Endpoint 2: Update status of a mother card registration
@app.put("/admin/mothercard_approval/{mothercard_id}")
def update_mothercard_status(mothercard_id: int, status: str, verified_by: str):
    """
    Admin can approve/reject a mother card request.
    Status should be either 'Approved' or 'Rejected'.
    """
    if status not in ["Approved", "Rejected"]:
        raise HTTPException(status_code=400, detail="Invalid status. Use 'Approved' or 'Rejected'.")

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        query = """
            UPDATE mother_card_registration
            SET status = %s, verified_by = %s, verification_date = %s
            WHERE id = %s
        """
        cursor.execute(query, (status, verified_by, datetime.datetime.now(), mothercard_id))
        conn.commit()

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Mother Card request not found.")

        return {"message": f"Mother Card ID {mothercard_id} updated successfully to {status}"}

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        cursor.close()
        conn.close()



from asyncpg import Connection
import logging
import os
from datetime import datetime

logging.basicConfig(level=logging.INFO)

# Ensure the uploads directory exists
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this to your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




@app.get("/mother-card")
async def get_all_mother_cards(request: Request, db: psycopg2.extensions.connection = Depends(get_db_connection)):
    user = request.session.get("user")  
    print("User session:", user)

    if not user:
        return templates.TemplateResponse(
            "users/mother-card.html",
            {"request": request, "message": "User not logged in or session expired", "records": []}
        )

    try:
        with db.cursor() as cursor:
            cursor.execute("""
                SELECT id, first_name, middle_name, last_name, husband_name, 
                       date_of_birth, aadhar_number, mobile_number, 
                       alternate_mobile_number, email, bank_account_number, 
                       residential_address, pregnancy_report, residence_proof
                FROM mother_card_applications WHERE user_id = %s
            """, (user["userid"],))
            print("Fetched records:", records)

            columns = [desc[0] for desc in cursor.description]  # Fetch column names
            records = [dict(zip(columns, row)) for row in cursor.fetchall()]  # Convert to list of dicts

        return templates.TemplateResponse(
            "users/mother-card.html",
            {"request": request, "records": records, "user": user["username"]}
        )

    except Exception as e:
        print(f"Database error: {str(e)}")
        return templates.TemplateResponse(
            "users/mother-card.html",
            {"request": request, "message": f"Database error: {str(e)}", "records": [], "user": user["username"]}
        )
        
        
        
        
import json
from datetime import date
from fastapi import FastAPI

# Assuming this is the application model or response model
class MotherCardApplication:
    def __init__(self, application_date, name, other_field):
        self.application_date = application_date
        self.name = name
        self.other_field = other_field
    
    def dict(self):
        return {
            'application_date': self.application_date.isoformat() if isinstance(self.application_date, date) else self.application_date,
            'name': self.name,
            'other_field': self.other_field
        }

# Custom JSON encoder for date objects
def custom_converter(obj):
    if isinstance(obj, date):
        return obj.isoformat()  # Convert date to ISO format string
    raise TypeError(f"Type {type(obj)} not serializable")

from psycopg2 import sql, Error


@app.get("/book")
async def book(request: Request):
    user = request.session.get("user")
    print("Session Data:", user)  # Debugging: Check if user exists

    if not user:
        return HTMLResponse(
            """
            <script>
                alert("Please log in first.");
                window.location.href = "/login";
            </script>
            """,
            status_code=200,
        )

    return templates.TemplateResponse("users/book.html", {"request": request, "user": user["username"]})

    
from fastapi import Request, Body
# Pydantic model for request body
class MotherCard(BaseModel):
    full_name: str
    aadhar_number: str
    age: int
    address: str
    contact_number: str

@app.post("/request_mother")
def register_mother(data: MotherCard):
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
    INSERT INTO mother_card_request (full_name, aadhar_number, age, address, contact_number)
    VALUES (%s, %s, %s, %s, %s)
    RETURNING id;
    """
    
    try:
        cursor.execute(query, (data.full_name, data.aadhar_number, data.age, data.address, data.contact_number))
        mother_id = cursor.fetchone()[0]  # ✅ Access first element of tuple
        conn.commit()
        return {"message": "Registration successful", "mother_id": mother_id}
    except Exception as e:
        conn.rollback()
        return {"error": str(e)}
    finally:
        cursor.close()
        conn.close()



# Vaccine model with quantity added
class Vaccine(BaseModel):
    vaccine_name: str
    availability: bool
    min_age: int
    max_age: int = None
    manufactured_date: date
    expiry_date: date
    quantity: int  # Added quantity field

@app.post("/vaccines/add")
def add_vaccine(vaccine: Vaccine):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection error")

    try:
        cursor = conn.cursor()
        query = """
        INSERT INTO vaccines (vaccine_name, availability, min_age, max_age, manufactured_date, expiry_date, quantity)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            vaccine.vaccine_name,
            vaccine.availability,  # ✅ Store boolean directly
            vaccine.min_age, 
            vaccine.max_age, 
            vaccine.manufactured_date, 
            vaccine.expiry_date, 
            vaccine.quantity
        ))
        conn.commit()

        cursor.close()
        conn.close()
        return {"message": "Vaccine added successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


from typing import List, Optional
# Endpoint to Get All Vaccines
@app.get("/vaccines", response_model=List[Vaccine])
def get_vaccines():
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection error")

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT vaccine_name, availability, min_age, max_age, manufactured_date, expiry_date, quantity FROM vaccines")
        vaccines = cursor.fetchall()
        cursor.close()
        conn.close()

        return [
            {
                "vaccine_name": row[0],
                "availability": row[1],
                "min_age": row[2],
                "max_age": row[3],
                "manufactured_date": row[4],
                "expiry_date": row[5],
                "quantity": row[6]  # Add quantity field
            }
            for row in vaccines
        ]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.put("/vaccines/update/{vaccine_name}")
def update_vaccine(vaccine_name: str, vaccine: Vaccine):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection error")

    try:
        cursor = conn.cursor()
        query = """
        UPDATE vaccines
        SET availability = %s, min_age = %s, max_age = %s, manufactured_date = %s, expiry_date = %s, quantity = %s
        WHERE vaccine_name = %s
        """
        cursor.execute(query, (
            int(vaccine.availability), vaccine.min_age, vaccine.max_age,
            vaccine.manufactured_date, vaccine.expiry_date, vaccine.quantity,
            vaccine_name
        ))
        conn.commit()
        cursor.close()
        conn.close()

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Vaccine not found")

        return {"message": "Vaccine updated successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/vaccines/delete/{vaccine_name}")
def delete_vaccine(vaccine_name: str):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection error")

    try:
        cursor = conn.cursor()
        query = "DELETE FROM vaccines WHERE vaccine_name = %s"
        cursor.execute(query, (vaccine_name,))
        conn.commit()
        cursor.close()
        conn.close()

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Vaccine not found")

        return {"message": "Vaccine deleted successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




@app.get("/staff_vaccine")  # Fix the route to match the link in the navbar
def get_vaccines(request: Request):
    return templates.TemplateResponse("anganwadi/staff_vaccine.html", {"request": request})

@app.get("/api/get_vaccines")
def get_vaccines():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM vaccines")
        vaccines = cursor.fetchall()
        conn.close()
        return vaccines
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

conn = get_db_connection()
cursor = conn.cursor()
class VaccineUpdate(BaseModel):
    vaccine_name: Optional[str] = None
    availability: Optional[bool] = None
    min_age: Optional[int] = None
    max_age: Optional[int] = None
    manufactured_date: Optional[str] = None
    expiry_date: Optional[str] = None
    quantity: Optional[int] = None  # Added quantity field

# Endpoint to Update Vaccine
@app.put("/vaccine_update/{vaccine_id}")
def update_vaccine(vaccine_id: int, vaccine: VaccineUpdate):
    updates = []
    values = []
    if vaccine.vaccine_name:
        updates.append("vaccine_name = %s")
        values.append(vaccine.vaccine_name)
    
    if updates:
        values.append(vaccine_id)
        update_query = f"UPDATE vaccines SET {', '.join(updates)} WHERE vaccine_id = %s"
        cursor.execute(update_query, tuple(values))
        conn.commit()
        return {"message": "Vaccine updated successfully"}
    
    raise HTTPException(status_code=400, detail="No valid fields to update")

@app.delete("/vaccine_delete/{vaccine_id}")
def delete_vaccine(vaccine_id: int):
    cursor.execute("DELETE FROM vaccines WHERE vaccine_id = %s", (vaccine_id,))
    conn.commit()
    return {"message": "Vaccine deleted successfully"}







# Staff or Anganwadi

from itsdangerous import URLSafeSerializer
from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from itsdangerous import URLSafeSerializer

# Session Middleware
SECRET_KEY = "your_secret_key"
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

# Template directory setup
templates = Jinja2Templates(directory="templates")

# Session serializer
serializer = URLSafeSerializer(SECRET_KEY)

# Dummy login credentials (Replace with database check)
ANGANWADI_CREDENTIALS = {
    "staff": "staff",
}

# ----------------- Anganwadi Staff Routes -----------------


from fastapi import FastAPI, Depends, HTTPException, Form, Request, Response
from passlib.context import CryptContext


# Logout Endpoint
@app.get("/staff_logout")
async def staff_logout(request: Request, response: Response):
    request.session.clear()
    response.delete_cookie("staff_session")
    return RedirectResponse(url="/anganwadi/login", status_code=302)



@app.get("/home")
def render_home_page(request: Request):
    return templates.TemplateResponse("anganwadi/home.html", {"request": request})

@app.get("/anganwadi/login", response_class=HTMLResponse)
async def anganwadi_login_page(request: Request):
    """Render Anganwadi login page"""
    return templates.TemplateResponse("anganwadi/login.html", {"request": request, "user_type": "Anganwadi"})

@app.post("/anganwadi/login")
async def anganwadi_login(request: Request, username: str = Form(...), password: str = Form(...)):
    """Handles Anganwadi staff login with session management"""
    if username in ANGANWADI_CREDENTIALS and ANGANWADI_CREDENTIALS[username] == password:
        # Store session details for staff
        request.session["staff"] = serializer.dumps({"username": username, "role": "anganwadi"})
        return RedirectResponse(url="/anganwadi/home", status_code=303)
    
    return templates.TemplateResponse("anganwadi/login.html", {"request": request, "user_type": "Anganwadi", "error": "Invalid credentials"})




@app.get("/anganwadi/home", response_class=HTMLResponse)
async def anganwadi_dashboard(request: Request):
    """Renders the Anganwadi staff dashboard if logged in"""
    staff_session = request.session.get("staff")
    
    if not staff_session:
        return RedirectResponse(url="/anganwadi/login")

    # Decode session data
    staff_data = serializer.loads(staff_session)

    return templates.TemplateResponse("anganwadi/home.html", {
        "request": request,
        "username": staff_data["username"],
        "role": staff_data["role"]
    })

from fastapi.responses import HTMLResponse
@app.get("/anganwadi/logout", response_class=HTMLResponse)
async def anganwadi_logout(request: Request):
    """Clears session and returns JavaScript alert"""
    request.session.clear()
    
    return """
    <script>
        alert("Logout Successful!");
        window.location.href = "/anganwadi/login";  // Redirect after alert
    </script>
    """
@app.get("/form", response_class=HTMLResponse)
async def serve_form(request: Request):
    return templates.TemplateResponse("anganwadi/form.html", {"request": request})
# Handle Form Submission and Insert Data Using SQL
# Pydantic Model for validation


from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr, StringConstraints
from typing import Annotated, Optional
import datetime

class MotherCardRegistration(BaseModel):
    mother_name: str
    husband_name: str
    last_name: Optional[str] = None
    date_of_birth: datetime.date
    aadhar_number: Annotated[str, StringConstraints(pattern="^[0-9]{12}$")]
    phone_number: Annotated[str, StringConstraints(pattern="^[0-9]{10,15}$")]
    email: EmailStr
    address: str
    anganwadi_name: str
    anganwadi_staff_name: str
    asha_staff_name: Optional[str] = None
    district: str
    taluk: str
    anganwadi_address: str
    blood_group: Optional[str] = None
    height_cm: Optional[int] = None
    weight_kg: Optional[float] = None
    number_of_pregnancies: Optional[int] = 0
    expected_delivery_date: Optional[datetime.date] = None
    first_trimester_checkup: Optional[datetime.date] = None
    second_trimester_checkup: Optional[datetime.date] = None
    third_trimester_checkup: Optional[datetime.date] = None
    tetanus_vaccine: Optional[bool] = False
    iron_folic_acid_supplements: Optional[bool] = False
    other_vaccinations: Optional[str] = None
    delivery_date: Optional[datetime.date] = None
    delivery_hospital: Optional[str] = None
    child_name: Optional[str] = None
    child_gender: Optional[str] = None
    child_weight_kg: Optional[float] = None
    terms_agreed: Optional[bool] = False
    status: Optional[str] = "Pending"
    verified_by: Optional[str] = None
    verification_date: Optional[datetime.datetime] = None
    userid: str  # FK to users table
    last_menstrual_period: Optional[datetime.date] = None  # New field

    
@app.post("/register_mother")
def register_mother(data: MotherCardRegistration):
    conn = get_db_connection()
    cursor = conn.cursor()
    print("Received Data:", data.model_dump())  # Debugging

    try:
        query = """
            INSERT INTO mother_card_registration (
                mother_name, husband_name, last_name, date_of_birth, aadhar_number,
                phone_number, email, address, anganwadi_name, anganwadi_staff_name,
                asha_staff_name, district, taluk, anganwadi_address, blood_group,
                height_cm, weight_kg, number_of_pregnancies, expected_delivery_date,
                first_trimester_checkup, second_trimester_checkup, third_trimester_checkup,
                tetanus_vaccine, iron_folic_acid_supplements, other_vaccinations, delivery_date,
                delivery_hospital, child_name, child_gender, child_weight_kg, terms_agreed,
                status, verified_by, verification_date, userid, last_menstrual_period
            ) VALUES (
                %(mother_name)s, %(husband_name)s, %(last_name)s, %(date_of_birth)s, %(aadhar_number)s,
                %(phone_number)s, %(email)s, %(address)s, %(anganwadi_name)s, %(anganwadi_staff_name)s,
                %(asha_staff_name)s, %(district)s, %(taluk)s, %(anganwadi_address)s, %(blood_group)s,
                %(height_cm)s, %(weight_kg)s, %(number_of_pregnancies)s, %(expected_delivery_date)s,
                %(first_trimester_checkup)s, %(second_trimester_checkup)s, %(third_trimester_checkup)s,
                %(tetanus_vaccine)s, %(iron_folic_acid_supplements)s, %(other_vaccinations)s, %(delivery_date)s,
                %(delivery_hospital)s, %(child_name)s, %(child_gender)s, %(child_weight_kg)s, %(terms_agreed)s,
                %(status)s, %(verified_by)s, %(verification_date)s, %(userid)s, %(last_menstrual_period)s
            )
        """

        cursor.execute(query, data.model_dump())
        conn.commit()

        return {"message": "Mother registered successfully"}

    except Exception as e:
        conn.rollback()
        print("Error:", str(e))  # Debugging output
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        cursor.close()
        conn.close()

@app.get("/user_ids")
def get_user_ids():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT userid, username FROM users")  # Ensure correct column names
        users = [{"id": row[0], "username": row[1]} for row in cursor.fetchall()]
        return {"users": users}
    except Exception as e:
        print(f"Database error: {e}")  # Print error for debugging
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()




from fastapi import FastAPI, Query

@app.get("/status")
async def check_status_page(request: Request):
    return templates.TemplateResponse("anganwadi/status.html", {"request": request})
from psycopg2.extras import DictCursor


@app.get("/api/check_status")
async def check_status(
    query: Optional[str] = Query(None, description="Search by name, email, or phone"),
    status: Optional[str] = Query(None, description="Filter by status (Pending, Approved, Rejected)")
):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        sql_query = "SELECT * FROM mother_card_registration WHERE TRUE"
        params = []

        if query:
            sql_query += " AND (mother_name ILIKE %s OR email ILIKE %s OR phone_number ILIKE %s)"
            params.extend([f"%{query}%", f"%{query}%", f"%{query}%"])

        if status:
            sql_query += " AND status = %s"
            params.append(status)

        cursor.execute(sql_query, params)
        results = cursor.fetchall()

        cursor.close()
        conn.close()

        return {"data": [dict(row) for row in results]}  # Convert DictCursor row to a dictionary

    except Exception as e:
        return {"error": str(e)}
    

@app.get("/request_forms")
def get_request_forms():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM mother_card_request;"
    
    try:
        cursor.execute(query)
        records = cursor.fetchall()
        
        # Fetch column names
        columns = [desc[0] for desc in cursor.description]
        
        # Convert data into dictionary format
        result = [dict(zip(columns, row)) for row in records]
        
        return {"data": result}
    except Exception as e:
        return {"error": str(e)}
    finally:
        cursor.close()
        conn.close()

@app.get("/request")
def render_request_page(request: Request):
    return templates.TemplateResponse("anganwadi/request.html", {"request": request})

# ✅ Pydantic model for request body
class StatusUpdate(BaseModel):
    status: str

# ✅ POST endpoint for updating status & attempts
@app.post("/update_status/{id}")
def update_status(id: int, status_update: StatusUpdate):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # ✅ Get current attempts left
        cursor.execute("SELECT update_attempts FROM mother_card_request WHERE id = %s", (id,))
        record = cursor.fetchone()

        if record is None:
            raise HTTPException(status_code=404, detail="Record not found")

        attempts_left = record[0]

        if attempts_left <= 0:
            raise HTTPException(status_code=400, detail="No more update attempts left")

        # ✅ Update the status and decrease attempts
        cursor.execute("""
            UPDATE mother_card_request 
            SET status = %s, update_attempts = update_attempts - 1
            WHERE id = %s
        """, (status_update.status, id))

        conn.commit()

        # ✅ Get updated attempts count
        cursor.execute("SELECT update_attempts FROM mother_card_request WHERE id = %s", (id,))
        new_attempts_left = cursor.fetchone()[0]

        return {
            "message": "Status updated successfully",
            "status": status_update.status,
            "update_attempts": new_attempts_left
        }

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        cursor.close()
        conn.close()
        
@app.get("/charts-data")
async def get_chart_data():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 1. Total Registered Mothers per District
        cursor.execute("SELECT district, COUNT(*) FROM mother_card_registration GROUP BY district;")
        districts = cursor.fetchall()
        district_labels = [row[0] for row in districts]
        district_counts = [row[1] for row in districts]
        total_districts = sum(district_counts)

        # 2. Number of Pregnancies Distribution
        cursor.execute("SELECT number_of_pregnancies, COUNT(*) FROM mother_card_registration GROUP BY number_of_pregnancies;")
        pregnancies = cursor.fetchall()
        pregnancies_labels = [str(row[0]) for row in pregnancies]
        pregnancies_counts = [row[1] for row in pregnancies]
        total_pregnancies = sum(pregnancies_counts)

        # 3. Vaccine Availability Status
        cursor.execute("SELECT vaccine_name, quantity FROM vaccines;")
        vaccines = cursor.fetchall()
        vaccine_labels = [row[0] for row in vaccines]
        vaccine_quantities = [row[1] for row in vaccines]
        total_vaccines = sum(vaccine_quantities)

        # 4. Age Distribution of Registered Mothers
        cursor.execute("SELECT age, COUNT(*) FROM mother_card_request GROUP BY age ORDER BY age;")
        age_distribution = cursor.fetchall()
        age_labels = [str(row[0]) for row in age_distribution]
        age_counts = [row[1] for row in age_distribution]
        total_age_distribution = sum(age_counts)

        # 5. Status of Mother Card Requests
        cursor.execute("SELECT status, COUNT(*) FROM mother_card_request GROUP BY status;")
        status_data = cursor.fetchall()
        status_labels = [row[0] for row in status_data]
        status_counts = [row[1] for row in status_data]
        total_status_requests = sum(status_counts)

        # 6. Trimester Checkups Completed
        cursor.execute("""
            SELECT 'First Trimester' AS trimester, COUNT(first_trimester_checkup) FROM mother_card_registration WHERE first_trimester_checkup IS NOT NULL
            UNION
            SELECT 'Second Trimester', COUNT(second_trimester_checkup) FROM mother_card_registration WHERE second_trimester_checkup IS NOT NULL
            UNION
            SELECT 'Third Trimester', COUNT(third_trimester_checkup) FROM mother_card_registration WHERE third_trimester_checkup IS NOT NULL;
        """)
        trimester_data = cursor.fetchall()
        trimester_labels = [row[0] for row in trimester_data]
        trimester_counts = [row[1] for row in trimester_data]
        total_trimester_checkups = sum(trimester_counts)

        conn.close()

        return JSONResponse(content={
            "districts": {"labels": district_labels, "data": district_counts, "total": total_districts},
            "pregnancies": {"labels": pregnancies_labels, "data": pregnancies_counts, "total": total_pregnancies},
            "vaccines": {"labels": vaccine_labels, "data": vaccine_quantities, "total": total_vaccines},
            "age_distribution": {"labels": age_labels, "data": age_counts, "total": total_age_distribution},
            "status": {"labels": status_labels, "data": status_counts, "total": total_status_requests},
            "trimester_checkups": {"labels": trimester_labels, "data": trimester_counts, "total": total_trimester_checkups}
        })

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


create_anganwadi_request_table()
from fastapi import FastAPI, HTTPException
import psycopg2
from pydantic import BaseModel, constr, conint
from typing import Literal


# Request Model
class RequestModel(BaseModel):
    staff_name: constr(min_length=1, max_length=255)
    center_name: constr(min_length=1, max_length=255)
    request_type: Literal["Vaccine", "Nutrition"]  # ✅ Correct way for Pydantic v1
    item_name: constr(min_length=1, max_length=255)
    quantity: conint(gt=0)  # Quantity must be greater than 0
    unit: constr(min_length=1, max_length=50)
    description: str

@app.post("/request")
def create_request(request: RequestModel):
    conn = None
    cursor = None
    try:
        # Connect to the database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        sql = """
        INSERT INTO anganwadi_requests (
            staff_name, center_name, request_type, item_name, quantity, unit, description
        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING request_id;
        """

        cursor.execute(sql, (
            request.staff_name, request.center_name, request.request_type,
            request.item_name, request.quantity, request.unit, request.description
        ))
        
        request_id = cursor.fetchone()[0]
        conn.commit()

        return {"message": "Request submitted successfully", "request_id": request_id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.get("/request_vaccines_nutrition")  # Fix the route to match the link in the navbar
def get_vaccines(request: Request):
    return templates.TemplateResponse("anganwadi/request_vaccines_nutrition.html", {"request": request})

@app.get("/requests_list")
def get_requests():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM anganwadi_requests ORDER BY request_date DESC;"
        cursor.execute(query)
        records = cursor.fetchall()

        # Get column names dynamically
        col_names = [desc[0] for desc in cursor.description]
        
        # Convert to list of dictionaries
        result = [dict(zip(col_names, row)) for row in records]

        cursor.close()
        conn.close()
        return result

    except Exception as e:
        return {"error": str(e)}

# API to delete a request
@app.delete("/delete_request/{request_id}")
def delete_request(request_id: int):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM anganwadi_requests WHERE request_id = %s", (request_id,))
    conn.commit()
    cur.close()
    conn.close()
    return {"message": "Request deleted successfully"}

# Model for status update request
class StatusUpdate(BaseModel):
    request_status: str
@app.put("/update_status/{request_id}")
def update_request_status(request_id: int, status_update: StatusUpdate):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Debugging: Print the received data
        print(f"Updating request_id {request_id} with status {status_update.request_status}")

        # Update query
        query = """
        UPDATE anganwadi_requests 
        SET request_status = %s, updated_at = CURRENT_TIMESTAMP
        WHERE request_id = %s
        """
        cursor.execute(query, (status_update.request_status, request_id))

        if cursor.rowcount == 0:
            conn.rollback()
            return HTTPException(status_code=404, detail="Request ID not found")

        conn.commit()
        cursor.close()
        conn.close()

        print("Update successful")  # Debugging
        return {"message": "Request status updated successfully"}

    except Exception as e:
        print("Error:", str(e))  # Debugging
        return HTTPException(status_code=500, detail=str(e))


# Model for status update request
class StatusUpdate(BaseModel):
    request_status: str

@app.put("/update_vaccine_status/{request_id}")
def update_vaccine_status(request_id: int, status_update: StatusUpdate):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Update the request status
        query = """
        UPDATE anganwadi_requests 
        SET request_status = %s, updated_at = CURRENT_TIMESTAMP
        WHERE request_id = %s AND request_type = 'Vaccine'
        """
        cursor.execute(query, (status_update.request_status, request_id))
        conn.commit()

        if cursor.rowcount == 0:
            conn.rollback()
            raise HTTPException(status_code=404, detail="Vaccine request not found")

        cursor.close()
        conn.close()
        return {"message": "Vaccine request status updated successfully"}
    
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))

import jinja2
from psycopg2.extras import RealDictCursor

template_loader = jinja2.FileSystemLoader("templates")
template_env = jinja2.Environment(loader=template_loader)
@app.get("/mother_card_report", response_class=HTMLResponse)
def read_data(db_conn=Depends(get_db_connection)):
    with db_conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute("SELECT * FROM mother_card_registration;")
        records = cursor.fetchall()

    # Render HTML with data
    template = template_env.get_template("users/report.html")
    return template.render(records=records)

from pydantic import BaseModel, EmailStr, conint, condecimal, constr
from typing import Optional


from fastapi import FastAPI, HTTPException, Depends
from typing import Optional as TypingOptional
from psycopg2.extras import RealDictCursor
from pydantic import BaseModel, EmailStr, Field, conint, condecimal
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, conint, condecimal
from typing import Optional

class MotherCardUpdate(BaseModel):
    mother_name: Optional[str] = None
    husband_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[str] = None
    aadhar_number: Optional[str] = Field(None, min_length=12, max_length=12, pattern="^[0-9]{12}$")
    phone_number: Optional[str] = Field(None, min_length=10, max_length=15, pattern="^[0-9]{10,15}$")
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    anganwadi_name: Optional[str] = None
    anganwadi_staff_name: Optional[str] = None
    asha_staff_name: Optional[str] = None
    district: Optional[str] = None
    taluk: Optional[str] = None
    anganwadi_address: Optional[str] = None
    blood_group: Optional[str] = Field(None, pattern="^(A\+|A-|B\+|B-|O\+|O-|AB\+|AB-)$")
    height_cm: Optional[conint(ge=50, le=250)] = None
    weight_kg: Optional[condecimal(ge=30, le=150, max_digits=5, decimal_places=2)] = None
    number_of_pregnancies: Optional[int] = None
    expected_delivery_date: Optional[str] = None
    first_trimester_checkup: Optional[str] = None
    second_trimester_checkup: Optional[str] = None
    third_trimester_checkup: Optional[str] = None
    tetanus_vaccine: Optional[bool] = None
    iron_folic_acid_supplements: Optional[bool] = None
    other_vaccinations: Optional[str] = None
    delivery_date: Optional[str] = None
    delivery_hospital: Optional[str] = None
    child_name: Optional[str] = None
    child_gender: Optional[str] = None
    child_weight_kg: Optional[condecimal(ge=0.5, le=6.0, max_digits=5, decimal_places=2)] = None
    terms_agreed: Optional[bool] = None
    status: Optional[str] = None
    verified_by: Optional[str] = None
    verification_date: Optional[str] = None

@app.patch("/update-mother-card/{id}")
def update_mother_card(id: int, update_data: MotherCardUpdate):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Fetch existing record
                cur.execute("SELECT * FROM mother_card_registration WHERE id = %s", (id,))
                existing_record = cur.fetchone()

                if not existing_record:
                    raise HTTPException(status_code=404, detail="Record not found")

                # Get column names
                column_names = [desc[0] for desc in cur.description]
                existing_data = dict(zip(column_names, existing_record))

                # Merge with new update data
                update_dict = update_data.dict(exclude_unset=True)
                existing_data.update(update_dict)

                # Ensure we are updating at least one field
                if not update_dict:
                    raise HTTPException(status_code=400, detail="No fields provided for update")

                # Generate SQL update query dynamically
                set_clause = ", ".join([f"{key} = %s" for key in update_dict.keys()])
                values = list(update_dict.values()) + [id]

                update_query = f"UPDATE mother_card_registration SET {set_clause} WHERE id = %s RETURNING *"

                # Execute update query
                cur.execute(update_query, values)
                updated_row = cur.fetchone()
                conn.commit()

                if not updated_row:
                    raise HTTPException(status_code=500, detail="Failed to update record")

                updated_data = dict(zip(column_names, updated_row))

        return {"message": "Record updated successfully", "updated_data": updated_data}

    except Exception as e:
        print(f"Error updating record: {e}")  # Logs error to console
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get-mother-card/{id}")
def get_mother_card(id: int):
    conn = get_db_connection()
    cur = conn.cursor()

    # Fetch the existing record
    cur.execute("SELECT * FROM mother_card_registration WHERE id = %s", (id,))
    existing_record = cur.fetchone()
    cur.close()
    conn.close()

    if not existing_record:
        raise HTTPException(status_code=404, detail="Record not found")

    # Convert to dictionary with column names (modify based on your DB schema)
    columns = [desc[0] for desc in cur.description]
    record_dict = dict(zip(columns, existing_record))

    return record_dict


# Route to render the HTML page
@app.get("/updates_records", response_class=HTMLResponse)
def update_page(request: Request):
    return templates.TemplateResponse("anganwadi/updates_records.html", {"request": request})
    
@app.get("/user_report", response_class=HTMLResponse)
def user_report(request: Request):
    user = request.session.get("user")
    print("Session Data:", user)  # Debugging
    if not user:
        return RedirectResponse(url="/login", status_code=303)

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Fetch report where `userid` matches the logged-in user
        cursor.execute("SELECT * FROM mother_card_registration WHERE userid = %s", (user["userid"],))
        record = cursor.fetchone()

        # print("Database Record Found:", record)  # Debugging

        if not record:
            return templates.TemplateResponse(
                "users/user_report.html",
                {"request": request, "user": user["username"], "report": None},
            )

        # Convert record to dictionary
        columns = [desc[0] for desc in cursor.description]
        report_data = dict(zip(columns, record))

        return templates.TemplateResponse(
            "users/user_report.html",
            {"request": request, "user": user["username"], "report": report_data},
        )

    except Exception as e:
        print(f"Database error: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while fetching the report.")

    finally:
        cursor.close()
        conn.close()




####################################### 

from typing import Annotated

@app.get("/mother_checkup_history")
def get_mother_checkup_history(request: Request):
    return templates.TemplateResponse("anganwadi/mother_checkup_history.html", {"request": request})

class MotherCheckupRecord(BaseModel):
    mother_id: int
    checkup_type: Annotated[str, constr(pattern="^(First Trimester|Second Trimester|Third Trimester|Postnatal)$")]
    checkup_date: date
    blood_pressure: Optional[str] = None  # Example: '120/80'
    weight_kg: Optional[Annotated[float, condecimal(ge=30, le=150, max_digits=5, decimal_places=2)]] = None
    hemoglobin_level: Optional[Annotated[float, condecimal(ge=0, le=20, max_digits=4, decimal_places=2)]] = None
    notes: Optional[str] = None


@app.post("/mother_checkup_history")
async def insert_mother_checkup_record(data: MotherCheckupRecord):
    """
    Insert a new record into the mother_checkup_history table.
    """
    conn = None
    cursor = None

    try:
        # Establish database connection
        conn = get_db_connection()
        cursor = conn.cursor()

        # Insert query
        query = """
        INSERT INTO mother_checkup_history (
            mother_id, checkup_type, checkup_date, blood_pressure, weight_kg, hemoglobin_level, notes
        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING checkup_id;
        """
        cursor.execute(query, (
            data.mother_id,
            data.checkup_type,
            data.checkup_date,
            data.blood_pressure,
            data.weight_kg,
            data.hemoglobin_level,
            data.notes
        ))

        # Commit the transaction
        conn.commit()

        # Fetch the inserted record's ID
        checkup_id = cursor.fetchone()[0]

        return {"message": "Mother checkup record inserted successfully", "checkup_id": checkup_id}

    except Exception as e:
        if conn:
            conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error inserting mother checkup record: {str(e)}")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            

class MotherCheckupRecordResponse(BaseModel):
    checkup_id: int
    mother_id: int
    checkup_type: str
    checkup_date: date
    blood_pressure: str
    weight_kg: float
    hemoglobin_level: float
    notes: str
@app.get("/mother_checkup_history_fetch")
async def get_mother_checkup_history():
    """
    Fetch all mother checkup records.
    """
    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Fetch records
        query = """
        SELECT checkup_id, mother_id, checkup_type, checkup_date, blood_pressure, weight_kg, hemoglobin_level, notes
        FROM mother_checkup_history;
        """
        cursor.execute(query)
        records = cursor.fetchall()

        # Convert records into JSON format
        result = [
            {
                "checkup_id": row[0],
                "mother_id": row[1],
                "checkup_type": row[2],
                "checkup_date": row[3].strftime("%Y-%m-%d"),
                "blood_pressure": row[4],
                "weight_kg": row[5],
                "hemoglobin_level": row[6],
                "notes": row[7],
            }
            for row in records
        ]

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching data: {str(e)}")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
