"""
Script to load data to SQL databass

Author: Akshay Dhotre
July 2024
"""

import sqlite3


def get_database_connection(db_file_name:str)->object:
    """
    Get database connection
    """
    connection = sqlite3.connect(db_file_name)
    return connection, connection.cursor()

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

    db_connection, db_cursor = get_database_connection('student_data.db')

    # Create table
    # TABLE_INFO = """
    # Create table STUDENT(NAME VARCHAR(25),CLASS VARCHAR(25),
    # SECTION VARCHAR(25),MARKS INT);
    # """

    TABLE_INFO = """
    CREATE TABLE StudentMarks 
    (StudentID INT AUTO_INCREMENT PRIMARY KEY,
    StudentName VARCHAR(50),
    Mathematics INT,
    Science INT,
    English INT,
    History INT,
    Geography INT,
    TotalMarks INT);
    """

    create_table(db_cursor, TABLE_INFO)

    # Insert records
    # insert_query_list = [
    #     '''Insert Into STUDENT values('Akshay','Data Science','A',90)''',
    #     '''Insert Into STUDENT values('Rohit','Industrial Automation','B',100)''',
    #     '''Insert Into STUDENT values('Snehal','Software Testing','A',86)''',
    #     '''Insert Into STUDENT values('Adinath','Electricals','A',50)''',
    #     '''Insert Into STUDENT values('Shree','IT','A',35)''',
    # ]

    insert_query_list = [
        '''INSERT INTO StudentMarks (StudentID, StudentName, Mathematics, Science, English, History, Geography, TotalMarks)
            VALUES 
                (1, 'John Doe', 85, 90, 75, 80, 70, 400),
                (2, 'Jane Smith', 78, 85, 88, 90, 75, 416),
                (3, 'Alice Johnson', 92, 87, 80, 85, 88, 432),
                (4, 'Robert Brown', 75, 80, 70, 78, 82, 385),
                (5, 'Emily Davis', 88, 92, 85, 89, 90, 444);'''
        ]

    execute_queries(db_cursor, insert_query_list)

    commit_db_changes(db_connection)

    # Display all records
    SELECT_QUERY = """select * from StudentMarks"""
    query_response = execute_query(db_cursor, SELECT_QUERY)
    print(f"Records Inserted: {[row for row in query_response]}")

    close_db_connection(db_connection)
