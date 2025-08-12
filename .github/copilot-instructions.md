---
applyTo: "**/*.py"
---

# Project Coding Guidelines

## Project Context
This project uses the pyRevit Python library for Revit API development.
The goal is to create a tool that implements changes in the BIM model according to user prompt. Always check information about the project in [README.md](../README.md).

## General Coding Practices
- Emphasize simplicity, readability, and DRY principles.
- Code must be clean, well-structured, and maintainable.
- Follow best practices for code quality and maintainability.

## Code Style and Typing
- Use strict type hints for all function parameters and return values.
- Use type aliases for complex types to improve readability.
- Follow Python standards: PEP 8 and PEP 257.
- Use descriptive variable names that clearly indicate their purpose.
- Use dotenv for secret management and configuration.

## Logging and Error Handling
- Use the `logging` module for comprehensive logging.
- Provide clear error messages and handle exceptions gracefully.
- Use appropriate logging levels.

## Documentation Standards
- All functions must include docstrings with the following format:
  - Brief description of the function.
  - Args section with parameter descriptions and types.
  - Returns section with return value description and type.
  - Raises section for any exceptions that may be thrown.
- Provide module-level docstrings for all modules.

## Testing Guidelines
- Provide unit tests for all new functions and classes using pytest.
- Enforce 100% test coverage for critical modules.