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


def clean_sql_from_response(response: str) -> str:
    """
    Clean and extract SQL from LLM response.
    
    Args:
        response: Raw response from LLM
        
    Returns:
        Cleaned SQL query
    """
    sql = response.strip()
    
    # Remove markdown code blocks if present
    if sql.startswith("```"):
        lines = sql.split('\n')
        # Find first non-empty line after opening backticks
        start_idx = 1
        while start_idx < len(lines) and not lines[start_idx].strip():
            start_idx += 1
        # Find last non-empty line before closing backticks
        end_idx = len(lines) - 1
        while end_idx > start_idx and not lines[end_idx].strip():
            end_idx -= 1
        
        if end_idx > start_idx:
            sql = '\n'.join(lines[start_idx:end_idx])
    
    return sql.strip()


def attempt_sql_generation(llm_model, table_schema: str, question: str, max_retries: int = 3) -> tuple:
    """
    Attempt to generate valid SQL with retries.
    
    Args:
        llm_model: LLM client
        table_schema: Database schema
        question: User question
        max_retries: Maximum number of attempts
        
    Returns:
        Tuple of (generated_sql, validation_msg, success_flag)
    """
    for attempt in range(1, max_retries + 1):
        try:
            # Generate SQL from LLM
            llm_prompt, llm_response = get_response_from_llm_model(
                llm_model=llm_model,
                table_schema=table_schema,
                question=question
            )
            
            # Clean SQL
            generated_sql = clean_sql_from_response(llm_response)
            
            # Validate query
            is_valid, validation_msg = validate_query(generated_sql)
            
            if not is_valid:
                if attempt < max_retries:
                    st.warning(f"⚠️ Attempt {attempt}/{max_retries}: Invalid SQL - {validation_msg}. Retrying...")
                    continue
                else:
                    return generated_sql, validation_msg, False
            
            # Check security guardrails
            is_safe, safety_msg = SQLGuardrails.check_query_safety(generated_sql)
            
            if not is_safe:
                if attempt < max_retries:
                    st.warning(f"⚠️ Attempt {attempt}/{max_retries}: Security check failed - {safety_msg}. Retrying...")
                    continue
                else:
                    return generated_sql, safety_msg, False
            
            # Success!
            if attempt > 1:
                st.success(f"✅ Valid SQL generated on attempt {attempt}/{max_retries}!")
            return generated_sql, llm_prompt, True
            
        except Exception as e:
            if attempt < max_retries:
                st.warning(f"⚠️ Attempt {attempt}/{max_retries}: Error - {str(e)}. Retrying...")
                continue
            else:
                return "", str(e), False
    
    return "", "Failed to generate valid SQL after all retries", False


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


def get_db_connection(config):
    """Get a fresh database connection (not cached to avoid threading issues)."""
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
    
    # Initialize LLM (cached)
    llm_model = initialize_llm(config)
    if llm_model is None:
        st.error("Failed to initialize LLM")
        return
    
    # Get fresh database connection (not cached to avoid threading issues)
    db_connection, db_cursor = get_db_connection(config)
    if db_cursor is None:
        st.error("Failed to initialize database")
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
    finally:
        # Close connection after schema retrieval
        if db_connection:
            db_connection.close()
    
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
                # Get max retries from config
                max_retries = config.get("llm", {}).get("max_retries", 3)
                
                # Attempt SQL generation with retries
                generated_sql, result_msg, success = attempt_sql_generation(
                    llm_model=llm_model,
                    table_schema=schema,
                    question=question,
                    max_retries=max_retries
                )
                
                if not success:
                    st.error(f"❌ Failed to generate valid SQL: {result_msg}")
                    st.info("💡 Tip: Try rephrasing your question or check your database schema")
                    return
                
                # Display prompt
                with st.expander("View Prompt Sent to LLM"):
                    st.code(result_msg, language="text")
                
                # Display generated query
                st.subheader("Generated SQL Query")
                st.code(generated_sql, language="sql")
                st.success("✅ Query validation and security checks passed!")
                
                # Execute query with fresh database connection
                with st.spinner("Executing query..."):
                    try:
                        # Create new connection for query execution
                        exec_connection, exec_cursor = get_db_connection(config)
                        if exec_cursor is None:
                            st.error("Failed to connect to database for query execution")
                            return
                        
                        sql_response = execute_query(exec_cursor, generated_sql)
                        
                        # Display results
                        st.subheader("Query Results")
                        
                        rows = sql_response.fetchall()
                        
                        if rows:
                            # Get column names
                            col_names = [desc[0] for desc in sql_response.description] if sql_response.description else []
                            
                            # Display as table
                            col_data = {col: [row[i] for row in rows] for i, col in enumerate(col_names)}
                            st.dataframe(col_data, use_container_width=True)
                            
                            st.success(f"✅ Query executed successfully! ({len(rows)} rows returned)")
                            
                            # Optional: Use LLM to format results
                            enable_formatting = config.get("llm", {}).get("enable_result_formatting", False)
                            if enable_formatting and len(rows) > 0:
                                with st.expander("📝 AI-Generated Insights"):
                                    try:
                                        with st.spinner("Generating insights..."):
                                            # Create a more informative summary prompt
                                            rows_preview = rows[:10]  # Show more rows for context
                                            
                                            summary_prompt = f"""Analyze these database query results and provide key insights:

Original Question: {question}
Column Names: {', '.join(col_names)}
Number of Results: {len(rows)}

Sample Data (first {min(len(rows_preview), 10)} rows):
{chr(10).join([f"  Row {i}: " + " | ".join(f"{col}: {val}" for col, val in zip(col_names, row)) for i, row in enumerate(rows_preview, 1)])}
{'...' + chr(10) + f'Total: {len(rows)} results' if len(rows) > 10 else ''}

Provide:
1. Key findings/patterns in the data (2-3 sentences)
2. Any notable observations (if applicable)
3. A brief summary of the complete result set

Keep the response concise and actionable."""
                                            
                                            _, summary = get_response_from_llm_model(
                                                llm_model=llm_model,
                                                table_schema="",
                                                question=summary_prompt
                                            )
                                            st.markdown(summary)
                                    except Exception as e:
                                        st.warning(f"Could not generate insights: {str(e)}")
                        else:
                            st.info("Query executed but returned no results")
                        
                        # Close connection after query execution
                        if exec_connection:
                            exec_connection.close()
                            
                    except Exception as e:
                        st.error(f"❌ Query Execution Error: {str(e)}")
                        # Ensure connection is closed even on error
                        if exec_connection:
                            exec_connection.close()
                
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
