import numpy as np

from collections import Counter
from sklearn.model_selection import train_test_split


def read_fasta(file_path: str):
    seq_records = {}
    seq_ids = []
    with open(file_path, "r") as f:
        lines = f.readlines()
        for line in lines:
            if line.startswith(">"):
                seq_id = line.replace(">", "").strip()
                seq_ids.append(seq_id)
                seq_records[seq_id] = ""
            else:
                seq_records[seq_id] += line.strip()
    assert len(seq_records) == len(seq_ids)
    return seq_records


def read_ids(file_path: str):
    with open(file_path, "r") as f:
        return [line.strip() for line in f.readlines()]


def load_targets(file_path: str):
    seq_targets = {}
    with open(file_path, "r") as f:
        lines = f.readlines()
        for line in lines:
            seq_id, target = line.strip().split("\t")
            target = [int(idx) - 1 for idx in target.split(",")]  # Target indices start from 1
            assert min(target) >= 0
            assert len(target) == len(set(target))
            seq_targets[seq_id] = target
    return seq_targets


def get_binding_data(seq_records, targets):
    seq_with_target = {}
    for seq_id, seq in seq_records.items():
        target = targets.get(seq_id, None)
        if target:
            target_set = set(target)
            binary_target = [1 if idx in target_set else 0 for idx, aa in enumerate(seq)]
            assert len(binary_target) == len(seq)
            assert sum(binary_target) == len(target_set)
            seq_with_target[seq_id] = {"seq": seq, "target": binary_target}
    return seq_with_target


def get_binding_data_combined(seq_records, targets1, targets2, targets3):
    seq_with_target = {}
    for seq_id, seq in seq_records.items():
        target1 = targets1.get(seq_id, [])
        target2 = targets2.get(seq_id, [])
        target3 = targets3.get(seq_id, [])
        target = target1 + target2 + target3
        if len(target) > 0:
            target_set = set(target)
            binary_target = [1 if idx in target_set else 0 for idx, aa in enumerate(seq)]
            assert len(binary_target) == len(seq)
            assert sum(binary_target) == len(target_set)
            seq_with_target[seq_id] = {"seq": seq, "target": binary_target}
    return seq_with_target


def split_binding_train_val(binding_records, val_percentage: float):
    train_ids, val_ids = train_test_split(list(binding_records.keys()),
                                          test_size=val_percentage, random_state=42)
    train_records = {seq_id: r for seq_id, r in binding_records.items() if seq_id in train_ids}
    val_records = {seq_id: r for seq_id, r in binding_records.items() if seq_id in val_ids}
    assert len(train_records) + len(val_records) == len(binding_records)

    train_binding_ratio = sum(sum(r['target']) for r in train_records.values()) / sum(
        len(r['target']) for r in train_records.values())
    val_binding_ratio = sum(sum(r['target']) for r in val_records.values()) / sum(
        len(r['target']) for r in val_records.values())
    print(f"  Train: {len(train_records)} sequences, binding ratio: {train_binding_ratio:.4f}")
    print(f"  Val:   {len(val_records)} sequences, binding ratio: {val_binding_ratio:.4f}")

    return train_records, val_records


def split_binding_train_val_stratified(binding_records, val_percentage: float):
    """
    Stratified split based on the proportion of binding residues in each sequence.
    This ensures train and val sets have similar distributions of binding ratios.
    """
    seq_ids = list(binding_records.keys())

    # Calculate binding ratio for each sequence
    binding_ratios = []
    for seq_id in seq_ids:
        record = binding_records[seq_id]
        binding_count = sum(record['target'])
        total_count = len(record['target'])
        binding_ratio = binding_count / total_count
        binding_ratios.append(binding_ratio)

    # Create stratification bins based on binding ratios
    # Adjust number of bins based on dataset size to avoid errors
    n_bins = min(10, max(2, len(seq_ids) // 20))

    # Create bins using percentiles to ensure balanced distribution
    percentiles = np.linspace(0, 100, n_bins + 1)[1:-1]  # Exclude 0 and 100
    bin_edges = np.percentile(binding_ratios, percentiles)
    stratify_labels = np.digitize(binding_ratios, bins=bin_edges)

    # Perform stratified split
    train_ids, val_ids = train_test_split(seq_ids,
                                          test_size=val_percentage,
                                          random_state=42,
                                          stratify=stratify_labels)

    train_records = {seq_id: r for seq_id, r in binding_records.items() if seq_id in train_ids}
    val_records = {seq_id: r for seq_id, r in binding_records.items() if seq_id in val_ids}

    train_binding_ratio = sum(sum(r['target']) for r in train_records.values()) / sum(
        len(r['target']) for r in train_records.values())
    val_binding_ratio = sum(sum(r['target']) for r in val_records.values()) / sum(
        len(r['target']) for r in val_records.values())
    print(f"  Train: {len(train_records)} sequences, binding ratio: {train_binding_ratio:.4f}")
    print(f"  Val:   {len(val_records)} sequences, binding ratio: {val_binding_ratio:.4f}")

    assert len(train_records) + len(val_records) == len(binding_records)
    return train_records, val_records


def to_biotrainer_format(train_records, val_records, test_records, file_name):
    compiled_records = [(train_records, "train"), (val_records, "val"), (test_records, "test")]
    with open(file_name, "w") as f:
        for records, split in compiled_records:
            for seq_id, record in records.items():
                target = "".join(list(map(str, record['target'])))
                f.write(f">{seq_id} SET={split} TARGET={target}\n{record['seq']}\n")


def _get_target_percentage(records):
    ts = [v["target"] for v in records.values()]
    n = 0
    total = 0
    for t in ts:
        n += sum(t)
        total += len(t)
    return n / total


def main():
    # Load training sequences
    train_seqs = read_fasta("data/development_set/all.fasta")

    # Check for duplicated sequences
    duplicates = {seq: c for seq, c in Counter(train_seqs.values()).items() if c > 1}
    print(f"Duplicated sequences in all.fasta: {duplicates}")
    # Found 2 (4 seq_ids) - removing them because of ambiguous target annotations
    duplicates_to_remove = ["P84229", "P84233", "P62801", "P62799"]
    train_seqs = {seq_id: seq for seq_id, seq in train_seqs.items() if seq_id not in duplicates_to_remove}
    # MARTKQTARKSTGGKAPRKQLATKAARKSAPATGGVKKPHRYRPGTVALREIRRYQKSTELLIRKLPFQRLVREIAQDFKTDLRFQSSAVMALQEASEAYLVGLFEDTNLCAIHAKRVTIMPKDIQLARRIRGERA
    # P84229: n - 121,46,119,73,84,42,44,118,25,41,45,85,48,65,66,43,67,86,70,64,40,117,87,47,50
    # P84229: s - 51,50,54,73,69,70,135,61,129,60,55,126,65
    # P84233: n - 37,46,73,42,35,38,44,41,45,48,66,57,86,70,64,116,26,50,121,119,84,118,82,85,65,43,67,40,117,123,87,47
    # P84233: m - 78, 77

    # MSGRGKGGKGLGKGGAKRHRKVLRDNIQGITKPAIRRLARRGGVKRISGLIYEETRGVLKVFLENVIRDAVTYTEHAKRKTVTAMDVVYALKRQGRTLYGFGG
    # P62801: n - 37,46,24,80,33,48,36,81,31,11,79,22,49,17,20,47
    # P62801: s - 46,36,31,34,40,29,47
    # P62799: s - 85,61,89,60,64,103
    # P62799: n - 37,6,46,19,16,24,18,3,4,80,78,33,48,15,36,81,31,5,79,10,22,49,2,17,20,9,21,47,13,7
    assert len(train_seqs.values()) == len(set(train_seqs.values()))

    # Load ids to double check consistency
    ids1 = read_ids("data/development_set/ids_split1.txt")
    ids2 = read_ids("data/development_set/ids_split2.txt")
    ids3 = read_ids("data/development_set/ids_split3.txt")
    ids4 = read_ids("data/development_set/ids_split4.txt")
    ids5 = read_ids("data/development_set/ids_split5.txt")
    ids6 = read_ids("data/development_set/uniprot_test.txt")
    all_ids = ids1 + ids2 + ids3 + ids4 + ids5 + ids6
    assert len(all_ids) == len(set(all_ids))
    assert len(all_ids) == len(train_seqs) + len(duplicates_to_remove)

    # Load binding targets
    metal_targets = load_targets("data/development_set/binding_residues_2.5_metal.txt")
    nuclear_targets = load_targets("data/development_set/binding_residues_2.5_nuclear.txt")
    small_targets = load_targets("data/development_set/binding_residues_2.5_small.txt")

    # Combine sequences with targets
    metal_records = get_binding_data(train_seqs, metal_targets)
    nuclear_records = get_binding_data(train_seqs, nuclear_targets)
    small_records = get_binding_data(train_seqs, small_targets)
    combined_records = get_binding_data_combined(train_seqs, metal_targets, nuclear_targets, small_targets)
    assert len(combined_records) > len(metal_records)
    assert len(combined_records) > len(nuclear_records)
    assert len(combined_records) > len(small_records)  # Combined dataset must contain more sequences than individual

    # Create binding-specific splits
    val_percentage = 0.1
    print("metal - train/val")
    metal_train, metal_val = split_binding_train_val_stratified(metal_records, val_percentage=val_percentage)
    print("nuclear - train/val")
    nuclear_train, nuclear_val = split_binding_train_val_stratified(nuclear_records, val_percentage=val_percentage)
    print("small - train/val")
    small_train, small_val = split_binding_train_val_stratified(small_records, val_percentage=val_percentage)
    print("combined - train/val")
    combined_train, combined_val = split_binding_train_val_stratified(combined_records, val_percentage=val_percentage)

    # Load test set
    test_seqs = read_fasta("data/independent_set/indep_set.fasta")
    for seq_id, seq in test_seqs.items():
        assert seq_id not in train_seqs.keys()
        assert seq not in train_seqs.values()
    assert len(test_seqs) == 46
    assert len(test_seqs.values()) == len(set(test_seqs.values()))

    metal_targets_test = load_targets("data/independent_set/binding_residues_metal.txt")
    nuclear_targets_test = load_targets("data/independent_set/binding_residues_nuclear.txt")
    small_targets_test = load_targets("data/independent_set/binding_residues_small.txt")

    metal_records_test = get_binding_data(test_seqs, metal_targets_test)
    nuclear_records_test = get_binding_data(test_seqs, nuclear_targets_test)
    small_records_test = get_binding_data(test_seqs, small_targets_test)
    combined_records_test = get_binding_data_combined(test_seqs, metal_targets_test, nuclear_targets_test, small_targets_test)
    assert len(combined_records_test) > len(metal_records_test)
    assert len(combined_records_test) > len(nuclear_records_test)
    assert len(combined_records_test) > len(small_records_test)

    # Print statistics
    print("Number of test sequences (metal, nuclear, small):")
    print(len(metal_records_test), len(nuclear_records_test), len(small_records_test))
    # Compare train/val target distributions
    print(
        f"Percentage of targets (metal) - train: {_get_target_percentage(metal_train)}, val: {_get_target_percentage(metal_val)}, test: {_get_target_percentage(metal_records_test)}")
    print(
        f"Percentage of targets (nuclear) - train: {_get_target_percentage(nuclear_train)}, val: {_get_target_percentage(nuclear_val)}, test: {_get_target_percentage(nuclear_records_test)}")
    print(
        f"Percentage of targets (small) - train: {_get_target_percentage(small_train)}, val: {_get_target_percentage(small_val)}, test: {_get_target_percentage(small_records_test)}")
    print(
        f"Percentage of targets (combined) - train: {_get_target_percentage(combined_train)}, val: {_get_target_percentage(combined_val)}, test: {_get_target_percentage(combined_records_test)}"
    )
    # Convert to biotrainer format
    to_biotrainer_format(metal_train, metal_val, metal_records_test, "binding_metal.fasta")
    to_biotrainer_format(nuclear_train, nuclear_val, nuclear_records_test, "binding_nuclear.fasta")
    to_biotrainer_format(small_train, small_val, small_records_test, "binding_small.fasta")
    to_biotrainer_format(combined_train, combined_val, combined_records_test, "binding_combined.fasta")

    print("Dataset compilation done for binding!")


if __name__ == "__main__":
    main()
