# GEMINI.md

## Project Overview

This project is a Python-based server that implements the Model Context Protocol (MCP) to manage [n8n](https://n8n.io/) workflows. It allows AI assistants to interact with n8n programmatically, enabling them to create, list, search, update, delete, activate, and deactivate workflows.

The server is built using the following main technologies:

*   **Python 3.8+**: The core programming language.
*   **MCP (Model Context Protocol)**: The server implements the `mcp` library to communicate with AI assistants.
*   **httpx**: An asynchronous HTTP client used to interact with the n8n API.
*   **Pydantic**: Used for data validation and settings management.
*   **structlog**: For structured logging.

The project is structured as follows:

*   `src/n8n_mcp/`: Contains the main source code.
    *   `server.py`: The main MCP server implementation, which defines the available tools and handles tool calls.
    *   `client.py`: The n8n API client, which handles all communication with the n8n instance.
    *   `config.py`: The configuration management module, which uses Pydantic to load and validate settings from a file or environment variables.
    *   `logging_config.py`: The logging configuration module.
*   `tests/`: Contains the tests for the project.
*   `config/`: Contains the configuration files.
*   `requirements.txt`: The list of Python dependencies.

## Building and Running

### Prerequisites

*   Python 3.8+
*   An n8n instance (cloud or self-hosted) with an API key.

### Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/yourusername/n8n-mcp-server.git
    cd n8n-mcp-server
    ```
2.  Create and activate a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate
    ```
3.  Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```

### Configuration

1.  Copy the example configuration file:
    ```bash
    cp config/config.example.json config/config.json
    ```
2.  Edit `config/config.json` with your n8n instance details (base URL and API key).

    Alternatively, you can use environment variables. Create a `.env` file with the following content:
    ```
    N8N_BASE_URL=https://your-instance.app.n8n.cloud
    N8N_API_KEY=your-n8n-api-key
    ```

### Running the Server

*   Using the configuration file:
    ```bash
    python -m src.n8n_mcp.server
    ```
*   Using environment variables:
    ```bash
    python -m src.n8n_mcp.server --env
    ```

### Testing

To run the tests, use the following command:
```bash
pytest
```

## Development Conventions

*   **Coding Style**: The project follows the [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide and uses [Black](https://github.com/psf/black) for code formatting and [isort](https://pycqa.github.io/isort/) for import sorting.
*   **Linting**: [Flake8](https://flake8.pycqa.org/en/latest/) is used for linting.
*   **Type Hinting**: The project uses type hints for better code quality, and [MyPy](http://mypy-lang.org/) is used for static type checking.
*   **Testing**: [Pytest](https://pytest.org/) is used for testing.
*   **Pre-commit Hooks**: The project uses pre-commit hooks to automatically run formatting and linting before each commit.
