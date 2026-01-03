# Development Scripts

Utility scripts for local development and setup.

## Scripts

### `load_sql_database.py`
Loads sample data into SQLite database for testing and development.

**Usage:**
```bash
python scripts/load_sql_database.py
```

**What it does:**
- Creates sample Students, Marks, and Attendance tables
- Inserts 10 sample students with realistic data
- Displays queries and results
- Sets up database: `students_data_multi_table.db`

**Output Tables:**
- **Students** - Student information (ID, Name, Age, Gender)
- **Marks** - Grades in Math, Science, English, History, Geography
- **Attendance** - Attendance records and percentages

**Example Query:**
Shows top 5 students by attendance with their math marks.

---

**Note:** These are development utilities. For production deployment, use proper migration and seeding tools.
