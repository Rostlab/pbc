# Phages

## Description

Targets:  {'integration_and_excision', 'connector', 'lysis', 'tail', 'head_and_packaging', 'moron_auxiliary_metabolic_gene_and_host_takeover', 'transcription_regulation', 'other', 'DNA_RNA_and_nucleotide_metabolism'}


## Dataset Compilation

The provided dataset is compiled as follows:

* Training, Validation, Test: Random split (Train 75%, Val 15%, Test 10%).

## Dataset Format

The dataset is provided in [biotrainer-ready](https://github.com/sacdallago/biotrainer) fasta format.
Each entry contains a sequence and a header, providing the sequence id, the set (train/val/test),
and the target class.


## Citations

* **TODO**

## Data licensing

* **TODO**

The RAW data downloaded from the aforementioned publications is subject
to [AGPL v3.0](https://www.gnu.org/licenses/agpl-3.0.en.html).
Modified data available in this repository falls under [AFL-3](https://opensource.org/licenses/AFL-3.0).
