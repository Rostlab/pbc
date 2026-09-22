from pathlib import Path
from collections import Counter

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


def remove_duplicates(all_seqs, lookup_fasta_enhanced, val_fasta_enhanced, test_fasta_enhanced):
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
        all_seqs_no_duplicates = lookup_fasta_enhanced + val_fasta_enhanced + test_fasta_enhanced
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
        all_seqs_no_duplicates = lookup_fasta_enhanced + val_fasta_enhanced + test_fasta_enhanced
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


def main():
    result_file = Path("../cath.fasta")

    # Load data
    lookup_fasta = read_FASTA("lookup69k.fasta")
    val_fasta = read_FASTA("val200.fasta")
    test_fasta = read_FASTA("test219.fasta")

    labels = read_labels(Path("cath_v430_dom_seqs_S100_161121_labels.txt"))
    assert len(labels) >= len(lookup_fasta) + len(val_fasta) + len(test_fasta)

    lookup_fasta_enhanced = [seq_record.copy_with_label(label=labels[seq_record.seq_id], set_name="lookup") for
                             seq_record in lookup_fasta]
    val_fasta_enhanced = [seq_record.copy_with_label(label=labels[seq_record.seq_id], set_name="val") for
                          seq_record in val_fasta]
    test_fasta_enhanced = [seq_record.copy_with_label(label=labels[seq_record.seq_id], set_name="test") for
                           seq_record in test_fasta]

    all_seqs = lookup_fasta_enhanced + val_fasta_enhanced + test_fasta_enhanced

    # Find and remove duplicates
    all_seqs = remove_duplicates(all_seqs, lookup_fasta_enhanced, val_fasta_enhanced, test_fasta_enhanced)

    # Write sequences
    write_FASTA(result_file, all_seqs)

    # Double-check written sequences
    seq_records_loaded = read_FASTA(result_file)
    assert len(seq_records_loaded) == len(all_seqs)

    print(f"Written {len(seq_records_loaded)} to {result_file} in biotrainer format!")

if __name__ == "__main__":
    main()
