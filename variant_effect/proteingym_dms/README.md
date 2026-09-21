# ProteinGYM DMS Development Mode Subsample

This directory provides the [development mode reference file](DMS_substitutions_pbc.csv) augmented by the
`pbc_dev_mode` column. It is added by the [split_dms_dev_mode.py](_dataset_compilation/split_dms_dev_mode.py) script 
and applied to the original 
[ProteinGym DMS reference file](https://marks.hms.harvard.edu/proteingym/ProteinGym_v1.3/DMS_substitutions.csv) 
(version 1.3).

## Dataset Generation

The development IDs are split such that they match about 40% of the original dataset size. This is to provide a 
reliable benchmarking for protein language models in less time while not testing on the full evaluation set.

The DMS_id(s) are split as follows:
```text
Virus development mode sample size: 12 (31 original, percent: 38.71%)
Non-virus development mode sample size: 74 (186 original, percent: 39.78%)
Total development mode sample size: 86 (217 original, percent: 39.63%)
```

## Citation

```bibtex
@InProceedings{Notin2023,
  author    = {Notin, Pascal and Kollasch, Aaron and Ritter, Daniel and van Niekerk, Lood and Paul, Steffanie and Spinner, Han and Rollins, Nathan and Shaw, Ada and Orenbuch, Rose and Weitzman, Ruben and Frazer, Jonathan and Dias, Mafalda and Franceschi, Dinko and Gal, Yarin and Marks, Debora},
  booktitle = {Advances in Neural Information Processing Systems},
  title     = {ProteinGym: Large-Scale Benchmarks for Protein Fitness Prediction and Design},
  year      = {2023},
  editor    = {A. Oh and T. Naumann and A. Globerson and K. Saenko and M. Hardt and S. Levine},
  pages     = {64331--64379},
  publisher = {Curran Associates, Inc.},
  volume    = {36},
  url       = {https://proceedings.neurips.cc/paper_files/paper/2023/file/cac723e5ff29f65e3fcbb0739ae91bee-Paper-Datasets_and_Benchmarks.pdf},
}
```

## License

The ProteinGym project is licensed under the [MIT](https://opensource.org/licenses/MIT) license.
Modified data available in this repository falls under [MIT](https://opensource.org/licenses/MIT).
The license of individual data sets in the protein gym benchmarks may vary.
