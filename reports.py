
from database import connect_db


def get_campus_booking_totals():
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT campuses.name, COUNT(bookings.id)
        FROM campuses
        LEFT JOIN bookings
            ON campuses.id = bookings.campus_id
        GROUP BY campuses.id, campuses.name
        ORDER BY campuses.name
    """)

    results = cursor.fetchall()
    connection.close()
    return results


def get_most_used_resources():
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT resources.resource_name,
               campuses.name,
               COUNT(bookings.id) AS total
        FROM resources
        JOIN campuses ON resources.campus_id = campuses.id
        LEFT JOIN bookings
            ON resources.id = bookings.resource_id
           AND bookings.status = 'Active'
        GROUP BY resources.id, resources.resource_name, campuses.name
        ORDER BY total DESC, resources.resource_name
    """)

    results = cursor.fetchall()
    connection.close()
    return results


def get_average_booking_duration():
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT campuses.name, AVG(bookings.duration)
        FROM campuses
        LEFT JOIN bookings
            ON campuses.id = bookings.campus_id
           AND bookings.status = 'Active'
        GROUP BY campuses.id, campuses.name
        ORDER BY campuses.name
    """)

    results = cursor.fetchall()
    connection.close()
    return results
