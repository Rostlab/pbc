# This script is used to visualize the datasets

from tqdm import tqdm
from pathlib import Path

from biocentral import BiocentralChart
from biotrainer_core.input_files import read_FASTA


def _get_and_make_analysis_directory(dataset_path: Path):
    analysis_directory = dataset_path.parent / "_dataset_analysis"
    analysis_directory.mkdir(exist_ok=True)
    return analysis_directory


def _analyze_supervised(dataset_path: Path):
    analysis_directory = _get_and_make_analysis_directory(dataset_path)
    stem = dataset_path.stem
    sequence_data = read_FASTA(dataset_path)

    sequence_length_distribution = BiocentralChart.sequence_length_distribution(sequence_data)
    sequence_length_distribution.save(analysis_directory / f"{stem}_sequence_length_distribution.svg")

    labels_filter = lambda label: label != "999.0"

    label_distribution = BiocentralChart.label_distribution(sequence_data, labels_filter=labels_filter)
    label_distribution.save(analysis_directory / f"{stem}_label_distribution.svg")

    split_distribution = BiocentralChart.split_distribution(sequence_data)
    split_distribution.save(analysis_directory / f"{stem}_split_distribution.svg")

    labels_by_split_distribution = BiocentralChart.labels_by_split_distribution(sequence_data, labels_filter=labels_filter)
    labels_by_split_distribution.save(analysis_directory / f"{stem}_labels_by_split_distribution.svg")


def analyze_supervised(dataset_paths: list[Path]):
    for dataset_path in tqdm(dataset_paths, unit="dataset"):
        _analyze_supervised(dataset_path)


def analyze_contacts(dataset_paths: list[Path]):
    sequence_data = []
    for path in dataset_paths:
        sequences = read_FASTA(path)
        set_annotation = str(path).split("extracted_sequences.fasta")[0].split("/")[-2]
        sequences = [seq.set_attribute("set", set_annotation) for seq in sequences]
        sequence_data.extend(sequences)

    analysis_directory = Path("../contacts/_dataset_analysis")
    analysis_directory.mkdir(exist_ok=True)

    sequence_length_distribution = BiocentralChart.sequence_length_distribution(sequence_data)
    sequence_length_distribution.save(analysis_directory / f"contacts_sequence_length_distribution.svg")

    split_distribution = BiocentralChart.split_distribution(sequence_data)
    split_distribution.save(analysis_directory / f"contacts_split_distribution.svg")


def main():
    paths_supervised = [
        Path("../supervised/conservation/conservation.fasta"),
        Path("../supervised/phages/phages.fasta"),
        Path("../supervised/disorder_chezod/disorder_chezod.fasta"),
        Path("../supervised/frustration/frustration_classification.fasta"),
        Path("../supervised/frustration/frustration_regression.fasta"),
        Path("../supervised/scl/scl.fasta"),
        Path("../supervised/secondary_structure/secondary_structure.fasta"),
    ]
    analyze_supervised(paths_supervised)

    paths_contact = [
        Path("../contacts/supervised/train/extracted_sequences.fasta"),
        Path("../contacts/supervised/val/extracted_sequences.fasta"),
        Path("../contacts/zeroshot/casp14/extracted_sequences.fasta"),
        Path("../contacts/zeroshot/casp15/extracted_sequences.fasta"),
        Path("../contacts/zeroshot/selected_protein/extracted_sequences.fasta"),
    ]

    analyze_contacts(paths_contact)


if __name__ == "__main__":
    main()
