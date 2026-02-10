from pathlib import Path
from collections import Counter


def read_fasta(file_path: Path):
    seq_records = {}
    seq_ids = []
    with open(file_path, "r") as f:
        lines = f.readlines()
        for line in lines:
            if line.startswith(">"):
                seq_id = line.split(">")[1].split(" ")[0].strip()
                seq_ids.append(seq_id)
                target = line.split("TARGET=")[1].split(" ")[0].strip() if "TARGET" in line else None
                split = line.split("SET=")[1].split(" ")[0].strip() if "SET" in line else None
                validation = line.split("VALIDATION=")[1].split(" ")[0].strip() if "VALIDATION" in line else None
                split_set = "val" if validation == "True" else split
                assert split_set in ["train", "val", "test", None]
                assert not (validation == "True" and split == "test")
                seq_records[seq_id] = {"target": target, "set": split_set}
            else:
                if "seq" not in seq_records[seq_id]:
                    seq_records[seq_id]["seq"] = ""
                seq_records[seq_id]["seq"] += line.strip()
    assert len(seq_records) == len(seq_ids)
    return seq_records


def write_mapped_biotrainer_fasta(out_path: Path, flip_records, seq_to_id) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w") as out:
        for idx, record in flip_records.items():
            out.write(f">{seq_to_id[record['seq']]} TARGET={record['target']} SET={record['set']} \n")
            out.write(f"{record['seq']}\n")


def main():
    deeploc_train = Path("deeploc_our_train_set.fasta")
    deeploc_val = Path("deeploc_our_val_set.fasta")
    setHard = Path("setHARD.fasta")

    flip_mixed_hard = Path("mixed_hard.fasta")

    deeploc_records = {}
    deeploc_train_r = read_fasta(deeploc_train)
    deeploc_records.update(deeploc_train_r)
    deeploc_val_r = read_fasta(deeploc_val)
    deeploc_records.update(deeploc_val_r)
    deeploc_test_r = read_fasta(setHard)
    deeploc_records.update(deeploc_test_r)
    flip_mixed_hard_records = read_fasta(flip_mixed_hard)
    flip_train = [r for r in flip_mixed_hard_records.values() if r['set'] == 'train']
    flip_val = [r for r in flip_mixed_hard_records.values() if r['set'] == 'val']
    flip_test = [r for r in flip_mixed_hard_records.values() if r['set'] == 'test']
    assert len(deeploc_records) == len(flip_mixed_hard_records)
    assert len(flip_train) + len(flip_val) + len(flip_test) == len(flip_mixed_hard_records)
    assert len(flip_train) == len(deeploc_train_r)
    assert len(flip_val) == len(deeploc_val_r)
    assert len(flip_test) == len(deeploc_test_r)

    duplicates = {seq: c for seq, c in Counter([r['seq'] for r in deeploc_records.values()]).items() if c > 1}
    if len(duplicates) > 0:
        print(f"Found {len(duplicates)} duplicate sequences: {duplicates}")
        assert False

    seq_to_id = {record["seq"]: seq_id for seq_id, record in deeploc_records.items()}
    assert len(seq_to_id) == len(deeploc_records)

    write_mapped_biotrainer_fasta(out_path=Path("scl.fasta"), flip_records=flip_mixed_hard_records, seq_to_id=seq_to_id)

if __name__ == "__main__":
    main()