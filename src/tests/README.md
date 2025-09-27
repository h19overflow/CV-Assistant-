# Resume System Tests

This directory contains comprehensive tests for the Resume System authentication and API endpoints.

## Test Structure

```
src/tests/
├── unit/                    # Unit tests for individual components
│   ├── test_auth_crud.py   # Authentication CRUD operations
│   └── test_resume_crud.py # Resume CRUD operations
├── integration/            # Integration tests for API endpoints
│   └── test_auth_endpoints.py # Authentication API tests
├── fixtures/              # Test data and fixtures
├── conftest.py           # Test configuration and fixtures
├── pytest.ini           # Pytest configuration
├── requirements.txt      # Test dependencies
└── run_tests.py         # Test runner script
```

## Running Tests

### Quick Start

```bash
# Run all tests
python src/tests/run_tests.py all

# Run only unit tests
python src/tests/run_tests.py unit

# Run only integration tests
python src/tests/run_tests.py integration

# Run tests with coverage report
python src/tests/run_tests.py coverage
```

### Manual pytest Commands

```bash
# Run all tests
python -m pytest src/tests/ -v

# Run specific test file
python -m pytest src/tests/unit/test_auth_crud.py -v

# Run specific test class
python -m pytest src/tests/unit/test_auth_crud.py::TestPasswordHashing -v

# Run specific test
python -m pytest src/tests/unit/test_auth_crud.py::TestPasswordHashing::test_hash_password_creates_different_hash_each_time -v

# Run with coverage
python -m pytest src/tests/ --cov=src/backend --cov-report=html
```

## Test Categories

### Unit Tests (`src/tests/unit/`)

- **`test_auth_crud.py`**: Tests authentication CRUD operations
  - Password hashing and verification
  - JWT token creation and validation
  - User creation and authentication
  - Convenience functions

- **`test_resume_crud.py`**: Tests resume CRUD operations
  - Resume creation, retrieval, updating, deletion
  - User-resume relationships
  - Data integrity and constraints

### Integration Tests (`src/tests/integration/`)

- **`test_auth_endpoints.py`**: Tests authentication API endpoints
  - User registration endpoint
  - User login endpoint
  - Protected endpoints requiring authentication
  - Complete authentication workflows

## Test Fixtures

The `conftest.py` file provides these fixtures:

- `test_client`: FastAPI test client
- `test_user_data`: Sample user registration data
- `created_test_user`: Pre-created test user in database
- `test_user_token`: JWT token for authenticated requests
- `auth_headers`: Authorization headers with JWT token
- `test_resume_data`: Sample resume data

## Test Database

Tests use a separate SQLite database (`test_resume_system.db`) that is:
- Created fresh for each test session
- Cleaned between individual tests
- Automatically deleted after tests complete

## Coverage Reports

When running tests with coverage:
- Terminal report shows line-by-line coverage
- HTML report is generated in `htmlcov/` directory
- Open `htmlcov/index.html` to view detailed coverage

## Dependencies

Install test dependencies:

```bash
pip install -r src/tests/requirements.txt
```

Key testing libraries:
- `pytest`: Test framework
- `pytest-cov`: Coverage reporting
- `pytest-asyncio`: Async test support
- `httpx`: HTTP client for API testing
- `faker`: Test data generation

## Best Practices

### Writing Tests

1. **Descriptive Names**: Use clear, descriptive test method names
2. **One Assertion Per Concept**: Focus each test on a single behavior
3. **Arrange-Act-Assert**: Structure tests clearly
4. **Use Fixtures**: Leverage fixtures for common setup
5. **Test Edge Cases**: Include error conditions and boundary cases

### Test Organization

1. **Group Related Tests**: Use test classes to group related functionality
2. **Mark Tests**: Use pytest markers for test categorization
3. **Isolated Tests**: Ensure tests don't depend on each other
4. **Clean Database**: Use fixtures that clean up after themselves

### Example Test

```python
def test_create_user_success(self, test_user_data):
    \"\"\"Test successful user creation.\"\"\"
    # Arrange
    email = test_user_data["email"]
    password = test_user_data["password"]

    # Act
    user = create_user(email, password)

    # Assert
    assert user.email == email.lower().strip()
    assert user.id is not None
    assert user.password_hash != password
```

## Continuous Integration

These tests are designed to run in CI/CD pipelines:
- No external dependencies (uses SQLite)
- Fast execution (most tests under 1 second)
- Clear pass/fail indicators
- Comprehensive coverage reporting

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure you're running from project root
2. **Database Errors**: Check that test database can be created/deleted
3. **JWT Errors**: Ensure `python-jose` is installed correctly
4. **Async Errors**: Make sure `pytest-asyncio` is installed

### Debug Failed Tests

```bash
# Run with detailed output
python -m pytest src/tests/ -v -s

# Run specific failing test
python -m pytest src/tests/unit/test_auth_crud.py::TestPasswordHashing::test_specific_test -v -s

# Debug with pdb
python -m pytest src/tests/ --pdb
```