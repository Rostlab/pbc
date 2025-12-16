# Membrane

## Description

The dataset provided here aims at predicting protein membrane state (9-state).
The possible membrane states for each residue (assigned to `TARGET`) are the following:
- `B`/`b`: Transmembrane beta strand
- `H`/`h`: Transmembrane alpha helix
- `S`: Signal peptide
- `1`: Non-Transmembrane, inside
- `2`: Non-Transmembrane, outside
- `U`: Unknown/Unresolved in PDB

## Dataset Compilation

The provided dataset was compiled from the 
[data provided in the TMbed repository](https://github.com/BernhoferM/TMbed/tree/main/data). The cross-validation (CV)
splits there were used to create hold-out splits for training, validation and testing. Additionally, all sequences from
the `predictions/blacklist.txt` were removed.

* Training: CV splits 1-4 (4520 sequences)
* Validation: Random 10% split of training (497 sequences)
* Test: CV split 0 (1265 sequences)

## Dataset Format

The dataset is provided in [biotrainer-ready](https://github.com/sacdallago/biotrainer) fasta format.
Each entry contains a sequence and a header, providing the sequence id, the set (train/val/test), the target label
and a mask (0 if U(nknown) else 1).

## Dataset Benchmarks

The [TMbed paper](https://link.springer.com/article/10.1186/s12859-022-04873-x) contains benchmarks 
for the membrane prediction task.

## Citations

```bibtex
@Article{Bernhofer2022,
  author    = {Michael Bernhofer and Burkhard Rost},
  journal   = {{BMC} Bioinformatics},
  title     = {{TMbed}: transmembrane proteins predicted through language model embeddings},
  year      = {2022},
  month     = {aug},
  number    = {1},
  volume    = {23},
  doi       = {10.1186/s12859-022-04873-x},
  publisher = {Springer Science and Business Media {LLC}},
}
```

## Data licensing

The RAW data downloaded from the aforementioned publication is subject
to the [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0.html).
Modified data available in this repository falls under [AFL-3](https://opensource.org/licenses/AFL-3.0).
