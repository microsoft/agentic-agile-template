# GitHub Copilot Agent Tool Adapter

This adapter provides the context file template for [GitHub Copilot](https://github.com/features/copilot). Copilot reads `.github/copilot-instructions.md` automatically in VS Code, GitHub.com, and JetBrains IDEs to apply project-specific context to all suggestions — copy the `copilot-instructions.md` template from this directory to `.github/copilot-instructions.md` in your repository, fill in the placeholders, and Copilot will use it as project context immediately. Keep the file concise: Copilot works best with focused, actionable instructions rather than exhaustive documentation.

## Review cycle

For PR review, fix whole classes of findings, write one holistic fix plan after any high-severity finding, and batch fixes into one exact-head review (`gh pr edit <pr> --add-reviewer @copilot` or re-request in the PR UI after pushing). Read threads on that head SHA, stop when no high or medium findings remain, and never merge on the human's behalf. See [agentic-review-cycle.md](../../../docs/agentic-review-cycle.md).
