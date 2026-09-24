# Zero-shot Contact Prediction

## Description
The datasets provided here are suitable for contact prediction task. In contact prediction, the input is a protein sequence of length L and the output is an L×L map of residue pairs indicating whether the pair is in contact or not. As ground truth, we consider pairs to be in contact if their Cβ atoms are within 8 Å.

## Dataset Format

There are three folders corresponding to the three datasets:
- **casp14** (96 samples)
- **casp15** (96 samples)
- **selected_protein** (1430 samples)
   
Each folder contains an `extracted_sequences.fasta` file which lists the sequences to be provided as input. The corresponding ground truth contact map per sequence is provided in the subfolder `contacts`. For example, for each sequence in extracted_sequences.fasta with ID `<id>`, the corresponding ground truth contact map can be found at `contacts/<id>.npy`. 

## Dataset Compilation

The **casp14** and **casp15** datasets contain sequences and contact maps extracted from domain-level structures in the official CASP14 and CASP15 datasets. For example, sequence with ID `T1024-D1` in `contacts/zeroshot/casp14/extracted_sequences.fasta` indicates D1 domain of T1024 from CASP14. 

Meanwhile the **selected_protein** dataset contains sequences and contact maps extracted from selected chain-level structures in RCSB PDB. For example, sequence with ID `1A8LA` in `contacts/zeroshot/selected_protein/extracted_sequences.fasta` indicates chain A of 1A8L from RCSB PDB. In this dataset, we re-used the same selection of sequences/chains as in https://github.com/zzhangzzhang/pLMs-interpretability/tree/main.

The sequences were extrcated from _pdb_ or _mmcif_ files using the script `dataset_compilation/pdb_to_contacts.py`, which drops hetero atoms and keeps only residues with a complete backbone (N, CA, C), so that the input sequence and the output contact map are in alignment. To obtain the ground truth, we followed the same approach as https://github.com/facebookresearch/esm/blob/main/examples/contact_prediction.ipynb, which marks residue pairs to be in contact if their Cβ atoms are within 8 Å.


## References

```bibtex
@article{rives2021biological,
  title={Biological structure and function emerge from scaling unsupervised learning to 250 million protein sequences},
  author={Rives, Alexander and Meier, Joshua and Sercu, Tom and Goyal, Siddharth and Lin, Zeming and Liu, Jason and Guo, Demi and Ott, Myle and Zitnick, C Lawrence and Ma, Jerry and others},
  journal={Proceedings of the national academy of sciences},
  volume={118},
  number={15},
  pages={e2016239118},
  year={2021},
  publisher={National Academy of Sciences}
}
```
```bibtex
@article{zhang2024protein,
  title={Protein language models learn evolutionary statistics of interacting sequence motifs},
  author={Zhang, Zhidian and Wayment-Steele, Hannah K and Brixi, Garyk and Wang, Haobo and Kern, Dorothee and Ovchinnikov, Sergey},
  journal={Proceedings of the National Academy of Sciences},
  volume={121},
  number={45},
  pages={e2406285121},
  year={2024},
  publisher={National Academy of Sciences}
}
```
```bibtex
@article{kryshtafovych2021critical,
  title={Critical assessment of methods of protein structure prediction (CASP)—Round XIV},
  author={Kryshtafovych, Andriy and Schwede, Torsten and Topf, Maya and Fidelis, Krzysztof and Moult, John},
  journal={Proteins: Structure, Function, and Bioinformatics},
  volume={89},
  number={12},
  pages={1607--1617},
  year={2021},
  publisher={Wiley Online Library}
}
```
```bibtex
@article{kryshtafovych2023critical,
  title={Critical assessment of methods of protein structure prediction (CASP)—Round XV},
  author={Kryshtafovych, Andriy and Schwede, Torsten and Topf, Maya and Fidelis, Krzysztof and Moult, John},
  journal={Proteins: Structure, Function, and Bioinformatics},
  volume={91},
  number={12},
  pages={1539--1549},
  year={2023},
  publisher={Wiley Online Library}
}
```



