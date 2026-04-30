name: Pull Request
description: Submit a pull request to PrivClaw
title: ""
labels: []
body:
  - type: markdown
    attributes:
      value: |
        Thanks for contributing to PrivClaw! Please fill out the information below.
  - type: input
    id: issue
    attributes:
      label: Related Issue
      description: Link to the issue this PR addresses (e.g., Closes #123).
      placeholder: Closes #
  - type: textarea
    id: description
    attributes:
      label: Description
      description: Briefly describe the changes in this PR.
    validations:
      required: true
  - type: textarea
    id: testing
    attributes:
      label: How to Test
      description: Describe how to test these changes.
      placeholder: |
        1. Run `make dev`
        2. Navigate to ...
        3. Verify that ...
    validations:
      required: true
  - type: textarea
    id: screenshots
    attributes:
      label: Screenshots
      description: If applicable, add screenshots to demonstrate the changes.
  - type: dropdown
    id: type
    attributes:
      label: PR Type
      description: What kind of change does this PR introduce?
      options:
        - feat (new feature)
        - fix (bug fix)
        - docs (documentation)
        - style (code style)
        - refactor
        - test
        - chore
    validations:
      required: true
  - type: checkboxes
    id: checklist
    attributes:
      label: Checklist
      description: Please ensure your PR meets these requirements.
      options:
        - label: I have read the [Contributing Guide](../CONTRIBUTING.md)
          required: true
        - label: I have added tests that prove my fix is effective or that my feature works
          required: false
        - label: I have updated the documentation accordingly
          required: false
        - label: I have run `make test` and all tests pass
          required: true
        - label: My commits follow the [Conventional Commits](https://www.conventionalcommits.org/) specification
          required: true
  - type: checkboxes
    id: terms
    attributes:
      label: Code of Conduct
      description: By submitting this PR, you agree to follow our [Code of Conduct](../CODE_OF_CONDUCT.md).
      options:
        - label: I agree to follow this project's Code of Conduct
          required: true
