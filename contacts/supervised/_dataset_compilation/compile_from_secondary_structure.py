import random
from pathlib import Path

import biotite.database.rcsb as rcsb
from biotrainer_core.input_files import read_FASTA

from pdb_to_contacts import load_atom_array, contacts_from_pdb
import numpy as np

SECONDARY_STRUCTURE_FILE = "../../../supervised/secondary_structure/secondary_structure.fasta"


def main():
    sequence_data = read_FASTA(SECONDARY_STRUCTURE_FILE)
    train_set = [data_point for data_point in sequence_data if data_point.set == "train"]
    assert len(train_set) == 9712

    val_set = [data_point for data_point in sequence_data if data_point.set == "val"]
    assert len(val_set) == 1080

    twenty_random_indices_train = random.sample(range(len(train_set)), 20)
    assert len(twenty_random_indices_train) == 20

    twenty_random_indices_val = random.sample(range(len(val_set)), 20)
    assert len(twenty_random_indices_val) == 20

    all_seq_ids = {train_set[idx].seq_id: "train"
                   for idx in twenty_random_indices_train}
    all_seq_ids.update({val_set[idx].seq_id: "val" for idx in twenty_random_indices_val})

    assert len(all_seq_ids) == 40

    # Download from PDB if not already downloaded in ./pdb_files
    pdb_dir = Path("./pdb_files")
    pdb_dir.mkdir(exist_ok=True)

    fasta_entries_train = []
    fasta_entries_val = []

    for seq_id, split in all_seq_ids.items():
        print(f"Processing {seq_id} ({split})")
        # Expected format: PDBID-CHAIN (e.g. 1es5-A)
        if "-" in seq_id:
            pdb_id, chain = seq_id.split("-")
        else:
            pdb_id = seq_id
            chain = None

        pdb_path = pdb_dir / f"{pdb_id}.pdb"
        if not pdb_path.exists():
            try:
                rcsb.fetch(pdb_id, "pdb", pdb_dir)
            except Exception as e:
                print(f"Failed to download {pdb_id}: {e}")
                continue

        # Apply pdb_to_contacts.py to get contacts
        try:
            structure = load_atom_array(pdb_path)
            contacts, sequence = contacts_from_pdb(structure, chain=chain)

            out_dir = Path(f"../{split}/contacts/")
            out_dir.mkdir(parents=True, exist_ok=True)
            contact_map_output_path = out_dir / f"{seq_id}.npy"

            np.save(contact_map_output_path, contacts)
            if split == "train":
                fasta_entries_train.append(f">{seq_id}\n{sequence}")
            else:
                fasta_entries_val.append(f">{seq_id}\n{sequence}")
            print(f"OK     {seq_id}: {len(sequence)} residues")
        except Exception as e:
            print(f"FAILED {seq_id}: {e}")

    fasta_path_train = Path("../train") / "extracted_sequences.fasta"
    fasta_path_val = Path("../val") / "extracted_sequences.fasta"
    fasta_path_train.write_text('\n'.join(fasta_entries_train) + '\n')
    fasta_path_val.write_text('\n'.join(fasta_entries_val) + '\n')
    print(f"\nWrote {fasta_path_train}")
    print(f"Wrote {fasta_path_val}")


if __name__ == "__main__":
    main()