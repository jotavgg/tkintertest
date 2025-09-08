# Copilot Instructions: Tkinter Academic System (Functional Prototype)

## 1. Project Overview

You are an expert Python developer specializing in desktop applications. Your task is to generate the code for a functional prototype of an "Academic Collaboration System" using the **Tkinter** library.

This application is a practical demonstration for a university project (P.I.M.). The full project is documented as a complete web system, but this deliverable is a simplified desktop app to prove the core business logic.

## 2. Core Technologies

- **GUI Framework:** Python's built-in `tkinter` library.
- **Database:** Python's built-in `sqlite3` library. No external database server is needed.
- **Data Import:** `pandas` and `openpyxl` for Excel file processing.
- **C Module Integration:** Python's `subprocess` module to call an external C executable.

## 3. Application Structure (Multi-Frame Tkinter App)

The application should be structured in a single Python file (`main.py`) using a multi-frame approach to simulate different pages.

- Create a main application class, e.g., `App(tk.Tk)`.
- This class will manage a container frame. Different "page" frames (Login, Teacher Dashboard, etc.) will be raised into view within this container.
- Implement a `show_frame(frame_class)` method in the main class to switch between frames.
- All user roles and data will be stored and manipulated in an SQLite database file (`academic_system.db`).

## 4. Database Schema (SQLite)

Generate a function `setup_database()` that connects to `academic_system.db` and creates the following tables if they don't exist. This function should be called once when the application starts.

- **`users` table:**
  - `id` (INTEGER PRIMARY KEY AUTOINCREMENT)
  - `username` (TEXT UNIQUE NOT NULL)
  - `password` (TEXT NOT NULL) -- For simplicity, we can store plain text or use a simple hash.
  - `first_name` (TEXT)
  - `last_name` (TEXT)
  - `email` (TEXT)
  - `role` (TEXT NOT NULL) -- Will store "STUDENT", "TEACHER", etc.

- **`courses` table:**
  - `id` (INTEGER PRIMARY KEY AUTOINCREMENT)
  - `name` (TEXT NOT NULL)
  - `teacher_id` (INTEGER, FOREIGN KEY REFERENCES users(id))

- **`enrollments` table (Many-to-Many relationship between users and courses):**
  - `user_id` (INTEGER, FOREIGN KEY REFERENCES users(id))
  - `course_id` (INTEGER, FOREIGN KEY REFERENCES courses(id))
  - PRIMARY KEY (user_id, course_id)

- **`assignments` and `submissions` tables:** (Similar structure, linking to courses and users).

## 5. Core Functionality (Tkinter Screens/Frames)

Generate a class for each of the following frames, inheriting from `tk.Frame`.

### 5.1. Login Screen (`LoginFrame`)
- Widgets: Labels and Entry boxes for "Username" and "Password", and a "Login" Button.
- Logic: The button's command will call a function that queries the `users` table. If the user is valid, it should store the user's ID and role globally (or in the App class) and then call `app.show_frame()` to navigate to the correct dashboard based on the user's role.

### 5.2. Teacher Dashboard (`TeacherFrame`)
- This frame should be shown after a teacher logs in.
- **Widgets:**
  - A `ttk.Combobox` to select one of their courses.
  - A `ttk.Treeview` or `tk.Listbox` to display students enrolled in the selected course.
  - Buttons for: "Enter Grades," "Search Students," and "View At-Risk Students."
- **Logic:**
  - When a course is selected, populate the student list.
  - "Enter Grades" should open a new `Toplevel` window for grade entry.
  - "View At-Risk Students" will trigger the AI feature logic.

### 5.3. Student Dashboard (`StudentFrame`)
- This frame should be shown after a student logs in.
- **Widgets:**
  - A `ttk.Treeview` to display their enrolled courses and current grades.
  - A `tk.Listbox` for upcoming assignment deadlines.

### 5.4. Other Role Dashboards
- Create placeholder frames for `CoordinatorFrame`, `SecretaryFrame`, and `DirectorFrame` with basic labels and buttons corresponding to their main functions (e.g., a "Manage Student Info" button for the Secretary).

## 6. Feature-Specific Instructions

### 6.1. Excel Data Import (Secretary/Director Feature)
- In the `SecretaryFrame` or `DirectorFrame`, add a button "Import Students from Excel".
- This button's command will call a function that:
  1. Uses `tkinter.filedialog.askopenfilename()` to let the user select an `.xlsx` file.
  2. If a file is selected, it uses `pandas.read_excel()` to process the file.
  3. The function then iterates through the data and executes `INSERT` or `UPDATE` SQL commands on the `users` table via `sqlite3`.
  4. Show a `tkinter.messagebox.showinfo()` with a success message.

### 6.2. C Module Integration (Secretary/Director Feature)
- In the `SecretaryFrame` or `DirectorFrame`, add a button "Register Student (C Module)".
- This button opens a `Toplevel` window with a simple form for a new student's name and email.
- The form's "Submit" button will call a Python function that:
  1. Gets the data from the form's entry fields.
  2. Uses `subprocess.run(['./c_module/student_manager', 'create', name, email], capture_output=True, text=True)` to execute the pre-compiled C program.
  3. Displays the result from the C program's output in a `messagebox`.

### 6.3. AI Feature (Teacher/Coordinator Feature)
- In the `TeacherFrame`, the "View At-Risk Students" button will call a function that:
  1. Queries the SQLite database to get all students and their average grades for a selected course.
  2. Uses Python logic to create a list of students whose average grade is below a threshold (e.g., 6.0).
  3. Displays the names of these students in a `messagebox` or a dedicated `tk.Label`.

## 7. Final Goal

The goal is to generate a single-file Python script (`main.py`) that creates a functional Tkinter application. The application must connect to an SQLite database, demonstrate the core logic for different user roles, and correctly integrate with both a C executable and the Pandas library for Excel import, all within the Tkinter GUI.