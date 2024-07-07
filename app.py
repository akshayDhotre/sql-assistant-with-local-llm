"""
Streamlit app file
"""
# Imports
import json
import streamlit as st
import load_sql_database
import load_llm_model

# Load config file
with open('config.json', 'r', encoding='utf-8') as config_file:
    config = json.load(config_file)

# Load configurations
LLM_PATH = config["LLM_PATH"]
MODEL_TYPE = config["MODEL_TYPE"]
GPU_LAYERS = config["GPU_LAYERS"]
DB_PATH = config["DB_PATH"]
BASE_PROMPT = config["BASE_PROMPT"]

# Load LLM model
llm_model = load_llm_model.get_llm_model(model_path=LLM_PATH,
                                         model_type=MODEL_TYPE,
                                         gpu_layers=GPU_LAYERS)

# Connect to database
db_connection, db_cursor = load_sql_database.get_database_connection(DB_PATH)

# Streamlit config
st.set_page_config(page_title="I can Retrieve Any SQL query")
st.header("SQL Chatbot Interface")

# Get question from user prompt window
# question=st.text_input("Input: ",key="input")
question = st.text_area("Query Input", height=100, key="input")

# Submit button information
submit=st.button("Submit")

# if submit is clicked get response from llm and displayon the screen
if submit:
    llm_prompt, llm_response=load_llm_model.get_response_from_llm_model(llm_model=llm_model,
                                                        base_prompt=BASE_PROMPT,
                                                        question=question)

    print(f'LLM Response - \n {llm_response}')

    sql_response = load_sql_database.execute_query(db_cursor,llm_response)

    st.subheader("The Response is")

    output_response = []
    for row in sql_response:
        output_response.append(" - ".join(str(element) for element in row))

    st.text_area("Response Output", value="\n".join(output_response), height=400)
