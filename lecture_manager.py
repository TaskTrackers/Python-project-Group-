import datetime
from db_connector import create_connection, close_connection
from mysql.connector import Error

def add_lecture(course_name, topic, lecture_date, lecture_time):
    """Adds a new lecture record to the database."""
    conn = create_connection()
    if conn:
        cursor = conn.cursor()
        try:
            sql = "INSERT INTO lectures (course_name, topic, lecture_date, lecture_time) VALUES (%s, %s, %s, %s)"
            val = (course_name, topic, lecture_date, lecture_time)
            cursor.execute(sql, val)
            conn.commit()
            print(f"Lecture '{course_name}' on {lecture_date} at {lecture_time} added successfully.")
            return True
        except Error as e:
            print(f"Error adding lecture: {e}")
            return False
        finally:
            cursor.close()
            close_connection(conn)
    return False

def get_all_lectures():
    """Retrieves all lecture records from the database."""
    conn = create_connection()
    lectures = []
    if conn:
        cursor = conn.cursor(dictionary=True) # Returns rows as dictionaries
        try:
            sql = "SELECT id, course_name, topic, lecture_date, lecture_time, notification_sent FROM lectures ORDER BY lecture_date, lecture_time"
            cursor.execute(sql)
            lectures = cursor.fetchall()
            print("All lectures retrieved successfully.")
        except Error as e:
            print(f"Error retrieving lectures: {e}")
        finally:
            cursor.close()
            close_connection(conn)
    return lectures

def update_lecture(lecture_id, course_name, topic, lecture_date, lecture_time):
    """Updates an existing lecture record in the database."""
    conn = create_connection()
    if conn:
        cursor = conn.cursor()
        try:
            sql = """UPDATE lectures SET course_name = %s, topic = %s, lecture_date = %s, lecture_time = %s
                     WHERE id = %s"""
            val = (course_name, topic, lecture_date, lecture_time, lecture_id)
            cursor.execute(sql, val)
            conn.commit()
            if cursor.rowcount > 0:
                print(f"Lecture with ID {lecture_id} updated successfully.")
                return True
            else:
                print(f"No lecture found with ID {lecture_id} to update.")
                return False
        except Error as e:
            print(f"Error updating lecture: {e}")
            return False
        finally:
            cursor.close()
            close_connection(conn)
    return False

def delete_lecture(lecture_id):
    """Deletes a lecture record from the database."""
    conn = create_connection()
    if conn:
        cursor = conn.cursor()
        try:
            sql = "DELETE FROM lectures WHERE id = %s"
            val = (lecture_id,)
            cursor.execute(sql, val)
            conn.commit()
            if cursor.rowcount > 0:
                print(f"Lecture with ID {lecture_id} deleted successfully.")
                return True
            else:
                print(f"No lecture found with ID {lecture_id} to delete.")
                return False
        except Error as e:
            print(f"Error deleting lecture: {e}")
            return False
        finally:
            cursor.close()
            close_connection(conn)
    return False

def mark_notification_sent(lecture_id):
    """Marks a lecture's notification_sent status as True."""
    conn = create_connection()
    if conn:
        cursor = conn.cursor()
        try:
            sql = "UPDATE lectures SET notification_sent = TRUE WHERE id = %s"
            val = (lecture_id,)
            cursor.execute(sql, val)
            conn.commit()
            if cursor.rowcount > 0:
                print(f"Notification sent for lecture ID {lecture_id}.")
                return True
            else:
                print(f"Could not mark notification sent for lecture ID {lecture_id}.")
                return False
        except Error as e:
            print(f"Error marking notification sent: {e}")
            return False
        finally:
            cursor.close()
            close_connection(conn)
    return False

def get_upcoming_lectures(minutes_ahead=15):
    """
    Retrieves lectures that are scheduled to start within the next 'minutes_ahead' minutes,
    and for which a notification has not yet been sent.
    """
    conn = create_connection()
    upcoming_lectures = []
    if conn:
        cursor = conn.cursor(dictionary=True)
        try:
            now = datetime.datetime.now()
            # Calculate the time window for upcoming lectures
            # We need to consider both date and time for comparison
            # SQL query will check if lecture_date is today and lecture_time is within the window
            sql = """
                SELECT id, course_name, topic, lecture_date, lecture_time
                FROM lectures
                WHERE lecture_date = CURDATE()
                AND lecture_time BETWEEN CURTIME() AND ADDTIME(CURTIME(), SEC_TO_TIME(%s * 60))
                AND notification_sent = FALSE
                ORDER BY lecture_time ASC
            """
            cursor.execute(sql, (minutes_ahead,))
            upcoming_lectures = cursor.fetchall()
        except Error as e:
            print(f"Error retrieving upcoming lectures: {e}")
        finally:
            cursor.close()
            close_connection(conn)
    return upcoming_lectures

if __name__ == '__main__':
    # --- Example Usage of CRUD operations ---
    # Add a lecture
    add_lecture("Physics I", "Newton's Laws", datetime.date(2025, 7, 26), datetime.time(9, 0, 0))
    add_lecture("Calculus II", "Integration Techniques", datetime.date(2025, 7, 27), datetime.time(14, 30, 0))

    # Get all lectures
    print("\n--- All Lectures ---")
    all_lectures = get_all_lectures()
    for lecture in all_lectures:
        print(lecture)

    # Update a lecture (assuming ID 1 exists)
    if all_lectures:
        first_lecture_id = all_lectures[0]['id']
        update_lecture(first_lecture_id, "Physics I (Revised)", "Kinematics", datetime.date(2025, 7, 26), datetime.time(9, 15, 0))

    # Get all lectures again to see the update
    print("\n--- Lectures After Update ---")
    all_lectures = get_all_lectures()
    for lecture in all_lectures:
        print(lecture)

    # Delete a lecture (assuming ID 2 exists)
    if len(all_lectures) > 1:
        second_lecture_id = all_lectures[1]['id']
        delete_lecture(second_lecture_id)

    # Get all lectures again to see the deletion
    print("\n--- Lectures After Deletion ---")
    all_lectures = get_all_lectures()
    for lecture in all_lectures:
        print(lecture)

    # Test upcoming lectures (adjust date/time for current testing)
    print("\n--- Upcoming Lectures (next 15 mins) ---")
    # For testing, you might want to manually insert a lecture that is very soon
    # add_lecture("Test Lecture", "Test Topic", datetime.date.today(), datetime.time(datetime.datetime.now().hour, datetime.datetime.now().minute + 1, 0))
    upcoming = get_upcoming_lectures(minutes_ahead=30) # Check for lectures in next 30 minutes
    if upcoming:
        for lec in upcoming:
            print(f"Upcoming: {lec['course_name']} at {lec['lecture_time']}")
            mark_notification_sent(lec['id'])
    else:
        print("No upcoming lectures.")
