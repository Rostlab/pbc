# Phages

## Description

The phage dataset comes from the PHROG v4 database (Terzian et al., 2021) with functional labels curated and expanded as
part of Phold (Bouras et al., 2026). PHROG is a database of 38,880 prokaryotic virus protein clusters with manually
curated per-protein functional labels given by experts in Terzian et al. Each protein cluster has a broad 9-class
functional category label specifically designed for prokaryotic viruses:

* integration_and_excision
* connector
* lysis
* tail
* head_and_packaging
* moron_auxiliary_metabolic_gene_and_host_takeover
* transcription_regulation
* other
* DNA_RNA_and_nucleotide_metabolism
* or unknown function (excluded from consideration in this benchmark).

Some functional category annotations of unknown function proteins (per PHROGs v4) were further curated by Bouras et al.
using manual annotation guided by heuristics based on protein structural homology.

To curate this dataset, all 440,550 non-redundant PHROG v4 protein sequences with predicted structures as part of Bouras
et al., 2026 were clustered with `foldseek cluster` (no sequence identity or coverage thresholds, so very stringent),
yielding 59,501 clusters. From these foldseek cluster representatives, only one representative per PHROG group with a
functional category was kept, yielding 5,131 proteins.

## Dataset Compilation

The provided dataset is compiled as follows:

* Training, Validation, Test: Random split (Train 75%, Val 15%, Test 10%).

## Dataset Format

The dataset is provided in [biotrainer-ready](https://github.com/sacdallago/biotrainer) fasta format.
Each entry contains a sequence and a header, providing the sequence id, the set (train/val/test),
and the target class.

## Citations

```bibtex
@article{terzian_phrog_2021,
	title = {{PHROG}: families of prokaryotic virus proteins clustered using remote homology},
	volume = {3},
	issn = {2631-9268},
	shorttitle = {{PHROG}},
	url = {https://doi.org/10.1093/nargab/lqab067},
	doi = {10.1093/nargab/lqab067},
	number = {3},
	urldate = {2023-05-23},
	journal = {NAR Genomics and Bioinformatics},
	author = {Terzian, Paul and Olo Ndela, Eric and Galiez, Clovis and Lossouarn, Julien and Pérez Bucio, Rubén Enrique and Mom, Robin and Toussaint, Ariane and Petit, Marie-Agnès and Enault, François},
	month = sep,
	year = {2021},
	pages = {lqab067},
}

@article{bouras_protein_2026,
	title = {Protein structure-informed bacteriophage genome annotation with {Phold}},
	volume = {54},
	issn = {1362-4962},
	url = {https://doi.org/10.1093/nar/gkaf1448},
	doi = {10.1093/nar/gkaf1448},
	number = {1},
	urldate = {2026-02-11},
	journal = {Nucleic Acids Research},
	author = {Bouras, George and Grigson, Susanna R and Mirdita, Milot and Heinzinger, Michael and Papudeshi, Bhavya and Mallawaarachchi, Vijini and Green, Renee and Kim, Rachel Seongeun and Mihalia, Victor and Psaltis, Alkis James and Wormald, Peter-John and Vreugde, Sarah and Steinegger, Martin and Edwards, Robert A},
	month = jan,
	year = {2026},
	pages = {gkaf1448},
}
```

## Data licensing

The RAW data downloaded from the aforementioned publications is subject
to [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
Modified data available in this repository falls under [AFL-3](https://opensource.org/licenses/AFL-3.0).
