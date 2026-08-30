# Silicon Sample Benchmark — method registration form

Fill in every item before the prediction lock; this file ships inside your repo's Zenodo release
(see the README's *Deposit* step). This form covers **one entry** (one repo / one Zenodo release,
`primary` or `secondary-k` — see the README's *What counts as a submission*); if you submit several
entries, fill one form per entry. Items marked **★**
must be disclosed **fully publicly** (never escrowed or withheld). Items marked **†** must be at
minimum escrowed — they may be sealed from the public, but never withheld from the core team. Items
not applicable to your approach: write `N/A`. When several models serve different pipeline stages, complete the model
sections (B) once per model. See the call's *Disclosure policy* for escrow rules.

> **History.** An earlier version of this entry was a **Tier-2** cell-mean forecast made by
> `claude-fable-5`, with a pipeline in `generation/`. It was withdrawn on 2026-08-28 and its code
> was deleted. That form is in git history at commit `aa4e060`. Nothing from it is carried into the
> answers deposited here.

> **This form covers the `secondary-1` entry.** It is one of two entries from `team_27`. The
> `primary` entry uses the same population, the same stimuli, the same model and the same hardware,
> and asks every item in its own prompt. This entry asks each multi-item scale as one block. That is
> the only factor that differs, and the pair is designed to bracket the human coherence value from
> below and above. See E.2.

> **Every fact the run produces is filled in**, from `sim/out/03_report_hybrid.txt`,
> `sim/out/05_coherence.txt` and `sim/out/run_entryB.log`. Two items are still `PENDING`, and both
> need a person, not a run: the competing-interests declaration (I.1) and the blinding attestation
> (I.3). Both must be signed by the members named in 0.1 before the deposit.

---

## 0 · Approach identity and output
- **0.1 Team ★** — name, the one or two members (teams are at most two, unless a larger team was approved on request), affiliations, corresponding contact:
  Team `team_27`, two members.
  Andres Laverde Marin, Joint Research Centre, European Commission, ORCID
  [0000-0002-9578-4412](https://orcid.org/0000-0002-9578-4412). Corresponding contact:
  andreslaverdemarin@gmail.com.
  Giordano De Marzo, University of Konstanz, ORCID
  [0000-0002-3127-5336](https://orcid.org/0000-0002-3127-5336).
  The same values are in `metadata.json` (`team_name`, `contact`, `creators`). Both ORCIDs pass the
  ISO 7064 MOD-11-2 checksum.
- **0.2 Plain-language summary ★** — one paragraph, what the approach does (not how):
  We build 9,000 synthetic people whose demographics match the United States adult population, and
  who are related to each other the way real people are. We give each person one of the 17 texts to
  read, then ask that person all 44 survey questions. The questions that belong to one scale are
  put on one page and answered together, in one pass, so the person can see the answers already
  given. The 7 questions that stand alone are asked one at a time. A local open-weights
  language model answers as that person. We never ask the model for an average, a trend or an
  effect. We collect 9,000 individual questionnaires, and the effects come out of the arithmetic
  afterwards, exactly as they do for the human study.
- **0.3 Submission tier & approach family ★** — tier (1/2/3); family (e.g. per-respondent simulation / agent / direct forecast; single model / ensemble / multi-agent / zero-shot / literature-conditioned):
  **Tier 1.** Per-respondent simulation. Single model, single draw for each respondent and item; no
  ensemble, no multi-agent scaffold, no averaging over repeats. Zero-shot: no fine-tuning, no
  retrieval, no in-context example of any study's results. The model is local open weights, run on
  our own hardware. The 44 raw survey items are generated and the 13 scored outcomes are computed by
  the benchmark's own `scripts/clean.R`.
  **Survey administration is HYBRID, and this is the one factor that separates this entry from our
  `primary` entry.** The 6 multi-item outcomes (37 items) are asked as **blocks**: every item of one
  scale is on one page and is answered in one forward pass. The 7 single-item outcomes are asked
  **one item for each call**, and their values are **reused unchanged from the `primary` entry**, not
  regenerated. Persona construction, stimulus, model, hardware and the persona-to-condition
  assignment are identical in the two entries. See E.2.
- **0.4 Pipeline diagram** — ordered steps from raw inputs to submitted file:
  1. `population/01c_quotas_18000.py` — build the quota targets from the preregistration Table 3 and
     Census CPS 2024.
  2. `population/02_build_personas.py` — rake 9,000 GSS respondents onto those margins by iterative
     proportional fitting, then quota-sample independently inside each of the 17 conditions
     (seed `20260807`).
  3. `sim/00_extract_materials.py` — extract the 17 condition texts and the 44 items into
     `sim/out/00_materials.json`.
  4. `sim/01_persona_characteristics.py` — write the 9,000-row persona table
     (`sim/out/01_personas.csv`) and its self-check (`sim/out/01_report.txt`).
  5. `sim/03_generate_replies.py` — the `primary` entry's run: 9,000 respondents x 44 items =
     396,000 generations, one prompt for each item. Writes `sim/out/03_replies.jsonl`. This entry
     takes its 7 single-item outcomes (63,000 answers) from that file, unchanged.
  6. `sim/03b_generate_hybrid.py` — this entry's run: 9,000 respondents x 6 scales = **54,000 block
     prompts**, covering the 37 items of the multi-item outcomes. It joins them to the 63,000 reused
     single-item answers and writes all 396,000 records to `sim/out/03_replies_hybrid.jsonl`.
  7. `sim/04_build_raw_export.py --answers sim/out/03_replies_hybrid.jsonl` — one row for each
     respondent, 44 raw item columns, into `raw_data_deposit/tier1_raw_export_hybrid.csv`.
  8. `make clean INPUT=raw_data_deposit/tier1_raw_export_hybrid.csv` — the benchmark's own
     `scripts/clean.R` builds every composite and writes
     `predictions/team_27_T1_secondary-1_v1.csv`.
  9. `make manifest` then `make check` — SHA-256 into `metadata.json`, then the organizers' validator.
  **Stage 2 (`sim/02_write_personas.py`) is NOT in this pipeline.** It writes prose personas with a
  second model. It was measured and dropped; see D.2.
- **0.5 Coverage ★** — number of respondents/cells/estimates; mapping to conditions. Full coverage is required: every submission predicts **all 16 interventions and all 13 outcomes** (partial coverage is not accepted). Confirm here:
  **Full coverage, confirmed.** 9,000 synthetic respondents: 500 in each of the 16 interventions and
  1,000 in `control`. Every respondent answers all 44 raw items, so all 13 scored outcomes are
  present for all 17 conditions. No cell is empty and no cell is `NA`. This meets the preregistered
  precision floor exactly (500 per intervention, 1,000 in control). Condition and outcome labels come
  from `scripts/lib/submission_spec.R`; no label is typed by hand or written by the model.

## A · Scope of LLM use
- **A.1 Purpose** — every workflow stage where LLMs are used:
  **Two stages of 0.4 produce submitted values, and both are answer stages.** Step 6
  (`sim/03b_generate_hybrid.py`) generates the 333,000 values of the 6 multi-item outcomes, as 54,000
  scale blocks. Step 5 (`sim/03_generate_replies.py`) generated the 63,000 values of the 7
  single-item outcomes; that run belongs to our `primary` entry and this entry **reuses its answers
  unchanged rather than regenerating them**, so it is declared here as a stage of this entry too.
  Together they are the 396,000 submitted values. One model, `Qwen/Qwen3.8-27B`, wrote every one.
  Every other step is deterministic Python or R. No language model builds the population, renders a
  persona, computes a composite, or edits an output file. `sim/02_write_personas.py` is the only
  other script in `sim/` that can call a model, and it is **not in this pipeline** (0.4, D.2).
  Two models were used **for validation only**, and neither contributed any submitted value:
  `google/gemma-4-26B-A4B-it` wrote prose personas in the measurement that led us to drop stage 2
  (D.2) and answered block prompts in the v18 format measurement on public Voelkel data (J.1); and
  `qwen/qwen3.8-flash` answered a 60-respondent probe used to check response realism (J.1). Gemma has
  a section B, because it ran locally on the same stack as the answering model. Flash does not,
  because it serves no pipeline stage; it is described in J.1 with its settings and cost in K.3.
  Six further open-weight models were run **only in the comparison that chose the answering model**,
  before this pipeline existed. None of them answered any item of this megastudy and none
  contributed a submitted value. They are named in section B (models 3 to 8).
- **A.2 Degree of automation ★** — confirm fully automated, no human in the loop at prediction time; note any exception:
  Fully automated at prediction time. The prompts are built by code from the materials before any
  answer exists. No answer is edited, selected, or re-asked with different wording. Two automated
  exceptions, both pre-specified and both blind to the value:
  1. **Re-ask.** A block whose text does not give one number for each item of the scale, or gives a
     number outside that item's scale, is re-asked with the **identical prompt** and a new seed, up
     to five rounds. The same rule applied to a single item in the step-5 run.
  2. **Midpoint fill.** A block still unparsed after five rounds would be written as 50 on every
     item of that scale, because `make check` fails on one `NA`.
  **Neither exception was used in this entry's own run: 54,000 of 54,000 blocks parsed on the first
  pass, no retry round ran, and no block was filled** (`sim/out/03_report_hybrid.txt`). The reused
  single-item answers carry the step-5 run's own retry record, reported in the `primary` entry's
  form. Nothing else is repaired.

## B · Model / system details (once per model)

### B — Model 1: the answering model (produces every submitted value)
- **B.1 Model name(s)** — exact identifiers incl. provider, size, version/timestamp, source link:
  `Qwen/Qwen3.8-27B` — 27 billion parameters, dense (no mixture of experts), instruction-tuned.
  Local weights from the Hugging Face Hub, <https://huggingface.co/Qwen/Qwen3.8-27B>. The weights are
  read from the local cache; no hosted endpoint answers any item.
- **B.2 Access & context mode** — API/web/local; API name + version; chat vs stateless; exact call dates:
  Local inference on our own hardware. No API, no provider, no account, no key. The interface is a
  **text completion, not a chat turn**: the chat template is not applied, and the model continues a
  survey page. A **block** prompt ends with `You answer:` and the model writes one numbered line for
  each item of that scale; a **single-item** prompt ends with `You choose: '`, as in the `primary`
  entry.
  **Statelessness, stated exactly.** The 396,000 submitted values come from 117,000 generations:
  54,000 block generations and 63,000 single-item generations. Every **generation** is stateless
  with respect to every other — the model is given one prompt and keeps no history across prompts.
  Inside one block generation the items are **not** independent, and that is the design: the model
  writes the whole scale in one forward pass and attends to the answers it has already written. No
  information crosses from one scale to another, or from one respondent to another.
  Call-date windows, both in UTC. **The two are stated separately, because 63,000 of the 396,000
  submitted values were generated in the `primary` entry's run and are reused here unchanged.**
  Block prompts, the 37 multi-item outcomes: **2026-08-30T06:17:55Z to 2026-08-30T08:13:40Z**.
  Single items, the 7 stand-alone outcomes, reused from the `primary` run:
  **2026-08-29T12:07:30Z to 2026-08-29T17:40:33Z**.
- **B.3 Configuration** — temperature, top-p/top-k, max tokens, penalties, stop sequences, seeds, reasoning effort, completions per item:
  **Block prompts (37 items, this entry's own run).** `temperature 1.6`, `top_p 0.95`, no top-k, no
  penalties, `max_tokens 320`, no stop sequence, `seed 20260830` (the per-block seed is a BLAKE2b
  hash of the seed, the `profile_id` and the scale name, so a block is reproducible on its own),
  `max_model_len 4096`. **Structured outputs are on**: vLLM `StructuredOutputsParams` with the regex built by
  `regex_for(k)`, which concatenates one literal line for each item of the scale —
  `1: (100|[0-9]{1,2})\n2: (100|[0-9]{1,2})\n` and so on up to `k`. **One
  completion per respondent and scale.**
  **Single items (7 items, reused from the `primary` run).** `temperature 1.0`, `top_p 0.95`,
  `max_tokens 64`, stop sequence `'` (the closing quote), `seed 20260828`, no structured output.
  Reasoning: not applicable in either case — these are completions, and no thinking mode is enabled.
  *Why 1.6 and why a regex.* At temperature 1.6 a free-running model broke the answer format in 64
  per cent of blocks, and 340 of 4,000 blocks were lost, so the blocks that survived were a
  compliant subset — a selection effect on the data. The regex makes the shape impossible to break,
  so nothing is dropped and no selection happens. Sampling continues inside the regex, so the
  per-answer noise is kept. Temperature 1.6 is the value at which block-mode inter-item correlation
  lands inside the human sampling interval on 2 of Voelkel's 4 scales and just outside on the other
  two; at 1.0 the block format overshoots on all four. Both facts were measured on public data
  (J.1), never on this study.
  The 320-token budget is deliberate: the trust block writes 12 numbered lines.
- **B.4 Customization** — fine-tuning, RAG, prompt optimization, tool use, web search, agentic scaffolds (cross-ref H):
  None. No fine-tuning, no retrieval, no web search, no tool use, no agentic scaffold, and no prompt
  optimization against any outcome data. The published weights are used as they are.
- **B.5 Persistent memory** — across interactions? what persisted:
  None. Each generation sees one prompt and nothing else. The engine's prefix cache is a speed
  optimization over identical token prefixes; it changes no output.
- **B.6 Inference stack** — for local models: serving framework + version, quantization, hardware:
  vLLM 0.19.1, torch 2.10.0+cu128, transformers 5.14.1, Python 3.11. **No quantization** — the
  published BF16 weights. Hardware: one NVIDIA H100 80GB HBM3, driver 550.127.08, CUDA 12.4.
  `gdn_prefill_backend: triton` is set, because the default kernel needs `nvcc`, which this machine
  does not have.
- **B.7 Ensembles** — members + exact aggregation rule:
  N/A. One model, one draw for each respondent and item. Nothing is averaged, and no ensemble exists.
  This is deliberate: v16 measured that averaging several draws for one person improves treatment-
  effect recovery a little and reduces the response variance ratio a great deal (from 0.36 to 0.14 on
  `Concern`), and the variance ratio is the benchmark's headline distributional diagnostic.

### B — Model 2: `google/gemma-4-26B-A4B-it` (validation only, no submitted value)
- **B.1–B.6** — `google/gemma-4-26B-A4B-it`, local weights, same vLLM stack and same H100. It was
  used twice, both times on public data: it wrote prose personas in the v15 measurement described in
  D.2, and it answered Voelkel block prompts in the v18 format measurement described in J.1. **No
  text or value it produced reaches the deposited answers**, because stage 2 is not in the pipeline
  and no Voelkel answer is a submitted value. Call windows: 2026-08-29 (v15) and 2026-08-29T21:23Z
  to 2026-08-29T21:53Z (v18).

### B — Models 3 to 8: the open-weight comparison set (validation only, no submitted value)
- **B.1–B.6** — The answering model was chosen before this pipeline existed, by running Ashokkumar
  et al.'s own method over that paper's **secondary archive (archive 2)**. Two criteria selected the
  studies, applied together: **nearest in subject** to this megastudy, and **deliverable as survey
  text**, because our model reads text only. That leaves three — `Voelkel2025`, `Doell` and
  `Zickfeld`. `Zickfeld` is pure text. `Voelkel2025` and `Doell` are text survey pages that also
  hold images (22 and 62 image positions); the image files are not deposited on OSF, so each
  position is marked in place and carries the authors' own caption where one exists. **`Goldwert`
  was left out**: six of its arms are video and **the control is one of them**, so no text control
  exists and no treatment effect can be formed. Eight open-weight models were scored on effect
  recovery, all locally on the same H100 and the same vLLM stack, no quantization, in the window
  **2026-08-17 to 2026-08-20**. Two are
  declared above: `Qwen/Qwen3.8-27B` (model 1, chosen) and `google/gemma-4-26B-A4B-it` (model 2).
  The other six are `google/gemma-4-E4B-it`, `openai/gpt-oss-20b`, `google/gemma-3-27b-it`,
  `microsoft/Phi-4`, `mistralai/Mistral-7B-Instruct-v0.3` and
  `deepseek-ai/DeepSeek-R1-Distill-Llama-8B`. `Qwen/Qwen3.8-27B` recovered the measured effects best
  and was chosen for Tier 1. **None of the six answered any item of this megastudy, and none
  contributed a submitted value.** This comparison ran in a separate working project, `modelbench`,
  which is **not part of this deposit** — see K.1. What is deposited is its conclusion: the choice of
  model 1. The ranking and the rest of the search are described in J.1.

## C · Prompts
- **C.1 Exact prompts** — verbatim text or link to deposited file; were they iteratively refined? pre-specified vs in response to outputs:
  Two builders, one for each format. Single items use `sim/lib/answer_prompt.py::build_prompt`,
  unchanged from the `primary` entry: the persona sentence, the condition text the respondent read,
  the item question, and the item's scale. Blocks use
  `sim/03b_generate_hybrid.py::build_block_prompt`, which **keeps that wording exactly** and changes
  only two things: it lists every item of the scale as a numbered question on the page, and it ends
  with an instruction to write one numbered line for each. So the two entries differ by the number
  of questions on a page and by the answer format, and not by how the person or the stimulus is
  described. The builders and their inputs (`sim/out/00_materials.json`, `sim/out/01_personas.csv`)
  are deposited, so every one of the 54,000 block prompts and 63,000 item prompts rebuilds exactly.
  The prompts are also stored verbatim beside every answer in the raw log (K.2).
  **Pre-specified**, in the sense that matters: the structure follows Ashokkumar et al. (2026), whose
  method this replicates, and it was fixed before any megastudy item was answered. It was not refined
  in response to any answer to this study's items.
- **C.2 System-wide instructions**:
  **None.** There is no system prompt, and no chat template is applied. The whole context is the
  completion text shown in C.1. The model is not told it is a language model, not told to be helpful,
  and not given any instruction about how to answer.
- **C.3 Prompt-design rationale** — brief rationale for the prompt design: why prompts were structured as they were, and the reasoning behind major design choices (recommended, not required):
  *One page for each scale, and one prompt for each single item.* Ashokkumar et al.'s own format is
  one item for each prompt, and our `primary` entry keeps it. This entry departs from it for the 6
  multi-item outcomes, for one measured reason. Independent calls make a respondent's answers to one
  scale nearly independent of each other: mean inter-item correlation 0.10 on the 12-item trust
  scale, against about 0.53 for real people on the identical scale (Cologna et al. 2025, alpha
  0.93). Averaging 12 nearly independent numbers collapses the composite, and 3 of the 7 scored
  Tier-1 analyses are distributional. Asking one scale in one forward pass makes consistency
  structural rather than requested. The 7 single-item outcomes have no such problem, so they keep the
  paper's format and are reused unchanged. See E.2 for what the change costs.
  *Not all 44 items in one prompt.* That was used earlier in the sibling project and was reversed on
  2026-08-19. One page for each scale is the middle position: it gives the model its own earlier
  answers inside a scale, and gives it nothing across scales.
  *A completion, not a chat turn.* The model continues a survey transcript instead of replying to a
  request. The published evidence says the two regimes differ: base and completion-style interfaces
  are better **emulators** — they give response distributions nearer to human data and preserve
  demographic structure better — while post-trained chat interfaces are better **estimators**
  (<https://arxiv.org/abs/2608.03044>). Tier 1 is an emulation task.
  *The prompt ends at an open quote.* This makes the candidate answers prefix-free, so the model
  writes a number and stops at the closing quote, and no instruction about formatting is needed.
  *No numeric prior.* The prompt never states where an outcome level sits. The level is part of what
  Tier 1 is scored on, so a stated prior would make our own base rate the prediction.

## D · Persona / profile construction (Tiers 1–2)
- **D.1 Profile source** — source of demographic profiles you constructed: a public survey (e.g. GSS / ANES / Census), other survey, fully synthetic, or none. The benchmark ships no participant pool; report how you built yours, incl. condition assignments:
  A public survey: 9,000 General Social Survey respondents from the 2018, 2021, 2022 and 2024 waves,
  with their post-stratification weights. **We did not draw this pool ourselves.** The file is
  `clone_profiles/profiles.csv` from the organizers' own research repository — the pool they built
  for their own v1 simulation, not a resource given to teams, and not something the benchmark ships.
  It is deposited here as `population/gss_profiles.csv`. Full provenance is in
  `population/README.md`.
  Construction: iterative proportional fitting of the GSS weights onto the preregistered quota
  margins (gender, age band, race from Table 3 of the benchmark preregistration, N = 18,000;
  education and income from Census CPS 2024), then quota sampling of the gender x age and
  gender x race cross-quotas **independently inside each of the 17 conditions**, which is what
  randomisation achieves in the real study and removes demographic composition as a confound of the
  treatment effects. Real microdata gives the joint structure, because independent draws for each
  variable produce people who do not exist and make the moderators artificially independent.
  Deterministic: seed `20260807`. `population/quota_report.txt` is the realised-against-target check.
- **D.2 Profile verbalization** — which variables, rendered how (template vs generated narrative; if generated: model + prompt):
  **A fixed template, built in code. No model writes any persona.** The renderer is
  `sim/lib/answer_prompt.py::template_persona`. It writes one paragraph in the second person, from
  these attributes: age, race, gender, region, education, household income, household size, social
  class, party (the detailed label where the pool has one), political ideology, religion,
  religiosity, born-again status, and prior confidence in the scientific community. A respondent with
  race `Other` has no race clause, and a respondent with no religion gets one sentence saying so.
  Nothing else is stated, and no attribute is invented.
  **Why a template and not a generated narrative.** We measured both. Run v15 answered 6,000
  respondents on Voelkel et al. (2025) twice, changing only the rendering: the code template, and
  prose written by `google/gemma-4-26B-A4B-it`. The template scored a mean treatment-effect
  correlation of 0.334 against the prose arm's 0.304, and the two were equal on every distributional
  metric (Concern variance ratio 0.41 against 0.40; Policies overlap 0.60 against 0.58). The prose
  writer therefore bought nothing measurable, while adding a second model to declare and silently
  dropping attributes it chose not to mention. It was removed.
- **D.3 Assignment & weighting** — number of personas, assignment to conditions (your responsibility, all 17 conditions), reuse, weighting/matching:
  9,000 profiles: 500 in each of the 16 interventions and 1,000 in `control`, matching the per-cell
  sizes of the human half that submissions are scored against. Each profile is assigned to exactly
  one condition, by quota sampling inside that condition, so no profile is reused across arms and
  the design is between-subjects, as the study is. Every profile is queried. **No weighting of any
  kind is applied to the submitted respondents**: the file is the raw synthetic sample.

## E · Stimulus and survey administration
- **E.1 Stimulus presentation** — verbatim vs paraphrase; how state-contingent content is handled:
  Verbatim. Each respondent reads exactly one condition text, extracted unmodified from the study
  materials. Control: each control respondent reads **one** of the three neutral filler texts, drawn
  in the persona table, not all three. State-contingent content: the `Extreme weather predictions`
  arm is state-adaptive in the real study. We reproduce it — a state is drawn for each respondent,
  weighted by adult population inside that respondent's region, and the respondent then reads the
  intro that names that state and its risk category, followed by the one case text that state maps
  to. A respondent with no region gets the study's own fallback, the generic intro and case 4, which
  is what a real participant who answers "prefer not to say" is shown.
- **E.2 Survey walk-through** — one item/call vs blocks vs whole survey; context carry-over; item/option ordering & randomization; scale display; attention/comprehension handling:
  **Hybrid: blocks for the scales, one call for each single item.** 13 calls for each respondent —
  6 block calls and 7 item calls.
  *Blocks.* The 12 `trust` items, the 7 `policy_specific` items, the 6 `behavior` items, the 5
  `inst_trust` items, the 4 `policy_role` items and the 3 `concern` items are each asked on one page
  and answered in one forward pass. **Context carry-over inside a scale is the point**: the model
  sees the answers it has already written for that scale while it writes the later ones.
  *Single items.* `trust_post_1`, `distrust_1`, `funding_5`, `belief_post_1`, `policy_general_1`,
  `donation` and `newsletter` are each asked in their own prompt, with no carry-over. **These 63,000
  values are reused from the `primary` entry, not regenerated.** Each was already asked in an
  independent prompt, so its answer does not depend on the other items; re-asking would add sampling
  noise between the two entries and nothing else. Reuse makes the two entries differ by exactly one
  factor.
  **No context carry-over across scales.** A block prompt holds one scale only. Every prompt, block
  or single, restates the persona and the condition text, so each page is answered by the same
  described person reading the same stimulus and nothing else.
  Items are asked in codebook order, and inside a block in codebook order; options are not
  randomised. The scale is shown with the item, with its endpoint labels, and `funding_5` also keeps
  its labelled midpoint, because the midpoint is part of the instrument. Attention and comprehension
  items are not generated — the benchmark does not score them.
  **What this buys, and what it costs. Both are measured, and both are stated plainly.**
  Against the `primary` entry, over all 9,000 respondents (`sim/05_coherence.py`,
  `sim/out/05_coherence.txt`):

  | measure | `primary` | this entry | human reference |
  | --- | --- | --- | --- |
  | mean inter-item r, 12-item trust | 0.099 | 0.842 | ~0.525 (Cologna et al. 2025, alpha 0.93) |
  | mean inter-item r, 3-item concern | 0.098 | 0.836 | 0.907 (Voelkel et al. 2025) |
  | mean inter-item r, 6-item behavior | 0.035 | 0.372 | 0.715 (Voelkel `Intent`) |
  | SD(trust composite) / mean SD(trust item) | 0.417 | 0.926 | 0.752 (implied by alpha 0.93) |
  | mean SD of one trust item | 31.6 | 17.5 | 30 to 33 (Voelkel scales) |
  | correlation between the 6 scale means | 0.265 | 0.483 | 0.665 (Voelkel, 4 scales) |
  | answers exactly 0 or 100, 37 block items | 14.7% | 0.4% | 18.1% (Voelkel, 13 items) |
  | answers exactly 0 or 100, 5 single sliders | 15.2% | 15.2% | 18.1% (Voelkel, 13 items) |

  *The cost is real and we do not hide it.* Block prompting raises coherence past the human value on
  `trust` and leaves `behavior` short of it. It narrows each single answer — the mean item SD falls
  from 31.6 to 17.5 — so the composite spread improves by shrinking its denominator, and stays
  below the human value in absolute terms. And it nearly removes extreme answers, from 14.7 per cent
  to 0.4 per cent against a human 18.1 per cent. The 5 single sliders are unchanged at 15.2 per
  cent, which confirms that the reuse is exact.
  *Why the pair is still the useful thing.* Our two entries hold every other factor fixed and
  bracket the human coherence value from below (0.10) and above (0.84). Neither is calibrated to it,
  because the human value for these items is sealed.
- **E.3 Response elicitation** — free text / constrained choice / structured output / token log-probabilities (if logprobs: normalization & mapping):
  Two regimes, one for each format.
  *Blocks — constrained structured output, then a strict parse.* vLLM `StructuredOutputsParams`
  holds the completion to a regex of `k` numbered lines, one for each item of the scale, with each
  number in 0 to 100. `sim/03b_generate_hybrid.py::parse_block` then reads the `k` numbers in the
  order the questions were asked and accepts a block only if every number is inside its item's
  scale. The regex constrains the **shape** of the answer, never its value: every number the scale
  allows stays reachable, and sampling runs normally inside it.
  *Single items — free text, then a strict parse.* Unchanged from the `primary` entry. The model
  completes the open quote and stops at the closing quote.
  `sim/lib/answer_prompt.py::parse` takes the first number in the completion and accepts it only if
  it is inside that item's scale: 0 to 100 for the 42 sliders, 0 to 10 whole dollars for
  `donation_ams`, 0 or 1 for `newsletter_signup`.
  **No log-probabilities are used** in either regime, and no answer is interpreted or rewritten.

## F · Stochasticity and aggregation
- **F.1 Runs & seeds** — runs per respondent/item/estimate; seeds; reproducibility under identical settings:
  **One run for each respondent and page.** One block generation for each respondent and scale, one
  item generation for each respondent and single item. No repeats and no draws to average. Seeds:
  `20260830` for the block sampler, `20260828` for the single-item sampler (inherited with the
  reused answers), `20260807` for the population. The stimulus seed is stage 3's in both entries, so
  the state drawn for the state-adaptive arm is the **same person's state** in both — otherwise the
  two entries would not be comparable. Reproducibility: the population rebuilds byte for byte, and
  every prompt rebuilds byte for byte. The generations themselves are sampled at temperature 1.6
  (blocks) and 1.0 (single items), so an identical rerun on identical hardware reproduces them only
  up to the engine's own batching non-determinism. All raw generations are deposited (K.2), so no
  result depends on a rerun.
- **F.2 Aggregation rule** — how multiple generations become submitted values (mean/median/mode/first/sampled/…):
  **None, at the respondent level.** There is exactly one generation for each respondent and item, and
  it is submitted as it is. The only aggregation is the benchmark's own: `scripts/clean.R` builds the
  six composite outcomes as row means of their items, and reverse-codes
  `funding_perceptions = 100 - funding_5`. **We compute no composite in our own code.**

## G · Validation & post-processing
- **G.1 Human validation** — any human review of outputs (often N/A):
  No human read, reviewed, edited or selected any generated value. Human review was limited to the
  code and to the aggregate reports.
- **G.2 Post-processing** — parsing rules; handling of refusals/malformed/missing/out-of-range; exclusions; for approaches that generate individual responses, the resulting effective N per condition (descriptive disclosure, not a scoring input):
  Parsing as in E.3: `k` numbered lines for a block, the first number for a single item, each
  accepted only inside its item's scale. A block that does not parse, or that holds a number outside
  the scale, is **re-asked with the identical prompt**, up to five rounds. A block that still fails
  after five rounds would be filled at the scale midpoint. Nothing else is repaired, interpolated or
  imputed, and no respondent is excluded — full coverage is mandatory.
  Effective N per condition: 500 for each intervention and 1,000 for control, with no exclusions.
  **Block run, measured (`sim/out/03_report_hybrid.txt`): 54,000 of 54,000 blocks parsed on the
  first pass — 100.0 per cent. No retry round was needed and no block was filled at the midpoint.**
  That is what the regex of E.3 buys. The 63,000 reused single-item answers carry the `primary`
  entry's own parse record, which is reported in that entry's form.
- **G.3 Calibration corrections** — any post-hoc scaling/shifting/debiasing and exactly what data it was fit on (cross-ref H/I):
  **None.** No scaling, no shifting, no debiasing, no clamping, no rounding, no reweighting. The
  submitted values are the parsed generations, and the composites are the benchmark's own arithmetic
  over them. No human outcome data, from this study or any other, was used to adjust any value.

## H · Learning and conditioning components
- **H.1 Fine-tuning data** — exact corpus (hashes/DOIs), hyperparameters, checkpoints:
  N/A — no fine-tuning. The published weights are used as they are.
- **H.2 Context & retrieval corpora** — exact document set in context / indexed, archived in the deposit:
  No retrieval and no index. The entire context of every generation is the prompt described in C.1,
  built from `sim/out/00_materials.json` (from the benchmark's own `survey/` and `codebook.csv`) and
  `sim/out/01_personas.csv`. Both are in this repository. Nothing else is ever placed in context.

## I · Data inputs, blinding, and competing interests
- **I.1 Competing interests ★** — funding, in-kind compute/model access, relationships with LLM-interested entities:
  `PENDING (team declaration)` — to be completed and signed by the members named in 0.1. Facts known
  to the pipeline: the answering model is open weights, downloaded publicly and run on the team's own
  hardware; no compute, credits or model access were granted by any model provider for this
  benchmark; the one hosted model used for validation, `qwen/qwen3.8-flash` through OpenRouter
  (J.1, K.3), was paid for out of pocket at a cost below one United States dollar. Institutional affiliations are the Joint Research Centre of
  the European Commission and the University of Konstanz. Any funding source and any relationship
  with an entity with an interest in language-model performance must be listed here by the team.
- **I.2 External human data †** — all external human datasets that informed the approach anywhere (training/fine-tuning/retrieval/ICL/calibration):
  Four, and none of them contains any outcome of this study.
  1. **General Social Survey** (2018, 2021, 2022, 2024), used only to build the demographic profiles
     (D.1), reused from the organizers' own v1 clone pool.
  2. **Census CPS 2024** marginals, used only as raking targets for education and income.
  3. **Voelkel et al. (2025)**, 13,821 public individual responses from OSF. Used **only for
     validation and for selecting the design** (J.1), never placed in context and never used to fit,
     scale or shift any submitted value. It is a different study, on climate attitudes, with no
     measure of trust in climate scientists.
  4. **Ashokkumar et al. (2026)**, *LLMs can predict the results of social science experiments*,
     Code Ocean capsule 9843791. It is our method reference and our scoring reference, in three
     distinct ways, none of which puts a number into a prediction:
     a. **Method.** The prompt structure and the one-item-per-call format come from that paper. Our
        `primary` entry keeps that format; this entry departs from it for the 6 multi-item outcomes,
        and C.3 says why.
     b. **Measured effects of other studies.** The capsule's archive holds the published arm effects
        and their standard errors for 4 megastudies (`voelkel2025`, `doell2024`, `zickfeld2025`,
        `broockman2023`). These are the human targets our format search was scored against (J.1).
     c. **Scoring code.** `r_raw` and `r_adj` in J.1 are computed by the capsule's own R functions
        (`metafor::rma.mv`), not by a re-implementation, so our numbers and the paper's are the same
        quantity. The published GPT-4 value we compare against, 0.745 / 0.803 on Voelkel, is that
        paper's own result and is reproduced from the archive to four decimal places.
     **No value from the capsule enters any prediction**, and it holds no outcome of this study.
  No outcome data from this study, or from any pilot of it, informed any part of the pipeline.
- **I.3 Blinding attestation ★** — **mandatory.** Signed attestation that no team member accessed, solicited, or was shown any human outcome data from this study, including pilots, before the prediction lock:
  `PENDING (team signature)` — **this attestation must be signed by the members named in 0.1, with a
  date. It is not signed here on the team's behalf.**
  Prepared text, to be signed: *"We attest that no member of team_27 accessed, solicited, or was
  shown any human outcome data from the target megastudy, including any pilot of it, at any time
  before the prediction lock."*
  Supporting facts for the signatories: the pipeline reads only the files listed in H.2, all of which
  are benchmark materials that contain no outcome data; no network request of any kind is made during
  generation, because the model is local; and `blinding_attestation` in `metadata.json` is `true`.
- **I.4 Contamination note †** — training cutoff of every model vs public release dates of this project's materials; note any known exposure:
  `Qwen/Qwen3.8-27B` publishes no exact training cutoff at the precision this item asks for. Relevant
  exposure risk: the benchmark's own materials — the call for participation, the preregistration and
  the survey instrument — are public web pages, so a model with a later cutoff may have seen the
  **design**, including the intervention texts and the quota table. That is not an advantage on the
  outcomes, which do not exist publicly: the parent megastudy's results are unpublished and the human
  data is sealed. The stimulus texts adapt previously published material, so the model may have seen
  the source articles. No team member has any knowledge of the study's human results.

## J · Internal selection procedure
- **J.1 Design-space search †** — how the final pipeline was chosen: how many configurations tried, internal validation criterion, what data it ran against:
  **This entry's design was selected on distributional realism, not on effect recovery.** We state the
  reason, because it is unusual and it is measured.
  *What was tried.* The sibling project `modelbench`, **which is not part of this deposit (K.1)**,
  scored 8 open-weight models and 14 prompt versions on 4 megastudies from the Ashokkumar archive
  (`voelkel2025`, `doell2024`, `zickfeld2025`, `broockman2023`), covering 255 arms over 49 cells,
  against a permutation null. Model choice used the 3 climate studies (B, models 3 to 8);
  `broockman2023` was added later, for the prompt-version work only.
  Renderings tried and rejected: enriched personas, per-replicate donors, two-voice narratives, ten
  bios for each person, ten different people for each demographic slot, and exact-distribution
  reading by log-probabilities.
  *Why we did not select on effect recovery.* Over the 11 prompt versions that ran on two of those
  megastudies, the ranking they induce agrees at **r = +0.16 (p = 0.63)**, Spearman +0.20 (p = 0.56).
  The spread across versions (sd 0.042 on `voelkel2025`) is **smaller** than the spread across single
  persona draws of one version (sd 0.023 to 0.132). Choosing the best of 12 such versions would buy
  about +0.07 in correlation from luck alone. A configuration selected that way would not generalise,
  and we did not select one.
  *What we did select on.* Properties of the generator that do not depend on which study is used to
  test them: inter-item coherence, response-shape realism, and the absence of any outcome with zero
  variance. These were measured against Voelkel et al. (2025), whose respondents are public.
  *The decisions this produced.* Drop the prose persona writer (D.2, measured in v15). Do not average
  several draws for each person (B.7, measured in v16). For **this** entry, ask each multi-item scale
  as one block (C.3, E.2), at temperature 1.6 with a shape regex (B.3), and reuse the single items
  from the `primary` entry unchanged.
  *How the block format was chosen, all on public data.* v17 tested a stance-first prompt, which
  failed; then one prompt for each scale, which worked. v19 tested `top_p` 1.0 against 0.95. v20
  tested guided decoding against free decoding at temperatures 1.4 and 1.6, and showed that free
  decoding at 1.6 loses 340 of 4,000 blocks to format failure, which selects the data. Every
  criterion was inter-item coherence and response shape against Voelkel et al. (2025), whose
  respondents are public. **No megastudy outcome was seen, because none exists.**
  *Effect recovery was measured after the design was fixed, not used to choose it.* We ran both
  entries' formats on Voelkel's 11 arms and scored them with the Ashokkumar capsule's own R code
  (`metafor::rma.mv`). Mean over the 4 outcomes: `primary` r_raw 0.449 / r_adj 0.476; this entry
  r_raw 0.504 / r_adj 0.537; GPT-4, as published by Ashokkumar et al., 0.745 / 0.803. The two
  entries are the same within noise — with 10 arms a Pearson r has a 95 per cent interval of about
  [-0.46, +0.75]. **The measurement was made to check that the block format does not damage effect
  recovery, and it does not. It did not select the format.**
  *A validation probe, disclosed for completeness.* `qwen/qwen3.8-flash` answered the same 60
  respondents and 44 items through a hosted endpoint, to test whether a much larger model uses the
  persona more. It produced higher inter-item coherence (0.581 against 0.120) and an equal
  party gap (18.4 against 17.1 points), but piled 44 per cent of its answers on the scale endpoints
  and returned a constant zero for `newsletter_signup`, which is a degenerate outcome. It was not
  adopted, and it contributed no submitted value.
  *What we did not fix.* The block format leaves our respondents too coherent on `trust` (0.84
  against about 0.53), not coherent enough on `behavior` (0.37 against 0.72), narrower on every
  single answer, and almost free of extreme answers (0.4 per cent against 18.1). We disclose the
  measurements (E.2) rather than tune them away after seeing them. No value was adjusted after any
  diagnostic was read.
- **J.2 Selection blinding †** — confirm no selection used outcome data from this study:
  Confirmed. No configuration, model, prompt, rendering or sampling setting was chosen using any
  outcome data from the target study, or from any pilot of it. Every selection above used either the
  public Voelkel et al. (2025) respondents, the public Ashokkumar archive, or measurements that use
  no human data at all.

## K · Reproducibility & frozen artifacts
- **K.1 Code & materials** — link/DOI, secrets removed, determinism/seeds documented (also record the link in `metadata.json` → `code_repository`):
  **Everything that produced a submitted value is in this repository, and this repository is the
  deposit**: `population/` (the profiles) and `sim/` (the Tier-1 pipeline), with `sim/README.md` as
  the runbook. Running `population/` then `sim/` steps 00 to 04 rebuilds
  `predictions/team_27_T1_secondary-1_v1.csv` from the deposited inputs, with no other repository
  needed.
  **What is deliberately NOT in this deposit.** The measurements that CHOSE the design — the
  model comparison in B (models 3 to 8) and the v15 to v21 format search in J.1 — ran in a separate
  working project, `modelbench`, against public archives. No code or output of theirs is used by any
  step above, and no value they produced enters a prediction. They are reported here as results, and
  the deposit stands on its own without them.
  Link recorded in `metadata.json` → `code_repository`:
  <https://github.com/AndresLaverdeMarin/silicon-sample-submission-secondary-1>. This entry has its **own** repository, separate from the `primary` entry's. **No secrets, no credentials and
  no API keys** are stored in the repository; the answering model is local and needs none.
  Determinism: the population uses seed `20260807` and rebuilds byte for byte; every prompt rebuilds
  byte for byte from deposited inputs; the block sampler uses seed `20260830` and the single-item
  sampler, inherited with the reused answers, uses seed `20260828`.
- **K.2 Raw output logs †** — complete unprocessed model responses archived, hashed, time-stamped (required for Tiers 1–2, public or escrowed; Tier 3 where intermediate generations exist; oversized logs may be a separate linked Zenodo upload):
  **Public, not escrowed.** All 396,000 records are deposited unprocessed in
  `sim/out/03_replies_hybrid.jsonl`, one record for each respondent and item, each holding the raw
  completion text beside the parsed value. A block's raw completion is stored on every one of the
  items it produced, so the page the model actually wrote is recoverable. The file is too large for
  the git repository, so it is a separate Zenodo upload linked from this deposit.
  SHA-256 `2464aac12dba37a17bb1b11e42807ffaa6c07be50609826b44740decb2a32473`, 76,119,278 bytes,
  396,000 records, written 2026-08-30T08:13:40Z.
  The 63,000 reused single-item answers also stand in the `primary` entry's own log,
  `sim/out/03_replies.jsonl`, SHA-256
  `b18b26a766933b8c1a1f46726b27e486eebe7252fbbafd2800df3e370904f75e`, 70,825,249 bytes, so the reuse
  is checkable line by line.
- **K.3 Computational resources** — API-call counts, total tokens, cost, compute time:
  **No API calls and no monetary cost for any submitted value**: the answering model runs on the
  team's own H100.
  *This entry's own run, measured (`sim/out/03_report_hybrid.txt`, `sim/out/run_entryB.log`).*
  54,000 block generations covering 333,000 of the 396,000 submitted values. Wall clock **115.8
  minutes**, of which 114.2 minutes is generation; **7.9 block prompts for each second**. Engine
  start-up about 1.6 minutes. Sustained throughput 7,568 input tokens and 303 output tokens for each
  second, so about **51.8 million input tokens and 2.07 million output tokens**. Zero retries, so no
  generation was spent twice.
  *Carried in from the `primary` run.* 63,000 single-item generations, already counted in that
  entry's form. This entry regenerated none of them.
  *Validation cost outside the submission.* One hosted model was used, `qwen/qwen3.8-flash` through
  OpenRouter (provider: Alibaba Cloud Int.), `/api/v1/chat/completions`, thinking disabled,
  `temperature` 1.0 / 0.7 / 0.3, `top_p` 0.95, `max_tokens` 16, call window 2026-08-29. It answered a
  60-respondent, 44-item probe in the control condition. **Total spend under one United States
  dollar, and no value it produced reaches the deposited answers.** Local compute: about 5 hours of
  the same H100 for the v15 to v21 measurements, of which 38 minutes was the v21 effect-recovery run
  on Voelkel reported in J.1.

## L · Disclosure class
Each item above is deposited as **public**, **escrowed** (sealed from the public but available to the
core team and auditors under confidentiality, with a public SHA-256 hash + timestamp so the lock is
still verifiable — an embargo with a sunset date is encouraged), or **withheld** (permitted only for
items marked neither ★ nor †). Your entry's class is set by its **most restricted item** and recorded
in `metadata.json` → `disclosure_class` (and `escrow_doi` if anything is escrowed):
- **A · Open** — all items public. Full results-table standing; all features enter the design-choice analysis.
- **B · Escrowed** — some items sealed but every item is available to the core team/auditors under confidentiality. Full standing with an *escrowed* badge; only publicly disclosed features enter the design-choice analysis.
- **C · Sealed** — one or more permitted items withheld even from escrow. Scored and reported with a *not independently verifiable* flag; excluded from the approach catalogue and design-choice analysis.

**This entry is class A · Open.** Every item above is public, including the † items: the prompt
builder, all 396,000 raw generations, the design-space search, the population code and the profile
pool itself. Nothing is escrowed and nothing is withheld, so `escrow_doi` in `metadata.json` is
`null`. No part of the pipeline is proprietary. The one artifact not inside the git repository is
the raw generation log, which is too large for git and is deposited to Zenodo separately (K.2).

★ items must always be public (never escrowed or withheld); † items must be at minimum escrowed. Full
policy: <https://janpfander.github.io/llm_predictions_megastudy/#disclosure>
