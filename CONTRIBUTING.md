# Contributing to SkillStream

Thank you for your interest in contributing to SkillStream! This document provides guidelines and information for contributors.

## 🚀 Getting Started

### Prerequisites

- Python 3.9 or higher
- Git
- Basic knowledge of Django and web development

### Development Setup

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/yourusername/skillstream.git
   cd skillstream
   ```
3. Run the setup script:
   ```bash
   ./scripts/setup.sh
   ```
4. Create a new branch for your feature:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## 📝 Development Guidelines

### Code Style

We use several tools to maintain code quality:

- **Black** for code formatting
- **isort** for import sorting
- **flake8** for linting
- **pre-commit** hooks for automated checks

Run code quality checks:
```bash
./scripts/test.sh
```

### Commit Messages

Use clear, descriptive commit messages following this format:
```
type(scope): brief description

Detailed explanation if needed

- List any breaking changes
- Reference issues: Fixes #123
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

### Testing

- Write tests for all new features and bug fixes
- Maintain test coverage above 80%
- Run the full test suite before submitting:
  ```bash
  python manage.py test
  ```

## 🔄 Pull Request Process

1. **Update Documentation**: Ensure README and docstrings are updated
2. **Add Tests**: Include comprehensive tests for new functionality
3. **Check Code Quality**: Run `./scripts/test.sh` and fix any issues
4. **Update Changelog**: Add your changes to the changelog
5. **Submit PR**: Create a pull request with a clear description

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] New tests added
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or clearly documented)
```

## 🐛 Bug Reports

When reporting bugs, please include:

- **Environment**: OS, Python version, Django version
- **Steps to Reproduce**: Clear, numbered steps
- **Expected Behavior**: What should happen
- **Actual Behavior**: What actually happens
- **Screenshots**: If applicable
- **Additional Context**: Any other relevant information

## 💡 Feature Requests

For feature requests, please provide:

- **Problem Statement**: What problem does this solve?
- **Proposed Solution**: How should it work?
- **Alternatives**: Other solutions considered
- **Additional Context**: Use cases, examples, etc.

## 📚 Documentation

Help improve our documentation:

- Fix typos and grammatical errors
- Add examples and use cases
- Improve API documentation
- Create tutorials and guides

## 🏗️ Architecture Guidelines

### Project Structure

```
skillstream/
├── core/                   # Main application
│   ├── models/            # Database models
│   ├── views/             # View logic
│   ├── services/          # Business logic
│   ├── tests/             # Test files
│   └── utils/             # Utility functions
├── config/                # Django configuration
├── requirements/          # Dependencies
├── scripts/               # Development scripts
└── docs/                  # Documentation
```

### Design Principles

- **Separation of Concerns**: Keep business logic in services
- **DRY (Don't Repeat Yourself)**: Reuse code where possible
- **SOLID Principles**: Follow object-oriented design principles
- **Security First**: Always consider security implications
- **Performance**: Write efficient, scalable code

## 🔒 Security

- **Never commit secrets**: Use environment variables
- **Validate input**: Always validate and sanitize user input
- **Follow Django security best practices**
- **Report security issues privately** to the maintainers

## 📞 Getting Help

- **GitHub Issues**: For bugs and feature requests
- **Discussions**: For questions and general discussion
- **Documentation**: Check the README and inline documentation

## 🎉 Recognition

Contributors will be recognized in:

- README.md contributors section
- Release notes for significant contributions
- GitHub contributors page

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to SkillStream! 🎬