name: Bug Report
description: Report a bug to help us improve PrivClaw
title: "[Bug]: "
labels: ["bug", "triage"]
body:
  - type: markdown
    attributes:
      value: |
        Thanks for taking the time to fill out this bug report!
  - type: textarea
    id: description
    attributes:
      label: Bug Description
      description: A clear and concise description of what the bug is.
      placeholder: Tell us what happened...
    validations:
      required: true
  - type: textarea
    id: reproduction
    attributes:
      label: Steps to Reproduce
      description: Steps to reproduce the behavior.
      placeholder: |
        1. Go to '...'
        2. Click on '...'
        3. Scroll down to '...'
        4. See error
    validations:
      required: true
  - type: textarea
    id: expected
    attributes:
      label: Expected Behavior
      description: A clear and concise description of what you expected to happen.
    validations:
      required: true
  - type: textarea
    id: actual
    attributes:
      label: Actual Behavior
      description: A clear and concise description of what actually happened.
    validations:
      required: true
  - type: dropdown
    id: environment
    attributes:
      label: Environment
      description: Where are you running PrivClaw?
      options:
        - Docker Compose (local)
        - Docker Compose (production)
        - Manual installation
        - Other
    validations:
      required: true
  - type: input
    id: version
    attributes:
      label: PrivClaw Version
      description: What version of PrivClaw are you running?
      placeholder: e.g., v1.1.1
  - type: input
    id: os
    attributes:
      label: Operating System
      description: What OS are you using?
      placeholder: e.g., Ubuntu 22.04, macOS 14, Windows 11
  - type: textarea
    id: logs
    attributes:
      label: Relevant Log Output
      description: Please copy and paste any relevant log output.
      render: shell
  - type: textarea
    id: screenshots
    attributes:
      label: Screenshots
      description: If applicable, add screenshots to help explain your problem.
  - type: checkboxes
    id: terms
    attributes:
      label: Code of Conduct
      description: By submitting this issue, you agree to follow our [Code of Conduct](../CODE_OF_CONDUCT.md).
      options:
        - label: I agree to follow this project's Code of Conduct
          required: true
