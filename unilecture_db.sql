CREATE DATABASE unilecture_db;
USE unilecture_db;

CREATE TABLE lectures (
    id INT AUTO_INCREMENT PRIMARY KEY,
    course_name VARCHAR(255) NOT NULL,
    topic VARCHAR(255),
    lecture_date DATE NOT NULL,
    lecture_time TIME NOT NULL,
    notification_sent BOOLEAN DEFAULT FALSE
);
USE unilecture_db;

-- Clear existing data (optional, but good for fresh start)
-- DELETE FROM lectures;
-- ALTER TABLE lectures AUTO_INCREMENT = 1;

-- Insert sample lecture data
INSERT INTO lectures (course_name, topic, lecture_date, lecture_time, notification_sent) VALUES
('Introduction to Programming', 'Variables and Data Types', '2025-07-24', '10:00:00', FALSE),
('Calculus I', 'Limits and Continuity', '2025-07-24', '14:30:00', FALSE),
('Linear Algebra', 'Vector Spaces', '2025-07-25', '09:00:00', FALSE),
('Data Structures', 'Linked Lists', '2025-07-25', '13:00:00', FALSE),
('Operating Systems', 'Process Management', '2025-07-26', '11:00:00', FALSE),
('Database Systems', 'SQL Joins', '2025-07-26', '16:00:00', FALSE),
('Web Development', 'Frontend Basics (HTML/CSS)', '2025-07-27', '09:30:00', FALSE),
('Artificial Intelligence', 'Machine Learning Intro', '2025-07-27', '15:00:00', FALSE),
('Networking Fundamentals', 'TCP/IP Model', '2025-07-28', '10:00:00', FALSE),
('Software Engineering', 'Agile Methodologies', '2025-07-28', '14:00:00', FALSE);

-- Optional: Add a lecture for today that might be upcoming soon for testing notifications
-- Adjust the time below to be a few minutes in the future from when you run this.
-- For example, if it's 11:15 AM now, set it to '11:20:00'
-- To make this work, ensure your system clock is accurate.
INSERT INTO lectures (course_name, topic, lecture_date, lecture_time, notification_sent) VALUES
('Urgent Test Lecture', 'Testing Notification System', CURDATE(), ADDTIME(CURTIME(), '00:05:00'), FALSE);

-- Verify the data
SELECT * FROM lectures;