---
description: Why Exordio treats the repository as the durable harness for AI-assisted development.
---

# Exordio: A spell for good beginnings

*Marcus Gawronsky · 3 November 2026*

![Exordio wordmark](../assets/exordio-wordmark.svg)

The agent boom has shifted who, where and how we build software. In 2022, we started with prompt engineering: using N-shot, Chain-of-Thought and Persona Patterns to help exploit pre-training in ChatGPT. In 2025, the hype turned to tool use and Retrieval Augmented Generation (RAG), as context engineering aimed to ground model outputs allowing platforms like Perplexity, DeepResearch and Harvey to gain massive popularity.

Today, while innovations like hash-anchored edits sand-boxing have revolutionised the Harness Engineering, most users don't even think about prompts, tools or guardrails. Post-training has advanced rapidly, allowing platforms like Claude Desktop, Meta Muse and GrokBot to proliferate among non-technical users, begging the question: "Is Harness Engineering dead?"

Despite this progress, many developers and users still find major frustrations and barriers when working with agents. Google have pushed Open Knowledge Format to help major corporations better encode and share domain-knowledge across teams and projects, and both SKILL.md and plugins have seen massive popularity.

Yet organising knowledge is only half the problem. A SKILL.md file can be outdated, a plugin can behave unexpectedly, and two agents working on the same project can make entirely different assumptions about its architecture, dependencies and environment.

With more code is being written than ever, the infrastructure, tooling and reliability of that software is now more important than ever, and yet much of it is not version controlled, or even checked for major and obvious security vulnerabilities like plain-text secrets or known supply-chain attacks, which explain recent horror stories of open-weights models leaking information back to foreign servers and leaked secrets used to hack major US companies.

As agents accelerate software production, these distinctions become increasingly important. The bottleneck is shifting away from generating code and towards verifying that code, maintaining the knowledge behind it, and ensuring that code can be hosted and scaled, securely. It is no surprise then that PaaS vendors like Vercel, Netlify and Fly.io are seeing record growth alongside the almost explosion in rust adoption, as developers combat the chaos of agentic coding with formalism of type-checking, static analysis tools, and even formal software verification.

## What Remains? The Repository

As agents become more capable, an important question is what remains when the conversation ends, the model changes, or another agent inherits the project. Source code is only one part of the answer. The dependencies, architectural decisions, project knowledge, validation rules and operating environment all influence whether subsequent work can be understood and reproduced.

This is where repo engineering comes in: treating the repository not just as a place to store code, but as the source of truth for the agent's knowledge, operating environment and validation rules. Rather than relying on prompts to encourage correct behaviour, developers can encode assumptions as schemas, lock dependencies, validate references, synchronise agent configurations and restrict access to secrets. The model remains probabilistic, but the surrounding system introduces deterministic checks.

At its core, Exordio is a project template built around this idea: the environment, knowledge and rules an agent needs to work effectively should live alongside the code it produces.

## Reproducibility from the First Commit

Modern projects rarely operate within a single language or toolchain. Python dominates much of data analysis, TypeScript remains central to web development, and academic research may combine LaTeX manuscripts with Lean4 mathematical proofs. While specialised languages have different strengths, keeping related components within a shared repository allows agents to inspect their interfaces, dependencies and underlying implementations.

Built on Copier, Exordio allows developers to select only the capabilities they need, from Python and TypeScript workspaces to Markdown planning, academic references and Lean4 projects integrating Mathlib, LeanArchitect and LeanBlueprint. The intention is not to impose a universal development framework, but to establish consistent project structures that agents and human contributors can navigate without repeatedly reconstructing their conventions.

Reproducibility, however, extends beyond directory structure. An agent may successfully execute a Python script locally, only for another agent to encounter incompatible dependencies, compiler versions or system libraries. Identical source code does not guarantee an identical execution environment.

Exordio uses Nix and Devenv to define a pinned development environment, with consistent commands for setup, execution and validation. This reduces dependence on undocumented local configurations, allowing developers, agents and CI systems to work from a common toolchain. Pinning does not guarantee that dependencies are secure or that every build is bit-for-bit reproducible, but it makes much of the environment explicit and reconstructable.

Yet reproducing the environment is only part of the problem. Projects also depend on the knowledge and decisions accumulated during development.

## From Context Engineering to Knowledge as Code

As agents increasingly work across longer tasks and multiple sessions, maintaining a consistent understanding of the project becomes difficult. Knowledge is scattered across README files, task trackers, design documents and agent-specific instructions. A developer closes an issue but forgets to update the roadmap; an agent modifies an implementation without updating its documentation; another agent begins working from yesterday's assumptions.

These difficulties become more pronounced with parallel agents. In Cursor's research on agent swarms, competing architectural decisions, conflicting changes and the accumulation of inconsistent context emerged as important coordination problems. One response involved recording shared decisions in documents that subsequent agents could inspect, rather than depending entirely on direct communication between them.

Perhaps the most interesting part of Exordio is its integration with Insitu, a Git-native reactive Markdown engine that treats documentation as structured, queryable data.

Instead of introducing another knowledge database or dashboard, Insitu uses ordinary Markdown and YAML front matter as the source of truth. Files are indexed into SQLite, queried using SQL and rendered back into Markdown through templates. Change a task's status, run insitu sync, and the corresponding roadmap can be updated automatically. Run insitu check, and stale generated views become validation failures rather than silently outdated documentation.

Importantly, these generated views live inside the repository itself. They can be inspected in VS Code, rendered on GitHub, compared in pull requests and committed alongside the records from which they were derived. There is no requirement for a proprietary viewer or continuously running external memory service.

This creates an interesting inversion of traditional RAG-based approaches. Rather than relying solely on an agent to retrieve potentially contradictory documents, developers can maintain canonical records and automatically derive the indexes, relationships and summaries that agents consume. Insitu does not replace retrieval, provide real-time coordination or guarantee that the underlying knowledge is correct. It provides a deterministic way of keeping derived representations consistent with their recorded sources.

## Putting Deterministic Checks Around Probabilistic Agents

Of course, keeping project knowledge consistent does not make it correct. An LLM can still invent a dependency, misunderstand a requirement or confidently declare that a task is complete when it isn't.

Consider a familiar scenario: an agent finishes implementing a feature, updates its documentation and reports success. But the task metadata is malformed, an internal reference points to a nonexistent file, and the generated roadmap still shows the feature as unfinished. To another model, these problems might be invisible. To a deterministic validator, they are testable conditions.

Exordio combines several tools addressing different aspects of this problem. Schematter validates structured documentation against explicit schemas, rumdl checks Markdown formatting and local links, and Lychee can test external links when explicitly requested. Its optional planning workflow also enforces completion rules, including checked acceptance criteria and restrictions on closing parent tasks while children remain open.

These checks can run through Prek, just check and GitHub Actions, making validation part of the project rather than an instruction an agent may or may not follow.

As Birgitta Böckeler argues in her work on harness engineering, agent environments benefit from both guides, which steer behaviour before an action, and sensors, which evaluate its results and enable correction. Existing software engineering practices such as tests, linters and static analysis provide precisely this kind of feedback.

These tools aren't revolutionary individually. Nor can they establish that an external source supports a claim or that an implementation satisfies every unstated requirement. But when generating plausible output becomes cheap, the ability to reject structurally invalid or inconsistent output becomes increasingly valuable.

## Shared Instructions and Bounded Access

Working across different agents introduces another problem: the project may be shared, but its instructions are often specific to a particular harness. A developer using Claude Code and a colleague using Codex may receive different guidance about architecture, conventions or validation commands, despite working on the same repository.

Exordio optionally integrates AgentSync, which projects shared instructions into supported Claude Code and Codex configurations. The objective is not to replace their native capabilities, but to reduce configuration drift and make common project expectations more portable between developers and agents.

Credentials present a different challenge. Historically, keeping .env files out of Git was a common precaution. Agents capable of executing commands and interacting with external services introduce broader questions about when credentials should become available and which processes actually require them.

Exordio's optional SecretSpec integration resolves configured credentials for an explicitly chosen command, rather than automatically loading secrets when a development shell starts. This does not prevent an authorised process from misusing a credential, but it makes access more deliberate and reduces unnecessary exposure.

Both integrations move responsibilities that might otherwise depend on informal prompting into explicit, inspectable project configuration.

## Reproducibility Beyond the Agent

Better models will continue to write more code, use more tools and operate with less human supervision. But larger context windows cannot guarantee accurate knowledge, more sophisticated reasoning cannot guarantee correct implementations, and better prompting cannot substitute for enforceable constraints. What we need is a way to combine the flexibility of probabilistic models with the predictability of deterministic systems.

As agent adoption expands across major corporations, these challenges will increasingly extend beyond traditional software development. Employees who have never used Git or a package manager can now build applications, automate workflows and share software across teams. Initiatives such as Google's Open Knowledge Format reflect a growing interest in making institutional knowledge accessible to AI systems, but access to knowledge is only part of the problem. Companies will also need to reconsider how internal procedures, shared libraries, credentials and software dependencies are maintained when non-technical employees become software creators. Version control, reproducible environments and validation may increasingly become organizational concerns rather than practices confined to engineering teams. The challenge will not simply be giving more employees access to agents, but developing the infrastructure that allows their work to be understood, secured and reused.

Exordio is one attempt to make that infrastructure accessible from the beginning of a project. Building the repository as the harness.

---

*Originally published on [LinkedIn](https://www.linkedin.com/pulse/exordio-spell-good-beginnings-marcus-gawronsky-fcz1f/) on 3 November 2026. Republished here as the project-specific edition.*
