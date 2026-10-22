
from datetime import datetime, timedelta

from database import connect_db
from booking_rules import get_booking_rule


def create_booking(
    user_id,
    campus_name,
    resource_name,
    booking_date,
    start_time,
    duration
):
    """Create a booking after validating campus rules and availability."""

    # Validate the date and time formats
    try:
        date_value = datetime.strptime(booking_date, "%Y-%m-%d").date()
        start_value = datetime.strptime(start_time, "%H:%M")
    except ValueError:
        return False, "Use date YYYY-MM-DD and time HH:MM."

    if date_value < datetime.today().date():
        return False, "You cannot book a resource for a past date."

    if start_value.strftime("%H:%M") != start_time:
        return False, "Enter time in HH:MM format."

    try:
        duration = int(duration)
    except (ValueError, TypeError):
        return False, "Duration must be a whole number of hours."

    if duration <= 0:
        return False, "Duration must be greater than zero."

    # Find the selected campus policy
    rule = get_booking_rule(campus_name)

    if rule is None:
        return False, "Unknown campus."

    if not rule.is_duration_valid(duration):
        return False, (
            f"This campus allows bookings for a maximum of "
            f"{rule.max_duration} hour(s)."
        )

    # Check operating hours, including the booking end time
    end_value = start_value + timedelta(hours=duration)

    if (
        start_value.strftime("%H:%M") < rule.opening_time
        or end_value.strftime("%H:%M") > rule.closing_time
        or end_value.date() != start_value.date()
    ):
        return False, (
            f"Bookings must finish within "
            f"{rule.opening_time}–{rule.closing_time}."
        )

    connection = connect_db()
    cursor = connection.cursor()

    try:
        cursor.execute(
            "SELECT id FROM campuses WHERE name = ?",
            (campus_name,)
        )
        campus = cursor.fetchone()

        if campus is None:
            return False, "Campus not found in the database."

        campus_id = campus[0]

        cursor.execute("""
            SELECT id FROM resources
            WHERE resource_name = ? AND campus_id = ?
        """, (resource_name, campus_id))

        resource = cursor.fetchone()

        if resource is None:
            return False, "Resource not found at this campus."

        resource_id = resource[0]

        # Check whether another active booking overlaps
        cursor.execute("""
            SELECT start_time, duration
            FROM bookings
            WHERE resource_id = ?
              AND booking_date = ?
              AND status = 'Active'
        """, (resource_id, booking_date))

        existing_bookings = cursor.fetchall()

        new_start = start_value
        new_end = end_value

        for existing_start, existing_duration in existing_bookings:
            old_start = datetime.strptime(existing_start, "%H:%M")
            old_end = old_start + timedelta(hours=existing_duration)

            if new_start < old_end and old_start < new_end:
                return False, "This resource is already booked for that time."

        # Save the booking
        cursor.execute("""
            INSERT INTO bookings
            (user_id, resource_id, campus_id, booking_date,
             start_time, duration, status)
            VALUES (?, ?, ?, ?, ?, ?, 'Active')
        """, (
            user_id,
            resource_id,
            campus_id,
            booking_date,
            start_time,
            duration
        ))

        connection.commit()
        return True, "Booking created successfully."

    except Exception as error:
        connection.rollback()
        return False, f"Booking failed: {error}"

    finally:
        connection.close()


def get_user_bookings(user_id):
    """Retrieve all bookings belonging to a user."""

    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT bookings.id,
               resources.resource_name,
               campuses.name,
               bookings.booking_date,
               bookings.start_time,
               bookings.duration,
               bookings.status
        FROM bookings
        JOIN resources ON bookings.resource_id = resources.id
        JOIN campuses ON bookings.campus_id = campuses.id
        WHERE bookings.user_id = ?
        ORDER BY bookings.booking_date, bookings.start_time
    """, (user_id,))

    bookings = cursor.fetchall()
    connection.close()

    return bookings


def cancel_booking(booking_id, user_id):
    """Cancel a future active booking belonging to the user."""

    from datetime import date

    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT booking_date, status
        FROM bookings
        WHERE id = ? AND user_id = ?
    """, (booking_id, user_id))

    booking = cursor.fetchone()

    if booking is None:
        connection.close()
        return False, "Booking not found."

    booking_date, status = booking

    if status != "Active":
        connection.close()
        return False, "This booking is not active."

    if date.fromisoformat(booking_date) < date.today():
        connection.close()
        return False, "Past bookings cannot be cancelled."

    cursor.execute("""
        UPDATE bookings
        SET status = 'Cancelled'
        WHERE id = ? AND user_id = ?
    """, (booking_id, user_id))

    connection.commit()
    connection.close()

    return True, "Booking cancelled successfully."


def add_resource(resource_name, resource_type, campus_name):
    from database import connect_db

    if not resource_name.strip() or not resource_type.strip():
        return False, "Resource name and type are required."

    connection = connect_db()
    cursor = connection.cursor()

    try:
        cursor.execute(
            "SELECT id FROM campuses WHERE name = ?",
            (campus_name,)
        )
        campus = cursor.fetchone()

        if campus is None:
            return False, "Campus not found."

        campus_id = campus[0]

        cursor.execute(
            """SELECT id FROM resources
               WHERE resource_name = ? AND campus_id = ?""",
            (resource_name.strip(), campus_id)
        )

        if cursor.fetchone():
            return False, "This resource already exists at this campus."

        cursor.execute(
            """INSERT INTO resources
               (resource_name, resource_type, campus_id)
               VALUES (?, ?, ?)""",
            (resource_name.strip(), resource_type.strip(), campus_id)
        )

        connection.commit()
        return True, "Resource added successfully."

    except Exception as error:
        return False, f"Could not add resource: {error}"

    finally:
        connection.close()
