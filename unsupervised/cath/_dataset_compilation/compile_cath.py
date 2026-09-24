import random
from pathlib import Path
from collections import Counter
from typing import List

from biotrainer_core.data_classes import SequenceData
from biotrainer_core.input_files import read_FASTA, write_FASTA

def read_labels(labels_file: Path):
    with open(labels_file, 'r') as f:
        lines = f.readlines()
        labels = {}
        for line in lines:
            vals = line.strip().split(",")
            labels[vals[0]] = vals[1]

    assert len(lines) == len(labels), f"Found non-unique labels in {labels_file}!"
    return labels


def remove_duplicates(all_seqs, lookup_fasta_enhanced, test_fasta_enhanced):
    # IDs
    all_seq_ids = [seq_record.seq_id for seq_record in all_seqs]
    seq_id_counts = Counter(all_seq_ids)
    duplicates = [seq_id for seq_id, count in seq_id_counts.items() if count > 1]
    if duplicates:
        print(f"Found {len(duplicates)} duplicate sequence IDs:")
        for seq_id in duplicates:
            print(f"  - {seq_id} (appears {seq_id_counts[seq_id]} times)")
        # Remove from lookup
        lookup_fasta_enhanced = [seq_record for seq_record in lookup_fasta_enhanced if
                                 seq_record.seq_id not in duplicates]
        all_seqs_no_duplicates = lookup_fasta_enhanced + test_fasta_enhanced
        size_difference = len(all_seqs) - len(all_seqs_no_duplicates)
        assert size_difference > 0
        print(f"Removed {size_difference} duplicate sequence IDs from lookup.")
        all_seqs = all_seqs_no_duplicates
    else:
        print("No duplicate sequence IDs found.")

    # Sequences
    all_sequences = [seq_record.seq for seq_record in all_seqs]
    seq_counts = Counter(all_sequences)
    duplicates = [seq_id for seq_id, count in seq_counts.items() if count > 1]
    if duplicates:
        print(f"Found {len(duplicates)} duplicate sequences:")
        for seq in duplicates:
            print(f"  - {seq} (appears {seq_counts[seq]} times)")
        # Remove from lookup
        lookup_fasta_enhanced = [seq_record for seq_record in lookup_fasta_enhanced if
                                 seq_record.seq not in duplicates]
        all_seqs_no_duplicates = lookup_fasta_enhanced + test_fasta_enhanced
        size_difference = len(all_seqs) - len(all_seqs_no_duplicates)
        assert size_difference > 0
        print(f"Removed {size_difference} duplicate sequences from lookup.")
        all_seqs = all_seqs_no_duplicates
    else:
        print("No duplicate sequences found.")

    # Double check removal
    all_sequences = [seq_record.seq for seq_record in all_seqs]
    seq_counts = Counter(all_sequences)
    duplicates = [seq_id for seq_id, count in seq_counts.items() if count > 1]
    assert len(duplicates) == 0

    return all_seqs


def remove_missing_labels_of_test_in_lookup(lookup_seqs: List[SequenceData], test_seqs: List[SequenceData]):
    lookup_labels = {seq_record.label for seq_record in lookup_seqs}
    test_labels = {seq_record.label for seq_record in test_seqs}

    missing_labels = set()
    for test_label in test_labels:
        if test_label not in lookup_labels:
            print(f"Missing label {test_label} in lookup.")
            missing_labels.add(test_label)

    print(f"Total missing labels for lookup: {len(missing_labels)} (will be removed)")
    return [seq_record for seq_record in test_seqs if seq_record.label not in missing_labels]

def create_dev_subset(lookup_seqs: List[SequenceData]):
    # Subsample dataset such that each catH-level has at most N sequences
    lookup_labels = {str(seq_record.label) for seq_record in lookup_seqs}
    h_level_labels = {label.split(".")[-1] for label in lookup_labels}  # Last level is catH

    print(f"Number of different h_level_labels: {len(h_level_labels)}")
    h_level_labels_to_lookup_seqs = {}
    for seq_record in lookup_seqs:
        h_level = seq_record.label.split(".")[-1]
        if h_level not in h_level_labels_to_lookup_seqs:
            h_level_labels_to_lookup_seqs[h_level] = []
        h_level_labels_to_lookup_seqs[h_level].append(seq_record)

    lookup_dev_subset = []
    random.seed(43)
    sample_maximum = 26  # Sample at most N sequences with the same H-level, 26 is chosen because it equals roughly 10% of the dataset as a result
    for h_level, seqs in h_level_labels_to_lookup_seqs.items():
        random_sample = random.sample(seqs, min(sample_maximum, len(seqs)))
        lookup_dev_subset.extend(random_sample)

    print(f"Number of sequences in lookup dev subset: {len(lookup_dev_subset)}")

    return lookup_dev_subset

def main():
    result_file = Path("../cath.fasta")

    # Load data
    lookup_fasta = read_FASTA("lookup69k.fasta")
    test_fasta = read_FASTA("test219.fasta")

    labels = read_labels(Path("cath_v430_dom_seqs_S100_161121_labels.txt"))
    assert len(labels) >= len(lookup_fasta) + len(test_fasta)

    lookup_seqs_enhanced = [seq_record.copy_with_label(label=labels[seq_record.seq_id], set_name="lookup") for
                             seq_record in lookup_fasta]

    test_seqs_enhanced = [seq_record.copy_with_label(label=labels[seq_record.seq_id], set_name="test") for
                           seq_record in test_fasta]

    # Remove missing lookup data (cannot be transferred)
    test_seqs_enhanced = remove_missing_labels_of_test_in_lookup(lookup_seqs_enhanced, test_seqs_enhanced)

    assert len(test_seqs_enhanced) < len(test_fasta)

    # Extract lookup dev subset
    lookup_dev_subset = create_dev_subset(lookup_seqs_enhanced)
    lookup_dev_subset_ids = {seq_record.seq_id: seq_record for seq_record in lookup_dev_subset}
    lookup_seqs_enhanced = [seq_record.set_attribute(key="DEV_MODE",
                                                     value=seq_record.seq_id in lookup_dev_subset_ids)
                            for seq_record in lookup_seqs_enhanced]
    # Test Seqs are always necessary for both modes (DEV AND EVAL), so DEV_MODE needs to be True
    test_seqs_enhanced = [seq_record.set_attribute(key="DEV_MODE", value=True)  for
                           seq_record in test_seqs_enhanced]

    all_seqs = lookup_seqs_enhanced + test_seqs_enhanced

    # Find and remove duplicates
    all_seqs = remove_duplicates(all_seqs, lookup_seqs_enhanced, test_seqs_enhanced)

    # Write sequences
    write_FASTA(result_file, all_seqs)

    # Double-check written sequences
    seq_records_loaded = read_FASTA(result_file)
    assert len(seq_records_loaded) == len(all_seqs)

    seq_records_dev = [seq_record for seq_record in all_seqs if seq_record.get_attribute("DEV_MODE")]

    assert len(seq_records_dev) == len(lookup_dev_subset) + len(test_seqs_enhanced)

    print(f"Written {len(seq_records_loaded)} to {result_file} in biotrainer format!")

if __name__ == "__main__":
    main()
