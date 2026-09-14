# Frustration

## Description

The datasets provided here aim at predicting **local energetic frustration** at single-residue resolution
from sequence alone. Local frustration quantifies how well the native amino acid at a position is
energetically optimized for its structural environment: minimally frustrated residues stabilize the fold,
while highly frustrated residues carry unresolved energetic conflicts that are often associated with
functional reasons (binding sites, catalytic sites, allosteric couplings, ...).

Ground-truth labels were computed with [FrustratometeR](https://github.com/proteinphysiologylab/frustratometeR)
on high-quality 3D structures. The dataset is a subsample 
of the [Funstration dataset](https://huggingface.co/datasets/leuschj/Funstration) and is offered in
two flavors, sharing identical sequences, identifiers, splits and masks:

* **Regression** (`*_regression.fasta`): the continuous single-residue **frustration index** (FI).

* **Classification** (`*_classification.fasta`): the FI discretized into the three canonical
  frustration states, following [Ferreiro et al. 2007](https://doi.org/10.1073/pnas.0709915104) and
  [Freiberger et al. 2023](https://doi.org/10.1038/s41467-023-43801-2):

  The classes are strongly imbalanced, and the functionally most interesting class (`H`) is the
  minority class.

## Dataset Compilation

The provided datasets are a redundancy-reduced subsample of the
[**Funstration** dataset](https://huggingface.co/datasets/leuschj/Funstration) (983,212 domains,
186M annotated residues, 8,259 FunFams).

Subsampling to the datasets provided here
([`pp_pbc_dataset.ipynb`](https://github.com/leuschjanphilipp/FrustrAI-Seq)) (TODO):

* Target sizes of 8,000 / 1,000 / 1,000 (train / validation / test) drawn from the parent splits.
* Within each split, **16 domains per CATH topology** were drawn first (guaranteeing that every
  topology of the parent split is represented), and the remaining quota was filled by uniform random
  sampling from the leftover domains (`seed = 42`, `split = 0`). All 499 / 30 / 33 CATH topologies of the parent
  train / validation / test splits are retained.
* Duplicated full-length sequences were then removed (10,000 → 9,995 entries; a single protein can
  contribute several domains, e.g. `..._TED01` and `..._TED02`), which is why the splits are slightly
  below their target sizes.

**Important:** labels exist only for the residues of the annotated *domain*, not for the full protein.
Each entry carries the **full-length UniProt sequence** (so that the pLM sees the natural sequence
context and no artificial fragments), but only the residues belonging to the annotated TED/CATH domain
are labeled and unmasked. Across the datasets, 1,768,265 of 4,369,685 residues (40.5%) are annotated.

## Dataset Format

The datasets are provided in [biotrainer-ready](https://github.com/sacdallago/biotrainer) fasta format
(`residue_to_value` for regression, `residue_to_class` for classification).
Each entry contains a sequence and a header, providing the sequence id, the set (train/val/test),
the per-residue target and a mask. Targets and masks always have exactly the length of the sequence.

* `id` - `<AlphaFold DB accession>_<TED domain>`, e.g. `AF-A0A3M7S3Z4-F1-model_v4_TED01`.
* `SET` - `train`, `val` or `test`.
* `MASK` - one character per residue: `1` = residue belongs to the annotated domain and carries a
  valid label, `0` = unannotated sequence context, label is a placeholder and **must be ignored**.
* `TARGET` (regression) - frustration indices separated by `;`; unannotated positions are `999.0`.
* `TARGET` (classification) - one class character per residue (`H`/`N`/`M`); unannotated positions are
  filled with `N`. Note that this placeholder is **identical to the neutral class label** (a dedicated
  placeholder such as `X` was avoided so that the label alphabet stays at three classes) - applying the
  mask is therefore mandatory for the classification dataset, otherwise ~75% of all `N` labels are
  spurious.

## Dataset Analysis

### Classification

![Split Distribution](_dataset_analysis/frustration_classification_split_distribution.svg)

![Label Distribution](_dataset_analysis/frustration_classification_label_distribution.svg)

![Labels By Split Distribution](_dataset_analysis/frustration_classification_labels_by_split_distribution.svg)

![Sequence Length Distribution](_dataset_analysis/frustration_classification_sequence_length_distribution.svg)

### Regression

![Split Distribution](_dataset_analysis/frustration_regression_split_distribution.svg)

![Label Distribution](_dataset_analysis/frustration_regression_label_distribution.svg)

![Labels By Split Distribution](_dataset_analysis/frustration_regression_labels_by_split_distribution.svg)

![Sequence Length Distribution](_dataset_analysis/frustration_regression_sequence_length_distribution.svg)

## Dataset Benchmarks

The [FrustrAI-Seq paper](https://doi.org/10.64898/2026.02.03.703498) provides benchmarks for this task.
Note that these numbers refer to the **full** Funstration test set (48k domains, all 33 test
topologies), not to the 1,000-sequence subsample provided here, and that models were trained on the
full 887k-sequence training set with a maximum sequence length of 512 residues. Macro-averaged F1,
precision and recall are computed on the three frustration states, Pearson's *r* and MAE on the
continuous frustration index; classification metrics are derived from the binned regression output.

| Model | Macro F1 | Macro Prec. | Macro Rec. | Pearson *r* | MAE |
|-------|----------|-------------|------------|-------------|-----|
| Random (permuted labels) | 0.333 | 0.333 | 0.333 | 0.000 | 1.037 |
| Baseline (amino-acid-specific mean / majority class) | 0.534 | 0.534 | 0.561 | 0.757 | 0.446 |
| FrustraMPNN (3D structure input) | 0.677 | 0.688 | 0.668 | 0.764 | 0.462 |
| ESM2-650M + CNN | 0.681 | 0.783 | 0.654 | 0.824 | 0.388 |
| ProstT5 + CNN | 0.650 | 0.762 | 0.629 | 0.806 | 0.408 |
| ProtT5 + CNN | 0.699 | 0.797 | 0.670 | 0.839 | 0.366 |
| **FrustrAI-Seq** (ProtT5 + LoRA + class weights) | **0.739** | **0.807** | **0.710** | **0.859** | **0.336** |

## Citations

```bibtex
@Article{Leusch2026,
  author    = {Leusch, Jan-Philipp and Poley-Gil, Miriam and Fernandez-Martin, Miguel and Bordin, Nicola and Rost, Burkhard and Parra, R. Gonzalo and Heinzinger, Michael},
  title     = {FrustrAI-Seq: Scaling Local Energetic Frustration to the Protein Sequence Space},
  year      = {2026},
  month     = Feb,
  doi       = {10.64898/2026.02.03.703498},
  publisher = {openRxiv},
}
```

```bibtex
@Article{Ferreiro2007,
  author    = {Ferreiro, Diego U. and Hegler, Joseph A. and Komives, Elizabeth A. and Wolynes, Peter G.},
  journal   = {Proceedings of the National Academy of Sciences},
  title     = {Localizing frustration in native proteins and protein assemblies},
  year      = {2007},
  month     = dec,
  number    = {50},
  pages     = {19819--19824},
  volume    = {104},
  doi       = {10.1073/pnas.0709915104},
  publisher = {Proceedings of the National Academy of Sciences},
}
```

```bibtex
@Article{Rausch2021,
  author    = {Rausch, Atilio O. and Freiberger, Maria I. and Leonetti, Cesar O. and Luna, Diego M. and Radusky, Leandro G. and Wolynes, Peter G. and Ferreiro, Diego U. and Parra, R. Gonzalo},
  journal   = {Bioinformatics},
  title     = {FrustratometeR: an R-package to compute local frustration in protein structures, point mutants and MD simulations},
  year      = {2021},
  issn      = {1367-4803},
  month     = sep,
  number    = {18},
  pages     = {3038--3040},
  volume    = {37},
  doi       = {10.1093/bioinformatics/btab176},
}
```

```bibtex
@Article{Freiberger2023,
  author    = {Freiberger, Maria I. and Ruiz-Serra, Victoria and Pontes, Camila and Romero-Durana, Miguel and Galaz-Davison, Pablo and Ram{\'i}rez-Sarmiento, Cesar A. and Schuster, Claudio D. and Marti, Marcelo A. and Wolynes, Peter G. and Ferreiro, Diego U. and Parra, R. Gonzalo and Valencia, Alfonso},
  journal   = {Nature Communications},
  title     = {Local energetic frustration conservation in protein families and superfamilies},
  year      = {2023},
  issn      = {2041-1723},
  month     = dec,
  number    = {1},
  pages     = {8379},
  volume    = {14},
  doi       = {10.1038/s41467-023-43801-2},
  publisher = {Nature Publishing Group},
}
```

## Data licensing

* Source dataset: [**Funstration**](https://huggingface.co/datasets/leuschj/Funstration)
  (Leusch et al. 2026), available on the Hugging Face Hub.

The RAW data downloaded from the aforementioned publication is subject
to [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/), i.e. it may be shared and adapted for
any purpose as long as appropriate credit is given (please cite Leusch et al. 2026 above).
Modified data available in this repository falls under [MIT](https://opensource.org/licenses/MIT),
with the attribution requirement of the source dataset remaining in effect.
