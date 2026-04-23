import json

disorder_output = "disorder_trizod.fasta"


def read_scores(jsonl_file: str):
    scores = {}
    with open(jsonl_file, "r") as f:
        for line in f:
            data = json.loads(line)
            seq_id = data["id"]
            score = data["y"]
            seq = data["x_0"]
            assert len(seq) == len(score)
            assert isinstance(score, list)
            assert isinstance(seq, str)
            assert isinstance(seq_id, str)
            assert isinstance(score[0], float) or isinstance(score[0], int)
            score = list(map(float, score))
            scores[seq_id] = (seq, score)
    return scores


def to_biotrainer_file(train_scores: dict, val_scores: dict, test_scores: dict):
    set_combinations = [("train", train_scores), ("val", val_scores),
                        ("test", test_scores)]
    n_written = 0
    with open(disorder_output, "w") as f:
        for set_name, scores_dict in set_combinations:
            for seq_id in scores_dict.keys():
                seq = scores_dict[seq_id][0]
                scores = scores_dict[seq_id][1]

                target = ";".join(list(map(str, scores)))
                mask = "".join(["1" if score != 999.0 else "0" for score in scores])
                assert len(seq) == len(scores)
                assert len(mask) == len(seq)
                f.write(f">{seq_id} SET={set_name} TARGET={target} MASK={mask}\n{seq}\n")
                n_written += 1

    assert n_written == len(train_scores) + len(val_scores) + len(test_scores)


def do_sanity_checks(train_scores: dict, val_scores: dict, test_scores: dict):
    train_seqs = [seq_r[0] for seq_r in train_scores.values()]
    val_seqs = [seq_r[0] for seq_r in val_scores.values()]
    test_seqs = [seq_r[0] for seq_r in test_scores.values()]
    train_seqs_set = set(train_seqs)
    val_seqs_set = set(val_seqs)
    test_seqs_set = set(test_seqs)

    for seq_id in train_scores:
        seq = train_scores[seq_id][0]
        assert seq_id not in val_scores
        assert seq_id not in test_scores
        assert seq in train_seqs_set
        assert seq not in val_seqs_set
        assert seq not in test_seqs_set

    for seq_id in val_scores:
        seq = val_scores[seq_id][0]
        assert seq_id not in train_scores
        assert seq_id not in test_scores
        assert seq not in train_seqs_set
        assert seq in val_seqs_set
        assert seq not in test_seqs_set

    for seq_id in test_scores:
        seq = test_scores[seq_id][0]
        assert seq_id not in train_scores
        assert seq_id not in val_scores
        assert seq not in train_seqs_set
        assert seq not in val_seqs_set
        assert seq in test_seqs_set

    all_seqs = [*train_seqs, *val_seqs, *test_seqs]
    counts = {seq: all_seqs.count(seq) for seq in set(all_seqs)}
    duplicates = {s: c for s, c in counts.items() if c > 1}
    if len(duplicates) > 0:
        print(f"Found {len(duplicates)} duplicate sequences to be removed: {duplicates}")
        assert False
    print("Sanity checks passed!")


def main():
    training_set_scores = read_scores("udonpred_trizod/train.jsonl")
    assert len(training_set_scores) == 3867
    val_set_scores = read_scores("udonpred_trizod/valid.jsonl")
    assert len(val_set_scores) == 685
    test_set_scores = read_scores("udonpred_trizod/test.jsonl")
    assert len(test_set_scores) == 348
    do_sanity_checks(training_set_scores, val_set_scores, test_set_scores)

    to_biotrainer_file(training_set_scores, val_set_scores, test_set_scores)
    print(f"Saved to {disorder_output}")


if __name__ == "__main__":
    main()
