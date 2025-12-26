# Contributing Guidelines

Thank you for your interest in contributing to the Correlation Heatmap System.

## Development Setup

1. Fork the repository
2. Clone your fork locally
3. Set up the development environment following the instructions in the main README
4. Create a new branch for your changes

## Code Style

### Backend (Python)
- Follow PEP 8 style guidelines
- Use type hints for all function signatures
- Run `ruff check app/` before committing
- Run `mypy app/` for type checking
- Write docstrings for all public functions and classes

### Frontend (TypeScript)
- Follow ESLint rules configured in `.eslintrc.cjs`
- Use TypeScript for all new code
- Run `npm run lint` before committing
- Run `npm run type-check` for type checking
- Use functional components with hooks

## Testing

- Write tests for new features
- Ensure all tests pass before submitting a pull request
- Backend: `pytest tests/ -v`
- Frontend: `npm run test:unit`

## Commit Messages

- Use clear, descriptive commit messages
- Reference issue numbers when applicable
- Follow conventional commit format when possible

## Pull Requests

1. Ensure your code follows the style guidelines
2. Update documentation if needed
3. Add tests for new features
4. Ensure all tests pass
5. Submit a pull request with a clear description of changes

