# Antigravity — Maksimal Quvvat Rejasi

> **Qanday ishlatiladi:** Har bir "PROMPT" bloki — Antigravity'ga to'g'ridan-to'g'ri nusxa ko'chirib qo'yiladigan matn. Tartib bilan boring: 0 → 1 → 2 → ... Har bosqich oldingisining natijasiga tayanadi.
>
> **Til haqida:** Prompt bloklari ingliz tilida yozilgan — agentlar ingliz tilida ancha barqaror ishlaydi. Tushuntirishlar o'zbekcha.

---

## 0-BOSQICH — Antigravity o'zini o'rgansin (eng muhim qadam)

Antigravity versiyalari orasida fayl yo'llari, slash command formati va sub-agent mexanizmi farq qilishi mumkin. Shuning uchun birinchi ish — agentning o'ziga o'z muhitini skanerlatish.

**PROMPT 0 — Capability Discovery**

```
You are running inside Google Antigravity. Before we write any code, I need you to
produce an accurate, evidence-based map of YOUR OWN capabilities in THIS build.

Do not guess. For every claim, cite the evidence (a file you read, a menu you found,
a command you ran, or a doc page you opened).

Investigate and report on:

1. CONFIG SURFACE
   - Which config directory does this build use? Check for: .antigravity/, .agent/,
     .windsurf/, .cursor/, .github/, and any AGENTS.md / GEMINI.md / CLAUDE.md
     convention. Read the docs or settings UI to confirm.
   - Where do project-level rules live? Where do global/user-level rules live?
   - What is the file format (Markdown? YAML frontmatter? JSON?) and are there
     size or token limits per rule file?

2. SLASH COMMANDS / WORKFLOWS
   - Are custom slash commands supported? What directory and file format?
   - Can a command accept arguments? What is the placeholder syntax?
   - Can one command invoke another?
   - List the BUILT-IN slash commands available right now.

3. SUB-AGENTS / PARALLEL EXECUTION
   - Can I spawn sub-agents or parallel agents? Through the Agent Manager UI,
     through a tool call, or both?
   - Can sub-agents be given distinct roles, distinct models, or distinct tool
     permissions? How is that configured?
   - How do sub-agents report back — shared workspace, artifacts, or messages?
   - What is the max number of concurrent agents?

4. SKILLS / EXTENSIONS / PLUGINS
   - Is there a "skills" concept (reusable instruction bundles)? Where do they live?
   - Which MCP servers are configured right now? Where is the MCP config file?
   - Is the VS Code extension marketplace available, and which extensions are active?

5. TOOLS
   - List every tool you can currently call, with a one-line description each.
   - Confirm specifically: browser control, terminal, file edit, web search,
     image/screenshot capture, git operations.
   - Is the browser extension installed and connected? Test it on example.com
     and show me the screenshot.

6. ARTIFACTS
   - Which artifact types can you produce (implementation plan, task list,
     walkthrough, screenshot, browser recording, diff review)?
   - Where are they stored on disk?

7. MODELS
   - Which models are selectable? Which one am I talking to right now?
   - Can different agents use different models in the same workspace?

8. MEMORY / KNOWLEDGE
   - Is there a persistent knowledge base or memory across sessions?
   - How do I write to it deliberately? How do I inspect what's stored?

OUTPUT: Write your findings to `docs/ANTIGRAVITY_CAPABILITIES.md` with a
"Confirmed / Unconfirmed / Not available" status for every item. Then give me a
short summary of the 5 most powerful capabilities I am currently NOT using.
```

**Nima uchun bu muhim:** shu fayl chiqqandan keyin qolgan barcha bosqichlarni aniq yo'llar bilan moslashtirasiz. Agar biror narsa "Not available" chiqsa, o'sha qismni tashlab ketasiz.

---

## 1-BOSQICH — Loyiha Konstitutsiyasi (AGENTS.md)

Bu — agent har bir so'rovda o'qiydigan asosiy qonun. Qisqa, qat'iy va bajariladigan bo'lishi kerak. 150 qatordan oshmasin — uzun bo'lsa agent e'tiborini yo'qotadi.

**PROMPT 1 — Constitution generator**

```
Create the project constitution file. Use the exact path and format you confirmed
in docs/ANTIGRAVITY_CAPABILITIES.md (AGENTS.md at repo root unless you found
otherwise).

First, scan the repository and derive the real facts — do not invent conventions
that the code does not follow. Run the build, run the tests, read package manifests,
check CI config.

Then write the constitution with these sections, keeping the whole file under
150 lines:

## Project
One paragraph: what this is, who uses it, what "working" means.

## Stack (verified)
Language + version, framework + version, package manager, database, test runner,
build command, dev command, lint command, typecheck command.
Every command must be one you actually ran successfully.

## Architecture invariants
The 5-10 rules that must never be broken. Examples: layer boundaries, where
business logic may live, what may import what, how errors propagate, how config
is read. Derive these from the existing code.

## Definition of Done
A change is not done until: it typechecks, it lints clean, tests pass, new
behaviour has a test, the browser flow was verified with a screenshot (for UI),
and no TODO/FIXME was introduced.

## Hard rules
- Never commit secrets. Never edit .env. Never run destructive git commands
  (reset --hard, push --force, clean -fd) without explicit approval in chat.
- Never invent an API — read the actual source or docs before calling anything.
- Never mark a task complete on the basis of "should work". Run it.
- If blocked twice on the same error, stop and ask instead of trying a third guess.

## Style
Formatting authority (prettier/ruff/gofmt config), naming conventions, comment
policy, commit message format.

After writing it, verify: re-read the file and check every command in it by
running it. Fix anything that fails.
```

---

## 2-BOSQICH — Rules (kontekstga qarab yoqiladigan qoidalar)

AGENTS.md — doim o'qiladi. Rules — faqat kerakli paytda. Bu token tejaydi va aniqlikni oshiradi.

**PROMPT 2 — Rule pack**

```
Create the rule files in the rules directory you confirmed. Each rule file must
have a trigger/glob so it only loads when relevant. If this build supports
frontmatter with globs or activation modes, use it; otherwise put the trigger
condition in the first line of the file.

Create these rules, each under 60 lines, each with concrete DO / DON'T examples
taken from this repository's real code:

1. frontend.md      — glob: components/UI files. Component structure, state rules,
                      accessibility minimums, styling system, no inline magic numbers.
2. backend.md       — glob: server/API files. Validation at the boundary, error
                      shape, logging rules, transaction handling, no N+1 queries.
3. database.md      — glob: migrations/schema. Migrations are additive and
                      reversible, never edit an applied migration, index policy.
4. testing.md       — glob: test files. What deserves a test, AAA structure,
                      no snapshot-only tests, no sleep() in tests, mock policy.
5. security.md      — always-on. Input validation, authz check placement,
                      secret handling, dependency policy, output encoding.
6. performance.md   — glob: hot paths. Budgets (bundle size, query time, TTI),
                      when to memoize and when not to.

For each rule, include a short "bad example / good example" pair using real
patterns from this codebase, not generic ones.
```

---

## 3-BOSQICH — Slash Command kutubxonasi

Bu yerda haqiqiy kuch bor: takrorlanuvchi ish oqimlarini bir marta yozib, keyin bitta buyruq bilan chaqirasiz.

**PROMPT 3 — Command library**

```
Create custom slash commands in the workflows/commands directory you confirmed,
using the exact file format and argument syntax you verified.

Build these commands. Each one must be a deterministic, numbered procedure with
explicit verification steps and a clear stop condition — not vague advice.

/plan <feature>
  Produce an implementation plan artifact: affected files, data model changes,
  API surface, edge cases, test list, rollback plan, and an ordered task list.
  Do NOT write code. End by asking for approval.

/build <task-id>
  Implement exactly one task from the approved plan. Smallest correct change.
  Run typecheck + lint + tests. Show the diff. Stop.

/verify
  Full gate: typecheck, lint, unit tests, integration tests, build.
  If any UI changed: open the browser, walk the affected flows, capture
  screenshots, compare against the intended behaviour. Report PASS/FAIL per gate
  with evidence. Never report PASS without having run the command.

/review
  Act as a hostile senior reviewer on the current diff. Check: correctness,
  security (authz, injection, secrets), error handling, race conditions,
  performance regressions, test quality, rule violations.
  Output findings as Blocker / Should-fix / Nit. Do not fix anything — just report.

/test <path>
  Write the missing tests for this file: happy path, every error branch,
  boundary values, and one regression test per bug fixed in git history for
  this file. Run them. Show coverage before/after.

/debug <symptom>
  1. Reproduce it and show the actual output.
  2. Form 3 hypotheses ranked by likelihood.
  3. Design the cheapest experiment that discriminates between them.
  4. Run it, report what it eliminated.
  5. Repeat until proven. Only then fix.
  Never fix before the root cause is proven.

/refactor <target>
  Precondition: tests covering the target must exist and pass. If not, write
  them first. Then refactor in behaviour-preserving steps, running the tests
  after each step. No feature changes allowed in the same pass.

/browser <flow>
  Drive the real app in the browser: execute the named user flow, capture a
  screenshot at every state change, check the console for errors and the
  network tab for failed requests. Produce a walkthrough artifact.

/ship
  Pre-merge gate: run /verify, run /review, confirm no secrets in the diff,
  confirm migrations are reversible, write the changelog entry, write the
  commit message. Stop before pushing and show me everything.

/learn <insight>
  Write a durable lesson into the persistent knowledge base / memory, in the
  exact mechanism you confirmed in ANTIGRAVITY_CAPABILITIES.md. Include:
  what happened, why it was wrong, the rule to follow next time.

After creating them, test each command once on a trivial input and fix any
that misfire.
```

---

## 4-BOSQICH — Sub-agentlar (parallel jamoa)

Agent Manager'ning asosiy afzalligi — bir nechta agentni bir vaqtda ishlatish. Lekin xato qilish oson: bir xil fayllarga tegadigan agentlarni parallel qo'ymang.

### Rol taqsimoti

| Rol | Vazifa | Yozish huquqi | Model tavsiyasi |
|---|---|---|---|
| **Architect** | Reja, dizayn, task breakdown | Faqat `docs/` | Eng kuchli reasoning modeli |
| **Implementer A** | Backend/API tasklari | `server/`, `api/` | Tez, kuchli kod modeli |
| **Implementer B** | Frontend tasklari | `app/`, `components/` | Tez, kuchli kod modeli |
| **Test Engineer** | Testlar | `tests/`, `__tests__/` | O'rtacha model yetarli |
| **Browser Verifier** | E2E, screenshot, konsol xatolari | Yozmaydi, faqat hisobot | Vision qo'llab-quvvatlaydigan model |
| **Reviewer** | Xavfsizlik va sifat auditi | Yozmaydi, faqat hisobot | Eng kuchli model |

**PROMPT 4 — Orchestration**

```
Set up parallel agent execution using the mechanism you confirmed.

Rules of engagement — enforce these strictly:

1. FILE OWNERSHIP. Before launching, assign each agent a disjoint set of paths.
   Two agents must never hold write access to the same file. If a task needs
   both frontend and backend changes to the same contract, define the shared
   interface FIRST, freeze it in a types file, and only then fan out.

2. CONTRACT FIRST. Any cross-agent boundary (API schema, event shape, DB type)
   is written and committed by the Architect before implementers start.

3. NO SILENT MERGES. Each agent works on its own branch or worktree. I review
   diffs before integration.

4. REPORT FORMAT. Every agent finishes with the same structure:
   - What changed (file list)
   - Evidence it works (commands run + output)
   - What I could NOT verify
   - Open questions

5. FAILURE PROTOCOL. An agent that is blocked twice on the same error stops,
   writes the blocker to the shared task list, and does not improvise.

6. SEQUENTIAL WHEN COUPLED. Refactors, migrations, dependency upgrades and
   config changes are NEVER parallelised. One agent, one at a time.

Now: take the approved plan, group the tasks into parallel-safe batches, show me
the ownership map and the batch order, and wait for my approval before launching.
```

---

## 5-BOSQICH — Brauzer bilan tekshirish (Antigravity'ning eng kuchli tomoni)

Ko'pchilik bu qismni ishlatmaydi va shu sababli "ishlaydi deb o'ylayman" darajasida qoladi.

**PROMPT 5 — Verification loop**

```
From now on, no UI-affecting task is complete until it has been verified in the
real browser. Standing procedure:

1. Start the dev server yourself and confirm it is actually serving.
2. Open the app in the browser tool.
3. Execute the user flow as a real user would — click, type, submit, navigate.
4. Screenshot every meaningful state, including the failure states.
5. Check the browser console. Any error or warning introduced by this change
   is a blocker.
6. Check the network tab. Any 4xx/5xx, any request that fires more times than
   it should, is a blocker.
7. Test the edge cases: empty state, loading state, error state, very long text,
   slow network, mobile width.
8. Produce a walkthrough artifact with the screenshots in order.

If you cannot reach the browser, say so explicitly and mark the task UNVERIFIED.
Never substitute reasoning for observation.
```

---

## 6-BOSQICH — MCP serverlar (tashqi quvvat)

Faqat haqiqatan kerakligini ulang — har bir server kontekst yeydi.

**PROMPT 6**

```
Review the MCP config. Recommend the minimal set of servers that would remove
real friction for THIS project specifically — not a generic list. For each one
justify it with a concrete task from our backlog that it would unblock.

Typical candidates: filesystem, git, the database we actually use, our issue
tracker, our docs source, a browser/fetch server, our cloud provider.

Then: for every server already configured but unused in the last sessions,
recommend removal and explain the context cost.

Show me the final config file and what each server is allowed to do. Flag any
server with write access to production as requiring my explicit approval.
```

---

## 7-BOSQICH — "100% mukammallik" darvozasi

Bu — har bir ish tugagach majburiy o'tiladigan tekshiruv.

**PROMPT 7 — Definition of Done**

```
Add this gate to the constitution and enforce it on every task.

A task is DONE only when all of these are true and you can show evidence:

[ ] Typecheck passes            → paste the command output
[ ] Lint passes                 → paste the command output
[ ] All tests pass              → paste the summary line
[ ] New behaviour has a test    → name the test
[ ] Error paths have a test     → name them
[ ] Build succeeds              → paste the output
[ ] UI verified in browser      → attach screenshots
[ ] Console clean               → state it explicitly
[ ] No secrets in the diff      → show the grep you ran
[ ] No new TODO/FIXME           → show the grep you ran
[ ] Rules not violated          → name which rule files applied
[ ] Diff is minimal             → no unrelated formatting churn
[ ] Rollback is possible        → one sentence on how

If any box cannot be ticked, the task is BLOCKED, not done. Report it as blocked.
Reporting a task as done without evidence is the single worst failure mode —
treat it as unacceptable.
```

---

## 8-BOSQICH — Xotira (sessiyalar orasida o'rganish)

**PROMPT 8**

```
At the end of every work session, without being asked, run this reflection and
write the result into the persistent knowledge base:

1. What did I get wrong on the first attempt, and why?
2. Which assumption about this codebase turned out to be false?
3. Which command or path did I have to discover the hard way?
4. Which rule should be added or tightened so this does not recur?

Write these as short imperative rules, not as a diary. Then propose the specific
edit to AGENTS.md or the rule files, and ask me to approve it.
```

---

## Ishlatish tartibi — kundalik oqim

```
1. /plan <feature>        → rejani ko'r, tasdiqla
2. Ownership map          → parallel batchlarni tasdiqla
3. /build <task>          → har bir task alohida
4. /verify                → to'liq darvoza
5. /browser <flow>        → UI bo'lsa
6. /review                → dushman ko'zi bilan
7. /ship                  → merge oldidan
8. /learn                 → sessiya oxirida
```

---

## Anti-patternlar — bularni qilmang

- **Bitta ulkan prompt.** "Menga to'liq ilova yoz" — agent adashadi. Reja → task → verify tsikli ishlaydi.
- **Bir xil faylga ikkita parallel agent.** Konflikt kafolatlangan.
- **AGENTS.md'ni 500 qatorga cho'zish.** Agent o'rtasini o'qimaydi. Qoidalarni rules fayllariga bo'ling.
- **Tekshirmasdan "tayyor" deyish.** Har bir tasdiq isbotga muhtoj.
- **Refactor + feature birga.** Diff o'qib bo'lmaydigan bo'ladi, bug yashirinadi.
- **Barcha MCP serverlarni yoqib qo'yish.** Kontekst to'lib, aniqlik tushadi.
- **Model tanlamaslik.** Reja va review — eng kuchli model. Oddiy CRUD — tezroq model.

---

## Loyiha turiga qarab moslashtirish

Yadro bir xil. Faqat quyidagi joylarni almashtiring.

### Noldan yangi web ilova
- **0-bosqichdan keyin** birinchi ish: `/plan` bilan stack tanlash. Agentga "3 ta variant, har biri uchun trade-off" deng, keyin o'zingiz tanlang. Agent o'zi tanlasa — moda stack tanlaydi.
- AGENTS.md dagi "Stack (verified)" bo'limi bo'sh bo'ladi — birinchi skeleton qurilgach to'ldiriladi.
- Sub-agentlar: Architect → (Implementer A backend ‖ Implementer B frontend) → Test → Browser Verifier.
- Brauzer verifikatsiyasi birinchi kundan yoqiladi.

### Mavjud repo — yaxshilash / refactor
- Eng muhim qo'shimcha PROMPT: agentga **avval arxeologiya** qildiring —
  `git log` bo'yicha eng tez-tez o'zgaradigan fayllar, eng ko'p bug tuzatilgan joylar, test qoplamasi eng past modullar. Shu ro'yxat refactor navbatini belgilaydi.
- Qattiq qoida: **refactordan oldin test**. Test yo'q joyni refactor qilish taqiqlanadi (`/refactor` buyrug'ida shu shart bor).
- Parallel ishlatmang. Refactor — ketma-ket.
- Har qadamdan keyin `/verify`, chunki regressiya bu yerda asosiy xavf.

### Backend / API xizmati
- `frontend.md` rule faylini tashlang, o'rniga `api-contract.md` yozing: versiyalash, xato formati, pagination, idempotentlik, rate limit.
- Brauzer o'rniga verifikatsiya = real HTTP so'rovlar. `/browser` ni `/probe` ga aylantiring: har bir endpointni `curl` bilan urib, status, schema va xato javoblarini ko'rsatsin.
- `database.md` va `security.md` rules og'irligi ikki barobar — authz tekshiruvi qayerda turishini aniq yozing.
- Load/perf budjeti Definition of Done ga kiradi (p95 javob vaqti).

### Mobil ilova
- Brauzer tooli ishlamaydi → verifikatsiya simulyator/emulyator orqali. PROMPT 5 ni shunga moslang: agent build qilsin, simulyatorda ishga tushirsin, screenshot olsin.
- Qo'shimcha rule: `platform.md` — iOS/Android farqlari, ruxsatlar (permissions), offline holat, ekran o'lchamlari.
- Definition of Done ga qo'shing: ikkala platformada build o'tdi, cold start vaqti o'lchandi.

---

## Tekshirish ro'yxati — setup tugaganini bilish

- [ ] `docs/ANTIGRAVITY_CAPABILITIES.md` mavjud va har bir band "Confirmed" yoki "Not available"
- [ ] AGENTS.md ichidagi har bir buyruq haqiqatan ishga tushgan
- [ ] Kamida 5 ta rule fayli, har birida real kod misoli
- [ ] 10 ta slash command yaratilgan va har biri bir marta sinovdan o'tgan
- [ ] Brauzer kengaytmasi ulangan va screenshot olgan
- [ ] Parallel ishlash uchun ownership map shabloni tayyor
- [ ] MCP config minimal va oqlangan
- [ ] Definition of Done konstitutsiyaga kiritilgan
- [ ] Xotiraga birinchi yozuv yozilgan
