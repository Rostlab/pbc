from sklearn.model_selection import train_test_split

phages_output = "phages.fasta"


def read_fasta(fasta_file):
    seq_records = {}
    with open(fasta_file, "r") as f:
        current_seq_id = None
        current_sequence = []
        current_target = None

        for line in f:
            line = line.strip()
            if line.startswith(">"):
                # Save previous record if exists
                if current_seq_id is not None:
                    seq_records[current_seq_id] = ("".join(current_sequence), current_target)

                # Parse new header
                current_seq_id = line.split(">")[1].split(" ")[0].strip()
                current_target = line.split("TARGET=")[1].split(" ")[0].strip().replace("\"", "")
                current_sequence = []
            else:
                # Append sequence line
                if line:
                    current_sequence.append(line)

        # Save last record
        if current_seq_id is not None:
            seq_records[current_seq_id] = ("".join(current_sequence), current_target)

    return seq_records


def split_train_val_test(unsplit_phages: dict):
    percentage_val = 0.15
    percentage_test = 0.1

    # First split: separate test set
    train_val_ids, test_ids = train_test_split(
        list(unsplit_phages.keys()),
        test_size=percentage_test,
        random_state=42,
        stratify=list([v[1] for v in unsplit_phages.values()])
    )

    # Second split: separate train and val from remaining data
    # Adjust val percentage to account for already removed test set
    adjusted_val_percentage = percentage_val / (1 - percentage_test)
    train_ids, val_ids = train_test_split(
        train_val_ids,
        test_size=adjusted_val_percentage,
        random_state=42,
        stratify=list([unsplit_phages[k][1] for k in train_val_ids])
    )

    assert len(train_ids) + len(val_ids) + len(test_ids) == len(unsplit_phages)
    assert len(set(train_ids).intersection(set(val_ids))) == 0
    assert len(set(val_ids).intersection(set(test_ids))) == 0
    assert len(set(train_ids).intersection(set(test_ids))) == 0
    total_size = len(train_ids) + len(val_ids) + len(test_ids)
    print(f"Train set size: {len(train_ids)} ({len(train_ids) / total_size * 100:.1f}%)")
    print(f"Val set size: {len(val_ids)} ({len(val_ids) / total_size * 100:.1f}%)")
    print(f"Test set size: {len(test_ids)} ({len(test_ids) / total_size * 100:.1f}%)")
    return (
        {k: v for k, v in unsplit_phages.items() if k in train_ids},
        {k: v for k, v in unsplit_phages.items() if k in val_ids},
        {k: v for k, v in unsplit_phages.items() if k in test_ids}
    )


def to_biotrainer_file(train_records: dict, val_records: dict, test_records: dict):
    set_combinations = [("train", train_records), ("val", val_records),
                        ("test", test_records)]
    n_written = 0
    with open(phages_output, "w") as f:
        for set_name, phage_dict in set_combinations:
            for seq_id in phage_dict.keys():
                seq = phage_dict[seq_id][0]
                target = phage_dict[seq_id][1]

                f.write(f">{seq_id} SET={set_name} TARGET={target}\n{seq}\n")
                n_written += 1

    assert n_written == len(train_records) + len(val_records) + len(test_records)


def main():
    phages_fasta_path = "rep_seq.one_phrog.with_function.fasta"
    phages_records = read_fasta(phages_fasta_path)
    assert len(phages_records) == 5131
    all_seqs = []
    all_targets = []
    for seq_id, (seq, target) in phages_records.items():
        assert target is not None and len(target) > 0
        assert seq is not None and len(seq) > 0
        assert '\"' not in target
        assert '\n' not in seq
        all_seqs.append(seq)
        all_targets.append(target)

    all_targets = set(all_targets)
    print("Targets: ", all_targets)

    assert len(set(all_seqs)) == len(all_seqs)
    train_recs, val_recs, test_recs = split_train_val_test(phages_records)
    to_biotrainer_file(train_recs, val_recs, test_recs)
    print("Saved to ", phages_output)
    print("Phage dataset compilation complete!")


if __name__ == "__main__":
    main()
