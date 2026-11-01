# Answer generation: qwen3:8b, prompt v2, unanswerable set

39 questions. Sources: top 4 chunks after hybrid search + reranking of the top 10. Temperature 0. Run 2026-11-01 02:17.

| Check | Result |
|---|---|
| **Correctly abstained** (expected document removed) | 28% |
| Answered anyway, from other documents | 72% |
| Expected document among the sources (retrieval) | 0% |
| Answered (did not abstain) | 72% |
| Cites the expected document, when it was among the sources | n/a |
| Abstained although the expected document was among the sources | n/a |
| Answers with invalid citation numbers | 0 |
| Gold-answer word overlap (rough proxy, mean) | 21% |
| Seconds per answer (median) | 103 |
| Prompt / answer tokens per second (median) | 18 / 3.2 |

The automatic checks are rough. Read the answers below: that is the real evaluation.

---

### qst_0006 (basic)

**Question:** In the draft spec about extending a routing policy engine for automated regional failover, what is the proposed priority order for evaluating different failure signals when deciding whether to shift traffic or fail over?

**Gold answer:** The draft proposes this canonical v1 signal priority order: (1) authoritative Reachability DOWN → FAILOVER (unless no healthy fallback), (2) fast/severe 5xx error burn → FAILOVER or PARTIAL_SHIFT depending on blast radius and capacity, (3) tail latency burn → PARTIAL_SHIFT first, escalating to FAILOVER if corroborated and sustained, (4) capacity exhaustion/hard gate → HOLD plus load shed (avoid shifting into constrained regions), and (5) control plane degradation → HOLD to avoid rapid flips/oscillation.

**Model answer:** The proposed priority order for evaluating failure signals is: reachability (authoritative) > 5xx burn > tail latency burn > capacity exhaustion [3].

**Sources given:**
1. Document: Latency-Cost Hybrid Routing Playbook | Section: Introduction
2. Document: Geo failover on-call playbook (draft) | Section: summary / content / Detection signals (combine; avoid flapping)
3. Document: Regional Failover Automation Upgrade — Kickoff Notes (Working Doc) | Section: Proposed high-level design (discussion summary)
4. Document: Regional Failover Automation Upgrade — Kickoff Notes (Working Doc) | Section: Action items (with owners) / Milestones (strawman)

*105 s, cited [3], gate score 0.541, gold-word overlap 22%*

---

### qst_0007 (basic)

**Question:** In a rolling investigation of a model regression on policy-related prompts after a recent deploy, what was the average triage rubric score change between the older baseline build and the newer optimized build in the first comparison run?

**Gold answer:** In the first comparison run, the baseline build averaged 2.7 while the newer optimized build averaged 1.9, a decrease of 0.8 rubric points.

**Model answer:** The average triage rubric score change between the older baseline build and the newer optimized build in the first comparison run was not explicitly stated in the sources [1][2][3][4]. I could not find this in the available documents.

**Sources given:**
1. Document: Model onboard testbed scripts and scoring notes | Section: Introduction
2. Document: Prep: eval deep-dive for optimize AB regression | Section: Introduction / Context / TL;DR
3. Document: Impromptu rubric stitchpad - Jorge Gomez | Section: Regression observations (pattern notes) / Mitigations I've used recently
4. Document: Model adoption snapshot + promptset hotlist (voice & search) | Section: Triage rubric used this cycle / (Score thresholds: >=8 urgent, 5–7 medium, <=4 low) / Diagnostics run so far

*98 s, cited [1, 2, 3, 4], gate score 0.829, gold-word overlap 53%*

---

### qst_0008 (basic)

**Question:** In the internal shiproom runner notes, what is the target time-to-recover threshold for a verified rollback in staging?

**Gold answer:** The rollback plan is considered verified in staging if the time-to-recover is under 10 minutes.

**Model answer:** I could not find this in the available documents.

**Sources given:**
1. Document: Game Day Plan: Auto-rollback on SLO breach (rollout controller integration) | Section: Target timing budgets (staging) / … / Fault injection approach (pick one)
2. Document: Onboarding acceptance playbook for experimental models | Section: Introduction
3. Document: Holdback & Fallback Runway Catalog — Preflight KPIs & Readiness | Section: readiness_checklist
4. Document: Holdback & Fallback Runway Catalog — Preflight KPIs & Readiness | Section: rollout_timeline_summary / operational_play_notes

*67 s, cited nothing, gate score 0.448, gold-word overlap 0%*

---

### qst_0039 (basic)

**Question:** In the 3-hour customer workshop plan for taking a team from initial evaluation to a proof of concept, what are the three types of go/no-go acceptance gates?

**Gold answer:** The three go/no-go acceptance gates are: a Quality gate (meets baseline precision/recall or user satisfaction on a representative dataset), a Performance gate (meets latency SLOs at target load with acceptable cost), and a Compliance gate (data handling and encryption meet stated requirements).

**Model answer:** The three types of go/no-go acceptance gates are Feature Gate, Performance Gate, and Compliance Gate [3]. These gates are part of the decision matrix used to determine if a feature meets the criteria for progression [3]. Each gate has specific exit criteria and owners [3].

**Sources given:**
1. Document: Market Debut Sprint Scoreboard and Acceptance Gates | Section: OVERVIEW
2. Document: Deployment Gate Triage: KPI Timeline & Ops Workbench | Section: Purpose / Context and guidance (notes to reviewers) / Primary contacts
3. Document: Market Debut Sprint Scoreboard and Acceptance Gates | Section: ACCEPTANCE GATES (Decision matrix) / PRE-LAUNCH CHECKLIST (top-risk items)
4. Document: Launch Gates & Metrics Inventory | Section: Introduction

*80 s, cited [3], gate score 0.690, gold-word overlap 29%*

---

### qst_0047 (basic)

**Question:** In some lab notes about reducing few-shot example copying, what tradeoff was noted when rotating the order of exemplars in prompts?

**Gold answer:** The notes say rotating exemplars can reduce position bias, but it interacts badly with prefix caching-rotating defeats the cached prefix and may require cache bypass/invalidations, making it less suitable for high-QPS routes.

**Model answer:** Rotating the order of exemplars in prompts was noted to introduce a tradeoff between reducing verbatim copying and increasing partial hallucinations, where the model invents fields when exemplar clusters contain examples with omitted fields [1].

**Sources given:**
1. Document: Prompt Cyclotron Experiments & Notes | Section: Observed failure cases (notes from quick runs) / Anchor design heuristics (initial)
2. Document: Prompt Cyclotron Experiments & Notes | Section: Introduction / Context and motivation
3. Document: Exemplar Pruning — Gambit Lab Notes | Section: Purpose / Notes on motivation
4. Document: Spark Template Concoction — scratchpad | Section: Example few-shot composition (for product copy rewriting) / … / Observed behavior (run 2024-11-20)

*78 s, cited [1], gate score 0.895, gold-word overlap 8%*

---

### qst_0050 (basic)

**Question:** What is the proposed HTTP header scheme for attributing API traffic to quickstart templates, including how the header value is formatted and the opt-in header?

**Gold answer:** The proposal is to tag template-originated API traffic with an optional header `X-Redwood-Template`, whose value is formatted as `<template_name>@<template_version>;<language>` (e.g., `rag-agent@1.1.0;python`). An additional opt-in header `X-Redwood-Template-Opt-In` is set to `true` or `false`.

**Model answer:** The proposed HTTP header scheme for attributing API traffic to quickstart templates requires telemetry header/tagging to be opt-in, disabled by default, and explicitly enabled via the environment variable `REDWOOD_TEMPLATE_TELEMETRY_OPT_IN=true` [1]. The header value should contain only a static template identifier and version, without any customer, organization, or user identifiers [1].

**Sources given:**
1. Document: Template Security Review Notes (Quickstart Templates v1) | Section: Findings and actions / P0 (must fix before public launch)
2. Document: SDK adopter playlist and anti-friction checklist | Section: Experiment ideas (A/B candidates) / Sample troubleshooting (top 6 with fixes) / Open questions / TODOs
3. Document: Template Security Review Notes (Quickstart Templates v1) | Section: Findings and actions / P0 (must fix before public launch)
4. Document: Template Security Review Notes (Quickstart Templates v1) | Section: Logging & redaction requirements (what “good” looks like) / OTel conventions (security-focused constraints)

*112 s, cited [1], gate score 0.531, gold-word overlap 25%*

---

### qst_0054 (basic)

**Question:** What was the decision for when and how to roll out the new lattice scheduler into a limited canary, and what condition would allow expanding it to higher traffic models?

**Gold answer:** They decided to move the lattice scheduler into a restricted canary for low-traffic models during a Mon-Wed window next week. If p95 latency improves and there are no errors, they would expand it to medium-tier (higher traffic) models.

**Model answer:** The decision was to start the canary rollout with 1% traffic and incrementally increase to 5%, 20%, and 100% over 5 days, with a hard rollback criteria of p95 latency increase >5% or error increase >0.5% above baseline [4]. The condition to expand to higher traffic models is meeting the rollback criteria without exceeding the thresholds [4].

**Sources given:**
1. Document: Cross-domain lead strategy sync - May 18 2027 | Section: Notes / Highlights
2. Document: Launch orchestra staffing heuristics and clockwork checklist — Apr 2028 (draft) | Section: Introduction
3. Document: Canary backfill decision briefing | Section: Background & what we know / Observed impact metrics (summary)
4. Document: Engineering mosaic weekly snapshot — Apr 04 2027 | Section: content

*103 s, cited [4], gate score 0.268, gold-word overlap 29%*

---

### qst_0057 (basic)

**Question:** In our staging cluster, checkpoint downloads sometimes hang when resuming with an HTTP Range request to a cloud storage signed URL; what unexpected HTTP status code is sometimes returned instead of partial content that triggers the stall?

**Gold answer:** In the failing resume cases, the server sometimes responds with **HTTP 200 OK** (instead of the expected **206 Partial Content**) to a Range request, which triggers the stall.

**Model answer:** I could not find this in the available documents.

**Sources given:**
1. Document: SSE output drain / limbo investigation notes | Section: Summary / Symptoms (observed) / Environment / build
2. Document: checkpoint handoff investigation (intermittent checksum failures) | Section: Introduction
3. Document: Weight fetch heuristics — scratchpad (model-loading breadcrumbs) | Section: Introduction
4. Document: JSON Corruption Bisect Notebook — intermittent toolcall parse fail | Section: content / … / Quick repro attempts (staging)

*94 s, cited nothing, gate score 0.248, gold-word overlap 0%*

---

### qst_0062 (basic)

**Question:** What is the proposed backend API endpoint and query parameters for fetching a trace in either grouped or full detail for the console timeline view?

**Gold answer:** The playbook proposes a backend trace fetch API of `GET /v1/traces/{id}?level=grouped|full&time_window=start,end`, where `level` selects grouped vs full detail and `time_window` optionally constrains the returned data to a start/end range.

**Model answer:** The proposed backend API endpoint for fetching a trace in either grouped or full detail is not explicitly stated in the provided sources. However, the document mentions the need for endpoints to support streaming of token detail and lightweight summary for list views [1]. Additionally, there is a mention of endpoints for folded-group expansion that return original spans without re-fetching full traces [2]. These endpoints likely support query parameters for trace detail level, but the exact parameters are not specified in the sources.

**Sources given:**
1. Document: Per-invocation econ UX journey and wires | Section: Introduction
2. Document: Compact trace mode + annotation search — grooming notes | Section: Introduction
3. Document: Error debugging inspector mockups | Section: Open questions / tradeoffs / … / Notes to self / rough TODOs
4. Document: Strawman: Request Threads and Actionable Sprint Lanes | Section: B) Operational Controls & Fallbacks (owner: Arjun Patel) / C) Observability & Diagnostics (owner: Sophie Nguyen)

*111 s, cited [1, 2], gate score 0.889, gold-word overlap 38%*

---

### qst_0069 (basic)

**Question:** In an ops day log about GPU rebalancing and brief west region network instability, what was the target slot capacity for the small hosted pool in the slot metrics dashboard?

**Gold answer:** The slot-metrics dashboard target pool size for the small hosted pool (hosted-small) was 4,200 slots.

**Model answer:** The target slot capacity for the small hosted pool in the slot metrics dashboard was not explicitly mentioned in the provided sources. However, the document mentions that during the APAC night window (00:00-06:00 local), +2 slots were allocated to the cluster-gamma-2 infer-small pool [1]. This allocation was part of short-term capacity planning for the next 7 days.

**Sources given:**
1. Document: GPU dashboard snapshot — ops scrapbook (weekly rollup) | Section: Introduction
2. Document: GPU availability snapshot and triage - 2026-03-20 | Section: Agenda
3. Document: Capacity slot rebalancer proposal and oncall runbook draft | Section: Introduction
4. Document: GPU Fleet Ops Standup - capacity & regional status (2026-03-09) | Section: summary / updates

*130 s, cited [1], gate score 0.798, gold-word overlap 50%*

---

### qst_0079 (basic)

**Question:** In a morning account blitz note from May 2026, what was the proposed mitigation to address repeated inference timeouts for a healthcare customer with a mid-June renewal?

**Gold answer:** For Fortis Health (renewal 2026-06-15), the note proposed mitigating the recurring inference timeouts by adding a 10% reserved burst during peak windows and enabling KV-prefix caching on their main inference route.

**Model answer:** The proposed mitigation to address repeated inference timeouts for the healthcare customer with a mid-June renewal was to schedule a 30-minute deep-dive with the infra oncall team to investigate the memory leak issue in long-context sessions [3].

**Sources given:**
1. Document: Runtime vignettes and mitigation ideas may 2026 | Section: Introduction
2. Document: Tia cs daybook qbr and renewal notes 2026 03 20 | Section: Introduction / … / Account: Fable Health (renewal Q3) — priority: medium-high
3. Document: Morning renewal triage and QBR prep - quick scratch | Section: Introduction
4. Document: Account sprint notes: renewal push + support triage (daily) | Section: body / MORNING BLOCK (8:00–11:30) / TODAY PRIORITIES (top of mind)

*113 s, cited [3], gate score 0.746, gold-word overlap 18%*

---

### qst_0085 (basic)

**Question:** What are the three request quality and cost tiers proposed in the lightweight interaction tiering model for user facing features?

**Gold answer:** The model proposes three tiers: micro (cheapest), standard (baseline/default), and deep (quality-first).

**Model answer:** The three request quality and cost tiers proposed in the lightweight interaction tiering model for user-facing features are:

1) Interactive low-latency tier: Target median <70ms, p95 <400ms. Recommended model: q4_7b with inline-prefetch, opportunistic batching, and stateless routing. Cost: ~$18–$22 per 1M tokens [3].

2) Quality-first mid tier: p95 <300ms but comfortable with higher cost. Recommended model: dense-7B with sticky affinity and modest batching. Cost: $22–$30 per 1M tokens [3].

3) Heavy long-session tier: Prioritize sticky affinity and larger reserved capacity (Dedicated) to avoid scheduling jitter. Consider 13b-q4f16 only if multi-turn length and per-response quality require it [3].

**Sources given:**
1. Document: Trace cost allocation and tenant chargeback proposal | Section: High-level proposal (three-tier attribution model)
2. Document: Three-tier KPI balance and fallback matrix | Section: Top-level summary (one line) / Tiers and KPIs (definitions + rationale)
3. Document: CDF-sliced econ bench: interactive tiers | Section: Short conclusions (actionable)
4. Document: Friction GPS + Feature Companion Brief | Section: prioritized_requests

*155 s, cited [3], gate score 0.421, gold-word overlap 36%*

---

### qst_0091 (basic)

**Question:** In the key rotation runbook, what is the recommended default rotation interval for per-tenant key encryption keys used to wrap data keys?

**Gold answer:** The runbook recommends rotating per-tenant Key-Encryption Keys (KEKs) every 6-12 months (with automated DEK rewraps during low-traffic windows).

**Model answer:** The recommended default rotation interval for per-tenant key encryption keys (KEKs) used to wrap data keys is less frequent than DEK rewrap, but specific intervals are not explicitly stated in the sources. However, it is mentioned that KEK rotation is recommended to be less frequent than DEK rewrap [1]. For tenant KEKs (BYOK), the rotation should follow the customer contract, and if the customer requests rotation, it should be coordinated and recorded with consent [3].

**Sources given:**
1. Document: Envelope Key Ownership Patterns and Audit Export Guide | Section: Introduction
2. Document: Enclave proxy key interop roadtest notes | Section: Introduction
3. Document: KMS ops: rotation checklist, SIEM export & evidence flow | Section: Introduction
4. Document: KMS ops: rotation checklist, SIEM export & evidence flow | Section: Introduction

*137 s, cited [1, 3], gate score 0.908, gold-word overlap 25%*

---

### qst_0094 (basic)

**Question:** What is the recommended emergency action to temporarily simplify routing policy rules when the edge route agent is causing high evaluation latency and end to end latency spikes?

**Gold answer:** Enable the emergency-compact policy set to temporarily apply a simplified ruleset, e.g., call the admin API: POST /v1/admin/policies/compact with body {"reason":"latency_immediate"}.

**Model answer:** The recommended emergency action is to apply an emergency override by setting per-edge override file (/etc/edge/overrides/region-hints.json) with pinned region affinities and restart the edge routing agent (systemctl restart edge-router) [1].

**Sources given:**
1. Document: Autonomous routing fallbacks & ops runbook | Section: Misrouting / policy misapplication scenario
2. Document: Cliff's notes on requests and runtime patches | Section: Introduction
3. Document: Tenant guidance for latency spike — concise update & mitigation steps | Section: Introduction
4. Document: Edge node degradation triage and add-capacity procedures (draft) | Section: Introduction

*101 s, cited [1], gate score 0.645, gold-word overlap 6%*

---

### qst_0105 (basic)

**Question:** What are the proposed internal time to mitigate targets by severity for incident response, regardless of customer deployment tier?

**Gold answer:** The proposed internal time-to-mitigate (TTM) targets (same for all tiers) are: Sev0 = 30 minutes, Sev1 = 2 hours, Sev2 = 1 business day, and Sev3 = 5 business days (or the next planned release train).

**Model answer:** The proposed internal time to mitigate targets by severity for incident response are as follows:

- Sev 1: Immediate mitigation in place within 10 minutes of confirmation [1].
- Sev 2: Mitigation in place within 20 minutes of confirmation [2].
- Sev 3: Mitigation in place within the earliest 0-90 minutes of an incident, with no specific time target mentioned [1].

**Sources given:**
1. Document: First Response Communication Architecture: runbook & templates (draft) | Section: Purpose / … / Incident severity -> communication posture
2. Document: Ops incident scribe: runbook + customer update templates | Section: Internal Slack scripts (templates) / Severity-specific guidance (short) / When to escalate to legal/compliance/PR
3. Document: Churn Risk Scorecard and Rapid Response Playbook | Section: Introduction
4. Document: Cross pillar reliability cadence and slo triage template initiative | Section: Deliverables / Proposed SLO triage template (fill at first alert)

*120 s, cited [1, 2], gate score 0.710, gold-word overlap 19%*

---

### qst_0112 (basic)

**Question:** In the proposed small business token pricing tiers, what is the monthly included token allowance for the plan priced at $25 per month?

**Gold answer:** The $25/month plan (Builder) includes 10 million tokens per month.

**Model answer:** I could not find this in the available documents.

**Sources given:**
1. Document: Pricing psychology, metric framing, and discount guidance | Section: Tier structure (recommended draft)
2. Document: Nanobatch unit-econ scratchpad (tokens, batching, quick tiers) | Section: Pricing ramifications / tier ideas (sketch)
3. Document: Practical token economics — sales playbook & positioning | Section: Appendix — Worked example (customer pitch) / End — one-pager summary for reps
4. Document: Unit econ one-pager: quick calc and tier sketches | Section: Edge considerations (things to model next) / Sketch pricing tiers (quick)

*88 s, cited nothing, gate score 0.509, gold-word overlap 0%*

---

### qst_0116 (basic)

**Question:** In the SOC2 readiness notes, what log retention duration is mentioned as a risk for some environments?

**Gold answer:** The notes mention that in some environments logs are only retained for 90 days, which is flagged as a potential risk.

**Model answer:** The SOC2 readiness notes mention that logs are rotated at 7 days for some services, which is considered a risk as auditors may ask for a 90-day baseline for investigative capability [3].

**Sources given:**
1. Document: Shoreline Labs POC infosec evidence & action plan | Section: Introduction
2. Document: Keystore tinkering and SOC2 readiness musing | Section: Last quick sketches (non-linear) / -- end of brain dump --
3. Document: Safeguard scratch lab: SOC2 prep fragments | Section: Introduction / Context / scope assumption (working)
4. Document: Lockdown Scrim — SOC2 field notes (Ashira) | Section: Open questions / unresolved risks

*71 s, cited [3], gate score 0.912, gold-word overlap 45%*

---

### qst_0122 (basic)

**Question:** Which GPU cluster or pool was flagged as having relatively low average usage but high churn, making its free capacity unreliable during a specific morning UTC window?

**Gold answer:** APAC-eu1-pool-A was flagged for low average utilization (about 47%) but high entropy (0.72), meaning its headroom is unreliable due to churn during roughly 09:00-13:00 UTC.

**Model answer:** The pool:ephemeral-ml-b was flagged as having relatively low average usage but high churn, making its free capacity unreliable during a specific morning UTC window [1].

**Sources given:**
1. Document: GPU utilization anomaly investigation - na clusters - march 2026 | Section: Introduction / Summary
2. Document: GPU dashboard snapshot — ops scrapbook (weekly rollup) | Section: Introduction
3. Document: GPU heatband cluster/pool weekly coverage (Jul 14-20 2026) | Section: Anomalies flagged this week / Suggested actions (prioritized)
4. Document: GPU utilization anomaly investigation - na clusters - march 2026 | Section: Per-cluster observations and hypotheses

*107 s, cited [1], gate score 0.846, gold-word overlap 42%*

---

### qst_0133 (basic)

**Question:** What are the pass fail criteria used in the quick pull request smoke checks for the embedding robustness noise and input length evaluation suite?

**Gold answer:** For the quick PR smoke checks, the suite flags failure if any of these exceed the thresholds: median cosine nearest-neighbor distance deviates by more than ±6% from baseline, NDCG@10 on curated-qrels-5lang drops by 3% absolute or more, or cluster purity drops by 5 percentage points or more.

**Model answer:** I could not find this in the available documents.

**Sources given:**
1. Document: Data Platform Proof-of-Value: Kickoff Playbook and Acceptance Criteria | Section: Acceptance tests (concrete pass/fail checks)
2. Document: Launchpad POC: Stakeholder Alignment & SLA Playbook | Section: Acceptance tests (pass/fail criteria and how we measure) / Milestones and timeline (high level)
3. Document: Bootstrap & Upgrade Failure Playbook and Terraform Notes | Section: Upgrade plan (template)
4. Document: First-pass metric gate and prompt sampler | Section: Introduction

*94 s, cited nothing, gate score 0.465, gold-word overlap 0%*

---

### qst_0134 (basic)

**Question:** What was the suspected root cause behind the brief p99 latency spikes on the hosted chat inference route during small burst traffic?

**Gold answer:** The leading suspicion was a KV-cache eviction storm-likely triggered by an eviction-boundary bug where a single long-context request causes aggressive shard invalidation, dropping cache hit-rate and forcing expensive cold-start decoding. This tail-latency spike may be compounded by bursty tiny micro-batches and occasional GPU memory fragmentation stalls on a worker.

**Model answer:** The suspected root cause behind the brief p99 latency spikes on the hosted chat inference route during small burst traffic was aggressive SDK-level retries with jitter and low backoff from the client, which caused high request churn and increased tail latency for other customers [1].

**Sources given:**
1. Document: Oncall throttle tuning experiments and mitigation notes | Section: Introduction
2. Document: Handoff latency snapshot and SLO audit - Jan 10 2028 | Section: Incidents (brief)
3. Document: KV cache eviction -> PCIe read amplification probe | Section: Introduction
4. Document: Runway scratchpad — kernel & perf quick log | Section: Introduction

*111 s, cited [1], gate score 0.993, gold-word overlap 6%*

---

### qst_0141 (basic)

**Question:** What was the target goal for average router queue time for very short token sequences, compared to the baseline of 28 ms, in the weekly sprint anchor about reducing staging inference queuing latency?

**Gold answer:** The goal was to reduce average router queue time for 1-8 token sequences by 10% from the 28 ms baseline, targeting about 25 ms.

**Model answer:** I could not find this in the available documents.

**Sources given:**
1. Document: Weekend sprint notebook — KPI check-in | Section: Sprint anchor (Feb 20–26) / Signals to watch (morning checklist)
2. Document: Ops Anchor: weekly thread & resolution notes — 2027-03-14 | Section: SLO snapshot and interpretation / Operational experiments and tuning notes
3. Document: Field notes: sprint trajectory & KPI tweaks (personal scratchpad) | Section: Purpose / context / … / Signals I'm watching (weekly)
4. Document: Commitment Studio — weekly sprint scrap | Section: Personal micro-OKRs (draft, 2–4 week horizon)

*81 s, cited nothing, gate score 0.913, gold-word overlap 0%*

---

### qst_0155 (basic)

**Question:** What are the lifecycle states and key transitions for the edge adapter service that registers with a control plane and can fall back to hosted inference?

**Gold answer:** The adapter's lifecycle states are INIT (boot/verify dependencies), REGISTERING (attempting control-plane join), ACTIVE (serving local traffic), DRAINING (stop new sessions and finish existing), DEGRADED (resource failure; limited service and/or redirected to hosted), and RETIRED (operator shutdown). Key transitions are INIT → REGISTERING → ACTIVE; ACTIVE → DRAINING (operator/rollout) → RETIRED; any state → DEGRADED on resource failure; and DEGRADED → ACTIVE after recovery.

**Model answer:** The edge adapter service has lifecycle states and key transitions as follows:  
- It registers with the control plane, which manages its state and routing policies [1].  
- It can fall back to hosted inference if the primary inference fleet is unavailable, using fallback tiers defined in the control-plane architecture [3].  
- The adapter must maintain compatibility with the control plane and handle any API changes as breaking changes requiring coordinated rollouts [1].  
- It exposes health and capacity metrics to the control plane for monitoring and steering [1].

**Sources given:**
1. Document: Control Plane Responsibility Atlas | Section: API Gateway specific responsibilities / Orchestration responsibilities (lifecycle & rollouts) / Runtime adapter invariants and contracts
2. Document: Edge resilience VPC onboarding cheat sheet | Section: High-level reference architecture (textual) / Minimal terraform module pattern (opinions)
3. Document: Autonomous routing fallbacks & ops runbook | Section: High-level architecture (short) / Design principles (ops-forward)
4. Document: Security log forwarder design: customer requirements and adapter guide | Section: Introduction

*93 s, cited [1, 3], gate score 0.448, gold-word overlap 26%*

---

### qst_0164 (basic)

**Question:** In the HyperOnboard 30-60-90 onboarding template, what are the escalation conditions that should trigger an email to people ops and the hiring manager?

**Gold answer:** The escalation triggers are: if the new hire is not shipping a measurable artifact by day 30, if access blockers persist for more than 48 hours, or if there are repeated missed meetings.

**Model answer:** The escalation conditions that should trigger an email to People Ops and the hiring manager include: if onboarding blocker prevents dev environment setup beyond day 3, if candidate declines offer after verbal acceptance, and if manager confidence-level is 'low' at day 30 [1]. Additionally, if dev access is not granted by Day 3, an auto-escalation to infra via ONBOARD-412 and notification to the hiring manager occurs [4].

**Sources given:**
1. Document: Hiring Sprint OPERA Playbook — 30/60/90 Impact | Section: escalation_rules / … / next_steps
2. Document: Hiring SLAs & Time-to-Offer Operational Runbook | Section: Quick templates (use verbatim or adapt) / Escalation matrix (fast-path triggers)
3. Document: Post-offer candidate experience: communication cadence and templates | Section: Risk signals and escalation
4. Document: Candidate First 6-Week Success Canvas and Async Checklist | Section: Hiring manager playbook (practical bullets) / Automation rules (People Ops playbook)

*106 s, cited [1, 4], gate score 0.918, gold-word overlap 24%*

---

### qst_0169 (basic)

**Question:** Who is responsible for signing off on latency regression in the weekly customer rollout tracker for Nimbus Health?

**Gold answer:** Maya Patel (Performance Engineer) is responsible for latency regression signoff in the Nimbus Health weekly rollout tracker.

**Model answer:** The responsibility for signing off on latency regression in the weekly customer rollout tracker for Nimbus Health is not explicitly stated in the provided sources [1][2][3][4]. I could not find this in the available documents.

**Sources given:**
1. Document: Integration deployment & handoff check-ins — 2026-05-12 | Section: Customer updates (concise)
2. Document: Account sprint notes: renewal push + support triage (daily) | Section: TEMPLATE: outage / regression notice (short) / STAKEHOLDER MAP (Nimbus) / RISKS / OPEN QUESTIONS
3. Document: Customer Success 1:1 — cheat sheet & follow-ups | Section: Introduction
4. Document: Account sprint notes: renewal push + support triage (daily) | Section: body / MORNING BLOCK (8:00–11:30) / TODAY PRIORITIES (top of mind)

*107 s, cited [1, 2, 3, 4], gate score 0.574, gold-word overlap 46%*

---

### qst_0195 (semantic)

**Question:** From the internal sandbox microbench in the EU West lab around May 2029, what was the estimated dollars per one million tokens for the biggest model on a single 40GB GPU when using the no-batching low-latency mode on the long output workload (about 300 tokens per response)?

**Gold answer:** For the long-generate workload (~300 tokens) using rw-70b-fp16 on a single A100 40GB in fastpath (no batching) mode, the estimated cost was $31.6 per 1M tokens.

**Model answer:** I could not find this in the available documents.

**Sources given:**
1. Document: Microqueue scarcity: dollar vs latency vignette | Section: Test rig / assumptions / Parameter sweep
2. Document: Hosted API — Unit Econ Sensitivity & Batch Opportunities (draft) | Section: body
3. Document: GPU benchmarking field notes — instance sizing & token/watt heuristics | Section: Introduction
4. Document: GPU benchmarking field notes — instance sizing & token/watt heuristics | Section: Introduction

*118 s, cited nothing, gate score 0.773, gold-word overlap 0%*

---

### qst_0196 (semantic)

**Question:** In the quick A100 microbenchmark notes comparing 4-bit weight compression to half precision on a 7B model at single-item batching, what speedup and quality hit were observed for the simplest run?

**Gold answer:** For the simplest A100 batch=1 run, NF4 post-training quantization on the 7B model achieved about a 1.8× token-throughput speedup versus fp16, with an estimated quality hit of roughly +0.6 perplexity on a small set of story prompts.

**Model answer:** In the simplest run of the A100 microbenchmark comparing 4-bit weight compression to half precision on a 7B model at single-item batching, the throughput was 2.9x higher with 4-bit, and the quality penalty was 3.4% [3].

**Sources given:**
1. Document: Precision parity sensitivity spreadsheet notes | Section: Introduction
2. Document: Burst efficiency and cold-start penalty vs batching — one-pager (Apr 2026) | Section: Experiment setup (short)
3. Document: Mixed-Precision Samplebank Recommendation Cookbook | Section: Introduction
4. Document: Quantization cost-quality-latency strata matrix | Section: Recommended heuristics for picking a profile (one-line each) / Example sensitivity snapshot (paste actual bench numbers here)

*103 s, cited [3], gate score 0.705, gold-word overlap 21%*

---

### qst_0199 (semantic)

**Question:** After a recent refactor to request grouping and the per request memoization layer, what is the specific risk if the cache key canonicalization now treats a trailing slash differently between callers, especially in a multi customer environment?

**Gold answer:** If cache key canonicalization strips vs. preserves a trailing slash inconsistently, two different callers (or even different tenants) can end up mapping distinct requests to the same KV-cache entry. In a multi-customer environment this can cause cross-tenant cache collisions/cache poisoning, leading to incorrect or leaked responses and silent correctness issues.

**Model answer:** If the cache key canonicalization treats a trailing slash differently between callers, it could lead to cache key divergence, resulting in different cache entries for semantically equivalent requests. This would reduce cache hit rates and increase per-token cost, especially in a multi-customer environment where requests may vary slightly in token boundaries [1]. Additionally, it could cause inconsistencies in cache population and lead to transient 5xx errors from origin throttles if traffic weights shift without proper cache invalidation [3].

**Sources given:**
1. Document: Tokenizer pool orchestration and prefix-aware KV cache keying (WIP) | Section: Purpose / Background & motivation / Goals
2. Document: Time windowed batching and progressive padding spec | Section: KV cache implications and rules
3. Document: Edge cache reconciliation after weighted shift — retro & runbook draft | Section: Technical analysis (deeper)
4. Document: Smoke sampler: quickplay rubric + regression notes | Section: Introduction

*101 s, cited [1, 3], gate score 0.156, gold-word overlap 31%*

---

### qst_0200 (semantic)

**Question:** For the hospital system that wants to run an interactive intake chatbot and auto-generate discharge writeups entirely inside its own locked-down data center with no patient data leaving the network, what end-to-end response time target did they set for producing about 200 tokens under peak load?

**Gold answer:** They targeted an end-to-end p95 of ≤ 18 seconds to generate about a 200-token response while handling 12 concurrent sessions (their peak-load concurrency goal).

**Model answer:** The hospital system set an end-to-end response time target of 95th percentile <= 750ms for autocomplete tokens under clinical workload [1]. This target applies to scenarios involving the generation of about 200 tokens under peak load.

**Sources given:**
1. Document: Telehealth pilot — POC success plan and workshop notes | Section: Success criteria (must be measurable)
2. Document: Empirical capacity experiment notes — multi-tenant GPU mix and autoscale rules | Section: Introduction
3. Document: Everest Diagnostics pilot intake — raw call notes | Section: Model & runtime preferences
4. Document: MedTech POC hosting synthesis and proposed hybrid topology | Section: Context / Customer constraints and non-functional priorities (summary)

*100 s, cited [1], gate score 0.555, gold-word overlap 13%*

---

### qst_0212 (semantic)

**Question:** How should we set up low-noise oncall dashboards and tiered paging for a streaming text generation service so that responders can jump from a latency spike to a trace with hashed prompt references and cache hotness context and resolve issues within about 15 minutes?

**Gold answer:** Use a slice-first observability design: build dashboards and alerts around high-value slices (e.g., enterprise customer_tier, /chat/stream vs /chat/batch, model_variant, and kv_cache_warmth hot/warm/cold) rather than global aggregates, and instrument canonical metrics like first_token_ms (p50/p90/p99), error rate, kv_cache.hit_rate/warmth_index, queue.wait_ms, and model.exec.gpu_ms. On the dashboard, include operational anchors (request rate, latency percentiles, errors), causality suspects (KV hit rate/warmth, queueing, GPU time), and investigation hooks (sample trace list, recent prompt snapshot IDs), so oncall can jump from a spike to a trace quickly.

For tracing, enforce a lightweight span contract (ingress.request → scheduler.queue → model.exec → emitter.stream → exporter.kv_lookup) with required tags including request_id, tenant_id, route, model_variant, kv_hit, batch_id, prompt_sha (hash only), and token_count; keep raw prompts out of traces and link any prompt snapshots as external secure artifacts by prompt_sha. Define KV warmth context via heuristics (warm if warmth_index ≥ 70 and hit_rate ≥ 0.8 over 5m; cold if warmth_index < 50 or hit_rate < 0.6) so responders can correlate cache state with TTF and GPU time.

For low-noise tiered paging, implement graded per-slice alerts instead of a single global threshold: P2 warning when 10m rolling first_token_ms p95 exceeds baseline×1.5 for 15m; P1 degradation when p95 exceeds baseline×2 for 10m or error_rate rises 5× for 5m; and P0 incident on SLA breach (e.g., enterprise p99 > SLA) or sustained 50% request loss. Add noise controls such as requiring at least 3 tenants impacted (or sustained absolute request growth) and enrich alerts with top tenants/routes, the last prompt_shas, and a link to a prebuilt investigation query to support alert → hypothesis → remediation in ~15 minutes.

**Model answer:** To set up low-noise oncall dashboards and tiered paging for a streaming text generation service, use Grafana dashboards with metrics like 95th latency, 429 rate, and stream errors [1]. Include a trace anchoring feature that links alerts to traces using request-id/session-id, with span breadcrumbs like auth -> routing -> model-invoke -> postprocess [2]. Ensure trace links are noise-resistant and include hashed prompt references for faster repro [3]. Tiered paging should notify #sre-oncall and pager duty SRE first, with #ops-prod paged if customer-impacting [1].

**Sources given:**
1. Document: Fast-lane API triage — pocket guide (timeouts, 429s, streaming, error spikes) | Section: Introduction / Channels & tools
2. Document: Oncall Succession: dashboard prototype & metric sunset storyboard | Section: Introduction
3. Document: Investigator pocket map: SLI ↔ Trace translation | Section: Open questions / follow-ups (actions) / Notes to self / shorthand / References & shortcuts
4. Document: Oncall context strip and visual anchors - notes for dashboard handoff | Section: Introduction

*130 s, cited [1, 2, 3], gate score 0.682, gold-word overlap 11%*

---

### qst_0225 (semantic)

**Question:** Before an external audit rehearsal happening in about three weeks, what are the due dates and owners for the main evidence gaps around deployment rollback proof, contractor access end date confirmation, encryption key rotation documentation placement, and two overdue third party security questionnaires?

**Gold answer:** * Deployment rollback proof (missing rollback evidence for two infra rollouts): Owner Devon (Release Eng); due 2026-02-28.
* Contractor access end date confirmation (SSO audit log contractors flagged; needs People Ops/HR attestation): Owner Maya (Identity); due 2026-02-24.
* Encryption key rotation documentation placement (KMS rotation procedure needs to be moved to the expected Confluence location and logs attached): Owners Paulina + Infra; due 2026-02-21.
* Two overdue third-party security questionnaires (observability + external model hosting): Owner Alex (to escalate to Procurement); due 2026-03-05.

**Model answer:** I could not find this in the available documents.

**Sources given:**
1. Document: Alderbrook POC — Security QA & Evidence Log | Section: Gaps identified & proposed mitigations / Evidence collection timeline (milestones)
2. Document: Northreach security onboarding & evidence log | Section: Introduction
3. Document: Sales + Solutions Engineering Training Notes — Enterprise Security Enablement Kit Rollout (2026) | Section: Service-level expectations (set customer expectations) / Internal checklist before sending security materials
4. Document: Field Signal mini-retrospective and action annotary (customer asks) | Section: Context and intake sources

*87 s, cited nothing, gate score 0.803, gold-word overlap 0%*

---

### qst_0233 (semantic)

**Question:** What is the target success criteria for the internal two week cross team rehearsal that practices incident response for model endpoint reliability, especially the time limit from alert to starting the incident call?

**Gold answer:** The bootcamp's success criteria include keeping alert-to-bridge (incident call/bridge) times to 5 minutes or less for synthetic tests. Other targets are at least one successful automated fallback during the live mini-sim with under 15% customer-impact traffic diverted, and 80% of participants able to list the SLO signal chain afterward.

**Model answer:** The target success criteria for the internal two-week cross-team rehearsal that practices incident response for model endpoint reliability includes a 40% reduction in alert-to-action time for paired teams [2]. The time limit from alert to starting the incident call is not explicitly stated, but the focus is on reducing the time it takes for teams to take action after an alert is triggered.

**Sources given:**
1. Document: Ops ownership cascade and SLO adoption sprint plan | Section: Introduction
2. Document: Resilience Rendezvous — Ops Sprint Notes & Cross-Team Cohesion Experiments | Section: Introduction
3. Document: Ops ownership cascade and SLO adoption sprint plan | Section: Introduction
4. Document: Reliability Onboarding and Collaboration Blueprint - Q3 2026 | Section: Purpose / … / Success metrics (tracked weekly)

*132 s, cited [2], gate score 0.730, gold-word overlap 11%*

---

### qst_0238 (semantic)

**Question:** How should I structure a small prompt experiment to reduce overconfident mistakes by mixing a couple of correct examples with one intentionally wrong example plus an immediate fix, while keeping the total examples very short and tracking things like made-up details and format compliance over a few hundred test prompts?

**Gold answer:** Structure the few-shot prompt with a maximum of 4 examples: 2 normal "good" exemplars, then 1 contrapositive exemplar (instruction → plausible but clearly wrong output) with a terse 6-12 token critique (e.g., "Incorrect because...") and an immediate corrected output right after it to anchor the right behavior. Run a small matrix over a few hundred probes (e.g., ~200 per condition): baseline 0-shot, standard 2-good few-shot, contrapositive (2 good + bad + correction, vary ordering), and an optional smoothing variant that adds a short preface like "Do not repeat the mistake in the examples below," plus a negative-control with the bad example but no correction.

Track metrics such as overclaim rate (made-up details), semantic accuracy (human-labeled), style/length or format compliance, calibration/confidence if available, and token-cost delta; tag runs with an experiment key and log results in your metrics backend.

**Model answer:** To structure a small prompt experiment for reducing overconfident mistakes, include 2–3 correct examples, 1 intentionally wrong example, and an immediate fix, keeping the total examples very short [2]. Track made-up details and format compliance by using a short QA rubric and tagging failure modes like "hallucination" or "format-escape" [3]. Prioritize experiments that mix canonical exemplars with adversarial ones for better precision and diversity [4]. Keep the prompt length under 512 tokens to avoid bugs related to token budget limits [1].

**Sources given:**
1. Document: Leftover Prompt Curio Cabinet — hunches & micro-experiments | Section: Introduction
2. Document: Prompt UX experiments notebook | Section: Purpose / quick context / Why this exists / Hypotheses I'm testing (high level)
3. Document: Prompt assembly: recipes & staged sandbox | Section: Introduction
4. Document: Microexemplar Tinkerbox: vignette seeds & negative probes | Section: Purpose / High-level hypotheses / Experiment matrix (priority order)

*108 s, cited [1, 2, 3, 4], gate score 0.562, gold-word overlap 21%*

---

### qst_0280 (semantic)

**Question:** In the rollout plan for the internal service that only hands out application secrets to verified runtime hosts using short lived machine health proofs and hardware backed key unwrapping, what is the default hot and cold retention period for the tamper resistant audit trail?

**Gold answer:** The tamper-evident audit trail defaults to 90 days of hot retention and 1 year of cold retention.

**Model answer:** The default hot retention period for the tamper-resistant audit trail is 90 days, and the default cold retention period is 2 years [1][3].

**Sources given:**
1. Document: Audit streaming pipeline patterns and retention rationale | Section: Indexing patterns and searchable keys / Retention tiers and TTL rationale (recommended defaults)
2. Document: SIEM export, backfill & failure runbook for audit/evidence logs | Section: Introduction
3. Document: RBAC v2: routing & retention for audit events — implementation notes | Section: Introduction
4. Document: Audit log transparency & customer commitments — draft language | Section: Q: "How long are logs kept?" / … / Sales enablement snippets (quick soundbites)

*103 s, cited [1, 3], gate score 0.723, gold-word overlap 60%*

---

### qst_0283 (semantic)

**Question:** In our long conversation serving experiments, what mitigation is suggested for the tendency to start making up references right after a retrieval step when older context has been aggressively shrunk to save memory?

**Gold answer:** The notes suggest mitigating this by using calibrated (confidence-aware) retrieval scoring/masking and adding hallucination detectors (e.g., watching for sudden entropy drops), plus doing a short-term KV cache reset immediately after retrieval events to reduce compression-triggered citation hallucinations.

**Model answer:** The suggested mitigation is to add a truncated-output guardrail that detects if the supporting doc id is missing from the final output and automatically retries with a narrower retrieval set or alternate routing [1]. This helps prevent the model from making up references when older context has been aggressively shrunk to save memory.

**Sources given:**
1. Document: Long-context recall + latency regression notes | Section: Introduction
2. Document: Paper curation memo — Context stitching, soft prefixes, and long-run inference heuristics | Section: Introduction
3. Document: Retrieval stress casebook 8k 32k 128k | Section: Purpose and scope / Audience / High-level summary (TL;DR)
4. Document: Long-context recall + latency regression notes | Section: Introduction

*92 s, cited [1], gate score 0.335, gold-word overlap 3%*

---

### qst_0300 (semantic)

**Question:** In the internal routing performance memo that compared a nearby low latency serving path versus a centralized high throughput batching path and a split strategy that starts local then hands off when the response gets longer, which approach had the cheapest cost per 1k tokens for medium length requests and what was that cost?

**Gold answer:** For the mid-thread (medium-length) workload, the centralized batching approach (core-tiling-multiplex) had the lowest cost at $0.062 per 1k tokens.

**Model answer:** The internal routing performance memo does not specifically mention a comparison of a nearby low latency serving path, a centralized high throughput batching path, and a split strategy for medium length requests. Therefore, I could not find this in the available documents.

**Sources given:**
1. Document: Micro-econ benchmarks and ask framework | Section: body
2. Document: Heuristic pricing matrix for smart routing (worksheet) | Section: Assumptions (for the numbers below)
3. Document: Hosted API cost decision signal notebook | Section: Quick signals & thresholds (candidate) / Operational action matrix (map combined signals -> action)
4. Document: Timbre: stochastic latency vs cost snapshot (sketch) | Section: Introduction

*122 s, cited nothing, gate score 0.932, gold-word overlap 17%*

---

### qst_0391 (constrained)

**Question:** In the hosted API incident in late April 2026 where streaming requests started returning 502/504 and non-streaming requests also saw a sharp tail-latency increase, what was the underlying trigger (involving an edge keepalive/connection-TTL change) and what immediate mitigations were used to restore service?

**Gold answer:** It was triggered by an edge configuration change that cut upstream connection keepalive/TTL from 90s to 10s, increasing connection churn and exposing a streaming-proxy TCP write-stall bug that caused 502/504 on streaming and sharp tail-latency for non-streaming. Service was restored by rolling restarting the streaming-proxy fleet to clear stuck buffers, rolling back the edge TTL/keepalive setting to 90s, and applying temporary traffic shaping (soft concurrency limits and rejecting new sessions on overloaded proxies).

**Model answer:** The incident in late April 2026 was triggered by a configuration drift in the edge router header normalization logic, which caused a malformed upstream fallback to an improperly configured maintenance pool [4]. The immediate mitigation involved adding a header normalization rule to force 'https' for all inbound requests at the edge, implemented as a hotfix via the control plane [4].

**Sources given:**
1. Document: P0 hosted API ratecap rollout regression investigation | Section: summary / impact
2. Document: Streaming latency ripple postmortem | Section: Introduction
3. Document: P0 hosted API multiplex controller hedging failchain analysis | Section: summary
4. Document: P0 hosted API: header mismatch fallback timeline and runbook draft | Section: Introduction

*112 s, cited [4], gate score 0.971, gold-word overlap 11%*

---

### qst_0452 (miscellaneous)

**Question:** Who owns the messy go-to-market misc assets dump with placeholder marketing files and micro-copy ideas created during a last-minute scramble before a partner call?

**Gold answer:** Priya Nair (go-to-market) owns the messy GTM misc assets dump.

**Model answer:** The owner of the messy go-to-market misc assets dump with placeholder marketing files and micro-copy ideas is Liam O'Connor, as indicated by the entry for "redwood-meme-pack-2025-v1.png" [1].

**Sources given:**
1. Document: Brand Meme & Misc Asset Inventory | Section: Introduction / Sections
2. Document: Brand Meme & Misc Asset Inventory | Section: Usage notes / … / Audit notes
3. Document: Partner marketplace messaging matrix and certification tasks | Section: Purpose and scope / Status note (quick)
4. Document: Brand Meme & Misc Asset Inventory | Section: Links & references / Notes

*76 s, cited [1], gate score 0.475, gold-word overlap 44%*

---

### qst_0453 (miscellaneous)

**Question:** Who is responsible for the stock canyon hero placeholder image that is suggested for demo slides, and what is its current status?

**Gold answer:** Priya Desai is responsible for the hero-placeholder-canyon.jpg stock canyon hero image, and its current status is "needs crop."

**Model answer:** The stock canyon hero placeholder image is not explicitly mentioned in the available documents. However, the document mentions a placeholder filename "hero-inference-abstract-v1.png" for landing page experiments, which is described as having a low-contrast gradient and noisy geometric shapes [2]. The status of this image is that it is a placeholder and not yet finalized, with a note to confirm image licenses before use [1].

**Sources given:**
1. Document: Gtm misc assets batch 2026 | Section: Rough micro-copy candidates (short, punchy) / … / Open questions / TODOs
2. Document: Gtm misc assets batch 2026 | Section: GTM Misc Assets — placeholder batch / Purpose / Notes to self / context / File stubs (upload names + quick usage notes)
3. Document: Marketplace listing value-prop playbook and preflight | Section: Introduction
4. Document: Landing copy — Inference economics experiment kit | Section: Notes for creative team

*91 s, cited [1, 2], gate score 0.043, gold-word overlap 42%*

---

### qst_0461 (miscellaneous)

**Question:** What is the proposed weekly cleanup schedule and routine for tidying the engineering kitchen fridge so old opened items get discarded?

**Gold answer:** The proposed routine is to label all opened jars with the date, and if something has been open for more than 14 days, check its smell/appearance and discard it if needed. A quick weekly tidy is scheduled for Fridays at 4pm to wipe counters, check the fridge, and toss obvious trash.

**Model answer:** I could not find this in the available documents.

**Sources given:**
1. Document: Ephemeral storage pressure workflow and debug playbook | Section: Introduction
2. Document: Dashboard sprint cookbook: metric rename proposals and migration notes | Section: Cleanup and follow-up / Open questions / outstanding decisions / Next steps (this week)
3. Document: Ephemeral storage pressure workflow and debug playbook | Section: Introduction
4. Document: Deployment readiness weekly briefing | Section: Open questions (to tidy up) / Freeform scratch (brain dump)

*84 s, cited nothing, gate score 0.004, gold-word overlap 0%*
