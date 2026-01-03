"""
Script to load data to SQL databass

Author: Akshay Dhotre
July 2024
"""

import sqlite3
import pandas as pd


def get_database_connection(db_file_name:str)->object:
    """
    Get database connection
    """
    db_connection = sqlite3.connect(db_file_name)
    return db_connection, db_connection.cursor()

def create_table(db_cursor:object, db_create_query:str)->None:
    """
    Function to create and insert data to sql database
    """
    db_cursor.execute(db_create_query)
    print("Database Created")
    return None

def execute_query(db_cursor:object, query_string:str)->object:
    """
    Run queries from given list sequentially.
    """
    response = db_cursor.execute(query_string)
    return response

def execute_queries(db_cursor:object, query_list:list)->None:
    """
    Run queries from given list sequentially.
    """
    for query_string in query_list:
        db_cursor.execute(query_string)
    print(f'Executed {len(query_list)} queries.')
    return None

def commit_db_changes(db_connection:object)->None:
    """
    Commit the database changes
    """
    db_connection.commit()
    print("Committed the changes")
    return None

def close_db_connection(db_connection:object)->None:
    """
    Close the database connection
    """
    db_connection.close()
    print("Closed the db connection")
    return None

if __name__=="__main__":

    connection, cursor = get_database_connection('students_data_multi_table.db')

    # Table Schema
    STUDENTS = '''CREATE TABLE IF NOT EXISTS Students (
        StudentID INTEGER PRIMARY KEY,
        Name TEXT,
        Age INTEGER,
        Gender TEXT
    );'''

    MARKS = '''CREATE TABLE IF NOT EXISTS Marks (
        StudentID INTEGER,
        Math INTEGER,
        Science INTEGER,
        English INTEGER,
        History INTEGER,
        Geography INTEGER,
        FOREIGN KEY (StudentID) REFERENCES Students(StudentID)
    );'''

    ATTENDANCE = '''CREATE TABLE IF NOT EXISTS Attendance (
        StudentID INTEGER,
        TotalClasses INTEGER,
        ClassesAttended INTEGER,
        AttendancePercentage REAL,
        FOREIGN KEY (StudentID) REFERENCES Students(StudentID)
    );'''
    
    # Create all tables
    create_table(cursor, STUDENTS)
    create_table(cursor, MARKS)
    create_table(cursor, ATTENDANCE)
    commit_db_changes(connection)
    
    # Insert sample data into Students table
    sample_students = [
        (1, 'Alice Johnson', 18, 'Female'),
        (2, 'Bob Smith', 19, 'Male'),
        (3, 'Charlie Brown', 18, 'Male'),
        (4, 'Diana Prince', 19, 'Female'),
        (5, 'Evan Davis', 18, 'Male'),
        (6, 'Fiona Green', 19, 'Female'),
        (7, 'George Miller', 18, 'Male'),
        (8, 'Hannah White', 19, 'Female'),
        (9, 'Isaac Newton', 20, 'Male'),
        (10, 'Julia Roberts', 18, 'Female'),
    ]
    
    for student in sample_students:
        try:
            cursor.execute('INSERT INTO Students (StudentID, Name, Age, Gender) VALUES (?, ?, ?, ?)', student)
        except sqlite3.IntegrityError:
            pass  # Skip if student already exists
    
    # Insert sample data into Marks table
    sample_marks = [
        (1, 85, 90, 75, 80, 70),
        (2, 92, 88, 85, 92, 88),
        (3, 78, 82, 80, 75, 79),
        (4, 95, 93, 92, 94, 96),
        (5, 88, 85, 87, 86, 84),
        (6, 72, 75, 78, 80, 82),
        (7, 91, 89, 90, 88, 92),
        (8, 76, 79, 81, 77, 80),
        (9, 98, 96, 97, 99, 98),
        (10, 84, 86, 85, 87, 89),
    ]
    
    for marks in sample_marks:
        try:
            cursor.execute('INSERT INTO Marks (StudentID, Math, Science, English, History, Geography) VALUES (?, ?, ?, ?, ?, ?)', marks)
        except sqlite3.IntegrityError:
            pass  # Skip if marks already exist
    
    # Insert sample data into Attendance table
    sample_attendance = [
        (1, 100, 95, 95.0),
        (2, 100, 98, 98.0),
        (3, 100, 85, 85.0),
        (4, 100, 100, 100.0),
        (5, 100, 92, 92.0),
        (6, 100, 78, 78.0),
        (7, 100, 96, 96.0),
        (8, 100, 88, 88.0),
        (9, 100, 99, 99.0),
        (10, 100, 91, 91.0),
    ]
    
    for attendance in sample_attendance:
        try:
            cursor.execute('INSERT INTO Attendance (StudentID, TotalClasses, ClassesAttended, AttendancePercentage) VALUES (?, ?, ?, ?)', attendance)
        except sqlite3.IntegrityError:
            pass  # Skip if attendance already exists
    
    # Commit all data
    commit_db_changes(connection)
    
    # Query the Students table
    students_df = pd.read_sql_query("SELECT * FROM Students", connection)
    print("Students Table:")
    print(students_df)

    # Query the Marks table
    marks_df = pd.read_sql_query("SELECT * FROM Marks", connection)
    print("\nMarks Table:")
    print(marks_df)

    # Query the Attendance table
    attendance_df = pd.read_sql_query("SELECT * FROM Attendance", connection)
    print("\nAttendance Table:")
    print(attendance_df)

    # Example: Query top 5 students by attendance with their math marks
    print("\n" + "="*60)
    print("Top 5 Students by Attendance and Their Math Marks")
    print("="*60)
    
    SELECT_QUERY = '''SELECT T2.Name, T1.Math, T3.AttendancePercentage
                        FROM Marks AS T1 
                        JOIN Students AS T2 ON T1.StudentID = T2.StudentID 
                        JOIN Attendance AS T3 ON T1.StudentID = T3.StudentID
                        ORDER BY T3.AttendancePercentage DESC 
                        LIMIT 5'''
    
    result_df = pd.read_sql_query(SELECT_QUERY, connection)
    print(result_df.to_string(index=False))
    
    print("\n" + "="*60)
    print("Database setup completed successfully!")
    print("="*60)

    close_db_connection(connection)
