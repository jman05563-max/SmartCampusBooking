
import sqlite3
import hashlib

from database import connect_db


def hash_password(password):
    """Hash a password before saving it."""
    return hashlib.sha256(password.encode()).hexdigest()


def register_user(full_name, username, password, role):
    """Register a new user in the database."""

    allowed_roles = ["Lecturer", "Campus Administrator", "System Operator"]

    if role not in allowed_roles:
        return False, "Invalid user role."

    if not full_name.strip() or not username.strip() or not password:
        return False, "All fields are required."

    connection = connect_db()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            INSERT INTO users (full_name, username, password, role)
            VALUES (?, ?, ?, ?)
        """, (
            full_name.strip(),
            username.strip(),
            hash_password(password),
            role
        ))

        connection.commit()
        return True, "Registration successful."

    except sqlite3.IntegrityError:
        return False, "That username already exists."

    finally:
        connection.close()


def login_user(username, password):
    """Verify login details and return the user's information."""

    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, full_name, username, role
        FROM users
        WHERE username = ? AND password = ?
    """, (username.strip(), hash_password(password)))

    user = cursor.fetchone()
    connection.close()

    if user:
        return {
            "id": user[0],
            "full_name": user[1],
            "username": user[2],
            "role": user[3]
        }

    return None


def ensure_demo_accounts():
    demo_accounts = [
        (
            "Campus Administrator",
            "admin1",
            "AdminPass123",
            "Campus Administrator"
        ),
        (
            "System Operator",
            "operator1",
            "OperatorPass123",
            "System Operator"
        )
    ]

    for full_name, username, password, role in demo_accounts:
        register_user(full_name, username, password, role)
