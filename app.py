import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from datetime import date, datetime


DB_CONFIG = {
    "host": "localhost",
    "user": "root", 
    "password": "1904", 
    "database": "gym_management"
}
# ======================================================================

class GymApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gym Management System")
        self.root.geometry("1200x700")

        # --- Style Configuration ---
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TNotebook.Tab', padding=[10, 5], font=('Arial', 11, 'bold'))
        self.style.configure('TButton', padding=5, font=('Arial', 10))
        self.style.configure('Accent.TButton', padding=5, font=('Arial', 10, 'bold'), background='#0078d4', foreground='white')
        self.style.map('Accent.TButton', background=[('active', '#005a9e')])
        self.style.configure('Treeview.Heading', font=('Arial', 10, 'bold'))
        self.style.configure('Success.TLabel', foreground='green', font=('Arial', 10, 'italic'))
        self.style.configure('Error.TLabel', foreground='red', font=('Arial', 10, 'italic'))

        # --- Main Notebook (Tabbed Interface) ---
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(pady=10, padx=10, expand=True, fill='both')

        # --- Create Tabs ---
        self.tab_checkin = ttk.Frame(self.notebook, padding="10")
        self.tab_members = ttk.Frame(self.notebook, padding="10")
        self.tab_payments = ttk.Frame(self.notebook, padding="10")
        self.tab_trainers = ttk.Frame(self.notebook, padding="10")
        self.tab_plans = ttk.Frame(self.notebook, padding="10")
        self.tab_admin = ttk.Frame(self.notebook, padding="10")

        self.notebook.add(self.tab_checkin, text='Check-in / Out')
        self.notebook.add(self.tab_members, text='Members')
        self.notebook.add(self.tab_payments, text='Payments')
        self.notebook.add(self.tab_trainers, text='Trainers')
        self.notebook.add(self.tab_plans, text='Workout Plans')
        self.notebook.add(self.tab_admin, text='Admin')

        # --- Populate Tabs ---
        self.setup_checkin_tab()
        self.setup_members_tab()
        self.setup_payments_tab()
        self.setup_trainers_tab()
        self.setup_plans_tab()
        self.setup_admin_tab()

        # --- Data Maps for Comboboxes ---
        self.member_map = {}
        self.trainer_map = {}
        self.exercise_map = {}

        # --- Initial Data Load ---
        self.load_members_data()
        self.load_payments_data()
        self.load_trainers_data()
        self.load_attendance_data()
        self.load_workout_plans()
        self.load_member_and_trainer_combos()
        self.load_all_exercises_map()

    def db_connect(self):
        """Establishes a connection to the database."""
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            return conn
        except mysql.connector.Error as err:
            messagebox.showerror("Database Connection Error", f"Failed to connect to MySQL:\n{err}\n\nPlease check your credentials in DB_CONFIG.")
            return None

    # ==================================================================
    # TAB 1: CHECK-IN / OUT
    # ==================================================================
    def setup_checkin_tab(self):
        main_frame = ttk.Frame(self.tab_checkin)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # --- Check-in/Out Frame ---
        checkin_frame = ttk.LabelFrame(main_frame, text="Member Actions", padding=15)
        checkin_frame.pack(fill='x', pady=10)

        ttk.Label(checkin_frame, text="Member ID:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.checkin_mem_id_entry = ttk.Entry(checkin_frame, width=30)
        self.checkin_mem_id_entry.grid(row=0, column=1, padx=5, pady=5, sticky='ew')

        checkin_btn = ttk.Button(checkin_frame, text="Check-in", command=self.handle_checkin, style='Accent.TButton')
        checkin_btn.grid(row=0, column=2, padx=10, pady=5)

        checkout_btn = ttk.Button(checkin_frame, text="Check-out", command=self.handle_checkout)
        checkout_btn.grid(row=0, column=3, padx=5, pady=5)

        checkin_frame.grid_columnconfigure(1, weight=1)

        self.checkin_status_label = ttk.Label(checkin_frame, text="")
        self.checkin_status_label.grid(row=1, column=0, columnspan=4, pady=5)

        # --- Currently In Frame ---
        attendance_frame = ttk.LabelFrame(main_frame, text="Members Currently Checked In", padding=15)
        attendance_frame.pack(fill='both', expand=True, pady=10)

        self.attendance_tree = self.create_treeview(attendance_frame, 
            columns=('Mem_ID', 'Name', 'Check_In_Time'),
            headings={'Mem_ID': 'Member ID', 'Name': 'Name', 'Check_In_Time': 'Check-in Time'}
        )
        ttk.Button(main_frame, text="Refresh List", command=self.load_attendance_data).pack(pady=5)

    def handle_checkin(self):
        mem_id = self.checkin_mem_id_entry.get()
        if not mem_id:
            messagebox.showwarning("Input Error", "Please enter a Member ID.")
            return

        conn = self.db_connect()
        if not conn:
            return
        
        cursor = conn.cursor()
        try:
            query = "INSERT INTO Attendance (Mem_ID, check_in) VALUES (%s, %s)"
            cursor.execute(query, (mem_id, datetime.now()))
            conn.commit()

            self.checkin_status_label.config(text=f"Member {mem_id} checked in successfully.", style='Success.TLabel')
            self.load_attendance_data() # Refresh "currently in" list

        except mysql.connector.Error as err:
            conn.rollback()
            # THIS IS THE TRIGGER DEMONSTRATION
            if err.sqlstate == '45000':
                messagebox.showerror("Check-in Failed", "Check-in failed: Membership is expired. Please make a payment.")
                self.checkin_status_label.config(text="Check-in failed: Membership expired.", style='Error.TLabel')
            else:
                messagebox.showerror("Database Error", f"Failed to check in:\n{err}")
                self.checkin_status_label.config(text="An error occurred.", style='Error.TLabel')
        finally:
            cursor.close()
            conn.close()

    def handle_checkout(self):
        mem_id = self.checkin_mem_id_entry.get()
        if not mem_id:
            messagebox.showwarning("Input Error", "Please enter a Member ID.")
            return

        conn = self.db_connect()
        if not conn:
            return
        
        cursor = conn.cursor()
        try:
            # Find the latest open check-in for this member
            query = """
                UPDATE Attendance 
                SET check_out = %s 
                WHERE Mem_ID = %s AND check_out IS NULL 
                ORDER BY check_in DESC 
                LIMIT 1
            """
            cursor.execute(query, (datetime.now(), mem_id))
            
            if cursor.rowcount == 0:
                messagebox.showinfo("Check-out Info", f"No active check-in found for Member {mem_id} to check out.")
                self.checkin_status_label.config(text=f"No active check-in found for {mem_id}.", style='Error.TLabel')
            else:
                conn.commit()
                self.checkin_status_label.config(text=f"Member {mem_id} checked out successfully.", style='Success.TLabel')
                self.load_attendance_data() # Refresh "currently in" list
        
        except mysql.connector.Error as err:
            conn.rollback()
            messagebox.showerror("Database Error", f"Failed to check out:\n{err}")
        finally:
            cursor.close()
            conn.close()

    def load_attendance_data(self):
        self.clear_treeview(self.attendance_tree)
        conn = self.db_connect()
        if not conn:
            return
        
        cursor = conn.cursor()
        query = """
            SELECT a.Mem_ID, m.Name, a.check_in 
            FROM Attendance a
            JOIN Member m ON a.Mem_ID = m.Mem_ID
            WHERE a.check_out IS NULL
        """
        try:
            cursor.execute(query)
            for (mem_id, name, check_in) in cursor:
                self.attendance_tree.insert('', 'end', values=(mem_id, name, check_in.strftime('%Y-%m-%d %H:%M:%S')))
        except mysql.connector.Error as err:
            messagebox.showerror("Data Error", f"Failed to load attendance data:\n{err}")
        finally:
            cursor.close()
            conn.close()

    # ==================================================================
    # TAB 2: MEMBERS
    # ==================================================================
    def setup_members_tab(self):
        main_frame = ttk.Frame(self.tab_members)
        main_frame.pack(fill='both', expand=True)

        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=5)

        ttk.Button(button_frame, text="Refresh List", command=self.load_members_data).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Add New Member", command=self.open_add_member_window).pack(side='left', padx=5)
        ttk.Button(button_frame, text="View Selected Member Details", command=self.open_member_details).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Delete Selected Member", command=self.delete_member).pack(side='left', padx=5)

        self.member_tree = self.create_treeview(main_frame,
            columns=('ID', 'Name', 'Phone', 'Join_Date', 'Age', 'Status'),
            headings={'ID': 'Member ID', 'Name': 'Name', 'Phone': 'Phone', 'Join_Date': 'Join Date', 'Age': 'Age', 'Status': 'Status'}
        )
        
        # Add tags for status coloring
        self.member_tree.tag_configure('Active', background='#e8f8e8', foreground='#006400')
        self.member_tree.tag_configure('Inactive', background='#f8e8e8', foreground='#a00000')

    def load_members_data(self):
        self.clear_treeview(self.member_tree)
        conn = self.db_connect()
        if not conn:
            return
        
        cursor = conn.cursor()
        query = "SELECT Mem_ID, Name, Phone_no, Join_date, Age, Member_Status FROM Member"
        try:
            cursor.execute(query)
            for (mem_id, name, phone, join_date, age, status) in cursor:
                tag = status if status in ('Active', 'Inactive') else 'Inactive'
                self.member_tree.insert('', 'end', values=(mem_id, name, phone, join_date.strftime('%Y-%m-%d'), age, status), tags=(tag,))
        except mysql.connector.Error as err:
            messagebox.showerror("Data Error", f"Failed to load member data:\n{err}")
        finally:
            cursor.close()
            conn.close()
            # Refresh combos in case of new member
            self.load_member_and_trainer_combos()

    def open_add_member_window(self):
        window = tk.Toplevel(self.root)
        window.title("Add New Member")
        
        form_frame = ttk.Frame(window, padding=10)
        form_frame.pack()

        fields = ['Mem_ID', 'Name', 'Phone_no', 'Age']
        entries = {}
        for i, field in enumerate(fields):
            ttk.Label(form_frame, text=f"{field}:").grid(row=i, column=0, padx=5, pady=5, sticky='w')
            entry = ttk.Entry(form_frame, width=30)
            entry.grid(row=i, column=1, padx=5, pady=5)
            entries[field] = entry

        # Add Join Date (auto-populated)
        ttk.Label(form_frame, text="Join_date:").grid(row=len(fields), column=0, padx=5, pady=5, sticky='w')
        join_date_entry = ttk.Entry(form_frame, width=30)
        join_date_entry.insert(0, date.today().strftime('%Y-%m-%d'))
        join_date_entry.grid(row=len(fields), column=1, padx=5, pady=5)
        entries['Join_date'] = join_date_entry
        
        def save():
            conn = self.db_connect()
            if not conn:
                return
            cursor = conn.cursor()
            try:
                query = "INSERT INTO Member (Mem_ID, Name, Phone_no, Age, Join_date) VALUES (%s, %s, %s, %s, %s)"
                data = (
                    entries['Mem_ID'].get(),
                    entries['Name'].get(),
                    entries['Phone_no'].get(),
                    int(entries['Age'].get()),
                    entries['Join_date'].get()
                )
                cursor.execute(query, data)
                conn.commit()
                messagebox.showinfo("Success", "Member added successfully.", parent=window)
                self.load_members_data()
                window.destroy()
            except mysql.connector.Error as err:
                messagebox.showerror("Database Error", f"Failed to add member:\n{err}", parent=window)
            except ValueError:
                messagebox.showerror("Input Error", "Age must be a number.", parent=window)
            finally:
                cursor.close()
                conn.close()

        ttk.Button(form_frame, text="Save Member", command=save, style='Accent.TButton').grid(row=len(fields)+1, column=0, columnspan=2, pady=10)

    def delete_member(self):
        selected_item = self.member_tree.focus()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select a member from the list to delete.")
            return
        
        member_data = self.member_tree.item(selected_item)['values']
        mem_id = member_data[0]
        mem_name = member_data[1]

        if not messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete {mem_name} ({mem_id})?\n\nWARNING: This will permanently delete all their associated payments, attendance records, and workout plans."):
            return

        conn = self.db_connect()
        if not conn:
            return
        
        cursor = conn.cursor()
        try:
            query = "DELETE FROM Member WHERE Mem_ID = %s"
            cursor.execute(query, (mem_id,))
            conn.commit()
            
            messagebox.showinfo("Success", f"Member {mem_name} was deleted successfully.")
            
            # Refresh all related data
            self.load_members_data()
            self.load_payments_data()
            self.load_attendance_data()
            self.load_workout_plans()

        except mysql.connector.Error as err:
            conn.rollback()
            messagebox.showerror("Database Error", f"Failed to delete member:\n{err}")
        finally:
            cursor.close()
            conn.close()

    def open_member_details(self):
        selected_item = self.member_tree.focus()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select a member from the list to view details.")
            return
        
        member_data = self.member_tree.item(selected_item)['values']
        mem_id = member_data[0]
        mem_name = member_data[1]

        window = tk.Toplevel(self.root)
        window.title(f"Details for {mem_name} ({mem_id})")
        window.geometry("800x600")

        conn = self.db_connect()
        if not conn:
            return
        cursor = conn.cursor()

        try:
            # --- General Info & Total Payments (FUNCTION 1) ---
            info_frame = ttk.LabelFrame(window, text="Member Summary", padding=10)
            info_frame.pack(pady=10, padx=10, fill='x')
            
            # Call GetTotalMemberPayments function
            cursor.execute("SELECT GetTotalMemberPayments(%s)", (mem_id,))
            total_payments = cursor.fetchone()[0]
            
            ttk.Label(info_frame, text=f"Name: {mem_name}").pack(anchor='w')
            ttk.Label(info_frame, text=f"Member ID: {mem_id}").pack(anchor='w')
            ttk.Label(info_frame, text=f"Total Payments Made: ₹{total_payments:.2f}").pack(anchor='w')

            # --- Attendance History (FUNCTION 2) ---
            attendance_frame = ttk.LabelFrame(window, text="Attendance History", padding=10)
            attendance_frame.pack(pady=10, padx=10, fill='both', expand=True)
            
            att_tree = self.create_treeview(attendance_frame, 
                columns=('ID', 'Check_In', 'Check_Out', 'Duration'),
                headings={'ID': 'Att. ID', 'Check_In': 'Check-in', 'Check_Out': 'Check-out', 'Duration': 'Duration (min)'}
            )
            
            cursor.execute("SELECT Attendance_ID, check_in, check_out FROM Attendance WHERE Mem_ID = %s", (mem_id,))
            for (att_id, check_in, check_out) in cursor:
                # Call CalculateWorkoutDuration function
                cursor.execute("SELECT CalculateWorkoutDuration(%s)", (att_id,))
                duration = cursor.fetchone()[0]
                duration_str = str(duration) if duration is not None else "N/A"
                att_tree.insert('', 'end', values=(att_id, check_in.strftime('%Y-%m-%d %H:%M'), check_out.strftime('%Y-%m-%d %H:%M') if check_out else "N/A", duration_str))

            # --- Workout Plan ---
            plan_frame = ttk.LabelFrame(window, text="Workout Plan", padding=10)
            plan_frame.pack(pady=10, padx=10, fill='both', expand=True)

            plan_tree = self.create_treeview(plan_frame,
                columns=('Trainer', 'Exercise', 'Reps/Sets'),
                headings={'Trainer': 'Trainer', 'Exercise': 'Exercise', 'Reps/Sets': 'Reps/Sets Info'}
            )

            plan_query = """
                SELECT t.Name, e.Exercise_name, pe.reps_sets_info
                FROM Workout_Plan w
                LEFT JOIN Trainers t ON w.Trainer_ID = t.Trainer_ID
                LEFT JOIN Plan_Exercises pe ON w.Plan_ID = pe.Plan_ID
                LEFT JOIN Exercises e ON pe.Exercise_ID = e.Exercise_ID
                WHERE w.Mem_ID = %s
            """
            cursor.execute(plan_query, (mem_id,))
            results = cursor.fetchall()
            
            if not results or results[0][1] is None:
                plan_tree.insert('', 'end', values=("No trainer assigned", "No exercises added", ""))
            else:
                for (trainer, exercise, reps) in results:
                    trainer_name = trainer if trainer else "N/A"
                    exercise_name = exercise if exercise else "N/A"
                    reps_info = reps if reps else "N/A"
                    plan_tree.insert('', 'end', values=(trainer_name, exercise_name, reps_info))

        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Failed to load member details:\n{err}", parent=window)
        finally:
            cursor.close()
            conn.close()

    # ==================================================================
    # TAB 3: PAYMENTS
    # ==================================================================
    def setup_payments_tab(self):
        main_frame = ttk.Frame(self.tab_payments)
        main_frame.pack(fill='both', expand=True)

        # --- Add Payment Frame ---
        add_payment_frame = ttk.LabelFrame(main_frame, text="Add New Payment", padding=15)
        add_payment_frame.pack(fill='x', pady=10)

        ttk.Label(add_payment_frame, text="Member ID:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.payment_mem_id_entry = ttk.Entry(add_payment_frame, width=30)
        self.payment_mem_id_entry.grid(row=0, column=1, padx=5, pady=5, sticky='ew')

        ttk.Label(add_payment_frame, text="Amount (₹):").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.payment_amount_entry = ttk.Entry(add_payment_frame, width=30)
        self.payment_amount_entry.grid(row=1, column=1, padx=5, pady=5, sticky='ew')
        
        add_payment_btn = ttk.Button(add_payment_frame, text="Submit Payment", command=self.handle_add_payment, style='Accent.TButton')
        add_payment_btn.grid(row=0, column=2, rowspan=2, padx=10, pady=5, sticky='ns')

        add_payment_frame.grid_columnconfigure(1, weight=1)

        # --- Payment History Frame ---
        history_frame = ttk.LabelFrame(main_frame, text="All Payments", padding=15)
        history_frame.pack(fill='both', expand=True, pady=10)

        self.payments_tree = self.create_treeview(history_frame,
            columns=('Payment_ID', 'Mem_ID', 'Amount', 'Date', 'Status'),
            headings={'Payment_ID': 'Payment ID', 'Mem_ID': 'Member ID', 'Amount': 'Amount (₹)', 'Date': 'Date', 'Status': 'Status'}
        )
        ttk.Button(main_frame, text="Refresh Payment List", command=self.load_payments_data).pack(pady=5)

    def handle_add_payment(self):
        mem_id = self.payment_mem_id_entry.get()
        amount_str = self.payment_amount_entry.get()

        if not mem_id or not amount_str:
            messagebox.showwarning("Input Error", "Please enter both Member ID and Amount.")
            return

        try:
            amount = float(amount_str)
        except ValueError:
            messagebox.showwarning("Input Error", "Amount must be a valid number.")
            return

        conn = self.db_connect()
        if not conn:
            return
        
        cursor = conn.cursor()
        try:
            query = "INSERT INTO Payment (Mem_ID, amount, Payment_date) VALUES (%s, %s, %s)"
            cursor.execute(query, (mem_id, amount, date.today()))
            conn.commit()

            messagebox.showinfo("Success", f"Payment of ₹{amount:.2f} for {mem_id} recorded.")
            
            # Clear entries
            self.payment_mem_id_entry.delete(0, 'end')
            self.payment_amount_entry.delete(0, 'end')
            
            # THIS IS THE TRIGGER DEMONSTRATION
            # The AfterPaymentInsert trigger has fired. Now we refresh the lists
            # to *show* its effect.
            self.load_payments_data()
            self.load_members_data() # This will show the member's status update

        except mysql.connector.Error as err:
            conn.rollback()
            messagebox.showerror("Database Error", f"Failed to add payment:\n{err}")
        finally:
            cursor.close()
            conn.close()

    def load_payments_data(self):
        self.clear_treeview(self.payments_tree)
        conn = self.db_connect()
        if not conn:
            return
        
        cursor = conn.cursor()
        query = "SELECT Payment_ID, Mem_ID, amount, Payment_date, Payment_status FROM Payment"
        try:
            cursor.execute(query)
            for (pid, mid, amount, pdate, status) in cursor:
                self.payments_tree.insert('', 'end', values=(pid, mid, f"₹{amount:.2f}", pdate.strftime('%Y-%m-%d'), status))
        except mysql.connector.Error as err:
            messagebox.showerror("Data Error", f"Failed to load payment data:\n{err}")
        finally:
            cursor.close()
            conn.close()

    # ==================================================================
    # TAB 4: TRAINERS
    # ==================================================================
    def setup_trainers_tab(self):
        main_frame = ttk.Frame(self.tab_trainers)
        main_frame.pack(fill='both', expand=True)

        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=5)

        ttk.Button(button_frame, text="Add New Trainer", command=self.open_add_trainer_window).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Delete Selected Trainer", command=self.delete_trainer).pack(side='left', padx=5)

        self.trainers_tree = self.create_treeview(main_frame,
            columns=('ID', 'Name', 'Salary', 'Date_Hired'),
            headings={'ID': 'Trainer ID', 'Name': 'Name', 'Salary': 'Salary (₹)', 'Date_Hired': 'Date Hired'}
        )
        # self.load_trainers_data() # Initial load <-- REMOVED: This call is premature and redundant.
        # Data will be loaded by the __init__ method after all tabs are created.

    def load_trainers_data(self):
        self.clear_treeview(self.trainers_tree)
        conn = self.db_connect()
        if not conn:
            return
        
        cursor = conn.cursor()
        query = "SELECT Trainer_ID, Name, Salary, Date_hired FROM Trainers"
        try:
            cursor.execute(query)
            for (tid, name, salary, hired) in cursor:
                self.trainers_tree.insert('', 'end', values=(tid, name, f"₹{salary:.2f}", hired.strftime('%Y-%m-%d')))
        except mysql.connector.Error as err:
            messagebox.showerror("Data Error", f"Failed to load trainer data:\n{err}")
        finally:
            cursor.close()
            conn.close()
            # Refresh combos in case of new trainer
            self.load_member_and_trainer_combos()

    def open_add_trainer_window(self):
        window = tk.Toplevel(self.root)
        window.title("Add New Trainer")
        
        form_frame = ttk.Frame(window, padding=10)
        form_frame.pack()

        fields = ['Name', 'Salary']
        entries = {}
        for i, field in enumerate(fields):
            label_text = f"{field} (₹):" if field == 'Salary' else f"{field}:"
            ttk.Label(form_frame, text=label_text).grid(row=i, column=0, padx=5, pady=5, sticky='w')
            entry = ttk.Entry(form_frame, width=30)
            entry.grid(row=i, column=1, padx=5, pady=5)
            entries[field] = entry

        ttk.Label(form_frame, text="Date_hired:").grid(row=len(fields), column=0, padx=5, pady=5, sticky='w')
        hired_date_entry = ttk.Entry(form_frame, width=30)
        hired_date_entry.insert(0, date.today().strftime('%Y-%m-%d'))
        hired_date_entry.grid(row=len(fields), column=1, padx=5, pady=5)
        entries['Date_hired'] = hired_date_entry
        
        def save():
            conn = self.db_connect()
            if not conn:
                return
            cursor = conn.cursor()
            try:
                query = "INSERT INTO Trainers (Name, Salary, Date_hired) VALUES (%s, %s, %s)"
                data = (
                    entries['Name'].get(),
                    float(entries['Salary'].get()),
                    entries['Date_hired'].get()
                )
                cursor.execute(query, data)
                conn.commit()
                messagebox.showinfo("Success", "Trainer added successfully.", parent=window)
                self.load_trainers_data()
                window.destroy()
            except mysql.connector.Error as err:
                messagebox.showerror("Database Error", f"Failed to add trainer:\n{err}", parent=window)
            except ValueError:
                messagebox.showerror("Input Error", "Salary must be a number.", parent=window)
            finally:
                cursor.close()
                conn.close()

        ttk.Button(form_frame, text="Save Trainer", command=save, style='Accent.TButton').grid(row=len(fields)+1, column=0, columnspan=2, pady=10)

    def delete_trainer(self):
        selected_item = self.trainers_tree.focus()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select a trainer from the list to delete.")
            return
        
        trainer_data = self.trainers_tree.item(selected_item)['values']
        trainer_id = trainer_data[0]
        trainer_name = trainer_data[1]

        if not messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete {trainer_name} (ID: {trainer_id})?\n\nWARNING: This will permanently delete all workout plans assigned to this trainer."):
            return

        conn = self.db_connect()
        if not conn:
            return
        
        cursor = conn.cursor()
        try:
            query = "DELETE FROM Trainers WHERE Trainer_ID = %s"
            cursor.execute(query, (trainer_id,))
            conn.commit()
            
            messagebox.showinfo("Success", f"Trainer {trainer_name} was deleted successfully.")
            
            # Refresh related data
            self.load_trainers_data()
            self.load_workout_plans()

        except mysql.connector.Error as err:
            conn.rollback()
            messagebox.showerror("Database Error", f"Failed to delete trainer:\n{err}")
        finally:
            cursor.close()
            conn.close()

    # ==================================================================
    # TAB 5: WORKOUT PLANS
    # ==================================================================
    def setup_plans_tab(self):
        main_frame = ttk.Frame(self.tab_plans)
        main_frame.pack(fill='both', expand=True)

        # --- Create New Plan Frame ---
        create_plan_frame = ttk.LabelFrame(main_frame, text="Create New Workout Plan", padding=15)
        create_plan_frame.pack(fill='x', pady=10)

        ttk.Label(create_plan_frame, text="Select Member:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.plan_member_combo = ttk.Combobox(create_plan_frame, state='readonly', width=30)
        self.plan_member_combo.grid(row=0, column=1, padx=5, pady=5, sticky='ew')

        ttk.Label(create_plan_frame, text="Select Trainer:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.plan_trainer_combo = ttk.Combobox(create_plan_frame, state='readonly', width=30)
        self.plan_trainer_combo.grid(row=1, column=1, padx=5, pady=5, sticky='ew')
        
        ttk.Label(create_plan_frame, text="Start Date (YYYY-MM-DD):").grid(row=2, column=0, padx=5, pady=5, sticky='w')
        self.plan_start_entry = ttk.Entry(create_plan_frame, width=30)
        self.plan_start_entry.insert(0, date.today().strftime('%Y-%m-%d'))
        self.plan_start_entry.grid(row=2, column=1, padx=5, pady=5, sticky='ew')

        ttk.Label(create_plan_frame, text="End Date (YYYY-MM-DD):").grid(row=3, column=0, padx=5, pady=5, sticky='w')
        self.plan_end_entry = ttk.Entry(create_plan_frame, width=30)
        self.plan_end_entry.grid(row=3, column=1, padx=5, pady=5, sticky='ew')

        create_plan_btn = ttk.Button(create_plan_frame, text="Create Plan", command=self.handle_create_plan, style='Accent.TButton')
        create_plan_btn.grid(row=1, column=2, rowspan=2, padx=10, pady=5, sticky='ns')

        create_plan_frame.grid_columnconfigure(1, weight=1)

        # --- Existing Plans Frame ---
        plans_frame = ttk.LabelFrame(main_frame, text="Existing Workout Plans", padding=15)
        plans_frame.pack(fill='both', expand=True, pady=10)

        self.plans_tree = self.create_treeview(plans_frame,
            columns=('Plan_ID', 'Member', 'Trainer', 'Start', 'End'),
            headings={'Plan_ID': 'Plan ID', 'Member': 'Member Name', 'Trainer': 'Trainer Name', 'Start': 'Start Date', 'End': 'End Date'}
        )
        
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=5)
        ttk.Button(button_frame, text="Refresh Plan List", command=self.load_workout_plans).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Manage Exercises for Selected Plan", command=self.open_manage_exercises_window).pack(side='left', padx=5)

    def load_workout_plans(self):
        self.clear_treeview(self.plans_tree)
        conn = self.db_connect()
        if not conn:
            return
        
        cursor = conn.cursor()
        query = """
            SELECT w.Plan_ID, m.Name, t.Name, w.Start_date, w.End_date 
            FROM Workout_Plan w
            JOIN Member m ON w.Mem_ID = m.Mem_ID
            JOIN Trainers t ON w.Trainer_ID = t.Trainer_ID
        """
        try:
            cursor.execute(query)
            for (pid, mem_name, trainer_name, start, end) in cursor:
                end_date_str = end.strftime('%Y-%m-%d') if end else "N/A"
                self.plans_tree.insert('', 'end', values=(pid, mem_name, trainer_name, start.strftime('%Y-%m-%d'), end_date_str))
        except mysql.connector.Error as err:
            messagebox.showerror("Data Error", f"Failed to load workout plans:\n{err}")
        finally:
            cursor.close()
            conn.close()

    def load_member_and_trainer_combos(self):
        conn = self.db_connect()
        if not conn:
            return
        
        cursor = conn.cursor()
        try:
            # Load members
            cursor.execute("SELECT Mem_ID, Name FROM Member")
            members = cursor.fetchall()
            self.member_map = {name: mem_id for (mem_id, name) in members}
            self.plan_member_combo['values'] = sorted(self.member_map.keys())

            # Load trainers
            cursor.execute("SELECT Trainer_ID, Name FROM Trainers")
            trainers = cursor.fetchall()
            self.trainer_map = {name: trainer_id for (trainer_id, name) in trainers}
            self.plan_trainer_combo['values'] = sorted(self.trainer_map.keys())

        except mysql.connector.Error as err:
            messagebox.showerror("Data Error", f"Failed to load member/trainer lists for combos:\n{err}")
        finally:
            cursor.close()
            conn.close()

    def load_all_exercises_map(self):
        """Loads all exercises from DB into the self.exercise_map."""
        conn = self.db_connect()
        if not conn:
            return
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT Exercise_ID, Exercise_name FROM Exercises")
            exercises = cursor.fetchall()
            self.exercise_map = {name: ex_id for (ex_id, name) in exercises}
        except mysql.connector.Error as err:
            messagebox.showerror("Data Error", f"Failed to load exercises list:\n{err}")
        finally:
            cursor.close()
            conn.close()

    def handle_create_plan(self):
        member_name = self.plan_member_combo.get()
        trainer_name = self.plan_trainer_combo.get()
        start_date_str = self.plan_start_entry.get()
        end_date_str = self.plan_end_entry.get()

        if not member_name or not trainer_name or not start_date_str:
            messagebox.showwarning("Input Error", "Please select a Member, a Trainer, and enter a Start Date.")
            return

        try:
            mem_id = self.member_map[member_name]
            trainer_id = self.trainer_map[trainer_name]
            
            # Validate dates
            datetime.strptime(start_date_str, '%Y-%m-%d')
            end_date = None
            if end_date_str:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            
        except KeyError:
            messagebox.showerror("Internal Error", "Could not find ID for selected member or trainer.")
            return
        except ValueError:
            messagebox.showwarning("Input Error", "Dates must be in YYYY-MM-DD format.")
            return

        conn = self.db_connect()
        if not conn:
            return
        
        cursor = conn.cursor()
        try:
            query = """
                INSERT INTO Workout_Plan (Mem_ID, Trainer_ID, Start_date, End_date) 
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query, (mem_id, trainer_id, start_date_str, end_date))
            conn.commit()
            
            messagebox.showinfo("Success", f"Workout plan created for {member_name}.")
            self.load_workout_plans() # Refresh the list

        except mysql.connector.Error as err:
            conn.rollback()
            messagebox.showerror("Database Error", f"Failed to create plan:\n{err}")
        finally:
            cursor.close()
            conn.close()

    def open_manage_exercises_window(self):
        selected_item = self.plans_tree.focus()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select a workout plan from the list to manage its exercises.")
            return
        
        plan_data = self.plans_tree.item(selected_item)['values']
        plan_id = plan_data[0]
        member_name = plan_data[1]
        window_title = f"Exercises for {member_name} (Plan ID: {plan_id})"

        # Pass the pre-loaded exercise map to the new window
        ManageExercisesWindow(self.root, plan_id, window_title, self.exercise_map)

    # ==================================================================
    # TAB 6: ADMIN (Renumbered)
    # ==================================================================
    def setup_admin_tab(self):
        admin_frame = ttk.LabelFrame(self.tab_admin, text="Administrative Tasks", padding=20)
        admin_frame.pack(pady=50, padx=50)

        ttk.Label(admin_frame, text="Update all member statuses based on last payment (31-day check).").pack(pady=10)
        
        ttk.Button(admin_frame, text="Run 'UpdateAllMemberStatuses' Procedure", 
                   command=self.run_status_update_procedure, 
                   style='Accent.TButton').pack(pady=10)
                   
        self.admin_status_label = ttk.Label(admin_frame, text="")
        self.admin_status_label.pack(pady=5)

    def run_status_update_procedure(self):
        if not messagebox.askyesno("Confirm", "Are you sure you want to update all member statuses? This will run the 'UpdateAllMemberStatuses' procedure."):
            return

        conn = self.db_connect()
        if not conn:
            return
        
        cursor = conn.cursor()
        try:
            self.admin_status_label.config(text="Executing procedure...", style='Success.TLabel')
            cursor.callproc('UpdateAllMemberStatuses')
            conn.commit()
            
            self.admin_status_label.config(text="All member statuses updated successfully.", style='Success.TLabel')
            messagebox.showinfo("Success", "Procedure 'UpdateAllMemberStatuses' executed successfully.")
            
            # Refresh members to show changes
            self.load_members_data()

        except mysql.connector.Error as err:
            conn.rollback()
            messagebox.showerror("Procedure Error", f"Failed to run procedure:\n{err}")
            self.admin_status_label.config(text="An error occurred.", style='Error.TLabel')
        finally:
            cursor.close()
            conn.close()

    # ==================================================================
    # HELPER/UTILITY FUNCTIONS
    # ==================================================================
    def create_treeview(self, parent, columns, headings):
        """Helper function to create a styled Treeview with scrollbar."""
        tree_frame = ttk.Frame(parent)
        tree_frame.pack(fill='both', expand=True, pady=5)
        
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side='right', fill='y')
        
        tree = ttk.Treeview(
            tree_frame, 
            columns=columns, 
            show='headings', 
            yscrollcommand=scrollbar.set
        )
        tree.pack(fill='both', expand=True)
        scrollbar.config(command=tree.yview)
        
        for col_id, text in headings.items():
            tree.heading(col_id, text=text, anchor='w')
            tree.column(col_id, anchor='w', width=100) # Default width
            
        return tree

    def clear_treeview(self, tree):
        """Removes all items from a Treeview."""
        for item in tree.get_children():
            tree.delete(item)

# ==================================================================
# NEW Toplevel Window Class for Managing Exercises
# ==================================================================
class ManageExercisesWindow:
    def __init__(self, parent, plan_id, title, exercise_map):
        self.window = tk.Toplevel(parent)
        self.window.title(title)
        self.window.geometry("600x500")
        
        self.plan_id = plan_id
        self.exercise_map = exercise_map # {name: id}

        self.setup_ui()
        self.load_plan_exercises()

    def db_connect(self):
        """Establishes a connection to the database."""
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            return conn
        except mysql.connector.Error as err:
            messagebox.showerror("Database Connection Error", f"Failed to connect to MySQL:\n{err}", parent=self.window)
            return None

    def setup_ui(self):
        # --- Top Frame: Add Exercise ---
        add_frame = ttk.LabelFrame(self.window, text="Add Exercise to Plan", padding=10)
        add_frame.pack(fill='x', padx=10, pady=10)

        ttk.Label(add_frame, text="Exercise:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.exercise_combo = ttk.Combobox(add_frame, state='readonly', width=30)
        self.exercise_combo['values'] = sorted(self.exercise_map.keys())
        self.exercise_combo.grid(row=0, column=1, padx=5, pady=5, sticky='ew')

        ttk.Label(add_frame, text="Reps/Sets Info:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.reps_entry = ttk.Entry(add_frame, width=30)
        self.reps_entry.grid(row=1, column=1, padx=5, pady=5, sticky='ew')
        
        ttk.Button(add_frame, text="Add Exercise", command=self.add_exercise_to_plan, style='Accent.TButton').grid(row=0, column=2, rowspan=2, padx=10, sticky='ns')
        add_frame.grid_columnconfigure(1, weight=1)

        # --- Bottom Frame: Current Exercises ---
        current_frame = ttk.LabelFrame(self.window, text="Current Exercises in Plan", padding=10)
        current_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Note: We include Exercise_ID in columns but hide it, to retrieve it for deletion
        self.plan_exercises_tree = self.create_treeview(
            current_frame,
            columns=('Name', 'Reps', 'Exercise_ID'),
            headings={'Name': 'Exercise', 'Reps': 'Reps/Sets Info', 'Exercise_ID': 'ID'}
        )
        self.plan_exercises_tree['displaycolumns'] = ('Name', 'Reps')

        ttk.Button(current_frame, text="Remove Selected Exercise", command=self.remove_exercise_from_plan).pack(pady=5)

    def load_plan_exercises(self):
        self.clear_treeview(self.plan_exercises_tree)
        conn = self.db_connect()
        if not conn:
            return
        
        cursor = conn.cursor()
        query = """
            SELECT e.Exercise_name, pe.reps_sets_info, e.Exercise_ID 
            FROM Plan_Exercises pe 
            JOIN Exercises e ON pe.Exercise_ID = e.Exercise_ID 
            WHERE pe.Plan_ID = %s
        """
        try:
            cursor.execute(query, (self.plan_id,))
            for (name, reps, ex_id) in cursor:
                self.plan_exercises_tree.insert('', 'end', values=(name, reps, ex_id))
        except mysql.connector.Error as err:
            messagebox.showerror("Data Error", f"Failed to load plan exercises:\n{err}", parent=self.window)
        finally:
            cursor.close()
            conn.close()

    def add_exercise_to_plan(self):
        exercise_name = self.exercise_combo.get()
        reps_info = self.reps_entry.get()

        if not exercise_name or not reps_info:
            messagebox.showwarning("Input Error", "Please select an exercise and enter reps/sets info.", parent=self.window)
            return

        try:
            exercise_id = self.exercise_map[exercise_name]
        except KeyError:
            messagebox.showerror("Internal Error", "Could not find selected exercise ID.", parent=self.window)
            return

        conn = self.db_connect()
        if not conn:
            return
        
        cursor = conn.cursor()
        query = "INSERT INTO Plan_Exercises (Plan_ID, Exercise_ID, reps_sets_info) VALUES (%s, %s, %s)"
        try:
            cursor.execute(query, (self.plan_id, exercise_id, reps_info))
            conn.commit()
            
            # Refresh list and clear entries
            self.load_plan_exercises()
            self.reps_entry.delete(0, 'end')
            self.exercise_combo.set('')

        except mysql.connector.Error as err:
            conn.rollback()
            if err.errno == 1062: # Duplicate entry
                messagebox.showerror("Database Error", "This exercise is already in the plan.", parent=self.window)
            else:
                messagebox.showerror("Database Error", f"Failed to add exercise:\n{err}", parent=self.window)
        finally:
            cursor.close()
            conn.close()

    def remove_exercise_from_plan(self):
        selected_item = self.plan_exercises_tree.focus()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select an exercise from the list to remove.", parent=self.window)
            return

        item_data = self.plan_exercises_tree.item(selected_item)['values']
        exercise_name = item_data[0]
        exercise_id = item_data[2] # Get the hidden Exercise_ID

        if not messagebox.askyesno("Confirm Deletion", f"Are you sure you want to remove '{exercise_name}' from this plan?", parent=self.window):
            return

        conn = self.db_connect()
        if not conn:
            return
        
        cursor = conn.cursor()
        query = "DELETE FROM Plan_Exercises WHERE Plan_ID = %s AND Exercise_ID = %s"
        try:
            cursor.execute(query, (self.plan_id, exercise_id))
            conn.commit()
            self.load_plan_exercises() # Refresh list
        except mysql.connector.Error as err:
            conn.rollback()
            messagebox.showerror("Database Error", f"Failed to remove exercise:\n{err}", parent=self.window)
        finally:
            cursor.close()
            conn.close()

    # --- Helper methods copied from GymApp ---
    def create_treeview(self, parent, columns, headings):
        tree_frame = ttk.Frame(parent)
        tree_frame.pack(fill='both', expand=True, pady=5)
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side='right', fill='y')
        tree = ttk.Treeview(tree_frame, columns=columns, show='headings', yscrollcommand=scrollbar.set)
        tree.pack(fill='both', expand=True)
        scrollbar.config(command=tree.yview)
        for col_id, text in headings.items():
            tree.heading(col_id, text=text, anchor='w')
            tree.column(col_id, anchor='w', width=100)
        return tree

    def clear_treeview(self, tree):
        for item in tree.get_children():
            tree.delete(item)


if __name__ == '__main__':
    root = tk.Tk()
    app = GymApp(root)
    root.mainloop()