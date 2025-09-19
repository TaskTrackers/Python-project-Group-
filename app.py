import tkinter as tk
from tkinter import messagebox, ttk
import datetime
import threading
import time
from lecture_manager import add_lecture, get_all_lectures, update_lecture, delete_lecture, get_upcoming_lectures, mark_notification_sent

class UniLectureNotifierApp:
    def __init__(self, master):
        self.master = master
        master.title("UniLecture Notifier")
        master.geometry("800x600") # Set initial window size
        master.resizable(True, True) # Allow resizing

        # Configure styles for ttk widgets
        style = ttk.Style()
        style.theme_use('clam') # Use 'clam', 'alt', 'default', 'classic'
        style.configure('TFrame', background='#e0f7fa')
        style.configure('TLabel', background='#e0f7fa', font=('Inter', 10))
        style.configure('TButton', font=('Inter', 10, 'bold'), padding=8, background='#00796b', foreground='white')
        style.map('TButton', background=[('active', '#004d40')])
        style.configure('Treeview.Heading', font=('Inter', 10, 'bold'))
        style.configure('Treeview', font=('Inter', 10))

        # --- Main Frames ---
        self.input_frame = ttk.Frame(master, padding="15 15 15 15", relief="groove", borderwidth=2)
        self.input_frame.pack(pady=10, padx=10, fill="x", expand=False)

        self.list_frame = ttk.Frame(master, padding="15 15 15 15", relief="groove", borderwidth=2)
        self.list_frame.pack(pady=10, padx=10, fill="both", expand=True)

        # --- Input Frame Widgets ---
        ttk.Label(self.input_frame, text="Course Name:").grid(row=0, column=0, sticky="w", pady=5, padx=5)
        self.course_name_entry = ttk.Entry(self.input_frame, width=40)
        self.course_name_entry.grid(row=0, column=1, pady=5, padx=5)

        ttk.Label(self.input_frame, text="Topic:").grid(row=1, column=0, sticky="w", pady=5, padx=5)
        self.topic_entry = ttk.Entry(self.input_frame, width=40)
        self.topic_entry.grid(row=1, column=1, pady=5, padx=5)

        ttk.Label(self.input_frame, text="Date (YYYY-MM-DD):").grid(row=2, column=0, sticky="w", pady=5, padx=5)
        self.date_entry = ttk.Entry(self.input_frame, width=40)
        self.date_entry.grid(row=2, column=1, pady=5, padx=5)
        self.date_entry.insert(0, datetime.date.today().strftime('%Y-%m-%d')) # Pre-fill with today's date

        ttk.Label(self.input_frame, text="Time (HH:MM:SS):").grid(row=3, column=0, sticky="w", pady=5, padx=5)
        self.time_entry = ttk.Entry(self.input_frame, width=40)
        self.time_entry.grid(row=3, column=1, pady=5, padx=5)
        self.time_entry.insert(0, "00:00:00") # Pre-fill with default time

        # Buttons for CRUD operations
        self.add_button = ttk.Button(self.input_frame, text="Add Lecture", command=self.add_lecture)
        self.add_button.grid(row=4, column=0, pady=10, padx=5, sticky="ew")

        self.update_button = ttk.Button(self.input_frame, text="Update Lecture", command=self.update_lecture)
        self.update_button.grid(row=4, column=1, pady=10, padx=5, sticky="ew")

        self.delete_button = ttk.Button(self.input_frame, text="Delete Lecture", command=self.delete_lecture)
        self.delete_button.grid(row=5, column=0, pady=10, padx=5, sticky="ew")

        self.clear_button = ttk.Button(self.input_frame, text="Clear Fields", command=self.clear_fields)
        self.clear_button.grid(row=5, column=1, pady=10, padx=5, sticky="ew")

        # --- Lecture List Frame Widgets (Treeview) ---
        self.lecture_tree = ttk.Treeview(self.list_frame, columns=("ID", "Course", "Topic", "Date", "Time", "Notified"), show="headings")
        self.lecture_tree.heading("ID", text="ID")
        self.lecture_tree.heading("Course", text="Course Name")
        self.lecture_tree.heading("Topic", text="Topic")
        self.lecture_tree.heading("Date", text="Date")
        self.lecture_tree.heading("Time", text="Time")
        self.lecture_tree.heading("Notified", text="Notified")

        self.lecture_tree.column("ID", width=50, anchor="center")
        self.lecture_tree.column("Course", width=150)
        self.lecture_tree.column("Topic", width=150)
        self.lecture_tree.column("Date", width=100, anchor="center")
        self.lecture_tree.column("Time", width=80, anchor="center")
        self.lecture_tree.column("Notified", width=70, anchor="center")

        self.lecture_tree.pack(fill="both", expand=True)

        # Scrollbar for the Treeview
        scrollbar = ttk.Scrollbar(self.list_frame, orient="vertical", command=self.lecture_tree.yview)
        self.lecture_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.lecture_tree.pack(side="left", fill="both", expand=True)

        # Bind selection event to populate fields
        self.lecture_tree.bind("<<TreeviewSelect>>", self.load_selected_lecture)

        self.load_lectures() # Load existing lectures on startup

        # Start notification checker in a separate thread
        self.notification_thread = threading.Thread(target=self.check_for_notifications, daemon=True)
        self.notification_thread.start()

    def show_message(self, title, message):
        """Custom message box instead of alert()."""
        top = tk.Toplevel(self.master)
        top.title(title)
        top.geometry("300x100")
        top.transient(self.master) # Make it appear on top of the main window
        top.grab_set() # Disable interaction with the main window

        ttk.Label(top, text=message, padding=10).pack(expand=True)
        ttk.Button(top, text="OK", command=top.destroy).pack(pady=5)

    def validate_input(self, course_name, topic, date_str, time_str):
        """Validates the input fields."""
        if not course_name.strip():
            self.show_message("Input Error", "Course Name cannot be empty.")
            return False
        try:
            datetime.date.fromisoformat(date_str)
        except ValueError:
            self.show_message("Input Error", "Invalid Date format. Use YYYY-MM-DD.")
            return False
        try:
            datetime.time.fromisoformat(time_str)
        except ValueError:
            self.show_message("Input Error", "Invalid Time format. Use HH:MM:SS.")
            return False
        return True

    def add_lecture(self):
        """Handles adding a new lecture."""
        course_name = self.course_name_entry.get()
        topic = self.topic_entry.get()
        date_str = self.date_entry.get()
        time_str = self.time_entry.get()

        if not self.validate_input(course_name, topic, date_str, time_str):
            return

        try:
            lecture_date = datetime.date.fromisoformat(date_str)
            lecture_time = datetime.time.fromisoformat(time_str)

            if add_lecture(course_name, topic, lecture_date, lecture_time):
                self.show_message("Success", "Lecture added successfully!")
                self.clear_fields()
                self.load_lectures()
            else:
                self.show_message("Error", "Failed to add lecture.")
        except ValueError as e:
            self.show_message("Input Error", f"Date/Time parsing error: {e}")

    def update_lecture(self):
        """Handles updating an existing lecture."""
        selected_item = self.lecture_tree.focus()
        if not selected_item:
            self.show_message("Selection Error", "Please select a lecture to update.")
            return

        lecture_id = self.lecture_tree.item(selected_item, 'values')[0]
        course_name = self.course_name_entry.get()
        topic = self.topic_entry.get()
        date_str = self.date_entry.get()
        time_str = self.time_entry.get()

        if not self.validate_input(course_name, topic, date_str, time_str):
            return

        try:
            lecture_date = datetime.date.fromisoformat(date_str)
            lecture_time = datetime.time.fromisoformat(time_str)

            if update_lecture(lecture_id, course_name, topic, lecture_date, lecture_time):
                self.show_message("Success", f"Lecture ID {lecture_id} updated successfully!")
                self.clear_fields()
                self.load_lectures()
            else:
                self.show_message("Error", f"Failed to update lecture ID {lecture_id}.")
        except ValueError as e:
            self.show_message("Input Error", f"Date/Time parsing error: {e}")

    def delete_lecture(self):
        """Handles deleting a lecture."""
        selected_item = self.lecture_tree.focus()
        if not selected_item:
            self.show_message("Selection Error", "Please select a lecture to delete.")
            return

        lecture_id = self.lecture_tree.item(selected_item, 'values')[0]

        # Custom confirmation dialog
        if self.ask_confirmation("Confirm Deletion", f"Are you sure you want to delete lecture ID {lecture_id}?"):
            if delete_lecture(lecture_id):
                self.show_message("Success", f"Lecture ID {lecture_id} deleted successfully!")
                self.clear_fields()
                self.load_lectures()
            else:
                self.show_message("Error", f"Failed to delete lecture ID {lecture_id}.")

    def ask_confirmation(self, title, message):
        """Custom confirmation dialog."""
        result = [False] # Use a list to allow modification from nested function

        top = tk.Toplevel(self.master)
        top.title(title)
        top.geometry("350x120")
        top.transient(self.master)
        top.grab_set()

        ttk.Label(top, text=message, padding=10).pack(expand=True)

        button_frame = ttk.Frame(top)
        button_frame.pack(pady=10)

        def on_yes():
            result[0] = True
            top.destroy()

        def on_no():
            result[0] = False
            top.destroy()

        ttk.Button(button_frame, text="Yes", command=on_yes).pack(side="left", padx=10)
        ttk.Button(button_frame, text="No", command=on_no).pack(side="right", padx=10)

        self.master.wait_window(top) # Wait for the Toplevel window to close
        return result[0]

    def load_lectures(self):
        """Loads all lectures from the database into the Treeview."""
        for item in self.lecture_tree.get_children():
            self.lecture_tree.delete(item) # Clear existing items

        lectures = get_all_lectures()
        for lec in lectures:
            # Ensure date and time are formatted correctly for display
            lec_date_str = lec['lecture_date'].strftime('%Y-%m-%d') if isinstance(lec['lecture_date'], datetime.date) else str(lec['lecture_date'])
            lec_time_str = lec['lecture_time'].strftime('%H:%M:%S') if isinstance(lec['lecture_time'], datetime.time) else str(lec['lecture_time'])
            notified_status = "Yes" if lec['notification_sent'] else "No"
            self.lecture_tree.insert("", "end", values=(
                lec['id'], lec['course_name'], lec['topic'], lec_date_str, lec_time_str, notified_status
            ))

    def load_selected_lecture(self, event):
        """Loads the details of the selected lecture into the input fields."""
        selected_item = self.lecture_tree.focus()
        if selected_item:
            values = self.lecture_tree.item(selected_item, 'values')
            self.clear_fields() # Clear first to avoid issues
            self.course_name_entry.insert(0, values[1])
            self.topic_entry.insert(0, values[2])
            self.date_entry.insert(0, values[3])
            self.time_entry.insert(0, values[4])

    def clear_fields(self):
        """Clears all input fields."""
        self.course_name_entry.delete(0, tk.END)
        self.topic_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)
        self.time_entry.delete(0, tk.END)
        self.date_entry.insert(0, datetime.date.today().strftime('%Y-%m-%d'))
        self.time_entry.insert(0, "00:00:00")

    def check_for_notifications(self):
        """
        Periodically checks for upcoming lectures and triggers notifications.
        Runs in a separate thread.
        """
        while True:
            upcoming = get_upcoming_lectures(minutes_ahead=15) # Check for lectures in next 15 minutes
            for lec in upcoming:
                # Use master.after to safely update GUI from a different thread
                self.master.after(0, self.trigger_notification, lec)
                mark_notification_sent(lec['id']) # Mark as sent immediately after triggering

            time.sleep(60) # Check every 60 seconds (1 minute)

    def trigger_notification(self, lecture_data):
        """Displays a notification for an upcoming lecture."""
        course = lecture_data['course_name']
        topic = lecture_data['topic']
        time_str = lecture_data['lecture_time'].strftime('%H:%M')
        date_str = lecture_data['lecture_date'].strftime('%Y-%m-%d')

        notification_message = (
            f"Upcoming Lecture Alert!\n\n"
            f"Course: {course}\n"
            f"Topic: {topic}\n"
            f"Time: {time_str} on {date_str}"
        )
        self.show_message("Lecture Reminder", notification_message)
        self.load_lectures() # Refresh the list to show notification_sent status update

if __name__ == '__main__':
    root = tk.Tk()
    app = UniLectureNotifierApp(root)
    root.mainloop()
