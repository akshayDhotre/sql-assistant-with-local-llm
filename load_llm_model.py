"""
Script to load llm model
"""

from ctransformers import AutoModelForCausalLM

def get_llm_model(model_path:str, model_type:str, gpu_layers:int)->object:
    """
    Load llm model
    """
    llm_model = AutoModelForCausalLM.from_pretrained(model_path,
                                               model_type=model_type,
                                               gpu_layers=gpu_layers,
                                               temperature=0.1)
    return llm_model

def get_response_from_llm_model(llm_model:object, table_schema:str, question:str)->str:
    """
    Get response from llm
    """

    prompt = f'''
    You are a professional SQL developer. Understand the question and return the most suitable query.
    Using valid SQLite syntax, answer the question for the table information provided below.

    ### Database Tables Schema
    `{table_schema}`

    Given the table structure from database, provide SQL query to question: `{question}`.
    
    SQL query:
    '''
    print(f'Prompt to LLM - \n {prompt}')
    response = llm_model(prompt=prompt)
    return prompt, response

if __name__=="__main__":
    MODEL_PATH = 'models/phi-3-sql.Q4_K_M.gguf'
    MODEL_TYPE = 'mistral'
    GPU_LAYERS = 30

    STUDENTS = '''CREATE TABLE Students (
        StudentID INTEGER PRIMARY KEY,
        Name TEXT,
        Age INTEGER,
        Gender TEXT
    );
    '''

    MARKS = '''CREATE TABLE Marks (
        StudentID INTEGER,
        Math INTEGER,
        Science INTEGER,
        English INTEGER,
        History INTEGER,
        Geography INTEGER,
      
        FOREIGN KEY (StudentID) REFERENCES Students(StudentID)
    );
    '''

    ATTENDANCE = '''CREATE TABLE IF NOT EXISTS Attendance (
        StudentID INTEGER,
        TotalClasses INTEGER,
        ClassesAttended INTEGER,
        AttendancePercentage REAL,
        FOREIGN KEY (StudentID) REFERENCES Students(StudentID)
    );
    '''

    TABLES_INFO = STUDENTS + '\n' + MARKS + '\n' + ATTENDANCE

    USER_QUERY = '''From students attendence find top 5 students with highest attendance and give me their marks in math.'''

    llm = get_llm_model(model_path=MODEL_PATH, model_type=MODEL_TYPE, gpu_layers=GPU_LAYERS)

    _, llm_response = get_response_from_llm_model(llm_model=llm,
                                               table_schema=TABLES_INFO,
                                               question=USER_QUERY)
    print(f'LLM Response - \n {llm_response}')
    print('---------')
