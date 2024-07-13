# SQL Chatbot Interface with Streamlit

This repository contains a Streamlit-based application that allows users to interact with an SQL database using a chatbot interface. The application takes natural language queries as input, creates SQL using LLMs executes them against an SQLite database, and displays the results in a readable format.

## Features

- **User-Friendly Interface**: Simple and intuitive UI with a title bar, input box for SQL queries, and a display box for the LLM responses.
- **SQL Execution**: Executes natural language queries against an SQLite database.
- **Readable Output**: Formats and displays the SQL response in a readable format.

## Installation

### Prerequisites

- Python 3.10
- Streamlit
- ctransformers
- LLM model file (Downloaded and stored in /models folder)

### LLM Model 
- I am using GGUF based model with ctransformers library.
- Hugging Face Model card - [TheBloke/nsql-llama-2-7B-GGUF](https://huggingface.co/TheBloke/nsql-llama-2-7B-GGUF)
- Model Download Link - [Download Link](https://huggingface.co/TheBloke/nsql-llama-2-7B-GGUF/blob/main/nsql-llama-2-7b.Q5_K_M.gguf)

### Setup

1. **Clone the repository**:

    ```bash
    git clone <Repo URL>
    cd sql-chatbot-interface
    ```

2. **Create a virtual environment** (optional but recommended):

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install the required packages**:

    ```bash
    pip install -r requirements.txt
    ```

4. **Setup the SQLite Database and Load Data**:
    - Edit script 'load_sql_database.py' with required table creation and data insertion queries.
    - Then run below command.

    ```bash
     python load_sql_database.py 
    ```
5. **Setup the Configuration JSON File**:
    Edit 'config.json' which contains all details for LLM model path and prompts to run the app.

6. **Run the Streamlit app**:

    ```bash
    streamlit run app.py
    ```

## Usage

1. Open your web browser and go to `http://localhost:8501`.
2. You will see a title bar with the text "SQL Chatbot Interface".
3. Type your SQL query in the "Query Input" box.
4. Click the "Submit" button.
5. The SQL response will be displayed in a formatted manner in the "Response Output" box.


## Update
- 13 July 2024: added multi table sample database and support for related queries.

## License
This project is licensed under the MIT License.