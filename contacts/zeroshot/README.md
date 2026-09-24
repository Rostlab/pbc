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

The **casp14** and **casp15** datasets contain sequences and contact maps extracted from domain-level structures in the official CASP14 and CASP15 datasets {TODO: ask Michael about selection criteria for casp15? citation?}. For example, sequence with ID `T1024-D1` in `contacts/zeroshot/casp14/extracted_sequences.fasta` indicates D1 domain of T1024 from CASP14. 

Meanwhile the **selected_protein** dataset contains sequences and contact maps extracted from selected chain-level structures in RCSB PDB. For example, sequence with ID `1A8LA` in `contacts/zeroshot/selected_protein/extracted_sequences.fasta` indicates A chain of 1A8LA from RCSB PDB. In this dataset, we re-used the same selection of sequences/chains as in {TODO: add citation to Sergey's work?}.

The sequences were extrcated from _pdb_ or _mmcif_ files using the script `dataset_compilation/pdb_to_contacts.py`, which drops hetero atoms and keeps only residues with a complete backbone (N, CA, C), so that the input sequence and the output contact map are in alignment. To obtain the ground truth, we followed the same approach as https://github.com/facebookresearch/esm/blob/main/examples/contact_prediction.ipynb {TODO: cite paper too?}, which marks residue pairs to be in contact if their Cβ atoms are within 8 Å.




