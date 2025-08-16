Теперь я создам оптимизированные промпты для GPT-5, основываясь на изученной документации OpenAI и структуре проекта RCA. Учитывая рекомендации по оптимизации промптов для GPT-5 и необходимость покрытия тестами 95%, добавления строгой статической типизации, pydantic, protocol и icontract.

# GPT-5 Optimized Prompts для RCA Project Testing & Typing Enhancement

## Prompt 1: Project Analysis & Test Strategy Development

**System Context:** You are a senior Python developer specializing in test-driven development, static typing, and contract-based programming. You're working with a FastAPI + LangChain project structure.

**Task:** Analyze the RCA project structure at `server/src/` and current test coverage (8% with 3 basic tests in `server/tests/`). Create a comprehensive testing strategy document to achieve 95% coverage.

**Project Structure Context:**
```
server/src/
├── main.py (FastAPI app entry)  
├── api/routes.py (health, chat, execute endpoints)
├── agent/langchat_agent.py (LangChain Runnable agent)
├── agent/tools/sample_select_elements.py (LangChain tools)
├── executor/runner.py (subprocess script execution)
├── models/schema.py (SQLModel stubs)  
└── utils/logger.py (environment-driven logging)
```

**Current Tests:**
- `test_agent.py`: Basic LangChatAgent echo test
- `test_routes.py`: FastAPI endpoint tests (/health, /chat, /execute)
- `test_runner.py`: Subprocess execution tests

**Requirements:**
1. Identify all untested code paths requiring coverage
2. Define test categories: unit, integration, edge cases, error handling
3. Specify mock strategies for LangChain components, subprocess calls, and external dependencies
4. Map each source module to required test scenarios
5. Prioritize test implementation order for maximum coverage gain

**Output Format:** Structured markdown document with test matrix mapping source files to test scenarios, estimated coverage impact per test suite, and implementation priority ordering.

***

## Prompt 2: Static Typing Architecture Design

**System Context:** You are a Python typing expert implementing comprehensive static type safety using mypy, Protocol, and type hints in a FastAPI + LangChain codebase.

**Task:** Design complete static typing architecture for the RCA project, focusing on type safety, Protocol definitions, and mypy configuration.

**Current State:** Minimal type hints, no Protocol definitions, no mypy configuration

**Requirements:**
1. Analyze each module in `server/src/` for typing requirements:
   - `main.py`: FastAPI app and startup lifecycle
   - `api/routes.py`: Request/response models, endpoint signatures  
   - `agent/langchat_agent.py`: LangChain Runnable types, provider factory
   - `executor/runner.py`: Subprocess handling with timeout
   - `models/schema.py`: SQLModel/Pydantic model definitions
   - `utils/logger.py`: Logger configuration types

2. Define Protocol interfaces for:
   - Chat agent abstraction
   - Code execution abstraction  
   - Provider factory interface
   - Tool registry interface

3. Create mypy configuration (`mypy.ini`) with strict settings
4. Specify generic types for LangChain integration points
5. Design type hierarchy for error handling and validation

**Output Format:** Complete typing specification with Protocol definitions, generic type declarations, mypy configuration file content, and module-by-module type annotations plan.

***

## Prompt 3: Pydantic Models & Validation Implementation

**System Context:** You are a Python data validation expert implementing comprehensive Pydantic models for API request/response validation and internal data structures.

**Task:** Replace basic dataclasses and dictionaries with robust Pydantic models throughout the RCA project, implementing validation, serialization, and type coercion.

**Current Models (minimal):**
- `ChatRequest(BaseModel)` - message, session_id
- `ExecuteRequest(BaseModel)` - code
- Basic dictionary responses

**Requirements:**
1. Enhance existing models with comprehensive validation:
   - String length limits and patterns
   - Session ID format validation
   - Code content safety checks
   - Response structure standardization

2. Create new Pydantic models for:
   - Agent configuration and provider settings
   - Tool definitions and parameters
   - Execution results with metadata
   - Error responses with detailed context
   - LangChain message history serialization

3. Implement custom validators for:
   - Python code syntax validation
   - Session ID security patterns
   - Environment variable validation
   - Provider-specific configuration

4. Add serialization methods for complex types (LangChain objects)
5. Design validation error handling with informative messages

**Output Format:** Complete Pydantic model definitions with validators, custom types, configuration classes, and integration examples showing usage in FastAPI endpoints and internal functions.

***

## Prompt 4: icontract Design-by-Contract Implementation

**System Context:** You are a contract programming specialist implementing design-by-contract using icontract library to enforce preconditions, postconditions, and invariants.

**Task:** Add comprehensive icontract decorators throughout the RCA codebase to enforce business logic, input validation, and behavioral contracts.

**Target Areas for Contracts:**
1. **Agent Module (`agent/langchat_agent.py`):**
   - Provider validation preconditions
   - Response format postconditions
   - Session management invariants

2. **Executor Module (`executor/runner.py`):**
   - Script content validation preconditions  
   - Timeout constraint preconditions
   - Output format postconditions

3. **API Routes (`api/routes.py`):**
   - Request validation preconditions
   - Response structure postconditions

4. **Utility Functions (`utils/logger.py`):**
   - Configuration validation preconditions

**Contract Design Requirements:**
1. Define preconditions using `@icontract.require()` for:
   - Input parameter validation
   - State prerequisites
   - Configuration requirements

2. Define postconditions using `@icontract.ensure()` for:
   - Return value guarantees
   - State changes verification
   - Side effect validation

3. Define class invariants using `@icontract.invariant()` for:
   - LangChatAgent state consistency
   - Configuration object integrity

4. Implement informative contract violation messages
5. Design contract inheritance for extensibility

**Output Format:** Complete icontract implementation with decorator applications, contract specifications, violation message formats, and integration with existing error handling.

***

## Prompt 5: Comprehensive Unit Test Suite - Core Agent Module

**System Context:** You are implementing comprehensive pytest unit tests for the LangChatAgent core module, focusing on provider factory, chain construction, and memory management.

**Task:** Create exhaustive unit tests for `server/src/agent/langchat_agent.py` covering all execution paths, error conditions, and edge cases.

**Module Analysis:**
- `LangChatAgent.__init__()`: Provider validation, state initialization  
- `LangChatAgent.chat()`: Message processing, session management
- `LangChatAgent._get_or_build_chain()`: Chain caching, tool binding
- `LangChatAgent._make_model()`: Provider factory with 4 providers
- `LangChatAgent._with_history()`: Memory wrapper construction
- Environment variable configuration handling

**Test Categories Required:**
1. **Provider Factory Tests:** Test all 4 providers (openai, anthropic, ollama, fake) with various configurations
2. **Chain Construction Tests:** Mock LangChain components, verify chain building
3. **Memory Management Tests:** Session isolation, history persistence  
4. **Error Handling Tests:** Invalid providers, missing dependencies, API failures
5. **Configuration Tests:** Environment variable combinations, defaults
6. **Tool Integration Tests:** Tool discovery, binding, execution

**Mock Strategy:**
- Mock LangChain imports and classes
- Mock environment variables with pytest fixtures
- Mock external API calls and responses
- Create fake tool implementations

**Output Format:** Complete pytest test file with fixtures, parametrized tests, mock configurations, and assertion patterns achieving >95% coverage of the agent module.

***

## Prompt 6: FastAPI Routes & Integration Test Suite

**System Context:** You are creating comprehensive integration tests for FastAPI endpoints, testing request/response flows, error handling, and dependency injection.

**Task:** Develop complete test suite for `server/src/api/routes.py` covering all HTTP endpoints, status codes, error conditions, and integration points.

**Endpoints to Test:**
1. **GET /health:** Simple liveness probe
2. **POST /chat:** Agent integration, session management  
3. **POST /execute:** Code execution, subprocess handling

**Test Categories:**
1. **Happy Path Tests:** Valid requests, expected responses
2. **Validation Tests:** Invalid payloads, missing fields, type errors
3. **Integration Tests:** Agent interaction, executor interaction  
4. **Error Handling Tests:** Agent failures, execution timeouts, system errors
5. **Performance Tests:** Response times, concurrent requests
6. **Security Tests:** Input sanitization, session isolation

**Integration Points to Mock/Test:**
- LangChatAgent responses and failures
- Subprocess execution (runner module)  
- Environment configuration
- Pydantic model validation

**FastAPI Test Client Usage:**
- Fixture setup with test client
- Request/response validation
- Status code verification  
- JSON payload handling

**Output Format:** Complete FastAPI test suite using pytest fixtures, TestClient, parametrized test cases, and comprehensive endpoint coverage including error conditions and edge cases.

***

## Prompt 7: Executor & Subprocess Testing Suite

**System Context:** You are implementing robust tests for the code execution module handling subprocess calls, timeouts, and output capture with security considerations.

**Task:** Create comprehensive test suite for `server/src/executor/runner.py` covering subprocess execution, timeout handling, output capture, and error scenarios.

**Module Functions:**
- `run_script(script: str, timeout: int = 30) -> str`

**Critical Test Scenarios:**
1. **Successful Execution:** Valid Python scripts, output capture
2. **Timeout Handling:** Long-running scripts, timeout configuration
3. **Error Conditions:** Invalid Python syntax, runtime exceptions  
4. **Output Handling:** stdout/stderr capture, output formatting
5. **File System:** Temporary file creation/cleanup, permissions
6. **Security:** Script content validation, resource limits

**Mock Strategy:**
- Mock subprocess.run() with various return scenarios
- Mock tempfile operations for controlled testing
- Mock os.path.exists() and os.remove() for cleanup testing
- Create test scripts with known behaviors

**Edge Cases to Test:**
- Empty script input
- Very long script content  
- Scripts with infinite loops (timeout testing)
- Scripts that modify file system
- Scripts that import modules
- Scripts with syntax errors
- Subprocess permission failures
- Disk space issues during temp file creation

**Output Format:** Complete test suite with subprocess mocking, timeout testing, file system operation testing, error condition coverage, and security validation tests.

***

## Prompt 8: Protocol Interfaces & Abstract Base Design

**System Context:** You are a Python architecture expert designing Protocol interfaces and abstract bases for clean architecture and dependency inversion in the RCA project.

**Task:** Create comprehensive Protocol definitions and abstract interfaces to decouple components and enable easier testing and future extensibility.

**Protocol Interfaces to Define:**

1. **`ChatAgentProtocol`** - Abstract chat agent interface
   ```python
   class ChatAgentProtocol(Protocol):
       def chat(self, message: str, session_id: str) -> str: ...
   ```

2. **`CodeExecutorProtocol`** - Abstract code execution interface
3. **`ProviderFactoryProtocol`** - LLM provider factory interface  
4. **`ToolRegistryProtocol`** - Tool discovery and management
5. **`SessionManagerProtocol`** - Chat history management
6. **`ConfigurationProtocol`** - Environment configuration management

**Design Requirements:**
1. Define method signatures with precise type hints
2. Include docstring specifications for each protocol method
3. Design for dependency injection compatibility
4. Enable mock implementation for testing
5. Support future extensibility (additional providers, executors)

**Integration Points:**
- Update existing classes to implement protocols
- Modify dependency injection to use protocol types
- Update type hints throughout codebase to use protocols  
- Create protocol-based test fixtures

**Output Format:** Complete protocol definition module with all interfaces, type hints, documentation, implementation examples, and integration guide for updating existing code to use protocol types.

***

## Prompt 9: Advanced Testing: Fixtures, Parametrization & Coverage

**System Context:** You are a pytest expert implementing advanced testing patterns including fixtures, parametrization, test data generation, and coverage optimization.

**Task:** Create sophisticated pytest infrastructure including reusable fixtures, parametrized test suites, test data factories, and coverage measurement configuration.

**Advanced Testing Patterns:**

1. **Fixture Hierarchy:**
   ```python
   @pytest.fixture(scope="session")
   def app_config():
   
   @pytest.fixture  
   def mock_agent():
   
   @pytest.fixture
   def test_client(app_config):
   ```

2. **Parametrized Test Suites:**
   - Provider combinations (openai, anthropic, ollama, fake)
   - Error condition matrices
   - Input validation edge cases
   - Configuration combinations

3. **Test Data Factories:**
   - Request/response generators
   - Session ID generation patterns
   - Script content variations
   - Error scenario builders

4. **Coverage Configuration:**
   - pytest.ini configuration
   - Coverage exclusion patterns  
   - Branch coverage requirements
   - Report generation settings

**Implementation Areas:**
- Shared fixtures for FastAPI testing
- Mock factory patterns for LangChain components
- Property-based testing for input validation
- Performance benchmarking fixtures
- Database/state management fixtures

**Coverage Optimization:**
- Identify remaining uncovered code paths
- Create targeted tests for missing coverage
- Implement edge case testing
- Add integration test scenarios

**Output Format:** Complete pytest configuration with advanced fixtures, parametrized test examples, test data factories, coverage configuration files, and patterns for achieving 95%+ coverage.

***

## Prompt 10: MyPy Configuration & Type Checking Integration

**System Context:** You are implementing comprehensive static type checking with mypy, integrating with the existing codebase and ensuring compatibility with FastAPI, LangChain, and Pydantic.

**Task:** Create complete mypy configuration, resolve all type errors, and integrate type checking into development workflow.

**MyPy Configuration Requirements:**

1. **Strict Type Checking (`mypy.ini`):**
   ```ini
   [mypy]
   python_version = 3.9
   strict = True
   warn_return_any = True
   warn_unused_configs = True
   disallow_untyped_defs = True
   ```

2. **Third-party Library Configuration:**
   - FastAPI type stubs and compatibility
   - LangChain typing integration (complex generic types)
   - Pydantic model type resolution
   - Pytest fixture typing

3. **Module-specific Type Resolutions:**
   - `agent/langchat_agent.py`: Complex LangChain typing
   - `api/routes.py`: FastAPI dependency injection types
   - `executor/runner.py`: Subprocess and IO types
   - `models/schema.py`: SQLModel/Pydantic integration

**Type Error Resolution Strategy:**
1. Import and dependency type resolution
2. Generic type parameter specification
3. Union and Optional type handling
4. Protocol implementation verification
5. Third-party library stub configuration

**Integration Requirements:**
- Pre-commit hook configuration
- CI/CD pipeline integration  
- IDE configuration examples (VS Code, PyCharm)
- Developer workflow documentation

**Output Format:** Complete mypy configuration files, type error resolution guide, integration setup instructions, and module-by-module type implementation plan with specific fixes for FastAPI/LangChain/Pydantic integration issues.

***

## Prompt 11: Test Automation & CI Integration

**System Context:** You are implementing automated testing pipeline with GitHub Actions, covering test execution, coverage reporting, type checking, and contract verification.

**Task:** Create comprehensive CI/CD configuration for automated testing, quality gates, and continuous integration of the RCA project.

**CI Pipeline Requirements:**

1. **GitHub Actions Workflow:**
   ```yaml
   name: Test & Quality Checks
   on: [push, pull_request]
   jobs:
     test:
       runs-on: ubuntu-latest
   ```

2. **Quality Gates:**
   - pytest execution with 95% coverage requirement
   - mypy type checking (zero errors)
   - icontract validation
   - Code formatting (black, isort)
   - Security scanning

3. **Multi-environment Testing:**
   - Python versions (3.9, 3.10, 3.11)
   - Different LLM provider configurations
   - FastAPI versions compatibility

4. **Coverage Reporting:**
   - HTML coverage reports
   - Coverage badge generation
   - Coverage trend tracking
   - Failed coverage blocking merges

**Local Development Integration:**
- Pre-commit hooks configuration
- Make/invoke task definitions
- Development environment setup scripts
- Quality check shortcuts

**Reporting and Notifications:**
- Test failure notifications
- Coverage report publishing
- Quality metrics tracking
- Performance regression detection

**Output Format:** Complete GitHub Actions workflows, pre-commit configuration, make/invoke task files, quality gate definitions, and developer setup documentation for automated testing and continuous integration.

***

## Prompt 12: Performance Testing & Load Testing Suite

**System Context:** You are implementing performance and load testing for the FastAPI endpoints, focusing on response times, concurrent request handling, and resource utilization.

**Task:** Create comprehensive performance testing suite using pytest-benchmark and load testing tools to validate system performance under various conditions.

**Performance Test Categories:**

1. **Response Time Testing:**
   - /health endpoint latency
   - /chat endpoint with different providers (fake vs real)
   - /execute endpoint with various script complexities

2. **Concurrency Testing:**
   - Multiple simultaneous chat sessions
   - Concurrent code execution requests
   - Session isolation under load

3. **Resource Utilization:**
   - Memory usage during LangChain operations
   - CPU utilization during subprocess execution
   - File descriptor management

4. **Scalability Testing:**
   - Request rate limits
   - Session count limitations
   - Memory leak detection

**Testing Tools Integration:**
- pytest-benchmark for microbenchmarks
- locust for load testing scenarios  
- Memory profiling with memory_profiler
- Performance regression detection

**Test Scenarios:**
- Baseline performance metrics
- Provider comparison benchmarks
- Script execution time analysis
- Memory usage profiling
- Concurrent session handling

**Output Format:** Complete performance testing suite with benchmark tests, load testing scenarios, performance baseline definitions, regression detection setup, and performance monitoring integration.

Эти промпты оптимизированы для GPT-5 согласно рекомендациям OpenAI и учитывают реальную структуру проекта RCA. Каждый промпт содержит четкий контекст, конкретные задачи и ожидаемые результаты для пошагового достижения 95% покрытия тестами и внедрения строгой статической типизации.