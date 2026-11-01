# Answer generation: qwen3:8b, prompt v2, answerable set

42 questions. Sources: top 4 chunks after hybrid search + reranking of the top 10. Temperature 0. Run 2026-11-01 01:08.

| Check | Result |
|---|---|
| Expected document among the sources (retrieval) | 93% |
| Answered (did not abstain) | 100% |
| Cites the expected document, when it was among the sources | 100% |
| Abstained although the expected document was among the sources | 0% |
| Answers with invalid citation numbers | 0 |
| Gold-answer word overlap (rough proxy, mean) | 48% |
| Seconds per answer (median) | 83 |
| Prompt / answer tokens per second (median) | 22 / 4.2 |

The automatic checks are rough. Read the answers below: that is the real evaluation.

---

### qst_0006 (basic)

**Question:** In the draft spec about extending a routing policy engine for automated regional failover, what is the proposed priority order for evaluating different failure signals when deciding whether to shift traffic or fail over?

**Gold answer:** The draft proposes this canonical v1 signal priority order: (1) authoritative Reachability DOWN → FAILOVER (unless no healthy fallback), (2) fast/severe 5xx error burn → FAILOVER or PARTIAL_SHIFT depending on blast radius and capacity, (3) tail latency burn → PARTIAL_SHIFT first, escalating to FAILOVER if corroborated and sustained, (4) capacity exhaustion/hard gate → HOLD plus load shed (avoid shifting into constrained regions), and (5) control plane degradation → HOLD to avoid rapid flips/oscillation.

**Model answer:** The proposed priority order for evaluating different failure signals is as follows:  
1) Reachability DOWN (authoritative) => FAILOVER (unless no healthy fallback) [1].  
2) Errors (5xx) fast burn (high severity) => FAILOVER or PARTIAL_SHIFT depending on blast radius and capacity [1].  
3) Tail latency burn (p99/p95) => PARTIAL_SHIFT first; escalate to FAILOVER if corroborated and sustained [1].  
4) Capacity exhaustion / hard gate => HOLD + load shed (controller action), avoid shifting into constrained region [1].  
5) Control plane degradation => HOLD (do not flip rapidly; prevent oscillation) [1].

**Sources given:**
1. Document: Draft Spec: Policy Engine Extensions for Regional Failover Automation | Section: B) Deterministic evaluation mode (required) / C) Signal hierarchy evaluation (ADR-042) / Notes  **(expected document)**
2. Document: Draft Spec: Policy Engine Extensions for Regional Failover Automation | Section: Determinism requirements (core)  **(expected document)**
3. Document: Draft Spec: Policy Engine Extensions for Regional Failover Automation | Section: Context / why this exists / Goals  **(expected document)**
4. Document: Draft Spec: Policy Engine Extensions for Regional Failover Automation | Section: Edge cases and expected behavior  **(expected document)**

*107 s, cited [1], gate score 0.991, gold-word overlap 74%*

---

### qst_0007 (basic)

**Question:** In a rolling investigation of a model regression on policy-related prompts after a recent deploy, what was the average triage rubric score change between the older baseline build and the newer optimized build in the first comparison run?

**Gold answer:** In the first comparison run, the baseline build averaged 2.7 while the newer optimized build averaged 1.9, a decrease of 0.8 rubric points.

**Model answer:** The average triage rubric score decreased from 2.7 in the older baseline build to 1.9 in the newer optimized build in the first comparison run [1].

**Sources given:**
1. Document: Rolling bias bisection log jared | Section: Bisection timeline (rolling)  **(expected document)**
2. Document: Prep: eval deep-dive for optimize AB regression | Section: Introduction / Context / TL;DR
3. Document: Impromptu rubric stitchpad - Jorge Gomez | Section: Regression observations (pattern notes) / Mitigations I've used recently
4. Document: Rolling bias bisection log jared | Section: Introduction / Summary / TL;DR / Ad-hoc rubric (quick, for nightly triage)  **(expected document)**

*71 s, cited [1], gate score 0.956, gold-word overlap 67%*

---

### qst_0008 (basic)

**Question:** In the internal shiproom runner notes, what is the target time-to-recover threshold for a verified rollback in staging?

**Gold answer:** The rollback plan is considered verified in staging if the time-to-recover is under 10 minutes.

**Model answer:** The target time-to-recover threshold for a verified rollback in staging is less than 10 minutes [1].

**Sources given:**
1. Document: Shiproom runner: personal prep log and sticky notes | Section: MEETING AGENDA (for my 10–15 min run) / GO/NO-GO CHECKLIST (my shorthand)  **(expected document)**
2. Document: Shiproom runner: personal prep log and sticky notes | Section: EXAMPLE QUICK COMMS (copyable) / MY PERSONAL CHECKLIST BEFORE HAND-OFF / FRAGMENTS / THINGS I WANT TO INVESTIGATE (later)  **(expected document)**
3. Document: Game Day Plan: Auto-rollback on SLO breach (rollout controller integration) | Section: Target timing budgets (staging) / … / Fault injection approach (pick one)
4. Document: Onboarding acceptance playbook for experimental models | Section: Introduction

*66 s, cited [1], gate score 0.963, gold-word overlap 57%*

---

### qst_0039 (basic)

**Question:** In the 3-hour customer workshop plan for taking a team from initial evaluation to a proof of concept, what are the three types of go/no-go acceptance gates?

**Gold answer:** The three go/no-go acceptance gates are: a Quality gate (meets baseline precision/recall or user satisfaction on a representative dataset), a Performance gate (meets latency SLOs at target load with acceptable cost), and a Compliance gate (data handling and encryption meet stated requirements).

**Model answer:** The three types of go/no-go acceptance gates in the 3-hour customer workshop plan are:  
1. Quality gate: model meets baseline precision/recall or user satisfaction target on representative dataset [2].  
2. Performance gate: meets latency SLOs at target load with acceptable cost [2].  
3. Compliance gate: data handling and encryption meet stated requirements [2].

**Sources given:**
1. Document: Market Debut Sprint Scoreboard and Acceptance Gates | Section: OVERVIEW
2. Document: Zero-to-POC Canvas + 30/60/90 Facilitation Notes | Section: Introduction  **(expected document)**
3. Document: Market Debut Sprint Scoreboard and Acceptance Gates | Section: ACCEPTANCE GATES (Decision matrix) / PRE-LAUNCH CHECKLIST (top-risk items)
4. Document: Launch Gates & Metrics Inventory | Section: Introduction

*79 s, cited [2], gate score 0.690, gold-word overlap 100%*

---

### qst_0047 (basic)

**Question:** In some lab notes about reducing few-shot example copying, what tradeoff was noted when rotating the order of exemplars in prompts?

**Gold answer:** The notes say rotating exemplars can reduce position bias, but it interacts badly with prefix caching-rotating defeats the cached prefix and may require cache bypass/invalidations, making it less suitable for high-QPS routes.

**Model answer:** Rotating the order of exemplars in prompts was noted to interact badly with caching, requiring a route-aware cache bypass [1]. This tradeoff involves potential increased latency and complexity in maintaining cache efficiency while avoiding position bias [1].

**Sources given:**
1. Document: Fewshot attenuation heuristics — lab notes | Section: Prototype heuristics (to test systematically) / Failure modes observed / notes  **(expected document)**
2. Document: Prompt Cyclotron Experiments & Notes | Section: Observed failure cases (notes from quick runs) / Anchor design heuristics (initial)
3. Document: Prompt Cyclotron Experiments & Notes | Section: Introduction / Context and motivation
4. Document: Exemplar Pruning — Gambit Lab Notes | Section: Purpose / Notes on motivation

*63 s, cited [1], gate score 0.943, gold-word overlap 28%*

---

### qst_0050 (basic)

**Question:** What is the proposed HTTP header scheme for attributing API traffic to quickstart templates, including how the header value is formatted and the opt-in header?

**Gold answer:** The proposal is to tag template-originated API traffic with an optional header `X-Redwood-Template`, whose value is formatted as `<template_name>@<template_version>;<language>` (e.g., `rag-agent@1.1.0;python`). An additional opt-in header `X-Redwood-Template-Opt-In` is set to `true` or `false`.

**Model answer:** The proposed HTTP header scheme for attributing API traffic to quickstart templates includes two headers: 

- `X-Redwood-Template` with a value formatted as `<template_name>@<template_version>;<language>` [1].
- `X-Redwood-Template-Opt-In` with a value of `true` or `false` [1].

Telemetry tagging is opt-in and requires an environment variable to enable it [3].

**Sources given:**
1. Document: Quickstarts Adoption KPIs (Hosted API) — draft sheet | Section: Template tag header proposal (for api.* attribution) / Notes / TAB: Dashboard Spec (What we want in Console/Analytics) / Dashboard 1: Quickstarts Overview  **(expected document)**
2. Document: Quickstarts Adoption KPIs (Hosted API) — draft sheet | Section: TAB: Open Questions / Change log  **(expected document)**
3. Document: Template Security Review Notes (Quickstart Templates v1) | Section: Findings and actions / P0 (must fix before public launch)
4. Document: Quickstarts Adoption KPIs (Hosted API) — draft sheet | Section: Inclusion criteria / … / Activation funnel stages (see “Funnel Events” tab)  **(expected document)**

*89 s, cited [1, 3], gate score 0.922, gold-word overlap 54%*

---

### qst_0054 (basic)

**Question:** What was the decision for when and how to roll out the new lattice scheduler into a limited canary, and what condition would allow expanding it to higher traffic models?

**Gold answer:** They decided to move the lattice scheduler into a restricted canary for low-traffic models during a Mon-Wed window next week. If p95 latency improves and there are no errors, they would expand it to medium-tier (higher traffic) models.

**Model answer:** The decision was to move the lattice scheduler into a restricted canary for low-traffic models next week (canary window Mon-Wed). If p95 improves and no errors occur, it will be expanded to medium tier [1]. The condition for expansion is that p95 latency improves and there are no errors during the canary period [1].

**Sources given:**
1. Document: Kernel lattice weekly capture | Section: Standup bullets (each attendee) / Decisions taken  **(expected document)**
2. Document: Cross-domain lead strategy sync - May 18 2027 | Section: Notes / Highlights
3. Document: Launch orchestra staffing heuristics and clockwork checklist — Apr 2028 (draft) | Section: Introduction
4. Document: Canary backfill decision briefing | Section: Background & what we know / Observed impact metrics (summary)

*80 s, cited [1], gate score 0.864, gold-word overlap 62%*

---

### qst_0057 (basic)

**Question:** In our staging cluster, checkpoint downloads sometimes hang when resuming with an HTTP Range request to a cloud storage signed URL; what unexpected HTTP status code is sometimes returned instead of partial content that triggers the stall?

**Gold answer:** In the failing resume cases, the server sometimes responds with **HTTP 200 OK** (instead of the expected **206 Partial Content**) to a Range request, which triggers the stall.

**Model answer:** The unexpected HTTP status code sometimes returned instead of partial content (206) is 200 OK [2]. This causes the client to treat it as a fallback to a full download, leading to confusion in Content-Length and eventual stall [3].

**Sources given:**
1. Document: Resume download hang notes | Section: Introduction  **(expected document)**
2. Document: Resume download hang notes | Section: Introduction  **(expected document)**
3. Document: Resume download hang notes | Section: Introduction  **(expected document)**
4. Document: Resume download hang notes | Section: Introduction  **(expected document)**

*96 s, cited [2, 3], gate score 0.912, gold-word overlap 41%*

---

### qst_0062 (basic)

**Question:** What is the proposed backend API endpoint and query parameters for fetching a trace in either grouped or full detail for the console timeline view?

**Gold answer:** The playbook proposes a backend trace fetch API of `GET /v1/traces/{id}?level=grouped|full&time_window=start,end`, where `level` selects grouped vs full detail and `time_window` optionally constrains the returned data to a start/end range.

**Model answer:** The proposed backend API endpoint is `/v1/traces/{id}` with query parameters `level=grouped|full` and `time_window=start,end` [2].

**Sources given:**
1. Document: Per-invocation econ UX journey and wires | Section: Introduction
2. Document: Span timeline playbook grooming notes | Section: Implementation notes for engineers / UX validation plan / Notes to self (brain dump)  **(expected document)**
3. Document: Compact trace mode + annotation search — grooming notes | Section: Introduction
4. Document: Span timeline playbook grooming notes | Section: Purpose and scope / High-level goals (why) / Constraints and assumptions  **(expected document)**

*72 s, cited [2], gate score 0.889, gold-word overlap 43%*

---

### qst_0069 (basic)

**Question:** In an ops day log about GPU rebalancing and brief west region network instability, what was the target slot capacity for the small hosted pool in the slot metrics dashboard?

**Gold answer:** The slot-metrics dashboard target pool size for the small hosted pool (hosted-small) was 4,200 slots.

**Model answer:** The target slot capacity for the small hosted pool in the slot metrics dashboard was 4200 slots [1].

**Sources given:**
1. Document: Ops daybook: GPU rebalance + network flaps | Section: Top priorities (today)  **(expected document)**
2. Document: GPU dashboard snapshot — ops scrapbook (weekly rollup) | Section: Introduction
3. Document: GPU availability snapshot and triage - 2026-03-20 | Section: Agenda
4. Document: Capacity slot rebalancer proposal and oncall runbook draft | Section: Introduction

*98 s, cited [1], gate score 0.995, gold-word overlap 50%*

---

### qst_0079 (basic)

**Question:** In a morning account blitz note from May 2026, what was the proposed mitigation to address repeated inference timeouts for a healthcare customer with a mid-June renewal?

**Gold answer:** For Fortis Health (renewal 2026-06-15), the note proposed mitigating the recurring inference timeouts by adding a 10% reserved burst during peak windows and enabling KV-prefix caching on their main inference route.

**Model answer:** The proposed mitigation to address repeated inference timeouts for Fortis Health, a healthcare customer with a mid-June renewal, was to propose a 10% reserved burst for their peak windows and enable KV prefix caching on the main inference route [1].

**Sources given:**
1. Document: Account Blitz Log — AM rounds | Section: Introduction  **(expected document)**
2. Document: Runtime vignettes and mitigation ideas may 2026 | Section: Introduction
3. Document: Tia cs daybook qbr and renewal notes 2026 03 20 | Section: Introduction / … / Account: Fable Health (renewal Q3) — priority: medium-high
4. Document: Morning renewal triage and QBR prep - quick scratch | Section: Introduction

*92 s, cited [1], gate score 0.991, gold-word overlap 59%*

---

### qst_0085 (basic)

**Question:** What are the three request quality and cost tiers proposed in the lightweight interaction tiering model for user facing features?

**Gold answer:** The model proposes three tiers: micro (cheapest), standard (baseline/default), and deep (quality-first).

**Model answer:** The three request quality and cost tiers proposed in the lightweight interaction tiering model are micro, standard, and deep [1].

**Sources given:**
1. Document: Interaction tiering: personal idea scrapbook | Section: Introduction / Problem statements / Design principles (rough)  **(expected document)**
2. Document: Interaction tiering: personal idea scrapbook | Section: Tiers (first pass) / User stories / Acceptance signals / metrics  **(expected document)**
3. Document: Trace cost allocation and tenant chargeback proposal | Section: High-level proposal (three-tier attribution model)
4. Document: Three-tier KPI balance and fallback matrix | Section: Top-level summary (one line) / Tiers and KPIs (definitions + rationale)

*79 s, cited [1], gate score 0.988, gold-word overlap 55%*

---

### qst_0091 (basic)

**Question:** In the key rotation runbook, what is the recommended default rotation interval for per-tenant key encryption keys used to wrap data keys?

**Gold answer:** The runbook recommends rotating per-tenant Key-Encryption Keys (KEKs) every 6-12 months (with automated DEK rewraps during low-traffic windows).

**Model answer:** The recommended default rotation interval for per-tenant key encryption keys (KEK) used to wrap data keys is 6–12 months [1].

**Sources given:**
1. Document: Crypto hierarchy, rotation, and SIEM export — runbook | Section: Rotation policy matrix (recommended default)  **(expected document)**
2. Document: Envelope Key Ownership Patterns and Audit Export Guide | Section: Introduction
3. Document: KMS ops: rotation checklist, SIEM export & evidence flow | Section: Introduction
4. Document: KMS ops: rotation checklist, SIEM export & evidence flow | Section: Introduction

*79 s, cited [1], gate score 0.973, gold-word overlap 19%*

---

### qst_0094 (basic)

**Question:** What is the recommended emergency action to temporarily simplify routing policy rules when the edge route agent is causing high evaluation latency and end to end latency spikes?

**Gold answer:** Enable the emergency-compact policy set to temporarily apply a simplified ruleset, e.g., call the admin API: POST /v1/admin/policies/compact with body {"reason":"latency_immediate"}.

**Model answer:** The recommended emergency action is to enable emergency-compact policy set: POST /v1/admin/policies/compact {"reason":"latency_immediate"} to temporarily apply simplified ruleset [2].

**Sources given:**
1. Document: Routing and controlplane runbook architecture notes | Section: Common incident scenarios + runbooks  **(expected document)**
2. Document: Routing and controlplane runbook architecture notes | Section: Common incident scenarios + runbooks  **(expected document)**
3. Document: Autonomous routing fallbacks & ops runbook | Section: Misrouting / policy misapplication scenario
4. Document: Cliff's notes on requests and runtime patches | Section: Introduction

*60 s, cited [2], gate score 0.929, gold-word overlap 78%*

---

### qst_0105 (basic)

**Question:** What are the proposed internal time to mitigate targets by severity for incident response, regardless of customer deployment tier?

**Gold answer:** The proposed internal time-to-mitigate (TTM) targets (same for all tiers) are: Sev0 = 30 minutes, Sev1 = 2 hours, Sev2 = 1 business day, and Sev3 = 5 business days (or the next planned release train).

**Model answer:** The proposed internal time-to-mitigate (TTM) targets by severity for incident response, regardless of customer deployment tier, are as follows:

- Sev0: 30 minutes  
- Sev1: 2 hours  
- Sev2: 1 business day  
- Sev3: 5 business days (or next planned release train) [1][2].

**Sources given:**
1. Document: Remediation SLA options + customer tier mapping (Hosted / Dedicated / Private) — working doc | Section: Recommendation (draft): Option B for v1 / … / TTF (tier-adjusted)  **(expected document)**
2. Document: Remediation SLA options + customer tier mapping (Hosted / Dedicated / Private) — working doc | Section: Definitions  **(expected document)**
3. Document: Remediation SLA options + customer tier mapping (Hosted / Dedicated / Private) — working doc | Section: Dedicated / … / Proposed adjustment for Private only  **(expected document)**
4. Document: Remediation SLA options + customer tier mapping (Hosted / Dedicated / Private) — working doc | Section: Data sanity check (informal) / Action items (next steps)  **(expected document)**

*92 s, cited [1, 2], gate score 0.965, gold-word overlap 86%*

---

### qst_0112 (basic)

**Question:** In the proposed small business token pricing tiers, what is the monthly included token allowance for the plan priced at $25 per month?

**Gold answer:** The $25/month plan (Builder) includes 10 million tokens per month.

**Model answer:** The monthly included token allowance for the plan priced at $25 per month is 10M tokens [1].

**Sources given:**
1. Document: Nano-tiering experiments scratchpad | Section: Quick sensitivity calcs (for ops)  **(expected document)**
2. Document: Pricing psychology, metric framing, and discount guidance | Section: Tier structure (recommended draft)
3. Document: Nanobatch unit-econ scratchpad (tokens, batching, quick tiers) | Section: Pricing ramifications / tier ideas (sketch)
4. Document: Practical token economics — sales playbook & positioning | Section: Appendix — Worked example (customer pitch) / End — one-pager summary for reps

*67 s, cited [1], gate score 0.816, gold-word overlap 43%*

---

### qst_0116 (basic)

**Question:** In the SOC2 readiness notes, what log retention duration is mentioned as a risk for some environments?

**Gold answer:** The notes mention that in some environments logs are only retained for 90 days, which is flagged as a potential risk.

**Model answer:** The log retention duration mentioned as a risk for some environments is 90 days, as SOC2 reviewers might expect 12 months for certain records [1].

**Sources given:**
1. Document: Risk-thread notes — SOC2 prep (scratch) | Section: Potential risks / escalations  **(expected document)**
2. Document: Shoreline Labs POC infosec evidence & action plan | Section: Introduction
3. Document: Keystore tinkering and SOC2 readiness musing | Section: Last quick sketches (non-linear) / -- end of brain dump --
4. Document: Safeguard scratch lab: SOC2 prep fragments | Section: Introduction / Context / scope assumption (working)

*61 s, cited [1], gate score 0.958, gold-word overlap 27%*

---

### qst_0122 (basic)

**Question:** Which GPU cluster or pool was flagged as having relatively low average usage but high churn, making its free capacity unreliable during a specific morning UTC window?

**Gold answer:** APAC-eu1-pool-A was flagged for low average utilization (about 47%) but high entropy (0.72), meaning its headroom is unreliable due to churn during roughly 09:00-13:00 UTC.

**Model answer:** The APAC-eu1-pool-A was flagged as having low average utilization (47%) but high entropy (0.72), indicating frequent slot churn due to ephemeral developer jobs, making its free capacity unreliable during the 9:00–13:00 UTC window [1].

**Sources given:**
1. Document: GPU entropy + headroom export (slice & queue attribution) 2026-06-09 | Section: Introduction  **(expected document)**
2. Document: GPU utilization anomaly investigation - na clusters - march 2026 | Section: Introduction / Summary
3. Document: GPU dashboard snapshot — ops scrapbook (weekly rollup) | Section: Introduction
4. Document: GPU heatband cluster/pool weekly coverage (Jul 14-20 2026) | Section: Anomalies flagged this week / Suggested actions (prioritized)

*103 s, cited [1], gate score 0.945, gold-word overlap 74%*

---

### qst_0133 (basic)

**Question:** What are the pass fail criteria used in the quick pull request smoke checks for the embedding robustness noise and input length evaluation suite?

**Gold answer:** For the quick PR smoke checks, the suite flags failure if any of these exceed the thresholds: median cosine nearest-neighbor distance deviates by more than ±6% from baseline, NDCG@10 on curated-qrels-5lang drops by 3% absolute or more, or cluster purity drops by 5 percentage points or more.

**Model answer:** The pass/fail criteria for quick pull request (smoke) checks include: median cosine NN distance within +/- 6% of baseline; NDCG@10 drop < 3% absolute on curated-qrels-5lang; and cluster purity drop < 5 percentage points [1].

**Sources given:**
1. Document: Embedding Robustness: Noise & Length Probe Suite | Section: Introduction  **(expected document)**
2. Document: Embedding Robustness: Noise & Length Probe Suite | Section: Introduction  **(expected document)**
3. Document: Embedding Robustness: Noise & Length Probe Suite | Section: Introduction  **(expected document)**
4. Document: Embedding Robustness: Noise & Length Probe Suite | Section: Introduction  **(expected document)**

*93 s, cited [1], gate score 0.935, gold-word overlap 56%*

---

### qst_0134 (basic)

**Question:** What was the suspected root cause behind the brief p99 latency spikes on the hosted chat inference route during small burst traffic?

**Gold answer:** The leading suspicion was a KV-cache eviction storm-likely triggered by an eviction-boundary bug where a single long-context request causes aggressive shard invalidation, dropping cache hit-rate and forcing expensive cold-start decoding. This tail-latency spike may be compounded by bursty tiny micro-batches and occasional GPU memory fragmentation stalls on a worker.

**Model answer:** The suspected root cause behind the brief p99 latency spikes on the hosted chat inference route during small burst traffic was a KV cache eviction storm, hypothesized to be caused by an eviction boundary bug where a single large request (long context) triggered a cascade that invalidated shards aggressively, leading to cache cold starts and extra decoding cost [2].

**Sources given:**
1. Document: Oncall throttle tuning experiments and mitigation notes | Section: Introduction
2. Document: Latency Sculptor — daily notes and triage | Section: Morning dump (walkthrough of last 36h) / Initial hypothesis/notes  **(expected document)**
3. Document: Handoff latency snapshot and SLO audit - Jan 10 2028 | Section: Incidents (brief)
4. Document: KV cache eviction -> PCIe read amplification probe | Section: Introduction

*91 s, cited [2], gate score 0.993, gold-word overlap 20%*

---

### qst_0141 (basic)

**Question:** What was the target goal for average router queue time for very short token sequences, compared to the baseline of 28 ms, in the weekly sprint anchor about reducing staging inference queuing latency?

**Gold answer:** The goal was to reduce average router queue time for 1-8 token sequences by 10% from the 28 ms baseline, targeting about 25 ms.

**Model answer:** The target goal for average router queue time for very short token sequences was to reduce it by 10–15% from the baseline of 28 ms, aiming for a target of approximately 25 ms [1].

**Sources given:**
1. Document: Weekly Clarity Anchor: commitments & micro-experiments | Section: Purpose / Week snapshot (Mar 8 - Mar 14, 2026) / Signals I care about (leading/lagging)  **(expected document)**
2. Document: Weekend sprint notebook — KPI check-in | Section: Sprint anchor (Feb 20–26) / Signals to watch (morning checklist)
3. Document: Weekly Clarity Anchor: commitments & micro-experiments | Section: Hypotheses + micro-experiments this week (ranked)  **(expected document)**
4. Document: Ops Anchor: weekly thread & resolution notes — 2027-03-14 | Section: SLO snapshot and interpretation / Operational experiments and tuning notes

*86 s, cited [1], gate score 0.999, gold-word overlap 69%*

---

### qst_0155 (basic)

**Question:** What are the lifecycle states and key transitions for the edge adapter service that registers with a control plane and can fall back to hosted inference?

**Gold answer:** The adapter's lifecycle states are INIT (boot/verify dependencies), REGISTERING (attempting control-plane join), ACTIVE (serving local traffic), DRAINING (stop new sessions and finish existing), DEGRADED (resource failure; limited service and/or redirected to hosted), and RETIRED (operator shutdown). Key transitions are INIT → REGISTERING → ACTIVE; ACTIVE → DRAINING (operator/rollout) → RETIRED; any state → DEGRADED on resource failure; and DEGRADED → ACTIVE after recovery.

**Model answer:** The lifecycle states for the edge adapter service are INIT, REGISTERING, ACTIVE, DRAINING, DEGRADED, and RETIRED [1]. Key transitions include INIT -> REGISTERING -> ACTIVE, ACTIVE -> DRAINING (operator or rollout), DRAINING -> RETIRED, and any state -> DEGRADED on resource failure; DEGRADED -> ACTIVE after heal [1].

**Sources given:**
1. Document: Edge Runner Adapter — lifecycle & API sketch | Section: Lifecycle states (local finite-state machine)  **(expected document)**
2. Document: Edge Runner Adapter — lifecycle & API sketch | Section: Context / Design goals  **(expected document)**
3. Document: Control Plane Responsibility Atlas | Section: API Gateway specific responsibilities / Orchestration responsibilities (lifecycle & rollouts) / Runtime adapter invariants and contracts
4. Document: Edge resilience VPC onboarding cheat sheet | Section: High-level reference architecture (textual) / Minimal terraform module pattern (opinions)

*68 s, cited [1], gate score 0.972, gold-word overlap 50%*

---

### qst_0164 (basic)

**Question:** In the HyperOnboard 30-60-90 onboarding template, what are the escalation conditions that should trigger an email to people ops and the hiring manager?

**Gold answer:** The escalation triggers are: if the new hire is not shipping a measurable artifact by day 30, if access blockers persist for more than 48 hours, or if there are repeated missed meetings.

**Model answer:** The escalation conditions that should trigger an email to People Ops and the hiring manager are: not shipping a measurable artifact by day 30, ongoing access blockers >48h, and repeated missing meetings [1].

**Sources given:**
1. Document: HyperOnboard: Role Launch Snapshot and 30-90 Activation Template | Section: Manager checklist and risk mitigations / Buddy playbook (short) / Evaluation signals (early)  **(expected document)**
2. Document: Hiring Sprint OPERA Playbook — 30/60/90 Impact | Section: escalation_rules / … / next_steps
3. Document: HyperOnboard: Role Launch Snapshot and 30-90 Activation Template | Section: Hiring plan snapshot (for manager + recruiter)  **(expected document)**
4. Document: HyperOnboard: Role Launch Snapshot and 30-90 Activation Template | Section: Template: 30/60/90 milestones (copyable) / Recruiting playbook notes (ops & interviewer hints) / Open questions / TODOs (working)  **(expected document)**

*83 s, cited [1], gate score 0.969, gold-word overlap 53%*

---

### qst_0169 (basic)

**Question:** Who is responsible for signing off on latency regression in the weekly customer rollout tracker for Nimbus Health?

**Gold answer:** Maya Patel (Performance Engineer) is responsible for latency regression signoff in the Nimbus Health weekly rollout tracker.

**Model answer:** Maya Patel is responsible for latency regression signoff in the weekly customer rollout tracker for Nimbus Health [1].

**Sources given:**
1. Document: Adoption Velocity Radar — Customer Implementation Compact | Section: summary / owners / milestones  **(expected document)**
2. Document: Integration deployment & handoff check-ins — 2026-05-12 | Section: Customer updates (concise)
3. Document: Account sprint notes: renewal push + support triage (daily) | Section: TEMPLATE: outage / regression notice (short) / STAKEHOLDER MAP (Nimbus) / RISKS / OPEN QUESTIONS
4. Document: Customer Success 1:1 — cheat sheet & follow-ups | Section: Introduction

*81 s, cited [1], gate score 0.976, gold-word overlap 77%*

---

### qst_0186 (semantic)

**Question:** In the notes about keeping long, stop-and-go chat sessions cheap without replaying the whole history, what storage setup and time-to-live were proposed for keeping the compact per-session state for recent sessions versus longer retention?

**Gold answer:** The notes propose keeping hot, recent per-session anchors in a per-customer LRU store in Redis, while storing longer-term anchors in S3 with a 30-day TTL.

**Model answer:** The storage setup proposed for keeping compact per-session state involves using a KV-prefix cache that stores recent prefixes and decoder KV chunks keyed by (tenant, session_id) [2]. For time-to-live (TTL), the default retention was aggressive (30s) to limit memory pressure, but there was a proposal to increase per-session retention for high-value clients or routes to reduce repeated warmups during microburst sessions [2].

**Sources given:**
1. Document: Thread Compressor — personal PRD sketch | Section: Introduction
2. Document: Session-window retention savings sim | Section: content
3. Document: Conversation Slices — rough PRD & idea pad | Section: Introduction
4. Document: Session bridger playbook scratch | Section: Introduction / Problem statement / High-level idea: "Session Bridger"

*94 s, cited [2], gate score 0.802, gold-word overlap 19%*

---

### qst_0195 (semantic)

**Question:** From the internal sandbox microbench in the EU West lab around May 2029, what was the estimated dollars per one million tokens for the biggest model on a single 40GB GPU when using the no-batching low-latency mode on the long output workload (about 300 tokens per response)?

**Gold answer:** For the long-generate workload (~300 tokens) using rw-70b-fp16 on a single A100 40GB in fastpath (no batching) mode, the estimated cost was $31.6 per 1M tokens.

**Model answer:** The estimated dollars per one million tokens for the biggest model (rw-70b-fp16) on a single 40GB GPU (A100x1) in the no-batching low-latency mode for the long output workload (about 300 tokens per response) is approximately $1.90 per million tokens [1]. This figure is derived from the economic assumptions in the document, which use spot-equivalent cost for comparison purposes.

**Sources given:**
1. Document: Throughput-Latency Phase Portrait — mini benchmark heuristic | Section: Testbed & assumptions  **(expected document)**
2. Document: Microqueue scarcity: dollar vs latency vignette | Section: Test rig / assumptions / Parameter sweep
3. Document: Hosted API — Unit Econ Sensitivity & Batch Opportunities (draft) | Section: body
4. Document: GPU benchmarking field notes — instance sizing & token/watt heuristics | Section: Introduction

*114 s, cited [1], gate score 0.940, gold-word overlap 56%*

---

### qst_0196 (semantic)

**Question:** In the quick A100 microbenchmark notes comparing 4-bit weight compression to half precision on a 7B model at single-item batching, what speedup and quality hit were observed for the simplest run?

**Gold answer:** For the simplest A100 batch=1 run, NF4 post-training quantization on the 7B model achieved about a 1.8× token-throughput speedup versus fp16, with an estimated quality hit of roughly +0.6 perplexity on a small set of story prompts.

**Model answer:** The NF4 PTQ on 7B model showed a ~1.8x token throughput improvement over fp16 at batch=1 on A100, with a ~+0.6 ppl loss for story prompts [1].

**Sources given:**
1. Document: Microbench notelet: small quant runs & prompt seeds | Section: Introduction / Top-line findings so far (quick) / Loose todo (next 48h)  **(expected document)**
2. Document: Precision parity sensitivity spreadsheet notes | Section: Introduction
3. Document: Burst efficiency and cold-start penalty vs batching — one-pager (Apr 2026) | Section: Experiment setup (short)
4. Document: Mixed-Precision Samplebank Recommendation Cookbook | Section: Introduction

*81 s, cited [1], gate score 0.826, gold-word overlap 29%*

---

### qst_0199 (semantic)

**Question:** After a recent refactor to request grouping and the per request memoization layer, what is the specific risk if the cache key canonicalization now treats a trailing slash differently between callers, especially in a multi customer environment?

**Gold answer:** If cache key canonicalization strips vs. preserves a trailing slash inconsistently, two different callers (or even different tenants) can end up mapping distinct requests to the same KV-cache entry. In a multi-customer environment this can cause cross-tenant cache collisions/cache poisoning, leading to incorrect or leaked responses and silent correctness issues.

**Model answer:** If the cache key canonicalization now treats a trailing slash differently between callers, it could lead to cache poisoning or silent correctness issues in a multi-customer environment. This is because different handling of trailing slashes can result in different cache keys for the same logical request, preventing cache hits and potentially serving incorrect data [1]. Additionally, this could cause cache fragmentation and reduce prefix cache hit rates, especially when customers have slightly varying token boundaries [2]. The risk is exacerbated in a multi-tenant setup where isolation and consistent key handling are critical [3].

**Sources given:**
1. Document: Refactor thoughtstream kiran | Section: Introduction  **(expected document)**
2. Document: Tokenizer pool orchestration and prefix-aware KV cache keying (WIP) | Section: Purpose / Background & motivation / Goals
3. Document: Time windowed batching and progressive padding spec | Section: KV cache implications and rules
4. Document: Edge cache reconciliation after weighted shift — retro & runbook draft | Section: Technical analysis (deeper)

*84 s, cited [1, 2, 3], gate score 0.807, gold-word overlap 43%*

---

### qst_0200 (semantic)

**Question:** For the hospital system that wants to run an interactive intake chatbot and auto-generate discharge writeups entirely inside its own locked-down data center with no patient data leaving the network, what end-to-end response time target did they set for producing about 200 tokens under peak load?

**Gold answer:** They targeted an end-to-end p95 of ≤ 18 seconds to generate about a 200-token response while handling 12 concurrent sessions (their peak-load concurrency goal).

**Model answer:** The hospital system set an end-to-end response time target of <= 18 seconds for producing about 200 tokens under peak load [1].

**Sources given:**
1. Document: ValeHealth on-prem implementation capture | Section: Introduction  **(expected document)**
2. Document: Telehealth pilot — POC success plan and workshop notes | Section: Success criteria (must be measurable)
3. Document: Empirical capacity experiment notes — multi-tenant GPU mix and autoscale rules | Section: Introduction
4. Document: Everest Diagnostics pilot intake — raw call notes | Section: Model & runtime preferences

*85 s, cited [1], gate score 0.828, gold-word overlap 20%*

---

### qst_0212 (semantic)

**Question:** How should we set up low-noise oncall dashboards and tiered paging for a streaming text generation service so that responders can jump from a latency spike to a trace with hashed prompt references and cache hotness context and resolve issues within about 15 minutes?

**Gold answer:** Use a slice-first observability design: build dashboards and alerts around high-value slices (e.g., enterprise customer_tier, /chat/stream vs /chat/batch, model_variant, and kv_cache_warmth hot/warm/cold) rather than global aggregates, and instrument canonical metrics like first_token_ms (p50/p90/p99), error rate, kv_cache.hit_rate/warmth_index, queue.wait_ms, and model.exec.gpu_ms. On the dashboard, include operational anchors (request rate, latency percentiles, errors), causality suspects (KV hit rate/warmth, queueing, GPU time), and investigation hooks (sample trace list, recent prompt snapshot IDs), so oncall can jump from a spike to a trace quickly.

For tracing, enforce a lightweight span contract (ingress.request → scheduler.queue → model.exec → emitter.stream → exporter.kv_lookup) with required tags including request_id, tenant_id, route, model_variant, kv_hit, batch_id, prompt_sha (hash only), and token_count; keep raw prompts out of traces and link any prompt snapshots as external secure artifacts by prompt_sha. Define KV warmth context via heuristics (warm if warmth_index ≥ 70 and hit_rate ≥ 0.8 over 5m; cold if warmth_index < 50 or hit_rate < 0.6) so responders can correlate cache state with TTF and GPU time.

For low-noise tiered paging, implement graded per-slice alerts instead of a single global threshold: P2 warning when 10m rolling first_token_ms p95 exceeds baseline×1.5 for 15m; P1 degradation when p95 exceeds baseline×2 for 10m or error_rate rises 5× for 5m; and P0 incident on SLA breach (e.g., enterprise p99 > SLA) or sustained 50% request loss. Add noise controls such as requiring at least 3 tenants impacted (or sustained absolute request growth) and enrich alerts with top tenants/routes, the last prompt_shas, and a link to a prebuilt investigation query to support alert → hypothesis → remediation in ~15 minutes.

**Model answer:** To set up low-noise oncall dashboards and tiered paging for a streaming text generation service, focus on slice-first dashboards with high-value slices like customer_tier=enterprise, route=/chat/stream, and kv_cache_warmth={hot,warm,cold} [1]. Include metrics such as inference.request.count and 95th latency for quick visibility [2]. Ensure trace anchoring with a sampled trace linked to the alert's request-id/session-id, and include hashed prompt references in trace indexes for faster repro [4]. Tiered paging should involve #sre-oncall and pager duty SRE primary for customer-impacting issues, with minimal user-facing changes during containment [2].

**Sources given:**
1. Document: Observability slice storyboard and alert finessing notes | Section: Introduction  **(expected document)**
2. Document: Fast-lane API triage — pocket guide (timeouts, 429s, streaming, error spikes) | Section: Introduction / Channels & tools
3. Document: Oncall Succession: dashboard prototype & metric sunset storyboard | Section: Introduction
4. Document: Investigator pocket map: SLI ↔ Trace translation | Section: Open questions / follow-ups (actions) / Notes to self / shorthand / References & shortcuts

*111 s, cited [1, 2, 4], gate score 0.752, gold-word overlap 16%*

---

### qst_0225 (semantic)

**Question:** Before an external audit rehearsal happening in about three weeks, what are the due dates and owners for the main evidence gaps around deployment rollback proof, contractor access end date confirmation, encryption key rotation documentation placement, and two overdue third party security questionnaires?

**Gold answer:** * Deployment rollback proof (missing rollback evidence for two infra rollouts): Owner Devon (Release Eng); due 2026-02-28.
* Contractor access end date confirmation (SSO audit log contractors flagged; needs People Ops/HR attestation): Owner Maya (Identity); due 2026-02-24.
* Encryption key rotation documentation placement (KMS rotation procedure needs to be moved to the expected Confluence location and logs attached): Owners Paulina + Infra; due 2026-02-21.
* Two overdue third-party security questionnaires (observability + external model hosting): Owner Alex (to escalate to Procurement); due 2026-03-05.

**Model answer:** - Deployment rollback proof: Due 2026-02-28, Owner: Devon [1][2].
- Contractor access end date confirmation: Due 2026-02-24, Owner: Maya [1][2].
- Encryption key rotation documentation placement: Due 2026-02-21, Owner: Paulina [1][2].
- Two overdue third-party security questionnaires: Due 2026-03-05, Owner: Alex [1].

**Sources given:**
1. Document: SOC2 ↔ ISO control translation — 1:1 dry-run scratchpad | Section: Quick gap snapshot (top items to speak to)  **(expected document)**
2. Document: SOC2 ↔ ISO control translation — 1:1 dry-run scratchpad | Section: Potential small talk / placemats (notes to self) / Follow-up action items (concrete, assignable)  **(expected document)**
3. Document: Northreach security onboarding & evidence log | Section: Introduction
4. Document: Sales + Solutions Engineering Training Notes — Enterprise Security Enablement Kit Rollout (2026) | Section: Service-level expectations (set customer expectations) / Internal checklist before sending security materials

*108 s, cited [1, 2], gate score 0.889, gold-word overlap 41%*

---

### qst_0233 (semantic)

**Question:** What is the target success criteria for the internal two week cross team rehearsal that practices incident response for model endpoint reliability, especially the time limit from alert to starting the incident call?

**Gold answer:** The bootcamp's success criteria include keeping alert-to-bridge (incident call/bridge) times to 5 minutes or less for synthetic tests. Other targets are at least one successful automated fallback during the live mini-sim with under 15% customer-impact traffic diverted, and 80% of participants able to list the SLO signal chain afterward.

**Model answer:** The target success criteria for the two-week cross-team rehearsal include completing 3 tabletop-to-live escalation handoffs within 2 weeks [1]. The specific time limit from alert to starting the incident call is not explicitly mentioned in the sources.

**Sources given:**
1. Document: SLO Cadence Bootcamp & Cross-functional Rehearsal Notebook | Section: Purpose / … / High-level bootcamp plan (2 weeks)  **(expected document)**
2. Document: Ops ownership cascade and SLO adoption sprint plan | Section: Introduction
3. Document: Resilience Rendezvous — Ops Sprint Notes & Cross-Team Cohesion Experiments | Section: Introduction
4. Document: Ops ownership cascade and SLO adoption sprint plan | Section: Introduction

*101 s, cited [1], gate score 0.776, gold-word overlap 14%*

---

### qst_0238 (semantic)

**Question:** How should I structure a small prompt experiment to reduce overconfident mistakes by mixing a couple of correct examples with one intentionally wrong example plus an immediate fix, while keeping the total examples very short and tracking things like made-up details and format compliance over a few hundred test prompts?

**Gold answer:** Structure the few-shot prompt with a maximum of 4 examples: 2 normal "good" exemplars, then 1 contrapositive exemplar (instruction → plausible but clearly wrong output) with a terse 6-12 token critique (e.g., "Incorrect because...") and an immediate corrected output right after it to anchor the right behavior. Run a small matrix over a few hundred probes (e.g., ~200 per condition): baseline 0-shot, standard 2-good few-shot, contrapositive (2 good + bad + correction, vary ordering), and an optional smoothing variant that adds a short preface like "Do not repeat the mistake in the examples below," plus a negative-control with the bad example but no correction.

Track metrics such as overclaim rate (made-up details), semantic accuracy (human-labeled), style/length or format compliance, calibration/confidence if available, and token-cost delta; tag runs with an experiment key and log results in your metrics backend.

**Model answer:** To structure a small prompt experiment for reducing overconfident mistakes, include a mix of 1–2 correct examples, 1 intentionally wrong example, and an immediate fix. Keep each exemplar short (3–5 tokens) to maintain brevity [2]. Track made-up details and format compliance by using failure probes and tagging outputs with short tags like "hallucination" or "format-escape" [1][4]. Ensure the experiment is reproducible with notes on prompt length and token budgets [2].

**Sources given:**
1. Document: Template Contrapositives Workbench | Section: Goal / Background / motivation / Quick glossary (informal)  **(expected document)**
2. Document: Leftover Prompt Curio Cabinet — hunches & micro-experiments | Section: Introduction
3. Document: Prompt UX experiments notebook | Section: Purpose / quick context / Why this exists / Hypotheses I'm testing (high level)
4. Document: Prompt assembly: recipes & staged sandbox | Section: Introduction

*85 s, cited [1, 2, 4], gate score 0.592, gold-word overlap 22%*

---

### qst_0280 (semantic)

**Question:** In the rollout plan for the internal service that only hands out application secrets to verified runtime hosts using short lived machine health proofs and hardware backed key unwrapping, what is the default hot and cold retention period for the tamper resistant audit trail?

**Gold answer:** The tamper-evident audit trail defaults to 90 days of hot retention and 1 year of cold retention.

**Model answer:** The default hot retention period for the tamper-resistant audit trail is 90 days, and the cold retention period is 1 year [1][2].

**Sources given:**
1. Document: Attestation-aware Secrets Gateway roadmap and terraform notes | Section: Secrets lifecycle acceptance tests (smoke checklist) / Audit & logging requirements  **(expected document)**
2. Document: SIEM export, backfill & failure runbook for audit/evidence logs | Section: Introduction
3. Document: RBAC v2: routing & retention for audit events — implementation notes | Section: Introduction
4. Document: Audit log transparency & customer commitments — draft language | Section: Q: "How long are logs kept?" / … / Sales enablement snippets (quick soundbites)

*85 s, cited [1, 2], gate score 0.938, gold-word overlap 70%*

---

### qst_0283 (semantic)

**Question:** In our long conversation serving experiments, what mitigation is suggested for the tendency to start making up references right after a retrieval step when older context has been aggressively shrunk to save memory?

**Gold answer:** The notes suggest mitigating this by using calibrated (confidence-aware) retrieval scoring/masking and adding hallucination detectors (e.g., watching for sudden entropy drops), plus doing a short-term KV cache reset immediately after retrieval events to reduce compression-triggered citation hallucinations.

**Model answer:** A practical mitigation suggested is calibrated retrieval scoring (confidence-aware masking), hallucination detectors that watch for sudden entropy drops, and short-term cache reset after retrieval events [1].

**Sources given:**
1. Document: Longform reading scrapbook: compression, KV heuristics, and RAG probes | Section: Introduction  **(expected document)**
2. Document: Long-context recall + latency regression notes | Section: Introduction
3. Document: Paper curation memo — Context stitching, soft prefixes, and long-run inference heuristics | Section: Introduction
4. Document: Retrieval stress casebook 8k 32k 128k | Section: Purpose and scope / Audience / High-level summary (TL;DR)

*76 s, cited [1], gate score 0.536, gold-word overlap 52%*

---

### qst_0291 (semantic)

**Question:** For the shipping customer rollout checklist, what is the requirement for output stability across repeated cold and warm starts before approving deployment?

**Gold answer:** Before deployment approval, outputs from the pinned prompts must be stable across 3 cold-starts and 5 warm-starts with string-level equivalence for structured fields, except for any explicitly stochastic fields documented in the prompts.

**Model answer:** The requirement for output stability across repeated cold and warm starts before approving deployment is to ensure that the model variant swap (A->A-q4 + fallback path) is tested with a warmup + spike to confirm that the quantized variant does not amplify latency due to smaller batch nuclei [1]. Additionally, the routing rule change (heuristic by latency/cost) must be verified with a cold start sweep to ensure fallback routing is honored under node churn [1].

**Sources given:**
1. Document: Stability Sandbox Protocols for Progressive Rollouts (WIP) | Section: SIMULATION MATRIX (what to run vs why) / CHECKLIST (run owner before sandbox run)
2. Document: Release gatekeeper templates & activation scripts (working) | Section: Observability checklist (what to glance at during stabilization) / … / Appendix: quick variable list for templates
3. Document: Hosting parity checklist and risk mitigation | Section: Introduction
4. Document: Feature Owner Stability Handbook and Rapid Escalation Templates | Section: Purpose and scope / … / Minimum SLO template (for feature owners)

*80 s, cited [1], gate score 0.211, gold-word overlap 19%*

---

### qst_0297 (semantic)

**Question:** For the tiny production experiment that tweaks how the model serving layer keeps and evicts attention memory, what are the concrete pass or fail thresholds for error rate and tail latency during the first hour?

**Gold answer:** During the first 60 minutes, the canary fails if the hosted-api 5xx rate spikes by more than 0.1% relative to baseline, or if p99 (tail) latency increases by more than +10 ms versus the baseline/pinned cohort.

**Model answer:** During the first hour, the error rate threshold is <0.2% absolute increase over baseline for 30 minutes [1]. For tail latency, the p95 increase must be <10% over baseline, and p99 <20% for a persistent 30-minute window [1].

**Sources given:**
1. Document: Stability Sentinel playlist and telemetry traffic sim plan | Section: Synthetic traffic scenarios (priority order)
2. Document: Admit Snapshot and Requirements Checker | Section: Quick quantitative checklist (pass / fail / n/a)
3. Document: Telemetry hourglass lane and deployment brief (June 2027) - doodle | Section: Hourglass telemetry cadence (what to sample when) / Key signals and thresholds (quick reference)
4. Document: Woven rollout patterns for LLM routing - notes | Section: Signal thresholds (example values — tune per product) / Observability playbook (what to look at) / Experiment design notes (A/B hybrids)

*89 s, cited [1], gate score 0.569, gold-word overlap 40%*

---

### qst_0300 (semantic)

**Question:** In the internal routing performance memo that compared a nearby low latency serving path versus a centralized high throughput batching path and a split strategy that starts local then hands off when the response gets longer, which approach had the cheapest cost per 1k tokens for medium length requests and what was that cost?

**Gold answer:** For the mid-thread (medium-length) workload, the centralized batching approach (core-tiling-multiplex) had the lowest cost at $0.062 per 1k tokens.

**Model answer:** The hybrid-evict approach had the cheapest cost per 1k tokens for medium length requests, with a cost of $10.50 per 1M tokens [2].

**Sources given:**
1. Document: Micro-econ benchmarks and ask framework | Section: body
2. Document: Dispatch surface playback: edge vs core econ memo | Section: TL;DR / Why we ran this (context)  **(expected document)**
3. Document: Heuristic pricing matrix for smart routing (worksheet) | Section: Assumptions (for the numbers below)
4. Document: Hosted API cost decision signal notebook | Section: Quick signals & thresholds (candidate) / Operational action matrix (map combined signals -> action)

*91 s, cited [2], gate score 0.932, gold-word overlap 25%*

---

### qst_0391 (constrained)

**Question:** In the hosted API incident in late April 2026 where streaming requests started returning 502/504 and non-streaming requests also saw a sharp tail-latency increase, what was the underlying trigger (involving an edge keepalive/connection-TTL change) and what immediate mitigations were used to restore service?

**Gold answer:** It was triggered by an edge configuration change that cut upstream connection keepalive/TTL from 90s to 10s, increasing connection churn and exposing a streaming-proxy TCP write-stall bug that caused 502/504 on streaming and sharp tail-latency for non-streaming. Service was restored by rolling restarting the streaming-proxy fleet to clear stuck buffers, rolling back the edge TTL/keepalive setting to 90s, and applying temporary traffic shaping (soft concurrency limits and rejecting new sessions on overloaded proxies).

**Model answer:** The underlying trigger was an unintended change to a per-connection TTL/keepalive config combined with an edge buffer write-stall bug in the streaming proxy, causing head-of-line stalls and backlog amplification under normal traffic spikes [1]. The immediate mitigations included rollback and emergency config override to restore baseline behavior [2].

**Sources given:**
1. Document: Streaming write-stall + TTL regression — hosted API outage postmortem (2026-04-25) | Section: Introduction  **(expected document)**
2. Document: P0 hosted API ratecap rollout regression investigation | Section: summary / impact
3. Document: Streaming latency ripple postmortem | Section: Introduction
4. Document: P0 hosted API multiplex controller hedging failchain analysis | Section: summary

*77 s, cited [1, 2], gate score 0.996, gold-word overlap 17%*

---

### qst_0452 (miscellaneous)

**Question:** Who owns the messy go-to-market misc assets dump with placeholder marketing files and micro-copy ideas created during a last-minute scramble before a partner call?

**Gold answer:** Priya Nair (go-to-market) owns the messy GTM misc assets dump.

**Model answer:** The owner of the messy go-to-market misc assets dump with placeholder marketing files and micro-copy ideas created during a last-minute scramble before a partner call is Priya Nair [1]. She is noted as the go-to-market owner of this dump [1].

**Sources given:**
1. Document: Gtm misc assets batch 2026 | Section: Random brainstorm bits (unstructured) / Change log (very small) / Contact / owners for follow-up  **(expected document)**
2. Document: Gtm misc assets batch 2026 | Section: GTM Misc Assets — placeholder batch / Purpose / Notes to self / context / File stubs (upload names + quick usage notes)  **(expected document)**
3. Document: Brand Meme & Misc Asset Inventory | Section: Introduction / Sections
4. Document: Brand Meme & Misc Asset Inventory | Section: Usage notes / … / Audit notes

*73 s, cited [1], gate score 0.930, gold-word overlap 67%*

---

### qst_0453 (miscellaneous)

**Question:** Who is responsible for the stock canyon hero placeholder image that is suggested for demo slides, and what is its current status?

**Gold answer:** Priya Desai is responsible for the hero-placeholder-canyon.jpg stock canyon hero image, and its current status is "needs crop."

**Model answer:** The stock canyon hero placeholder image is owned by Priya Desai, and its current status is "needs crop" [1].

**Sources given:**
1. Document: Brand Meme & Misc Asset Inventory | Section: Introduction / Sections  **(expected document)**
2. Document: Brand Meme & Misc Asset Inventory | Section: Usage notes / … / Audit notes  **(expected document)**
3. Document: Gtm misc assets batch 2026 | Section: Rough micro-copy candidates (short, punchy) / … / Open questions / TODOs
4. Document: Gtm misc assets batch 2026 | Section: GTM Misc Assets — placeholder batch / Purpose / Notes to self / context / File stubs (upload names + quick usage notes)

*71 s, cited [1], gate score 0.955, gold-word overlap 75%*

---

### qst_0461 (miscellaneous)

**Question:** What is the proposed weekly cleanup schedule and routine for tidying the engineering kitchen fridge so old opened items get discarded?

**Gold answer:** The proposed routine is to label all opened jars with the date, and if something has been open for more than 14 days, check its smell/appearance and discard it if needed. A quick weekly tidy is scheduled for Fridays at 4pm to wipe counters, check the fridge, and toss obvious trash.

**Model answer:** The proposed weekly cleanup schedule is a quick tidy on Fridays at 4pm, which involves wiping counters, checking the fridge, and tossing obvious trash [1]. Old opened items are to be discarded if they are more than 14 days old, based on the date labeled on the jar [1].

**Sources given:**
1. Document: Taco tuesday fridge inventory wip | Section: Taco team volunteers (informal) / … / Random messy brainstorms (feel free to ignore)  **(expected document)**
2. Document: Taco tuesday fridge inventory wip | Section: Taco Tuesday & Fridge Inventory - WIP / Quick context / Current inventory (very approximate) / Fridge weirdness / notes to self  **(expected document)**
3. Document: Taco tuesday fridge inventory wip | Section: Links / references / Next steps (short)  **(expected document)**
4. Document: Ephemeral storage pressure workflow and debug playbook | Section: Introduction

*81 s, cited [1], gate score 0.750, gold-word overlap 45%*
