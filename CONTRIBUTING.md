# Contributing to n8n MCP Server

Thank you for your interest in contributing to n8n MCP Server! This document provides guidelines and instructions for contributing.

## 🌟 Ways to Contribute

- **Report Bugs**: Submit detailed bug reports via GitHub Issues
- **Suggest Features**: Propose new features or improvements
- **Submit Code**: Fix bugs, implement features, or improve documentation
- **Improve Documentation**: Help make our docs clearer and more comprehensive
- **Share Feedback**: Tell us about your experience using the project

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- A GitHub account
- n8n instance for testing (cloud or self-hosted)

### Development Setup

1. **Fork the Repository**
   ```bash
   # Click "Fork" on GitHub, then clone your fork
   git clone https://github.com/YOUR_USERNAME/n8n-mcp-server.git
   cd n8n-mcp-server
   ```

2. **Create a Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bug-fix
   ```

5. **Set Up Configuration**
   ```bash
   cp config/config.example.json config/config.json
   # Edit with your n8n instance details
   ```

## 💻 Development Workflow

### Making Changes

1. **Write Clean Code**
   - Follow PEP 8 style guide
   - Use type hints
   - Add docstrings to functions and classes
   - Keep functions focused and single-purpose

2. **Test Your Changes**
   ```bash
   # Run tests
   pytest
   
   # Run with coverage
   pytest --cov=src/n8n_mcp --cov-report=html
   
   # Run specific test
   pytest tests/test_client.py::test_create_workflow
   ```

3. **Format Your Code**
   ```bash
   # Auto-format with black
   black src/ tests/
   
   # Sort imports
   isort src/ tests/
   
   # Check with flake8
   flake8 src/ tests/
   
   # Type checking
   mypy src/
   ```

4. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "feat: add amazing new feature"
   ```

   **Commit Message Format:**
   - `feat:` New feature
   - `fix:` Bug fix
   - `docs:` Documentation changes
   - `style:` Code style changes (formatting, etc.)
   - `refactor:` Code refactoring
   - `test:` Adding or updating tests
   - `chore:` Maintenance tasks

5. **Push to Your Fork**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create a Pull Request**
   - Go to GitHub and create a PR from your fork
   - Provide a clear description of your changes
   - Reference any related issues

## 📝 Code Style Guidelines

### Python Style

```python
# Good: Clear, documented, typed
def create_workflow(
    name: str,
    nodes: List[Dict[str, Any]],
    active: bool = False
) -> WorkflowModel:
    """
    Create a new n8n workflow.
    
    Args:
        name: Workflow name
        nodes: List of node configurations
        active: Whether workflow should be active
        
    Returns:
        Created workflow model
        
    Raises:
        N8nApiError: If API request fails
    """
    # Implementation
    pass
```

### Documentation

- Use clear, concise language
- Provide examples where helpful
- Keep documentation up to date with code changes
- Use proper Markdown formatting

## 🧪 Testing Guidelines

### Writing Tests

```python
import pytest
from src.n8n_mcp.client import N8nApiClient

@pytest.mark.asyncio
async def test_create_workflow():
    """Test workflow creation."""
    client = N8nApiClient(
        base_url="https://test.app.n8n.cloud",
        api_key="test-key"
    )
    
    workflow = WorkflowModel(name="Test Workflow")
    result = await client.create_workflow(workflow)
    
    assert result.name == "Test Workflow"
    assert result.id is not None
```

### Test Coverage

- Aim for at least 80% code coverage
- Test both success and failure scenarios
- Include edge cases
- Test error handling

## 🐛 Reporting Bugs

When reporting bugs, please include:

1. **Clear Title**: Summarize the issue
2. **Description**: Detailed explanation of the bug
3. **Steps to Reproduce**: Numbered steps to recreate the issue
4. **Expected Behavior**: What should happen
5. **Actual Behavior**: What actually happens
6. **Environment**:
   - OS (e.g., macOS 14.0, Ubuntu 22.04)
   - Python version (e.g., Python 3.11.5)
   - n8n version
   - MCP server version
7. **Logs**: Relevant error messages or logs
8. **Screenshots**: If applicable

### Bug Report Template

```markdown
## Bug Description
[Clear description of the bug]

## Steps to Reproduce
1. Step one
2. Step two
3. Step three

## Expected Behavior
[What should happen]

## Actual Behavior
[What actually happens]

## Environment
- OS: macOS 14.0
- Python: 3.11.5
- n8n: 1.29.1
- MCP Server: 1.0.0

## Logs
```
[Paste relevant logs here]
```

## Screenshots
[If applicable]
```

## ✨ Suggesting Features

When suggesting features:

1. **Clear Use Case**: Explain why this feature is needed
2. **Proposed Solution**: Describe how it should work
3. **Alternatives**: Consider alternative approaches
4. **Impact**: Who benefits from this feature?

### Feature Request Template

```markdown
## Feature Description
[Clear description of the feature]

## Use Case
[Why is this needed?]

## Proposed Solution
[How should it work?]

## Alternatives Considered
[Other approaches]

## Additional Context
[Any other relevant information]
```

## 📋 Pull Request Checklist

Before submitting a PR, ensure:

- [ ] Code follows project style guidelines
- [ ] All tests pass
- [ ] New tests added for new features
- [ ] Documentation updated
- [ ] Commit messages follow convention
- [ ] Branch is up to date with main
- [ ] No merge conflicts
- [ ] PR description is clear and complete

## 🔍 Code Review Process

1. **Automated Checks**: CI/CD runs tests and linting
2. **Maintainer Review**: A maintainer reviews your code
3. **Feedback**: Address any comments or suggestions
4. **Approval**: Once approved, your PR will be merged
5. **Recognition**: Contributors are acknowledged in CHANGELOG

## 🎯 Priority Areas

We especially welcome contributions in:

- **Testing**: Expanding test coverage
- **Documentation**: Improving guides and examples
- **Performance**: Optimizing API calls and caching
- **Features**: New workflow management capabilities
- **Error Handling**: Better error messages and recovery
- **Examples**: Real-world usage examples

## 💬 Communication

- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Pull Requests**: For code contributions

## 📜 Code of Conduct

### Our Standards

- Be respectful and inclusive
- Accept constructive criticism gracefully
- Focus on what's best for the community
- Show empathy towards others

### Unacceptable Behavior

- Harassment or discriminatory comments
- Trolling or insulting remarks
- Public or private harassment
- Publishing others' private information

## 🏆 Recognition

Contributors are recognized in:
- CHANGELOG.md for each release
- GitHub Contributors page
- Special mentions for significant contributions

## ❓ Questions?

- Check existing issues and documentation
- Ask in GitHub Discussions
- Reach out to maintainers

## 📚 Resources

- [n8n Documentation](https://docs.n8n.io)
- [n8n API Reference](https://docs.n8n.io/api/api-reference/)
- [MCP Documentation](https://modelcontextprotocol.io)
- [Python Style Guide](https://peps.python.org/pep-0008/)

---

Thank you for contributing to n8n MCP Server! 🎉
