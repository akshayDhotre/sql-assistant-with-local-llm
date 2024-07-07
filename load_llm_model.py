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
                                               gpu_layers=gpu_layers)
    return llm_model

def get_response_from_llm_model(llm_model:object, base_prompt:str, question:str)->str:
    """
    Get response from llm
    """
    prompt= base_prompt + "\n\n Question:" + question + "\n\nQuery:"
    print(f'Query to LLM - \n {prompt}')
    print('---------')
    response = llm_model(prompt=prompt)
    return prompt, response

if __name__=="__main__":
    llm_model_path = "models/nsql-llama-2-7b.Q5_K_M.gguf"
    model_type = 'llama'
    gpu_layers = 50

    prompt_template = """You are a SQL database expert who writes SQL queries from given text.
    
    SQL query used to create database - CREATE TABLE StudentMarks (StudentID INT AUTO_INCREMENT PRIMARY KEY, StudentName VARCHAR(50), Mathematics INT, Science INT, English INT, History INT, Geography INT, TotalMarks INT);
    
    Using valid SQLite, answer the following question for the table information provided above."""

    question = "I need all names of students with their marks."

    llm = get_llm_model(model_path=llm_model_path, model_type=model_type, gpu_layers=gpu_layers)

    _, llm_response = get_response_from_llm_model(llm_model=llm, 
                                               base_prompt=prompt_template, 
                                               question=question)
    print(f'LLM Response - \n {llm_response}')
    print('---------')
