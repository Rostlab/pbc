"""
Script to summarize statistics and generate publication-ready plots for PBC supervised datasets.
"""

from pathlib import Path
from typing import Dict, List, Any, Optional
import numpy as np
import pandas as pd
import altair as alt

from biotrainer_core.input_files import read_FASTA


SUPERVISED_DATASETS = [
    {
        "name": "Conservation",
        "key": "conservation",
        "path": Path("supervised/conservation/conservation.fasta"),
        "level": "Residue",
        "task_type": "Classification (9-state)",
        "task_type_short": "Classification",
        "source": "Marquet et al. (2021) / FLIP",
    },
    {
        "name": "Disorder (CheZOD)",
        "key": "disorder_chezod",
        "path": Path("supervised/disorder_chezod/disorder_chezod.fasta"),
        "level": "Residue",
        "task_type": "Regression (CheZOD score)",
        "task_type_short": "Regression",
        "source": "Nielsen & Mulder (2020) / SETH",
    },
    {
        "name": "Frustration (Class.)",
        "key": "frustration_classification",
        "path": Path("supervised/frustration/frustration_classification.fasta"),
        "level": "Residue",
        "task_type": "Classification (3-class: H/N/M)",
        "task_type_short": "Classification",
        "source": "Leusch et al. (2026)",
    },
    {
        "name": "Frustration (Regr.)",
        "key": "frustration_regression",
        "path": Path("supervised/frustration/frustration_regression.fasta"),
        "level": "Residue",
        "task_type": "Regression (Frustration Index)",
        "task_type_short": "Regression",
        "source": "Leusch et al. (2026)",
    },
    {
        "name": "Phages",
        "key": "phages",
        "path": Path("supervised/phages/phages.fasta"),
        "level": "Sequence",
        "task_type": "Classification (9-class)",
        "task_type_short": "Classification",
        "source": "Bouras et al. (2026) / PHROG v4",
    },
    {
        "name": "Subcellular Loc. (SCL)",
        "key": "scl",
        "path": Path("supervised/scl/scl.fasta"),
        "level": "Sequence",
        "task_type": "Classification (10-class)",
        "task_type_short": "Classification",
        "source": "Stärk et al. (2021) / DeepLoc",
    },
    {
        "name": "Secondary Structure",
        "key": "secondary_structure",
        "path": Path("supervised/secondary_structure/secondary_structure.fasta"),
        "level": "Residue",
        "task_type": "Classification (3-state: C/H/E)",
        "task_type_short": "Classification",
        "source": "Elnaggar et al. (2021) / CASP 12-14",
    },
]


def collect_statistics(datasets: List[Dict[str, Any]], base_path: Path = Path(".")) -> (pd.DataFrame, pd.DataFrame, pd.DataFrame):
    """
    Parses datasets and computes sequence-level, split-level, and length distributions.
    """
    summary_records = []
    split_records = []
    length_records = []

    datasets = sorted(datasets, key=lambda d: d["level"])

    for d in datasets:
        dataset_path = base_path / d["path"] if not d["path"].is_absolute() else d["path"]
        if not dataset_path.exists():
            # Try looking relative to script location or parent directory
            alt_path = Path(__file__).resolve().parent.parent / d["path"]
            if alt_path.exists():
                dataset_path = alt_path
            else:
                raise FileNotFoundError(f"Dataset fasta not found at {dataset_path} or {alt_path}")

        seq_records = read_FASTA(dataset_path)
        lengths = [len(s.seq) for s in seq_records]
        total_seqs = len(seq_records)
        total_res = sum(lengths)

        # Split breakdown
        split_counts: Dict[str, int] = {}
        split_residues: Dict[str, int] = {}
        for s in seq_records:
            s_set = s.set
            split_counts[s_set] = split_counts.get(s_set, 0) + 1
            split_residues[s_set] = split_residues.get(s_set, 0) + len(s.seq)
            length_records.append({
                "Dataset": d["name"],
                "Key": d["key"],
                "Length": len(s.seq),
                "Set": s.set,
            })

        for s_set, count in split_counts.items():
            split_records.append({
                "Dataset": d["name"],
                "Key": d["key"],
                "Set": s_set,
                "Sequences": count,
                "Residues": split_residues[s_set],
            })

        # Annotated residue counts
        annotated_res = 0
        if d["level"] == "Residue":
            for s in seq_records:
                if hasattr(s, "mask") and s.mask is not None:
                    annotated_res += sum(1 for m in s.mask if str(m) == "1")
                elif ";" in (s.label or ""):
                    vals = s.label.split(";")
                    annotated_res += sum(1 for v in vals if v not in ("999.0", "999", ""))
                else:
                    annotated_res += len(s.seq)
        else:
            annotated_res = total_res

        train_c = split_counts.get("train", 0)
        val_c = split_counts.get("val", 0)
        test_c = sum(v for k, v in split_counts.items() if k not in ("train", "val"))
        test_detail = ", ".join(f"{k}: {v}" for k, v in split_counts.items() if k not in ("train", "val"))

        summary_records.append({
            "Dataset": d["name"],
            "Key": d["key"],
            "Level": d["level"],
            "Task Type": d["task_type"],
            "Task Type Short": d["task_type_short"],
            "Total Seqs": total_seqs,
            "Train Seqs": train_c,
            "Val Seqs": val_c,
            "Test Seqs": test_c,
            "Test Split Details": test_detail,
            "Total Residues": total_res,
            "Annotated Residues": annotated_res,
            "Len Min": int(min(lengths)),
            "Len Median": int(np.median(lengths)),
            "Len Mean": round(float(np.mean(lengths)), 1),
            "Len Max": int(max(lengths)),
            "Source / Reference": d["source"],
        })

    return pd.DataFrame(summary_records), pd.DataFrame(split_records), pd.DataFrame(length_records)


def generate_markdown_table(df_summary: pd.DataFrame) -> str:
    """
    Generates a Markdown formatted table from the summary dataframe.
    """
    display_df = df_summary.copy()
    headers = [col for col in display_df.columns if col not in ("Key",)]
    rows = []
    header_line = "| " + " | ".join(headers) + " |"
    sep_line = "| " + " | ".join(["---"] * len(headers)) + " |"
    rows.append(header_line)
    rows.append(sep_line)
    for _, r in display_df.iterrows():
        row_str = "| " + " | ".join(str(r[h]) for h in headers) + " |"
        rows.append(row_str)
    return "\n".join(rows)


def generate_latex_table(df_summary: pd.DataFrame) -> str:
    """
    Generates a publication-ready LaTeX table formatted with booktabs.
    """
    lines = [
        r"\begin{table*}[t]",
        r"\centering",
        r"\small",
        r"\caption{Overview of Supervised Benchmark Datasets in PBC.}",
        r"\label{tab:pbc_supervised_datasets}",
        r"\begin{tabular}{llrrrrrrc}",
        r"\toprule",
        r"\textbf{Dataset} & \textbf{Level} & \textbf{Task Type} & \textbf{Total Seqs} & \textbf{Train} & \textbf{Val} & \textbf{Test} & \textbf{Residues} & \textbf{Mean Length} \\",
        r"\midrule",
    ]

    for _, row in df_summary.iterrows():
        name = row["Dataset"]
        level = row["Level"]
        task = row["Task Type Short"]
        tot_seq = f"{row['Total Seqs']:,}"
        train = f"{row['Train Seqs']:,}"
        val = f"{row['Val Seqs']:,}"
        test = f"{row['Test Seqs']:,}"
        annot = f"{row['Annotated Residues']:,}"
        length_str = f"{row['Len Mean']:.0f}"
        lines.append(f"{name} & {level} & {task} & {tot_seq} & {train} & {val} & {test} & {annot} & {length_str} \\\\")

    lines.extend([
        r"\bottomrule",
        r"\end{tabular}",
        r"\end{table*}",
    ])
    return "\n".join(lines)


def _create_separator_with_annotation(y_position: float = 4.5,
                                      annotation_text: str = "Residue | Sequence") -> alt.LayerChart:
    """
    Creates a horizontal separator line with annotation to distinguish dataset levels.
    
    Args:
        y_position: Y-coordinate for the separator line
        annotation_text: Text to display next to the separator
    
    Returns:
        Layered chart with separator line and annotation
    """
    separator = alt.Chart(pd.DataFrame({'y': [y_position]})).mark_rule(
        strokeDash=[5, 5],
        stroke='gray',
        strokeWidth=1.5,
        opacity=0.6
    ).encode(
        y=alt.Y('y:Q', scale=alt.Scale(domain=[-0.5, 6.5]))
    )

    annotation = alt.Chart(pd.DataFrame({
        'y': [y_position],
        'text': [annotation_text]
    })).mark_text(
        align='left',
        dx=5,
        dy=-8,
        fontSize=10,
        color='gray',
        fontStyle='italic'
    ).encode(
        y=alt.Y('y:Q', scale=alt.Scale(domain=[-0.5, 6.5])),
        text='text:N'
    )

    return separator + annotation


def plot_dataset_splits(df_splits: pd.DataFrame, output_prefix: Optional[Path] = None,
                        is_subplot: bool = False) -> alt.Chart:
    """
    Creates a publication-quality stacked bar chart of dataset sequences by split.
    """
    color_scale = alt.Scale(
        domain=["train", "val", "test", "newPISCES364", "casp12", "casp13", "casp14"],
        range=["#2b5c8f", "#d97724", "#2ca02c", "#17becf", "#9467bd", "#e377c2", "#8c564b"]
    )

    # Add a Level column to the dataframe for grouping
    df_with_level = df_splits.copy()
    level_map = {ds['name']: ds['level'] for ds in SUPERVISED_DATASETS}
    df_with_level['Level'] = df_with_level['Dataset'].map(level_map)

    y_axis = alt.Axis(labelFontSize=12) if is_subplot else alt.Axis(labelFontSize=13, titleFontSize=14)
    x_axis = alt.Axis(labelFontSize=11, titleFontSize=12) if is_subplot else alt.Axis(labelFontSize=12, titleFontSize=14)
    legend = (
        alt.Legend(title="Split", labelFontSize=11, titleFontSize=12)
        if is_subplot
        else alt.Legend(title="Data Split", labelFontSize=12, titleFontSize=13)
    )
    title = (
        alt.TitleParams(text="A: Dataset Size by Split", fontSize=14, anchor="start")
        if is_subplot
        else alt.TitleParams(text="Supervised Datasets: Sequence Count by Split", fontSize=16, anchor="start")
    )
    width = 400 if is_subplot else 550
    height = 260 if is_subplot else 280

    chart = alt.Chart(df_with_level).mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3).encode(
        y=alt.Y("Dataset:N", sort=None, title="" if is_subplot else "Dataset", axis=y_axis),
        x=alt.X("Sequences:Q", title="Number of Sequences", axis=x_axis),
        color=alt.Color("Set:N", scale=color_scale, legend=legend),
        tooltip=["Dataset:N", "Set:N", "Sequences:Q", "Residues:Q"]
    ).properties(
        width=width,
        height=height,
        title=title
    )

    # Add separator with annotation
    separator = _create_separator_with_annotation(y_position=4.5, annotation_text="Level: Residue | Sequence")
    chart_with_separator = chart + separator

    if is_subplot:
        return chart_with_separator

    combined_chart = chart_with_separator.configure_view(stroke=None)
    if output_prefix is not None:
        combined_chart.save(f"{output_prefix}_split_distribution.svg")
    return combined_chart


def plot_length_distributions(df_lengths: pd.DataFrame, output_prefix: Optional[Path] = None,
                              is_subplot: bool = False) -> alt.Chart:
    """
    Creates a boxplot comparing protein sequence length distributions across datasets.
    """
    # Add a Level column to the dataframe for grouping
    df_with_level = df_lengths.copy()
    level_map = {ds['name']: ds['level'] for ds in SUPERVISED_DATASETS}
    df_with_level['Level'] = df_with_level['Dataset'].map(level_map)

    y_axis = alt.Axis(labels=False, ticks=False) if is_subplot else alt.Axis(labelFontSize=13, titleFontSize=14)
    x_axis = alt.Axis(labelFontSize=11, titleFontSize=12) if is_subplot else alt.Axis(labelFontSize=12, titleFontSize=14)
    x_title = "Sequence Length (log scale)" if is_subplot else "Sequence Length (Amino Acids, log scale)"
    title = (
        alt.TitleParams(text="B: Sequence Length Distribution", fontSize=14, anchor="start")
        if is_subplot
        else alt.TitleParams(text="Supervised Datasets: Sequence Length Distributions", fontSize=16, anchor="start")
    )
    width = 400 if is_subplot else 550
    height = 260 if is_subplot else 280
    box_size = 20 if is_subplot else 24
    box_color = "#2b5c8f" if is_subplot else "#4c78a8"

    chart = alt.Chart(df_with_level).mark_boxplot(extent=1.5, size=box_size, color=box_color).encode(
        y=alt.Y("Dataset:N", sort=None, title="" if is_subplot else "Dataset", axis=y_axis),
        x=alt.X(
            "Length:Q",
            scale=alt.Scale(type="log"),
            title=x_title,
            axis=x_axis
        ),
        tooltip=["Dataset:N", "Length:Q"]
    ).properties(
        width=width,
        height=height,
        title=title
    )

    # Add separator with annotation
    separator = _create_separator_with_annotation(y_position=4.5, annotation_text="Level: Residue | Sequence")
    chart_with_separator = chart + separator

    if is_subplot:
        return chart_with_separator

    combined_chart = chart_with_separator.configure_view(stroke=None)
    if output_prefix is not None:
        combined_chart.save(f"{output_prefix}_length_distribution.svg")
    return combined_chart


def plot_combined_overview(df_splits: pd.DataFrame, df_lengths: pd.DataFrame,
                           df_summary: Optional[pd.DataFrame] = None,
                           output_prefix: Optional[Path] = None) -> alt.Chart:
    """
    Creates a 2-panel combined overview figure suitable for papers.
    Reuses plot_dataset_splits and plot_length_distributions logic.
    """
    chart_splits = plot_dataset_splits(df_splits, is_subplot=True)
    chart_lengths = plot_length_distributions(df_lengths, is_subplot=True)

    combined = alt.hconcat(
        chart_splits,
        chart_lengths
    ).resolve_scale(
        color="independent"
    ).configure_view(
        stroke=None
    ).configure_axis(
        labelFontSize=11,
        titleFontSize=12
    )

    if output_prefix is not None:
        combined.save(f"{output_prefix}_combined_overview.pdf")
        combined.save(f"{output_prefix}_combined_overview.svg")
    return combined


def main():
    output_dir = Path("../supervised/_dataset_analysis")
    output_dir.mkdir(parents=True, exist_ok=True)

    print("Analyzing supervised datasets...")
    df_summary, df_splits, df_lengths = collect_statistics(SUPERVISED_DATASETS)

    # Save CSVs
    summary_csv = output_dir / "supervised_datasets_summary.csv"
    df_summary.to_csv(summary_csv, index=False)
    print(f"Saved summary CSV: {summary_csv}")

    # Save LaTeX table
    latex_code = generate_latex_table(df_summary)
    latex_path = output_dir / "supervised_datasets_table.tex"
    with open(latex_path, "w") as f:
        f.write(latex_code)
    print(f"Saved LaTeX table: {latex_path}")

    # Generate plots
    plot_prefix = output_dir / "supervised"
    plot_dataset_splits(df_splits, plot_prefix)
    print(f"Saved split distribution plot: {plot_prefix}_split_distribution.svg")

    plot_length_distributions(df_lengths, plot_prefix)
    print(f"Saved length distribution plot: {plot_prefix}_length_distribution.svg")

    plot_combined_overview(df_splits, df_lengths, df_summary, plot_prefix)
    print(f"Saved combined overview plot: {plot_prefix}_combined_overview.svg")

    print("\n" + "=" * 80)
    print("DATASET SUMMARY TABLE (MARKDOWN)")
    print("=" * 80)
    markdown_table = generate_markdown_table(df_summary)
    print(markdown_table)
    md_path = output_dir / "supervised_datasets_table.md"
    with open(md_path, "w") as f:
        f.write(markdown_table)
    print(f"Saved Markdown table: {md_path}")

    print("\n" + "=" * 80)
    print("LATEX TABLE CODE")
    print("=" * 80)
    print(latex_code)


if __name__ == "__main__":
    main()
