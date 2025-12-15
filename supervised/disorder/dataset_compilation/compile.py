import os

from pathlib import Path
from sklearn.model_selection import train_test_split

disorder_output = "disorder.fasta"


def read_test_set_scores():
    test_set_files = os.listdir("CheZOD117_test_set_CheZOD_scores")
    test_set_scores = {}
    for test_set_file in test_set_files:
        test_set_path = Path(f"CheZOD117_test_set_CheZOD_scores/{test_set_file}")
        if os.path.isdir(test_set_path):
            continue
        test_seq_id = test_set_file.split(".")[0].split("zscores")[1]
        with open(test_set_path, "r") as tf:
            lines = tf.readlines()
            test_seq = ""
            test_scores = []
            for line in lines:
                vals = line.replace("\n", "").split(" ")
                test_seq += vals[0]
                test_scores.append(float(vals[-1]))
        test_set_scores[test_seq_id] = {"seq": test_seq, "scores": test_scores}

    return test_set_scores


def read_training_set_scores():
    with open("CheZOD1174_training_set_CheZOD_scores.txt", "r") as tf:
        lines = tf.readlines()
        training_scores = {}
        for line in lines:
            vals = line.replace("\n", "").split(":")
            seq_id = vals[0]
            scores = vals[1].split(",")
            training_scores[seq_id] = [float(score.replace("\t", "").replace(" ", "")) for score in scores]

    return training_scores


def read_fasta(file_path: str):
    with open(file_path, "r") as f:
        lines = f.readlines()
        seqs = {}
        for line in lines:
            if line.startswith(">"):
                seq_id = line.replace(">", "").strip()
                seqs[seq_id] = ""
            else:
                seqs[seq_id] += line.strip()
    return seqs


def split_train_val(training_seqs):
    percentage = 0.1
    train_ids, val_ids = train_test_split(list(training_seqs.keys()), test_size=percentage)
    return {k: v for k, v in training_seqs.items() if k in train_ids}, {k: v for k, v in training_seqs.items() if
                                                                        k in val_ids}


def to_biotrainer_file(training_set_scores, test_set_scores, training_seqs, val_seqs, test_seqs, duplicates):
    set_combinations = [("train", training_seqs, training_set_scores), ("val", val_seqs, training_set_scores),
                        ("test", test_seqs, test_set_scores)]
    n_written = 0
    with open(disorder_output, "w") as f:
        for set_name, seqs, scores in set_combinations:
            for seq_id, seq in seqs.items():
                if seq in duplicates:
                    continue
                target = ";".join(list(map(str, scores[seq_id])))
                mask = "".join(["1" if score != 999.0 else "0" for score in scores[seq_id]])
                f.write(f">{seq_id} SET={set_name} TARGET={target} MASK={mask}\n{seq}\n")
                n_written += 1

    assert n_written == 1285


def do_sanity_checks(training_set_scores, test_set_scores, training_seqs, val_seqs, test_seqs):
    assert len(training_seqs) + len(val_seqs) == 1174
    assert len(training_set_scores) == len(training_seqs) + len(val_seqs)
    assert len(test_seqs) == 117
    assert len(test_set_scores) == len(test_seqs)
    for seq_id in test_set_scores:
        seq_from_scores = test_set_scores[seq_id]["seq"]
        assert seq_from_scores == test_seqs[seq_id]
        scores = test_set_scores[seq_id]["scores"]
        assert len(scores) == len(seq_from_scores)
    for seq_id, seq in [*training_seqs.items(), *val_seqs.items()]:
        assert seq_id in training_set_scores
        score = training_set_scores[seq_id]
        assert len(score) == len(seq)

    print("Sanity checks passed!")
    all_seqs = [*training_seqs.values(), *val_seqs.values(), *test_seqs.values()]
    counts = {seq: all_seqs.count(seq) for seq in set(all_seqs)}
    duplicates = {s: c for s, c in counts.items() if c > 1}
    print(f"Found {len(duplicates)} duplicate sequences to be removed: {duplicates}")
    return set(duplicates.keys())


def main():
    training_set_scores = read_training_set_scores()
    test_set_seqs_and_scores = read_test_set_scores()
    training_seqs = read_fasta("CheZOD1174_training_set_sequences.fasta")
    training_seqs, val_seqs = split_train_val(training_seqs)
    test_seqs = read_fasta("CheZOD117_test_set_sequences.fasta")
    duplicates = do_sanity_checks(training_set_scores, test_set_seqs_and_scores, training_seqs, val_seqs, test_seqs)

    test_set_only_scores = {seq_id: d["scores"] for seq_id, d in test_set_seqs_and_scores.items()}
    to_biotrainer_file(training_set_scores, test_set_only_scores, training_seqs, val_seqs, test_seqs,
                       duplicates=duplicates)
    print(f"Saved to {disorder_output}")


if __name__ == "__main__":
    main()
