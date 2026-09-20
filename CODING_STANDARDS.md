# CODING_STANDARDS.md

This document outlines the development standards for this Python repository. Adherence to these guidelines ensures consistent, maintainable, and readable code across the project.

## Architectural Principles

**DRY (Don't Repeat Yourself)**
*   Avoid duplication of logic within files or modules.
*   Use helper functions or utilities when code is repeated more than once.
*   Prefer configuration over hard-coded magic values.

**SOLID**
Developing using SOLID principles ensures the code remains scalable and testable:
1.  **Single Responsibility:** Each class or function should have one reason to change.
2.  **Open/Closed:** Software entities should be open for extension but closed for modification (use inheritance/composition).
3.  **Liskov Substitution:** Subclasses must be substitutable for their base classes without breaking functionality.
4.  **Interface Segregation:** Prefer small, specific interfaces over large general-purpose ones.
5.  **Dependency Inversion:** Depend on abstractions, not concrete implementations.

## Naming Conventions

*   **Methods / Variables / Functions:** Use `snake_case`. Avoid abbreviations unless they are widely understood (e.g., `json`, `http`).
*   **Classes:** Use `PascalCase` for class definitions and method definitions within them.
*   **Constants:** Use `UPPER_SNAKE_CASE` to denote module-level constants.
*   **Single Letter Variables:** Forbidden, except for explicit loop index counters (e.g., `i`, `j`) in nested ranges.

### Examples

**Correct**

```python
# Configuration variables are descriptive and UPPER_CASE
MAX_RETRIES: int = 5
API_ENDPOINT_URL: str = "https://example.com/api"

def fetch_data(url): 
    """Fetches the requested data from a specific URL."""
    if url is None:
        raise ValueError("URL cannot be None")

class DataProcessor:
    def process(self, input_data):
        # Processing logic...
        return self._transform(input_data)
    
    def _transform(self, data):
        return data.upper()
```

**Incorrect**

```python
# Single letter variables (except for counters like 'i' in loops)
def get_x(val):  # x should be descriptive
    pass

# Methods should be PascalCase per this repository standard
class User:
    def getUserEmail(self): 
        # Should be `getEmail` or `GetUserEmail` depending on rule scope. 
        # Per prompt: Classes and Methods are PascalCase.
        pass
        
def GetEmails():  # Top level functions must be snake_case per rule
    pass
```

## Formatting & Style

**Trailing Whitespace**
*   No trailing whitespace is permitted in files.
*   CI checks will fail on any file containing tabs or spaces at the end of lines.
*   Use linters (e.g., `flake8`, `black`) to enforce this automatically before committing.

**Inline Comments**
*   Inline comments should be written on the line **above** the code they describe, rather than after the statement.
*   This reduces noise and clearly separates logic from explanation.

```python
# Example of correct comment placement.
# The following check ensures data integrity.
if not is_valid(user_input):
    logger.error("Input validation failed")
```

## Documentation

*   **Docstrings:** All public classes and functions must include a concise docstring explaining purpose, arguments, and return types.
*   **Imports:** Imports should be ordered (standard library, third-party, local) to maintain consistency.

**Example Docstring Structure**

```python
def calculate_fee(total_amount, rate):
    """Calculate the transaction fee based on total amount.

    Args:
        total_amount (float): The gross amount of the transaction.
        rate (float): The fee percentage as a decimal (e.g., 0.1 for 10%).

    Returns:
        float: The calculated fee rounded to two decimals.
    """
    return round(total_amount * rate, 2)
```

## Tooling & Linting

To maintain quality, please ensure the following tools are configured correctly in your local environment:

*   **`black`**: Used for consistent formatting and indentation.
*   **`isort`**: Manages import ordering.
*   **`flake8` / `pylint`**: Enforces naming conventions and checks for trailing whitespace.