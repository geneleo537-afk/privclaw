# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Refresh token rotation mechanism (planned)
- WeChat Pay integration (planned)
- Plugin review system frontend UI (planned)
- Admin dashboard data visualization (planned)

### Security
- Plan to migrate password hashing to Argon2id

---

## [1.2.0] - 2026-05-01

### Added
- **JWT RS256 support**: Asymmetric encryption with RSA key pairs, auto-generates keys on first use
- **AES-256-GCM encryption utility**: `DataEncryption` class for sensitive data (email, phone, etc.)
- **Ruff linter & formatter**: pyproject.toml configuration with PEP 8 + bugbear + simplify rules
- **pytest coverage**: Added `pytest-cov` for code coverage reporting
- **Encryption tests**: 12 test cases for AES-256-GCM encrypt/decrypt/key generation
- **Wallet schema tests**: 7 test cases for withdrawal request validation
- **Order schema tests**: 6 test cases for order response and payment requests

### Changed
- `security.py` refactored to support both HS256 and RS256 algorithms
- CI workflow now includes ruff format check and coverage upload to Codecov
- Makefile `test` command now includes `--cov=app --cov-report=term-missing`

### Security
- JWT can now use RS256 (asymmetric) by setting `JWT_ALGORITHM=RS256`
- Sensitive data encryption utility ready for production use
- RSA private keys automatically excluded from git via `.gitignore`

---

## [1.1.1] - 2026-04-30

### Added
- PrivClaw brand rebranding from LobsterMart
- Design system with unified design tokens
- Production deployment with Docker Compose
- HTTPS with self-signed certificate + HSTS
- Security hardening: CORS restriction, password minimum 8 characters, production key validation
- Nginx rate limiting and security headers

### Changed
- Updated CORS policy to restrict origins
- Upgraded to FastAPI 0.115.6
- Updated to Next.js 15 + React 19

### Fixed
- Settlement unique constraint (Alembic migration 002)
- Production environment key validation

### Security
- Added production key validation to prevent default secret usage
- Nginx scanner/crawler UA blocking

---

## [1.0.0] - 2026-03-10

### Added
- User authentication system (JWT dual token: access + refresh)
- User management (roles: buyer/developer/admin)
- Plugin CRUD with version management
- Plugin file upload (MinIO/OSS)
- Full-text search with PostgreSQL TSVECTOR
- Category system with tree structure
- Order system with timeout auto-close (Celery 30 minutes)
- Payment system (Alipay face-to-face + wallet balance)
- Wallet system (recharge, withdrawal, balance management)
- Admin dashboard (user management, plugin review, order management)
- Frontend brand pages (home, about, contact)
- Docker Compose development environment
- Database schema with 14 tables
- Alembic database migrations
- Demo seed data script

[Unreleased]: https://github.com/privclaw/privclaw/compare/v1.1.1...HEAD
[1.1.1]: https://github.com/privclaw/privclaw/compare/v1.0.0...v1.1.1
[1.0.0]: https://github.com/privclaw/privclaw/releases/tag/v1.0.0
