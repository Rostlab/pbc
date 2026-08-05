# Binding

## Description

The datasets provided here aim at predicting protein binding (2-state).
We provide the following four datasets:
* `binding_metal.fasta`: Binding to metal ions (0/1)
* `binding_nuclear.fasta`: Binding to nucleic acids (0/1)
* `binding_small.fasta`: Binding to small molecules (0/1)
* `binding_combined.fasta`: Binding to metal, nucleic acids OR small molecules (0/1)

## Dataset Compilation

The provided dataset was compiled from the 
[data provided in the bindEmbed repository](https://github.com/Rostlab/bindPredict/tree/master/data). 

* Training: Data from the [development set](https://github.com/Rostlab/bindPredict/tree/master/data/development_set)
* Validation: Stratified random 10% split of training
* Test: Data from the [independent set](https://github.com/Rostlab/bindPredict/tree/master/data/independent_set)

## Dataset Format

The dataset is provided in [biotrainer-ready](https://github.com/sacdallago/biotrainer) fasta format.
Each entry contains a sequence and a header, providing the sequence id, the set (train/val/test) and the target label.

## Dataset Benchmarks

The [bindEmbed paper](https://doi.org/10.1038/s41598-021-03431-4) contains benchmarks 
for the binding prediction tasks. The [TestSetNew46](https://www.nature.com/articles/s41598-021-03431-4/figures/1)
is the independent set used for these datasets.

## Citations

```bibtex
@Article{Littmann2021b,
  author    = {Littmann, Maria and Heinzinger, Michael and Dallago, Christian and Weissenow, Konstantin and Rost, Burkhard},
  journal   = {Scientific Reports},
  title     = {Protein embeddings and deep learning predict binding residues for various ligand classes},
  year      = {2021},
  issn      = {2045-2322},
  month     = dec,
  number    = {1},
  volume    = {11},
  doi       = {10.1038/s41598-021-03431-4},
  publisher = {Springer Science and Business Media LLC},
}
```

## Data licensing

The RAW data downloaded from the aforementioned publication is subject
to the [MIT license](https://opensource.org/license/MIT).
Modified data available in this repository falls under [AFL-3](https://opensource.org/licenses/AFL-3.0).
