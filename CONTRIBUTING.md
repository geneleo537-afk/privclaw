# Contributing Guide

Thank you for your interest in contributing to PrivClaw! We welcome all forms of contributions, including code, documentation, testing, bug reports, and feature suggestions.

## Quick Start

### 1. Fork the Repository

Click the "Fork" button on GitHub to copy the repository to your account.

### 2. Clone Locally

```bash
git clone https://github.com/YOUR_USERNAME/privclaw.git
cd privclaw
```

### 3. Add Upstream Remote

```bash
git remote add upstream https://github.com/privclaw/privclaw.git
```

### 4. Set Up Development Environment

```bash
# Copy environment configuration
cp .env.example .env

# Start all services
make dev

# Run database migrations
make migrate

# Initialize demo data (optional)
make seed
```

### 5. Run Tests

```bash
make test
```

## Development Workflow

### Branch Strategy

- `main`: Stable branch, all releases come from here
- `develop`: Development branch, daily work happens here
- `feature/*`: Feature branches, branched from `develop`, merged back when complete
- `bugfix/*`: Bug fix branches, branched from `develop`
- `hotfix/*`: Hotfix branches, branched from `main`, merged to both `main` and `develop`

### Commit Message Convention

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

**Types:**

| Type | Description |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation changes |
| `style` | Code formatting (no functional change) |
| `refactor` | Code refactoring |
| `test` | Test-related changes |
| `chore` | Build/tooling changes |

**Examples:**

```
feat(auth): add refresh token rotation
fix(wallet): correct balance calculation for refunds
docs(readme): update deployment instructions
test(auth): add login failure test cases
```

### Code Style

**Backend (Python):**

- Follow [PEP 8](https://peps.python.org/pep-0008/) style guide
- Use type hints
- Use Google-style docstrings for functions/classes
- Line length limit: 120 characters

**Frontend (TypeScript):**

- Follow project ESLint configuration (`eslint-config-next`)
- Use TypeScript strict mode
- Components use PascalCase, hooks use camelCase
- Prefer functional components and hooks

### Run Lint

```bash
# Backend (using ruff)
cd backend
ruff check .

# Frontend
cd frontend
npm run lint
```

## Submitting a Pull Request

1. **Ensure tests pass**: `make test`
2. **Update documentation**: If changes affect API or configuration, update relevant docs
3. **Update CHANGELOG**: Add change description to `CHANGELOG.md`
4. **Create PR**:
   - Title follows Conventional Commits format
   - Description includes: what changed, related issues, testing steps, screenshots (if applicable)
   - Link issues (use `Closes #123` syntax)

### PR Template

```markdown
## Description
[Brief description of changes]

## Related Issue
Closes #123

## Testing
[How to test this change]

## Screenshots (if applicable)
[Screenshots]
```

## Reporting Bugs

Please use GitHub Issues to report bugs, including:

- Bug description
- Steps to reproduce
- Expected behavior
- Actual behavior
- Environment info (OS, Docker version, browser, etc.)
- Screenshots/logs (if applicable)

## Feature Requests

We welcome feature requests! Please:

1. Search existing issues first to avoid duplicates
2. If none exists, create a new issue describing:
   - Feature description
   - Use case
   - Expected outcome

## Becoming a Core Contributor

If you contribute consistently (3+ merged PRs), we may invite you to become a core contributor, granting:

- Write access to the repository
- Participation in project decisions
- Code review permissions

## Code of Conduct

This project follows the [Contributor Covenant](CODE_OF_CONDUCT.md). By participating, you agree to abide by its terms.

## License

This project is licensed under the MIT License. By submitting a PR, you agree that your contributions will be licensed under the MIT License.

---

Thank you for your contributions!
