# Secondary Structure

## Description

The dataset provided here aims at predicting protein secondary structure (3-state).
The possible structure states for each residue (assigned to `TARGET`) are `C` (Coil), `H` (Helix) and `E` (Extended
strand - beta-sheet).

## Dataset Compilation

The provided dataset is compiled as follows:

* Training: [FLIP-sampled](https://github.com/J-SNACKKB/FLIP/tree/4363d5e07f096e4e4a3d0bfd7e6a5a21b2b79dad/splits/secondary_structure)
based on [the ProtT5 publication](https://doi.org/10.1109/tpami.2021.3095381)
* Validation: [FLIP-sampled](https://github.com/J-SNACKKB/FLIP/tree/4363d5e07f096e4e4a3d0bfd7e6a5a21b2b79dad/splits/secondary_structure)
based on [the ProtT5 publication](https://doi.org/10.1109/tpami.2021.3095381)
* Test:
    * newPISCES364: [FLIP-sampled](https://github.com/J-SNACKKB/FLIP/tree/4363d5e07f096e4e4a3d0bfd7e6a5a21b2b79dad/splits/secondary_structure)
    based on [the ProtT5 publication](https://doi.org/10.1109/tpami.2021.3095381)
    * CASP12: [HF: proteinea/secondary_structure_prediction](https://huggingface.co/datasets/proteinea/secondary_structure_prediction/tree/main)
    * CASP13: [HF: proteinea/secondary_structure_prediction](https://huggingface.co/datasets/proteinea/secondary_structure_prediction/tree/main)
    * CASP14: [HF: proteinea/secondary_structure_prediction](https://huggingface.co/datasets/proteinea/secondary_structure_prediction/tree/main)

*There was one sequence overlap between newPISCES364 and CASP14, which was kept in the newPISCES364 dataset and 
excluded from the CASP14 dataset.*

## Dataset Format

The dataset is provided in [biotrainer-ready](https://github.com/sacdallago/biotrainer) fasta format.
Each entry contains a sequence and a header, providing the sequence id, the set (train/val/test), the target label,
and a mask indicating if the target label should be used for calculating the loss.

## Dataset Benchmarks

The [ProtT5 paper](https://doi.org/10.1109/tpami.2021.3095381) provides a number of benchmarks for the dataset.

## Citations

```bibtex
@Article{klausen2019netsurfp,
title={NetSurfP-2.0: Improved prediction of protein structural features by integrated deep learning},
author={Klausen, Michael Schantz and Jespersen, Martin Closter and Nielsen, Henrik and Jensen, Kamilla Kjaergaard and Jurtz, Vanessa Isabell and Soenderby, Casper Kaae and Sommer, Morten Otto Alexander and Winther, Ole and Nielsen, Morten and Petersen, Bent and others},
journal={Proteins: Structure, Function, and Bioinformatics},
volume={87},
number={6},
pages={520--527},
year={2019},
publisher={Wiley Online Library}
}
```

```bibtex
@Article{9477085,
author={Elnaggar, Ahmed and Heinzinger, Michael and Dallago, Christian and Rehawi, Ghalia and Wang, Yu and Jones, Llion and Gibbs, Tom and Feher, Tamas and Angerer, Christoph and Steinegger, Martin and Bhowmik, Debsindhu and Rost, Burkhard},
journal={IEEE Transactions on Pattern Analysis and Machine Intelligence},
title={ProtTrans: Towards Cracking the Language of Lifes Code Through Self-Supervised Deep Learning and High Performance Computing},
year={2021},
volume={},
number={},
pages={1-1},
doi={10.1109/TPAMI.2021.3095381}
}
```

```bibtex
@Article{moult2018critical,
title={Critical assessment of methods of protein structure prediction (CASP)—Round XII},
author={Moult, John and Fidelis, Krzysztof and Kryshtafovych, Andriy and Schwede, Torsten and Tramontano, Anna},
journal={Proteins: Structure, Function, and Bioinformatics},
volume={86},
pages={7--15},
year={2018},
publisher={Wiley Online Library}
}
```

```bibtex
@Article{Kryshtafovych2019,
  author    = {Kryshtafovych, Andriy and Schwede, Torsten and Topf, Maya and Fidelis, Krzysztof and Moult, John},
  journal   = {Proteins: Structure, Function, and Bioinformatics},
  title     = {Critical assessment of methods of protein structure prediction (CASP)—Round XIII},
  year      = {2019},
  issn      = {1097-0134},
  month     = oct,
  number    = {12},
  pages     = {1011--1020},
  volume    = {87},
  doi       = {10.1002/prot.25823},
  publisher = {Wiley},
}
```

```bibtex
@Article{Kinch2021,
  author    = {Kinch, Lisa N. and Schaeffer, R. Dustin and Kryshtafovych, Andriy and Grishin, Nick V.},
  journal   = {Proteins: Structure, Function, and Bioinformatics},
  title     = {Target classification in the 14th round of the critical assessment of protein structure prediction (CASP14)},
  year      = {2021},
  issn      = {1097-0134},
  month     = aug,
  number    = {12},
  pages     = {1618--1632},
  volume    = {89},
  doi       = {10.1002/prot.26202},
  publisher = {Wiley},
}
```

## Data licensing

The RAW data downloaded from the aforementioned publications is subject
to [Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/).
Modified data available in this repository falls under [AFL-3](https://opensource.org/licenses/AFL-3.0).

This is an Open Access article distributed under the terms of the Creative Commons Attribution
License (https://creativecommons.org/licenses/by/4.0/), which permits unrestricted reuse, distribution, and reproduction
in any medium, provided the original work is properly cited.
