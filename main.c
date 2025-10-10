#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sqlite3.h>

// Estrutura para armazenar dados do usuário
typedef struct {
    int id;
    char username[100];
    char password[100];
    char first_name[100];
    char last_name[100];
    char email[150];
    char role[20];
} User;

// Função para validar login
int validate_login(const char* username, const char* password, User* user) {
    sqlite3 *db;
    sqlite3_stmt *stmt;
    int rc;
    int result = 0;
    
    // Abrir banco de dados
    rc = sqlite3_open("academic_system.db", &db);
    if (rc != SQLITE_OK) {
        fprintf(stderr, "Erro ao abrir banco de dados: %s\n", sqlite3_errmsg(db));
        return 0;
    }
    
    // Preparar query
    const char *sql = "SELECT id, username, password, first_name, last_name, email, role "
                     "FROM users WHERE username = ? AND password = ?";
    
    rc = sqlite3_prepare_v2(db, sql, -1, &stmt, NULL);
    if (rc != SQLITE_OK) {
        fprintf(stderr, "Erro ao preparar statement: %s\n", sqlite3_errmsg(db));
        sqlite3_close(db);
        return 0;
    }
    
    // Bind dos parâmetros
    sqlite3_bind_text(stmt, 1, username, -1, SQLITE_STATIC);
    sqlite3_bind_text(stmt, 2, password, -1, SQLITE_STATIC);
    
    // Executar query
    if (sqlite3_step(stmt) == SQLITE_ROW) {
        // Login válido - copiar dados do usuário
        user->id = sqlite3_column_int(stmt, 0);
        strncpy(user->username, (const char*)sqlite3_column_text(stmt, 1), 99);
        strncpy(user->password, (const char*)sqlite3_column_text(stmt, 2), 99);
        strncpy(user->first_name, (const char*)sqlite3_column_text(stmt, 3), 99);
        strncpy(user->last_name, (const char*)sqlite3_column_text(stmt, 4), 99);
        strncpy(user->email, (const char*)sqlite3_column_text(stmt, 5), 149);
        strncpy(user->role, (const char*)sqlite3_column_text(stmt, 6), 19);
        result = 1;
    }
    
    sqlite3_finalize(stmt);
    sqlite3_close(db);
    
    return result;
}

// Função para registrar novo estudante
int register_student(const char* username, const char* password, 
                    const char* first_name, const char* last_name, 
                    const char* email) {
    sqlite3 *db;
    sqlite3_stmt *stmt;
    int rc;
    int student_id = -1;
    
    // Abrir banco de dados
    rc = sqlite3_open("academic_system.db", &db);
    if (rc != SQLITE_OK) {
        fprintf(stderr, "Erro ao abrir banco de dados: %s\n", sqlite3_errmsg(db));
        return -1;
    }
    
    // Verificar se username já existe
    const char *check_sql = "SELECT id FROM users WHERE username = ?";
    rc = sqlite3_prepare_v2(db, check_sql, -1, &stmt, NULL);
    if (rc != SQLITE_OK) {
        fprintf(stderr, "Erro ao preparar statement: %s\n", sqlite3_errmsg(db));
        sqlite3_close(db);
        return -1;
    }
    
    sqlite3_bind_text(stmt, 1, username, -1, SQLITE_STATIC);
    
    if (sqlite3_step(stmt) == SQLITE_ROW) {
        // Username já existe
        fprintf(stderr, "ERRO: Username '%s' já existe\n", username);
        sqlite3_finalize(stmt);
        sqlite3_close(db);
        return -2;
    }
    sqlite3_finalize(stmt);
    
    // Inserir novo estudante
    const char *insert_sql = "INSERT INTO users (username, password, first_name, last_name, email, role) "
                            "VALUES (?, ?, ?, ?, ?, 'STUDENT')";
    
    rc = sqlite3_prepare_v2(db, insert_sql, -1, &stmt, NULL);
    if (rc != SQLITE_OK) {
        fprintf(stderr, "Erro ao preparar statement: %s\n", sqlite3_errmsg(db));
        sqlite3_close(db);
        return -1;
    }
    
    // Bind dos parâmetros
    sqlite3_bind_text(stmt, 1, username, -1, SQLITE_STATIC);
    sqlite3_bind_text(stmt, 2, password, -1, SQLITE_STATIC);
    sqlite3_bind_text(stmt, 3, first_name, -1, SQLITE_STATIC);
    sqlite3_bind_text(stmt, 4, last_name, -1, SQLITE_STATIC);
    sqlite3_bind_text(stmt, 5, email, -1, SQLITE_STATIC);
    
    // Executar insert
    rc = sqlite3_step(stmt);
    if (rc == SQLITE_DONE) {
        student_id = (int)sqlite3_last_insert_rowid(db);
        printf("SUCESSO: Estudante registrado com ID: %d\n", student_id);
    } else {
        fprintf(stderr, "Erro ao inserir estudante: %s\n", sqlite3_errmsg(db));
    }
    
    sqlite3_finalize(stmt);
    sqlite3_close(db);
    
    return student_id;
}

// Função para matricular estudante em curso
int enroll_student(int student_id, int course_id) {
    sqlite3 *db;
    sqlite3_stmt *stmt;
    int rc;
    
    // Abrir banco de dados
    rc = sqlite3_open("academic_system.db", &db);
    if (rc != SQLITE_OK) {
        fprintf(stderr, "Erro ao abrir banco de dados: %s\n", sqlite3_errmsg(db));
        return 0;
    }
    
    // Inserir matrícula
    const char *sql = "INSERT OR IGNORE INTO enrollments (user_id, course_id) VALUES (?, ?)";
    
    rc = sqlite3_prepare_v2(db, sql, -1, &stmt, NULL);
    if (rc != SQLITE_OK) {
        fprintf(stderr, "Erro ao preparar statement: %s\n", sqlite3_errmsg(db));
        sqlite3_close(db);
        return 0;
    }
    
    sqlite3_bind_int(stmt, 1, student_id);
    sqlite3_bind_int(stmt, 2, course_id);
    
    rc = sqlite3_step(stmt);
    int success = (rc == SQLITE_DONE) ? 1 : 0;
    
    sqlite3_finalize(stmt);
    sqlite3_close(db);
    
    return success;
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Uso: %s <comando> [argumentos]\n", argv[0]);
        fprintf(stderr, "Comandos disponíveis:\n");
        fprintf(stderr, "  login <username> <password>\n");
        fprintf(stderr, "  register <username> <password> <first_name> <last_name> <email>\n");
        fprintf(stderr, "  enroll <student_id> <course_id>\n");
        return 1;
    }
    
    const char *command = argv[1];
    
    // Comando LOGIN
    if (strcmp(command, "login") == 0) {
        if (argc != 4) {
            fprintf(stderr, "Uso: %s login <username> <password>\n", argv[0]);
            return 1;
        }
        
        User user;
        if (validate_login(argv[2], argv[3], &user)) {
            printf("LOGIN_SUCCESS\n");
            printf("USER_ID:%d\n", user.id);
            printf("USERNAME:%s\n", user.username);
            printf("FIRST_NAME:%s\n", user.first_name);
            printf("LAST_NAME:%s\n", user.last_name);
            printf("EMAIL:%s\n", user.email);
            printf("ROLE:%s\n", user.role);
            return 0;
        } else {
            printf("LOGIN_FAILED\n");
            return 1;
        }
    }
    
    // Comando REGISTER
    else if (strcmp(command, "register") == 0) {
        if (argc != 7) {
            fprintf(stderr, "Uso: %s register <username> <password> <first_name> <last_name> <email>\n", argv[0]);
            return 1;
        }
        
        int student_id = register_student(argv[2], argv[3], argv[4], argv[5], argv[6]);
        
        if (student_id > 0) {
            printf("REGISTER_SUCCESS\n");
            printf("STUDENT_ID:%d\n", student_id);
            return 0;
        } else if (student_id == -2) {
            printf("REGISTER_FAILED:USERNAME_EXISTS\n");
            return 2;
        } else {
            printf("REGISTER_FAILED:DATABASE_ERROR\n");
            return 1;
        }
    }
    
    // Comando ENROLL
    else if (strcmp(command, "enroll") == 0) {
        if (argc != 4) {
            fprintf(stderr, "Uso: %s enroll <student_id> <course_id>\n", argv[0]);
            return 1;
        }
        
        int student_id = atoi(argv[2]);
        int course_id = atoi(argv[3]);
        
        if (enroll_student(student_id, course_id)) {
            printf("ENROLL_SUCCESS\n");
            return 0;
        } else {
            printf("ENROLL_FAILED\n");
            return 1;
        }
    }
    
    else {
        fprintf(stderr, "Comando desconhecido: %s\n", command);
        return 1;
    }
    
    return 0;
}
