import random

from typing import List, Set
from biotrainer_core.input_files import read_FASTA, write_FASTA
from biotrainer_core.data_classes import SequenceData

SAMPLE_RATIO_CASP = 0.4  # Higher ratio for the rather small datasets to keep a meaningful sample
SAMPLE_RATIO_SELECTED = 0.05
MAX_SEQ_LENGTH = 512

def filter_max_seq_length(seq_records: List[SequenceData]) -> List[SequenceData]:
    return [seq_record for seq_record in seq_records if len(seq_record.seq) <= MAX_SEQ_LENGTH]

def subsample_seq_records_for_contact_development_mode(seq_records: List[SequenceData], file_name: str) -> Set[str]:
    initial_n = len(seq_records)

    if initial_n < 100:
        sample_ratio = SAMPLE_RATIO_CASP
    else:
        sample_ratio = SAMPLE_RATIO_SELECTED
    rng = random.Random(14)
    sample = rng.sample(seq_records, int(len(seq_records) * sample_ratio))

    print(f"Subsampled {initial_n} sequences to {len(sample)} for contact development mode ({file_name}).")
    sample_ids = {seq_record.seq_id for seq_record in sample}
    assert len(sample_ids) == len(sample), "Duplicate sequence IDs found in the sample."

    return sample_ids


def main():
    all_files = ["casp14.fasta", "casp15.fasta", "selected_protein.fasta"]
    for file in all_files:
        seq_records = read_FASTA(file)

        # 1. Filter Length
        seq_records_filtered = filter_max_seq_length(seq_records)
        assert len(seq_records_filtered) > 0, "No sequences left after filtering by maximum sequence length."
        print(f"Filtered {len(seq_records)} sequences to {len(seq_records_filtered)} "
              f"by maximum sequence length ({file}).")

        # 2. Split to dev mode
        dev_mode_sample_ids = subsample_seq_records_for_contact_development_mode(seq_records_filtered, file_name=file)
        seq_records_updated = [seq_record.set_attribute(key="DEV_MODE",
                                                        value="True" if seq_record.seq_id in dev_mode_sample_ids else "False")
                               for seq_record in seq_records_filtered]
        assert len(seq_records_updated) == len(seq_records_filtered), "Sequence records were modified unexpectedly."

        file_stem = file.split(".")[0]
        result_file_path = f"../{file_stem}/extracted_sequences.fasta"
        write_FASTA(result_file_path, seq_records_updated)

        seq_records_loaded = read_FASTA(result_file_path)
        assert len(seq_records_loaded) == len(seq_records_updated), "Sequence records were modified unexpectedly during loading."
        assert sum([seq_record.get_attribute("DEV_MODE") == "True" for seq_record in seq_records_loaded]) == len(dev_mode_sample_ids), "Unexpected number of sequences marked as DEV_MODE=True."

if __name__ == "__main__":
    main()
