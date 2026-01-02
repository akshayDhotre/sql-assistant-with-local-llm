"""
SQL Assistant - Streamlit Application

A chatbot interface for querying SQL databases using natural language and LLM models.

Author: Akshay Dhotre
Date: July 2024
"""

import streamlit as st
import yaml
from pathlib import Path

# Import modules from the reorganized structure
from llm import get_llm_model, get_response_from_llm_model
from sql import get_database_connection, execute_query
from sql.validator import validate_query
from sql.schema_introspector import get_database_schema
from security.sql_guardrails import SQLGuardrails


# Load configuration
def load_config(config_path: str = "config.yaml") -> dict:
    """Load configuration from YAML file."""
    try:
        with open(config_path, 'r', encoding='utf-8') as config_file:
            return yaml.safe_load(config_file)
    except FileNotFoundError:
        st.error(f"Configuration file not found: {config_path}")
        return {}


@st.cache_resource
def initialize_llm(config):
    """Initialize Ollama LLM client (cached)."""
    try:
        return get_llm_model(
            ollama_base_url=config["llm"]["base_url"],
            model_name=config["llm"]["model_name"]
        )
    except Exception as e:
        st.error(f"Failed to connect to Ollama service: {str(e)}")
        return None


@st.cache_resource
def initialize_database(config):
    """Initialize database connection (cached)."""
    try:
        connection, cursor = get_database_connection(config["database"]["path"])
        return connection, cursor
    except Exception as e:
        st.error(f"Failed to connect to database: {str(e)}")
        return None, None


def main():
    """Main Streamlit application."""
    
    # Page configuration
    st.set_page_config(
        page_title="SQL Assistant",
        page_icon="🔍",
        layout="wide"
    )
    
    st.header("SQL Chatbot Interface")
    st.markdown("Convert natural language questions to SQL queries using AI")
    
    # Load configuration
    config = load_config("config.yaml")
    if not config:
        st.error("Failed to load configuration")
        return
    
    # Initialize LLM and database
    llm_model = initialize_llm(config)
    db_connection, db_cursor = initialize_database(config)
    
    if llm_model is None or db_cursor is None:
        st.error("Failed to initialize application resources")
        return
    
    # Get database schema
    try:
        schema = get_database_schema(db_cursor)
        if not schema:
            st.warning("Could not retrieve database schema")
            schema = "Students, Marks, Attendance tables available"
    except Exception as e:
        st.warning(f"Error retrieving schema: {str(e)}")
        schema = "Students, Marks, Attendance tables available"
    
    # Create two columns for layout
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📝 Query Input")
        question = st.text_area(
            "Ask your question about the database:",
            height=120,
            placeholder="e.g., Find the top 5 students with highest attendance and their math marks"
        )
    
    with col2:
        st.subheader("📊 Database Schema")
        st.text_area(
            "Current Schema:",
            value=schema if schema else "No schema available",
            height=120,
            disabled=True
        )
    
    # Submit button
    col_submit, col_clear = st.columns(2)
    
    with col_submit:
        submit = st.button("🚀 Generate SQL & Execute", use_container_width=True)
    
    with col_clear:
        if st.button("🔄 Clear Results", use_container_width=True):
            st.rerun()
    
    # Process submission
    if submit and question:
        with st.spinner("Generating SQL query..."):
            try:
                # Generate SQL from LLM
                llm_prompt, llm_response = get_response_from_llm_model(
                    llm_model=llm_model,
                    table_schema=schema,
                    question=question
                )
                
                # Display prompt (optional)
                with st.expander("View Prompt Sent to LLM"):
                    st.code(llm_prompt, language="text")
                
                # Display generated query
                st.subheader("Generated SQL Query")
                
                # Clean and extract SQL from response
                generated_sql = llm_response.strip()
                
                # Remove markdown code blocks if present
                if generated_sql.startswith("```"):
                    lines = generated_sql.split('\n')
                    generated_sql = '\n'.join(lines[1:-1]) if len(lines) > 2 else generated_sql
                
                st.code(generated_sql, language="sql")
                
                # Validate query
                is_valid, validation_msg = validate_query(generated_sql)
                
                if not is_valid:
                    st.error(f"❌ Query Validation Failed: {validation_msg}")
                    return
                
                # Check security guardrails
                is_safe, safety_msg = SQLGuardrails.check_query_safety(generated_sql)
                
                if not is_safe:
                    st.error(f"❌ Security Check Failed: {safety_msg}")
                    return
                
                st.success("✅ Query validation passed!")
                
                # Execute query
                with st.spinner("Executing query..."):
                    try:
                        sql_response = execute_query(db_cursor, generated_sql)
                        
                        # Display results
                        st.subheader("Query Results")
                        
                        output_response = []
                        rows = sql_response.fetchall()
                        
                        if rows:
                            # Get column names
                            col_names = [desc[0] for desc in sql_response.description] if sql_response.description else []
                            
                            # Display as table
                            col_data = {col: [row[i] for row in rows] for i, col in enumerate(col_names)}
                            st.dataframe(col_data, use_container_width=True)
                            
                            st.success(f"✅ Query executed successfully! ({len(rows)} rows returned)")
                        else:
                            st.info("Query executed but returned no results")
                            
                    except Exception as e:
                        st.error(f"❌ Query Execution Error: {str(e)}")
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    elif submit and not question:
        st.warning("Please enter a question")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    ### About
    This SQL Assistant uses LLM to convert natural language questions into SQL queries.
    
    **Safety Features:**
    - ✅ Query validation and syntax checking
    - ✅ SQL injection prevention
    - ✅ Read-only query enforcement (SELECT only)
    """)


if __name__ == "__main__":
    main()
