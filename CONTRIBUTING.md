# Contributing to CoHost.AI

Thank you for your interest in contributing to CoHost.AI! This document provides guidelines and information for contributors.

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- Virtual environment (recommended)

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/yourusername/cohost.ai.git
   cd cohost.ai
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

## 📝 Code Style

### Python Code Standards

- **PEP 8**: Follow Python PEP 8 style guidelines
- **Type Hints**: Use type hints for all function parameters and return values
- **Docstrings**: Use Google-style docstrings for all classes and functions
- **Line Length**: Maximum 88 characters (Black formatter standard)

### Example Function Documentation

```python
def example_function(param1: str, param2: int = 10) -> bool:
    """
    Brief description of the function.
    
    Longer description if needed, explaining the purpose and behavior
    of the function in more detail.
    
    Args:
        param1: Description of the first parameter
        param2: Description of the second parameter (default: 10)
        
    Returns:
        Description of the return value
        
    Raises:
        ValueError: Description of when this exception is raised
        TypeError: Description of when this exception is raised
    """
    # Implementation here
    return True
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/test_specific.py

# Run with coverage
python -m pytest --cov=src
```

### Writing Tests

- Write unit tests for all new functionality
- Use descriptive test names
- Follow the Arrange-Act-Assert pattern
- Mock external dependencies

## 📋 Pull Request Process

### Before Submitting

1. **Code Quality**
   - [ ] Code follows PEP 8 standards
   - [ ] All functions have proper docstrings
   - [ ] Type hints are used consistently
   - [ ] No unused imports or variables

2. **Testing**
   - [ ] All existing tests pass
   - [ ] New tests written for new functionality
   - [ ] Test coverage maintained or improved

3. **Documentation**
   - [ ] README updated if needed
   - [ ] Docstrings added/updated
   - [ ] Comments added for complex logic

### Submitting a Pull Request

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**
   - Write clean, well-documented code
   - Add tests for new functionality
   - Update documentation as needed

3. **Commit Changes**
   ```bash
   git add .
   git commit -m "feat: add new feature description"
   ```

4. **Push and Create PR**
   ```bash
   git push origin feature/your-feature-name
   ```
   Then create a pull request on GitHub.

### Commit Message Format

Use conventional commit format:

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting, etc.)
- `refactor:` Code refactoring
- `test:` Adding or updating tests
- `chore:` Maintenance tasks

## 🐛 Bug Reports

### Before Reporting

1. Check existing issues
2. Ensure you're using the latest version
3. Test with minimal configuration

### Bug Report Template

```markdown
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. See error

**Expected behavior**
What you expected to happen.

**Environment:**
- OS: [e.g. Windows 10]
- Python version: [e.g. 3.9.0]
- CoHost.AI version: [e.g. 1.0.0]

**Additional context**
Any other context about the problem.
```

## 💡 Feature Requests

We welcome feature requests! Please:

1. Check if the feature already exists
2. Describe the use case clearly
3. Explain why it would be valuable
4. Consider implementation complexity

## 📞 Getting Help

- **Issues**: GitHub Issues for bugs and feature requests
- **Discussions**: GitHub Discussions for questions and ideas
- **Documentation**: Check the README and code documentation

## 🏆 Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes for significant contributions
- GitHub contributor graphs

Thank you for contributing to CoHost.AI! 🎉
