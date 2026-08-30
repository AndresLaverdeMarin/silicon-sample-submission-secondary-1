#!/usr/bin/env python3
"""
Stage 5 — COHERENCE. Do one person's answers to one scale hang together?

WHY THIS IS THE TEST THAT MATTERS

Three of the seven scored Tier-1 analyses are distributional. They compare the
SHAPE of our answers with the humans'. A composite (for example
`trust_multidimensional`, the mean of 12 trust items) is only as wide as its
items are correlated:

    SD(composite) / mean SD(item) = sqrt((1 + (k - 1) r) / k)

With k = 12 items and mean inter-item correlation r = 0.10, that ratio is
0.35. With r = 0.53, it is 0.75. So a low r collapses the composite spread,
and the distributional metrics see a panel that is far too narrow.

WHAT IT REPORTS, FOR EACH MULTI-ITEM SCALE

    mean r        the average correlation between two items of one scale,
                  taken across people. It does not depend on the item count,
                  so it can be compared between scales of different length.
    alpha         Cronbach alpha. The same information, scaled by k.
    item SD       the mean standard deviation of one item, across people.
    comp SD       the standard deviation of the scale mean.
    ratio         comp SD / item SD. What the composite spread costs.

HUMAN ANCHORS

The megastudy outcomes are sealed, so no human value for THESE items exists.
Two public anchors are used, and both are named in the output:

  * Voelkel et al. (2025), 13,821 public respondents, four climate scales.
    Read from `ashokkumar_bench/data/osf/deidentified.csv`. `Belief_Post_3_1`
    is reverse coded there, so it is flipped first.
  * Cologna et al. (2025) report alpha = 0.93 on the same 12-item trust
    scale this megastudy uses. Spearman-Brown gives the mean r that implies.

    .venv-vllm/bin/python sim/05_coherence.py

**Written in ASD-STE100 Simplified Technical English.**
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from lib import spec                                       # noqa: E402

ENTRY_A = Path("/home/jovyan/silicon-sample-submission/raw_data_deposit/"
               "tier1_raw_export.csv")
ENTRY_B = HERE.parent / "raw_data_deposit" / "tier1_raw_export_hybrid.csv"
HUMAN = Path("/home/jovyan/LLMmegastudy/ashokkumar_bench/data/osf/"
             "deidentified.csv")
REPORT = HERE / "out" / "05_coherence.txt"

# The 6 multi-item scales the hybrid asks as BLOCKS.
SCALES = {
    "trust": spec.TRUST_ITEMS,
    "policy_specific": spec.POLICY_SPECIFIC_ITEMS,
    "behavior": spec.BEHAVIOR_ITEMS,
    "inst_trust": spec.INST_TRUST_ITEMS,
    "policy_role": spec.POLICY_ROLE_ITEMS,
    "concern": spec.CONCERN_ITEMS,
}
# The 7 single-item outcomes. Entry B REUSES Entry A for these, unchanged.
SINGLES = ["trust_post_1", "distrust_1", "funding_5", "belief_post_1",
           "policy_general_1", "donation", "newsletter"]

# Public human scales, and the megastudy scale each one speaks to.
VOELKEL = {
    "Belief_Post": ["Belief_Post_1_1", "Belief_Post_2_1", "Belief_Post_3_1"],
    "Concern_Post": ["Concern_Post_1_1", "Concern_Post_2_1",
                     "Concern_Post_3_1"],
    "Policies_Post": ["Policies_Post_1", "Policies_Post_2", "Policies_Post_3"],
    "Intent_Post": [f"Intent_Post_{i}" for i in range(1, 5)],
}
NEAREST = {"concern": "Concern_Post", "policy_specific": "Policies_Post",
           "policy_role": "Policies_Post", "behavior": "Intent_Post"}
REVERSE = {"Belief_Post_3_1"}
COLOGNA_ALPHA = 0.93            # 12-item trust scale, Cologna et al. 2025


def stats(X: pd.DataFrame) -> dict:
    k = X.shape[1]
    alpha = k / (k - 1) * (1 - X.var(ddof=1).sum() / X.sum(axis=1).var(ddof=1))
    r = X.corr().values[np.triu_indices(k, 1)].mean()
    isd, csd = X.std().mean(), X.mean(axis=1).std()
    return {"k": k, "n": len(X), "alpha": alpha, "r": r, "item_sd": isd,
            "comp_sd": csd, "ratio": csd / isd}


def spearman_brown_r(alpha: float, k: int) -> float:
    """The mean inter-item r that an alpha of `alpha` on `k` items implies."""
    return alpha / (k - alpha * (k - 1))


def human_interval(X: pd.DataFrame, n: int, draws: int = 200,
                   seed: int = 20260830) -> dict:
    """What a HUMAN sample of `n` people gives, 2.5th to 97.5th percentile.

    Every statistic measured on a sample wobbles with who was asked. A number
    is only different from the humans if it falls outside this interval.
    """
    rng = np.random.default_rng(seed)
    A = X.to_numpy(dtype="float64")
    k = A.shape[1]
    n = min(n, len(A))
    rs, isd, csd, rat = [], [], [], []
    for _ in range(draws):
        S = A[rng.choice(len(A), n, replace=False)]
        rs.append(np.corrcoef(S, rowvar=False)[np.triu_indices(k, 1)].mean())
        isd.append(S.std(axis=0, ddof=1).mean())
        csd.append(S.mean(axis=1).std(ddof=1))
        rat.append(csd[-1] / isd[-1])
    return {key: (float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5)))
            for key, v in (("r", rs), ("item_sd", isd), ("comp_sd", csd),
                           ("ratio", rat))}


def extreme_share(frame: pd.DataFrame, items: list[str]) -> float:
    v = frame[items].to_numpy(dtype="float64").ravel()
    return float(np.mean((v == 0) | (v == 100)))


def main() -> None:
    for p in (ENTRY_A, ENTRY_B, HUMAN):
        if not p.exists():
            raise SystemExit(f"missing {p}")
    A = pd.read_csv(ENTRY_A)
    B = pd.read_csv(ENTRY_B)
    h = pd.read_csv(HUMAN, low_memory=False)

    hstat, hband = {}, {}
    for name, cols in VOELKEL.items():
        H = h[cols].apply(pd.to_numeric, errors="coerce").dropna()
        for c in cols:
            if c in REVERSE:
                H[c] = 100 - H[c]
        hstat[name] = stats(H)
        hband[name] = human_interval(H, 1000)
    human_extreme = extreme_share(
        h[sum(VOELKEL.values(), [])].apply(pd.to_numeric, errors="coerce")
         .dropna(), sum(VOELKEL.values(), []))

    L = ["=" * 78,
         "STAGE 5 — COHERENCE, ENTRY A (item mode) AGAINST ENTRY B (hybrid)",
         "=" * 78, "",
         f"entry A  {ENTRY_A}",
         f"entry B  {ENTRY_B}",
         "",
         "Entry A asks all 44 items in 44 independent prompts.",
         "Entry B asks the 6 multi-item scales as BLOCKS, one prompt for one",
         "scale, and REUSES Entry A unchanged for the 7 single items.",
         ""]

    for pop, frames in (("control only", {k: v[v.condition == "control"]
                                          for k, v in (("A", A), ("B", B))}),
                        ("all 17 conditions", {"A": A, "B": B})):
        L += ["-" * 78,
              f"{pop.upper()}   n = {len(frames['A']):,} respondents",
              "-" * 78,
              f"{'scale':16s} {'entry':6s} {'k':>2s} {'alpha':>6s} "
              f"{'mean r':>7s} {'itemSD':>7s} {'compSD':>7s} {'ratio':>6s}",
              "-" * 78]
        for name, cols in SCALES.items():
            for tag, frame in frames.items():
                s = stats(frame[cols].dropna())
                L.append(f"{name:16s} {tag:6s} {s['k']:2d} {s['alpha']:6.3f} "
                         f"{s['r']:7.3f} {s['item_sd']:7.1f} "
                         f"{s['comp_sd']:7.1f} {s['ratio']:6.3f}")
            if name == "trust":
                r = spearman_brown_r(COLOGNA_ALPHA, len(cols))
                L.append(f"{'':16s} {'human':6s} {len(cols):2d} "
                         f"{COLOGNA_ALPHA:6.3f} {r:7.3f} {'':7s} {'':7s} "
                         f"{np.sqrt((1 + (len(cols) - 1) * r) / len(cols)):6.3f}"
                         "   Cologna et al. 2025, same 12-item scale")
            elif name in NEAREST:
                v = NEAREST[name]
                s = hstat[v]
                b = hband[v]
                L.append(f"{'':16s} {'human':6s} {s['k']:2d} "
                         f"{s['alpha']:6.3f} {s['r']:7.3f} "
                         f"{s['item_sd']:7.1f} {s['comp_sd']:7.1f} "
                         f"{s['ratio']:6.3f}   Voelkel {v}, "
                         f"r 95% [{b['r'][0]:.2f},{b['r'][1]:.2f}]")
            L.append("")

    # ------------------------------------------------------- overshoot --
    L += ["-" * 78,
          "OVERSHOOT GUARD — correlation BETWEEN the 6 scale means.",
          "Block prompting must make each scale coherent, not make all 37",
          "items one thing. The human value is for Voelkel's 4 scales.",
          "-" * 78]
    for tag, frame in (("entry A", A), ("entry B", B)):
        comp = pd.DataFrame({k: frame[v].mean(axis=1)
                             for k, v in SCALES.items()})
        cr = comp.corr().values[np.triu_indices(len(SCALES), 1)]
        L.append(f"  {tag:8s} mean r between the 6 scale means: {cr.mean():.3f}")
    hc = pd.DataFrame()
    for name, cols in VOELKEL.items():
        X = h[cols].apply(pd.to_numeric, errors="coerce")
        for c in cols:
            if c in REVERSE:
                X[c] = 100 - X[c]
        hc[name] = X.mean(axis=1)
    hc = hc.dropna()
    L.append(f"  {'human':8s} mean r between Voelkel's 4 scale means: "
             f"{hc.corr().values[np.triu_indices(4, 1)].mean():.3f}"
             f"   (n = {len(hc):,})")

    # --------------------------------------------------------- extremes --
    L += ["", "-" * 78,
          "EXTREME ANSWERS — share exactly 0 or exactly 100",
          "Block prompting drives these down. The 7 single items are reused",
          "from Entry A, so their share must be IDENTICAL in the two entries.",
          "-" * 78]
    block_items = sum(SCALES.values(), [])
    single_sliders = [i for i in SINGLES if i in spec.SLIDER_ITEMS]
    for tag, frame in (("entry A", A), ("entry B", B)):
        L.append(f"  {tag:8s} 37 block items {extreme_share(frame, block_items):6.1%}"
                 f"     5 single sliders {extreme_share(frame, single_sliders):6.1%}")
    L.append(f"  {'human':8s} Voelkel, 13 items {human_extreme:6.1%}")

    L += ["", "=" * 78,
          "READ IT LIKE THIS",
          "  Entry B is doing its job if mean r rises from Entry A toward the",
          "  human value ON THE SAME KIND OF SCALE, the composite ratio rises",
          "  with it, the overshoot guard stays near the human number, and",
          "  the single-item extreme share is unchanged.",
          "=" * 78, ""]

    text = "\n".join(L)
    print(text)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(text)
    print(f"wrote {REPORT}")


if __name__ == "__main__":
    main()
