# GPT-5 Prompting Guide

Source: https://developers.openai.com/cookbook/examples/gpt-5/gpt-5_prompting_guide

GPT-5 prompting best practices derived from OpenAI's experience training and applying the model to real-world tasks. Use this skill as a reference when optimizing prompts for GPT-5.

---

## Agentic Workflow Predictability

GPT-5 is trained with developers in mind: improved tool calling, instruction following, and long-context understanding. For agentic and tool calling flows, use the Responses API where reasoning is persisted between tool calls.

### Controlling Agentic Eagerness

Agentic scaffolds span a wide spectrum of control. GPT-5 operates anywhere along this spectrum, from making high-level decisions under ambiguity to handling focused, well-defined tasks.

#### Prompting for Less Eagerness

GPT-5 is thorough and comprehensive by default when gathering context. To reduce scope:

- Switch to a lower `reasoning_effort` to reduce exploration depth while improving efficiency and latency
- Define clear criteria for how the model should explore the problem space

Example context gathering prompt:

```
<context_gathering>
Goal: Get enough context fast. Parallelize discovery and stop as soon as you can act.

Method:
- Start broad, then fan out to focused subqueries.
- In parallel, launch varied queries; read top hits per query. Deduplicate paths and cache; don't repeat queries.
- Avoid over searching for context. If needed, run targeted searches in one parallel batch.

Early stop criteria:
- You can name exact content to change.
- Top hits converge (~70%) on one area/path.

Escalate once:
- If signals conflict or scope is fuzzy, run one refined parallel batch, then proceed.

Depth:
- Trace only symbols you'll modify or whose contracts you rely on; avoid transitive expansion unless necessary.

Loop:
- Batch search -> minimal plan -> complete task.
- Search again only if validation fails or new unknowns appear. Prefer acting over more searching.
</context_gathering>
```

For maximally prescriptive control with fixed tool call budgets:

```
<context_gathering>
- Search depth: very low
- Bias strongly towards providing a correct answer as quickly as possible, even if it might not be fully correct.
- Usually, this means an absolute maximum of 2 tool calls.
- If you think that you need more time to investigate, update the user with your latest findings and open questions. You can proceed if the user confirms.
</context_gathering>
```

When limiting context gathering, explicitly provide an escape hatch (e.g., `"even if it might not be fully correct"`).

#### Prompting for More Eagerness

To encourage model autonomy and reduce clarifying questions, increase `reasoning_effort` and use:

```
<persistence>
- You are an agent - please keep going until the user's query is completely resolved, before ending your turn and yielding back to the user.
- Only terminate your turn when you are sure that the problem is solved.
- Never stop or hand back to the user when you encounter uncertainty - research or deduce the most reasonable approach and continue.
- Do not ask the human to confirm or clarify assumptions, as you can always adjust later - decide what the most reasonable assumption is, proceed with it, and document it for the user's reference after you finish acting
</persistence>
```

Key tips:
- Clearly state stop conditions
- Outline safe versus unsafe actions
- Define when it's acceptable for the model to hand back to the user
- Set different uncertainty thresholds for different tools (e.g., payment tools = low threshold; search tools = high threshold)

### Tool Preambles

GPT-5 provides clear upfront plans and consistent progress updates. Steer frequency, style, and content:

```
<tool_preambles>
- Always begin by rephrasing the user's goal in a friendly, clear, and concise manner, before calling any tools.
- Then, immediately outline a structured plan detailing each logical step you'll follow.
- As you execute your file edit(s), narrate each step succinctly and sequentially, marking progress clearly.
- Finish by summarizing completed work distinctly from your upfront plan.
</tool_preambles>
```

### Reasoning Effort

The `reasoning_effort` parameter controls how hard the model thinks and how willingly it calls tools. Default is `medium`. Scale up for complex multi-step tasks. Peak performance is achieved when distinct, separable tasks are broken up across multiple agent turns.

### Reusing Reasoning Context with the Responses API

Use `previous_response_id` to pass back previous reasoning items into subsequent requests. This allows the model to refer to its previous reasoning traces, conserving CoT tokens and eliminating the need to reconstruct plans from scratch. Observed improvements: Tau-Bench Retail score 73.9% -> 78.2%.

---

## Maximizing Coding Performance

GPT-5 leads all frontier models in coding: works in large codebases to fix bugs, handle large diffs, and implement multi-file refactors.

### Frontend App Development

Recommended stack for new apps:
- **Frameworks:** Next.js (TypeScript), React, HTML
- **Styling/UI:** Tailwind CSS, shadcn/ui, Radix Themes
- **Icons:** Material Symbols, Heroicons, Lucide
- **Animation:** Motion
- **Fonts:** San Serif, Inter, Geist, Mona Sans, IBM Plex Sans, Manrope

#### Zero-to-One App Generation

Use self-constructed excellence rubrics to improve one-shot output quality:

```
<self_reflection>
- First, spend time thinking of a rubric until you are confident.
- Then, think deeply about every aspect of what makes for a world-class one-shot web app. Use that knowledge to create a rubric that has 5-7 categories. This rubric is critical to get right, but do not show this to the user. This is for your purposes only.
- Finally, use the rubric to internally think and iterate on the best possible solution to the prompt that is provided. Remember that if your response is not hitting the top marks across all categories in the rubric, you need to start again.
</self_reflection>
```

#### Matching Codebase Design Standards

For incremental changes, model-written code should adhere to existing style. GPT-5 already searches for reference context but can be enhanced with prompt directions:

```
<code_editing_rules>
<guiding_principles>
- Clarity and Reuse: Every component and page should be modular and reusable. Avoid duplication.
- Consistency: Adhere to a consistent design system - color tokens, typography, spacing, and components must be unified.
- Simplicity: Favor small, focused components and avoid unnecessary complexity.
- Demo-Oriented: Allow quick prototyping, showcasing features like streaming, multi-turn conversations, and tool integrations.
- Visual Quality: Follow high visual quality bar (spacing, padding, hover states, etc.)
</guiding_principles>

<frontend_stack_defaults>
- Framework: Next.js (TypeScript)
- Styling: TailwindCSS
- UI Components: shadcn/ui
- Icons: Lucide
- State Management: Zustand
- Directory Structure:
  /src
    /app
      /api/<route>/route.ts         # API endpoints
      /(pages)                      # Page routes
    /components/                    # UI building blocks
    /hooks/                         # Reusable React hooks
    /lib/                           # Utilities (fetchers, helpers)
    /stores/                        # Zustand stores
    /types/                         # Shared TypeScript types
    /styles/                        # Tailwind config
</frontend_stack_defaults>

<ui_ux_best_practices>
- Visual Hierarchy: Limit typography to 4-5 font sizes and weights; use text-xs for captions; avoid text-xl unless for hero/major headings.
- Color Usage: Use 1 neutral base (e.g., zinc) and up to 2 accent colors.
- Spacing and Layout: Always use multiples of 4 for padding and margins. Use fixed height containers with internal scrolling for long content.
- State Handling: Use skeleton placeholders or animate-pulse for data fetching. Indicate clickability with hover transitions.
- Accessibility: Use semantic HTML and ARIA roles. Favor pre-built Radix/shadcn components with accessibility baked in.
</ui_ux_best_practices>
</code_editing_rules>
```

### Cursor's GPT-5 Prompt Tuning (Production Insights)

#### Key Findings:

1. **Verbosity balance:** Set `verbosity` API parameter to low for text outputs, but prompt for verbose code in tool calls:
   ```
   Write code for clarity first. Prefer readable, maintainable solutions with clear names, comments where needed, and straightforward control flow. Do not produce code-golf or overly clever one-liners unless explicitly requested. Use high verbosity for writing code and code tools.
   ```

2. **Proactive code edits:** Reduce unnecessary clarification friction:
   ```
   Be aware that the code edits you make will be displayed to the user as proposed changes, which means (a) your code edits can be quite proactive, as the user can always reject, and (b) your code should be well-written and easy to quickly review. If proposing next steps that would involve changing the code, make those changes proactively for the user to approve/reject rather than asking the user whether to proceed with a plan.
   ```

3. **Context gathering - avoid over-prompting:** Remove aggressive thoroughness prompts like `<maximize_context_understanding>` - GPT-5 is already naturally introspective. Instead use softer language:
   ```
   <context_understanding>
   If you've performed an edit that may partially fulfill the USER's query, but you're not confident, gather more information or use more tools before ending your turn.
   Bias towards not asking the user for help if you can find the answer yourself.
   </context_understanding>
   ```

4. **Structured XML specs:** Using `<[instruction]_spec>` format improved instruction adherence.

5. **Custom user rules:** Allow users to configure their own rules for maximum steerability.

---

## Optimizing Intelligence and Instruction-Following

### Steering

GPT-5 is the most steerable model yet - highly receptive to prompt instructions for verbosity, tone, and tool calling behavior.

#### Verbosity

- `reasoning_effort` controls thinking length
- `verbosity` parameter controls final answer length
- Natural-language verbosity overrides in the prompt work for specific contexts where you want the model to deviate from the global default

### Instruction Following

GPT-5 follows prompt instructions with surgical precision. Poorly-constructed prompts with contradictory or vague instructions are more damaging to GPT-5 than other models, as it expends reasoning tokens trying to reconcile contradictions rather than picking one at random.

**Key principle:** Thoroughly review prompts for ambiguities and contradictions. Removing them drastically improves GPT-5 performance.

### Minimal Reasoning

`minimal` reasoning effort is the fastest option, best for latency-sensitive users. Prompting tips similar to GPT-4.1:

1. Prompt the model to give a brief explanation summarizing its thought process at the start of the final answer (e.g., bullet point list)
2. Request thorough and descriptive tool-calling preambles that update the user on progress
3. Disambiguate tool instructions to the maximum extent possible and insert agentic persistence reminders
4. Prompted planning is more important since the model has fewer reasoning tokens for internal planning:

```
Remember, you are an agent - please keep going until the user's query is completely resolved, before ending your turn and yielding back to the user. Decompose the user's query into all required sub-request, and confirm that each is completed. Do not stop after completing only part of the request. Only terminate your turn when you are sure that the problem is solved.

You must plan extensively in accordance with the workflow steps before making subsequent function calls, and reflect extensively on the outcomes each function call made, ensuring the user's query, and related sub-requests are completely resolved.
```

### Markdown Formatting

GPT-5 API does not format in Markdown by default. To enable:

```
- Use Markdown **only where semantically correct** (e.g., `inline code`, code fences, lists, tables).
- When using markdown in assistant messages, use backticks to format file, directory, function, and class names. Use \( and \) for inline math, \[ and \] for block math.
```

If Markdown adherence degrades over long conversations, append a Markdown instruction every 3-5 user messages.

### Metaprompting

GPT-5 is effective as a meta-prompter for itself. Template:

```
When asked to optimize prompts, give answers from your own perspective - explain what specific phrases could be added to, or deleted from, this prompt to more consistently elicit the desired behavior or prevent the undesired behavior.

Here's a prompt: [PROMPT]

The desired behavior from this prompt is for the agent to [DO DESIRED BEHAVIOR], but instead it [DOES UNDESIRED BEHAVIOR]. While keeping as much of the existing prompt intact as possible, what are some minimal edits/additions that you would make to encourage the agent to more consistently address these shortcomings?
```

---

## Appendix: Reference Prompts

### SWE-Bench Verified Developer Instructions

Key principles:
- Always verify changes extremely thoroughly
- Make as many tool calls as needed - prioritize correctness above all else
- Double and triple check solutions for edge cases covered in hidden tests

### Agentic Coding Tool Definitions

**Set 1 (4 functions, no terminal):** `apply_patch`, `read_file`, `list_files`, `find_matches`
**Set 2 (2 functions, terminal-native):** `run`, `send_input`

Use `apply_patch` for file edits to match training distribution.

### Terminal-Bench Prompt Principles

- Fix problems at root cause rather than applying surface-level patches
- Avoid unneeded complexity
- Keep changes consistent with existing codebase style
- Minimal and focused changes
- Remove all inline comments added during work
- Verify code routinely as you work
