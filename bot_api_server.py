"""
Простой API сервер для доступа к SQLite БД бота
Запускайте этот файл на сервере с ботом (Linux)
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os
import logging

app = Flask(__name__)
CORS(app)  # Разрешаем запросы с других доменов

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Путь к БД бота
DB_PATH = 'students.db'  # Или укажите полный путь: '/path/to/students.db'

def get_db_connection():
    """Получение подключения к SQLite БД"""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/api/health', methods=['GET'])
def health():
    """Проверка работоспособности API"""
    return jsonify({'status': 'ok', 'db_exists': os.path.exists(DB_PATH)})

@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Получение информации о пользователе"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT user_id, role, full_name FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return jsonify(dict(user))
    return jsonify({'error': 'User not found'}), 404

@app.route('/api/student/<int:student_id>/grades', methods=['GET'])
def get_student_grades(student_id):
    """Получение оценок студента"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT g.grade, g.date, d.name as discipline, u.full_name as teacher, 
               COALESCE(k.description, 'Нет описания КТП') as description,
               COALESCE(k.homework, 'Нет домашнего задания') as homework
        FROM grades g
        JOIN disciplines d ON g.discipline_id = d.discipline_id
        JOIN users u ON g.teacher_id = u.user_id
        LEFT JOIN ktp k ON g.ktp_id = k.ktp_id
        WHERE g.student_id = ?
        ORDER BY g.date DESC
    """, (student_id,))
    
    grades = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    # Преобразуем -1 в "н"
    for grade in grades:
        if grade['grade'] == -1:
            grade['grade'] = 'н'
    
    return jsonify(grades)

@app.route('/api/student/<int:student_id>/teachers', methods=['GET'])
def get_student_teachers(student_id):
    """Получение преподавателей студента"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT t.teacher_id, u.full_name, st.tokens 
        FROM student_teacher st
        JOIN teachers t ON st.teacher_id = t.teacher_id
        JOIN users u ON t.teacher_id = u.user_id
        WHERE st.student_id = ?
    """, (student_id,))
    
    teachers = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(teachers)

@app.route('/api/teacher/<int:teacher_id>/disciplines', methods=['GET'])
def get_teacher_disciplines(teacher_id):
    """Получение дисциплин преподавателя"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT discipline_id, name, group_name FROM disciplines WHERE teacher_id = ? ORDER BY name",
                  (teacher_id,))
    disciplines = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(disciplines)

@app.route('/api/teacher/<int:teacher_id>/students', methods=['GET'])
def get_teacher_students(teacher_id):
    """Получение студентов преподавателя"""
    group_name = request.args.get('group')
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """
        SELECT DISTINCT s.student_id, u.full_name, s.group_name 
        FROM students s
        JOIN users u ON s.student_id = u.user_id
        JOIN student_teacher st ON s.student_id = st.student_id
        WHERE st.teacher_id = ?
    """
    params = [teacher_id]
    
    if group_name:
        query += " AND s.group_name = ?"
        params.append(group_name)
    
    query += " ORDER BY u.full_name"
    cursor.execute(query, params)
    students = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(students)

@app.route('/api/teacher/<int:teacher_id>/ktp', methods=['GET'])
def get_teacher_ktp(teacher_id):
    """Получение КТП преподавателя"""
    discipline_id = request.args.get('discipline_id')
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """
        SELECT k.ktp_id, k.discipline_id, k.group_name, k.type, k.description, k.practice_number, k.homework
        FROM ktp k
        WHERE k.teacher_id = ?
    """
    params = [teacher_id]
    
    if discipline_id:
        query += " AND k.discipline_id = ?"
        params.append(discipline_id)
    
    query += " ORDER BY k.description"
    cursor.execute(query, params)
    ktps = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(ktps)

@app.route('/api/teacher/grade/set', methods=['POST'])
def set_grade():
    """Выставление оценки"""
    data = request.json
    
    student_id = data.get('student_id')
    teacher_id = data.get('teacher_id')
    discipline_id = data.get('discipline_id')
    ktp_id = data.get('ktp_id')
    grade = data.get('grade')
    date = data.get('date')
    
    if grade == 'н':
        grade = -1
    else:
        grade = int(grade)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT grade_id FROM grades WHERE student_id = ? AND discipline_id = ? AND ktp_id = ?",
                  (student_id, discipline_id, ktp_id))
    existing = cursor.fetchone()
    
    is_update = bool(existing)
    
    if existing:
        cursor.execute("""
            UPDATE grades 
            SET grade = ?, date = ? 
            WHERE student_id = ? AND discipline_id = ? AND ktp_id = ?
        """, (grade, date, student_id, discipline_id, ktp_id))
    else:
        cursor.execute("""
            INSERT INTO grades (student_id, teacher_id, discipline_id, ktp_id, grade, date)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (student_id, teacher_id, discipline_id, ktp_id, grade, date))
    
    if grade != -1:
        cursor.execute("SELECT tokens_per_attendance FROM teachers WHERE teacher_id = ?", (teacher_id,))
        result = cursor.fetchone()
        if result:
            tokens_per_attendance = result[0]
            cursor.execute("""
                UPDATE student_teacher 
                SET tokens = tokens + ? 
                WHERE student_id = ? AND teacher_id = ?
            """, (tokens_per_attendance, student_id, teacher_id))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'is_update': is_update})

@app.route('/api/admin/stats', methods=['GET'])
def get_admin_stats():
    """Статистика для администратора"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM students")
    students_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM teachers")
    teachers_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM disciplines")
    disciplines_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM grades WHERE grade != -1")
    grades_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT role, COUNT(*) as count FROM users GROUP BY role")
    role_distribution = {row['role']: row['count'] for row in cursor.fetchall()}
    
    conn.close()
    
    return jsonify({
        'students_count': students_count,
        'teachers_count': teachers_count,
        'disciplines_count': disciplines_count,
        'grades_count': grades_count,
        'role_distribution': role_distribution
    })

if __name__ == '__main__':
    # Запуск на всех интерфейсах, порт 5001 (чтобы не конфликтовать с веб-приложением)
    app.run(host='0.0.0.0', port=5001, debug=True)

