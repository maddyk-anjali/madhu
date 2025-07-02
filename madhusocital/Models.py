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
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from apscheduler.schedulers.background import BackgroundScheduler
import logging
from datetime import datetime, timedelta


# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG to capture all levels of logs
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("email_scheduler.log"),  # Log to a file
        logging.StreamHandler()  # Log to the console
    ]
)



SMTP_SERVER = "smtp.gmail.com"  # Replace with your SMTP server
SMTP_PORT = 587
EMAIL_ADDRESS = "madhukalakeri@gmail.com"  # Replace with your email
EMAIL_PASSWORD = "swqr hvqk xhkh ehac"  # Replace with your email password


DB_USER = "postgres"
DB_PASSWORD = "Madhu@123"
DB_HOST = "localhost"
DB_PORT = "5432"
DEFAULT_DB = "postgres"  # Default database to connect to
NEW_DB = "child_care" 

# Database Functions
def get_db_connection():
    """
    Establish a connection to the PostgreSQL database.
    """
    conn = psycopg2.connect(
        dbname=NEW_DB,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    return conn


def create_database():
    """
    Create the database if it doesn't exist.
    """
    try:
        conn = psycopg2.connect(
            dbname=DEFAULT_DB,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        conn.set_isolation_level(0)  # Enable autocommit
        cursor = conn.cursor()

        # Check if the database already exists
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{NEW_DB}'")
        exists = cursor.fetchone()

        if not exists:
            cursor.execute(f"CREATE DATABASE {NEW_DB}")
            print(f"Database '{NEW_DB}' created successfully!")
        else:
            print(f"Database '{NEW_DB}' already exists.")

        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error while creating database: {e}")


def create_user_table():
    """
    Create the users table in the database.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        create_table_query = """
        CREATE TABLE IF NOT EXISTS users (
            userid SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        cursor.execute(create_table_query)

        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error while creating table: {e}")

def create_vaccine_table():
    """
    Create the vaccines table in the database.
    """
    try:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()

            create_table_query = """
            CREATE TABLE IF NOT EXISTS vaccines (
            vaccine_id SERIAL PRIMARY KEY,
            vaccine_name VARCHAR(100) NOT NULL,
            availability BOOLEAN DEFAULT TRUE,
            quantity INT NOT NULL CHECK (quantity >= 0),
            min_age INT NOT NULL CHECK (min_age >= 0),
            max_age INT CHECK (max_age >= min_age),
            manufactured_date DATE NOT NULL,
            expiry_date DATE
        );

            """
            cursor.execute(create_table_query)

            conn.commit()
            cursor.close()
            conn.close()
            print("Vaccines table created successfully.")
    except Exception as e:
        print(f"Error while creating table: {e}")

def insert_user(username, email, password):
    """
    Insert a new user into the users table.
    """
    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        insert_query = """
        INSERT INTO users (username, email, password, created_at)
        VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
        RETURNING userid;
        """
        cursor.execute(insert_query, (username, email, hashed_password))

        user_id = cursor.fetchone()[0]

        conn.commit()
        cursor.close()
        conn.close()

        print(f"User '{username}' successfully created with ID {user_id}")
        return user_id

    except Exception as e:
        print(f"Error inserting user: {str(e)}")
        raise HTTPException(status_code=500, detail="Error inserting user.")


def check_user_credentials(username, password):
    """
    Check if the username and password match any record in the database.
    """
    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM users WHERE username = %s AND password = %s
        """, (username, hashed_password))

        user = cursor.fetchone()

        cursor.close()
        conn.close()

        return user

    except Exception as e:
        print(f"Error checking credentials: {str(e)}")
        raise HTTPException(status_code=500, detail="Error checking credentials.")




def create_mother_card_request():
    """
    Create the mother_card_request table in the database.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        create_table_query = """
        CREATE TABLE mother_card_request (
            id SERIAL PRIMARY KEY,  -- ✅ Uses SERIAL instead of AUTOINCREMENT
            full_name TEXT NOT NULL,
            aadhar_number VARCHAR(12) UNIQUE NOT NULL,
            age INTEGER NOT NULL,
            address TEXT NOT NULL,
            contact_number TEXT NOT NULL,
            status TEXT DEFAULT 'Not visited',
            update_attempts INTEGER DEFAULT 3  -- ✅ Tracks update attempts
        );



        """
        cursor.execute(create_table_query)

        conn.commit()
        cursor.close()
        conn.close()
        print("Mother Card Request able created successfully.")    
    except Exception as e:
        print(f"Error while creating table: {e}")



def create_mother_card_table():
    """
    Create the mother_card table in the database.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        create_table_query = """
        -- Create ENUM types (if they don't exist)
            DO $$ 
            BEGIN 
                IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'gender_enum') THEN
                    CREATE TYPE gender_enum AS ENUM ('Male', 'Female', 'Other');
                END IF;
                
                IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'status_enum') THEN
                    CREATE TYPE status_enum AS ENUM ('Pending', 'Approved', 'Rejected', 'Completed');
                END IF;
            END $$;

            -- Create the mother_card_registration table
            CREATE TABLE mother_card_registration (
                id SERIAL PRIMARY KEY,
                mother_name VARCHAR(255) NOT NULL,
                husband_name VARCHAR(255) NOT NULL,
                last_name VARCHAR(255),
                date_of_birth DATE NOT NULL,
                aadhar_number VARCHAR(12) UNIQUE NOT NULL CHECK (aadhar_number ~ '^[0-9]{12}$'),
                phone_number VARCHAR(20) NOT NULL CHECK (phone_number ~ '^[0-9]{10,15}$'),
                email VARCHAR(255) UNIQUE NOT NULL CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
                address TEXT NOT NULL,
                anganwadi_name VARCHAR(255) NOT NULL,
                anganwadi_staff_name VARCHAR(255) NOT NULL,
                asha_staff_name VARCHAR(255),
                district VARCHAR(255) NOT NULL,
                taluk VARCHAR(255) NOT NULL,
                anganwadi_address TEXT NOT NULL,
                blood_group VARCHAR(5) CHECK (blood_group IN ('A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-')),
                height_cm INT CHECK (height_cm BETWEEN 50 AND 250),
                weight_kg DECIMAL(5,2) CHECK (weight_kg BETWEEN 30 AND 150),
                number_of_pregnancies INT DEFAULT NULL,
                last_menstrual_period DATE,
                expected_delivery_date DATE,
                first_trimester_checkup DATE,
                second_trimester_checkup DATE,
                third_trimester_checkup DATE,
                tetanus_vaccine BOOLEAN,
                iron_folic_acid_supplements BOOLEAN,
                other_vaccinations TEXT,
                delivery_date DATE,
                delivery_hospital VARCHAR(255),
                child_name VARCHAR(255),
                child_gender gender_enum,
                child_weight_kg DECIMAL(5,2) CHECK (child_weight_kg BETWEEN 0.5 AND 6.0),
                terms_agreed BOOLEAN,
                status status_enum,
                verified_by VARCHAR(255),
                verification_date TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                -- Foreign Key (Placed at the end)
                userid INT NOT NULL,
                CONSTRAINT fk_user FOREIGN KEY (userid) REFERENCES users(userid) ON DELETE CASCADE
            );
        """
        cursor.execute(create_table_query)

        conn.commit()
        cursor.close()
        conn.close()
        print("Mother Card table created successfully.")    
    except Exception as e:
        print(f"Error while creating table: {e}")



def create_nutrition_table():
    """
    Create the nutrition table in the database.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        create_table_query = """
        CREATE TABLE nutrition (
            nutrition_id SERIAL PRIMARY KEY,
            nutrition_name VARCHAR(255) NOT NULL,
            quantity VARCHAR(100) NOT NULL, -- Example: '5 kg', '10 packets'
            unit VARCHAR(50) NOT NULL, -- Example: kg, packets, liters
            nutritional_value TEXT NOT NULL, -- Details about calories, proteins, etc.
            distribution_date DATE NOT NULL, -- Date when it should be sent
            anganwadi_center VARCHAR(255) NOT NULL, -- Name of the center receiving the nutrition
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        """
        cursor.execute(create_table_query)

        conn.commit()
        cursor.close()
        conn.close()
        print("Nutrition table created successfully.")    
    except Exception as e:
        print(f"Error while creating table: {e}")


def create_anganwadi_request_table():
    """
    Create the nutrition table in the database.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        create_table_query = """
        CREATE TABLE anganwadi_requests (
            request_id SERIAL PRIMARY KEY,
            staff_name VARCHAR(255) NOT NULL,
            center_name VARCHAR(255) NOT NULL, -- Anganwadi center making the request
            request_type VARCHAR(50) NOT NULL CHECK (request_type IN ('Vaccine', 'Nutrition')), 
            item_name VARCHAR(255) NOT NULL, -- Name of the requested vaccine or nutrition item
            quantity INT NOT NULL CHECK (quantity > 0), -- Requested quantity
            unit VARCHAR(50) NOT NULL, -- Example: kg, liters, doses, packets
            description TEXT NOT NULL, -- Additional details about the vaccine/nutrition
            request_status VARCHAR(50) DEFAULT 'Pending' CHECK (request_status IN ('Pending', 'Approved', 'Rejected')),
            request_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
            admin_response TEXT DEFAULT NULL, -- Admin's response or comments
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        cursor.execute(create_table_query)

        conn.commit()
        cursor.close()
        conn.close()
        print("Request For Vaccines & Nutritions table created successfully.")    
    except Exception as e:
        print(f"Error while creating table: {e}")




def create_staff_table():
    """
    Create the Staff table in the database.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        create_table_query = """
        CREATE EXTENSION IF NOT EXISTS pgcrypto;

        CREATE TABLE anganwadi_staff (
            staff_id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            role VARCHAR(50) NOT NULL CHECK (role IN ('Anganwadi', 'Worker', 'Helper', 'Health Assistant')),
            phone VARCHAR(15) UNIQUE NOT NULL,
            email VARCHAR(100) UNIQUE,
            assigned_center VARCHAR(150) NOT NULL,
            address TEXT,
            joining_date DATE NOT NULL DEFAULT CURRENT_DATE,
            status VARCHAR(20) NOT NULL DEFAULT 'Active' CHECK (status IN ('Active', 'Inactive', 'On Leave')),
            password VARCHAR(255) NOT NULL DEFAULT crypt('staff', gen_salt('bf'))
        );

        """
        cursor.execute(create_table_query)

        conn.commit()
        cursor.close()
        conn.close()
        print("Staff Table table created successfully. \nAdmin will add the Staff")    
    except Exception as e:
        print(f"Error while creating table: {e}")




def insert_sample_data():
    """
    Inserts at least 5 sample records into all tables.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Insert into users table
        users_data = [
            ('Madhu', 'madhu@example.com', hashlib.sha256("password1".encode()).hexdigest()),
            ('Anjali', 'anjali@example.com', hashlib.sha256("password2".encode()).hexdigest()),
            ('Khan', 'khan@example.com', hashlib.sha256("password3".encode()).hexdigest()),
            ('Anil', 'anil@example.com', hashlib.sha256("password4".encode()).hexdigest()),
            ('Sameer', 'sameer@example.com', hashlib.sha256("password5".encode()).hexdigest()),
        ]
        cursor.executemany("""
            INSERT INTO users (username, email, password) VALUES (%s, %s, %s)
        """, users_data)

        # Insert into vaccines table
        vaccines_data = [
            ('Polio', True, 100, 0, 5, '2024-01-01', '2026-01-01'),
            ('BCG', True, 50, 0, 2, '2023-06-01', '2025-06-01'),
            ('Hepatitis B', True, 70, 0, 1, '2023-12-01', '2025-12-01'),
            ('DTP', True, 80, 0, 5, '2024-02-01', '2026-02-01'),
            ('MMR', True, 60, 1, 10, '2023-09-01', '2025-09-01'),
        ]
        cursor.executemany("""
            INSERT INTO vaccines (vaccine_name, availability, quantity, min_age, max_age, manufactured_date, expiry_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, vaccines_data)

        # Insert into mother_card_request table
        mother_requests = [
            ('Anjali', '123456789012', 28, 'Dharwad', '9876543210', 'Not visited', 3),
            ('Madhu', '123456789013', 30, 'Hubli', '9876543211', 'Not visited', 3),
            ('Khan', '123456789014', 26, 'Bangalore', '9876543212', 'Not visited', 3),
            ('Anil', '123456789015', 32, 'Mysore', '9876543213', 'Not visited', 3),
            ('Sameer', '123456789016', 29, 'Belgaum', '9876543214', 'Not visited', 3),
        ]
        cursor.executemany("""
            INSERT INTO mother_card_request (full_name, aadhar_number, age, address, contact_number, status, update_attempts)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, mother_requests)

        # Insert into mother_card_registration table
        mother_card_data = [
            ('Anjali', 'Raj', 'Sharma', '1995-05-15', '123456789012', '9876543210', 'anjali@example.com', 'Dharwad', 'Anganwadi 1', 'Staff 1', 'Asha 1', 'Dharwad', 'Taluk 1', 'Address 1', 'A+', 160, 55.5, 1, '2024-08-15', '2024-01-10', '2024-03-10', '2024-06-10', True, True, 'None', NULL, NULL, NULL, NULL, 'Female', 2.8, True, 'Approved', 'Doctor 1', '2024-03-15'),
            ('Madhu', 'Kumar', 'Patil', '1993-02-20', '123456789013', '9876543211', 'madhu@example.com', 'Hubli', 'Anganwadi 2', 'Staff 2', 'Asha 2', 'Hubli', 'Taluk 2', 'Address 2', 'B+', 170, 65.0, 2, '2024-09-20', '2024-02-15', '2024-04-15', '2024-07-15', True, False, 'Tetanus', NULL, NULL, NULL, NULL, 'Male', 3.2, True, 'Pending', NULL, NULL),
        ]
        cursor.executemany("""
            INSERT INTO mother_card_registration (
                mother_name, husband_name, last_name, date_of_birth, aadhar_number, phone_number, email,
                address, anganwadi_name, anganwadi_staff_name, asha_staff_name, district, taluk, anganwadi_address,
                blood_group, height_cm, weight_kg, number_of_pregnancies, expected_delivery_date,
                first_trimester_checkup, second_trimester_checkup, third_trimester_checkup,
                tetanus_vaccine, iron_folic_acid_supplements, other_vaccinations,
                delivery_date, delivery_hospital, child_name, child_gender, child_weight_kg,
                terms_agreed, status, verified_by, verification_date
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, mother_card_data)

        conn.commit()
        cursor.close()
        conn.close()
        print("Sample data inserted successfully!")
    except Exception as e:
        print(f"Error inserting data: {e}")

def create_nutrition_history_table():
    """
    Create the nutrition_history table to maintain the history of nutrition records.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        create_table_query = """
        CREATE TABLE IF NOT EXISTS nutrition_history (
            history_id SERIAL PRIMARY KEY,
            nutrition_id INT NOT NULL, -- Reference to the original nutrition record
            nutrition_name VARCHAR(255) NOT NULL,
            quantity VARCHAR(100) NOT NULL,
            unit VARCHAR(50) NOT NULL,
            nutritional_value TEXT NOT NULL,
            distribution_date DATE NOT NULL,
            anganwadi_center VARCHAR(255) NOT NULL,
            action VARCHAR(50) NOT NULL CHECK (action IN ('INSERT', 'UPDATE', 'DELETE')), -- Action type
            action_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- When the action occurred
        );
        """
        cursor.execute(create_table_query)
        conn.commit()
        cursor.close()
        conn.close()
        print("Nutrition history table created successfully.")
    except Exception as e:
        print(f"Error while creating nutrition history table: {e}")


def create_vaccine_history_table():
    """
    Create the vaccine_history table to maintain the history of vaccine records.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        create_table_query = """
        CREATE TABLE IF NOT EXISTS vaccine_history (
            history_id SERIAL PRIMARY KEY,
            vaccine_id INT NOT NULL, -- Reference to the original vaccine record
            vaccine_name VARCHAR(100) NOT NULL,
            availability BOOLEAN NOT NULL,
            quantity INT NOT NULL,
            min_age INT NOT NULL,
            max_age INT,
            manufactured_date DATE NOT NULL,
            expiry_date DATE,
            action VARCHAR(50) NOT NULL CHECK (action IN ('INSERT', 'UPDATE', 'DELETE')), -- Action type
            action_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- When the action occurred
        );
        """
        cursor.execute(create_table_query)
        conn.commit()
        cursor.close()
        conn.close()
        print("Vaccine history table created successfully.")
    except Exception as e:
        print(f"Error while creating vaccine history table: {e}")


def create_distribution_history_table():
    """
    Create the distribution_history table to maintain the history of both vaccines and nutrition records.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        create_table_query = """
        CREATE TABLE IF NOT EXISTS distribution_history (
            history_id SERIAL PRIMARY KEY,
            mother_id INT NOT NULL,
            staff_id INT NOT NULL,
            type VARCHAR(50) NOT NULL CHECK (type IN ('Vaccine', 'Nutrition')),
            item_name VARCHAR(255) NOT NULL,
            quantity VARCHAR(100) NOT NULL,
            unit VARCHAR(50) NOT NULL,
            distribution_date DATE NOT NULL,
            status VARCHAR(50) NOT NULL CHECK (status IN ('Upcoming', 'Distributed', 'Today','Missed')),
            action_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT fk_mother FOREIGN KEY (mother_id) REFERENCES mother_card_registration(id) ON DELETE CASCADE
        );
        """

        cursor.execute(create_table_query)

        # Now safely run the update
        update_status_query = """
        UPDATE distribution_history
        SET status = 'Today'
        WHERE distribution_date = CURRENT_DATE AND status = 'Upcoming';
        """
        cursor.execute(update_status_query)

        conn.commit()
        cursor.close()
        conn.close()
        print("Distribution history table created successfully.")
    except Exception as e:
        print(f"Error while creating distribution history table: {e}")

def create_vaccine_schedule_table():
    """
    Create the vaccine_schedule table to maintain the schedule of vaccines for pregnant women.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        create_table_query = """
        CREATE TABLE IF NOT EXISTS vaccine_schedule (
            schedule_id SERIAL PRIMARY KEY,
            mother_id INT NOT NULL, -- Reference to the mother_card_registration table
            vaccine_name VARCHAR(100) NOT NULL, -- Name of the vaccine
            scheduled_date DATE NOT NULL, -- Date when the vaccine is scheduled
            status VARCHAR(50) DEFAULT 'Pending' CHECK (status IN ('Pending', 'Completed', 'Missed')), -- Status of the vaccine
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT fk_mother FOREIGN KEY (mother_id) REFERENCES mother_card_registration(id) ON DELETE CASCADE,
            CONSTRAINT vaccine_name FOREIGN KEY (vaccine_name) REFERENCES vaccines(vaccine_name) ON DELETE CASCADE
        );
        """
        cursor.execute(create_table_query)
        conn.commit()
        cursor.close()
        conn.close()
        print("Vaccine schedule table created successfully.")
    except Exception as e:
        print(f"Error while creating vaccine schedule table: {e}")

def create_mother_checkup_history_table():
    """
    Create the mother_checkup_history table to track the checkup history and health details of mothers.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        create_table_query = """
        CREATE TABLE IF NOT EXISTS mother_checkup_history (
            checkup_id SERIAL PRIMARY KEY,
            mother_id INT NOT NULL, -- Reference to the mother_card_registration table
            checkup_type VARCHAR(50) NOT NULL CHECK (checkup_type IN ('First Trimester', 'Second Trimester', 'Third Trimester', 'Postnatal')),
            checkup_date DATE NOT NULL,
            blood_pressure VARCHAR(20), -- Example: '120/80'
            weight_kg DECIMAL(5,2) CHECK (weight_kg BETWEEN 30 AND 150),
            hemoglobin_level DECIMAL(4,2), -- Example: 12.5
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT fk_mother FOREIGN KEY (mother_id) REFERENCES mother_card_registration(id) ON DELETE CASCADE
        );
        """
        cursor.execute(create_table_query)
        conn.commit()
        cursor.close()
        conn.close()
        print("Mother checkup history table created successfully.")
    except Exception as e:
        print(f"Error while creating mother checkup history table: {e}")        
##################sending sueduled mail#############33

def send_email(to_email, subject, body):
    """
    Sends an email to the specified recipient.
    """
    try:
        logging.debug(f"Preparing to send email to {to_email} with subject '{subject}'.")
        msg = MIMEMultipart()
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = to_email
        msg["Subject"] = subject

        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, to_email, msg.as_string())

        logging.info(f"Email sent successfully to {to_email}.")
    except Exception as e:
        logging.error(f"Error sending email to {to_email}: {e}")

def get_upcoming_reminders():
    """
    Fetch reminders for users whose trimester checkup dates are within the next 7 days.
    """
    try:
        logging.debug("Fetching upcoming reminders from the database.")
        conn = get_db_connection()
        cursor = conn.cursor()

        # Calculate the date range for the next 7 days
        today = datetime.now().date()
        next_week = today + timedelta(days=7)

        # Query to fetch reminders for upcoming trimester checkups
        query = """
        SELECT mother_name, email, first_trimester_checkup, second_trimester_checkup, third_trimester_checkup
        FROM mother_card_registration
        WHERE 
            (first_trimester_checkup BETWEEN %s AND %s) OR
            (second_trimester_checkup BETWEEN %s AND %s) OR
            (third_trimester_checkup BETWEEN %s AND %s)
        """
        cursor.execute(query, (today, next_week, today, next_week, today, next_week))
        reminders = cursor.fetchall()

        cursor.close()
        conn.close()

        logging.debug(f"Found {len(reminders)} upcoming reminders.")
        return reminders
    except Exception as e:
        logging.error(f"Error fetching reminders: {e}")
        return []
    
# Function to Send Trimester Reminders
def send_trimester_reminders():
    """
    Send reminder emails for upcoming trimester checkups.
    """
    logging.info("Executing scheduled job: send_trimester_reminders.")
    reminders = get_upcoming_reminders()

    if not reminders:
        logging.info("No upcoming trimester reminders found.")
        return

    for reminder in reminders:
        name = reminder[0]  # Assuming the first column is 'mother_name'
        email = reminder[1]  # Assuming the second column is 'email'
        trimester = "Trimester"  # Replace with appropriate logic if needed
        date = reminder[2]  # Assuming the third column is the date

        subject = f"Reminder: {trimester} Trimester Checkup"
        body = f"Dear {name},\n\nThis is a reminder for your {trimester.lower()} trimester checkup scheduled on {date}.\n\nBest regards,\nYour Healthcare Team"
        send_email(email, subject, body)


# Function to Start the Scheduler
def start_scheduler():
    """
    Start the APScheduler to run the email-sending job daily.
    """
    try:
        logging.debug("Starting the scheduler.")
        scheduler = BackgroundScheduler()
        scheduler.add_job(send_trimester_reminders, "interval", days=1)  # Run daily
        scheduler.start()
        logging.info("Scheduler started successfully.")
    except Exception as e:
        logging.error(f"Error starting the scheduler: {e}")



def send_vaccination_reminders():
    """
    Send vaccination reminder emails 3 days before the scheduled vaccination date based on the last menstrual period.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Define the vaccination schedule
        today = datetime.now().date()
        reminder_date = today + timedelta(days=3)  # Reminder 3 days before the vaccination date
        cursor.execute("""
            SELECT mother_name, email, anganwadi_name, last_menstrual_period
            FROM mother_card_registration
            WHERE last_menstrual_period IS NOT NULL
        """)
        mothers = cursor.fetchall()

        for mother in mothers:
            mother_name = mother[0]
            email = mother[1]
            anganwadi_name = mother[2]
            last_menstrual_period = mother[3]

            # Calculate vaccination dates
            tt1_date = last_menstrual_period + timedelta(weeks=12)
            tt2_date = last_menstrual_period + timedelta(weeks=16)
            influenza_date = last_menstrual_period + timedelta(weeks=20)

            # Check if any vaccination reminder is due
            if reminder_date == tt1_date:
                send_email(
                    email,
                    "Vaccination Reminder: TT1",
                    f"""
                    Dear {mother_name},

                    This is a reminder that your TT1 vaccination is scheduled in 3 days. 
                    Please visit your Anganwadi center ({anganwadi_name}) to get vaccinated.

                    Best regards,
                    Care One Team
                    """
                )
            elif reminder_date == tt2_date:
                send_email(
                    email,
                    "Vaccination Reminder: TT2",
                    f"""
                    Dear {mother_name},

                    This is a reminder that your TT2 vaccination is scheduled in 3 days. 
                    Please visit your Anganwadi center ({anganwadi_name}) to get vaccinated.

                    Best regards,
                    Care One Team
                    """
                )
            elif reminder_date == influenza_date:
                send_email(
                    email,
                    "Vaccination Reminder: Influenza",
                    f"""
                    Dear {mother_name},

                    This is a reminder that your Influenza vaccination is scheduled in 3 days. 
                    Please visit your Anganwadi center ({anganwadi_name}) to get vaccinated.

                    Best regards,
                    Care One Team
                    """
                )

        print("Vaccination reminders sent successfully.")

    except Exception as e:
        print(f"Error while sending vaccination reminders: {e}")

    finally:
        cursor.close()
        conn.close()

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(send_vaccination_reminders, "cron", hour=8)  # Run daily at 8 AM
    scheduler.start()
    print("Scheduler started.")