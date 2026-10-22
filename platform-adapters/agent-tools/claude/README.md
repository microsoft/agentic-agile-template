# Claude Agent Tool Adapter

This adapter provides the context file template for [Claude](https://www.anthropic.com/claude) (Anthropic's AI assistant and Claude Code CLI). Claude automatically reads a file named `CLAUDE.md` at the repository root on every session start, giving the agent immediate access to your project's purpose, structure, conventions, and workflow expectations without any manual setup. Copy the `CLAUDE.md` template from this directory to your repository root, fill in the placeholders, and Claude will use it as project context from the first interaction forward.

## Review cycle

For PR review, fix whole classes of findings, write one holistic fix plan after any high-severity finding, and batch fixes into one review triggered once on the pushed head. Stop when no high or medium findings remain, and never merge on the human's behalf. See [agentic-review-cycle.md](../../../docs/agentic-review-cycle.md).
