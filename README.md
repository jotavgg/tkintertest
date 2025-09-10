# Academic Collaboration System - Tkinter Prototype

## Overview
This is a functional desktop application prototype for an Academic Collaboration System built using Python's Tkinter library. It demonstrates core business logic for a university management system with different user roles and features.

## Features

### Multi-Role Authentication System
- **Teacher Dashboard**: Course management, grade entry, student search, at-risk student identification
- **Student Dashboard**: View enrolled courses, grades, and assignment deadlines
- **Coordinator Dashboard**: Academic program management (placeholder functions)
- **Secretary Dashboard**: Excel data import, C module integration for student registration
- **Director Dashboard**: Institutional analytics, report generation (placeholder functions)

### Core Functionality
1. **SQLite Database Integration**: Stores users, courses, enrollments, assignments, and submissions
2. **Excel Data Import**: Import student data from Excel files using pandas and openpyxl
3. **C Module Integration**: Simulated integration with external C programs for student management
4. **AI Feature**: Identifies at-risk students based on grade thresholds

## Installation & Setup

### Prerequisites
- Python 3.7 or higher
- The following packages are automatically installed:
  - pandas
  - openpyxl
  - sqlite3 (built-in)
  - tkinter (built-in)

### Running the Application
1. Navigate to the project directory
2. Run the application:
   ```bash
   python main.py
   ```

## Sample Login Credentials

| Role | Username | Password |
|------|----------|----------|
| Teacher | teacher1 | pass123 |
| Student | student1 | pass123 |
| Student | student2 | pass123 |
| Coordinator | coordinator1 | pass123 |
| Secretary | secretary1 | pass123 |
| Director | director1 | pass123 |

## Database Schema

The application automatically creates an SQLite database (`academic_system.db`) with the following tables:

- **users**: User accounts with roles (TEACHER, STUDENT, COORDINATOR, SECRETARY, DIRECTOR)
- **courses**: Academic courses linked to teachers
- **enrollments**: Many-to-many relationship between users and courses
- **assignments**: Course assignments
- **submissions**: Student submissions with grades

## Testing Features

### Excel Import (Secretary/Director)
1. Log in as `secretary1` or `director1`
2. Click "Import Students from Excel"
3. Select the provided `sample_students.xlsx` file
4. The system will import the student data into the database

### At-Risk Student Identification (Teacher)
1. Log in as `teacher1`
2. Select a course from the dropdown
3. Click "View At-Risk Students"
4. The system will show students with average grades below 6.0

### C Module Integration (Secretary/Director)
1. Log in as `secretary1` or `director1`
2. Click "Register Student (C Module)"
3. Fill in **all required information**: First Name, Last Name, Username, Password, and Email
4. **Optionally select courses** to enroll the student in using the checkboxes
5. The system simulates calling an external C program for registration
6. The new student can immediately log in with the provided credentials

### Student List Management (Teachers/Secretaries)
1. **Teachers**: 
   - Use the "Refresh Students" button to update the student list after new registrations
   - Use "Show All Students" to view all students regardless of course enrollment
   - Select a specific course to view only students enrolled in that course
2. **Secretaries**: Use "View All Students" to see a comprehensive list of all registered students
3. **Secretaries**: Use "Manage Student Records" for basic student record management

### Student Search (Teachers)
1. Log in as a teacher
2. Click "Search Students"
3. Enter part of a student's first or last name
4. Press Enter or click "Search" to find matching students
5. Results show student names and email addresses (passwords are not displayed for security)

### Secretary Functions (Fully Implemented)
1. **Process Enrollments**: 
   - Select a student and enroll them in multiple courses
   - View current enrollments for each student
   - Prevent duplicate enrollments
2. **Generate Student Reports**:
   - Create enrollment reports, academic performance reports, contact lists, or complete summaries
   - Export reports to CSV files or display in-window
   - Multiple report formats available

### Course Content Management (Teachers)
1. **Create Assignment**:
   - Create assignments with title, description, due date, and point values
   - Select assignment types (homework, quiz, project, exam)
   - Assignments are stored in the database
2. **Course Materials**:
   - Manage syllabus, lessons, and resources
   - Tabbed interface for different content types
   - Add custom lessons and course materials
3. **View Submissions**:
   - View student submissions for assignments
   - Grade submissions with numerical scores and feedback
   - Track submission status (submitted, missing, graded)

## File Structure

```
tkintertest/
├── main.py                 # Main application file
├── academic_system.db      # SQLite database (created automatically)
├── sample_students.xlsx    # Sample Excel file for testing
├── sample_students.csv     # Alternative CSV format
├── github/
│   └── copilot-instructions.md  # Project specifications
└── README.md              # This file
```

## Key Fixes and Improvements

### Recent Updates (Fixed Issues)
1. **Complete Student Registration**: C Module registration now collects all required fields (First Name, Last Name, Username, Password, Email)
2. **Course Enrollment During Registration**: Students can now be enrolled in courses during the registration process
3. **Student List Refresh**: Teachers can now refresh student lists to see newly registered students
4. **Show All Students Feature**: Teachers can view all students regardless of course enrollment status
5. **Fixed Search Function**: Student search now works properly and doesn't expose password information
6. **Secretary Functions Implemented**: All placeholder functions now have full implementations
7. **Course Content Management**: Teachers can create assignments, manage materials, and grade submissions
8. **Student Reports System**: Generate and export comprehensive student reports
9. **Enrollment Management**: Process student course enrollments with validation
10. **Enhanced UI**: Improved button layouts and window designs throughout the application

## Key Implementation Details

### Multi-Frame Architecture
- Uses a container frame approach where different "pages" (frames) are stacked
- The `App.show_frame()` method switches between different user role dashboards
- Each frame inherits from `tk.Frame` and implements its own interface

### Database Operations
- All database operations use parameterized queries to prevent SQL injection
- Database connection is opened and closed for each operation
- Sample data is automatically inserted on first run

### Error Handling
- Comprehensive try-catch blocks for database operations
- User-friendly error messages using `messagebox`
- Input validation for forms and data entry

## Technical Specifications

- **GUI Framework**: Python Tkinter (built-in)
- **Database**: SQLite3 (built-in)
- **Data Processing**: Pandas + OpenPyXL for Excel handling
- **External Integration**: Subprocess module for C program simulation
- **Architecture**: Single-file application with multi-frame design

## Development Notes

This prototype demonstrates:
1. Complete user authentication and role-based access control
2. Database design and operations for academic management
3. File import/export capabilities
4. External system integration patterns
5. AI/analytics features for educational insights

The application is designed as a functional proof-of-concept for a larger web-based academic collaboration system, showcasing core business logic in a desktop environment.

## Troubleshooting

### Common Issues
1. **Import Error**: Ensure pandas and openpyxl are installed
2. **Database Error**: Delete `academic_system.db` to reset the database
3. **Excel Import Issues**: Ensure Excel file has required columns: username, first_name, last_name, email

### Reset Application
To reset the application completely:
1. Delete `academic_system.db`
2. Restart the application
3. Fresh sample data will be created automatically

## Future Enhancements
- Real C module compilation and integration
- Advanced reporting with charts and graphs
- Email notification system
- Assignment submission handling
- Grade book export functionality
- Advanced search and filtering options
