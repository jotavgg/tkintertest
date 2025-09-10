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
        self.title("Sistema de Colaboração Acadêmica")
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
            type TEXT DEFAULT 'assignment',
            FOREIGN KEY (course_id) REFERENCES courses(id)
        )
    ''')
    
    # Add type column if it doesn't exist (for existing databases)
    try:
        cursor.execute('ALTER TABLE assignments ADD COLUMN type TEXT DEFAULT "assignment"')
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    # Add content and submitted_at columns to submissions table if they don't exist
    try:
        cursor.execute('ALTER TABLE submissions ADD COLUMN content TEXT')
    except sqlite3.OperationalError:
        pass  # Column already exists
        
    try:
        cursor.execute('ALTER TABLE submissions ADD COLUMN submitted_at TEXT')
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    # Create quiz questions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quiz_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            assignment_id INTEGER,
            question_text TEXT NOT NULL,
            option_a TEXT NOT NULL,
            option_b TEXT NOT NULL,
            option_c TEXT NOT NULL,
            option_d TEXT NOT NULL,
            correct_answer TEXT NOT NULL,
            points INTEGER DEFAULT 1,
            FOREIGN KEY (assignment_id) REFERENCES assignments (id)
        )
    ''')
    
    # Create quiz answers table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quiz_answers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            submission_id INTEGER,
            question_id INTEGER,
            selected_answer TEXT NOT NULL,
            is_correct BOOLEAN DEFAULT 0,
            FOREIGN KEY (submission_id) REFERENCES submissions (id),
            FOREIGN KEY (question_id) REFERENCES quiz_questions (id)
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
        title_label = tk.Label(main_frame, text="Sistema de Colaboração Acadêmica", 
                              font=("Arial", 18, "bold"))
        title_label.pack(pady=20)
        
        # Username
        tk.Label(main_frame, text="Usuário:", font=("Arial", 12)).pack(pady=5)
        self.username_entry = tk.Entry(main_frame, font=("Arial", 12), width=25)
        self.username_entry.pack(pady=5)
        
        # Password
        tk.Label(main_frame, text="Senha:", font=("Arial", 12)).pack(pady=5)
        self.password_entry = tk.Entry(main_frame, font=("Arial", 12), width=25, show="*")
        self.password_entry.pack(pady=5)
        
        # Login button
        login_btn = tk.Button(main_frame, text="Entrar", font=("Arial", 12),
                             command=self.login, bg="#4CAF50", fg="white", 
                             width=20, height=2)
        login_btn.pack(pady=20)
        
        # Sample credentials info
        info_frame = tk.Frame(main_frame)
        info_frame.pack(pady=10)
        
        tk.Label(info_frame, text="Credenciais de Exemplo:", font=("Arial", 10, "bold")).pack()
        tk.Label(info_frame, text="Professor: teacher1/pass123", font=("Arial", 9)).pack()
        tk.Label(info_frame, text="Estudante: student1/pass123", font=("Arial", 9)).pack()
        tk.Label(info_frame, text="Secretária: secretary1/pass123", font=("Arial", 9)).pack()
        
        # Bind Enter key to login only in these entry widgets
        self.username_entry.bind('<Return>', lambda e: self.login())
        self.password_entry.bind('<Return>', lambda e: self.login())
    
    def login(self):
        """Authenticate user and navigate to appropriate dashboard."""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not username or not password:
            messagebox.showerror("Erro", "Por favor, insira usuário e senha.")
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
            messagebox.showerror("Erro", "Usuário ou senha inválidos.")


class TeacherFrame(tk.Frame):
    """Teacher dashboard for course and student management."""
    
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # Header frame
        header_frame = tk.Frame(self)
        header_frame.pack(fill="x", padx=20, pady=10)
        
        self.welcome_label = tk.Label(header_frame, text="Painel do Professor", 
                                     font=("Arial", 16, "bold"))
        self.welcome_label.pack(side="left")
        
        logout_btn = tk.Button(header_frame, text="Sair", command=controller.logout,
                              bg="#f44336", fg="white")
        logout_btn.pack(side="right")
        
        # Main content frame
        content_frame = tk.Frame(self)
        content_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Course selection
        course_frame = tk.LabelFrame(content_frame, text="Seleção de Disciplina", 
                                   font=("Arial", 12, "bold"))
        course_frame.pack(fill="x", pady=10)
        
        course_selection_frame = tk.Frame(course_frame)
        course_selection_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Label(course_selection_frame, text="Selecionar Disciplina:", font=("Arial", 10)).pack(side="left", padx=5)
        self.course_combo = ttk.Combobox(course_selection_frame, font=("Arial", 10), state="readonly")
        self.course_combo.pack(side="left", padx=5)
        self.course_combo.bind('<<ComboboxSelected>>', self.on_course_selected)
        
        # Add "Show All Students" button
        tk.Button(course_selection_frame, text="Mostrar Todos os Estudantes", 
                 command=self.show_all_students, bg="#9C27B0", fg="white",
                 font=("Arial", 9)).pack(side="left", padx=10)
        
        # Students list
        students_frame = tk.LabelFrame(content_frame, text="Estudantes Inscritos", 
                                     font=("Arial", 12, "bold"))
        students_frame.pack(fill="both", expand=True, pady=10)
        
        # Create Treeview for students
        columns = ("ID", "Nome", "Email", "Nota Média")
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
        
        # First row of buttons
        buttons_row1 = tk.Frame(buttons_frame)
        buttons_row1.pack(fill="x", pady=2)
        
        tk.Button(buttons_row1, text="Atualizar Estudantes", command=self.refresh_students,
                 bg="#4CAF50", fg="white", font=("Arial", 10)).pack(side="left", padx=5)
        
        tk.Button(buttons_row1, text="Inserir Notas", command=self.enter_grades,
                 bg="#2196F3", fg="white", font=("Arial", 10)).pack(side="left", padx=5)
        
        tk.Button(buttons_row1, text="Buscar Estudantes", command=self.search_students,
                 bg="#FF9800", fg="white", font=("Arial", 10)).pack(side="left", padx=5)
        
        tk.Button(buttons_row1, text="Ver Estudantes em Risco", command=self.view_at_risk_students,
                 bg="#f44336", fg="white", font=("Arial", 10)).pack(side="left", padx=5)
        
        # Second row of buttons - Course Content
        buttons_row2 = tk.Frame(buttons_frame)
        buttons_row2.pack(fill="x", pady=2)
        
        tk.Button(buttons_row2, text="Criar Atividade", command=self.create_assignment,
                 bg="#9C27B0", fg="white", font=("Arial", 10)).pack(side="left", padx=5)
        
        tk.Button(buttons_row2, text="Material da Disciplina", command=self.manage_course_materials,
                 bg="#607D8B", fg="white", font=("Arial", 10)).pack(side="left", padx=5)
        
        tk.Button(buttons_row2, text="Ver Entregas", command=self.view_submissions,
                 bg="#795548", fg="white", font=("Arial", 10)).pack(side="left", padx=5)
    
    def refresh_data(self):
        """Refresh the teacher's courses when frame is shown."""
        if self.controller.current_user:
            self.welcome_label.config(
                text=f"Painel do Professor - Bem-vindo(a), {self.controller.current_user['first_name']}!"
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
            messagebox.showinfo("Info", "Por favor, selecione uma disciplina primeiro.")
    
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
        self.students_tree.heading("#4", text="Disciplinas Inscritas")
        
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
        self.students_tree.heading("#4", text="Nota Média")
        
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
            messagebox.showwarning("Aviso", "Por favor, selecione um estudante primeiro.")
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
                    messagebox.showerror("Erro", "Por favor, insira o nome da atividade.")
                    return
                
                if not 0 <= grade <= 100:
                    messagebox.showerror("Erro", "A nota deve estar entre 0 e 100.")
                    return
                
                messagebox.showinfo("Sucesso", f"Nota {grade} salva para {assignment}")
                grade_window.destroy()
                
            except ValueError:
                messagebox.showerror("Erro", "Por favor, insira uma nota numérica válida.")
        
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
        
        # Button frame for better layout
        button_frame = tk.Frame(search_window)
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="Search", command=perform_search,
                 bg="#2196F3", fg="white", font=("Arial", 11), 
                 width=15, height=2).pack(side="left", padx=5)
        
        tk.Button(button_frame, text="Fechar", command=search_window.destroy,
                 bg="#f44336", fg="white", font=("Arial", 11),
                 width=15, height=2).pack(side="left", padx=5)
    
    def view_at_risk_students(self):
        """AI Feature: Show students with low grades."""
        selection = self.course_combo.get()
        if not selection:
            messagebox.showwarning("Aviso", "Por favor, selecione um curso primeiro.")
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
    
    def create_assignment(self):
        """Criar uma nova atividade para o curso selecionado."""
        selection = self.course_combo.get()
        if not selection:
            messagebox.showwarning("Aviso", "Por favor, selecione um curso primeiro.")
            return
        
        course_id = int(selection.split("ID: ")[1].rstrip(")"))
        course_name = selection.split(" (ID:")[0]
        
        assignment_window = tk.Toplevel(self.controller)
        assignment_window.title(f"Criar Atividade - {course_name}")
        assignment_window.geometry("700x800")
        assignment_window.transient(self.controller)
        assignment_window.grab_set()
        
        tk.Label(assignment_window, text=f"Criar Atividade para {course_name}", 
                font=("Arial", 14, "bold")).pack(pady=10)
        
        # Create main canvas and scrollbar for scrolling
        main_canvas = tk.Canvas(assignment_window)
        main_scrollbar = tk.Scrollbar(assignment_window, orient="vertical", command=main_canvas.yview)
        scrollable_main_frame = tk.Frame(main_canvas)
        
        scrollable_main_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )
        
        main_canvas.create_window((0, 0), window=scrollable_main_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=main_scrollbar.set)
        
        # Pack canvas and scrollbar
        main_canvas.pack(side="left", fill="both", expand=True, padx=20)
        main_scrollbar.pack(side="right", fill="y")
        
        # Assignment details form (now inside scrollable frame)
        form_frame = tk.Frame(scrollable_main_frame)
        form_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Title
        tk.Label(form_frame, text="Título da Atividade:", font=("Arial", 11, "bold")).pack(anchor='w')
        title_entry = tk.Entry(form_frame, font=("Arial", 11), width=50)
        title_entry.pack(fill="x", pady=(0, 10))
        
        # Description
        tk.Label(form_frame, text="Descrição:", font=("Arial", 11, "bold")).pack(anchor='w')
        desc_text = tk.Text(form_frame, height=4, font=("Arial", 10))
        desc_text.pack(fill="x", pady=(0, 10))
        
        # Due date
        tk.Label(form_frame, text="Data de Entrega (AAAA-MM-DD):", font=("Arial", 11, "bold")).pack(anchor='w')
        due_entry = tk.Entry(form_frame, font=("Arial", 11), width=20)
        due_entry.pack(anchor='w', pady=(0, 10))
        due_entry.insert(0, "2025-09-30")  # Default date
        
        # Max points
        tk.Label(form_frame, text="Pontuação Máxima:", font=("Arial", 11, "bold")).pack(anchor='w')
        points_entry = tk.Entry(form_frame, font=("Arial", 11), width=10)
        points_entry.pack(anchor='w', pady=(0, 10))
        points_entry.insert(0, "100")
        
        # Assignment type
        tk.Label(form_frame, text="Tipo de Atividade:", font=("Arial", 11, "bold")).pack(anchor='w')
        type_var = tk.StringVar(value="homework")
        type_frame = tk.Frame(form_frame)
        type_frame.pack(anchor='w', pady=(0, 10))
        
        tk.Radiobutton(type_frame, text="Tarefa", variable=type_var, value="homework").pack(side="left")
        tk.Radiobutton(type_frame, text="Quiz", variable=type_var, value="quiz").pack(side="left", padx=10)
        tk.Radiobutton(type_frame, text="Projeto", variable=type_var, value="project").pack(side="left")
        tk.Radiobutton(type_frame, text="Prova", variable=type_var, value="exam").pack(side="left", padx=10)
        
        # Quiz questions frame (initially hidden) - now properly scrollable
        quiz_main_frame = tk.Frame(form_frame)
        
        # Add label for quiz section
        quiz_label = tk.Label(quiz_main_frame, text="Questões do Quiz:", font=("Arial", 11, "bold"))
        quiz_label.pack(anchor='w', pady=(5, 0))
        
        # Quiz questions will be added here
        quiz_frame = tk.Frame(quiz_main_frame)
        quiz_frame.pack(fill="both", expand=True, pady=5)
        
        quiz_questions = []
        
        def toggle_quiz_options():
            if type_var.get() == "quiz":
                quiz_main_frame.pack(fill="both", expand=True, pady=10)
                if not quiz_questions:  # Only add button if no questions yet
                    add_question_btn.pack(pady=10)
                add_quiz_question()
            else:
                quiz_main_frame.pack_forget()
                quiz_questions.clear()
                for widget in quiz_frame.winfo_children():
                    widget.destroy()
        
        def add_quiz_question():
            question_num = len(quiz_questions) + 1
            q_frame = tk.LabelFrame(quiz_frame, text=f"Questão {question_num}", font=("Arial", 10, "bold"))
            q_frame.pack(fill="x", pady=5, padx=5)
            
            # Question text
            tk.Label(q_frame, text="Pergunta:", font=("Arial", 9, "bold")).pack(anchor='w', padx=5, pady=2)
            question_entry = tk.Text(q_frame, height=3, font=("Arial", 9))
            question_entry.pack(fill="x", padx=5, pady=2)
            
            # Options
            options_frame = tk.Frame(q_frame)
            options_frame.pack(fill="x", padx=5, pady=5)
            
            option_entries = {}
            correct_var = tk.StringVar(value="A")
            
            for i, letter in enumerate(['A', 'B', 'C', 'D']):
                row_frame = tk.Frame(options_frame)
                row_frame.pack(fill="x", pady=2)
                
                tk.Radiobutton(row_frame, text="", variable=correct_var, value=letter).pack(side="left")
                tk.Label(row_frame, text=f"Opção {letter}:", font=("Arial", 9), width=8).pack(side="left")
                option_entry = tk.Entry(row_frame, font=("Arial", 9))
                option_entry.pack(side="left", fill="x", expand=True, padx=5)
                option_entries[letter] = option_entry
            
            tk.Label(q_frame, text="Selecione a resposta correta acima", 
                    font=("Arial", 8), fg="gray").pack(anchor='w', padx=5)
            
            # Points for this question
            points_frame = tk.Frame(q_frame)
            points_frame.pack(fill="x", padx=5, pady=5)
            tk.Label(points_frame, text="Pontos:", font=("Arial", 9)).pack(side="left")
            question_points = tk.Entry(points_frame, width=5, font=("Arial", 9))
            question_points.pack(side="left", padx=5)
            question_points.insert(0, "1")
            
            # Remove button
            def remove_question():
                quiz_questions.remove(question_data)
                q_frame.destroy()
                update_question_numbers()
                # Re-pack add button if no questions left
                if not quiz_questions:
                    add_question_btn.pack(pady=10)
                # Update canvas scroll region
                scrollable_main_frame.update_idletasks()
                main_canvas.configure(scrollregion=main_canvas.bbox("all"))
            
            tk.Button(q_frame, text="Remover Questão", command=remove_question,
                     bg="#f44336", fg="white", font=("Arial", 8)).pack(anchor='e', padx=5, pady=5)
            
            question_data = {
                'frame': q_frame,
                'question_entry': question_entry,
                'options': option_entries,
                'correct_var': correct_var,
                'points_entry': question_points
            }
            quiz_questions.append(question_data)
            
            # Pack add button after the question
            add_question_btn.pack_forget()
            add_question_btn.pack(pady=10)
            
            # Update canvas scroll region after adding question
            scrollable_main_frame.update_idletasks()
            main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        
        def update_question_numbers():
            for i, q_data in enumerate(quiz_questions, 1):
                q_data['frame'].config(text=f"Questão {i}")
        
        # Bind radio button changes
        for widget in type_frame.winfo_children():
            if isinstance(widget, tk.Radiobutton):
                widget.config(command=toggle_quiz_options)
        
        # Add question button for quiz
        add_question_btn = tk.Button(quiz_frame, text="+ Adicionar Questão", 
                                   command=add_quiz_question, bg="#2196F3", fg="white")
        
        # Mouse wheel scrolling support
        def on_mousewheel(event):
            main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        main_canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        def save_assignment():
            title = title_entry.get().strip()
            description = desc_text.get(1.0, tk.END).strip()
            due_date = due_entry.get().strip()
            assignment_type = type_var.get()
            
            try:
                max_points = int(points_entry.get().strip())
            except ValueError:
                messagebox.showerror("Erro", "A pontuação máxima deve ser um número.")
                return
            
            if not title:
                messagebox.showerror("Erro", "Por favor, insira um título para a atividade.")
                return
            
            # Validate quiz questions if it's a quiz
            if assignment_type == "quiz":
                if not quiz_questions:
                    messagebox.showerror("Erro", "Por favor, adicione pelo menos uma questão para o quiz.")
                    return
                
                total_points = 0
                for q_data in quiz_questions:
                    question_text = q_data['question_entry'].get(1.0, tk.END).strip()
                    if not question_text:
                        messagebox.showerror("Erro", "Todas as questões devem ter texto.")
                        return
                    
                    for letter, entry in q_data['options'].items():
                        if not entry.get().strip():
                            messagebox.showerror("Erro", f"Todas as opções devem ser preenchidas na questão.")
                            return
                    
                    try:
                        q_points = int(q_data['points_entry'].get())
                        total_points += q_points
                    except ValueError:
                        messagebox.showerror("Erro", "Pontos da questão devem ser números.")
                        return
                
                # Update max_points to match total quiz points
                max_points = total_points
            
            try:
                conn = sqlite3.connect('academic_system.db')
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO assignments (course_id, title, description, due_date, max_points, type)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (course_id, title, description, due_date, max_points, assignment_type))
                
                assignment_id = cursor.lastrowid
                
                # Save quiz questions if it's a quiz
                if assignment_type == "quiz":
                    for q_data in quiz_questions:
                        question_text = q_data['question_entry'].get(1.0, tk.END).strip()
                        correct_answer = q_data['correct_var'].get()
                        q_points = int(q_data['points_entry'].get())
                        
                        cursor.execute('''
                            INSERT INTO quiz_questions 
                            (assignment_id, question_text, option_a, option_b, option_c, option_d, correct_answer, points)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (assignment_id, question_text,
                              q_data['options']['A'].get(),
                              q_data['options']['B'].get(),
                              q_data['options']['C'].get(),
                              q_data['options']['D'].get(),
                              correct_answer, q_points))
                
                conn.commit()
                conn.close()
                
                if assignment_type == "quiz":
                    messagebox.showinfo("Sucesso", 
                                      f"Quiz '{title}' criado com sucesso!\n"
                                      f"ID da Atividade: {assignment_id}\n"
                                      f"Total de questões: {len(quiz_questions)}\n"
                                      f"Pontuação total: {max_points}")
                else:
                    messagebox.showinfo("Sucesso", 
                                      f"Atividade '{title}' criada com sucesso!\n"
                                      f"ID da Atividade: {assignment_id}")
                assignment_window.destroy()
                
            except Exception as e:
                messagebox.showerror("Erro", f"Falha ao criar atividade: {str(e)}")
        
        # Buttons
        button_frame = tk.Frame(assignment_window)
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="Criar Atividade", command=save_assignment,
                 bg="#4CAF50", fg="white", font=("Arial", 11), width=15).pack(side="left", padx=5)
        
        tk.Button(button_frame, text="Cancelar", command=assignment_window.destroy,
                 bg="#f44336", fg="white", font=("Arial", 11), width=15).pack(side="left", padx=5)
    
    def manage_course_materials(self):
        """Manage course materials and content."""
        selection = self.course_combo.get()
        if not selection:
            messagebox.showwarning("Aviso", "Por favor, selecione um curso primeiro.")
            return
        
        course_id = int(selection.split("ID: ")[1].rstrip(")"))
        course_name = selection.split(" (ID:")[0]
        
        materials_window = tk.Toplevel(self.controller)
        materials_window.title(f"Course Materials - {course_name}")
        materials_window.geometry("600x500")
        materials_window.transient(self.controller)
        materials_window.grab_set()
        
        tk.Label(materials_window, text=f"Course Materials for {course_name}", 
                font=("Arial", 14, "bold")).pack(pady=10)
        
        # Notebook for different types of content
        notebook = ttk.Notebook(materials_window)
        notebook.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Syllabus tab
        syllabus_frame = tk.Frame(notebook)
        notebook.add(syllabus_frame, text="Syllabus")
        
        tk.Label(syllabus_frame, text="Course Syllabus", font=("Arial", 12, "bold")).pack(pady=5)
        syllabus_text = tk.Text(syllabus_frame, height=15, font=("Arial", 10))
        syllabus_text.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Load existing syllabus or add sample content
        sample_syllabus = f"""Course: {course_name}
        
Course Description:
This course covers fundamental concepts and practical applications in the subject area.

Learning Objectives:
- Understand core principles and theories
- Apply knowledge to solve real-world problems
- Develop critical thinking and analytical skills
- Work effectively in teams and individually

Assessment:
- Assignments: 40%
- Quizzes: 20%
- Midterm Exam: 20%
- Final Project: 20%

Required Materials:
- Textbook: [To be announced]
- Online resources and readings
- Calculator (if applicable)

Course Schedule:
Week 1-2: Introduction and Fundamentals
Week 3-4: Core Concepts
Week 5-6: Applications
Week 7-8: Advanced Topics
Week 9-10: Review and Assessment
"""
        syllabus_text.insert(1.0, sample_syllabus)
        
        # Lessons tab
        lessons_frame = tk.Frame(notebook)
        notebook.add(lessons_frame, text="Lessons")
        
        tk.Label(lessons_frame, text="Course Lessons", font=("Arial", 12, "bold")).pack(pady=5)
        
        lessons_list_frame = tk.Frame(lessons_frame)
        lessons_list_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        lessons_listbox = tk.Listbox(lessons_list_frame, font=("Arial", 10))
        lessons_listbox.pack(side="left", fill="both", expand=True)
        
        lessons_scroll = ttk.Scrollbar(lessons_list_frame, orient="vertical", command=lessons_listbox.yview)
        lessons_listbox.configure(yscrollcommand=lessons_scroll.set)
        lessons_scroll.pack(side="right", fill="y")
        
        # Sample lessons
        sample_lessons = [
            "Lesson 1: Introduction to the Subject",
            "Lesson 2: Basic Principles and Concepts",
            "Lesson 3: Practical Applications",
            "Lesson 4: Problem-Solving Techniques",
            "Lesson 5: Case Studies and Examples",
            "Lesson 6: Advanced Topics Overview",
            "Lesson 7: Review and Practice",
            "Lesson 8: Final Assessment Preparation"
        ]
        
        for lesson in sample_lessons:
            lessons_listbox.insert(tk.END, lesson)
        
        lesson_buttons = tk.Frame(lessons_frame)
        lesson_buttons.pack(pady=5)
        
        tk.Button(lesson_buttons, text="Add Lesson", bg="#4CAF50", fg="white",
                 command=lambda: self.add_lesson_dialog(lessons_listbox)).pack(side="left", padx=5)
        
        # Resources tab
        resources_frame = tk.Frame(notebook)
        notebook.add(resources_frame, text="Resources")
        
        tk.Label(resources_frame, text="Course Resources", font=("Arial", 12, "bold")).pack(pady=5)
        resources_text = tk.Text(resources_frame, height=15, font=("Arial", 10))
        resources_text.pack(fill="both", expand=True, padx=10, pady=5)
        
        sample_resources = """Online Resources:
• Course Website: [URL]
• Online Library: [URL]
• Video Lectures: [URL]
• Practice Exercises: [URL]

Recommended Reading:
• Primary Textbook: [Title and Author]
• Supplementary Materials: [List]
• Research Papers: [References]

Tools and Software:
• Required Software: [List]
• Online Platforms: [List]
• Mobile Apps: [List]

Support:
• Office Hours: [Schedule]
• Teaching Assistant: [Contact]
• Study Groups: [Information]
• Online Forum: [URL]
"""
        resources_text.insert(1.0, sample_resources)
        
        def save_materials():
            """Save course materials (in a real system, this would save to database)."""
            messagebox.showinfo("Salvo", "Materiais do curso foram salvos com sucesso!")
        
        # Buttons
        button_frame = tk.Frame(materials_window)
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="Save Materials", command=save_materials,
                 bg="#4CAF50", fg="white", font=("Arial", 11), width=15).pack(side="left", padx=5)
        
        tk.Button(button_frame, text="Fechar", command=materials_window.destroy,
                 bg="#f44336", fg="white", font=("Arial", 11), width=15).pack(side="left", padx=5)
    
    def add_lesson_dialog(self, lessons_listbox):
        """Add a new lesson to the course."""
        lesson_window = tk.Toplevel(self.controller)
        lesson_window.title("Add New Lesson")
        lesson_window.geometry("400x200")
        lesson_window.transient(self.controller)
        lesson_window.grab_set()
        
        tk.Label(lesson_window, text="Add New Lesson", font=("Arial", 12, "bold")).pack(pady=10)
        
        tk.Label(lesson_window, text="Lesson Title:").pack()
        lesson_entry = tk.Entry(lesson_window, font=("Arial", 11), width=40)
        lesson_entry.pack(pady=5)
        
        def add_lesson():
            lesson_title = lesson_entry.get().strip()
            if lesson_title:
                lessons_listbox.insert(tk.END, lesson_title)
                lesson_window.destroy()
            else:
                messagebox.showerror("Erro", "Por favor, insira um título para a aula.")
        
        tk.Button(lesson_window, text="Add Lesson", command=add_lesson,
                 bg="#4CAF50", fg="white", font=("Arial", 11)).pack(pady=20)
    
    def view_submissions(self):
        """View and grade student submissions."""
        selection = self.course_combo.get()
        if not selection:
            messagebox.showwarning("Aviso", "Por favor, selecione um curso primeiro.")
            return
        
        course_id = int(selection.split("ID: ")[1].rstrip(")"))
        course_name = selection.split(" (ID:")[0]
        
        submissions_window = tk.Toplevel(self.controller)
        submissions_window.title(f"Entregas dos Estudantes - {course_name}")
        submissions_window.geometry("800x600")
        submissions_window.transient(self.controller)
        submissions_window.grab_set()
        
        tk.Label(submissions_window, text=f"Entregas dos Estudantes para {course_name}", 
                font=("Arial", 14, "bold")).pack(pady=10)
        
        # Assignment selection
        assignment_frame = tk.Frame(submissions_window)
        assignment_frame.pack(fill="x", padx=20, pady=5)
        
        tk.Label(assignment_frame, text="Selecionar Atividade:", font=("Arial", 11)).pack(side="left")
        assignment_combo = ttk.Combobox(assignment_frame, font=("Arial", 10), state="readonly", width=40)
        assignment_combo.pack(side="left", padx=10)
        
        # Load assignments for this course
        conn = sqlite3.connect('academic_system.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, title, due_date FROM assignments 
            WHERE course_id = ? ORDER BY due_date DESC
        ''', (course_id,))
        assignments = cursor.fetchall()
        conn.close()
        
        if assignments:
            assignment_list = [f"{assignment[1]} - Due: {assignment[2]} (ID: {assignment[0]})" for assignment in assignments]
            assignment_combo['values'] = assignment_list
            assignment_combo.current(0)
        else:
            assignment_combo['values'] = ["No assignments found"]
        
        # Submissions display
        submissions_frame = tk.LabelFrame(submissions_window, text="Submissions", 
                                        font=("Arial", 12, "bold"))
        submissions_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Create Treeview for submissions
        columns = ("Student", "Submission Date", "Grade", "Status")
        submissions_tree = ttk.Treeview(submissions_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            submissions_tree.heading(col, text=col)
            submissions_tree.column(col, width=150)
        
        scrollbar_sub = ttk.Scrollbar(submissions_frame, orient="vertical", command=submissions_tree.yview)
        submissions_tree.configure(yscrollcommand=scrollbar_sub.set)
        
        submissions_tree.pack(side="left", fill="both", expand=True)
        scrollbar_sub.pack(side="right", fill="y")
        
        def load_submissions():
            """Load submissions for the selected assignment."""
            selection = assignment_combo.get()
            if not selection or "No assignments" in selection:
                return
            
            assignment_id = int(selection.split("ID: ")[1].rstrip(")"))
            
            # Check if this is a quiz
            conn = sqlite3.connect('academic_system.db')
            cursor = conn.cursor()
            cursor.execute('SELECT type FROM assignments WHERE id = ?', (assignment_id,))
            assignment_type = cursor.fetchone()[0]
            conn.close()
            
            # Clear existing items
            for item in submissions_tree.get_children():
                submissions_tree.delete(item)
            
            conn = sqlite3.connect('academic_system.db')
            cursor = conn.cursor()
            
            if assignment_type == "quiz":
                # For quizzes, show additional quiz-specific information
                cursor.execute('''
                    SELECT u.id, u.first_name || ' ' || u.last_name as name,
                           s.submitted_at, s.grade, s.id as submission_id,
                           (SELECT COUNT(*) FROM quiz_answers qa 
                            JOIN quiz_questions qq ON qa.question_id = qq.id 
                            WHERE qa.submission_id = s.id AND qa.is_correct = 1) as correct_answers,
                           (SELECT COUNT(*) FROM quiz_questions qq 
                            WHERE qq.assignment_id = ?) as total_questions
                    FROM users u
                    JOIN enrollments e ON u.id = e.user_id
                    LEFT JOIN submissions s ON u.id = s.student_id AND s.assignment_id = ?
                    WHERE e.course_id = ? AND u.role = 'STUDENT'
                    ORDER BY u.first_name, u.last_name
                ''', (assignment_id, assignment_id, course_id))
            else:
                # Get all students enrolled in this course with their submission status
                cursor.execute('''
                    SELECT u.id, u.first_name || ' ' || u.last_name as name,
                           s.submitted_at, s.grade, s.id as submission_id, NULL, NULL
                    FROM users u
                    JOIN enrollments e ON u.id = e.user_id
                    LEFT JOIN submissions s ON u.id = s.student_id AND s.assignment_id = ?
                    WHERE e.course_id = ? AND u.role = 'STUDENT'
                    ORDER BY u.first_name, u.last_name
                ''', (assignment_id, course_id))
            
            students = cursor.fetchall()
            conn.close()
            
            for student_data in students:
                student_id, student_name, submission_date, grade, submission_id, correct_answers, total_questions = student_data
                
                if submission_date:  # Student has submitted
                    if grade is not None:
                        status = "Avaliado"
                        display_grade = f"{grade:.1f}"
                        if assignment_type == "quiz" and correct_answers is not None:
                            display_grade += f" ({correct_answers}/{total_questions})"
                    else:
                        status = "Entregue - Pendente"
                        display_grade = "Não Avaliado"
                    
                    submissions_tree.insert("", "end", values=(
                        student_name, submission_date, display_grade, status
                    ), tags=(str(submission_id), assignment_type))
                else:  # No submission
                    submissions_tree.insert("", "end", values=(
                        student_name, "Não Entregue", "N/A", "Faltando"
                    ), tags=("none", assignment_type))
        
        assignment_combo.bind('<<ComboboxSelected>>', lambda e: load_submissions())
        
        # Load initial submissions
        if assignments:
            load_submissions()
        
        def grade_submission():
            """Grade the selected submission."""
            selection = submissions_tree.selection()
            if not selection:
                messagebox.showwarning("Aviso", "Por favor, selecione uma entrega para avaliar.")
                return
            
            item = submissions_tree.item(selection[0])
            student_name = item['values'][0]
            current_grade = item['values'][2]
            submission_id = item['tags'][0]
            
            if item['values'][3] == "Missing":
                messagebox.showwarning("Aviso", "Não é possível avaliar entrega não encontrada.")
                return
            
            if submission_id == "none":
                messagebox.showwarning("Aviso", "Nenhuma entrega encontrada para este estudante.")
                return
            
            # Get submission content
            conn = sqlite3.connect('academic_system.db')
            cursor = conn.cursor()
            cursor.execute('SELECT feedback FROM submissions WHERE id = ?', (submission_id,))
            submission_content = cursor.fetchone()
            conn.close()
            
            # Grade entry dialog
            grade_window = tk.Toplevel(self.controller)
            grade_window.title(f"Grade Submission - {student_name}")
            grade_window.geometry("600x500")
            grade_window.transient(self.controller)
            grade_window.grab_set()
            
            tk.Label(grade_window, text=f"Grade Submission for {student_name}", 
                    font=("Arial", 12, "bold")).pack(pady=10)
            
            # Show submission content
            content_frame = tk.LabelFrame(grade_window, text="Student Submission", 
                                        font=("Arial", 11, "bold"))
            content_frame.pack(fill="both", expand=True, padx=20, pady=10)
            
            content_text = tk.Text(content_frame, height=10, font=("Arial", 10))
            content_text.pack(fill="both", expand=True, padx=10, pady=10)
            
            if submission_content and submission_content[0]:
                content_text.insert(1.0, submission_content[0])
            else:
                content_text.insert(1.0, "No content available.")
            content_text.config(state="disabled")
            
            # Grading section
            grade_frame = tk.LabelFrame(grade_window, text="Grading", 
                                      font=("Arial", 11, "bold"))
            grade_frame.pack(fill="x", padx=20, pady=10)
            
            grade_input_frame = tk.Frame(grade_frame)
            grade_input_frame.pack(fill="x", padx=10, pady=10)
            
            tk.Label(grade_input_frame, text="Grade (0-100):").pack(side="left")
            grade_entry = tk.Entry(grade_input_frame, font=("Arial", 11), width=10)
            grade_entry.pack(side="left", padx=10)
            
            if current_grade != "Not Graded" and current_grade != "N/A":
                grade_entry.insert(0, str(current_grade))
            
            tk.Label(grade_frame, text="Teacher Feedback:").pack(anchor='w', padx=10)
            feedback_text = tk.Text(grade_frame, height=4, width=50, font=("Arial", 10))
            feedback_text.pack(fill="x", padx=10, pady=(5, 10))
            
            def save_grade():
                try:
                    grade = float(grade_entry.get())
                    if not 0 <= grade <= 100:
                        messagebox.showerror("Erro", "A nota deve estar entre 0 e 100.")
                        return
                    
                    feedback = feedback_text.get(1.0, tk.END).strip()
                    
                    # Update grade in database
                    conn = sqlite3.connect('academic_system.db')
                    cursor = conn.cursor()
                    cursor.execute('''
                        UPDATE submissions SET grade = ? 
                        WHERE id = ?
                    ''', (grade, submission_id))
                    conn.commit()
                    conn.close()
                    
                    # Update the treeview
                    submissions_tree.item(selection[0], values=(
                        student_name, item['values'][1], f"{grade:.1f}", "Graded"
                    ))
                    
                    messagebox.showinfo("Sucesso", f"Nota {grade} salva para {student_name}")
                    grade_window.destroy()
                    
                except ValueError:
                    messagebox.showerror("Erro", "Por favor, insira uma nota numérica válida.")
            
            # Buttons
            button_frame = tk.Frame(grade_window)
            button_frame.pack(pady=10)
            
            tk.Button(button_frame, text="Save Grade", command=save_grade,
                     bg="#4CAF50", fg="white", font=("Arial", 11)).pack(side="left", padx=5)
            
            tk.Button(button_frame, text="Cancelar", command=grade_window.destroy,
                     bg="#f44336", fg="white", font=("Arial", 11)).pack(side="left", padx=5)
        
        # Functions for quiz details
        def view_quiz_details():
            """Visualizar detalhes específicos do quiz."""
            selection = submissions_tree.selection()
            if not selection:
                messagebox.showwarning("Aviso", "Por favor, selecione uma entrega para visualizar.")
                return
            
            item = submissions_tree.item(selection[0])
            submission_id = item['tags'][0]
            assignment_type = item['tags'][1] if len(item['tags']) > 1 else "assignment"
            
            if assignment_type != "quiz":
                messagebox.showinfo("Info", "Esta função é apenas para quizzes.")
                return
            
            if submission_id == "none":
                messagebox.showwarning("Aviso", "Estudante não fez o quiz ainda.")
                return
            
            # Get quiz results
            conn = sqlite3.connect('academic_system.db')
            cursor = conn.cursor()
            
            # Get assignment details
            assignment_selection = assignment_combo.get()
            assignment_id = int(assignment_selection.split("ID: ")[1].rstrip(")"))
            
            cursor.execute('''
                SELECT title FROM assignments WHERE id = ?
            ''', (assignment_id,))
            quiz_title = cursor.fetchone()[0]
            
            # Get questions and answers
            cursor.execute('''
                SELECT qq.id, qq.question_text, qq.option_a, qq.option_b, qq.option_c, qq.option_d, 
                       qq.correct_answer, qq.points, qa.selected_answer, qa.is_correct
                FROM quiz_questions qq
                LEFT JOIN quiz_answers qa ON qq.id = qa.question_id AND qa.submission_id = ?
                WHERE qq.assignment_id = ?
                ORDER BY qq.id
            ''', (submission_id, assignment_id))
            
            quiz_data = cursor.fetchall()
            conn.close()
            
            # Show detailed quiz results
            show_teacher_quiz_results(quiz_title, item['values'][0], quiz_data)
        
        def show_teacher_quiz_results(quiz_title, student_name, quiz_data):
            """Mostrar resultados detalhados do quiz para o professor."""
            results_window = tk.Toplevel(submissions_window)
            results_window.title(f"Resultados do Quiz: {student_name}")
            results_window.geometry("900x700")
            results_window.transient(self.controller)
            results_window.grab_set()
            
            # Header
            tk.Label(results_window, text=f"📊 Quiz: {quiz_title}", 
                    font=("Arial", 16, "bold")).pack(pady=10)
            
            tk.Label(results_window, text=f"Estudante: {student_name}", 
                    font=("Arial", 14)).pack(pady=5)
            
            # Calculate stats
            total_questions = len(quiz_data)
            correct_answers = sum(1 for q in quiz_data if q[9])  # is_correct
            total_points = sum(q[7] for q in quiz_data)  # points
            earned_points = sum(q[7] for q in quiz_data if q[9])
            
            stats_frame = tk.Frame(results_window, bg="#f0f0f0", relief="ridge", bd=2)
            stats_frame.pack(fill="x", padx=20, pady=10)
            
            tk.Label(stats_frame, text=f"Questões Corretas: {correct_answers}/{total_questions}", 
                    font=("Arial", 12, "bold"), bg="#f0f0f0").pack(pady=2)
            tk.Label(stats_frame, text=f"Pontos Obtidos: {earned_points}/{total_points}", 
                    font=("Arial", 12, "bold"), bg="#f0f0f0").pack(pady=2)
            
            percentage = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
            tk.Label(stats_frame, text=f"Porcentagem: {percentage:.1f}%", 
                    font=("Arial", 12, "bold"), bg="#f0f0f0").pack(pady=2)
            
            # Scrollable frame for detailed answers
            canvas = tk.Canvas(results_window)
            scrollbar = tk.Scrollbar(results_window, orient="vertical", command=canvas.yview)
            scrollable_frame = tk.Frame(canvas)
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            canvas.pack(side="left", fill="both", expand=True, padx=20)
            scrollbar.pack(side="right", fill="y")
            
            # Show each question
            for i, question_data in enumerate(quiz_data, 1):
                (q_id, q_text, opt_a, opt_b, opt_c, opt_d, correct_answer, 
                 points, selected_answer, is_correct) = question_data
                
                # Question frame
                bg_color = "#e8f5e8" if is_correct else "#ffeaea"
                q_frame = tk.LabelFrame(scrollable_frame, 
                                       text=f"Questão {i} ({'✓' if is_correct else '✗'}) - {points} pontos", 
                                       font=("Arial", 11, "bold"), 
                                       bg=bg_color, padx=10, pady=10)
                q_frame.pack(fill="x", pady=10, padx=10)
                
                # Question text
                tk.Label(q_frame, text=q_text, font=("Arial", 11), 
                        wraplength=700, justify="left", bg=bg_color).pack(anchor='w', pady=(0, 10))
                
                # Show options
                options = {'A': opt_a, 'B': opt_b, 'C': opt_c, 'D': opt_d}
                
                for letter, option_text in options.items():
                    color = "black"
                    prefix = f"{letter}) "
                    
                    if letter == correct_answer and letter == selected_answer:
                        color = "green"
                        prefix = f"{letter}) ✓ "
                    elif letter == correct_answer:
                        color = "green"
                        prefix = f"{letter}) ✓ (Correta) "
                    elif letter == selected_answer:
                        color = "red"
                        prefix = f"{letter}) ✗ (Escolhida) "
                    
                    tk.Label(q_frame, text=f"{prefix}{option_text}", 
                            font=("Arial", 10), fg=color, bg=bg_color,
                            wraplength=650, justify="left").pack(anchor='w', pady=1)
            
            tk.Button(results_window, text="Fechar", command=results_window.destroy,
                     bg="#f44336", fg="white", font=("Arial", 11)).pack(pady=10)
        
        # Buttons
        button_frame = tk.Frame(submissions_window)
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="Avaliar Selecionado", command=grade_submission,
                 bg="#4CAF50", fg="white", font=("Arial", 11), width=15).pack(side="left", padx=5)
        
        def check_quiz_button():
            """Verificar se deve mostrar o botão de detalhes do quiz."""
            selection = assignment_combo.get()
            if selection and "Quiz" in selection:
                quiz_button.pack(side="left", padx=5)
            else:
                quiz_button.pack_forget()
        
        quiz_button = tk.Button(button_frame, text="Detalhes do Quiz", command=view_quiz_details,
                               bg="#FF9800", fg="white", font=("Arial", 11), width=15)
        
        tk.Button(button_frame, text="Atualizar", command=lambda: [load_submissions(), check_quiz_button()],
                 bg="#2196F3", fg="white", font=("Arial", 11), width=15).pack(side="left", padx=5)
        
        tk.Button(button_frame, text="Fechar", command=submissions_window.destroy,
                 bg="#f44336", fg="white", font=("Arial", 11), width=15).pack(side="left", padx=5)
        
        # Initial check for quiz button
        assignment_combo.bind('<<ComboboxSelected>>', lambda e: [load_submissions(), check_quiz_button()])


class StudentFrame(tk.Frame):
    """Student dashboard for viewing courses and grades."""
    
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # Header frame
        header_frame = tk.Frame(self)
        header_frame.pack(fill="x", padx=20, pady=10)
        
        self.welcome_label = tk.Label(header_frame, text="Painel do Estudante", 
                                     font=("Arial", 16, "bold"))
        self.welcome_label.pack(side="left")
        
        logout_btn = tk.Button(header_frame, text="Sair", command=controller.logout,
                              bg="#f44336", fg="white")
        logout_btn.pack(side="right")
        
        # Main content frame
        content_frame = tk.Frame(self)
        content_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Enrolled courses
        courses_frame = tk.LabelFrame(content_frame, text="Minhas Disciplinas e Notas", 
                                    font=("Arial", 12, "bold"))
        courses_frame.pack(fill="both", expand=True, pady=10)
        
        # Create Treeview for courses
        columns = ("Disciplina", "Professor", "Nota Média")
        self.courses_tree = ttk.Treeview(courses_frame, columns=columns, show="headings", height=8)
        
        for col in columns:
            self.courses_tree.heading(col, text=col)
            self.courses_tree.column(col, width=200)
        
        scrollbar_courses = ttk.Scrollbar(courses_frame, orient="vertical", command=self.courses_tree.yview)
        self.courses_tree.configure(yscrollcommand=scrollbar_courses.set)
        
        self.courses_tree.pack(side="left", fill="both", expand=True)
        scrollbar_courses.pack(side="right", fill="y")
        
        # Assignments deadlines
        deadlines_frame = tk.LabelFrame(content_frame, text="Atividades Pendentes", 
                                      font=("Arial", 12, "bold"))
        deadlines_frame.pack(fill="x", pady=10)
        
        assignments_frame = tk.Frame(deadlines_frame)
        assignments_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create Treeview for assignments
        columns = ("Disciplina", "Atividade", "Tipo", "Data de Entrega", "Status")
        self.assignments_tree = ttk.Treeview(assignments_frame, columns=columns, show="headings", height=6)
        
        for col in columns:
            self.assignments_tree.heading(col, text=col)
            if col == "Tipo":
                self.assignments_tree.column(col, width=80)
            else:
                self.assignments_tree.column(col, width=150)
        
        scrollbar_assignments = ttk.Scrollbar(assignments_frame, orient="vertical", command=self.assignments_tree.yview)
        self.assignments_tree.configure(yscrollcommand=scrollbar_assignments.set)
        
        self.assignments_tree.pack(side="left", fill="both", expand=True)
        scrollbar_assignments.pack(side="right", fill="y")
        
        # Assignment action buttons
        assignment_buttons = tk.Frame(deadlines_frame)
        assignment_buttons.pack(pady=5)
        
        self.submit_button = tk.Button(assignment_buttons, text="Entregar Atividade", command=self.submit_assignment,
                 bg="#4CAF50", fg="white", font=("Arial", 10))
        self.submit_button.pack(side="left", padx=5)
        
        self.details_button = tk.Button(assignment_buttons, text="Ver Detalhes", command=self.view_assignment_details,
                 bg="#2196F3", fg="white", font=("Arial", 10))
        self.details_button.pack(side="left", padx=5)
        
        # Bind selection event to update button labels
        self.assignments_tree.bind('<<TreeviewSelect>>', self.on_assignment_selection)
    
    def on_assignment_selection(self, event):
        """Update button labels based on selected assignment type."""
        selection = self.assignments_tree.selection()
        if selection:
            item = self.assignments_tree.item(selection[0])
            assignment_type = item['values'][2] if len(item['values']) > 2 else ""
            
            if assignment_type == "Quiz":
                self.submit_button.config(text="Entregar Quiz")
                self.details_button.config(text="Fazer Quiz")
            else:
                self.submit_button.config(text="Entregar Atividade")
                self.details_button.config(text="Ver Detalhes")
    
    def refresh_data(self):
        """Refresh student data when frame is shown."""
        if self.controller.current_user:
            self.welcome_label.config(
                text=f"Painel do Estudante - Bem-vindo(a), {self.controller.current_user['first_name']}!"
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
        """Load upcoming assignments from the database."""
        self.load_assignments()
    
    def load_assignments(self):
        """Carregar atividades do banco de dados."""
        if not self.controller.current_user:
            return
            
        # Clear existing items
        for item in self.assignments_tree.get_children():
            self.assignments_tree.delete(item)
        
        conn = sqlite3.connect('academic_system.db')
        cursor = conn.cursor()
        
        # Get assignments for courses the student is enrolled in
        cursor.execute('''
            SELECT a.id, a.title, c.name, a.due_date, a.type,
                   CASE WHEN s.id IS NOT NULL THEN 'Entregue' ELSE 'Pendente' END as status
            FROM assignments a
            JOIN courses c ON a.course_id = c.id
            JOIN enrollments e ON c.id = e.course_id
            LEFT JOIN submissions s ON a.id = s.assignment_id AND s.student_id = ?
            WHERE e.user_id = ? AND a.due_date IS NOT NULL
            ORDER BY a.due_date
        ''', (self.controller.current_user['id'], self.controller.current_user['id']))
        
        assignments = cursor.fetchall()
        conn.close()
        
        for assignment in assignments:
            # Translate assignment type to Portuguese
            type_translations = {
                'homework': 'Tarefa',
                'quiz': 'Quiz',
                'project': 'Projeto',
                'exam': 'Prova',
                'assignment': 'Atividade'
            }
            assignment_type = type_translations.get(assignment[4], assignment[4])
            
            self.assignments_tree.insert("", "end", values=(
                assignment[2],  # Course name
                assignment[1],  # Assignment title
                assignment_type,  # Assignment type
                assignment[3],  # Due date
                assignment[5]   # Status
            ), tags=(str(assignment[0]),))  # Store assignment ID in tags
    
    def submit_assignment(self):
        """Entregar uma atividade."""
        selection = self.assignments_tree.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Por favor, selecione uma atividade para entregar.")
            return
        
        item = self.assignments_tree.item(selection[0])
        assignment_id = item['tags'][0]
        assignment_title = item['values'][1]
        course_name = item['values'][0]
        assignment_type = item['values'][2]  # Get the type from the display
        status = item['values'][4]  # Status is now in position 4 (after type)
        
        if status == "Entregue":
            messagebox.showinfo("Info", "Você já entregou esta atividade.")
            return
        
        # Check if it's a quiz and redirect to quiz interface
        if assignment_type == "Quiz":
            # Call view_assignment_details which will handle quiz display
            self.view_assignment_details()
            return
        
        # Create submission window for regular assignments
        submit_window = tk.Toplevel(self.controller)
        submit_window.title(f"Entregar Atividade: {assignment_title}")
        submit_window.geometry("600x500")
        submit_window.transient(self.controller)
        submit_window.grab_set()
        
        tk.Label(submit_window, text=f"Entregar Atividade: {assignment_title}", 
                font=("Arial", 14, "bold")).pack(pady=10)
        tk.Label(submit_window, text=f"Disciplina: {course_name}", 
                font=("Arial", 11)).pack()
        
        # Submission form
        form_frame = tk.Frame(submit_window)
        form_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        tk.Label(form_frame, text="Sua Resposta/Entrega:", font=("Arial", 11, "bold")).pack(anchor='w')
        submission_text = tk.Text(form_frame, height=15, font=("Arial", 10))
        submission_text.pack(fill="both", expand=True, pady=(5, 10))
        
        # File attachment simulation
        tk.Label(form_frame, text="Notas Adicionais:", font=("Arial", 11, "bold")).pack(anchor='w')
        notes_text = tk.Text(form_frame, height=4, font=("Arial", 10))
        notes_text.pack(fill="x", pady=(5, 10))
        
        def submit_work():
            submission_content = submission_text.get(1.0, tk.END).strip()
            notes = notes_text.get(1.0, tk.END).strip()
            
            if not submission_content:
                messagebox.showerror("Erro", "Por favor, insira o conteúdo da sua entrega.")
                return
            
            try:
                conn = sqlite3.connect('academic_system.db')
                cursor = conn.cursor()
                
                from datetime import datetime
                submission_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # Insert submission
                cursor.execute('''
                    INSERT INTO submissions (assignment_id, student_id, submission_date, grade, feedback)
                    VALUES (?, ?, ?, NULL, ?)
                ''', (assignment_id, self.controller.current_user['id'], submission_date, 
                      f"Submission: {submission_content}\n\nNotes: {notes}"))
                
                conn.commit()
                conn.close()
                
                messagebox.showinfo("Sucesso", "Atividade entregue com sucesso!")
                submit_window.destroy()
                
                # Refresh the assignments list
                self.load_deadlines()
                
            except Exception as e:
                messagebox.showerror("Erro", f"Falha ao entregar atividade: {str(e)}")
        
        # Buttons
        button_frame = tk.Frame(submit_window)
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="Entregar Atividade", command=submit_work,
                 bg="#4CAF50", fg="white", font=("Arial", 11), width=15).pack(side="left", padx=5)
        
        tk.Button(button_frame, text="Cancelar", command=submit_window.destroy,
                 bg="#f44336", fg="white", font=("Arial", 11), width=15).pack(side="left", padx=5)
    
    def view_assignment_details(self):
        """Visualizar detalhes da atividade."""
        selection = self.assignments_tree.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Por favor, selecione uma atividade para visualizar.")
            return
        
        item = self.assignments_tree.item(selection[0])
        assignment_id = item['tags'][0]
        
        # Get assignment details
        conn = sqlite3.connect('academic_system.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT title, description, due_date, max_points, type
            FROM assignments WHERE id = ?
        ''', (assignment_id,))
        assignment = cursor.fetchone()
        
        if not assignment:
            conn.close()
            messagebox.showerror("Erro", "Atividade não encontrada.")
            return
        
        title, description, due_date, max_points, assignment_type = assignment
        
        # Check if it's a quiz and get questions
        if assignment_type and assignment_type.lower() == "quiz":
            cursor.execute('''
                SELECT id, question_text, option_a, option_b, option_c, option_d, points
                FROM quiz_questions WHERE assignment_id = ? ORDER BY id
            ''', (assignment_id,))
            questions = cursor.fetchall()
            conn.close()
            
            # Show quiz interface
            self.show_quiz_interface(assignment_id, title, description, due_date, max_points, questions)
        else:
            conn.close()
            # Show regular assignment details
            self.show_regular_assignment_details(assignment_id, title, description, due_date, max_points)
    
    def show_quiz_interface(self, assignment_id, title, description, due_date, max_points, questions):
        """Mostrar interface do quiz para o estudante."""
        quiz_window = tk.Toplevel(self.controller)
        quiz_window.title(f"Quiz: {title}")
        quiz_window.geometry("700x600")
        quiz_window.transient(self.controller)
        quiz_window.grab_set()
        
        # Header
        header_frame = tk.Frame(quiz_window, bg="#2196F3")
        header_frame.pack(fill="x", pady=(0, 10))
        
        tk.Label(header_frame, text=f"📝 Quiz: {title}", 
                font=("Arial", 16, "bold"), bg="#2196F3", fg="white").pack(pady=10)
        
        info_frame = tk.Frame(quiz_window)
        info_frame.pack(fill="x", padx=20, pady=5)
        
        tk.Label(info_frame, text=f"Data de Entrega: {due_date}", 
                font=("Arial", 11)).pack(anchor='w')
        tk.Label(info_frame, text=f"Pontuação Total: {max_points} pontos", 
                font=("Arial", 11)).pack(anchor='w')
        tk.Label(info_frame, text=f"Número de Questões: {len(questions)}", 
                font=("Arial", 11)).pack(anchor='w')
        
        if description:
            tk.Label(info_frame, text=f"Descrição: {description}", 
                    font=("Arial", 10), wraplength=600).pack(anchor='w', pady=(5, 0))
        
        # Check if already submitted
        conn = sqlite3.connect('academic_system.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, grade, submitted_at FROM submissions 
            WHERE assignment_id = ? AND student_id = ?
        ''', (assignment_id, self.controller.current_user['id']))
        submission = cursor.fetchone()
        conn.close()
        
        if submission:
            tk.Label(quiz_window, text="✅ Você já respondeu este quiz!", 
                    font=("Arial", 12, "bold"), fg="green").pack(pady=10)
            
            if submission[1] is not None:  # Grade available
                tk.Label(quiz_window, text=f"Sua nota: {submission[1]}/{max_points}", 
                        font=("Arial", 12, "bold"), fg="blue").pack()
            
            tk.Label(quiz_window, text=f"Entregue em: {submission[2]}", 
                    font=("Arial", 10)).pack()
            
            # Show answers button
            def show_quiz_results():
                self.show_quiz_results(assignment_id, questions, submission[0])
            
            tk.Button(quiz_window, text="Ver Respostas", command=show_quiz_results,
                     bg="#FF9800", fg="white", font=("Arial", 11)).pack(pady=10)
        else:
            # Show quiz questions for answering
            self.show_quiz_questions(quiz_window, assignment_id, questions, max_points)
        
        tk.Button(quiz_window, text="Fechar", command=quiz_window.destroy,
                 bg="#f44336", fg="white", font=("Arial", 11)).pack(pady=10)
    
    def show_quiz_questions(self, parent_window, assignment_id, questions, max_points):
        """Mostrar questões do quiz para responder."""
        # Create a frame to hold canvas and submit button separately
        content_frame = tk.Frame(parent_window)
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Scrollable frame for questions
        canvas = tk.Canvas(content_frame)
        scrollbar = tk.Scrollbar(content_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Mouse wheel scrolling support
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Store answers
        answers = {}
        
        for i, question in enumerate(questions, 1):
            q_id, q_text, opt_a, opt_b, opt_c, opt_d, points = question
            
            # Question frame with better spacing
            q_frame = tk.LabelFrame(scrollable_frame, text=f"Questão {i} ({points} pontos)", 
                                   font=("Arial", 11, "bold"), padx=10, pady=10)
            q_frame.pack(fill="x", pady=10, padx=10)
            
            # Question text
            tk.Label(q_frame, text=q_text, font=("Arial", 11), 
                    wraplength=600, justify="left").pack(anchor='w', pady=(0, 10))
            
            # Answer options
            answer_var = tk.StringVar()
            answers[q_id] = answer_var
            
            for letter, option_text in [('A', opt_a), ('B', opt_b), ('C', opt_c), ('D', opt_d)]:
                tk.Radiobutton(q_frame, text=f"{letter}) {option_text}", 
                              variable=answer_var, value=letter,
                              font=("Arial", 10), wraplength=550).pack(anchor='w', pady=2)
        
        # Submit button
        def submit_quiz():
            # Check if all questions are answered
            unanswered = []
            for q_id, answer_var in answers.items():
                if not answer_var.get():
                    unanswered.append(q_id)
            
            if unanswered:
                messagebox.showwarning("Aviso", 
                                     f"Por favor, responda todas as questões antes de entregar.\n"
                                     f"Questões não respondidas: {len(unanswered)}")
                return
            
            # Confirm submission
            if not messagebox.askyesno("Confirmar", 
                                     "Tem certeza de que deseja entregar o quiz?\n"
                                     "Você não poderá alterar suas respostas depois."):
                return
            
            try:
                conn = sqlite3.connect('academic_system.db')
                cursor = conn.cursor()
                
                # Create submission
                cursor.execute('''
                    INSERT INTO submissions (assignment_id, student_id, content, submitted_at)
                    VALUES (?, ?, ?, datetime('now'))
                ''', (assignment_id, self.controller.current_user['id'], "Quiz submission"))
                
                submission_id = cursor.lastrowid
                
                # Save answers and calculate score
                total_score = 0
                total_possible = 0
                
                for question in questions:
                    q_id, q_text, opt_a, opt_b, opt_c, opt_d, points = question
                    
                    # Get correct answer
                    cursor.execute('''
                        SELECT correct_answer FROM quiz_questions WHERE id = ?
                    ''', (q_id,))
                    correct_answer = cursor.fetchone()[0]
                    
                    selected_answer = answers[q_id].get()
                    is_correct = selected_answer == correct_answer
                    
                    if is_correct:
                        total_score += points
                    total_possible += points
                    
                    # Save answer
                    cursor.execute('''
                        INSERT INTO quiz_answers (submission_id, question_id, selected_answer, is_correct)
                        VALUES (?, ?, ?, ?)
                    ''', (submission_id, q_id, selected_answer, is_correct))
                
                # Update submission with grade
                final_grade = (total_score / total_possible) * max_points if total_possible > 0 else 0
                cursor.execute('''
                    UPDATE submissions SET grade = ? WHERE id = ?
                ''', (final_grade, submission_id))
                
                conn.commit()
                conn.close()
                
                messagebox.showinfo("Sucesso", 
                                  f"Quiz entregue com sucesso!\n\n"
                                  f"Sua pontuação: {total_score}/{total_possible} questões corretas\n"
                                  f"Nota final: {final_grade:.1f}/{max_points}")
                
                parent_window.destroy()
                self.load_assignments()  # Refresh assignments list
                
            except Exception as e:
                messagebox.showerror("Erro", f"Falha ao entregar quiz: {str(e)}")
        
        # Submit button outside of scroll area
        button_frame = tk.Frame(parent_window)
        button_frame.pack(side="bottom", fill="x", pady=10)
        
        tk.Button(button_frame, text="Entregar Quiz", command=submit_quiz,
                 bg="#4CAF50", fg="white", font=("Arial", 12, "bold")).pack(pady=10)
    
    def show_regular_assignment_details(self, assignment_id, title, description, due_date, max_points):
        """Mostrar detalhes de atividade regular."""
        # Create details window
        details_window = tk.Toplevel(self.controller)
        details_window.title(f"Detalhes da Atividade: {title}")
        details_window.geometry("500x400")
        details_window.transient(self.controller)
        details_window.grab_set()
        
        tk.Label(details_window, text=title, 
                font=("Arial", 14, "bold")).pack(pady=10)
        
        info_frame = tk.Frame(details_window)
        info_frame.pack(fill="x", padx=20, pady=5)
        
        tk.Label(info_frame, text=f"Data de Entrega: {due_date}", 
                font=("Arial", 11)).pack(anchor='w')
        tk.Label(info_frame, text=f"Pontuação Máxima: {max_points}", 
                font=("Arial", 11)).pack(anchor='w')
        
        tk.Label(details_window, text="Descrição:", 
                font=("Arial", 11, "bold")).pack(anchor='w', padx=20, pady=(10, 5))
        
        desc_text = tk.Text(details_window, height=15, font=("Arial", 10))
        desc_text.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        desc_text.insert(1.0, description or "Nenhuma descrição disponível.")
        desc_text.config(state="disabled")
        
        tk.Button(details_window, text="Fechar", command=details_window.destroy,
                 bg="#f44336", fg="white", font=("Arial", 11)).pack(pady=10)

    def show_quiz_results(self, assignment_id, questions, submission_id):
        """Mostrar resultados do quiz com respostas corretas e incorretas."""
        results_window = tk.Toplevel(self.controller)
        results_window.title("Resultados do Quiz")
        results_window.geometry("800x600")
        results_window.transient(self.controller)
        results_window.grab_set()
        
        # Get user's answers
        conn = sqlite3.connect('academic_system.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT qa.question_id, qa.selected_answer, qa.is_correct,
                   qq.question_text, qq.option_a, qq.option_b, qq.option_c, qq.option_d, 
                   qq.correct_answer, qq.points
            FROM quiz_answers qa
            JOIN quiz_questions qq ON qa.question_id = qq.id
            WHERE qa.submission_id = ?
            ORDER BY qq.id
        ''', (submission_id,))
        user_answers = cursor.fetchall()
        
        # Get overall grade
        cursor.execute('''
            SELECT grade FROM submissions WHERE id = ?
        ''', (submission_id,))
        grade = cursor.fetchone()[0]
        
        cursor.execute('''
            SELECT max_points FROM assignments WHERE id = ?
        ''', (assignment_id,))
        max_points = cursor.fetchone()[0]
        
        conn.close()
        
        # Header
        tk.Label(results_window, text="📊 Resultados do Quiz", 
                font=("Arial", 16, "bold")).pack(pady=10)
        
        tk.Label(results_window, text=f"Nota Final: {grade:.1f}/{max_points}", 
                font=("Arial", 14, "bold"), fg="blue").pack(pady=5)
        
        # Scrollable frame
        canvas = tk.Canvas(results_window)
        scrollbar = tk.Scrollbar(results_window, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=20)
        scrollbar.pack(side="right", fill="y")
        
        # Show each question and answer
        correct_count = 0
        for i, answer_data in enumerate(user_answers, 1):
            (q_id, selected, is_correct, q_text, opt_a, opt_b, opt_c, opt_d, 
             correct_answer, points) = answer_data
            
            if is_correct:
                correct_count += 1
            
            # Question frame with color coding
            bg_color = "#e8f5e8" if is_correct else "#ffeaea"
            q_frame = tk.LabelFrame(scrollable_frame, 
                                   text=f"Questão {i} ({'✓ Correto' if is_correct else '✗ Incorreto'}) - {points} pontos", 
                                   font=("Arial", 11, "bold"), 
                                   bg=bg_color, padx=10, pady=10)
            q_frame.pack(fill="x", pady=10, padx=10)
            
            # Question text
            tk.Label(q_frame, text=q_text, font=("Arial", 11), 
                    wraplength=700, justify="left", bg=bg_color).pack(anchor='w', pady=(0, 10))
            
            # Show all options with indicators
            options = {'A': opt_a, 'B': opt_b, 'C': opt_c, 'D': opt_d}
            
            for letter, option_text in options.items():
                option_frame = tk.Frame(q_frame, bg=bg_color)
                option_frame.pack(fill="x", pady=2)
                
                # Create indicator text
                indicator = ""
                text_color = "black"
                
                if letter == correct_answer:
                    indicator = "✓ (Resposta Correta)"
                    text_color = "green"
                elif letter == selected and letter != correct_answer:
                    indicator = "✗ (Sua Resposta)"
                    text_color = "red"
                elif letter == selected and letter == correct_answer:
                    indicator = "✓ (Sua Resposta Correta)"
                    text_color = "green"
                
                option_label = f"{letter}) {option_text}"
                if indicator:
                    option_label += f" {indicator}"
                
                tk.Label(option_frame, text=option_label, 
                        font=("Arial", 10), fg=text_color, bg=bg_color,
                        wraplength=650, justify="left").pack(anchor='w')
        
        # Summary
        summary_frame = tk.Frame(scrollable_frame, bg="#f0f0f0", relief="ridge", bd=2)
        summary_frame.pack(fill="x", pady=20, padx=10)
        
        tk.Label(summary_frame, text="📈 Resumo", 
                font=("Arial", 12, "bold"), bg="#f0f0f0").pack(pady=5)
        
        tk.Label(summary_frame, 
                text=f"Questões Corretas: {correct_count}/{len(user_answers)}", 
                font=("Arial", 11), bg="#f0f0f0").pack()
        
        percentage = (correct_count / len(user_answers)) * 100 if user_answers else 0
        tk.Label(summary_frame, 
                text=f"Porcentagem de Acerto: {percentage:.1f}%", 
                font=("Arial", 11), bg="#f0f0f0").pack()
        
        tk.Button(results_window, text="Fechar", command=results_window.destroy,
                 bg="#f44336", fg="white", font=("Arial", 11)).pack(pady=10)


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
        
        self.welcome_label = tk.Label(header_frame, text="Painel da Secretaria", 
                                     font=("Arial", 16, "bold"))
        self.welcome_label.pack(side="left")
        
        logout_btn = tk.Button(header_frame, text="Sair", command=controller.logout,
                              bg="#f44336", fg="white")
        logout_btn.pack(side="right")
        
        # Main content
        content_frame = tk.Frame(self)
        content_frame.pack(fill="both", expand=True, padx=20, pady=50)
        
        tk.Label(content_frame, text="Funções da Secretaria", 
                font=("Arial", 14, "bold")).pack(pady=20)
        
        # Excel import button
        tk.Button(content_frame, text="Importar Estudantes do Excel", 
                 font=("Arial", 11), width=30, height=2,
                 bg="#4CAF50", fg="white",
                 command=self.import_students_excel).pack(pady=10)
        
        # C module integration button
        tk.Button(content_frame, text="Registrar Estudante (Módulo C)", 
                 font=("Arial", 11), width=30, height=2,
                 bg="#2196F3", fg="white",
                 command=self.register_student_c_module).pack(pady=10)
        
        # Other functions
        other_functions = [
            ("Gerenciar Registros de Estudantes", self.manage_student_records),
            ("Ver Todos os Estudantes", self.view_all_students),
            ("Processar Matrículas", self.process_enrollments),
            ("Gerar Relatórios de Estudantes", self.generate_student_reports)
        ]
        
        for func_name, func_command in other_functions:
            tk.Button(content_frame, text=func_name, font=("Arial", 11),
                     width=30, height=2, command=func_command).pack(pady=5)
    
    def refresh_data(self):
        """Refresh secretary data when frame is shown."""
        if self.controller.current_user:
            self.welcome_label.config(
                text=f"Painel da Secretaria - Bem-vinda, {self.controller.current_user['first_name']}!"
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
            message = f"Importados {imported_count} estudantes com sucesso."
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
        register_window.title("Registrar Estudante (Módulo C)")
        register_window.geometry("400x500")
        register_window.transient(self.controller)
        register_window.grab_set()
        
        tk.Label(register_window, text="Register New Student", 
                font=("Arial", 14, "bold")).pack(pady=20)
        
        # Form fields
        tk.Label(register_window, text="Primeiro Nome:").pack()
        first_name_entry = tk.Entry(register_window, font=("Arial", 11), width=30)
        first_name_entry.pack(pady=5)
        
        tk.Label(register_window, text="Último Nome:").pack()
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
                    
                    messagebox.showinfo("Sucesso", 
                                      f"Estudante '{first_name} {last_name}' registrado com sucesso via módulo C!\n"
                                      f"Usuário: {username}\n"
                                      f"ID do Estudante: {result['student_id']}{course_info}")
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
        columns = ("ID", "Usuário", "Primeiro Nome", "Último Nome", "Email", "Cursos Matriculados")
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
    
    def process_enrollments(self):
        """Process student enrollments in courses."""
        enrollment_window = tk.Toplevel(self.controller)
        enrollment_window.title("Process Student Enrollments")
        enrollment_window.geometry("600x500")
        enrollment_window.transient(self.controller)
        enrollment_window.grab_set()
        
        tk.Label(enrollment_window, text="Student Course Enrollments", 
                font=("Arial", 14, "bold")).pack(pady=10)
        
        # Create main frame
        main_frame = tk.Frame(enrollment_window)
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Student selection
        student_frame = tk.LabelFrame(main_frame, text="Select Student", font=("Arial", 12, "bold"))
        student_frame.pack(fill="x", pady=5)
        
        tk.Label(student_frame, text="Student:").pack(side="left", padx=5)
        student_combo = ttk.Combobox(student_frame, font=("Arial", 10), state="readonly", width=30)
        student_combo.pack(side="left", padx=5, pady=10)
        
        # Load students
        conn = sqlite3.connect('academic_system.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, first_name || ' ' || last_name || ' (' || username || ')' as display_name
            FROM users WHERE role = 'STUDENT' ORDER BY first_name, last_name
        ''')
        students = cursor.fetchall()
        conn.close()
        
        student_list = [f"{student[1]} (ID: {student[0]})" for student in students]
        student_combo['values'] = student_list
        
        # Course selection
        course_frame = tk.LabelFrame(main_frame, text="Available Courses", font=("Arial", 12, "bold"))
        course_frame.pack(fill="both", expand=True, pady=5)
        
        # Create frame for course checkboxes
        courses_scroll_frame = tk.Frame(course_frame)
        courses_scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Get courses
        conn = sqlite3.connect('academic_system.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id, name FROM courses ORDER BY name')
        courses = cursor.fetchall()
        conn.close()
        
        course_vars = {}
        for course_id, course_name in courses:
            var = tk.BooleanVar()
            course_vars[course_id] = var
            tk.Checkbutton(courses_scroll_frame, text=course_name, variable=var,
                          font=("Arial", 10)).pack(anchor='w', pady=2)
        
        # Current enrollments display
        current_frame = tk.LabelFrame(main_frame, text="Current Enrollments", font=("Arial", 12, "bold"))
        current_frame.pack(fill="x", pady=5)
        
        current_text = tk.Text(current_frame, height=4, font=("Arial", 9))
        current_text.pack(fill="x", padx=10, pady=5)
        
        def update_current_enrollments():
            """Update the display of current enrollments for selected student."""
            selection = student_combo.get()
            if not selection:
                current_text.delete(1.0, tk.END)
                return
            
            student_id = int(selection.split("ID: ")[1].rstrip(")"))
            
            conn = sqlite3.connect('academic_system.db')
            cursor = conn.cursor()
            cursor.execute('''
                SELECT c.name FROM courses c
                JOIN enrollments e ON c.id = e.course_id
                WHERE e.user_id = ?
            ''', (student_id,))
            enrolled_courses = cursor.fetchall()
            conn.close()
            
            current_text.delete(1.0, tk.END)
            if enrolled_courses:
                current_text.insert(tk.END, "Currently enrolled in:\n")
                for course in enrolled_courses:
                    current_text.insert(tk.END, f"• {course[0]}\n")
            else:
                current_text.insert(tk.END, "Not enrolled in any courses.")
        
        student_combo.bind('<<ComboboxSelected>>', lambda e: update_current_enrollments())
        
        def process_enrollment():
            """Process the enrollment changes."""
            selection = student_combo.get()
            if not selection:
                messagebox.showerror("Error", "Please select a student.")
                return
            
            student_id = int(selection.split("ID: ")[1].rstrip(")"))
            selected_courses = [course_id for course_id, var in course_vars.items() if var.get()]
            
            if not selected_courses:
                messagebox.showwarning("Aviso", "Por favor, selecione pelo menos um curso.")
                return
            
            try:
                conn = sqlite3.connect('academic_system.db')
                cursor = conn.cursor()
                
                enrolled_count = 0
                for course_id in selected_courses:
                    cursor.execute('''
                        INSERT OR IGNORE INTO enrollments (user_id, course_id)
                        VALUES (?, ?)
                    ''', (student_id, course_id))
                    if cursor.rowcount > 0:
                        enrolled_count += 1
                
                conn.commit()
                conn.close()
                
                messagebox.showinfo("Sucesso", 
                                  f"Estudante matriculado com sucesso em {enrolled_count} novo(s) curso(s).")
                update_current_enrollments()
                
                # Clear course selections
                for var in course_vars.values():
                    var.set(False)
                    
            except Exception as e:
                messagebox.showerror("Error", f"Failed to process enrollment: {str(e)}")
        
        # Buttons
        button_frame = tk.Frame(enrollment_window)
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="Enroll in Selected Courses", 
                 command=process_enrollment, bg="#4CAF50", fg="white",
                 font=("Arial", 11), width=20).pack(side="left", padx=5)
        
        tk.Button(button_frame, text="Close", command=enrollment_window.destroy,
                 bg="#f44336", fg="white", font=("Arial", 11), width=15).pack(side="left", padx=5)
    
    def generate_student_reports(self):
        """Generate various student reports."""
        reports_window = tk.Toplevel(self.controller)
        reports_window.title("Generate Student Reports")
        reports_window.geometry("500x400")
        reports_window.transient(self.controller)
        reports_window.grab_set()
        
        tk.Label(reports_window, text="Student Reports Generator", 
                font=("Arial", 14, "bold")).pack(pady=20)
        
        # Report type selection
        report_frame = tk.LabelFrame(reports_window, text="Select Report Type", 
                                   font=("Arial", 12, "bold"))
        report_frame.pack(fill="x", padx=20, pady=10)
        
        report_var = tk.StringVar(value="enrollment")
        
        report_options = [
            ("enrollment", "Student Enrollment Report"),
            ("academic", "Academic Performance Report"), 
            ("contact", "Student Contact Information"),
            ("summary", "Complete Student Summary")
        ]
        
        for value, text in report_options:
            tk.Radiobutton(report_frame, text=text, variable=report_var, value=value,
                          font=("Arial", 10)).pack(anchor='w', padx=10, pady=5)
        
        # Output format
        format_frame = tk.LabelFrame(reports_window, text="Output Format", 
                                   font=("Arial", 12, "bold"))
        format_frame.pack(fill="x", padx=20, pady=10)
        
        format_var = tk.StringVar(value="display")
        
        tk.Radiobutton(format_frame, text="Display in Window", variable=format_var, 
                      value="display", font=("Arial", 10)).pack(anchor='w', padx=10, pady=5)
        tk.Radiobutton(format_frame, text="Export to CSV File", variable=format_var, 
                      value="csv", font=("Arial", 10)).pack(anchor='w', padx=10, pady=5)
        
        def generate_report():
            """Generate the selected report."""
            report_type = report_var.get()
            output_format = format_var.get()
            
            try:
                conn = sqlite3.connect('academic_system.db')
                cursor = conn.cursor()
                
                if report_type == "enrollment":
                    cursor.execute('''
                        SELECT u.first_name || ' ' || u.last_name as name, u.email,
                               GROUP_CONCAT(c.name, ', ') as courses
                        FROM users u
                        LEFT JOIN enrollments e ON u.id = e.user_id
                        LEFT JOIN courses c ON e.course_id = c.id
                        WHERE u.role = 'STUDENT'
                        GROUP BY u.id, u.first_name, u.last_name, u.email
                        ORDER BY u.first_name, u.last_name
                    ''')
                    columns = ["Student Name", "Email", "Enrolled Courses"]
                    
                elif report_type == "academic":
                    cursor.execute('''
                        SELECT u.first_name || ' ' || u.last_name as name,
                               c.name as course, COALESCE(AVG(s.grade), 0) as avg_grade
                        FROM users u
                        JOIN enrollments e ON u.id = e.user_id
                        JOIN courses c ON e.course_id = c.id
                        LEFT JOIN submissions s ON u.id = s.student_id
                        LEFT JOIN assignments a ON s.assignment_id = a.id AND a.course_id = c.id
                        WHERE u.role = 'STUDENT'
                        GROUP BY u.id, c.id
                        ORDER BY u.first_name, u.last_name, c.name
                    ''')
                    columns = ["Student Name", "Course", "Average Grade"]
                    
                elif report_type == "contact":
                    cursor.execute('''
                        SELECT first_name || ' ' || last_name as name, 
                               username, email
                        FROM users WHERE role = 'STUDENT'
                        ORDER BY first_name, last_name
                    ''')
                    columns = ["Student Name", "Username", "Email"]
                    
                else:  # summary
                    cursor.execute('''
                        SELECT u.first_name || ' ' || u.last_name as name,
                               u.username, u.email,
                               COUNT(DISTINCT e.course_id) as course_count,
                               COALESCE(AVG(s.grade), 0) as overall_avg
                        FROM users u
                        LEFT JOIN enrollments e ON u.id = e.user_id
                        LEFT JOIN submissions s ON u.id = s.student_id
                        WHERE u.role = 'STUDENT'
                        GROUP BY u.id
                        ORDER BY u.first_name, u.last_name
                    ''')
                    columns = ["Student Name", "Username", "Email", "Enrolled Courses", "Overall Average"]
                
                data = cursor.fetchall()
                conn.close()
                
                if output_format == "display":
                    self.display_report(data, columns, report_type)
                else:
                    self.export_report_csv(data, columns, report_type)
                    
            except Exception as e:
                messagebox.showerror("Erro", f"Falha ao gerar relatório: {str(e)}")
        
        # Buttons
        button_frame = tk.Frame(reports_window)
        button_frame.pack(pady=20)
        
        tk.Button(button_frame, text="Gerar Relatório", command=generate_report,
                 bg="#4CAF50", fg="white", font=("Arial", 11), width=15).pack(side="left", padx=5)
        
        tk.Button(button_frame, text="Close", command=reports_window.destroy,
                 bg="#f44336", fg="white", font=("Arial", 11), width=15).pack(side="left", padx=5)
    
    def display_report(self, data, columns, report_type):
        """Display report in a new window."""
        display_window = tk.Toplevel(self.controller)
        display_window.title(f"Report: {report_type.title()}")
        display_window.geometry("800x600")
        display_window.transient(self.controller)
        
        tk.Label(display_window, text=f"{report_type.title()} Report", 
                font=("Arial", 14, "bold")).pack(pady=10)
        
        # Create frame for treeview
        frame = tk.Frame(display_window)
        frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Create Treeview
        tree = ttk.Treeview(frame, columns=columns, show="headings", height=20)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)
        
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Insert data
        for row in data:
            # Format the data appropriately
            formatted_row = []
            for i, item in enumerate(row):
                if item is None:
                    formatted_row.append("N/A")
                elif isinstance(item, float):
                    formatted_row.append(f"{item:.1f}")
                else:
                    formatted_row.append(str(item))
            tree.insert("", "end", values=formatted_row)
        
        tk.Button(display_window, text="Close", command=display_window.destroy,
                 bg="#f44336", fg="white", font=("Arial", 11)).pack(pady=10)
    
    def export_report_csv(self, data, columns, report_type):
        """Export report to CSV file."""
        try:
            import csv
            from datetime import datetime
            
            filename = f"student_{report_type}_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(columns)
                
                for row in data:
                    # Handle None values and format numbers
                    formatted_row = []
                    for item in row:
                        if item is None:
                            formatted_row.append("N/A")
                        elif isinstance(item, float):
                            formatted_row.append(f"{item:.1f}")
                        else:
                            formatted_row.append(str(item))
                    writer.writerow(formatted_row)
            
            messagebox.showinfo("Export Complete", 
                              f"Relatório exportado com sucesso para:\n{filename}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export report: {str(e)}")
    
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
        tk.Button(content_frame, text="Gerar Relatórios (Módulo C)", 
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
                                  f"Relatórios institucionais gerados com sucesso!\n\n"
                                  f"Generated files:\n"
                                  f"• {result['enrollment_report']}\n"
                                  f"• {result['performance_report']}\n"
                                  f"• {result['financial_report']}")
            else:
                messagebox.showerror("Error", f"Report generation failed: {result['error']}")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao gerar relatórios: {str(e)}")
    
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
