# Start here (solo run with Antigravity)

## Before the first prompt (you)
1. Open this folder in Antigravity as the workspace. Run `git init`, `git add .`, `git commit -m "Initial docs and rules"`.
2. Have your PayPal developer login ready (task P0.1 is yours).
3. Decide which LLM the finished app will use (needed at task P6.0). This is separate from the tools you build with.

## Prompts to paste
**Kickoff (first time only)**
```
Read .agent/rules/resolveai.md, docs/TASKS.md and START-HERE.md. Tell me the rules in your own words, the first three unchecked tasks, and which of them are mine. Do not start any task yet.
```

**Next task (repeat)**
```
next
```
(The workflow in .agent/workflows/next-task.md and the rules tell the agent what to do. If it ignores them, paste: "Follow .agent/workflows/next-task.md and do the next unchecked task in docs/TASKS.md.")

**Resume after a new session or a usage limit**
```
Read .agent/rules/resolveai.md and docs/TASKS.md. Tell me the last task marked done, the next unchecked task, and whether the working tree has uncommitted changes. Do not start work until I say next.
```

**At a gate**
```
gate passed
```
(Only after you have checked the evidence yourself and committed.)

**When something fails**
```
Stop. Explain what failed and why, show the exact error, and propose a fix. Do not change anything until I approve.
```

## Habits
- Progress lives in docs/TASKS.md, not in the chat, so any new session can pick up where you stopped.
- Commit after every accepted task.
- Use Planning mode for complex tasks (auth, decision logic, executor, dispute pipeline, security and evaluation). Fast mode is fine for small UI changes.
- Run the app and click through it yourself at each gate. Do not rely on "it works".
- Never paste secrets into prompts. Keep them in `.env`.

## Limits to expect
- The agent cannot create your PayPal accounts, hold your keys, pick your LLM provider or record your demo. Those tasks are tagged [YOU].
- Usage limits can interrupt long runs. That is why each run is one task.
- The plan has no fixed dates for solo work. Time your first few tasks and extrapolate to your deadline. If you run short, drop later steps in this order: Phase 1b polish, Phase 3, Phase 11, Phase 7b.
