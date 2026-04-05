# Phase 20: Specialized Lane Integration and Workflow Compatibility - Research

**Researched:** 2026-04-05
**Domain:** specialized materials LLM lane integration over the existing operator-governed closed-loop workflow
**Confidence:** MEDIUM

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

### Specialized lane role
- **D-01:** The first real `specialized_materials` lane should be
  evaluation-primary rather than direct-generation-first.
- **D-02:** The specialized lane should prove its value through
  synthesizability, materials plausibility, precursor guidance, anomaly
  detection, or similarly honest evaluation-style behavior.
- **D-03:** Phase 20 should not force the first specialized lane to pretend it
  can already generate strong Zomic directly if the available model does not
  support that honestly.

### Proof target
- **D-04:** Phase 20 should prove the specialized lane on one real system plus
  one thin compatibility fixture or lighter second-system proof.
- **D-05:** The main proof should show the specialized lane doing real workflow
  work on one concrete system instead of spreading effort thinly across two
  full benchmark lanes.
- **D-06:** The second proof path should be enough to show compatibility across
  launch, replay, and compare without turning Phase 20 into the full benchmark
  milestone.

### Serving source
- **D-07:** The specialized lane may use any runnable OpenAI-compatible
  specialized endpoint; local serving is preferred but not mandatory for the
  first operational proof.
- **D-08:** What matters in Phase 20 is that the specialized lane is real and
  executable inside the workflow, not that every specialized checkpoint is
  packaged for purely local operation from day one.
- **D-09:** Phase 20 should not stop at a contract-only specialized lane. A
  real runnable endpoint is required.

### Workflow touchpoint
- **D-10:** The specialized lane should be evaluation-primary and
  generation-compatible.
- **D-11:** The clearest Phase 20 value is to route the specialized lane
  through `llm-evaluate` or equivalent assessment-style outputs while keeping
  `llm-generate`, `llm-launch`, `llm-replay`, and `llm-compare` compatible with
  that lane as the originating lane.
- **D-12:** Generation compatibility still matters, but it is secondary to
  getting one honest specialized-lane workflow role working end to end.

### Compatibility boundary
- **D-13:** Core artifact shapes should remain stable.
- **D-14:** Phase 20 should add richer lineage plus explicit lane-aware
  compare/report fields so operators can tell which outcomes came from a
  specialized lane and what exact serving identity was involved.
- **D-15:** Phase 20 should not create a specialized-only artifact path or a
  parallel workflow family.

### Inherited constraints
- **D-16:** Config remains authoritative for available lanes and their serving
  identities.
- **D-17:** `llm-generate` remains the single generation engine; `llm-launch`
  and `llm-replay` remain wrappers.
- **D-18:** Explicit fallback and replay identity rules from Phase 19 remain in
  force for specialized lanes.
- **D-19:** The workflow stays operator-governed, file-backed, and explicitly
  no-DFT.
- **D-20:** Off-the-shelf specialized materials models are not assumed to
  understand Zomic natively; Phase 20 should choose the highest-value supported
  role rather than forcing direct Zomic symmetry.

### Claude's Discretion
- The exact specialized model or endpoint selected, provided it is genuinely
  materials-specific and executable behind the Phase 19 serving contract
- The exact system chosen for the “real” proof versus the thinner compatibility
  proof
- The exact additive lineage field names and compare/report output wording,
  provided the core artifact contracts stay stable
- The exact place where the specialized lane is surfaced most prominently in
  operator docs, provided the role stays evaluation-primary

### Deferred Ideas (OUT OF SCOPE)
- Forcing direct specialized-lane Zomic generation as the primary Phase 20 goal
- Requiring every specialized lane to be locally served before it can enter the
  workflow
- Full two-system benchmark parity as part of Phase 20 instead of Phase 21
- Creating a specialized-only artifact path or specialized-only workflow
- Zomic-native local generation adaptation or fine-tuned checkpoint training
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| LLM-15 | The platform can use at least one specialized materials model path for a real workflow role, such as synthesis-aware evaluation or QC-conditioned generation, while remaining additive to the existing LLM workflow. This does not assume off-the-shelf specialized models are already Zomic-native. | Use a real `specialized_materials` evaluation lane via `llm-evaluate`, backed by one OpenAI-compatible specialist endpoint. Prefer CSLLM-style synthesizability/precursor assessment on Al-Cu-Fe, with generation compatibility preserved through the existing lane registry. |
| LLM-16 | `llm-launch`, `llm-replay`, and `llm-compare` remain compatible when the originating run used a local or specialized lane. | Keep the existing launch/replay wrappers and extend artifacts additively so originating lane identity survives launch, replay, outcome snapshots, and comparison summaries without a second workflow path. |
| OPS-09 | Every local or specialized run records auditable serving lineage including adapter type, provider/model lane, model identifier or checkpoint, runtime endpoint or path, and launch/replay provenance. | Propagate `LlmServingIdentity` into evaluation manifests/provenance and denormalize it into launch/replay/compare artifacts so checkpoint, revision, endpoint/path, and replay provenance are all explicit. |
</phase_requirements>

## Summary

Phase 20 is mostly a contract-and-lineage phase, not a transport rewrite. The
current repo already has the right additive seams for generation, launch,
replay, and compare: `resolve_serving_lane()`, `LlmServingIdentity`,
`resolve_campaign_launch()`, and `build_replay_serving_identity()` already keep
lane selection explicit and replay-safe. The largest functional gap is
`llm-evaluate`: today it is not lane-aware, it resolves only from
`config.backend`, and its run manifest/provenance do not record the same rich
serving identity that generation and replay already understand.

The most honest first specialized lane is a structure-conditioned evaluation
lane, not a direct Zomic generator. Public CSLLM artifacts are a strong fit for
the chosen scope: the official model family is specialized for
synthesizability, method prediction, and precursor recommendation, but its own
docs and code assume crystal-structure inputs such as CIF/POSCAR or a derived
structure string, not Zomic-native prompts. That means the clean Phase 20
implementation is: keep `llm-generate` unchanged as the single generation
engine, make `llm-evaluate` lane-aware, add a small specialist-input formatter,
and preserve artifact shapes while enriching lineage.

The recommended proof is one real Al-Cu-Fe specialized evaluation lane plus one
thin Sc-Zn compatibility pass. Al-Cu-Fe is the better real proof because the
existing icosahedral/QC-oriented system makes precursor and synthesizability
judgments more defensible. Sc-Zn should stay thin: just enough to prove that
launch, replay, and compare stay compatible when the originating lane is
specialized. The current targeted Phase 20 test slice already passes
(`24 passed` across launch, replay, compare, and evaluate tests), so the plan
should extend existing coverage rather than rebuild it.

**Primary recommendation:** reuse the existing `llm_generate.model_lanes`
registry for `llm-evaluate`, add a specialist structure-serialization module for
the evaluation-primary lane, and denormalize full `serving_identity` into
evaluation and comparison artifacts without creating any new artifact family.

## Project Constraints (from CLAUDE.md)

- The repo is a vZome monorepo including the `materials-discovery/` no-DFT
  quasicrystal pipeline.
- Every change under `materials-discovery/` must update
  `materials-discovery/Progress.md`.
- Progress updates must add a Changelog row and append a timestamped Diary entry
  under the current date heading.
- This progress-tracking rule applies to code, config, docs, experiments,
  fixes, refactors, and new systems.

## Standard Stack

### Core

| Library / Contract | Version | Purpose | Why Standard |
|--------------------|---------|---------|--------------|
| Existing lane registry: `LlmModelLaneConfig` + `resolve_serving_lane()` | repo current | Single authoritative lane-resolution contract | Already shipped, already tested, and already shared by generation, launch, and replay. Reusing it keeps Phase 20 additive. |
| Existing lineage contract: `LlmServingIdentity` | repo current | Auditable provider/model/checkpoint/endpoint identity | Replay already depends on hard identity matching; extending this contract is safer than inventing per-stage identity dicts. |
| `httpx` | 0.28.1 (PyPI latest, published 2024-12-06) | OpenAI-compatible HTTP transport | Already used by `openai_compat_v1`; no new transport abstraction is needed inside the repo. |
| `vLLM` | 0.19.0 (PyPI latest, published 2026-04-03) | Recommended self-hosted OpenAI-compatible specialist endpoint | Official docs support OpenAI-compatible serving, custom chat templates, and LoRA adapter serving, which fits a specialist-lane proof without changing the repo transport contract. |

### Supporting

| Library / Service | Version | Purpose | When to Use |
|-------------------|---------|---------|-------------|
| `pymatgen` | 2026.3.23 (PyPI latest, published 2026-03-23) | `CandidateRecord` to crystal-structure object/serialization bridge | Use for the real specialized evaluation proof so the lane sees a structure-centric input, not only the current JSON prompt. |
| `pyxtal` | 1.1.3 (PyPI latest, published 2026-03-20) | CSLLM-style structure string formatting via symmetry/Wyckoff features | Use if the real proof targets CSLLM fidelity rather than a thinner prompt-only compatibility lane. |
| Hugging Face TGI Messages API | 1.4.0+ (official minimum for OpenAI compatibility) | Alternative OpenAI-compatible serving layer | Use instead of vLLM when the specialist model is already deployed behind TGI or a managed Hugging Face Inference Endpoint. |
| CSLLM model family | official public model card current 2026-04-05 | Real materials-specific evaluation model for synthesizability, methods, and precursors | Use for the main proof lane because its published task profile matches the phase boundary better than direct Zomic generation does. |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `vLLM` specialist serving | TGI Messages API / dedicated HF endpoint | Good alternative for merged chat models or managed endpoints, but vLLM is stronger for LoRA-style specialist loading and custom chat-template handling. |
| Exact structure-aware specialist input | Prompt-only JSON evaluation over the current `CandidateRecord` payload | Easier, but lower-fidelity to CSLLM's published input shape; acceptable only for the thin compatibility proof, not the main proof. |
| Reusing `llm_generate.model_lanes` | New `llm_evaluate.model_lanes` config block | Avoid this. A second lane registry would fragment authority and make replay/compare lineage drift more likely. |

**Installation:**

```bash
# Repo side: only needed if the real proof implements exact CSLLM-style structure serialization
cd materials-discovery
uv add --optional specialized-eval "pyxtal>=1.1.3"

# Serving host side: only needed if the specialist endpoint is self-hosted with vLLM
python3 -m pip install "vllm>=0.19.0"
```

**Version verification:** This is a Python project, so verify against PyPI or
the project metadata, not `npm view`.

```bash
python3 -m pip index versions vllm
python3 -m pip index versions pyxtal
python3 -m pip index versions pymatgen
python3 - <<'PY'
import json, urllib.request
for pkg in ["vllm", "pyxtal", "pymatgen", "httpx"]:
    with urllib.request.urlopen(f"https://pypi.org/pypi/{pkg}/json") as r:
        data = json.load(r)
    print(pkg, data["info"]["version"])
PY
```

## Architecture Patterns

### Recommended Project Structure

```text
materials-discovery/src/materials_discovery/llm/
├── runtime.py          # Existing transport adapters and readiness checks
├── launch.py           # Existing lane authority and serving identity builders
├── replay.py           # Existing hard-identity replay rules
├── compare.py          # Existing outcome/comparison artifacts
├── evaluate.py         # Evaluation orchestration and manifest writing
└── specialist.py       # New: specialist-lane serializers, prompts, and parsers
```

### Pattern 1: Make `llm-evaluate` Lane-Aware Through the Existing Lane Registry

**What:** Add `--model-lane` to `mdisc llm-evaluate` and resolve the lane with
the same precedence and config authority already used by generation and launch.

**When to use:** Always. The evaluation-primary specialized lane should not get
its own parallel config or runtime path.

**Example:**

```python
# Source: materials-discovery/src/materials_discovery/llm/launch.py
resolved_lane, lane_config, lane_source = resolve_serving_lane(
    requested_lane,
    config.llm_generate,
    config.backend,
)
serving_identity = build_serving_identity(
    requested_lane=requested_lane,
    resolved_lane=resolved_lane,
    lane_source=lane_source,
    backend=config.backend,
    lane_config=lane_config,
)
```

### Pattern 2: Keep Artifact Shapes Stable, but Denormalize Serving Identity

**What:** Extend existing artifacts additively rather than creating new ones.
The fields that most need denormalization are:

- `LlmEvaluationRunManifest`
- `candidate.provenance["llm_assessment"]`
- `LlmCampaignLaunchSummary`
- `LlmCampaignOutcomeSnapshot`
- `LlmCampaignComparisonResult`

**When to use:** Any time a run uses `local` or `specialized_materials`
serving.

**Example:**

```python
# Source: materials-discovery/src/materials_discovery/llm/schema.py
class LlmServingIdentity(BaseModel):
    requested_model_lane: str | None = None
    resolved_model_lane: str
    resolved_model_lane_source: ResolvedModelLaneSource
    adapter: str
    provider: str
    model: str
    effective_api_base: str | None = None
    checkpoint_id: str | None = None
    model_revision: str | None = None
    local_model_path: str | None = None
```

### Pattern 3: Put Specialist Input Formatting Behind a Small Adapter Module

**What:** Convert a `CandidateRecord` into a structure-oriented specialist
payload before prompting the specialized lane. For the real proof, prefer a
`pymatgen.Structure` bridge plus a CSLLM-style structure string. Keep the
current JSON prompt builder as the fallback/general-purpose path.

**When to use:** The real Al-Cu-Fe specialized evaluation proof.

**Example:**

```python
# Source shape: materials-discovery/src/materials_discovery/common/schema.py
# Specialist formatting target: https://github.com/szl666/CSLLM/blob/main/material_str.py
from pymatgen.core import Lattice, Structure

structure = Structure(
    Lattice.from_parameters(**candidate.cell),
    [site.species for site in candidate.sites],
    [site.fractional_position for site in candidate.sites],
)
specialist_input = structure_to_str(structure)  # CSLLM-style serializer
```

### Pattern 4: Compare Should Surface Lane Identity, Not Only Metric Deltas

**What:** Preserve the current metric-delta comparison flow, but add lane-aware
summary lines and stored identity fields so operators can see which endpoint,
checkpoint, or local path produced the result.

**When to use:** Every `llm-compare` result whose current or prior outcome came
from `local` or `specialized_materials` serving.

**Example:**

```python
# Source: materials-discovery/src/materials_discovery/llm/compare.py
lines = [
    f"{current_outcome.system} campaign {current_outcome.campaign_id} "
    f"launch {current_outcome.launch_id} ({comparison_id})",
    f"Acceptance baseline loaded for {acceptance_baseline.system}.",
]
```

Recommended extension: prepend a lane line such as
`specialized_materials via openai_compat_v1 / csllm-precursor / ckpt-...`.

### Anti-Patterns to Avoid

- **Separate specialized-only CLI path:** Do not add `llm-specialized-evaluate`
  or a parallel workflow family. Phase 20 must stay inside the current
  closed-loop CLI surface.
- **Second lane registry under `llm_evaluate`:** This would split config
  authority between generation and evaluation, which conflicts with the Phase
  19 contract.
- **Lane label without hard identity fields:** Recording only
  `specialized_materials` is not auditable enough for replay or compare.
- **Silent downgrade from requested specialist lane to general-purpose:** This
  violates the explicit-fallback rules inherited from Phase 19.
- **Pretending CSLLM is Zomic-native:** Its published input surface is crystal
  structure oriented, so the first proof should stay evaluation-primary.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| OpenAI-compatible specialist serving | Custom FastAPI/Flask wrapper around HF weights | `vllm serve` or TGI Messages API | The repo already expects `/v1/chat/completions` plus a `/v1/models`-style readiness probe. vLLM and TGI already implement that contract. |
| Structure/symmetry stringification for a specialist model | Bespoke cell/Wyckoff/symmetry text formatting | `pymatgen` plus `pyxtal`, following CSLLM's own `structure_to_str()` pattern | This input shape is easy to get subtly wrong, and symmetry/space-group formatting is not a good place to invent new logic. |
| Lane identity propagation | Stage-specific ad hoc dicts | Existing `LlmServingIdentity` and existing launch/replay helpers | The replay code already enforces hard identity drift rules; reuse the same contract everywhere. |
| Specialist lane switching | Custom per-stage model swap logic | The existing lane registry and `resolve_serving_lane()` precedence | It already encodes requested/default/fallback/backend-default behavior and is covered by tests. |

**Key insight:** the hard part of Phase 20 is not talking to an HTTP endpoint.
It is keeping one authoritative lane registry and one auditable lineage contract
across evaluation, launch, replay, and compare.

## Common Pitfalls

### Pitfall 1: Extending Only `backend`, Not Lane Resolution

**What goes wrong:** `llm-evaluate` continues to use only `config.backend`, so
the specialist lane is never actually selected even when config contains a
`specialized_materials` lane.

**Why it happens:** The current `evaluate.py` path resolves only `_resolve_adapter(config)`,
which reads the backend fields directly.

**How to avoid:** Add `--model-lane` to `llm-evaluate`, reuse
`resolve_serving_lane()`, and persist the resulting `LlmServingIdentity`.

**Warning signs:** The evaluation run manifest shows only the baseline
provider/model, and changing `model_lanes.specialized_materials` has no effect.

### Pitfall 2: Recording Lineage in Generation but Not in Evaluation/Compare

**What goes wrong:** Launch/replay may remain replay-safe, but operators still
cannot tell which specialist endpoint or checkpoint produced an evaluation or a
comparison summary.

**Why it happens:** `LlmEvaluationRunManifest`, `LlmCampaignOutcomeSnapshot`,
and current comparison summary lines do not carry the full serving identity.

**How to avoid:** Denormalize `serving_identity` into evaluation and comparison
artifacts instead of relying on linked files only.

**Warning signs:** Compare output says only `specialized_materials` without
adapter/provider/model/checkpoint details.

### Pitfall 3: Sending Zomic-Native or Generic JSON Input to a Crystal-Structure Specialist

**What goes wrong:** The specialist lane appears wired up, but the model is
being asked to operate outside the format it was published for.

**Why it happens:** Public CSLLM docs and code target crystal-structure inputs,
not Zomic-native prompts.

**How to avoid:** Treat the main proof as structure-conditioned evaluation and
add a small structure serializer module. Use prompt-only evaluation only for the
thin compatibility proof.

**Warning signs:** The specialist lane returns vague chemistry text, weak
precursor signals, or no measurable improvement over the generic lane.

### Pitfall 4: Making Purely Local GPU Serving a Hard Requirement

**What goes wrong:** The phase plan becomes blocked on infrastructure that is
not needed for the first operational proof.

**Why it happens:** It is easy to assume "specialized lane" implies local GPU
serving on the development machine.

**How to avoid:** Keep the repo transport contract OpenAI-compatible and accept
either a local server or a remote/dedicated endpoint for the first real proof.

**Warning signs:** The plan assumes `vllm`, GPU, or `localhost:8000` are
available even though the current machine does not have them.

### Pitfall 5: Creating a Specialized-Only Artifact Family

**What goes wrong:** Operators now need different tooling for specialized runs,
and replay/compare logic diverges immediately.

**Why it happens:** Specialized evaluation feels different enough to tempt a
new artifact root or a new manifest schema.

**How to avoid:** Keep current artifact roots and schema versions stable. Add
fields, not new families.

**Warning signs:** Proposed file names or schema versions start branching into
`*_specialized_*` families.

## Code Examples

Verified patterns from official sources:

### Lane Resolution and Identity Reuse

```python
# Source: materials-discovery/src/materials_discovery/llm/launch.py
requested_lanes, resolved_lane, lane_config, lane_source = resolve_campaign_model_lane(
    spec,
    config,
)
serving_identity = build_serving_identity(
    requested_lane=requested_lanes[0] if requested_lanes else None,
    resolved_lane=resolved_lane,
    lane_source=lane_source,
    backend=config.backend,
    lane_config=lane_config,
)
```

### vLLM LoRA Serving Behind the Existing OpenAI-Compatible Contract

```bash
# Source: https://docs.vllm.ai/en/latest/features/lora/
vllm serve meta-llama/Llama-3.2-3B-Instruct \
  --enable-lora \
  --lora-modules sql-lora=jeeejeee/llama32-3b-text2sql-spider
```

Phase 20 adaptation: serve the specialist model under a stable model ID, then
point the repo's `specialized_materials` lane at that endpoint via
`openai_compat_v1`.

### TGI Messages API as a Compatible Alternative

```python
# Source: https://huggingface.co/docs/text-generation-inference/main/messages_api
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:3000/v1",
    api_key="-",
)
chat_completion = client.chat.completions.create(
    model="tgi",
    messages=[{"role": "user", "content": "What is deep learning?"}],
    stream=False,
)
```

### CSLLM Structure String Formatting Surface

```python
# Source: https://github.com/szl666/CSLLM/blob/main/material_str.py
def structure_to_str(structure):
    px_structure = pyxtal()
    px_structure._from_pymatgen(structure)
    ...
    return f"{spg_symbol} {lattice_str} {'->'.join(wyckoff_strings)}"
```

Planning implication: the first real specialist proof should include a small
adapter that emits a structure-centric payload before prompting the lane.

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Hosted-provider-only or mock-only LLM path | OpenAI-compatible multi-lane serving seam with recorded lane identity | Landed in Phase 19 / 2026-04-05 | Phase 20 can stay additive and does not need a new transport abstraction. |
| Single merged model per endpoint | Base-model plus LoRA-style per-model serving under one OpenAI-compatible server | Mature in current vLLM docs and package releases | A specialist lane can be introduced as a named served model instead of a separate runtime family. |
| Generic chemistry prompting for evaluation | Specialist synthesizability / precursor models such as CSLLM | CSLLM published 2025 | The first honest specialized lane should target evaluation tasks, not forced direct Zomic generation. |

**Deprecated/outdated:**

- In-process local inference as the first integration: contradicted by the
  inherited Phase 19 contract.
- Specialized lane as metadata only: not sufficient for Phase 20's real
  workflow-role requirement.
- Direct Zomic generation as the only meaningful specialist proof: out of scope
  for the first operational cut.

## Open Questions

1. **Should the real proof use exact CSLLM-style structure formatting or a thinner prompt-only bridge?**
   - What we know: CSLLM's public repo and model card expect crystal-structure-oriented inputs and expose tasks aligned with synthesizability, methods, and precursor prediction.
   - What's unclear: whether the team wants to pay the optional `pyxtal` dependency cost in Phase 20 or defer it.
   - Recommendation: use exact structure formatting for the main Al-Cu-Fe proof; allow prompt-only formatting only for the thin compatibility proof.

2. **Should `serving_identity` be denormalized into outcome/comparison artifacts or only linked through launch files?**
   - What we know: replay already depends on `LlmServingIdentity`, but `LlmCampaignOutcomeSnapshot` and `LlmCampaignComparisonResult` currently store only lane/source and metric deltas.
   - What's unclear: how much duplication the team considers acceptable.
   - Recommendation: denormalize the full identity. Auditability is the point of OPS-09, and compare artifacts should be self-describing.

3. **What exact endpoint form should the planner assume for the first proof?**
   - What we know: the current machine does not have `vllm`, no local endpoint is running at `localhost:8000`, and no NVIDIA runtime is visible.
   - What's unclear: whether the team already has a remote or dedicated OpenAI-compatible specialist endpoint outside the repo.
   - Recommendation: plan the code against any `openai_compat_v1` endpoint and keep the endpoint recipe/operator setup as a separate execution concern.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python 3.11 | Repo runtime requirement (`requires-python >=3.11`) | ✓ | 3.11.15 | Use `uv run --python 3.11 ...` because default `python3` is 3.9.6 |
| `uv` | Reproducible test execution in the current environment | ✓ | 0.10.10 | — |
| `pytest` on PATH | Direct test invocation | ✗ | — | Use `uv run --python 3.11 --with pytest pytest ...` |
| OpenAI-compatible endpoint at `http://localhost:8000` | Current real-mode sample configs | ✗ | — | Use a remote/dedicated OpenAI-compatible endpoint or start a local server explicitly |
| `vllm` CLI | Self-hosted specialist endpoint | ✗ | — | Use TGI or a remote/dedicated endpoint for the first proof |
| Docker | Containerized serving fallback | ✓ | 29.3.0 | — |
| NVIDIA runtime / GPU visibility | Local CSLLM/vLLM serving on this machine | ✗ | — | Use remote/dedicated endpoint; do not make local GPU serving a hard Phase 20 prerequisite |
| `pymatgen` in the current env | Exact structure serialization for the specialist lane | ✗ | — | Install as project extra or use the thin compatibility proof |
| `pyxtal` in the current env | CSLLM-style structure string formatting | ✗ | — | Install as optional extra or defer exact serialization |

**Missing dependencies with no fallback:**

- None for planning and code implementation.
- If the team insists on a purely local CSLLM proof on this machine, GPU/runtime
  availability becomes a blocker.

**Missing dependencies with fallback:**

- No local OpenAI-compatible endpoint is running at `localhost:8000`.
- `vllm` is not installed locally.
- `pymatgen` and `pyxtal` are not installed in the current environment.
- Direct `pytest` execution is not available on PATH for Python 3.11, but `uv`
  is available and works.

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | `pytest` (repo config in `materials-discovery/pyproject.toml`; validated with `uv run --python 3.11 --with pytest pytest`) |
| Config file | `materials-discovery/pyproject.toml` |
| Quick run command | `cd materials-discovery && uv run --python 3.11 --with pytest pytest tests/test_llm_launch_core.py tests/test_llm_replay_core.py tests/test_llm_compare_core.py tests/test_llm_evaluate_cli.py -q` |
| Full suite command | `cd materials-discovery && uv run --python 3.11 --with pytest pytest -q` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| LLM-15 | `llm-evaluate` can resolve and run a real `specialized_materials` lane while preserving additive artifacts | unit + integration | `cd materials-discovery && uv run --python 3.11 --with pytest pytest tests/test_llm_evaluate_cli.py -q` | ✅ extend existing file |
| LLM-16 | launch, replay, and compare remain compatible when the originating lane is local or specialized | unit + integration | `cd materials-discovery && uv run --python 3.11 --with pytest pytest tests/test_llm_launch_core.py tests/test_llm_replay_core.py tests/test_llm_compare_core.py -q` | ✅ |
| OPS-09 | serving identity is auditable across evaluation, generation, launch, replay, and compare | unit | `cd materials-discovery && uv run --python 3.11 --with pytest pytest tests/test_llm_generate_core.py tests/test_llm_replay_core.py tests/test_llm_compare_core.py tests/test_llm_evaluate_schema.py -q` | ✅ extend existing files |

### Sampling Rate

- **Per task commit:** `cd materials-discovery && uv run --python 3.11 --with pytest pytest tests/test_llm_launch_core.py tests/test_llm_replay_core.py tests/test_llm_compare_core.py tests/test_llm_evaluate_cli.py -q`
- **Per wave merge:** `cd materials-discovery && uv run --python 3.11 --with pytest pytest tests/test_llm_launch_core.py tests/test_llm_replay_core.py tests/test_llm_compare_core.py tests/test_llm_evaluate_cli.py tests/test_real_mode_pipeline.py -q`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps

- [ ] `materials-discovery/tests/test_llm_evaluate_core.py` — dedicated lane-resolution and `serving_identity` coverage for `llm-evaluate` (currently missing as a separate core test module)
- [ ] `materials-discovery/tests/test_llm_evaluate_cli.py` — extend to assert specialized-lane selection and evaluation-manifest lineage
- [ ] `materials-discovery/tests/test_llm_compare_core.py` — extend to assert denormalized `serving_identity` and lane-aware summary lines
- [ ] `materials-discovery/tests/test_llm_launch_cli.py` — extend to assert `serving_identity` is persisted on the successful launch-summary path, not only via `resolved_launch`
- [ ] `materials-discovery/tests/test_real_mode_pipeline.py` — add the one-real-system plus one-thin-proof specialized-lane path

## Sources

### Primary (HIGH confidence)

- Local repo context and contracts:
  - `.planning/phases/20-specialized-lane-integration-and-workflow-compatibility/20-CONTEXT.md`
  - `.planning/phases/19-local-serving-runtime-and-lane-contracts/19-CONTEXT.md`
  - `.planning/REQUIREMENTS.md`
  - `materials-discovery/src/materials_discovery/common/schema.py`
  - `materials-discovery/src/materials_discovery/llm/schema.py`
  - `materials-discovery/src/materials_discovery/llm/evaluate.py`
  - `materials-discovery/src/materials_discovery/llm/launch.py`
  - `materials-discovery/src/materials_discovery/llm/replay.py`
  - `materials-discovery/src/materials_discovery/llm/compare.py`
  - `materials-discovery/src/materials_discovery/cli.py`
  - `materials-discovery/tests/test_llm_launch_core.py`
  - `materials-discovery/tests/test_llm_replay_core.py`
  - `materials-discovery/tests/test_llm_compare_core.py`
  - `materials-discovery/tests/test_llm_evaluate_cli.py`
- Official model/docs:
  - https://huggingface.co/zhilong777/csllm
  - https://github.com/szl666/CSLLM
  - https://github.com/szl666/CSLLM/blob/main/material_str.py
  - https://docs.vllm.ai/en/latest/features/lora/
  - https://docs.vllm.ai/en/latest/cli/serve.html
  - https://huggingface.co/docs/text-generation-inference/main/messages_api
- Package registries:
  - https://pypi.org/pypi/vllm/json
  - https://pypi.org/pypi/pyxtal/json
  - https://pypi.org/pypi/pymatgen/json
  - https://pypi.org/pypi/httpx/json

### Secondary (MEDIUM confidence)

- `materials-discovery/developers-docs/llm-integration.md` — current project architecture and literature summary
- `materials-discovery/developers-docs/llm-quasicrystal-landscape.md` — project rationale for evaluation-focused specialist models
- `materials-discovery/developers-docs/pipeline-stages.md` — CLI behavior summary
- `materials-discovery/developers-docs/configuration-reference.md` — config semantics and Phase 19 lane notes

### Tertiary (LOW confidence)

- None. I did not rely on unverified community posts for any recommendation.

## Metadata

**Confidence breakdown:**

- Standard stack: MEDIUM - repo-side contracts are high confidence, but the
  exact specialist endpoint choice is still an implementation decision and was
  not executed live in this environment.
- Architecture: HIGH - the lane, replay, and lineage patterns are all visible
  in the shipped code and current tests.
- Pitfalls: MEDIUM - they are strongly supported by the current code gaps and
  official model docs, but the exact failure modes of a live specialist
  endpoint were not exercised locally.

**Research date:** 2026-04-05
**Valid until:** 2026-04-12
