# Security Policy

## Reporting a Vulnerability

The PrivClaw team takes security seriously. If you discover any security vulnerabilities, please contact us:

- **Email**: security@privclaw.com (pending setup)
- **GitHub Security Advisories**: Submit a private report via [GitHub Security](https://github.com/privclaw/privclaw/security/advisories)

**Please do not report security issues through public Issues**, so we have time to fix them before public disclosure.

## Response Commitment

- **Acknowledgment**: Within 24 hours
- **Initial Assessment**: Within 48 hours
- **Fix Plan**: Within 7 days (48 hours for critical vulnerabilities)
- **Public Disclosure**: Within 30 days after fix release

## Security Best Practices

### Deployment Security

1. **Never commit `.env` files to the repository**
2. **Use strong random keys in production** (`APP_SECRET_KEY`, `JWT_SECRET`)
3. **Enable HTTPS in production** (Let's Encrypt or commercial certificates)
4. **Update dependencies regularly** (use Dependabot or manual checks)

### Key Management

- Use environment variables or secret management services (e.g., AWS Secrets Manager, HashiCorp Vault)
- Rotate JWT signing keys regularly
- Use RSA2 (2048-bit or above) for Alipay private keys

### Data Security

- Sensitive data (email, phone) encrypted with AES-256-GCM at rest
- Passwords hashed with bcrypt (planned upgrade to Argon2id)
- Database connections use SSL/TLS encryption

## Known Security Limitations

| Limitation | Status | Plan |
|------------|--------|------|
| JWT using HS256 (symmetric) | ✅ RS256 supported | Set `JWT_ALGORITHM=RS256` to switch |
| No refresh token rotation | Current | Planned |
| Password hashing uses bcrypt | Current | Planned upgrade to Argon2id |
| Sensitive data encryption | ✅ AES-256-GCM implemented | Use `encrypt_field()` / `decrypt_field()` |

## Security Audits

We welcome independent security researchers to audit PrivClaw. Audit results will be published through Security Advisories.

## Version Security Support

| Version | Security Updates |
|---------|-----------------|
| v1.x | Active support |
| v0.x | No longer supported |

---

Thank you for helping make PrivClaw more secure!
