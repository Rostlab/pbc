# Protein (language model) Benchmarking Collection - PBC

This repository contains well-established datasets for interpretable and reliable 
protein language model (pLM) benchmarking.

## Datasets

All included datasets are listed below. Details and files can be found in the respective folders.

### Supervised

* [conservation](supervised/conservation)
* [subcellular location](supervised/scl)
* [secondary structure](supervised/secondary_structure)

## Benchmarking

If you want to benchmark a new or existing pLM on these datasets, please check out one of the following methods:

* [biotrainer: autoeval](https://github.com/sacdallago/biotrainer) - Automatic evaluation of pLMs on our supervised
  benchmark datasets. You can find an example
  notebook [here](https://github.com/sacdallago/biotrainer/tree/main/examples/autoeval).
* **BETA** [biocentral: plm_eval](https://app.biocentral.cloud) - Automatic evaluation of pLMs on all benchmark
  datasets, including a visual leaderboard and model-to-model comparison.