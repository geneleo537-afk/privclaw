name: General Issue / Contribution
description: Ask a question, propose an idea, or discuss a contribution
title: "[General]: "
labels: ["question", "discussion"]
body:
  - type: markdown
    attributes:
      value: |
        Thanks for reaching out! Please fill out the relevant sections below.
        
        **Want to contribute code directly?** Check out our [Contributing Guide](../CONTRIBUTING.md) for step-by-step instructions!

  - type: dropdown
    id: type
    attributes:
      label: Issue Type
      description: What kind of issue is this?
      options:
        - Question
        - Feature Discussion
        - Contribution Proposal
        - Documentation Improvement
        - Other
    validations:
      required: true

  - type: textarea
    id: description
    attributes:
      label: Description
      description: Describe your question, idea, or proposal.
      placeholder: Tell us what's on your mind...
    validations:
      required: true

  - type: textarea
    id: context
    attributes:
      label: Additional Context
      description: Add any relevant context, screenshots, or code snippets.

  - type: checkboxes
    id: terms
    attributes:
      label: Code of Conduct
      description: By submitting this issue, you agree to follow our [Code of Conduct](../CODE_OF_CONDUCT.md).
      options:
        - label: I agree to follow this project's Code of Conduct
          required: true
