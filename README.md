# Gym Management System

## Project Description

This project is a complete Gym Management System, combining a robust MySQL database backend with a feature-rich Python Tkinter graphical user interface (GUI).

The system is designed to manage all core aspects of a gym's operations, including members, trainers, payments, attendance, and customized workout plans.

The database backend (SQL script) includes advanced features like triggers, stored procedures, and functions to ensure data integrity and automate common tasks. The frontend (Python GUI) provides a user-friendly, multi-tabbed interface for staff to interact with the database and manage the gym.

## Features

### GUI (Python Tkinter) Features

* **Multi-Tab Interface:** A clean, organized layout separating key management areas (Check-in, Members, Payments, Trainers, Workout Plans, Admin).
* **Member Management:**
    * Add new members with all necessary details.
    * Delete members (which cascades to all their related data).
    * View a complete list of all members, color-coded by their 'Active' or 'Inactive' status.
    * Open a detailed view for any member to see their payment history, attendance log (with workout durations), and assigned workout plan.
* **Trainer Management:**
    * Add new trainers to the system.
    * Delete trainers (which cascades to their assigned workout plans).
* **Payment System:**
    * Log new payments for members.
    * Automatically triggers the database to update a member's status to 'Active'.
    * View a complete, filterable history of all payments.
* **Attendance Tracking:**
    * Check-in members using their Member ID.
    * Check-out members.
    * View a real-time list of all members currently checked into the gym.
* **Workout Plan Management:**
    * Create new workout plans by assigning a trainer to a member.
    * Open a dedicated window to manage a specific plan.
    * Assign exercises from a master list to the plan.
    * Set custom reps/sets information for each assigned exercise.
    * Remove exercises from a plan.
* **Admin Panel:**
    * Provides access to database administrative tasks.
    * Includes a button to run the `UpdateAllMemberStatuses` procedure to synchronize all member statuses at once.

### Database (MySQL) Features

* **Triggers:**
    * `AfterPaymentInsert`: Automatically updates a member's `Member_Status` to 'Active' the moment a new payment is inserted for them.
    * `PreventInactiveMemberCheckin`: Prevents a member from being checked in if their last payment was more than 31 days ago, enforcing membership validity at the door.
* **Stored Procedures:**
    * `UpdateAllMemberStatuses`: A procedure that can be called to iterate through all members and set their status to 'Active' or 'Inactive' based on their payment history. This is used by the Admin tab.
* **Functions:**
    * `CalculateWorkoutDuration`: Calculates the duration of a specific workout session in minutes based on check-in and check-out times.
    * `GetTotalMemberPayments`: Returns the sum of all payments made by a specific member.

## Prerequisites

To run this project, you will need:

* **Python 3.x**
* **MySQL Server** (local or remote)
* **Python Libraries:**
    * `tkinter` (This is typically included with standard Python installations)
    * `mysql-connector-python`

## Installation and Setup

Follow these steps to get the application running:

### 1. Database Setup

1.  Ensure you have a running MySQL server.
2.  Open a MySQL client (like MySQL Workbench or the command-line interface).
3.  Execute the provided SQL script (e.g., `gym_management.sql`) to create the `gym_management` database, all required tables, triggers, functions, and stored procedures.

### 2. Python Application Setup

1.  Install the required Python library using pip:
    ```bash
    pip install mysql-connector-python
    ```
2.  Open the `gym_app_main.py` file in a text editor.
3.  Locate the `DB_CONFIG` dictionary at the top of the file:

    ```python
    DB_CONFIG = {
        "host": "localhost",
        "user": "your_mysql_user", 
        "password": "your_mysql_password", 
        "database": "gym_management"
    }
    ```
4.  **Crucial:** Update the `host`, `user`, and `password` fields to match your local MySQL server credentials.

### 3. Running the Application

Once the database is set up and the `DB_CONFIG` is updated, you can run the application:

```bash
python gym_app_main.py
