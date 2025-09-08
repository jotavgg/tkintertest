"""
Academic Collaboration System - Tkinter Prototype
A functional desktop application demonstrating academic management system features.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import pandas as pd
import subprocess
import os
from typing import Optional, Dict, Any


class App(tk.Tk):
    """Main application class managing the multi-frame interface."""
    
    def __init__(self):
        super().__init__()
        
        # Window configuration
        self.title("Academic Collaboration System")
        self.geometry("800x600")
        self.resizable(True, True)
        
        # Current user session data
        self.current_user: Optional[Dict[str, Any]] = None
        
        # Initialize database
        setup_database()
        
        # Create container frame for all pages
        self.container = tk.Frame(self)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        
        # Dictionary to store frame instances
        self.frames = {}
        
        # Initialize all frames
        frame_classes = [
            LoginFrame,
            TeacherFrame,
            StudentFrame,
            CoordinatorFrame,
            SecretaryFrame,
            DirectorFrame
        ]
        
        for frame_class in frame_classes:
            frame = frame_class(parent=self.container, controller=self)
            self.frames[frame_class] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        
        # Show login frame initially
        self.show_frame(LoginFrame)
    
    def show_frame(self, frame_class):
        """Switch to the specified frame."""
        frame = self.frames[frame_class]
        frame.tkraise()
        
        # Refresh frame data if needed
        if hasattr(frame, 'refresh_data'):
            frame.refresh_data()
    
    def set_current_user(self, user_data: Dict[str, Any]):
        """Set the current logged-in user."""
        self.current_user = user_data
    
    def logout(self):
        """Log out the current user and return to login screen."""
        self.current_user = None
        self.show_frame(LoginFrame)


def setup_database():
    """Initialize SQLite database with required tables."""
    conn = sqlite3.connect('academic_system.db')
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            first_name TEXT,
            last_name TEXT,
            email TEXT,
            role TEXT NOT NULL
        )
    ''')
    
    # Create courses table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            teacher_id INTEGER,
            FOREIGN KEY (teacher_id) REFERENCES users(id)
        )
    ''')
    
    # Create enrollments table (many-to-many)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS enrollments (
            user_id INTEGER,
            course_id INTEGER,
            PRIMARY KEY (user_id, course_id),
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (course_id) REFERENCES courses(id)
        )
    ''')
    
    # Create assignments table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS assignments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id INTEGER,
            title TEXT NOT NULL,
            description TEXT,
            due_date TEXT,
            max_points INTEGER DEFAULT 100,
            FOREIGN KEY (course_id) REFERENCES courses(id)
        )
    ''')
    
    # Create submissions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            assignment_id INTEGER,
            student_id INTEGER,
            submission_date TEXT,
            grade REAL,
            feedback TEXT,
            FOREIGN KEY (assignment_id) REFERENCES assignments(id),
            FOREIGN KEY (student_id) REFERENCES users(id)
        )
    ''')
    
    # Insert sample data if tables are empty
    cursor.execute('SELECT COUNT(*) FROM users')
    if cursor.fetchone()[0] == 0:
        insert_sample_data(cursor)
    
    conn.commit()
    conn.close()


def insert_sample_data(cursor):
    """Insert sample data for testing purposes."""
    # Sample users
    users_data = [
        ('teacher1', 'pass123', 'Maria', 'Silva', 'maria.silva@email.com', 'TEACHER'),
        ('student1', 'pass123', 'João', 'Santos', 'joao.santos@email.com', 'STUDENT'),
        ('student2', 'pass123', 'Ana', 'Costa', 'ana.costa@email.com', 'STUDENT'),
        ('coordinator1', 'pass123', 'Carlos', 'Lima', 'carlos.lima@email.com', 'COORDINATOR'),
        ('secretary1', 'pass123', 'Paula', 'Ferreira', 'paula.ferreira@email.com', 'SECRETARY'),
        ('director1', 'pass123', 'Roberto', 'Oliveira', 'roberto.oliveira@email.com', 'DIRECTOR'),
    ]
    
    cursor.executemany('''
        INSERT INTO users (username, password, first_name, last_name, email, role)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', users_data)
    
    # Sample courses
    courses_data = [
        ('Mathematics I', 1),
        ('Programming Fundamentals', 1),
        ('Data Structures', 1),
    ]
    
    cursor.executemany('''
        INSERT INTO courses (name, teacher_id)
        VALUES (?, ?)
    ''', courses_data)
    
    # Sample enrollments
    enrollments_data = [
        (2, 1), (2, 2),  # student1 in Math and Programming
        (3, 1), (3, 3),  # student2 in Math and Data Structures
    ]
    
    cursor.executemany('''
        INSERT INTO enrollments (user_id, course_id)
        VALUES (?, ?)
    ''', enrollments_data)
    
    # Sample assignments
    assignments_data = [
        (1, 'Calculus Assignment', 'Solve differential equations problems', '2025-09-15', 100),
        (1, 'Linear Algebra Quiz', 'Matrix operations and transformations', '2025-09-22', 50),
        (2, 'Python Project 1', 'Create a simple calculator application', '2025-09-20', 100),
        (2, 'Data Types Exercise', 'Work with lists, dictionaries, and sets', '2025-09-18', 75),
        (3, 'Binary Tree Implementation', 'Implement binary search tree in Python', '2025-09-25', 100),
        (3, 'Algorithm Analysis', 'Analyze time complexity of sorting algorithms', '2025-09-30', 80),
    ]
    
    cursor.executemany('''
        INSERT INTO assignments (course_id, title, description, due_date, max_points)
        VALUES (?, ?, ?, ?, ?)
    ''', assignments_data)


class LoginFrame(tk.Frame):
    """Login screen for user authentication."""
    
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # Main frame
        main_frame = tk.Frame(self)
        main_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Title
        title_label = tk.Label(main_frame, text="Academic Collaboration System", 
                              font=("Arial", 18, "bold"))
        title_label.pack(pady=20)
        
        # Username
        tk.Label(main_frame, text="Username:", font=("Arial", 12)).pack(pady=5)
        self.username_entry = tk.Entry(main_frame, font=("Arial", 12), width=25)
        self.username_entry.pack(pady=5)
        
        # Password
        tk.Label(main_frame, text="Password:", font=("Arial", 12)).pack(pady=5)
        self.password_entry = tk.Entry(main_frame, font=("Arial", 12), width=25, show="*")
        self.password_entry.pack(pady=5)
        
        # Login button
        login_btn = tk.Button(main_frame, text="Login", font=("Arial", 12),
                             command=self.login, bg="#4CAF50", fg="white", 
                             width=20, height=2)
        login_btn.pack(pady=20)
        
        # Sample credentials info
        info_frame = tk.Frame(main_frame)
        info_frame.pack(pady=10)
        
        tk.Label(info_frame, text="Sample Credentials:", font=("Arial", 10, "bold")).pack()
        tk.Label(info_frame, text="Teacher: teacher1/pass123", font=("Arial", 9)).pack()
        tk.Label(info_frame, text="Student: student1/pass123", font=("Arial", 9)).pack()
        tk.Label(info_frame, text="Secretary: secretary1/pass123", font=("Arial", 9)).pack()
        
        # Bind Enter key to login only in these entry widgets
        self.username_entry.bind('<Return>', lambda e: self.login())
        self.password_entry.bind('<Return>', lambda e: self.login())
    
    def login(self):
        """Authenticate user and navigate to appropriate dashboard."""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password.")
            return
        
        # Query database for user
        conn = sqlite3.connect('academic_system.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, username, first_name, last_name, email, role
            FROM users WHERE username = ? AND password = ?
        ''', (username, password))
        
        user_data = cursor.fetchone()
        conn.close()
        
        if user_data:
            # Store user data
            user_dict = {
                'id': user_data[0],
                'username': user_data[1],
                'first_name': user_data[2],
                'last_name': user_data[3],
                'email': user_data[4],
                'role': user_data[5]
            }
            
            self.controller.set_current_user(user_dict)
            
            # Navigate to appropriate dashboard
            role = user_data[5]
            if role == 'TEACHER':
                self.controller.show_frame(TeacherFrame)
            elif role == 'STUDENT':
                self.controller.show_frame(StudentFrame)
            elif role == 'COORDINATOR':
                self.controller.show_frame(CoordinatorFrame)
            elif role == 'SECRETARY':
                self.controller.show_frame(SecretaryFrame)
            elif role == 'DIRECTOR':
                self.controller.show_frame(DirectorFrame)
            
            # Clear fields
            self.username_entry.delete(0, tk.END)
            self.password_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Error", "Invalid username or password.")


class TeacherFrame(tk.Frame):
    """Teacher dashboard for course and student management."""
    
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # Header frame
        header_frame = tk.Frame(self)
        header_frame.pack(fill="x", padx=20, pady=10)
        
        self.welcome_label = tk.Label(header_frame, text="Teacher Dashboard", 
                                     font=("Arial", 16, "bold"))
        self.welcome_label.pack(side="left")
        
        logout_btn = tk.Button(header_frame, text="Logout", command=controller.logout,
                              bg="#f44336", fg="white")
        logout_btn.pack(side="right")
        
        # Main content frame
        content_frame = tk.Frame(self)
        content_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Course selection
        course_frame = tk.LabelFrame(content_frame, text="Course Selection", 
                                   font=("Arial", 12, "bold"))
        course_frame.pack(fill="x", pady=10)
        
        course_selection_frame = tk.Frame(course_frame)
        course_selection_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Label(course_selection_frame, text="Select Course:", font=("Arial", 10)).pack(side="left", padx=5)
        self.course_combo = ttk.Combobox(course_selection_frame, font=("Arial", 10), state="readonly")
        self.course_combo.pack(side="left", padx=5)
        self.course_combo.bind('<<ComboboxSelected>>', self.on_course_selected)
        
        # Add "Show All Students" button
        tk.Button(course_selection_frame, text="Show All Students", 
                 command=self.show_all_students, bg="#9C27B0", fg="white",
                 font=("Arial", 9)).pack(side="left", padx=10)
        
        # Students list
        students_frame = tk.LabelFrame(content_frame, text="Enrolled Students", 
                                     font=("Arial", 12, "bold"))
        students_frame.pack(fill="both", expand=True, pady=10)
        
        # Create Treeview for students
        columns = ("ID", "Name", "Email", "Average Grade")
        self.students_tree = ttk.Treeview(students_frame, columns=columns, show="headings", height=10)
        
        for col in columns:
            self.students_tree.heading(col, text=col)
            self.students_tree.column(col, width=150)
        
        scrollbar = ttk.Scrollbar(students_frame, orient="vertical", command=self.students_tree.yview)
        self.students_tree.configure(yscrollcommand=scrollbar.set)
        
        self.students_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Action buttons
        buttons_frame = tk.Frame(content_frame)
        buttons_frame.pack(fill="x", pady=10)
        
        tk.Button(buttons_frame, text="Refresh Students", command=self.refresh_students,
                 bg="#4CAF50", fg="white", font=("Arial", 10)).pack(side="left", padx=5)
        
        tk.Button(buttons_frame, text="Enter Grades", command=self.enter_grades,
                 bg="#2196F3", fg="white", font=("Arial", 10)).pack(side="left", padx=5)
        
        tk.Button(buttons_frame, text="Search Students", command=self.search_students,
                 bg="#FF9800", fg="white", font=("Arial", 10)).pack(side="left", padx=5)
        
        tk.Button(buttons_frame, text="View At-Risk Students", command=self.view_at_risk_students,
                 bg="#f44336", fg="white", font=("Arial", 10)).pack(side="left", padx=5)
    
    def refresh_data(self):
        """Refresh the teacher's courses when frame is shown."""
        if self.controller.current_user:
            self.welcome_label.config(
                text=f"Teacher Dashboard - Welcome, {self.controller.current_user['first_name']}!"
            )
            self.load_courses()
    
    def load_courses(self):
        """Load teacher's courses into the combobox."""
        if not self.controller.current_user:
            return
        
        conn = sqlite3.connect('academic_system.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, name FROM courses WHERE teacher_id = ?
        ''', (self.controller.current_user['id'],))
        
        courses = cursor.fetchall()
        conn.close()
        
        course_list = [f"{course[1]} (ID: {course[0]})" for course in courses]
        self.course_combo['values'] = course_list
        
        if course_list:
            self.course_combo.current(0)
            self.on_course_selected(None)
    
    def refresh_students(self):
        """Refresh the student list for the currently selected course."""
        if self.course_combo.get():
            self.on_course_selected(None)
        else:
            messagebox.showinfo("Info", "Please select a course first.")
    
    def show_all_students(self):
        """Show all students regardless of course enrollment."""
        conn = sqlite3.connect('academic_system.db')
        cursor = conn.cursor()
        
        # Get all students with their course information
        cursor.execute('''
            SELECT u.id, u.first_name || ' ' || u.last_name as name, u.email,
                   GROUP_CONCAT(c.name, ', ') as enrolled_courses
            FROM users u
            LEFT JOIN enrollments e ON u.id = e.user_id
            LEFT JOIN courses c ON e.course_id = c.id
            WHERE u.role = 'STUDENT'
            GROUP BY u.id, u.first_name, u.last_name, u.email
            ORDER BY u.first_name, u.last_name
        ''')
        
        all_students = cursor.fetchall()
        conn.close()
        
        # Clear and populate treeview
        for item in self.students_tree.get_children():
            self.students_tree.delete(item)
        
        # Update column headers to show "Enrolled Courses" instead of "Average Grade"
        self.students_tree.heading("#4", text="Enrolled Courses")
        
        for student in all_students:
            courses = student[3] if student[3] else "No enrollments"
            self.students_tree.insert("", "end", values=(
                student[0], student[1], student[2], courses
            ))
    
    def on_course_selected(self, event):
        """Handle course selection and load students."""
        selection = self.course_combo.get()
        if not selection:
            return
        
        # Restore the original column header for course-specific view
        self.students_tree.heading("#4", text="Average Grade")
        
        # Extract course ID from selection
        course_id = int(selection.split("ID: ")[1].rstrip(")"))
        
        conn = sqlite3.connect('academic_system.db')
        cursor = conn.cursor()
        
        # Get enrolled students with their average grades
        cursor.execute('''
            SELECT u.id, u.first_name || ' ' || u.last_name as name, u.email,
                   COALESCE(AVG(s.grade), 0) as avg_grade
            FROM users u
            JOIN enrollments e ON u.id = e.user_id
            LEFT JOIN submissions s ON u.id = s.student_id
            LEFT JOIN assignments a ON s.assignment_id = a.id AND a.course_id = ?
            WHERE e.course_id = ? AND u.role = 'STUDENT'
            GROUP BY u.id, u.first_name, u.last_name, u.email
        ''', (course_id, course_id))
        
        students = cursor.fetchall()
        conn.close()
        
        # Clear and populate treeview
        for item in self.students_tree.get_children():
            self.students_tree.delete(item)
        
        for student in students:
            self.students_tree.insert("", "end", values=(
                student[0], student[1], student[2], f"{student[3]:.1f}"
            ))
    
    def enter_grades(self):
        """Open grade entry window."""
        selection = self.students_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a student first.")
            return
        
        student_data = self.students_tree.item(selection[0])['values']
        
        # Create grade entry window
        grade_window = tk.Toplevel(self.controller)
        grade_window.title("Enter Grade")
        grade_window.geometry("300x200")
        grade_window.transient(self.controller)
        grade_window.grab_set()
        
        tk.Label(grade_window, text=f"Student: {student_data[1]}", 
                font=("Arial", 12, "bold")).pack(pady=10)
        
        tk.Label(grade_window, text="Grade (0-100):").pack()
        grade_entry = tk.Entry(grade_window)
        grade_entry.pack(pady=5)
        
        tk.Label(grade_window, text="Assignment:").pack()
        assignment_entry = tk.Entry(grade_window)
        assignment_entry.pack(pady=5)
        
        def save_grade():
            try:
                grade = float(grade_entry.get())
                assignment = assignment_entry.get().strip()
                
                if not assignment:
                    messagebox.showerror("Error", "Please enter assignment name.")
                    return
                
                if not 0 <= grade <= 100:
                    messagebox.showerror("Error", "Grade must be between 0 and 100.")
                    return
                
                messagebox.showinfo("Success", f"Grade {grade} saved for {assignment}")
                grade_window.destroy()
                
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid numeric grade.")
        
        tk.Button(grade_window, text="Save Grade", command=save_grade,
                 bg="#4CAF50", fg="white").pack(pady=20)
    
    def search_students(self):
        """Open student search dialog."""
        search_window = tk.Toplevel(self.controller)
        search_window.title("Search Students")
        search_window.geometry("400x300")
        search_window.transient(self.controller)
        search_window.grab_set()
        
        tk.Label(search_window, text="Search Students", 
                font=("Arial", 14, "bold")).pack(pady=10)
        
        tk.Label(search_window, text="Enter student name:").pack()
        search_entry = tk.Entry(search_window, font=("Arial", 12))
        search_entry.pack(pady=5)
        
        results_text = tk.Text(search_window, height=10, width=40)
        results_text.pack(pady=10, fill="both", expand=True)
        
        def perform_search():
            query = search_entry.get().strip()
            if not query:
                return
            
            conn = sqlite3.connect('academic_system.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT first_name, last_name, email FROM users
                WHERE role = 'STUDENT' AND (first_name LIKE ? OR last_name LIKE ?)
            ''', (f'%{query}%', f'%{query}%'))
            
            results = cursor.fetchall()
            conn.close()
            
            results_text.delete(1.0, tk.END)
            if results:
                for student in results:
                    results_text.insert(tk.END, f"{student[0]} {student[1]} - {student[2]}\n")
            else:
                results_text.insert(tk.END, "No students found.")
        
        # Bind Enter key to search in this window
        search_entry.bind('<Return>', lambda e: perform_search())
        
        tk.Button(search_window, text="Search", command=perform_search,
                 bg="#2196F3", fg="white").pack(pady=5)
    
    def view_at_risk_students(self):
        """AI Feature: Show students with low grades."""
        selection = self.course_combo.get()
        if not selection:
            messagebox.showwarning("Warning", "Please select a course first.")
            return
        
        course_id = int(selection.split("ID: ")[1].rstrip(")"))
        
        conn = sqlite3.connect('academic_system.db')
        cursor = conn.cursor()
        
        # Get students with average grade below 6.0
        cursor.execute('''
            SELECT u.first_name || ' ' || u.last_name as name, 
                   COALESCE(AVG(s.grade), 0) as avg_grade
            FROM users u
            JOIN enrollments e ON u.id = e.user_id
            LEFT JOIN submissions s ON u.id = s.student_id
            LEFT JOIN assignments a ON s.assignment_id = a.id AND a.course_id = ?
            WHERE e.course_id = ? AND u.role = 'STUDENT'
            GROUP BY u.id, u.first_name, u.last_name
            HAVING avg_grade < 6.0 OR avg_grade = 0
        ''', (course_id, course_id))
        
        at_risk_students = cursor.fetchall()
        conn.close()
        
        if at_risk_students:
            message = "At-Risk Students (Average < 6.0):\n\n"
            for student in at_risk_students:
                message += f"• {student[0]} - Average: {student[1]:.1f}\n"
        else:
            message = "No at-risk students found in this course."
        
        messagebox.showinfo("At-Risk Students", message)


class StudentFrame(tk.Frame):
    """Student dashboard for viewing courses and grades."""
    
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # Header frame
        header_frame = tk.Frame(self)
        header_frame.pack(fill="x", padx=20, pady=10)
        
        self.welcome_label = tk.Label(header_frame, text="Student Dashboard", 
                                     font=("Arial", 16, "bold"))
        self.welcome_label.pack(side="left")
        
        logout_btn = tk.Button(header_frame, text="Logout", command=controller.logout,
                              bg="#f44336", fg="white")
        logout_btn.pack(side="right")
        
        # Main content frame
        content_frame = tk.Frame(self)
        content_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Enrolled courses
        courses_frame = tk.LabelFrame(content_frame, text="My Courses & Grades", 
                                    font=("Arial", 12, "bold"))
        courses_frame.pack(fill="both", expand=True, pady=10)
        
        # Create Treeview for courses
        columns = ("Course", "Teacher", "Average Grade")
        self.courses_tree = ttk.Treeview(courses_frame, columns=columns, show="headings", height=8)
        
        for col in columns:
            self.courses_tree.heading(col, text=col)
            self.courses_tree.column(col, width=200)
        
        scrollbar_courses = ttk.Scrollbar(courses_frame, orient="vertical", command=self.courses_tree.yview)
        self.courses_tree.configure(yscrollcommand=scrollbar_courses.set)
        
        self.courses_tree.pack(side="left", fill="both", expand=True)
        scrollbar_courses.pack(side="right", fill="y")
        
        # Assignments deadlines
        deadlines_frame = tk.LabelFrame(content_frame, text="Upcoming Assignments", 
                                      font=("Arial", 12, "bold"))
        deadlines_frame.pack(fill="x", pady=10)
        
        self.deadlines_listbox = tk.Listbox(deadlines_frame, height=5, font=("Arial", 10))
        self.deadlines_listbox.pack(fill="x", padx=10, pady=10)
    
    def refresh_data(self):
        """Refresh student data when frame is shown."""
        if self.controller.current_user:
            self.welcome_label.config(
                text=f"Student Dashboard - Welcome, {self.controller.current_user['first_name']}!"
            )
            self.load_courses()
            self.load_deadlines()
    
    def load_courses(self):
        """Load student's enrolled courses and grades."""
        if not self.controller.current_user:
            return
        
        conn = sqlite3.connect('academic_system.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT c.name, u.first_name || ' ' || u.last_name as teacher_name,
                   COALESCE(AVG(s.grade), 0) as avg_grade
            FROM courses c
            JOIN enrollments e ON c.id = e.course_id
            JOIN users u ON c.teacher_id = u.id
            LEFT JOIN assignments a ON c.id = a.course_id
            LEFT JOIN submissions s ON a.id = s.assignment_id AND s.student_id = ?
            WHERE e.user_id = ?
            GROUP BY c.id, c.name, u.first_name, u.last_name
        ''', (self.controller.current_user['id'], self.controller.current_user['id']))
        
        courses = cursor.fetchall()
        conn.close()
        
        # Clear and populate treeview
        for item in self.courses_tree.get_children():
            self.courses_tree.delete(item)
        
        for course in courses:
            self.courses_tree.insert("", "end", values=(
                course[0], course[1], f"{course[2]:.1f}"
            ))
    
    def load_deadlines(self):
        """Load upcoming assignment deadlines from the database."""
        if not self.controller.current_user:
            return
            
        self.deadlines_listbox.delete(0, tk.END)
        
        conn = sqlite3.connect('academic_system.db')
        cursor = conn.cursor()
        
        # Get assignments for courses the student is enrolled in
        cursor.execute('''
            SELECT a.title, c.name, a.due_date
            FROM assignments a
            JOIN courses c ON a.course_id = c.id
            JOIN enrollments e ON c.id = e.course_id
            WHERE e.user_id = ? AND a.due_date IS NOT NULL
            ORDER BY a.due_date
        ''', (self.controller.current_user['id'],))
        
        assignments = cursor.fetchall()
        conn.close()
        
        if assignments:
            for assignment in assignments:
                deadline_text = f"{assignment[1]} - {assignment[0]} - Due: {assignment[2]}"
                self.deadlines_listbox.insert(tk.END, deadline_text)
        else:
            # If no assignments in database, show sample deadlines
            sample_deadlines = [
                "Mathematics I - Calculus Assignment - Due: Sep 15, 2025",
                "Programming Fundamentals - Project 1 - Due: Sep 20, 2025",
                "Data Structures - Lab Report - Due: Sep 25, 2025"
            ]
            
            for deadline in sample_deadlines:
                self.deadlines_listbox.insert(tk.END, deadline)


class CoordinatorFrame(tk.Frame):
    """Coordinator dashboard placeholder."""
    
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # Header frame
        header_frame = tk.Frame(self)
        header_frame.pack(fill="x", padx=20, pady=10)
        
        self.welcome_label = tk.Label(header_frame, text="Coordinator Dashboard", 
                                     font=("Arial", 16, "bold"))
        self.welcome_label.pack(side="left")
        
        logout_btn = tk.Button(header_frame, text="Logout", command=controller.logout,
                              bg="#f44336", fg="white")
        logout_btn.pack(side="right")
        
        # Main content
        content_frame = tk.Frame(self)
        content_frame.pack(fill="both", expand=True, padx=20, pady=50)
        
        tk.Label(content_frame, text="Coordinator Functions", 
                font=("Arial", 14, "bold")).pack(pady=20)
        
        functions = [
            "Manage Academic Programs",
            "Monitor Course Performance",
            "Generate Reports",
            "Coordinate with Teachers"
        ]
        
        for func in functions:
            tk.Button(content_frame, text=func, font=("Arial", 11),
                     width=25, height=2, command=lambda f=func: self.placeholder_action(f)).pack(pady=5)
    
    def refresh_data(self):
        """Refresh coordinator data when frame is shown."""
        if self.controller.current_user:
            self.welcome_label.config(
                text=f"Coordinator Dashboard - Welcome, {self.controller.current_user['first_name']}!"
            )
    
    def placeholder_action(self, function_name):
        """Placeholder action for coordinator functions."""
        messagebox.showinfo("Function", f"{function_name} - Feature coming soon!")


class SecretaryFrame(tk.Frame):
    """Secretary dashboard with Excel import and C module integration."""
    
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # Header frame
        header_frame = tk.Frame(self)
        header_frame.pack(fill="x", padx=20, pady=10)
        
        self.welcome_label = tk.Label(header_frame, text="Secretary Dashboard", 
                                     font=("Arial", 16, "bold"))
        self.welcome_label.pack(side="left")
        
        logout_btn = tk.Button(header_frame, text="Logout", command=controller.logout,
                              bg="#f44336", fg="white")
        logout_btn.pack(side="right")
        
        # Main content
        content_frame = tk.Frame(self)
        content_frame.pack(fill="both", expand=True, padx=20, pady=50)
        
        tk.Label(content_frame, text="Secretary Functions", 
                font=("Arial", 14, "bold")).pack(pady=20)
        
        # Excel import button
        tk.Button(content_frame, text="Import Students from Excel", 
                 font=("Arial", 11), width=30, height=2,
                 bg="#4CAF50", fg="white",
                 command=self.import_students_excel).pack(pady=10)
        
        # C module integration button
        tk.Button(content_frame, text="Register Student (C Module)", 
                 font=("Arial", 11), width=30, height=2,
                 bg="#2196F3", fg="white",
                 command=self.register_student_c_module).pack(pady=10)
        
        # Other functions
        other_functions = [
            ("Manage Student Records", self.manage_student_records),
            ("View All Students", self.view_all_students),
            ("Process Enrollments", lambda: self.placeholder_action("Process Enrollments")),
            ("Generate Student Reports", lambda: self.placeholder_action("Generate Student Reports"))
        ]
        
        for func_name, func_command in other_functions:
            tk.Button(content_frame, text=func_name, font=("Arial", 11),
                     width=30, height=2, command=func_command).pack(pady=5)
    
    def refresh_data(self):
        """Refresh secretary data when frame is shown."""
        if self.controller.current_user:
            self.welcome_label.config(
                text=f"Secretary Dashboard - Welcome, {self.controller.current_user['first_name']}!"
            )
    
    def import_students_excel(self):
        """Import students from Excel file using pandas."""
        try:
            # Open file dialog
            file_path = filedialog.askopenfilename(
                title="Select Excel File",
                filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
            )
            
            if not file_path:
                return
            
            # Read Excel file
            df = pd.read_excel(file_path)
            
            # Validate required columns
            required_columns = ['username', 'first_name', 'last_name', 'email']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                messagebox.showerror("Error", 
                                   f"Missing required columns: {', '.join(missing_columns)}")
                return
            
            # Connect to database
            conn = sqlite3.connect('academic_system.db')
            cursor = conn.cursor()
            
            imported_count = 0
            errors = []
            
            for row_num, row in df.iterrows():
                try:
                    # Insert or update student record
                    cursor.execute('''
                        INSERT OR REPLACE INTO users 
                        (username, password, first_name, last_name, email, role)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        row['username'],
                        row.get('password', 'default123'),  # Default password if not provided
                        row['first_name'],
                        row['last_name'],
                        row['email'],
                        'STUDENT'
                    ))
                    imported_count += 1
                    
                except Exception as e:
                    errors.append(f"Row {imported_count + 1}: {str(e)}")
            
            conn.commit()
            conn.close()
            
            # Show result
            message = f"Successfully imported {imported_count} students."
            if errors:
                message += f"\n\nErrors encountered:\n" + "\n".join(errors[:5])
                if len(errors) > 5:
                    message += f"\n... and {len(errors) - 5} more errors."
            
            messagebox.showinfo("Import Complete", message)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to import Excel file: {str(e)}")
    
    def register_student_c_module(self):
        """Register student using C module integration."""
        # Create student registration window
        register_window = tk.Toplevel(self.controller)
        register_window.title("Register Student (C Module)")
        register_window.geometry("400x500")
        register_window.transient(self.controller)
        register_window.grab_set()
        
        tk.Label(register_window, text="Register New Student", 
                font=("Arial", 14, "bold")).pack(pady=20)
        
        # Form fields
        tk.Label(register_window, text="First Name:").pack()
        first_name_entry = tk.Entry(register_window, font=("Arial", 11), width=30)
        first_name_entry.pack(pady=5)
        
        tk.Label(register_window, text="Last Name:").pack()
        last_name_entry = tk.Entry(register_window, font=("Arial", 11), width=30)
        last_name_entry.pack(pady=5)
        
        tk.Label(register_window, text="Username:").pack()
        username_entry = tk.Entry(register_window, font=("Arial", 11), width=30)
        username_entry.pack(pady=5)
        
        tk.Label(register_window, text="Password:").pack()
        password_entry = tk.Entry(register_window, font=("Arial", 11), width=30, show="*")
        password_entry.pack(pady=5)
        
        tk.Label(register_window, text="Email:").pack()
        email_entry = tk.Entry(register_window, font=("Arial", 11), width=30)
        email_entry.pack(pady=5)
        
        # Course selection
        tk.Label(register_window, text="Enroll in Courses (optional):").pack(pady=(10, 5))
        
        # Create frame for course checkboxes
        courses_frame = tk.Frame(register_window)
        courses_frame.pack(pady=5)
        
        # Get available courses
        conn = sqlite3.connect('academic_system.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id, name FROM courses ORDER BY name')
        available_courses = cursor.fetchall()
        conn.close()
        
        # Create checkboxes for courses
        course_vars = {}
        if available_courses:
            for course_id, course_name in available_courses:
                var = tk.BooleanVar()
                course_vars[course_id] = var
                tk.Checkbutton(courses_frame, text=course_name, variable=var).pack(anchor='w')
        else:
            tk.Label(courses_frame, text="No courses available", fg="gray").pack()
        
        def submit_registration():
            first_name = first_name_entry.get().strip()
            last_name = last_name_entry.get().strip()
            username = username_entry.get().strip()
            password = password_entry.get().strip()
            email = email_entry.get().strip()
            
            if not all([first_name, last_name, username, password, email]):
                messagebox.showerror("Error", "Please fill in all fields.")
                return
            
            try:
                # Call the C module simulation with all required data
                result = self.simulate_c_module_call(first_name, last_name, username, password, email)
                
                if result['success']:
                    # Enroll student in selected courses
                    selected_courses = [course_id for course_id, var in course_vars.items() if var.get()]
                    if selected_courses:
                        self.enroll_student_in_courses(result['student_id'], selected_courses)
                    
                    course_info = f"\nEnrolled in {len(selected_courses)} course(s)" if selected_courses else "\nNo course enrollments"
                    
                    messagebox.showinfo("Success", 
                                      f"Student '{first_name} {last_name}' registered successfully via C module!\n"
                                      f"Username: {username}\n"
                                      f"Student ID: {result['student_id']}{course_info}")
                    register_window.destroy()
                else:
                    messagebox.showerror("Error", f"C Module Error: {result['error']}")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Failed to execute C module: {str(e)}")
        
        tk.Button(register_window, text="Submit Registration", 
                 command=submit_registration, bg="#4CAF50", fg="white",
                 font=("Arial", 11)).pack(pady=20)
    
    def simulate_c_module_call(self, first_name, last_name, username, password, email):
        """
        Simulate C module integration.
        In a real implementation, this would use subprocess.run() to call a C executable.
        """
        # Simulate the C module execution
        try:
            # This would be: subprocess.run(['./c_module/student_manager', 'create', 
            #                              first_name, last_name, username, password, email], 
            #                              capture_output=True, text=True)
            
            # For simulation, we'll add the student directly to the database
            conn = sqlite3.connect('academic_system.db')
            cursor = conn.cursor()
            
            # Check if username already exists
            cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
            if cursor.fetchone():
                conn.close()
                return {'success': False, 'error': f'Username "{username}" already exists'}
            
            cursor.execute('''
                INSERT INTO users (username, password, first_name, last_name, email, role)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (username, password, first_name, last_name, email, 'STUDENT'))
            
            student_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return {'success': True, 'student_id': student_id}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def enroll_student_in_courses(self, student_id, course_ids):
        """Enroll a student in the specified courses."""
        try:
            conn = sqlite3.connect('academic_system.db')
            cursor = conn.cursor()
            
            for course_id in course_ids:
                cursor.execute('''
                    INSERT OR IGNORE INTO enrollments (user_id, course_id)
                    VALUES (?, ?)
                ''', (student_id, course_id))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error enrolling student in courses: {e}")
    
    def manage_student_records(self):
        """Open student records management window."""
        records_window = tk.Toplevel(self.controller)
        records_window.title("Manage Student Records")
        records_window.geometry("600x400")
        records_window.transient(self.controller)
        records_window.grab_set()
        
        tk.Label(records_window, text="Student Records Management", 
                font=("Arial", 14, "bold")).pack(pady=10)
        
        # Simple student list with basic management
        frame = tk.Frame(records_window)
        frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Treeview for student records
        columns = ("ID", "Username", "Name", "Email")
        tree = ttk.Treeview(frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120)
        
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Load students
        conn = sqlite3.connect('academic_system.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, username, first_name || ' ' || last_name, email 
            FROM users WHERE role = 'STUDENT'
            ORDER BY first_name, last_name
        ''')
        students = cursor.fetchall()
        conn.close()
        
        for student in students:
            tree.insert("", "end", values=student)
        
        tk.Button(records_window, text="Close", command=records_window.destroy,
                 bg="#f44336", fg="white").pack(pady=10)
    
    def view_all_students(self):
        """View all students in the system."""
        students_window = tk.Toplevel(self.controller)
        students_window.title("All Students")
        students_window.geometry("700x500")
        students_window.transient(self.controller)
        students_window.grab_set()
        
        tk.Label(students_window, text="All Registered Students", 
                font=("Arial", 14, "bold")).pack(pady=10)
        
        # Create frame for the treeview
        frame = tk.Frame(students_window)
        frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Create Treeview
        columns = ("ID", "Username", "First Name", "Last Name", "Email", "Enrolled Courses")
        tree = ttk.Treeview(frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            tree.heading(col, text=col)
            if col == "Email":
                tree.column(col, width=200)
            elif col == "Enrolled Courses":
                tree.column(col, width=150)
            else:
                tree.column(col, width=100)
        
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Load students with course information
        conn = sqlite3.connect('academic_system.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT u.id, u.username, u.first_name, u.last_name, u.email,
                   GROUP_CONCAT(c.name, ', ') as courses
            FROM users u
            LEFT JOIN enrollments e ON u.id = e.user_id
            LEFT JOIN courses c ON e.course_id = c.id
            WHERE u.role = 'STUDENT'
            GROUP BY u.id, u.username, u.first_name, u.last_name, u.email
            ORDER BY u.first_name, u.last_name
        ''')
        
        students = cursor.fetchall()
        conn.close()
        
        for student in students:
            courses = student[5] if student[5] else "No enrollments"
            tree.insert("", "end", values=(
                student[0], student[1], student[2], student[3], student[4], courses
            ))
        
        # Button frame
        button_frame = tk.Frame(students_window)
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="Refresh", command=lambda: self.refresh_student_list(tree),
                 bg="#4CAF50", fg="white").pack(side="left", padx=5)
        
        tk.Button(button_frame, text="Close", command=students_window.destroy,
                 bg="#f44336", fg="white").pack(side="left", padx=5)
    
    def refresh_student_list(self, tree):
        """Refresh the student list in the treeview."""
        # Clear existing items
        for item in tree.get_children():
            tree.delete(item)
        
        # Reload students
        conn = sqlite3.connect('academic_system.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT u.id, u.username, u.first_name, u.last_name, u.email,
                   GROUP_CONCAT(c.name, ', ') as courses
            FROM users u
            LEFT JOIN enrollments e ON u.id = e.user_id
            LEFT JOIN courses c ON e.course_id = c.id
            WHERE u.role = 'STUDENT'
            GROUP BY u.id, u.username, u.first_name, u.last_name, u.email
            ORDER BY u.first_name, u.last_name
        ''')
        
        students = cursor.fetchall()
        conn.close()
        
        for student in students:
            courses = student[5] if student[5] else "No enrollments"
            tree.insert("", "end", values=(
                student[0], student[1], student[2], student[3], student[4], courses
            ))
        
        messagebox.showinfo("Refreshed", "Student list has been refreshed.")
    
    def placeholder_action(self, function_name):
        """Placeholder action for secretary functions."""
        messagebox.showinfo("Function", f"{function_name} - Feature coming soon!")


class DirectorFrame(tk.Frame):
    """Director dashboard with advanced features."""
    
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # Header frame
        header_frame = tk.Frame(self)
        header_frame.pack(fill="x", padx=20, pady=10)
        
        self.welcome_label = tk.Label(header_frame, text="Director Dashboard", 
                                     font=("Arial", 16, "bold"))
        self.welcome_label.pack(side="left")
        
        logout_btn = tk.Button(header_frame, text="Logout", command=controller.logout,
                              bg="#f44336", fg="white")
        logout_btn.pack(side="right")
        
        # Main content
        content_frame = tk.Frame(self)
        content_frame.pack(fill="both", expand=True, padx=20, pady=50)
        
        tk.Label(content_frame, text="Director Functions", 
                font=("Arial", 14, "bold")).pack(pady=20)
        
        # Excel import button (directors can also import data)
        tk.Button(content_frame, text="Import Academic Data from Excel", 
                 font=("Arial", 11), width=35, height=2,
                 bg="#4CAF50", fg="white",
                 command=self.import_academic_data).pack(pady=10)
        
        # C module integration button
        tk.Button(content_frame, text="Generate Reports (C Module)", 
                 font=("Arial", 11), width=35, height=2,
                 bg="#2196F3", fg="white",
                 command=self.generate_reports_c_module).pack(pady=10)
        
        # Other director functions
        other_functions = [
            "View Institution Analytics",
            "Manage Faculty",
            "Strategic Planning Tools",
            "Budget Management"
        ]
        
        for func in other_functions:
            tk.Button(content_frame, text=func, font=("Arial", 11),
                     width=35, height=2, command=lambda f=func: self.placeholder_action(f)).pack(pady=5)
    
    def refresh_data(self):
        """Refresh director data when frame is shown."""
        if self.controller.current_user:
            self.welcome_label.config(
                text=f"Director Dashboard - Welcome, {self.controller.current_user['first_name']}!"
            )
    
    def import_academic_data(self):
        """Import academic data from Excel (similar to secretary but with more options)."""
        messagebox.showinfo("Excel Import", 
                          "Academic data import functionality.\n"
                          "This would allow importing courses, faculty, and administrative data.")
    
    def generate_reports_c_module(self):
        """Generate institutional reports using C module."""
        try:
            # Simulate C module call for report generation
            result = self.simulate_report_generation()
            
            if result['success']:
                messagebox.showinfo("Reports Generated", 
                                  f"Institutional reports generated successfully!\n\n"
                                  f"Generated files:\n"
                                  f"• {result['enrollment_report']}\n"
                                  f"• {result['performance_report']}\n"
                                  f"• {result['financial_report']}")
            else:
                messagebox.showerror("Error", f"Report generation failed: {result['error']}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate reports: {str(e)}")
    
    def simulate_report_generation(self):
        """Simulate C module report generation."""
        # In a real implementation, this would call a C executable for complex report generation
        try:
            return {
                'success': True,
                'enrollment_report': 'enrollment_report_2025.pdf',
                'performance_report': 'academic_performance_2025.pdf',
                'financial_report': 'financial_summary_2025.pdf'
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def placeholder_action(self, function_name):
        """Placeholder action for director functions."""
        messagebox.showinfo("Function", f"{function_name} - Feature coming soon!")


def main():
    """Main function to run the application."""
    try:
        app = App()
        app.mainloop()
    except Exception as e:
        messagebox.showerror("Application Error", f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main()
