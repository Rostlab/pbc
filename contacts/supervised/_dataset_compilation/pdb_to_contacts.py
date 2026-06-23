"""
Convert PDB/CIF structures to contact maps (Cβ distance < threshold) and extract corresponding sequences.

Example:
  python pdb_to_contacts.py --input data/casp14/pdb-domain --out-dir ground_truth/casp14
"""

import argparse
from pathlib import Path
from typing import Iterable, List, Optional, Tuple

import numpy as np
from scipy.spatial.distance import pdist, squareform

import biotite.structure as bs
from biotite.structure import get_residue_starts
from biotite.structure.io.pdb import PDBFile
from biotite.structure.io.pdbx import CIFFile, get_structure

AA3TO1 = {
    'ALA': 'A', 'ARG': 'R', 'ASN': 'N', 'ASP': 'D', 'CYS': 'C',
    'GLN': 'Q', 'GLU': 'E', 'GLY': 'G', 'HIS': 'H', 'ILE': 'I',
    'LEU': 'L', 'LYS': 'K', 'MET': 'M', 'PHE': 'F', 'PRO': 'P',
    'SER': 'S', 'THR': 'T', 'TRP': 'W', 'TYR': 'Y', 'VAL': 'V',
}


def extend(a: np.ndarray, b: np.ndarray, c: np.ndarray, L: float, A: float, D: float) -> np.ndarray:
    """
    Reconstruct a fourth coordinate from three points, length, angle, dihedral.
    Matches logic from esm2_contact_prediction.ipynb.
    """

    def normalize(x: np.ndarray) -> np.ndarray:
        return x / np.linalg.norm(x, ord=2, axis=-1, keepdims=True)

    bc = normalize(b - c)
    n = normalize(np.cross(b - a, bc))
    m = [bc, np.cross(n, bc), n]
    d = [L * np.cos(A), L * np.sin(A) * np.cos(D), -L * np.sin(A) * np.sin(D)]
    return c + sum([m * d for m, d in zip(m, d)])


def load_atom_array(path: Path) -> bs.AtomArray:
    """
    Load PDB/CIF/mmCIF into a single AtomArray (first model).
    """
    suffix = path.suffix.lower()
    if suffix == ".pdb":
        arr = PDBFile.read(path).get_structure(model=1)
    elif suffix in {".cif", ".mmcif"}:
        arr = get_structure(CIFFile.read(path), model=1)
    else:
        raise ValueError(f"Unsupported file extension for {path}; only .pdb, .cif, .mmcif are supported.")
    if isinstance(arr, bs.AtomArrayStack):
        arr = arr[0]
    return arr


def contacts_from_pdb(
    structure: bs.AtomArray,
    distance_threshold: float = 8.0,
    chain: Optional[str] = None,
) -> Tuple[np.ndarray, str]:
    """
    Compute contact map and extract sequence from the same residue set.
    Only residues with complete backbone (N, CA, C) are included, 
    so that returned sequence and contact map are guaranteed to have 
    identical length and ordering.

    Returns (contacts, sequence) where contacts is an (L x L) int64 array.
    """
    mask = ~structure.hetero
    if chain is not None:
        mask &= structure.chain_id == chain

    ## original esm2_contact_prediction.ipynb code does below, but in our datasets there seem to be some missing N, CA, C atoms!
    # N = structure.coord[mask & (structure.atom_name == "N")]
    # CA = structure.coord[mask & (structure.atom_name == "CA")]
    # C = structure.coord[mask & (structure.atom_name == "C")]

    res_starts = get_residue_starts(structure)
    N_list, CA_list, C_list, seq_list = [], [], [], []
    for start, stop in zip(res_starts, np.append(res_starts[1:], len(structure))):
        res = structure[start:stop][mask[start:stop]]
        n  = res.coord[res.atom_name == "N"]
        ca = res.coord[res.atom_name == "CA"]
        c  = res.coord[res.atom_name == "C"]
        if len(n) == 1 and len(ca) == 1 and len(c) == 1:
            N_list.append(n[0])
            CA_list.append(ca[0])
            C_list.append(c[0])
            seq_list.append(AA3TO1.get(res.res_name[0], 'X'))
    if not N_list:
        raise ValueError("No residues with complete backbone (N, CA, C) after filtering.")
    N  = np.array(N_list)
    CA = np.array(CA_list)
    C  = np.array(C_list)

    Cbeta = extend(C, N, CA, 1.522, 1.927, -2.143)
    dist = squareform(pdist(Cbeta))
    contacts = (dist < distance_threshold).astype(np.int64)
    contacts[np.isnan(dist)] = -1

    return contacts, ''.join(seq_list)


def iter_structures(input_path: Path) -> Iterable[Path]:
    if input_path.is_file():
        yield input_path
        return
    for ext in ("*.pdb", "*.cif", "*.mmcif"):
        for p in sorted(input_path.glob(ext)):
            yield p


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert PDB/CIF to contact maps (.npy) and sequences (.fasta).")
    parser.add_argument("--input", required=True, help="PDB/CIF file or directory containing structures.")
    parser.add_argument("--out-dir", default=None, help="Output directory (default: alongside input).")
    parser.add_argument("--distance-threshold", type=float, default=8.0, help="Contact distance threshold (Å).")
    chain_group = parser.add_mutually_exclusive_group()
    chain_group.add_argument("--chain", default=None, help="Chain ID to extract from every structure.")
    chain_group.add_argument("--chain-from-filename", action="store_true",
                             help="Infer chain from last character of filename stem "
                                  "(e.g. 1B5QA.cif -> chain A). Use for selected_protein.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_path = Path(args.input)
    out_dir = Path(args.out_dir) if args.out_dir else (input_path if input_path.is_dir() else input_path.parent)
    out_dir.mkdir(parents=True, exist_ok=True)

    files: List[Path] = list(iter_structures(input_path))
    if not files:
        raise SystemExit(f"No structures found under {input_path}")

    fasta_entries: List[str] = []
    ok, failed = 0, 0
    for pdb_path in files:
        chain = pdb_path.stem[-1] if args.chain_from_filename else args.chain
        try:
            arr = load_atom_array(pdb_path)
            contacts, sequence = contacts_from_pdb(
                arr, distance_threshold=args.distance_threshold, chain=chain
            )
        except Exception as exc:
            print(f"FAILED {pdb_path.name}: {exc}")
            failed += 1
            continue

        np.save(out_dir / f"{pdb_path.stem}_contacts.npy", contacts)
        fasta_entries.append(f">{pdb_path.stem}\n{sequence}")
        print(f"OK     {pdb_path.name}: {len(sequence)} residues")
        ok += 1

    fasta_path = out_dir / "extracted_protein.fasta"
    fasta_path.write_text('\n'.join(fasta_entries) + '\n')
    print(f"\nWrote {fasta_path}")
    print(f"Done: {ok} succeeded, {failed} failed.")


if __name__ == "__main__":
    main()
