#!/usr/bin/env python3
"""
Create a zip archive containing a predefined set of project files compatible with the biotrainer autoeval module.
"""

import sys
import zipfile
from pathlib import Path

from sanity_check_datasets import sanity_check_supervised, sanity_check_contacts


def zip_supervised(repo_root: Path):
    zip_file_name = "AUTOEVAL_PBC_SUPERVISED.zip"
    # Files to include (relative to repo root)
    include_paths = [
        Path("LICENSE"),
        Path("README.md"),
        Path("supervised/conservation/conservation.fasta"),
        Path("supervised/conservation/README.md"),
        Path("supervised/disorder_chezod/disorder_chezod.fasta"),
        Path("supervised/disorder_chezod/README.md"),
        Path("supervised/disorder_trizod/disorder_trizod.fasta"),
        Path("supervised/disorder_trizod/README.md"),
        Path("supervised/phages/phages.fasta"),
        Path("supervised/phages/README.md"),
        Path("supervised/membrane/membrane.fasta"),
        Path("supervised/membrane/README.md"),
        Path("supervised/frustration/frustration_classification.fasta"),
        Path("supervised/frustration/frustration_regression.fasta"),
        Path("supervised/frustration/README.md"),
        Path("supervised/scl/scl.fasta"),
        Path("supervised/scl/README.md"),
        Path("supervised/secondary_structure/secondary_structure.fasta"),
        Path("supervised/secondary_structure/README.md"),
    ]
    fasta_file_paths = [Path("..") / file for file in include_paths if file.name.endswith(".fasta")]
    sanity_check_supervised(fasta_file_paths)

    # Archive output path (in repo root)
    archive_path = repo_root / zip_file_name

    # Validate that files exist
    missing = [str(p) for p in include_paths if not (repo_root / p).is_file()]
    if missing:
        msg = (
                "The following required files are missing and cannot be added to the archive:\n"
                + "\n".join(missing)
        )
        print(msg, file=sys.stderr)
        sys.exit(1)

    # Create zip archive and add files preserving relative paths
    with zipfile.ZipFile(archive_path, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        for rel_path in include_paths:
            abs_path = repo_root / rel_path
            save_path = rel_path
            # arcname ensures paths inside zip are relative to project root
            zf.write(abs_path, arcname=str(save_path))

    print(f"Created archive: {archive_path}")
    print("Included files:")
    for rel_path in include_paths:
        print(f" - {rel_path}")


def zip_contacts(repo_root: Path):
    zip_file_name = "AUTOEVAL_PBC_CONTACTS.zip"

    fasta_paths_to_check = [
        Path("../contacts/zeroshot/casp14/extracted_sequences.fasta"),
        Path("../contacts/zeroshot/casp15/extracted_sequences.fasta"),
        Path("../contacts/zeroshot/selected_protein/extracted_sequences.fasta"),
        Path("../contacts/supervised/train/extracted_sequences.fasta"),
        Path("../contacts/supervised/val/extracted_sequences.fasta"),
    ]

    sanity_check_contacts(fasta_paths_to_check)

    include_paths = [
        Path("LICENSE"),
        Path("README.md"),
        Path("contacts/zeroshot/casp14"),
        Path("contacts/zeroshot/casp15"),
        Path("contacts/zeroshot/selected_protein"),
        Path("contacts/supervised/train"),
        Path("contacts/supervised/val"),
    ]

    copy_paths = {Path("contacts/zeroshot/casp14"): Path("contacts/supervised/casp14"),
                  Path("contacts/zeroshot/casp15"): Path("contacts/supervised/casp15"),
                  Path("contacts/zeroshot/selected_protein"): Path("contacts/supervised/selected_protein")}

    # Archive output path (in repo root)
    archive_path = repo_root / zip_file_name

    # Validate that files exist
    missing = [str(p) for p in include_paths if not (repo_root / p).is_file() and not (repo_root / p).is_dir()]
    if missing:
        msg = (
                "The following required files are missing and cannot be added to the archive:\n"
                + "\n".join(missing)
        )
        print(msg, file=sys.stderr)
        sys.exit(1)

    # Create zip archive and add files preserving relative paths
    with zipfile.ZipFile(archive_path, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        for rel_path in include_paths:
            abs_path = repo_root / rel_path
            save_path = rel_path
            if abs_path.is_dir():
                # Add directory and all its contents recursively
                for file_path in abs_path.rglob("*"):
                    if file_path.is_file():
                        arcname = rel_path / file_path.relative_to(abs_path)
                        zf.write(file_path, arcname=str(arcname))
            else:
                # arcname ensures paths inside zip are relative to project root
                zf.write(abs_path, arcname=str(save_path))

        # Copy paths to destination in the zip file
        for source_path, dest_path in copy_paths.items():
            abs_source_path = repo_root / source_path
            if abs_source_path.is_dir():
                # Add directory and all its contents recursively to destination
                for file_path in abs_source_path.rglob("*"):
                    if file_path.is_file():
                        arcname = dest_path / file_path.relative_to(abs_source_path)
                        zf.write(file_path, arcname=str(arcname))
            else:
                # Copy single file to destination
                zf.write(abs_source_path, arcname=str(dest_path))

    print(f"Created archive: {archive_path}")
    print("Included files:")
    for rel_path in include_paths:
        print(f" - {rel_path}")


def main() -> None:
    # Resolve repository root as the parent of this script's directory
    script_path = Path(__file__).resolve()
    repo_root = script_path.parent.parent  # scripts/ -> project root

    zip_supervised(repo_root)
    zip_contacts(repo_root)


if __name__ == "__main__":
    main()
