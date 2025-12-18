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

import argparse
import random
from pathlib import Path
from typing import Dict, List, Tuple
from sklearn.model_selection import train_test_split


def read_cv_fasta(path: Path) -> List[Tuple[str, str, str]]:
    """Read a 3-line-per-record FASTA with sequence and annotation.

    Returns list of tuples: (id, seq, target)
    """
    records: List[Tuple[str, str, str]] = []
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
            raise ValueError(f"Expected header starting with '>' in {path} at line {i+1}")
        header = lines[i][1:].strip()
        if i + 2 >= n:
            raise ValueError(f"Incomplete record at end of file {path}, starting at line {i+1}")
        seq = lines[i + 1].strip()
        target = lines[i + 2].strip()
        # derive a compact ID: take up to first whitespace in header
        # then, if '|' present, keep the first token before whitespace as the ID
        id_token = header.split()[0]
        seq_id = id_token  # keep full token (often Accession|...|...|fold)
        seq_ids.append(seq_id)
        # sanity: lengths can differ in some sources, but we don't enforce here strictly
        records.append((seq_id, seq, target))
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

def write_biotrainer_fasta(out_path: Path, entries: List[Tuple[str, str, str, str]]) -> None:
    """Write entries to FASTA with conservation-like header.

    entries: list of (seq_id, seq, target, split)
    """
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w") as out:
        for seq_id, seq, target, split in entries:
            mask = "".join(["0" if res == "U" else "1" for res in target])
            out.write(f">{seq_id} SET={split} TARGET={target} MASK={mask}\n")
            out.write(f"{seq}\n")


def main():
    cv_dir = Path("data/cv/")
    seed = 42
    val_fraction = 0.1

    # Gather records per fold
    fold_records: Dict[int, List[Tuple[str, str, str]]] = {}
    for fold in range(5):
        path = cv_dir / f"cv_0{fold}_a.fasta"
        if not path.exists():
            raise FileNotFoundError(f"Missing CV file: {path}")
        fold_records[fold] = read_cv_fasta(path)

    # Assign splits
    test_entries: List[Tuple[str, str, str, str]] = []
    train_pool: List[Tuple[str, str, str]] = []

    # CV0 → test
    for seq_id, seq, target in fold_records[0]:
        test_entries.append((seq_id, seq, target, "test"))
    test_ids = {seq_id for seq_id, _, _, _ in test_entries}
    assert len(test_ids) == len(test_entries)
    print(f"Number of test sequences extracted: {len(test_ids)}")

    # CV1–4 → train pool
    for fold in (1, 2, 3, 4):
        train_pool.extend(fold_records[fold])
    train_ids = {seq_id for seq_id, _, _ in train_pool}
    print("Number of training sequences extracted:", len(train_ids))

    for train_id in train_ids:
        assert train_id not in test_ids
    for test_id in test_ids:
        assert test_id not in train_ids

    # Deduplicate by seq_id keeping first occurrence
    seen: set[str] = set()
    dedup_train_pool: List[Tuple[str, str, str]] = []
    for seq_id, seq, target in train_pool:
        if seq_id in seen:
            continue
        seen.add(seq_id)
        dedup_train_pool.append((seq_id, seq, target))
    dedup_ids = {seq_id for seq_id, _, _ in dedup_train_pool}
    assert len(dedup_ids) == len(dedup_train_pool)

    # Apply blacklist
    blacklist_ids = read_blacklist()
    test_entries = [entry for entry in test_entries if entry[0] not in blacklist_ids]
    dedup_train_pool = [entry for entry in dedup_train_pool if entry[0] not in blacklist_ids]

    print(f"Number of blacklist sequences: {len(blacklist_ids)}")
    print(f"Number of train sequences after blacklist removal: {len(dedup_train_pool)}")
    print(f"Number of test sequences after blacklist removal: {len(test_entries)}")

    # Check for unique sequences
    train_seqs = {seq for _, seq, _ in dedup_train_pool}
    test_seqs = {seq for _, seq, _, _ in test_entries}

    assert len(train_seqs) == len(set(train_seqs))
    assert len(test_seqs) == len(set(test_seqs))

    # Split train/validation
    train_ids, val_ids = train_test_split(list(dedup_ids), test_size=val_fraction, random_state=seed)

    train_entries: List[Tuple[str, str, str, str]] = []
    val_entries: List[Tuple[str, str, str, str]] = []
    for i, (seq_id, seq, target) in enumerate(dedup_train_pool):
        split = "val" if seq_id in val_ids else "train"
        (val_entries if split == "val" else train_entries).append((seq_id, seq, target, split))

    # Combine and write
    all_entries = train_entries + val_entries + test_entries

    # Sort entries for reproducible file order (by split, then id)
    split_order = {"train": 0, "val": 1, "test": 2}
    all_entries.sort(key=lambda x: (split_order[x[3]], x[0]))

    out = Path("membrane.fasta")
    write_biotrainer_fasta(Path("membrane.fasta"), all_entries)

    # Print a short summary
    print(f"Wrote: {out}")
    print(f"  train: {len(train_entries)}")
    print(f"  val:   {len(val_entries)} (val_fraction={val_fraction})")
    print(f"  test:  {len(test_entries)} (from CV0)")
    

if __name__ == "__main__":
    main()
