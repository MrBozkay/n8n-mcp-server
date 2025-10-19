# n8n MCP Server 🚀

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://modelcontextprotocol.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Professional MCP (Model Context Protocol) server for managing n8n workflows programmatically. Enables AI assistants like Claude, GPT, and others to create, manage, and orchestrate n8n workflows seamlessly.

## 🚀 Quick Start

Get up and running in minutes with Docker:

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/MrBozkay/n8n-mcp-server.git
    cd n8n-mcp-server
    ```

2.  **Build the Docker image:**
    ```bash
    docker build -t n8n-mcp-server .
    ```

3.  **Run the container:**
    Replace the placeholder values for `N8N_BASE_URL` and `N8N_API_KEY` with your actual n8n credentials.
    ```bash
    docker run -d -p 8080:8080 \
      -e N8N_BASE_URL="https://your-instance.app.n8n.cloud" \
      -e N8N_API_KEY="your-n8n-api-key" \
      --name n8n-mcp-container \
      n8n-mcp-server
    ```

4.  **Connect your MCP client:**
    Point your MCP client (e.g., Claude Desktop) to `http://localhost:8080`.

For more detailed instructions, see the [Installation](#-installation) and [Usage](#-usage) sections.

## 🎯 Project Goals

### Main Purpose
Empower AI assistants to programmatically manage n8n workflows through a standardized, secure interface.

### Business Objectives
- ✅ Enable AI-driven workflow automation
- ✅ Streamline workflow creation, search, and management
- ✅ Secure and efficient n8n API integration
- ✅ Developer-friendly tooling and documentation

### Success Criteria
- ✅ 100% functional CRUD operations for workflows
- ✅ API response time < 2 seconds
- ✅ Error rate < 1%
- ✅ Full MCP protocol compliance
- ✅ Comprehensive documentation and examples

## ✨ Features

### Core Operations
- **Create Workflow**: Build new n8n workflows with nodes and connections
- **Get Workflow**: Retrieve workflow details by ID
- **List Workflows**: Browse workflows with filtering (active, tags, pagination)
- **Search Workflows**: Find workflows by name or tags
- **Update Workflow**: Modify existing workflows
- **Delete Workflow**: Remove workflows safely
- **Activate/Deactivate**: Control workflow execution state
- **Health Check**: Monitor API connection status

### Technical Features
- 🔐 **Secure Authentication**: API key-based authentication
- ⚡ **Performance**: Built-in caching with configurable TTL
- 🔄 **Retry Mechanism**: Automatic retry with exponential backoff
- 📊 **Comprehensive Logging**: Structured logging with different levels
- 🛡️ **Error Handling**: Robust error handling and recovery
- 🔌 **MCP Protocol**: Full compliance with MCP standard

## 📋 Prerequisites

- **Python**: 3.8 or higher
- **n8n Instance**: Cloud or self-hosted with API access
- **n8n API Key**: [How to create](https://docs.n8n.io/api/authentication/)
- **MCP Client**: Claude Desktop, or any MCP-compatible AI assistant

## 🛠 Installation

### Method 1: Using Docker (Recommended for Production & AI Assistants)

Docker, projenin tüm bağımlılıklarıyla birlikte izole bir ortamda çalışmasını sağlar ve en stabil yöntemdir.

1.  **Docker imajını oluşturun:**
    Projenin ana dizininde aşağıdaki komutu çalıştırın:
    ```bash
    docker build -t n8n-mcp-server .
    ```

2.  **Konteyneri Çalıştırın:**
    Aşağıdaki komutu kullanarak konteyneri başlatın. Bu komut, sunucuyu arka planda başlatır ve makinenizin 8080 portunu konteynerin 8080 portuna yönlendirir.

    **Önemli:** Komutu çalıştırmadan önce `-e` ile belirtilen `N8N_BASE_URL` ve `N8N_API_KEY` ortam değişkenlerini kendi n8n bilgilerinizle değiştirmeyi unutmayın.

    ```bash
    docker run -d -p 8080:8080 \
      -e N8N_BASE_URL="https://your-instance.app.n8n.cloud" \
      -e N8N_API_KEY="your-n8n-api-key" \
      --name n8n-mcp-container \
      n8n-mcp-server
    ```

3.  **Logları Kontrol Edin:**
    Konteynerin durumunu ve loglarını kontrol etmek için aşağıdaki komutu kullanabilirsiniz:
    ```bash
    docker logs -f n8n-mcp-container
    ```

### Method 2: From Source (For Development)

```bash
# Clone the repository
git clone https://github.com/yourusername/n8n-mcp-server.git
cd n8n-mcp-server

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up configuration
cp config/config.example.json config/config.json
# Edit config/config.json with your n8n instance details
```

### Method 2: Using pip (Coming Soon)

```bash
pip install n8n-mcp-server
```

## ⚙️ Configuration

### Option 1: JSON Configuration File

Create `config/config.json`:

```json
{
  "n8n": {
    "base_url": "https://your-instance.app.n8n.cloud",
    "api_key": "your-n8n-api-key-here",
    "timeout": 30,
    "max_retries": 3
  },
  "mcp": {
    "server_name": "n8n-mcp-server",
    "version": "1.0.0"
  },
  "logging": {
    "level": "INFO",
    "file_path": "logs/n8n_mcp_server.log"
  },
  "performance": {
    "cache_ttl": 300
  }
}
```

### Option 2: Environment Variables

Create `.env` file:

```bash
N8N_BASE_URL=https://your-instance.app.n8n.cloud
N8N_API_KEY=your-n8n-api-key-here
N8N_TIMEOUT=30
N8N_MAX_RETRIES=3
MCP_SERVER_NAME=n8n-mcp-server
MCP_VERSION=1.0.0
LOG_LEVEL=INFO
LOG_FILE_PATH=logs/n8n_mcp_server.log
CACHE_TTL=300
```

Then run with:
```bash
python -m src.n8n_mcp.server --env
```

## 🚀 Usage

### Starting the Server

```bash
# Using config file
python -m src.n8n_mcp.server

# Using environment variables
python -m src.n8n_mcp.server --env

# Using custom config path
python -m src.n8n_mcp.server /path/to/config.json
```

### Using with an MCP Client (e.g., Claude Desktop)

You can connect any MCP-compatible client to this server. Here are a couple of common methods:

#### Method 1: Connecting to the Docker Container (Recommended)

Once the Docker container is running, it exposes the MCP server on port `8080`. You can connect your MCP client to it by defining a remote server.

In your MCP client's configuration (e.g., `claude_desktop_config.json`), add a server entry pointing to `http://localhost:8080`:

```json
{
  "mcpServers": {
    "n8n-docker": {
      "url": "http://localhost:8080"
    }
  }
}
```
*Remember to replace `"n8n-docker"` with the name you want to use for the tool provider.*

#### Method 2: Running from Source (For Development)

Add to your Claude Desktop configuration (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "n8n-local": {
      "command": "python",
      "args": [
        "-m",
        "src.n8n_mcp.server",
        "--env"
      ],
      "cwd": "/absolute/path/to/n8n-mcp-server"
    }
  }
}
```
*Make sure you have a `.env` file in the project root or have the necessary environment variables exported in your shell.*

### Example Operations

#### Create a Workflow

```python
# Ask Claude:
"Create a new n8n workflow called 'Data Sync' that syncs data between two systems"
```

#### Search Workflows

```python
# Ask Claude:
"Find all workflows with 'email' in their name"
```

#### Activate a Workflow

```python
# Ask Claude:
"Activate the workflow with ID 'abc123'"
```

## 📚 Available Tools

### 1. create_workflow
Create a new n8n workflow.

**Parameters:**
- `name` (required): Workflow name
- `nodes` (optional): Array of node configurations
- `connections` (optional): Node connections object
- `active` (optional): Boolean, default false
- `tags` (optional): Array of tag objects

### 2. get_workflow
Retrieve a specific workflow by ID.

**Parameters:**
- `workflow_id` (required): Workflow ID
- `use_cache` (optional): Boolean, default true

### 3. list_workflows
List workflows with optional filters.

**Parameters:**
- `active` (optional): Filter by active status
- `tags` (optional): Array of tag names
- `limit` (optional): Max results (1-100), default 20
- `offset` (optional): Pagination offset, default 0

### 4. search_workflows
Search workflows by name or tags.

**Parameters:**
- `query` (required): Search query string
- `limit` (optional): Max results (1-100), default 20

### 5. update_workflow
Update an existing workflow.

**Parameters:**
- `workflow_id` (required): Workflow ID
- `name` (optional): New workflow name
- `nodes` (optional): Updated nodes configuration
- `connections` (optional): Updated connections
- `active` (optional): Active status
- `tags` (optional): Updated tags

### 6. delete_workflow
Delete a workflow.

**Parameters:**
- `workflow_id` (required): Workflow ID

### 7. activate_workflow
Activate a workflow to make it run automatically.

**Parameters:**
- `workflow_id` (required): Workflow ID

### 8. deactivate_workflow
Deactivate a workflow to stop automatic execution.

**Parameters:**
- `workflow_id` (required): Workflow ID

### 9. health_check
Check n8n API connection health.

**Parameters:** None

## 🏗 Project Structure

```
n8n-mcp-server/
├── src/
│   └── n8n_mcp/
│       ├── __init__.py
│       ├── server.py          # Main MCP server implementation
│       ├── client.py          # n8n API client
│       ├── config.py          # Configuration management
│       └── logging_config.py  # Logging setup
├── config/
│   ├── config.json            # Main configuration
│   └── config.example.json    # Configuration template
├── tests/
│   ├── test_client.py
│   └── test_server.py
├── docs/
│   └── USAGE.md              # Detailed usage guide
├── logs/                      # Log files directory
├── requirements.txt          # Python dependencies
├── setup.py                  # Package setup
├── .gitignore
├── LICENSE
└── README.md                 # This file
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/n8n_mcp --cov-report=html

# Run specific test file
pytest tests/test_client.py
```

## 🔧 Development

### Setup Development Environment

```bash
# Install development dependencies
pip install -r requirements.txt

# Install pre-commit hooks
pre-commit install

# Run code formatting
black src/ tests/

# Run linting
flake8 src/ tests/

# Type checking
mypy src/
```

### Code Style

This project follows:
- **PEP 8** style guide
- **Black** for code formatting
- **isort** for import sorting
- **Type hints** for better code quality

## 🐛 Troubleshooting

### Common Issues

**Issue**: "Configuration error: Invalid n8n configuration"
- **Solution**: Check your n8n base URL and API key in config.json

**Issue**: "API health check failed"
- **Solution**: Verify your n8n instance is accessible and API key is valid

**Issue**: "Import Error: No module named 'mcp'"
- **Solution**: Install dependencies: `pip install -r requirements.txt`

### Debug Mode

Enable debug logging in config.json:
```json
{
  "logging": {
    "level": "DEBUG"
  }
}
```

## 📊 Performance Tips

1. **Caching**: Adjust `cache_ttl` based on your workflow update frequency
2. **Pagination**: Use `limit` and `offset` for large workflow lists
3. **Retry Logic**: Tune `max_retries` for unstable networks
4. **Timeouts**: Increase `timeout` for complex workflows

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

### Quick Start for Contributors

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📝 Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [n8n](https://n8n.io) for the amazing workflow automation platform
- [Model Context Protocol](https://modelcontextprotocol.io) for the MCP standard
- [Anthropic](https://anthropic.com) for Claude and MCP inspiration

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/n8n-mcp-server/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/n8n-mcp-server/discussions)
- **Email**: support@yourproject.com

## 🔗 Links

- [n8n Documentation](https://docs.n8n.io)
- [n8n API Reference](https://docs.n8n.io/api/api-reference/)
- [MCP Documentation](https://modelcontextprotocol.io)
- [Project Homepage](https://github.com//n8n-mcp-server)

---

**Made with ❤️ for the n8n and AI automation community**
