from pathlib import Path

_test_sets = ["test", "newPISCES364", "casp12", "casp13", "casp14"]

def read_fasta(file_path: Path):
    seq_records = {}
    seq_ids = []
    with open(file_path, "r") as f:
        lines = f.readlines()
        for line in lines:
            if line.startswith(">"):
                seq_id = line.split(">")[1].split(" ")[0].strip()
                seq_ids.append(seq_id)
                target = line.split("TARGET=")[1].split(" ")[0].strip()
                split = line.split("SET=")[1].split(" ")[0].strip()
                seq_records[seq_id] = {"target": target, "set": split}
            else:
                seq_records[seq_id]["seq"] = line.strip()
    assert len(seq_records) == len(seq_ids)
    return seq_records


def _check(seq_records: dict[str, dict[str, str]]):
    assert len(seq_records) > 0
    assert len(seq_records) == len(set(seq_records.keys()))  # No duplicate ids
    seqs = [record["seq"] for record in seq_records.values()]
    assert len(seq_records) == len(set(seqs))  # No duplicate sequences

    train_seqs = set([record["seq"] for record in seq_records.values() if record["set"] == "train"])
    val_seqs = set([record["seq"] for record in seq_records.values() if record["set"] == "val"])
    test_seqs = set([record["seq"] for record in seq_records.values() if
                     record["set"] in _test_sets])

    for seq in test_seqs:
        assert seq not in train_seqs
        assert seq not in val_seqs

    for seq_id, record in seq_records.items():
        assert record["set"] in ["train", "val", "test", *_test_sets]
        assert len(record["seq"]) > 0
        target = record["target"]
        if ";" in target:
            target = target.split(";")
        assert len(target) > 0
        assert len(record["seq"]) == len(target) if len(record["target"]) > 25 else True


def sanity_check(dataset_paths: list[Path]):
    for dataset_path in dataset_paths:
        print(f"Checking {dataset_path}...")
        seq_records = read_fasta(dataset_path)
        _check(seq_records)
        print(f"Checked {dataset_path}!")
