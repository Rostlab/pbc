#!/usr/bin/env python3
"""
Compile membrane dataset from CV FASTA splits into a single biotrainer-style FASTA.

Input data layout (existing in repo):
  supervised/membrane/data/cv/cv_00_a.fasta
  supervised/membrane/data/cv/cv_01_a.fasta
  supervised/membrane/data/cv/cv_02_a.fasta
  supervised/membrane/data/cv/cv_03_a.fasta
  supervised/membrane/data/cv/cv_04_a.fasta

Each file is expected to contain repeating 3-line records:
  >HEADER (e.g., ">P22619|NEGATIVE|TAT|0")
  SEQUENCE
  TARGET_ANNOTATION (same length as SEQUENCE)

Compilation logic:
  - CV fold 0 → Test set (SET=test)
  - CV folds 1–4 pooled → Train pool; from this pool, create a random validation split (SET=val)
    and keep the remaining as training (SET=train).

Output format (biotrainer-style, similar to supervised/conservation/conservation.fasta):
  >{ID} TARGET={TARGET_ANNOTATION} SET={train|val|test}
  {SEQUENCE}

By default writes to: supervised/membrane/data/datasets/membrane.fasta

Usage examples:
  python compile_membrane_dataset.py
  python compile_membrane_dataset.py --val-fraction 0.1 --seed 1337 \
      --out ../data/datasets/membrane.fasta
"""
from __future__ import annotations

import numpy as np
from pathlib import Path
from typing import Dict, List
from collections import namedtuple
from sklearn.model_selection import train_test_split

_Record = namedtuple("_Record", ["seq_id", "seq", "target", "mask", "set"])


def _map_target(target: str):
    target_map = {"B": "B",
                  "b": "B",
                  "H": "H",
                  "h": "H",
                  "S": "S",
                  "U": "N",
                  "1": "N",
                  "2": "N"}
    return "".join([target_map[t] for t in target])


def read_cv_fasta(path: Path) -> List[_Record]:
    """Read a 3-line-per-record FASTA with sequence and annotation.

    Returns list of tuples: (id, seq, target)
    """
    records: List[_Record] = []
    seq_ids = []
    with path.open("r") as f:
        lines = [line.rstrip("\n") for line in f]

    i = 0
    n = len(lines)
    while i < n:
        # skip blank lines just in case
        if not lines[i]:
            i += 1
            continue
        if not lines[i].startswith(">"):
            raise ValueError(f"Expected header starting with '>' in {path} at line {i + 1}")
        header = lines[i][1:].strip()
        if i + 2 >= n:
            raise ValueError(f"Incomplete record at end of file {path}, starting at line {i + 1}")
        seq = lines[i + 1].strip()
        target = lines[i + 2].strip()
        mask = "".join(["0" if res == "U" else "1" for res in target])
        mapped_target = _map_target(target)
        # derive a compact ID: take up to first whitespace in header
        # then, if '|' present, keep the first token before whitespace as the ID
        id_token = header.split()[0]
        seq_id = id_token  # keep full token (often Accession|...|...|fold)
        seq_ids.append(seq_id)
        records.append(_Record(seq_id, seq, mapped_target, mask, "train"))
        i += 3
    assert len(seq_ids) == len(set(seq_ids))
    return records


def read_blacklist():
    ids = set()
    with open("data/predictions/blacklist.txt", "r") as f:
        lines = f.readlines()
        for line in lines:
            ids.add(line[1:].strip())
    assert len(ids) == 235
    return ids


def split_membrane_train_val_stratified(dedup_train_pool: list[_Record], seed: int, train_ids, val_fraction: float):
    # Stratified Split train/validation based on membrane residue ratio per sequence
    # Define helper to compute membrane ratio (B/H/S counted) among unmasked positions
    def membrane_ratio(record: _Record) -> float:
        mem = 0
        total = 0
        for t, m in zip(record.target, record.mask):
            if m == "1":
                total += 1
                if t != "N":
                    mem += 1
        # avoid div by zero (shouldn't happen, but be safe)
        return (mem / total) if total > 0 else 0.0

    # Prepare ids and ratios aligned
    seq_ids: List[str] = [r.seq_id for r in dedup_train_pool]
    ratios: List[float] = [membrane_ratio(r) for r in dedup_train_pool]

    # Determine number of bins based on dataset size
    n_bins = min(10, max(2, len(seq_ids) // 20))
    percentiles = np.linspace(0, 100, n_bins + 1)[1:-1]  # exclude 0 and 100
    bin_edges = np.percentile(ratios, percentiles) if len(percentiles) > 0 else []
    stratify_labels = np.digitize(ratios, bins=bin_edges)
    train_ids, val_ids = train_test_split(
        seq_ids, test_size=val_fraction, random_state=seed, stratify=stratify_labels
    )

    # Report ratios after splitting
    train_ratios = [ratios[i] for i, id_ in enumerate(seq_ids) if id_ in train_ids]
    val_ratios = [ratios[i] for i, id_ in enumerate(seq_ids) if id_ in val_ids]
    print(f"Average membrane ratio - train: {np.mean(train_ratios):.4f}, val: {np.mean(val_ratios):.4f}")

    return train_ids, val_ids


def write_biotrainer_fasta(out_path: Path, entries: List[_Record]) -> None:
    """Write entries to FASTA with conservation-like header.

    entries: list of (seq_id, seq, target, split)
    """
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w") as out:
        for record in entries:
            out.write(f">{record.seq_id} SET={record.set} TARGET={record.target} MASK={record.mask}\n")
            out.write(f"{record.seq}\n")


def main():
    cv_dir = Path("data/cv/")
    seed = 42
    val_fraction = 0.1

    # Gather records per fold
    fold_records: Dict[int, List[_Record]] = {}
    for fold in range(5):
        path = cv_dir / f"cv_0{fold}_a.fasta"
        if not path.exists():
            raise FileNotFoundError(f"Missing CV file: {path}")
        fold_records[fold] = read_cv_fasta(path)

    # Assign splits
    test_entries: List[_Record] = []
    train_pool: List[_Record] = []

    # CV0 → test
    for record in fold_records[0]:
        test_entries.append(record._replace(set="test"))
    test_ids = {r.seq_id for r in test_entries}
    assert len(test_ids) == len(test_entries)
    print(f"Number of test sequences extracted: {len(test_ids)}")

    # CV1–4 → train pool
    for fold in (1, 2, 3, 4):
        train_pool.extend(fold_records[fold])
    train_ids = {r.seq_id for r in train_pool}
    print("Number of training sequences extracted:", len(train_ids))

    for train_id in train_ids:
        assert train_id not in test_ids
    for test_id in test_ids:
        assert test_id not in train_ids

    # Deduplicate by seq_id keeping first occurrence
    seen: set[str] = set()
    dedup_train_pool: List[_Record] = []
    for record in train_pool:
        if record.seq_id in seen:
            continue
        seen.add(record.seq_id)
        dedup_train_pool.append(record)
    dedup_ids = {r.seq_id for r in dedup_train_pool}
    assert len(dedup_ids) == len(dedup_train_pool)

    # Apply blacklist
    blacklist_ids = read_blacklist()
    test_entries = [r for r in test_entries if r.seq_id not in blacklist_ids]
    dedup_train_pool = [r for r in dedup_train_pool if r.seq_id not in blacklist_ids]

    print(f"Number of blacklist sequences: {len(blacklist_ids)}")
    print(f"Number of train sequences after blacklist removal: {len(dedup_train_pool)}")
    print(f"Number of test sequences after blacklist removal: {len(test_entries)}")

    # Check for unique sequences
    train_seqs = [r.seq for r in dedup_train_pool]
    test_seqs = [r.seq for r in test_entries]

    assert len(train_seqs) == len(set(train_seqs))
    assert len(test_seqs) == len(set(test_seqs))

    train_ids, val_ids = split_membrane_train_val_stratified(dedup_train_pool, seed, train_ids, val_fraction)

    train_id_set = set(train_ids)
    val_id_set = set(val_ids)
    assert len(train_id_set) + len(val_id_set) == len(dedup_train_pool)

    train_entries: List[_Record] = []
    val_entries: List[_Record] = []
    for record in dedup_train_pool:
        if record.seq_id in val_id_set:
            val_entries.append(record._replace(set="val"))
        else:
            train_entries.append(record._replace(set="train"))

    # Combine and write
    all_entries = train_entries + val_entries + test_entries

    # Sort entries for reproducible file order (by split, then id)
    split_order = {"train": 0, "val": 1, "test": 2}
    all_entries.sort(key=lambda x: (split_order[x.set], x.seq_id))

    out = Path("membrane.fasta")
    write_biotrainer_fasta(Path("membrane.fasta"), all_entries)

    # Print a short summary
    print(f"Wrote: {out}")

    # Compute and print membrane ratios for train/val for verification
    def agg_membrane_ratio(entries: List[_Record]) -> float:
        pos = 0
        tot = 0
        for r in entries:
            for t, m in zip(r.target, r.mask):
                if m == "1":
                    tot += 1
                    if t != "N":
                        pos += 1
        return (pos / tot) if tot > 0 else 0.0

    train_ratio = agg_membrane_ratio(train_entries)
    val_ratio = agg_membrane_ratio(val_entries)
    test_ratio = agg_membrane_ratio(test_entries)

    print(f"  train: {len(train_entries)} (membrane ratio: {train_ratio:.4f})")
    print(f"  val:   {len(val_entries)} (val_fraction={val_fraction}, membrane ratio: {val_ratio:.4f})")
    print(f"  test:  {len(test_entries)} (from CV0), membrane ratio: {test_ratio:.4f}")


if __name__ == "__main__":
    main()
