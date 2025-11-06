-- ====================================================================
-- SECTION 1: DATABASE SETUP
-- Creates the database and drops old tables safely.
-- ====================================================================

CREATE DATABASE IF NOT EXISTS gym_management;
USE gym_management;

-- Temporarily disable foreign key checks to allow dropping tables in any order
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS Plan_Exercises;
DROP TABLE IF EXISTS Attendance;
DROP TABLE IF EXISTS Payment;
DROP TABLE IF EXISTS Workout_Plan;
DROP TABLE IF EXISTS Member;
DROP TABLE IF EXISTS Trainers;
DROP TABLE IF EXISTS Exercises;

-- Re-enable foreign key checks
SET FOREIGN_KEY_CHECKS = 1;


-- ====================================================================
-- SECTION 2: SCHEMA (TABLE CREATION)
-- ====================================================================

-- Trainers Table: Stores trainer information and supervisor hierarchy.
CREATE TABLE Trainers (
    Trainer_ID INT PRIMARY KEY AUTO_INCREMENT,
    Name VARCHAR(100) NOT NULL,
    Salary DECIMAL(10, 2) NOT NULL,
    Date_hired DATE NOT NULL,
    FOREIGN KEY (Mem_ID) REFERENCES Member(Mem_ID) ON DELETE CASCADE
);

-- Exercises Table: A catalog of all available exercises.
CREATE TABLE Exercises (
    Exercise_ID INT PRIMARY KEY AUTO_INCREMENT,
    Exercise_name VARCHAR(100) NOT NULL UNIQUE,
    equipment VARCHAR(100),
    instruction TEXT
);

-- Member Table: Stores details for each gym member.
CREATE TABLE Member (
    Mem_ID VARCHAR(20) PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    Phone_no VARCHAR(15) UNIQUE,
    Join_date DATE NOT NULL,
    Age INT,
    Member_Status VARCHAR(20) DEFAULT 'Inactive' -- Can be 'Active' or 'Inactive'
);

-- Workout Plan Table: Links a member to a trainer for a specific plan.
CREATE TABLE Workout_Plan (
    Plan_ID INT PRIMARY KEY AUTO_INCREMENT,
    Mem_ID VARCHAR(20) NOT NULL,
    Trainer_ID INT NOT NULL,
    Start_date DATE NOT NULL,
    End_date DATE,
    FOREIGN KEY (Mem_ID) REFERENCES Member(Mem_ID) ON DELETE CASCADE,
    FOREIGN KEY (Trainer_ID) REFERENCES Trainers(Trainer_ID) ON DELETE CASCADE
);

-- Payment Table: Records all payments made by members.
CREATE TABLE Payment (
    Payment_ID INT PRIMARY KEY AUTO_INCREMENT,
    Mem_ID VARCHAR(20) NOT NULL,
    amount DECIMAL(8, 2) NOT NULL,
    Payment_date DATE NOT NULL,
    Payment_status VARCHAR(20) DEFAULT 'Completed',
    FOREIGN KEY (Mem_ID) REFERENCES Member(Mem_ID) ON DELETE CASCADE
);

-- Attendance Table: Logs member check-in and check-out times.
CREATE TABLE Attendance (
    Attendance_ID INT PRIMARY KEY AUTO_INCREMENT,
    Mem_ID VARCHAR(20) NOT NULL,
    check_in DATETIME NOT NULL,
    check_out DATETIME,
    FOREIGN KEY (Mem_ID) REFERENCES Member(Mem_ID) ON DELETE CASCADE
);

-- Plan_Exercises Linking Table: Defines which exercises are in which plan.
CREATE TABLE Plan_Exercises (
    Plan_ID INT NOT NULL,
    Exercise_ID INT NOT NULL,
    reps_sets_info VARCHAR(50), -- e.g., '3 sets of 12 reps'
    PRIMARY KEY (Plan_ID, Exercise_ID),
    FOREIGN KEY (Plan_ID) REFERENCES Workout_Plan(Plan_ID) ON DELETE CASCADE,
    FOREIGN KEY (Exercise_ID) REFERENCES Exercises(Exercise_ID) ON DELETE CASCADE
);


-- ====================================================================
-- SECTION 3: SAMPLE DATA (WITH UPDATED DATES)
-- Dates are now relative to the current date (October 2025) for better testing.
-- ====================================================================

-- Inserting Trainers
INSERT INTO Trainers (Trainer_ID, Name, Salary, Date_hired) VALUES
(1, 'Arjun Gupta', 50000.00, '2022-01-15'),
(2, 'Priya Sharma', 45000.00, '2022-03-01'),
(3, 'Rohan Singh', 42000.00, '2023-05-20'),
(4, 'Anjali Verma', 46000.00, '2023-02-10');

-- Inserting Exercises
INSERT INTO Exercises (Exercise_name, equipment, instruction) VALUES
('Bench Press', 'Barbell, Bench', 'Lie on the bench, lower the bar to your chest, and press upwards.'),
('Squat', 'Barbell, Squat Rack', 'Place the barbell on your shoulders, lower your hips as if sitting, and rise back up.'),
('Deadlift', 'Barbell', 'Lift the barbell from the floor by extending your hips and knees.'),
('Pull-up', 'Pull-up Bar', 'Hang from the bar and pull your body up until your chin is over the bar.'),
('Leg Press', 'Leg Press Machine', 'Push the platform away with your feet.'),
('Bicep Curl', 'Dumbbells', 'Curl the dumbbells towards your shoulders, keeping elbows stationary.'),
('Tricep Dip', 'Parallel Bars', 'Lower and raise your body using your triceps.'),
('Plank', 'Mat', 'Hold a push-up position on your forearms.'),
('Treadmill Run', 'Treadmill', 'Run or walk on the moving belt.'),
('Cycling', 'Stationary Bike', 'Pedal at a consistent pace.');

-- Inserting Members
INSERT INTO Member (Mem_ID, Name, Phone_no, Join_date, Age) VALUES
('MEM1003', 'Sneha Patel', '9876543212', '2023-02-20', 29),
('MEM1004', 'Vikram Rathore', '9876543213', '2025-08-05', 35), -- Recent joiner
('MEM1005', 'Aisha Khan', '9876543214', '2025-09-12', 26), -- Recent joiner
('MEM1006', 'Deepak Kumar', '9876543215', '2023-05-18', 45), -- Old member
('MEM1007', 'Fatima Sheikh', '9876543216', '2025-09-22', 23); -- Very recent joiner

-- Inserting Payments (NOTE: Dates are updated for realistic status checks)
INSERT INTO Payment (Mem_ID, amount, Payment_date) VALUES
('MEM1003', 5000.00, '2024-02-20'),                               -- Expired payment
('MEM1004', 1500.00, DATE_SUB(CURDATE(), INTERVAL 10 DAY)), -- Active payment
('MEM1005', 1500.00, DATE_SUB(CURDATE(), INTERVAL 5 DAY)),  -- Active payment
('MEM1006', 5000.00, '2024-05-18'),                               -- Expired payment
('MEM1007', 1500.00, CURDATE());                                   -- Active payment (paid today)

-- Inserting Attendance Records
INSERT INTO Attendance (Mem_ID, check_in, check_out) VALUES
('MEM1004', '2025-10-01 07:00:00', '2025-10-01 08:30:00'),
('MEM1005', '2025-10-02 18:00:00', '2025-10-02 19:15:00'),
('MEM1007', '2025-10-03 09:00:00', NULL); -- Member hasn't checked out yet

-- Inserting Workout Plans
INSERT INTO Workout_Plan (Mem_ID, Trainer_ID, Start_date, End_date) VALUES
('MEM1004', 2, '2025-08-06', '2025-11-06'),
('MEM1005', 4, '2025-09-13', '2025-12-13'),
('MEM1007', 1, '2025-09-22', NULL);

-- Populating Plan_Exercises
INSERT INTO Plan_Exercises (Plan_ID, Exercise_ID, reps_sets_info) VALUES
(1, 1, '3 sets of 10 reps'), -- Vikram's Plan: Bench Press
(1, 2, '4 sets of 8 reps'),  -- Vikram's Plan: Squat
(2, 9, '30 minutes'),        -- Aisha's Plan: Treadmill Run
(2, 8, '3 sets of 60s'),     -- Aisha's Plan: Plank
(3, 3, '5 sets of 3 reps'),  -- Fatima's Plan: Deadlift
(3, 5, '4 sets of 10 reps'); -- Fatima's Plan: Leg Press


-- ====================================================================
-- SECTION 4: FUNCTIONS
-- ====================================================================

-- Function 1: Calculate the duration of a workout in minutes.
DROP FUNCTION IF EXISTS CalculateWorkoutDuration;
DELIMITER $$
CREATE FUNCTION CalculateWorkoutDuration(p_attendance_id INT)
RETURNS INT
DETERMINISTIC
BEGIN
    DECLARE v_check_in DATETIME;
    DECLARE v_check_out DATETIME;
    DECLARE v_duration INT;

    SELECT check_in, check_out INTO v_check_in, v_check_out
    FROM Attendance
    WHERE Attendance_ID = p_attendance_id;

    IF v_check_out IS NULL THEN
        RETURN NULL;
    ELSE
        SET v_duration = TIMESTAMPDIFF(MINUTE, v_check_in, v_check_out);
        RETURN v_duration;
    END IF;
END$$
DELIMITER ;

-- Function 2: Get the total sum of payments for a specific member.
DROP FUNCTION IF EXISTS GetTotalMemberPayments;
DELIMITER $$
CREATE FUNCTION GetTotalMemberPayments(p_mem_id VARCHAR(20))
RETURNS DECIMAL(10, 2)
DETERMINISTIC
BEGIN
    DECLARE v_total_payment DECIMAL(10, 2);

    SELECT SUM(amount) INTO v_total_payment
    FROM Payment
    WHERE Mem_ID = p_mem_id;

    RETURN IFNULL(v_total_payment, 0.00);
END$$
DELIMITER ;


-- ====================================================================
-- SECTION 5: TRIGGERS AND PROCEDURES
-- ====================================================================

-- Trigger 1: Instantly marks a member as 'Active' right after a payment is inserted.
DROP TRIGGER IF EXISTS AfterPaymentInsert;
DELIMITER $$
CREATE TRIGGER AfterPaymentInsert
AFTER INSERT ON Payment
FOR EACH ROW
BEGIN
    UPDATE Member
    SET Member_Status = 'Active'
    WHERE Mem_ID = NEW.Mem_ID;
END$$
DELIMITER ;

-- Trigger 2: Prevents check-in if membership is expired.
DROP TRIGGER IF EXISTS PreventInactiveMemberCheckin;
DELIMITER $$
CREATE TRIGGER PreventInactiveMemberCheckin
BEFORE INSERT ON Attendance
FOR EACH ROW
BEGIN
    DECLARE v_last_payment_date DATE;

    SELECT MAX(Payment_date) INTO v_last_payment_date
    FROM Payment
    WHERE Mem_ID = NEW.Mem_ID;

    IF v_last_payment_date IS NULL OR v_last_payment_date < DATE_SUB(CURDATE(), INTERVAL 31 DAY) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Check-in failed: Membership is expired. Please make a payment.';
    END IF;
END$$
DELIMITER ;

-- Stored Procedure 1: Updates the status for ALL members based on their last payment.
DROP PROCEDURE IF EXISTS UpdateAllMemberStatuses;
DELIMITER $$
CREATE PROCEDURE UpdateAllMemberStatuses()
BEGIN
    -- Set members with a recent payment to 'Active'
    UPDATE Member m JOIN (
        SELECT Mem_ID, MAX(Payment_date) AS last_payment FROM Payment GROUP BY Mem_ID
    ) AS p ON m.Mem_ID = p.Mem_ID
    SET m.Member_Status = 'Active'
    WHERE p.last_payment >= DATE_SUB(CURDATE(), INTERVAL 31 DAY);

    -- Set all other members to 'Inactive'
    UPDATE Member m LEFT JOIN (
        SELECT Mem_ID, MAX(Payment_date) AS last_payment FROM Payment GROUP BY Mem_ID
    ) AS p ON m.Mem_ID = p.Mem_ID
    SET m.Member_Status = 'Inactive'
    WHERE p.last_payment IS NULL OR p.last_payment < DATE_SUB(CURDATE(), INTERVAL 31 DAY);
END$$
DELIMITER ;

