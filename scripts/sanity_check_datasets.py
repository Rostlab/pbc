from pathlib import Path
from typing import List

from biotrainer_core.input_files import read_FASTA
from biotrainer_core.data_classes import SequenceData

_test_sets = ["test", "newPISCES364", "casp12", "casp13", "casp14"]


def _check_supervised(seq_records: List[SequenceData]):
    assert len(seq_records) > 0
    assert len(seq_records) == len(set([sr.seq_id for sr in seq_records]))  # No duplicate ids
    seqs = [sr.seq for sr in seq_records]
    counts = {seq: seqs.count(seq) for seq in set(seqs)}
    duplicates = {s: c for s, c in counts.items() if c > 1}
    if len(duplicates) > 0:
        print(f"Found {len(duplicates)} duplicate sequences: {duplicates}")
    assert len(seq_records) == len(set(seqs))  # No duplicate sequences

    train_seqs = set([sr.seq for sr in seq_records if sr.set == "train"])
    val_seqs = set([sr.seq for sr in seq_records if sr.set == "val"])
    test_seqs = set([sr.seq for sr in seq_records if sr.set in _test_sets])

    for seq in test_seqs:
        assert seq not in train_seqs
        assert seq not in val_seqs

    for record in seq_records:
        assert record.set in ["train", "val", "test", *_test_sets]
        assert len(record.seq) > 0
        target = record.label
        assert target is not None
        if ";" in target:
            target = target.split(";")
        assert len(target) > 0

        assert len(record.seq) == len(target) if (len(target) > 50 or ';' in (record.label or "")) else True


def sanity_check_supervised(dataset_paths: list[Path]):
    for dataset_path in dataset_paths:
        print(f"Checking {dataset_path}...")
        seq_records = read_FASTA(dataset_path)
        _check_supervised(seq_records)
        print(f"Checked {dataset_path}!")


def sanity_check_contacts(dataset_paths: list[Path]):
    for dataset_path in dataset_paths:
        print(f"Checking {dataset_path}...")
        seq_records = read_FASTA(dataset_path)
        assert len(seq_records) > 0
        seqs = [sr.seq for sr in seq_records]
        assert len(set(seqs)) == len(seqs)
        seq_ids = [sr.seq_id for sr in seq_records]
        assert len(set(seq_ids)) == len(seq_ids)
        print(f"Checked {dataset_path}!")