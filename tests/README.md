# Unit Testing Guide

This directory contains comprehensive unit tests for the SQL Assistant with Local LLM application.

## Test Files Overview

### 1. **test_sql_generation.py** - Core SQL Processing Tests (60+ tests)

Tests for SQL query generation, validation, and execution:

- **TestSQLValidator**: Query validation and keyword checking
  - Valid/invalid query detection
  - Dangerous keyword identification
  - SQL syntax validation (parentheses, quotes matching)
  
- **TestSQLGenerator**: SQL query parsing and cleaning
  - Markdown code block removal
  - SQL query extraction from LLM responses
  - Whitespace normalization

- **TestSQLGuardrails**: Security and safety checks
  - SQL injection detection (UNION-based attacks)
  - Comment injection prevention
  - Multiple statement detection
  - Query sanitization

- **TestSQLExecutor**: Database operations
  - Connection management
  - Query execution (simple and complex)
  - Batch query execution
  - Connection lifecycle

- **TestSchemaIntrospector**: Database schema analysis
  - Table discovery
  - Schema retrieval
  - Column information extraction
  - Full database schema generation

### 2. **test_llm_module.py** - LLM and Prompt Tests (30+ tests)

Tests for LLM interaction and prompt generation:

- **TestPromptGeneration**: Prompt template creation
  - SQL generation prompts
  - Query validation prompts
  - Result analysis prompts
  - Prompt structure validation

- **TestLLMInference**: LLM inference functions
  - Mock LLM calls
  - Prompt-response handling
  - Result summarization

- **TestPromptEdgeCases**: Edge case handling
  - Complex schemas
  - Special characters
  - Empty results
  - NULL values

### 3. **test_integration.py** - End-to-End Integration Tests (15+ tests)

High-level integration and error handling tests:

- **TestApplicationIntegration**: Full workflow testing
  - Complete question-to-result pipelines
  - Schema introspection with real databases
  - Complex query execution
  - JOIN and aggregation queries

- **TestErrorHandling**: Error scenarios
  - Malformed SQL handling
  - SQL injection attempt blocking
  - Empty result handling

- **TestDataValidation**: Data safety and sanitization
  - Query sanitization
  - Keyword filtering
  - Query type verification

- **TestPromptSanitization**: Prompt input validation
  - Special character handling
  - Large schema processing

## Running Tests

### Run All Tests

```bash
python -m unittest discover tests -v
```

### Run Specific Test File

```bash
python -m unittest tests.test_sql_generation -v
python -m unittest tests.test_llm_module -v
python -m unittest tests.test_integration -v
```

### Run Specific Test Class

```bash
python -m unittest tests.test_sql_generation.TestSQLValidator -v
```

### Run Specific Test Method

```bash
python -m unittest tests.test_sql_generation.TestSQLValidator.test_valid_select_query -v
```

## Test Coverage

| Component | Tests | Status |
|-----------|-------|--------|
| SQL Validation | 12 | ✅ |
| SQL Generation | 7 | ✅ |
| SQL Guardrails | 9 | ✅ |
| Database Executor | 5 | ✅ |
| Schema Introspector | 6 | ✅ |
| Prompt Generation | 8 | ✅ |
| LLM Inference | 5 | ✅ |
| Prompt Edge Cases | 5 | ✅ |
| Integration | 5 | ✅ |
| Error Handling | 3 | ✅ |
| Data Validation | 3 | ✅ |
| Prompt Sanitization | 2 | ✅ |
| **Total** | **74** | **✅ All Passing** |

## Key Testing Areas

### Security Testing

- ✅ SQL Injection detection (UNION-based, comment-based)
- ✅ Dangerous keyword filtering
- ✅ Multiple statement prevention
- ✅ Query sanitization

### Functionality Testing

- ✅ Query validation and execution
- ✅ Schema introspection
- ✅ Database operations
- ✅ Complex queries (JOINs, aggregations)

### Prompt & LLM Testing

- ✅ Prompt generation with various inputs
- ✅ LLM response handling
- ✅ Result analysis and summarization
- ✅ Edge case handling

### Integration Testing

- ✅ End-to-end workflows
- ✅ Error handling and recovery
- ✅ Data validation pipelines

## Test Features

### Temporary Database Creation

Tests use `tempfile.NamedTemporaryFile` to create isolated test databases without affecting the main application database.

### Mock Objects

Uses Python's `unittest.mock` for:

- LLM model simulation
- Function call verification
- Response generation

### Comprehensive Assertions

Each test includes multiple assertions to verify:

- Return value correctness
- Side effects
- Error messages
- Data integrity

## Writing New Tests

When adding new features, follow this pattern:

```python
class TestNewFeature(unittest.TestCase):
    """Test new feature description."""
    
    def setUp(self):
        """Set up test fixtures."""
        pass
    
    def tearDown(self):
        """Clean up after tests."""
        pass
    
    def test_specific_behavior(self):
        """Test description."""
        # Arrange: Set up test data
        # Act: Call the function
        # Assert: Verify the results
        pass
```

## Continuous Testing

To run tests automatically during development:

```bash
# Watch for changes and run tests (requires pytest-watch)
ptw tests/

# Or manually run periodically
python -m unittest discover tests -v
```

## Known Limitations

1. **LLM Testing**: Uses mocks since actual Ollama calls would be slow
2. **Large Dataset Testing**: Tests use sample data; performance testing would require separate benchmarks
3. **Database Platform**: Tests use SQLite; other databases would require platform-specific tests

## Contributing

When making changes to the codebase:

1. Run all tests to ensure no regressions
2. Add new tests for new functionality
3. Update this README if adding new test files or categories
4. Aim for >80% code coverage

## Future Enhancements

- [ ] Add performance/benchmark tests
- [ ] Add load testing for concurrent queries
- [ ] Integrate with CI/CD pipeline
- [ ] Generate coverage reports
- [ ] Add tests for different database platforms
