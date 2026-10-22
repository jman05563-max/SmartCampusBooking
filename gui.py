from database import create_tables, insert_campuses, insert_resources
from authentication import ensure_demo_accounts

from booking_manager import (
    create_booking,
    get_user_bookings,
    cancel_booking,
    add_resource
)

from reports import (
    get_campus_booking_totals,
    get_most_used_resources,
    get_average_booking_duration
)

import tkinter as tk
from tkinter import ttk, messagebox

from authentication import register_user, login_user


class SmartCampusApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Campus Resource Booking System")
        self.root.geometry("600x450")
        self.root.resizable(False, False)

        self.current_user = None

        self.show_login()

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_login(self):
        self.clear_window()

        tk.Label(
            self.root,
            text="Smart Campus Resource Booking System",
            font=("Arial", 16, "bold")
        ).pack(pady=20)

        tk.Label(self.root, text="Username").pack()
        self.username_entry = tk.Entry(self.root, width=35)
        self.username_entry.pack(pady=5)

        tk.Label(self.root, text="Password").pack()
        self.password_entry = tk.Entry(
            self.root, width=35, show="*"
        )
        self.password_entry.pack(pady=5)

        tk.Button(
            self.root,
            text="Login",
            width=20,
            command=self.login
        ).pack(pady=15)

        tk.Button(
            self.root,
            text="Register Lecturer Account",
            command=self.show_register
        ).pack()

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        user = login_user(username, password)

        if user:
            self.current_user = user
            self.show_dashboard()
        else:
            messagebox.showerror(
                "Login Failed",
                "Incorrect username or password."
            )

    def show_register(self):
        self.clear_window()

        tk.Label(
            self.root,
            text="Register Lecturer Account",
            font=("Arial", 16, "bold")
        ).pack(pady=15)

        tk.Label(self.root, text="Full Name").pack()
        self.name_entry = tk.Entry(self.root, width=35)
        self.name_entry.pack(pady=4)

        tk.Label(self.root, text="Username").pack()
        self.reg_username_entry = tk.Entry(self.root, width=35)
        self.reg_username_entry.pack(pady=4)

        tk.Label(self.root, text="Password").pack()
        self.reg_password_entry = tk.Entry(
            self.root, width=35, show="*"
        )
        self.reg_password_entry.pack(pady=4)

        tk.Button(
            self.root,
            text="Create Account",
            command=self.register
        ).pack(pady=12)

        tk.Button(
            self.root,
            text="Back to Login",
            command=self.show_login
        ).pack()

    def register(self):
        name = self.name_entry.get()
        username = self.reg_username_entry.get()
        password = self.reg_password_entry.get()

        success, message = register_user(
            name, username, password, "Lecturer"
        )

        if success:
            messagebox.showinfo("Registration", message)
            self.show_login()
        else:
            messagebox.showerror("Registration", message)

    def show_dashboard(self):
        self.clear_window()

        tk.Label(
            self.root,
            text="Smart Campus Dashboard",
            font=("Arial", 18, "bold")
        ).pack(pady=20)

        if self.current_user["role"] == "Campus Administrator":
            tk.Button(
                self.root,
                text="Manage Resources",
                width=20,
                command=self.show_manage_resources
            ).pack(pady=5)

        tk.Label(
            self.root,
            text=f"Welcome, {self.current_user['full_name']}"
        ).pack(pady=5)

        tk.Label(
            self.root,
            text=f"Role: {self.current_user['role']}"
        ).pack(pady=5)

        tk.Label(
            self.root,
            text="Select Campus:"
        ).pack(pady=10)

        if self.current_user["role"] == "System Operator":
            tk.Button(
                self.root,
                text="View Campus Reports",
                width=20,
                command=self.show_reports
            ).pack(pady=5)

        self.campus_var = tk.StringVar()

        campus_dropdown = ttk.Combobox(
            self.root,
            textvariable=self.campus_var,
            values=[
                "Richfield Pretoria Campus",
                "Richfield NewTown Campus",
                "Richfield Centurion Campus"
            ],
            state="readonly",
            width=35
        )
        campus_dropdown.pack(pady=5)
        campus_dropdown.current(0)

        tk.Button(
            self.root,
            text="View Resources",
            width=20,
            command=self.view_resources
        ).pack(pady=10)

        if self.current_user["role"] == "Lecturer":
            tk.Button(
                self.root,
                text="Book a Resource",
                width=20,
                command=self.show_booking_form
            ).pack(pady=5)

            if self.current_user["role"] == "Lecturer":
                tk.Button(
                    self.root,
                    text="My Bookings",
                    width=20,
                    command=self.show_my_bookings
                ).pack(pady=5)

        tk.Label(
            self.root,
            textvariable=self.campus_var
        ).pack(pady=5)

        tk.Button(
            self.root,
            text="Logout",
            width=20,
            command=self.show_login
        ).pack(pady=20)

    def view_resources(self):
        from database import connect_db
        from tkinter import simpledialog

        campus_name = self.campus_var.get()

        connection = connect_db()
        cursor = connection.cursor()

        cursor.execute(
            "SELECT id FROM campuses WHERE name = ?",
            (campus_name,)
        )
        campus = cursor.fetchone()

        if campus is None:
            connection.close()
            messagebox.showerror(
                "Error",
                "The selected campus was not found."
            )
            return

        cursor.execute("""
            SELECT resource_name, resource_type
            FROM resources
            WHERE campus_id = ?
        """, (campus[0],))

        resources = cursor.fetchall()
        connection.close()

        self.clear_window()

        tk.Label(
            self.root,
            text=f"Resources at {campus_name}",
            font=("Arial", 15, "bold")
        ).pack(pady=20)

        if resources:
            for name, resource_type in resources:
                tk.Label(
                    self.root,
                    text=f"{name} — {resource_type}"
                ).pack(pady=5)
        else:
            tk.Label(
                self.root,
                text="No resources found for this campus."
            ).pack(pady=10)

        tk.Button(
            self.root,
            text="Back to Dashboard",
            command=self.show_dashboard
        ).pack(pady=20)


    def show_booking_form(self):
        from tkinter import simpledialog

        self.clear_window()

        tk.Label(
            self.root,
            text="Book a Campus Resource",
            font=("Arial", 16, "bold")
        ).pack(pady=15)

        tk.Label(self.root, text="Campus").pack()
        self.booking_campus = ttk.Combobox(
            self.root,
            values=[
                "Richfield Pretoria Campus",
                "Richfield NewTown Campus",
                "Richfield Centurion Campus"
            ],
            state="readonly",
            width=35
        )
        self.booking_campus.pack(pady=5)
        self.booking_campus.current(0)

        tk.Label(self.root, text="Resource").pack()
        self.booking_resource = ttk.Combobox(
            self.root,
            state="readonly",
            width=35
        )
        self.booking_resource.pack(pady=5)

        def load_resources(event=None):
            from database import connect_db

            campus_name = self.booking_campus.get()
            connection = connect_db()
            cursor = connection.cursor()

            cursor.execute(
                "SELECT id FROM campuses WHERE name = ?",
                (campus_name,)
            )
            campus = cursor.fetchone()

            if campus:
                cursor.execute("""
                    SELECT resource_name FROM resources
                    WHERE campus_id = ?
                """, (campus[0],))
                names = [row[0] for row in cursor.fetchall()]
            else:
                names = []

            connection.close()
            self.booking_resource["values"] = names

            if names:
                self.booking_resource.current(0)

        self.booking_campus.bind("<<ComboboxSelected>>", load_resources)
        load_resources()

        tk.Label(self.root, text="Booking Date (YYYY-MM-DD)").pack()
        self.booking_date = tk.Entry(self.root, width=38)
        self.booking_date.pack(pady=5)

        tk.Label(self.root, text="Start Time (HH:MM)").pack()
        self.booking_time = tk.Entry(self.root, width=38)
        self.booking_time.pack(pady=5)

        tk.Label(self.root, text="Duration (whole hours)").pack()
        self.booking_duration = tk.Entry(self.root, width=38)
        self.booking_duration.pack(pady=5)

        tk.Button(
            self.root,
            text="Confirm Booking",
            command=self.submit_booking
        ).pack(pady=12)

        tk.Button(
            self.root,
            text="Back to Dashboard",
            command=self.show_dashboard
        ).pack()

    def submit_booking(self):
        campus = self.booking_campus.get()
        resource = self.booking_resource.get()
        date = self.booking_date.get().strip()
        start_time = self.booking_time.get().strip()
        duration = self.booking_duration.get().strip()

        if not resource:
            messagebox.showerror("Booking", "Select a resource.")
            return

        success, message = create_booking(
            self.current_user["id"],
            campus,
            resource,
            date,
            start_time,
            duration
        )

        if success:
            messagebox.showinfo("Booking", message)
            self.show_dashboard()
        else:
            messagebox.showerror("Booking", message)


    def show_my_bookings(self):
        self.clear_window()

        tk.Label(
            self.root,
            text="My Booking History",
            font=("Arial", 16, "bold")
        ).pack(pady=15)

        bookings = get_user_bookings(self.current_user["id"])

        self.booking_list = tk.Listbox(
            self.root,
            width=85,
            height=12
        )
        self.booking_list.pack(padx=10, pady=10)

        for booking in bookings:
            booking_id, resource, campus, date, time, duration, status = booking

            self.booking_list.insert(
                tk.END,
                f"ID: {booking_id} | {resource} | {campus} | "
                f"{date} {time} | {duration} hour(s) | {status}"
            )

        if not bookings:
            self.booking_list.insert(tk.END, "You have no bookings yet.")

        tk.Button(
            self.root,
            text="Cancel Selected Booking",
            command=self.cancel_selected_booking
        ).pack(pady=5)

        tk.Button(
            self.root,
            text="Back to Dashboard",
            command=self.show_dashboard
        ).pack(pady=5)

    def cancel_selected_booking(self):
        selection = self.booking_list.curselection()

        if not selection:
            messagebox.showwarning(
                "Cancel Booking",
                "Please select a booking first."
            )
            return

        selected_text = self.booking_list.get(selection[0])

        try:
            booking_id = int(selected_text.split("|")[0].replace("ID:", "").strip())
        except (ValueError, IndexError):
            messagebox.showerror(
                "Cancel Booking",
                "Could not identify the selected booking."
            )
            return

        confirm = messagebox.askyesno(
            "Confirm Cancellation",
            "Are you sure you want to cancel this booking?"
        )

        if not confirm:
            return

        success, message = cancel_booking(
            booking_id,
            self.current_user["id"]
        )

        if success:
            messagebox.showinfo("Cancellation", message)
            self.show_my_bookings()
        else:
            messagebox.showerror("Cancellation", message)


    def show_manage_resources(self):
        self.clear_window()

        tk.Label(
            self.root,
            text="Manage Campus Resources",
            font=("Arial", 16, "bold")
        ).pack(pady=15)

        tk.Label(self.root, text="Campus:").pack()
        self.admin_campus_var = tk.StringVar(
            value="Richfield Pretoria Campus"
        )

        campuses = [
            "Richfield Pretoria Campus",
            "Richfield NewTown Campus",
            "Richfield Centurion Campus"
        ]

        ttk.Combobox(
            self.root,
            textvariable=self.admin_campus_var,
            values=campuses,
            state="readonly",
            width=35
        ).pack(pady=5)

        tk.Label(self.root, text="Resource Name:").pack()
        self.resource_name_entry = tk.Entry(self.root, width=38)
        self.resource_name_entry.pack(pady=5)

        tk.Label(self.root, text="Resource Type:").pack()
        self.resource_type_entry = tk.Entry(self.root, width=38)
        self.resource_type_entry.pack(pady=5)

        tk.Button(
            self.root,
            text="Add Resource",
            command=self.submit_resource
        ).pack(pady=8)

        tk.Button(
            self.root,
            text="View Resources",
            command=self.view_resources
        ).pack(pady=5)

        tk.Button(
            self.root,
            text="Back to Dashboard",
            command=self.show_dashboard
        ).pack(pady=5)

    def submit_resource(self):
        resource_name = self.resource_name_entry.get().strip()
        resource_type = self.resource_type_entry.get().strip()
        campus_name = self.admin_campus_var.get()

        success, message = add_resource(
            resource_name,
            resource_type,
            campus_name
        )

        if success:
            messagebox.showinfo("Resource Management", message)
            self.resource_name_entry.delete(0, tk.END)
            self.resource_type_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Resource Management", message)


    def show_reports(self):
        self.clear_window()

        tk.Label(
            self.root,
            text="System Operator Reports",
            font=("Arial", 16, "bold")
        ).pack(pady=10)

        report_box = tk.Text(
            self.root,
            width=85,
            height=22,
            wrap=tk.WORD
        )
        report_box.pack(padx=10, pady=10)

        report_box.insert(tk.END, "CAMPUS BOOKING TOTALS\n")
        report_box.insert(tk.END, "-" * 40 + "\n")

        totals = get_campus_booking_totals()

        for campus, total in totals:
            report_box.insert(
                tk.END, f"{campus}: {total} booking(s)\n"
            )

        report_box.insert(tk.END, "\nMOST-USED RESOURCES\n")
        report_box.insert(tk.END, "-" * 40 + "\n")

        resources = get_most_used_resources()

        for resource, campus, total in resources:
            report_box.insert(
                tk.END,
                f"{resource} | {campus} | {total} active booking(s)\n"
            )

        report_box.insert(tk.END, "\nAVERAGE BOOKING DURATION\n")
        report_box.insert(tk.END, "-" * 40 + "\n")

        averages = get_average_booking_duration()

        for campus, average in averages:
            if average is None:
                duration_text = "No active bookings"
            else:
                duration_text = f"{average:.2f} hour(s)"

            report_box.insert(
                tk.END, f"{campus}: {duration_text}\n"
            )

        report_box.config(state=tk.DISABLED)

        tk.Button(
            self.root,
            text="Back to Dashboard",
            command=self.show_dashboard
        ).pack(pady=5)


if __name__ == "__main__":
    create_tables()
    insert_campuses()
    insert_resources()
    ensure_demo_accounts()

    root = tk.Tk()
    app = SmartCampusApp(root)
    root.mainloop()


