# Disorder - TriZOD

## Description

The dataset provided here aims at predicting protein disorder (continuous).
The disorder values used here are TriZOD scores.

## Dataset Compilation

The provided dataset is compiled as follows:

* Training, Validation, Test: The [UdonPred dataset](https://figshare.com/articles/dataset/UdonPred/31444642) was used.

## Dataset Format

The dataset is provided in [biotrainer-ready](https://github.com/sacdallago/biotrainer) fasta format.
Each entry contains a sequence and a header, providing the sequence id, the set (train/val/test),
the target scores (separated by ';') and masks (unresolved (0): disorder value == 999, otherwise resolved (1)).

## Dataset Benchmarks

The [UdonPred paper](https://doi.org/10.64898/2026.01.26.701679) provides benchmarks for the disorder prediction task
on various datasets, including the one presented here.

## Citations

* [TriZOD Score GitHub](https://github.com/MarkusHaak/trizod)

```bibtex
@article {UdonPred,
	author = {Schlensok, Julius and Wagemann, David and Senoner, Tobias and Haak, Markus and Rost, Burkhard},
	title = {UdonPred: Untangling Protein Intrinsic Disorder Prediction},
	elocation-id = {2026.01.26.701679},
	year = {2026},
	doi = {10.64898/2026.01.26.701679},
	publisher = {Cold Spring Harbor Laboratory},
	URL = {https://www.biorxiv.org/content/early/2026/01/28/2026.01.26.701679},
	eprint = {https://www.biorxiv.org/content/early/2026/01/28/2026.01.26.701679.full.pdf},
	journal = {bioRxiv}
}
```

## Data licensing

The RAW data downloaded from the aforementioned publications is subject
to [AGPL v3.0](https://www.gnu.org/licenses/agpl-3.0.en.html).
Modified data available in this repository falls under [AFL-3](https://opensource.org/licenses/AFL-3.0).
