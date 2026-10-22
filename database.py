import sqlite3


DATABASE_NAME = "campus_booking.db"


def connect_db():
    """Create a connection to the SQLite database."""
    return sqlite3.connect(DATABASE_NAME)


def create_tables():
    """Create all required database tables."""

    connection = connect_db()
    cursor = connection.cursor()

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    """)

    # Campuses table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS campuses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            max_duration INTEGER NOT NULL,
            opening_time TEXT NOT NULL,
            closing_time TEXT NOT NULL
        )
    """)

    # Resources table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS resources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            resource_name TEXT NOT NULL,
            resource_type TEXT NOT NULL,
            campus_id INTEGER NOT NULL,
            FOREIGN KEY (campus_id) REFERENCES campuses(id)
        )
    """)

    # Bookings table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            resource_id INTEGER NOT NULL,
            campus_id INTEGER NOT NULL,
            booking_date TEXT NOT NULL,
            start_time TEXT NOT NULL,
            duration INTEGER NOT NULL,
            status TEXT DEFAULT 'Active',
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (resource_id) REFERENCES resources(id),
            FOREIGN KEY (campus_id) REFERENCES campuses(id)
        )
    """)

    connection.commit()
    connection.close()

    print("Database tables created successfully.")


def insert_campuses():
    """Insert the three campuses if they do not already exist."""

    connection = connect_db()
    cursor = connection.cursor()

    campuses = [
        ("Richfield Pretoria Campus", 2, "08:00", "17:00"),
        ("Richfield NewTown Campus", 3, "07:00", "18:00"),
        ("Richfield Centurion Campus", 1, "09:00", "16:00")
    ]

    for campus in campuses:
        cursor.execute("""
            UPDATE campuses
            SET name = 'Richfield NewTown Campus'
            WHERE name = 'Richfield Johannesburg Campus'
        """)

        cursor.execute("""
            UPDATE campuses
            SET name = 'Richfield Centurion Campus'
            WHERE name = 'Richfield Cape Town Campus'
        """)

        connection.commit()
        cursor.execute("""
            INSERT OR IGNORE INTO campuses
            (name, max_duration, opening_time, closing_time)
            VALUES (?, ?, ?, ?)
        """, campus)

    connection.commit()
    connection.close()

    print("Three campuses added successfully.")



def insert_resources():
    """Add sample resources to each campus without duplicating them."""

    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("SELECT id, name FROM campuses")
    campuses = cursor.fetchall()

    resources = [
        ("Computer Laboratory 1", "Computer Lab"),
        ("Multimedia Projector 1", "Projector"),
        ("Seminar Room 1", "Seminar Room"),
        ("Presentation Equipment 1", "Presentation Equipment")
    ]

    for campus_id, campus_name in campuses:
        for resource_name, resource_type in resources:
            cursor.execute("""
                SELECT id FROM resources
                WHERE resource_name = ?
                AND campus_id = ?
            """, (resource_name, campus_id))

            if cursor.fetchone() is None:
                cursor.execute("""
                    INSERT INTO resources
                    (resource_name, resource_type, campus_id)
                    VALUES (?, ?, ?)
                """, (resource_name, resource_type, campus_id))

    connection.commit()
    connection.close()

    print("Resources added successfully.")


if __name__ == "__main__":
    create_tables()
    insert_campuses()
    insert_resources()
