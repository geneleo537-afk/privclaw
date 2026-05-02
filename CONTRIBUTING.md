# Contributing Guide

> **🎉 All contributions are welcome!** Whether you're fixing a typo, adding a feature, or reporting a bug – **I will review and merge PRs quickly**. Don't be shy, every contribution matters!

Thank you for your interest in contributing to PrivClaw! This guide will help you get started.

## 🚀 Quick Start (5 Minutes)

### Step 1: Fork the Repository

Click the **"Fork"** button at the top-right of this page to copy the repository to your GitHub account.

### Step 2: Clone Your Fork

```bash
git clone https://github.com/YOUR_USERNAME/privclaw.git
cd privclaw
```

### Step 3: Set Up Development Environment

```bash
# Copy environment configuration
cp .env.example .env

# Start all services (Docker required)
make dev

# Run database migrations
make migrate

# Seed demo data (optional)
make seed
```

### Step 4: Make Your Changes

- Find an issue to work on (see [Finding Issues to Work On](#finding-issues-to-work-on))
- Create a new branch: `git checkout -b feature/your-feature-name`
- Make your changes
- Run tests: `make test`

### Step 5: Submit a Pull Request

1. Push your branch: `git push origin feature/your-feature-name`
2. Go to the original repository on GitHub
3. Click **"Compare & pull request"**
4. Fill in the PR description (see template below)
5. **That's it! I'll review and merge it ASAP.**

---

##  Finding Issues to Work On

### Good First Issues

Look for issues labeled [`good-first-issue`](https://github.com/geneleo537-afk/privclaw/labels/good%20first%20issue). These are perfect for beginners!

### How to Claim an Issue

1. Find an issue you want to work on
2. Leave a comment: **"I'd like to work on this!"**
3. I'll assign it to you
4. Start coding!

### Can't Find an Issue?

- **Found a bug?** Open a new issue with the bug report template
- **Have a feature idea?** Open a new issue with the feature request template
- **Want to improve docs?** Just submit a PR directly!

---

## 📝 Development Workflow

### Branch Naming

- Features: `feature/add-dark-mode`
- Bug fixes: `fix/wallet-calculation`
- Documentation: `docs/update-readme`

### Commit Messages

We use [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>
```

**Common types:** `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

**Examples:**
```
feat(auth): add refresh token rotation
fix(wallet): correct balance calculation
docs(readme): update deployment instructions
```

### Code Style

**Backend (Python):**
- Follow PEP 8
- Use type hints
- Run `ruff check .` before committing

**Frontend (TypeScript):**
- Follow ESLint rules
- Run `npm run lint` before committing

---

##  Pull Request Template

When submitting a PR, please include:

```markdown
## Description
[Brief description of what you changed]

## Related Issue
Closes #123

## Testing
[How to test this change]

## Screenshots (if applicable)
[Screenshots]
```

---

## 🐛 Reporting Bugs

Use GitHub Issues with:
- Bug description
- Steps to reproduce
- Expected vs actual behavior
- Environment info (OS, Docker version, browser)

---

## 💡 Feature Requests

We love new ideas! Please:
1. Search existing issues first
2. Create a new issue describing the feature and use case

---

##  Becoming a Core Contributor

Contribute consistently (3+ merged PRs) and I may invite you to become a core contributor with:
- Write access to the repository
- Participation in project decisions
- Code review permissions

---

## 📜 Code of Conduct

This project follows the [Contributor Covenant](CODE_OF_CONDUCT.md). Be respectful and kind!

---

##  License

This project is MIT licensed. By contributing, you agree your contributions will be under the MIT License.

---

**Thank you for contributing! 🙏** If you have any questions, feel free to open an issue or contact me directly.
