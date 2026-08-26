# Model routing and usage

Three engines. Most work belongs on the middle one. Routing badly is the most common way to
spend the firm's allowance on nothing.

## The routing table

| Task | Model | Effort | Why |
|---|---|---|---|
| Reformatting a table, tidying data, a short reply, checking a definition | **Haiku** | Default | Mechanical. Speed matters, judgement does not |
| Extracting fields from a document into a table | **Haiku** | Default | Extraction, not interpretation |
| Log reconciliation and exception listing | **Haiku** | Default | Comparison against a rule |
| Drafting an IM section, a teaser, a dossier | **Sonnet** | Default | The everyday workhorse |
| Buyer universe, sector screen, outreach, process update | **Sonnet** | Default | Structured judgement against a written method |
| Client emails and updates, research summaries, meeting debriefs | **Sonnet** | Default | Volume work where quality and speed both count |
| Q&A answers drafted from the room | **Sonnet** | Raised | Consistency across dozens of answers matters |
| Deal structuring notes, offer comparison, negotiation preparation | **Opus** | Raised | Genuinely hard, and expensive to get wrong |
| Board-level advisory papers, complex diligence review | **Opus** | Raised | Multi-part reasoning under uncertainty |
| Equity story stress-testing, "what would a buyer attack" | **Opus** | Raised, extended thinking | Adversarial reasoning is where the tier earns its cost |

Two further dials sit alongside the model: **effort**, which controls how thorough Claude is
with every response, and **extended thinking**, which lets it reason before answering.
Leave both on default for routine work. Raise them when the answer genuinely has to be
right, and expect to wait longer.

## In the agent cookbooks

| Role | Model ID |
|---|---|
| Orchestrator on a hard stage (diligence, offers) | `claude-opus-5` |
| Orchestrator on a drafting stage (IM, buyer universe, origination) | `claude-sonnet-5` |
| Leaf worker: reading, extraction, reconciliation | `claude-haiku-4-5-20251001` |
| Leaf worker: drafting or scoring | `claude-sonnet-5` |

An orchestrator on Opus with Haiku readers underneath is usually both better and cheaper
than everything on Sonnet: the expensive tier sees only the structured results, not the raw
documents.

## Where the allowance actually goes

The five patterns that consume it, in order:

1. **Re-pasting the same documents** into every new conversation. Work inside the Project.
2. **Very long threads**, where the whole history is re-read every turn. Start fresh when
   the task changes.
3. **Opus on work Sonnet would have handled.** Check the table above before reaching for it.
4. **Agentic work left on automatic approval**, which adds a safety check to every action.
5. **Six small prompts** where one structured prompt would have done.

## Six habits

1. Work inside a Project so context is loaded once, not pasted every time.
2. Edit your previous message rather than adding a correction underneath it.
3. Ask for everything you need in one structured prompt — Role, Task, Context, Format,
   Constraints.
4. Start a fresh conversation whenever the task genuinely changes.
5. Haiku for the trivial, Opus only when it matters.
6. Reserve agents for work that is genuinely multi-step. Chat is cheaper and easier to
   steer sentence by sentence.

## Agent runs cost more, and are worth it selectively

An agent plans, executes and returns finished files, and keeps working when the laptop is
shut. It also consumes considerably more than a chat. The test: would this have taken a
person more than an hour of mechanical assembly across more than one document or system? If
yes, run the agent. If no, use chat and a skill.

Usage is visible per person in Settings → Usage. The allowance refreshes on a rolling
basis; hitting it costs the afternoon, not the day.
