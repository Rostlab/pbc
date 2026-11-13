# This script is used to visualize the datasets

from tqdm import tqdm
from pathlib import Path
from typing import Union
import pandas as pd
import altair as alt

from biocentral import BiocentralChart
from biotrainer_core.input_files import read_FASTA


def _get_and_make_analysis_directory(dataset_path: Path):
    analysis_directory = dataset_path.parent / "_dataset_analysis"
    analysis_directory.mkdir(exist_ok=True)
    return analysis_directory


def _postprocess_chart(chart: BiocentralChart):
    chart.chart = chart.chart.properties(
        width=600,
        height=400,
    ).configure_axis(
        labelFontSize=18,
        titleFontSize=22
    ).configure_title(
        fontSize=24,
        font='Liberation Sans'
    ).configure_legend(
        labelFontSize=18,
        titleFontSize=22
    )
    return chart


def _analyze_supervised(dataset_path: Path):
    analysis_directory = _get_and_make_analysis_directory(dataset_path)
    stem = dataset_path.stem
    sequence_data = read_FASTA(dataset_path)

    sequence_length_distribution = BiocentralChart.sequence_length_distribution(sequence_data)
    sequence_length_distribution = _postprocess_chart(sequence_length_distribution)
    sequence_length_distribution.save(analysis_directory / f"{stem}_sequence_length_distribution.svg")

    labels_filter = lambda label: label != "999.0"

    label_distribution = BiocentralChart.label_distribution(sequence_data, labels_filter=labels_filter)
    label_distribution = _postprocess_chart(label_distribution)
    label_distribution.save(analysis_directory / f"{stem}_label_distribution.svg")

    split_distribution = BiocentralChart.split_distribution(sequence_data)
    split_distribution = _postprocess_chart(split_distribution)
    split_distribution.save(analysis_directory / f"{stem}_split_distribution.svg")

    labels_by_split_distribution = BiocentralChart.labels_by_split_distribution(sequence_data,
                                                                                labels_filter=labels_filter)
    labels_by_split_distribution = _postprocess_chart(labels_by_split_distribution)
    labels_by_split_distribution.save(analysis_directory / f"{stem}_labels_by_split_distribution.svg")


def analyze_supervised_or_unsupervised(dataset_paths: list[Path]):
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
    sequence_length_distribution = _postprocess_chart(sequence_length_distribution)
    sequence_length_distribution.save(analysis_directory / f"contacts_sequence_length_distribution.svg")

    split_distribution = BiocentralChart.split_distribution(sequence_data)
    split_distribution = _postprocess_chart(split_distribution)
    split_distribution.save(analysis_directory / f"contacts_split_distribution.svg")


def plot_assay_type_by_taxonomy(
        reference_file: Union[Path, str, pd.DataFrame]
) -> alt.Chart:
    """
    Plots the distribution of coarse_selection_type against Taxonomy (Virus / Non-Virus).
    """
    if isinstance(reference_file, (str, Path)):
        df = pd.read_csv(reference_file)
    else:
        df = reference_file.copy()

    df["Taxonomy"] = df["taxon"].apply(
        lambda x: "Virus" if str(x).strip().lower() == "virus" else "Non-Virus"
    )

    chart = (
        alt.Chart(df)
        .mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3)
        .encode(
            x=alt.X(
                "coarse_selection_type:N",
                title="Assay Type",
                axis=alt.Axis(labelAngle=0),
            ),
            y=alt.Y("count():Q", title="Number of DMS Assays"),
            color=alt.Color(
                "Taxonomy:N",
                title="Taxonomy",
                scale=alt.Scale(
                    domain=["Non-Virus", "Virus"],
                    range=["#2b5c8f", "#d97724"],
                ),
            ),
            xOffset=alt.XOffset("Taxonomy:N", sort=["Non-Virus", "Virus"]),
            tooltip=[
                alt.Tooltip("Taxonomy:N", title="Taxonomy"),
                alt.Tooltip("coarse_selection_type:N", title="Assay Type"),
                alt.Tooltip("count():Q", title="Count"),
            ],
        )
        .properties(
            width=600,
            height=400,
            title=alt.TitleParams(
                text="Distribution of Assay Types by Taxonomy",
                fontSize=24,
                font="Liberation Sans",
                anchor="start",
            ),
        )
        .configure_axis(labelFontSize=18, titleFontSize=22)
        .configure_title(fontSize=24, font="Liberation Sans")
        .configure_legend(labelFontSize=18, titleFontSize=22)
    )

    return chart


def _without_top_level_config(chart: alt.Chart) -> alt.Chart:
    """
    Return a copy of an Altair chart without its top-level config.

    Altair does not allow charts with a top-level ``config`` attribute to be
    used inside compound charts such as ``alt.hconcat``. Individual charts may
    still be saved with their configs, but config-free copies should be used
    when composing charts.
    """
    chart_copy = chart.copy()
    chart_copy.config = alt.Undefined
    return chart_copy

def analyze_variant_effect(path_to_datasets: Path):
    import os

    from biocentral import BiocentralChart
    from biotrainer_core.input_files import parse_pgym_file
    save_path = _get_and_make_analysis_directory(path_to_datasets)

    reference_file = path_to_datasets.parent / "DMS_substitutions_pbc.csv"
    assay_chart = plot_assay_type_by_taxonomy(reference_file)
    assay_chart.save(os.path.join(save_path, "pgym_assay_distribution.svg"))

    csv_files = [file for file in os.listdir(path_to_datasets) if file.endswith(".csv")]
    all_variants = []
    for pgym_file in csv_files:
        all_variants.extend(parse_pgym_file(os.path.join(path_to_datasets, pgym_file)))

    mutation_chart = BiocentralChart.mutation_depth_distribution([vs.variant for vs in all_variants])

    mutation_chart_for_saving = _postprocess_chart(mutation_chart)
    mutation_chart_for_saving.save(os.path.join(save_path, "pgym_mutation_depth_distribution.svg"))

    combined = alt.hconcat(
        _without_top_level_config(mutation_chart.chart).properties(width=600, height=400),
        _without_top_level_config(assay_chart)
    ).resolve_scale(
        color="independent"
    ).configure_view(
        stroke=None
    ).configure_axis(
        labelFontSize=18,
        titleFontSize=22
    ).configure_title(
        fontSize=24,
        font="Liberation Sans"
    ).configure_legend(
        labelFontSize=18,
        titleFontSize=22
    )

    combined.save(os.path.join(save_path, "pgym_combined.pdf"))


def main():
    path_variant_effect = [
        Path("../variant_effect/proteingym_dms/DMS_ProteinGym_substitutions")
    ]
    analyze_variant_effect(path_variant_effect[0])

    paths_supervised = [
        Path("../supervised/conservation/conservation.fasta"),
        Path("../supervised/phages/phages.fasta"),
        Path("../supervised/disorder_chezod/disorder_chezod.fasta"),
        Path("../supervised/frustration/frustration_classification.fasta"),
        Path("../supervised/frustration/frustration_regression.fasta"),
        Path("../supervised/scl/scl.fasta"),
        Path("../supervised/secondary_structure/secondary_structure.fasta"),
    ]
    analyze_supervised_or_unsupervised(paths_supervised)

    paths_unsupervised = [
        Path("../unsupervised/cath/cath.fasta")
    ]
    analyze_supervised_or_unsupervised(paths_unsupervised)

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
