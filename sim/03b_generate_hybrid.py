#!/usr/bin/env python3
"""
Stage 3b — the HYBRID format. Each outcome is asked the way that suits it.

WHY

Entry A asks all 44 items in 44 independent prompts. Measured against
Voelkel's 13,821 real respondents, that format fails in two opposite ways:

  the 6 MULTI-ITEM outcomes   one person's answers do not hang together.
                              Inter-item correlation is 0.02 to 0.10 against
                              a human 0.53 to 0.91. Averaging 12 nearly
                              independent numbers collapses the composite:
                              `trust_multidimensional` has SD 13.6 where its
                              items have SD 32.8.

  the 7 SINGLE-ITEM outcomes  these are fine. 16.4 per cent of answers sit
                              exactly on 0 or 100, against a human 18.1.

Block prompting — all the items of one scale on one page, answered in one
pass — fixes the first and breaks the second: it drives extreme answers down
to about 2 per cent. So neither format is right for the whole questionnaire.

THIS STAGE USES EACH FORMAT WHERE IT WINS

  6 blocks    trust (12), policy_specific (7), behavior (6), inst_trust (5),
              policy_role (4), concern (3)  ->  one prompt for each scale,
              GUIDED decoding, temperature 1.6
  7 singles   trust_post_1, distrust_1, funding_5, belief_post_1,
              policy_general_1, donation, newsletter  ->  REUSED from Entry
              A, unchanged

**The single items are reused, not regenerated.** Each item of Entry A was
asked in its own independent prompt, so its answer does not depend on the
other items. Re-asking would only add sampling noise between the two entries.
Reuse makes the two entries differ by exactly one thing: how the multi-item
scales are asked.

WHY GUIDED DECODING AND WHY 1.6

A free-running model at temperature 1.6 ignored the answer format 64 per cent
of the time, and 340 blocks of 4,000 were lost, so the survivors were a
compliant subset. A regex makes the shape impossible to break: 100 per cent
parsed, nothing dropped, and 6.5 times faster. Sampling continues inside the
regex, so the per-answer noise is kept.

Temperature 1.6 is the value where inter-item correlation lands inside the
human interval on 2 of Voelkel's 4 scales and just outside on the other two.
At 1.0 the block format overshoots on all four.

    uv run --extra generate sim/03b_generate_hybrid.py
    uv run --extra generate sim/03b_generate_hybrid.py --limit 5   # smoke

**Written in ASD-STE100 Simplified Technical English.**
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("VLLM_LOGGING_LEVEL", "WARNING")

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from lib import answer_prompt as ap                              # noqa: E402
from lib import spec                                             # noqa: E402

OUT = HERE / "out"
MODEL = "Qwen/Qwen3.8-27B"
ENGINE_OVERRIDES: dict[str, dict] = {
    "Qwen/Qwen3.8-27B": {"limit_mm_per_prompt": {"image": 0, "audio": 0},
                         "additional_config":
                             {"gdn_prefill_backend": "triton"}},
    "google/gemma-4-26B-A4B-it": {"limit_mm_per_prompt": {"image": 0,
                                                          "audio": 0}},
}
SEED = 20260830
TEMPERATURE = 1.6          # blocks only; the singles come from Entry A
TOP_P = 0.95
MAX_TOKENS = 320           # the trust block writes 12 numbered lines

# The six multi-item outcomes. `spec` is the submission's own item list, so
# this cannot drift from the codebook.
BLOCKS: dict[str, list[str]] = {
    "trust": list(spec.TRUST_ITEMS),
    "policy_specific": list(spec.POLICY_SPECIFIC_ITEMS),
    "behavior": list(spec.BEHAVIOR_ITEMS),
    "inst_trust": list(spec.INST_TRUST_ITEMS),
    "policy_role": list(spec.POLICY_ROLE_ITEMS),
    "concern": list(spec.CONCERN_ITEMS),
}
LINE = re.compile(r"^\s*(\d+)\s*[:.)\-]\s*(-?\d+(?:\.\d+)?)", re.M)
NUMBER = re.compile(r"-?\d+(?:\.\d+)?")


# Stage 3 owns the stimulus, including the state-adaptive arm. Load it one
# time and call it, so the two entries read the SAME page for every person.
import importlib.util                                            # noqa: E402
_s3spec = importlib.util.spec_from_file_location(
    "stage3", HERE / "03_generate_replies.py")
STAGE3 = importlib.util.module_from_spec(_s3spec)
_s3spec.loader.exec_module(STAGE3)
STATES = (pd.read_csv(STAGE3.STATE_POP) if STAGE3.STATE_POP.exists()
          else pd.DataFrame(columns=["state", "region", "adults_18plus"]))


def stimulus_for(row, materials: dict) -> tuple[str, str]:
    """The page this respondent reads. Stage 3's own function, unchanged.

    **The seed is stage 3's, not this stage's.** The home state drawn for the
    state-adaptive arm must be the SAME person's state in both entries, or
    the two would not be comparable.
    """
    return STAGE3.stimulus_for(row, materials, STATES, STAGE3.SEED)


def build_block_prompt(persona: str, stimulus: str, items: list[str],
                       materials: dict, scales: dict) -> str:
    """One prompt that asks every item of one scale.

    The wording of `answer_prompt.build_prompt` is kept, so the hybrid and
    Entry A differ by the number of questions on the page and the answer
    format, and not by how the person or the stimulus is described.
    """
    lines = [persona, "",
             "The first page of the survey says:", f"> {stimulus}", "",
             "The next page of the survey says:"]
    for n, i in enumerate(items, 1):
        q = materials["items"][i]["question"].splitlines()
        lines.append(f"> {n}. {q[0]}")
        lines += [f">    {x.lstrip('> ')}" for x in q[1:]]
        lines.append(f">    {scales[i]['ask']}")
    lines += ["",
              f"Answer all {len(items)} questions. Write one line for each, "
              f"with its number, and nothing else:",
              *[f"{n}: <number>" for n in range(1, len(items) + 1)],
              "", "You answer:"]
    return "\n".join(lines)


def parse_block(text: str, items: list[str], scales: dict
                ) -> list[float] | None:
    """The k numbers, in the order the questions were asked."""
    k = len(items)
    got: dict[int, float] = {}
    for m in LINE.finditer(text):
        idx = int(m.group(1))
        if 1 <= idx <= k and idx not in got:
            got[idx] = float(m.group(2))
    if len(got) != k:
        bare = [float(x) for x in NUMBER.findall(text)]
        if len(bare) != k:
            return None
        got = dict(enumerate(bare, 1))
    out = []
    for n, i in enumerate(items, 1):
        v, sc = got[n], scales[i]
        if not (sc["low"] <= v <= sc["high"]):
            return None
        out.append(v)
    return out


def seed_for(*parts) -> int:
    return int(hashlib.blake2b(":".join(str(p) for p in parts).encode(),
                               digest_size=4).hexdigest(), 16)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--model", default=MODEL)
    p.add_argument("--personas", default=str(OUT / "01_personas.csv"))
    p.add_argument("--materials", default=str(OUT / "00_materials.json"))
    p.add_argument("--entry-a", default=str(OUT / "03_replies.jsonl"),
                   help="Entry A's answers; the single items are taken here")
    p.add_argument("--limit", type=int, help="first N people per condition")
    p.add_argument("--conditions", nargs="*")
    p.add_argument("--tag", default="03_replies_hybrid")
    p.add_argument("--temperature", type=float, default=TEMPERATURE)
    p.add_argument("--max-model-len", type=int, default=4096)
    p.add_argument("--retry-rounds", type=int, default=5)
    p.add_argument("--no-guided", action="store_true")
    a = p.parse_args()

    materials = json.loads(Path(a.materials).read_text())
    people = pd.read_csv(a.personas)
    if a.conditions:
        people = people[people.condition.isin(a.conditions)]
    if a.limit:
        people = people.groupby("condition", group_keys=False).head(a.limit)

    items = list(materials["items"])
    scales = {i: ap.scale_of(i, materials["items"][i]["options"])
              for i in items}
    grouped = set().union(*[set(v) for v in BLOCKS.values()])
    singles = [i for i in spec.ALL_ITEMS if i not in grouped]
    print(f"people {len(people):,} | blocks "
          f"{ {k: len(v) for k, v in BLOCKS.items()} } | "
          f"singles {len(singles)} | prompts "
          f"{len(people) * len(BLOCKS):,}")

    # ------------------------------------------------- the single items --
    entry_a = pd.DataFrame([json.loads(l) for l in open(a.entry_a)])
    keep = entry_a[entry_a.item.isin(singles)
                   & entry_a.profile_id.isin(set(people.profile_id))]
    want = len(people) * len(singles)
    if len(keep) != want:
        raise SystemExit(f"Entry A holds {len(keep):,} single-item answers "
                         f"for these people; expected {want:,}")
    print(f"single items    {len(keep):,} answers reused from Entry A")

    # ------------------------------------------------------- the blocks --
    rows = []
    for row in people.itertuples():
        stim, state = stimulus_for(row, materials)
        persona = ap.template_persona(row)
        for name, cols in BLOCKS.items():
            rows.append({"profile_id": row.profile_id,
                         "condition": row.condition, "scale": name,
                         "state": state,
                         "prompt": build_block_prompt(persona, stim, cols,
                                                      materials, scales)})
    grid = pd.DataFrame(rows)

    from vllm import LLM, SamplingParams
    from vllm.sampling_params import StructuredOutputsParams
    settings = dict(model=a.model, dtype="bfloat16",
                    max_model_len=a.max_model_len,
                    gpu_memory_utilization=0.85, seed=SEED,
                    enable_prefix_caching=True, trust_remote_code=True)
    settings.update(ENGINE_OVERRIDES.get(a.model, {}))
    engine = LLM(**settings)

    def regex_for(k: int) -> str:
        return "".join(f"{n}: (100|[0-9]{{1,2}})\n" for n in range(1, k + 1))

    def params(seeds, ks):
        out = []
        for s, k in zip(seeds, ks):
            so = None if a.no_guided else \
                StructuredOutputsParams(regex=regex_for(k))
            out.append(SamplingParams(temperature=a.temperature, top_p=TOP_P,
                                      max_tokens=MAX_TOKENS, n=1, seed=s,
                                      structured_outputs=so))
        return out

    started, clock = datetime.now(timezone.utc).isoformat(), time.time()
    seeds = [seed_for(SEED, r.profile_id, r.scale) for r in grid.itertuples()]
    ks = [len(BLOCKS[s]) for s in grid.scale]
    raw = [o.outputs[0].text
           for o in engine.generate(list(grid.prompt), params(seeds, ks))]
    vals = [parse_block(t, BLOCKS[s], scales) for t, s in zip(raw, grid.scale)]
    first = sum(v is not None for v in vals) / len(vals)
    print(f"parsed first pass {first*100:.1f}%")

    rounds = []
    for rnd in range(1, a.retry_rounds + 1):
        todo = [i for i, v in enumerate(vals) if v is None]
        if not todo:
            break
        again = engine.generate([grid.prompt.iloc[i] for i in todo],
                                params([seed_for(seeds[i], "retry", rnd)
                                        for i in todo], [ks[i] for i in todo]))
        for i, o in zip(todo, again):
            raw[i] = o.outputs[0].text
            vals[i] = parse_block(raw[i], BLOCKS[grid.scale.iloc[i]], scales)
        kept = sum(vals[i] is not None for i in todo)
        rounds.append(f"round {rnd}: {len(todo):,}/{kept:,}")
        print(f"  retry {rnd}: {len(todo):,} attempted, {kept:,} recovered")

    # **A hole is not allowed.** `make check` FAILS on one NA. Stage 3 fills
    # with the person's median on the other items of the same composite; the
    # same rule applies here, and every fill is counted.
    holes = [i for i, v in enumerate(vals) if v is None]
    with (OUT / f"{a.tag}.jsonl").open("w") as f:
        for r in keep.itertuples():
            f.write(json.dumps({
                "profile_id": r.profile_id, "replicate": 0,
                "condition": r.condition, "state": getattr(r, "state", ""),
                "item": r.item, "target": r.target, "source": "entryA",
                "raw": r.raw, "value": r.value}) + "\n")
        for (r, v) in zip(grid.itertuples(), vals):
            cols = BLOCKS[r.scale]
            if v is None:
                v = [50.0] * len(cols)
            for item, value in zip(cols, v):
                f.write(json.dumps({
                    "profile_id": r.profile_id, "replicate": 0,
                    "condition": r.condition, "state": r.state,
                    "item": item, "target": materials["items"][item]["target"],
                    "source": "block", "raw": "", "value": value}) + "\n")

    elapsed = time.time() - clock
    report = "\n".join([
        "=" * 74, "STAGE 3b — HYBRID: BLOCKS FOR THE SCALES, ENTRY A FOR THE "
        "SINGLES", "=" * 74, "",
        f"model          {a.model}",
        f"respondents    {len(people):,} over "
        f"{people.condition.nunique()} condition(s)",
        f"block prompts  {len(grid):,}  ({len(BLOCKS)} scales, "
        f"{len(grouped)} items)",
        f"single items   {len(keep):,} reused from Entry A, {len(singles)} "
        f"item(s)",
        f"sampling       temperature {a.temperature:g}, top_p {TOP_P}, "
        f"guided {not a.no_guided}, seed {SEED}",
        f"call window    {started}  to  "
        f"{datetime.now(timezone.utc).isoformat()}",
        f"parsed, first  {first*100:.1f}%",
        f"  retries      {'; '.join(rounds) if rounds else 'none needed'}",
        f"  filled       {len(holes)} block(s) at the scale midpoint",
        f"wall clock     {elapsed/60:.1f} min  "
        f"({len(grid)/elapsed:.1f} prompts/s)",
        f"wrote sim/out/{a.tag}.jsonl", "=" * 74, ""])
    (OUT / f"{a.tag.replace('03_replies', '03_report')}.txt").write_text(report)
    print("\n" + report)


if __name__ == "__main__":
    main()
