# Contributing to Project MorningStar

Thank you for considering contributing to Project MorningStar! This guide will help you understand our development process and how to contribute effectively.

## 🎯 Project Overview

Project MorningStar consists of two main components:
- **SWGDB**: Public web database and tools for SWG players
- **MS11**: Advanced automation bot for long-session gameplay

## 📋 Batch System Development

### What is the Batch System?

Project MorningStar uses a **batch-based development system** for organized feature implementation. Each batch represents a complete feature or enhancement with:

- **Implementation**: Core functionality and logic
- **Demo Scripts**: Showcase and testing scripts  
- **Test Suites**: Comprehensive unit and integration tests
- **Documentation**: Detailed implementation summaries

### Batch Structure

```
BATCH_XXX_IMPLEMENTATION_SUMMARY.md  # Implementation documentation
demo_batch_XXX_feature.py            # Demo script
test_batch_XXX_feature.py            # Test suite
```

### Batch Development Process

1. **Create Batch Files**:
   ```bash
   # Implementation
   touch core/feature/your_feature.py
   
   # Demo script
   touch demo_batch_XXX_your_feature.py
   
   # Test suite
   touch test_batch_XXX_your_feature.py
   
   # Documentation
   touch BATCH_XXX_IMPLEMENTATION_SUMMARY.md
   ```

2. **Implement Feature**: Core functionality with proper error handling
3. **Create Demo**: Showcase script demonstrating the feature
4. **Write Tests**: Comprehensive test coverage
5. **Document**: Detailed implementation summary
6. **Submit**: Pull request with all components

### Batch Naming Convention

- **Implementation**: `core/feature/feature_name.py`
- **Demo**: `demo_batch_XXX_feature_name.py`
- **Test**: `test_batch_XXX_feature_name.py`
- **Documentation**: `BATCH_XXX_IMPLEMENTATION_SUMMARY.md`

Where `XXX` is the next available batch number.

## 🛠️ Development Environment Setup

### Prerequisites

```bash
# System Requirements
- Python 3.8+
- Tesseract OCR (for screen reading)
- Git (for version control)
- Windows 10/11 (primary development platform)
```

### Installation

```bash
# Clone the repository
git clone https://github.com/project-morningstar/Project-MorningStar.git
cd Project-MorningStar

# Install Python dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt

# Install Tesseract OCR
# Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki
# Linux: sudo apt-get install tesseract-ocr
# macOS: brew install tesseract

# Run setup script
python setup.py
```

### Environment Configuration

Create a `.env` file with your settings:

```env
# MS11 Configuration
BOT_INSTANCE_NAME=MS11_Dev
LOG_LEVEL=DEBUG
DISCORD_TOKEN=your_discord_token

# SWGDB Configuration
SWGDB_DATABASE_URL=sqlite:///swgdb.db
GOOGLE_ANALYTICS_ID=G-Q4ZZ5SFJC0

# Development Settings
DEBUG=True
TESTING=True
```

## 📝 Development Standards

### Code Style

- **Python**: Follow PEP 8 guidelines
- **Documentation**: Use docstrings for all functions and classes
- **Type Hints**: Include type hints for function parameters and return values
- **Comments**: Add comments for complex logic

### Naming Conventions

- **Files**: Use snake_case for Python files
- **Functions**: Use snake_case for function names
- **Classes**: Use PascalCase for class names
- **Constants**: Use UPPER_SNAKE_CASE for constants
- **Variables**: Use snake_case for variable names

### Error Handling

- **Graceful Degradation**: Handle errors gracefully with fallbacks
- **Logging**: Use appropriate log levels (DEBUG, INFO, WARNING, ERROR)
- **User Feedback**: Provide clear error messages to users
- **Recovery**: Implement automatic recovery where possible

### Testing Requirements

- **Unit Tests**: Test individual functions and methods
- **Integration Tests**: Test feature integration
- **Demo Scripts**: End-to-end functionality demonstration
- **Coverage**: Aim for 80%+ test coverage

## 🧪 Testing Guidelines

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest test_batch_XXX_feature.py

# Run with coverage
pytest --cov=core --cov-report=html

# Run demo scripts
python demo_batch_XXX_feature.py

# Run validation
make validate
```

### Test Structure

```python
# Example test structure
def test_feature_functionality():
    """Test the main functionality of the feature."""
    # Arrange
    input_data = "test_input"
    
    # Act
    result = feature_function(input_data)
    
    # Assert
    assert result == "expected_output"

def test_feature_error_handling():
    """Test error handling for the feature."""
    # Arrange
    invalid_input = None
    
    # Act & Assert
    with pytest.raises(ValueError):
        feature_function(invalid_input)
```

### Demo Scripts

Demo scripts should:
- Demonstrate the feature in action
- Include realistic usage examples
- Show error handling and recovery
- Provide clear output and feedback

## 📚 Documentation Standards

### Implementation Summaries

Each batch should include a comprehensive implementation summary:

```markdown
# Batch XXX - Feature Name

## Overview
Brief description of the feature and its purpose.

## Implementation Details
- Core functionality implemented
- Key algorithms and logic
- Error handling and recovery
- Performance considerations

## Usage Examples
```python
# Example usage code
feature = FeatureClass()
result = feature.process_data(input_data)
```

## Testing
- Unit tests covering all functionality
- Integration tests for feature interaction
- Demo script for end-to-end testing

## Configuration
Required configuration options and their defaults.

## Dependencies
Any new dependencies added or modified.
```

### Code Documentation

- **Function Docstrings**: Include purpose, parameters, return values, and examples
- **Class Docstrings**: Describe the class purpose and usage
- **Module Docstrings**: Overview of the module's functionality
- **Inline Comments**: Explain complex logic and algorithms

## 🔄 Contribution Workflow

### 1. Fork and Clone

```bash
git clone https://github.com/your-username/Project-MorningStar.git
cd Project-MorningStar
```

### 2. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 3. Follow Development Standards

- **Code Style**: Follow PEP 8 and project linting rules
- **Testing**: Write tests for new features
- **Documentation**: Update relevant documentation
- **Batch System**: Use the batch system for new features

### 4. Implement Your Feature

1. **Create Batch Files**: Follow the batch structure
2. **Implement Core Logic**: Focus on functionality and error handling
3. **Write Tests**: Comprehensive test coverage
4. **Create Demo**: Showcase script demonstrating the feature
5. **Document**: Detailed implementation summary

### 5. Testing and Validation

```bash
# Run tests
pytest

# Run linting
flake8 .

# Run type checking
mypy .

# Run validation
make validate

# Run demo script
python demo_batch_XXX_your_feature.py
```

### 6. Submit a Pull Request

- Include a clear description of changes
- Reference any related issues
- Ensure all tests pass
- Update documentation as needed
- Include batch documentation

## 🎯 Contribution Areas

### SWGDB (Public Web Application)

**Frontend Development**:
- HTML/CSS/JavaScript improvements
- UI/UX enhancements
- Mobile responsiveness
- Performance optimization

**Backend Development**:
- Python API development
- Database optimization
- Data import/export features
- Analytics integration

**Content Creation**:
- Heroic database entries
- Quest information and guides
- Build showcases and strategies
- Community tools and utilities

### MS11 (Automation Bot)

**Core Automation**:
- New automation modes
- Improved navigation systems
- Enhanced OCR capabilities
- Performance optimizations

**Safety and Detection**:
- Anti-detection improvements
- Safety feature enhancements
- Crash recovery systems
- Monitoring and alerting

**Integration Features**:
- Discord bot enhancements
- External API integrations
- Data collection and analysis
- Reporting and analytics

## 🚀 Getting Started

### For New Contributors

1. **Read the Documentation**: Start with the main README and this guide
2. **Explore the Codebase**: Understand the project structure
3. **Pick a Simple Issue**: Start with a beginner-friendly task
4. **Follow the Batch System**: Use the batch system for all contributions
5. **Ask for Help**: Don't hesitate to ask questions

### Finding Issues to Work On

- **Good First Issues**: Look for issues labeled "good first issue"
- **Bug Fixes**: Help fix reported bugs
- **Documentation**: Improve documentation and guides
- **Feature Requests**: Implement requested features
- **Performance**: Optimize existing code

### Communication

- **GitHub Issues**: Report bugs and request features
- **GitHub Discussions**: Ask questions and share ideas
- **Discord**: Join our community server for real-time chat
- **Pull Requests**: Include detailed descriptions and examples

## 📋 Checklist for Contributions

Before submitting a pull request, ensure:

- [ ] Code follows PEP 8 style guidelines
- [ ] All functions and classes have docstrings
- [ ] Type hints are included where appropriate
- [ ] Unit tests are written and passing
- [ ] Integration tests are included
- [ ] Demo script demonstrates the feature
- [ ] Implementation summary is documented
- [ ] No new linting errors are introduced
- [ ] All existing tests still pass
- [ ] Documentation is updated
- [ ] Batch system is followed

## 🤝 Community Guidelines

### Code of Conduct

- **Be Respectful**: Treat all contributors with respect
- **Be Helpful**: Help others learn and grow
- **Be Patient**: Understand that everyone learns at their own pace
- **Be Constructive**: Provide constructive feedback and suggestions

### Communication Guidelines

- **Clear and Concise**: Write clear, concise messages
- **Specific Examples**: Include specific examples when possible
- **Respectful Tone**: Maintain a respectful and professional tone
- **Follow Up**: Follow up on discussions and issues

## 📞 Getting Help

### Resources

- **[README.md](../README.md)**: Project overview and quick start
- **[Documentation](docs/)**: Detailed guides and references
- **[Issues](https://github.com/project-morningstar/issues)**: Bug reports and feature requests
- **[Discussions](https://github.com/project-morningstar/discussions)**: Community discussions

### Contact

- **GitHub Issues**: For bug reports and feature requests
- **GitHub Discussions**: For questions and community chat
- **Discord**: For real-time community interaction
- **Email**: For private or sensitive matters

## 🎉 Recognition

Contributors are recognized in several ways:

- **Contributors List**: Added to the project contributors list
- **Release Notes**: Mentioned in release notes for significant contributions
- **Documentation**: Credited in relevant documentation
- **Community**: Acknowledged in community discussions

---

Thank you for contributing to Project MorningStar! Your contributions help make the SWG community better for everyone.

**May the Force be with you!** 🌟 