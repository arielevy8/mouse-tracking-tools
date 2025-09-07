#!/usr/bin/env python3
"""
Batch-process CSVs to add:
  • choice_rank_string  (global popularity ranks with counts; includes items never chosen → count 0)
  • choice_is_higher_ranked  (True if chosen item has higher count; False on ties; NA if practice/no choice)
  • choice_is_one_more       ((chosen_count - 1) == other_count; NA if practice/no choice)
  • total_one_more_true      (same value in every row; counts True in choice_is_one_more)

Edit DATA_DIR and PRACTICE_TRIALS, then run:  python rank_csv_batch.py
Required columns (case-sensitive):  Left_option  Right_option  choice
"""

from pathlib import Path
import pandas as pd
import numpy as np

# ------------------------------------------------------------ CONFIGURATION
DATA_DIR         = Path(r"THE/PATH/TO/YOUR/FOLDER")   # folder with input CSVs
PRACTICE_TRIALS  = 2                                # skip first N non-blank 'choice' rows
OUTPUT_SUBDIR    = "ranked"                         # sub-folder for outputs
# ---------------------------------------------------------------------------


def build_rank_info(df: pd.DataFrame, practice_rows):
    """
    Build the popularity ranking *excluding* practice rows and using the union
    of Left_option + Right_option (non-practice only) as the universe of items.
    Every item in that universe appears in the rank string; if never chosen,
    its count is 0.

    Returns
    -------
    rank_string   : str   e.g. '1: apple (12), 2: grape (0), 3: orange (10)'
    rank_lookup   : dict  item -> numeric rank (1 = best)
    choice_counts : dict  item -> chosen count (practice rows excluded)
    """
    # Non-practice subset
    non_pr_df = df.drop(index=practice_rows)

    # Universe from Left/Right (non-practice only)
    universe = (
        pd.concat([non_pr_df["Left_option"], non_pr_df["Right_option"]])
          .dropna()
          .unique()
    )

    # Counts from 'choice' (non-practice only), reindexed so every shown item appears
    choice_counts_series = (
        non_pr_df["choice"]
        .value_counts()
        .reindex(universe, fill_value=0)
    )

    # Random tie-break for equal counts
    counts_df = choice_counts_series.to_frame("count")
    counts_df["rand"] = np.random.rand(len(counts_df))
    ranked_items = (
        counts_df.sort_values(["count", "rand"], ascending=[False, True])
                 .index
                 .tolist()
    )

    # Rank string with counts (zeros included)
    rank_string = ", ".join(
        f"{i+1}: {item} ({int(choice_counts_series[item])})"
        for i, item in enumerate(ranked_items)
    )

    rank_lookup   = {item: i + 1 for i, item in enumerate(ranked_items)}
    choice_counts = choice_counts_series.to_dict()

    return rank_string, rank_lookup, choice_counts


def numeric_rank(item, lookup):
    """Return numeric rank; unseen → worst + 1 (safety fallback)."""
    return lookup.get(item, len(lookup) + 1)


def process_csv(csv_path: Path, out_dir: Path):
    df = pd.read_csv(csv_path)

    # Identify practice rows (first N non-blank 'choice' rows)
    nb_idx = df.index[df["choice"].notna() & (df["choice"] != "")]
    practice_rows = nb_idx[:PRACTICE_TRIALS] if PRACTICE_TRIALS else []

    # Build ranking info (practice excluded; universe from Left/Right)
    rank_string, rank_lookup, choice_counts = build_rank_info(df, practice_rows)
    df["choice_rank_string"] = rank_string  # identical in every row

    # ------------------------------------------------ choice_is_higher_ranked (counts-based; False on ties)
    def higher_ranked(row):
        """
        True if chosen item has strictly higher count than the other option.
        False if counts tie or chosen item is lower.
        NA for practice rows or blank choice.
        """
        if row.name in practice_rows:
            return pd.NA
        ch = row["choice"]
        if pd.isna(ch) or ch == "":
            return pd.NA

        l_item = row["Left_option"]
        r_item = row["Right_option"]

        l_cnt = choice_counts.get(l_item, 0)
        r_cnt = choice_counts.get(r_item, 0)

        if l_cnt == r_cnt:
            return False

        higher_item = l_item if l_cnt > r_cnt else r_item
        return higher_item == ch

    df["choice_is_higher_ranked"] = df.apply(higher_ranked, axis=1)

    # ------------------------------------------------ choice_is_one_more ((chosen_count - 1) == other_count)
    def one_more(row):
        if row.name in practice_rows:
            return pd.NA
        ch = row["choice"]
        if pd.isna(ch) or ch == "":
            return pd.NA

        if ch == row["Left_option"]:
            other = row["Right_option"]
        elif ch == row["Right_option"]:
            other = row["Left_option"]
        else:
            return False  # data mismatch

        chosen_total = choice_counts.get(ch, 0)
        other_total  = choice_counts.get(other, 0)

        return (chosen_total - 1) == other_total

    df["choice_is_one_more"] = df.apply(one_more, axis=1)

    # ------------------------------------------------ total_one_more_true (constant)
    total_true = int(df["choice_is_one_more"].sum(skipna=True))
    df["total_one_more_true"] = total_true

    # ------------------------------------------------ save
    out_path = out_dir / f"{csv_path.stem}_ranked.csv"
    df.to_csv(out_path, index=False)
    print(f"✔ {csv_path.name} → {out_path.relative_to(DATA_DIR)}")


if __name__ == "__main__":
    if not DATA_DIR.is_dir():
        raise SystemExit(f"[!] DATA_DIR not found: {DATA_DIR}")

    csv_files = sorted(DATA_DIR.glob("*.csv"))
    if not csv_files:
        raise SystemExit(f"[!] No CSV files in {DATA_DIR}")

    out_dir = DATA_DIR / OUTPUT_SUBDIR
    out_dir.mkdir(exist_ok=True)

    for csv in csv_files:
        process_csv(csv, out_dir)
