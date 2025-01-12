# Contributing to PyramidPy Tools

First off, thank you for considering contributing to PyramidPy Tools! It's people like you that make PyramidPy Tools such a great toolkit.

## Code of Conduct

By participating in this project, you are expected to uphold our Code of Conduct. Please report unacceptable behavior to [project maintainers].

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the issue list as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible:

* Use a clear and descriptive title
* Describe the exact steps which reproduce the problem
* Provide specific examples to demonstrate the steps
* Describe the behavior you observed after following the steps
* Explain which behavior you expected to see instead and why
* Include any error messages or stack traces

### Suggesting Enhancements

If you have a suggestion for a new feature or enhancement:

* Use a clear and descriptive title
* Provide a step-by-step description of the suggested enhancement
* Provide specific examples to demonstrate the steps
* Describe the current behavior and explain which behavior you expected to see instead
* Explain why this enhancement would be useful

### Pull Requests

1. Fork the repo and create your branch from `main`
2. If you've added code that should be tested, add tests
3. If you've changed APIs, update the documentation
4. Ensure the test suite passes
5. Make sure your code follows the existing style (we use `black` for formatting)

### Development Process

1. Set up your development environment:
   ```bash
   # Clone your fork
   git clone https://github.com/<your-username>/pyramidpy-tools.git
   cd pyramidpy-tools
   
   # Install dependencies
   uv sync --all-extras
   ```

2. Create a new branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. Make your changes and commit:
   ```bash
   git add .
   git commit -m "feat: add your feature"
   ```

4. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

5. Open a Pull Request

### Commit Messages

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification. Each commit message should be structured as follows:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

Types:
- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation only changes
- `style`: Changes that do not affect the meaning of the code
- `refactor`: A code change that neither fixes a bug nor adds a feature
- `perf`: A code change that improves performance
- `test`: Adding missing tests or correcting existing tests
- `chore`: Changes to the build process or auxiliary tools

### Testing

- Write test cases for any new functionality
- Run the test suite before submitting:
  ```bash
  pytest tests/
  ```
- Ensure test coverage is maintained or improved

### Documentation

- Update the README.md if you change functionality
- Add docstrings to new functions/classes following Google style
- Update type hints for all function parameters and return values

## Style Guide

- We use `black` for code formatting
- Follow PEP 8 guidelines
- Use type hints for all function parameters and return values
- Write descriptive variable names
- Add comments for complex logic
- Keep functions focused and concise

## Questions?

Feel free to open an issue with your question or reach out to the maintainers directly.

Thank you for contributing! 🎉 