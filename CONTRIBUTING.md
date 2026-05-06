# Contributing to Agentic-Agile Template

Thank you for your interest in contributing. This project provides a template for teams adopting Agentic-Agile Development, and contributions that improve the templates, documentation, and examples are welcome.

## Code of Conduct

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/). For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

## How to Contribute

### Getting Started

1. **Fork** the repository.
2. **Clone** your fork locally.
3. **Create a branch** from `main` for your changes.
4. **Make your changes** following the guidelines below.
5. **Submit a pull request** back to the `main` branch of this repository.

### Contribution Workflow (Agentic-Agile Style)

This project practices what it preaches. Contributions follow the Agentic-Agile workflow:

1. **Issue first.** Open a GitHub Issue describing what you want to change and why. Use the `agentic-story.md` issue template for substantial changes.
2. **Scope clearly.** Define which files your change will touch. Avoid overlapping with other open issues.
3. **Implement.** Make your changes in a feature branch. Keep changes focused on the issue scope.
4. **Self-review.** Before submitting a PR, review your own changes against the acceptance criteria in the issue.
5. **Submit PR.** Reference the issue number. Describe what changed and why.
6. **Review.** A maintainer will review your PR. Expect questions about scope, clarity, and consistency with existing templates.

### What Makes a Good Contribution

- **Template improvements:** Clearer placeholder text, better examples, additional sections that teams commonly need.
- **Documentation fixes:** Typos, broken links, unclear instructions.
- **New examples:** Worked examples in `docs/` that demonstrate Agentic-Agile patterns.
- **Process refinements:** Improvements to issue templates, workflow definitions, or configuration examples.

### What to Avoid

- Changes that make templates specific to a single tool, language, or platform (templates should remain generic).
- Adding dependencies or build tooling (this is a template repo, not a software project).
- Large restructuring without prior discussion in an issue.

## Pull Request Guidelines

- **One concern per PR.** Keep pull requests focused.
- **Descriptive title.** Summarize what changed.
- **Reference the issue.** Link to the GitHub Issue your PR addresses.
- **Explain your reasoning.** The PR description should explain why the change improves the templates.

## Commit Message Format

Use clear, descriptive commit messages:

```
<type>: <short summary>

<optional longer description>
```

Types: `docs`, `template`, `example`, `fix`, `chore`

Example:
```
docs: clarify wave execution section in epic decomposition example

Added a concrete dependency graph showing how stories map to waves.
The previous version was too abstract for teams new to the concept.
```

## License

By contributing, you agree that your contributions will be licensed under the MIT License that covers this project.
