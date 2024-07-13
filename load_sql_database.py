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
    STUDENTS = '''CREATE TABLE Students (
        StudentID INTEGER PRIMARY KEY,
        Name TEXT,
        Age INTEGER,
        Gender TEXT
    );'''

    MARKS = '''CREATE TABLE Marks (
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
    
    # Query the Students table
    students_df = pd.read_sql_query("SELECT * FROM Students", connection)
    print("Students Table:")
    print(students_df.head())

    # Query the Marks table
    marks_df = pd.read_sql_query("SELECT * FROM Marks", connection)
    print("\nMarks Table:")
    print(marks_df.head())

    # Query the Attendance table
    attendance_df = pd.read_sql_query("SELECT * FROM Attendance", connection)
    print("\nAttendance Table:")
    print(attendance_df.head())

    # Insert data into Students table
    cursor.execute('''
    INSERT INTO Students (StudentID, Name, Age, Gender)
    VALUES (?, ?, ?, ?)
    ''', (51, 'New_Student', 20, 'Male'))

    # Insert data into Marks table
    cursor.execute('''
    INSERT INTO Marks (StudentID, Math, Science, English, History, Geography)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (51, 85, 90, 75, 80, 70))

    # Insert data into Attendance table
    cursor.execute('''
    INSERT INTO Attendance (StudentID, TotalClasses, ClassesAttended, AttendancePercentage)
    VALUES (?, ?, ?, ?)
    ''', (51, 100, 85, (85.0 / 100.0) * 100))

    # Commit data
    connection.commit()

    # Query to database with custom select query
    SELECT_QUERY = '''SELECT T2.Name, T1.Math
                        FROM Marks AS T1 JOIN Students AS T2 ON T1.StudentID = T2.StudentID 
                        WHERE T2.Name IN 
                        (SELECT T4.Name 
                        FROM Attendance AS T3 JOIN Students AS T4 ON T3.StudentID = T4.StudentID 
                        ORDER BY T3.AttendancePercentage DESC LIMIT 5)'''
    query_response = execute_query(cursor, SELECT_QUERY)

    print('Custom query response:\n '+ str(list(query_response)))

    close_db_connection(connection)
