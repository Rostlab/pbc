# SCL (SubCellularLocation)

## Description

The dataset provided here aims at predicting protein subcellular location.
The possible subcellular localizations (assigned to `TARGET`) are `Cytoplasm`, `Nucleus`,
`Cell membrane`, `Mitochondrion`, `Endoplasmic reticulum`, `Lysosome/Vacuole`, `Golgi apparatus`, `Peroxisome`,
`Extracellular` and `Plastid`.

## Dataset Compilation

The provided dataset is the `mixed_hard` split from the
[FLIP scl split repository](https://github.com/J-SNACKKB/FLIP/tree/4363d5e07f096e4e4a3d0bfd7e6a5a21b2b79dad/splits/scl)
with remapped UniProt ids.
It contains [LightAttention dataset](https://academic.oup.com/bioinformaticsadvances/article/1/1/vbab035/6432029),
namely
the [LightAttention train split](https://github.com/HannesStark/protein-localization/blob/7b0be1e64a91db8ad1a8feae994a4d09aa9d7b1b/data_files/deeploc_our_train_set.fasta),
the [LightAttention validation split](https://github.com/HannesStark/protein-localization/blob/7b0be1e64a91db8ad1a8feae994a4d09aa9d7b1b/data_files/deeploc_our_val_set.fasta),
which were both derived from
the [DeepLoc 1.0 publication](https://academic.oup.com/bioinformatics/article/33/21/3387/3931857),
and
the [LightAttention setHard test set](https://github.com/HannesStark/protein-localization/blob/7b0be1e64a91db8ad1a8feae994a4d09aa9d7b1b/data_files/setHARD.fasta),

## Dataset Format

The dataset is provided in [biotrainer-ready](https://github.com/sacdallago/biotrainer) fasta format.
Each entry contains a sequence and a header, providing the sequence id, the set (train/val/test) and the target label.

## Dataset Benchmarks

![LightAttention-Benchmarks](https://oup.silverchair-cdn.com/oup/backfile/Content_public/Journal/bioinformaticsadvances/1/1/10.1093_bioadv_vbab035/2/m_vbab035f2.jpeg?Expires=1763717766&Signature=IPN~pjw1qn2o8c7dr9zLYzETVYpXPkZVHZxb34XqwCeb7eA2lSF-zc7dc7nzunDB9kKdBCD2qsNdW-LsrBTMlekUF-BGELohKay0mjrN3Y7X1WNms1AhfMtriGTDDrk5OuO1q7sD71-snT-JIkJpcxWv4AR2QCvwFc7No4VarEcjL30nAJYI6LPZbKuFxIHqT1-8KZ~9XS1NxvXGJiL6jH5TJFlTSlDVkN66Cur8B3SfYySTyd6-xB2zpYoz59sUhxMIfJ7ruWg-CnySfIeBi~oxQNka3IJ-sDg7l~bmexCk3tS08J-4IRdrPwaQ-ldIzXfBld3gzzPu0D5BFVgSwA__&Key-Pair-Id=APKAIE5G5CRDK6RD3PGA "SCL-LightAttention Benchmarks")

The [LightAttention paper](https://academic.oup.com/bioinformaticsadvances/article/1/1/vbab035/6432029) provides a
number of benchmarks for the dataset.

## Citations

```bibtex
@article{10.1093/bioadv/vbab035,
author = {Stärk, Hannes and Dallago, Christian and Heinzinger, Michael and Rost, Burkhard},
title = "{Light attention predicts protein location from the language of life}",
journal = {Bioinformatics Advances},
volume = {1},
number = {1},
year = {2021},
month = {11},
abstract = "{Although knowing where a protein functions in a cell is important to characterize biological processes, this information remains unavailable for most known proteins. Machine learning narrows the gap through predictions from expert-designed input features leveraging information from multiple sequence alignments (MSAs) that is resource expensive to generate. Here, we showcased using embeddings from protein language models for competitive localization prediction without MSAs. Our lightweight deep neural network architecture used a softmax weighted aggregation mechanism with linear complexity in sequence length referred to as light attention. The method significantly outperformed the state-of-the-art (SOTA) for 10 localization classes by about 8 percentage points (Q10). So far, this might be the highest improvement of just embeddings over MSAs. Our new test set highlighted the limits of standard static datasets: while inviting new models, they might not suffice to claim improvements over the SOTA.The novel models are available as a web-service at http://embed.protein.properties. Code needed to reproduce results is provided at https://github.com/HannesStark/protein-localization. Predictions for the human proteome are available at https://zenodo.org/record/5047020.Supplementary data are available at Bioinformatics Advances online.}",
issn = {2635-0041},
doi = {10.1093/bioadv/vbab035},
url = {https://doi.org/10.1093/bioadv/vbab035},
note = {vbab035},
eprint = {https://academic.oup.com/bioinformaticsadvances/article-pdf/1/1/vbab035/41640353/vbab035.pdf},
}
```

```bibtex
@article{10.1093/bioinformatics/btx431,
author = {Almagro Armenteros, José Juan and Sønderby, Casper Kaae and Sønderby, Søren Kaae and Nielsen, Henrik and Winther, Ole},
title = "{DeepLoc: prediction of protein subcellular localization using deep learning}",
journal = {Bioinformatics},
volume = {33},
number = {21},
pages = {3387-3395},
year = {2017},
month = {07},
abstract = "{The prediction of eukaryotic protein subcellular localization is a well-studied topic in bioinformatics due to its relevance in proteomics research. Many machine learning methods have been successfully applied in this task, but in most of them, predictions rely on annotation of homologues from knowledge databases. For novel proteins where no annotated homologues exist, and for predicting the effects of sequence variants, it is desirable to have methods for predicting protein properties from sequence information only.Here, we present a prediction algorithm using deep neural networks to predict protein subcellular localization relying only on sequence information. At its core, the prediction model uses a recurrent neural network that processes the entire protein sequence and an attention mechanism identifying protein regions important for the subcellular localization. The model was trained and tested on a protein dataset extracted from one of the latest UniProt releases, in which experimentally annotated proteins follow more stringent criteria than previously. We demonstrate that our model achieves a good accuracy (78\\% for 10 categories; 92\\% for membrane-bound or soluble), outperforming current state-of-the-art algorithms, including those relying on homology information.The method is available as a web server at http://www.cbs.dtu.dk/services/DeepLoc. Example code is available at https://github.com/JJAlmagro/subcellular\_localization. The dataset is available at http://www.cbs.dtu.dk/services/DeepLoc/data.php.}",
issn = {1367-4803},
doi = {10.1093/bioinformatics/btx431},
url = {https://doi.org/10.1093/bioinformatics/btx431},
eprint = {https://academic.oup.com/bioinformatics/article-pdf/33/21/3387/25166063/btx431.pdf},
}
```

```bibtex
@article {Dallago2021.11.09.467890,
	author = {Dallago, Christian and Mou, Jody and Johnston, Kadina E. and Wittmann, Bruce J. and Bhattacharya, Nicholas and Goldman, Samuel and Madani, Ali and Yang, Kevin K.},
	title = {FLIP: Benchmark tasks in fitness landscape inference for proteins},
	elocation-id = {2021.11.09.467890},
	year = {2022},
	doi = {10.1101/2021.11.09.467890},
	publisher = {Cold Spring Harbor Laboratory},
	URL = {https://www.biorxiv.org/content/early/2022/01/19/2021.11.09.467890},
	eprint = {https://www.biorxiv.org/content/early/2022/01/19/2021.11.09.467890.full.pdf},
	journal = {bioRxiv}
}
```

## Data licensing

The RAW data downloaded from the aforementioned publications is subject
to [Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/).
Modified data available in this repository falls under [AFL-3](https://opensource.org/licenses/AFL-3.0).

This is an Open Access article distributed under the terms of the Creative Commons Attribution
License (https://creativecommons.org/licenses/by/4.0/), which permits unrestricted reuse, distribution, and reproduction
in any medium, provided the original work is properly cited.
