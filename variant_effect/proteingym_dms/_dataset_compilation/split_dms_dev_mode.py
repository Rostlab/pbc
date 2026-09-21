import random
import pandas as pd

from pathlib import Path

DEVELOPMENT_MODE_SUBSAMPLE_RATIO = 0.4


def main():
    result_path = Path("../DMS_substitutions_pbc.csv")
    pgym_dms_reference_file_orig = Path("DMS_substitutions.csv")

    pgym_orig_df = pd.read_csv(pgym_dms_reference_file_orig)

    virus_identifier = "Virus"
    virus_df = pgym_orig_df[pgym_orig_df["taxon"] == virus_identifier]
    non_virus_df = pgym_orig_df[pgym_orig_df["taxon"] != virus_identifier]

    rng = random.Random(12)
    virus_sample = virus_df.sample(n=int(len(virus_df) * DEVELOPMENT_MODE_SUBSAMPLE_RATIO),
                                   random_state=rng.getstate()[1][0])
    non_virus_sample = non_virus_df.sample(n=int(len(non_virus_df) * DEVELOPMENT_MODE_SUBSAMPLE_RATIO),
                                           random_state=rng.getstate()[1][0])

    print(
        f"Virus development mode sample size: {len(virus_sample)} ({len(virus_df)} original, "
        f"percent: {len(virus_sample) / len(virus_df):.2%})")
    print(
        f"Non-virus development mode sample size: {len(non_virus_sample)} ({len(non_virus_df)} original, "
        f"percent: {len(non_virus_sample) / len(non_virus_df):.2%})")
    print(
        f"Total development mode sample size: {len(virus_sample) + len(non_virus_sample)} ({len(pgym_orig_df)} original,"
        f" percent: {(len(virus_sample) + len(non_virus_sample)) / len(pgym_orig_df):.2%})")

    pgym_orig_df["pbc_dev_mode"] = False
    pgym_orig_df.loc[virus_sample.index, "pbc_dev_mode"] = True
    pgym_orig_df.loc[non_virus_sample.index, "pbc_dev_mode"] = True

    pgym_orig_df.to_csv(result_path, index=False)

    changed_df = pd.read_csv(result_path)
    assert sum([1 for v in changed_df["pbc_dev_mode"] if v]) == len(virus_sample) + len(non_virus_sample)


if __name__ == "__main__":
    main()
