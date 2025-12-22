#!/usr/bin/env python3
"""
Create a zip archive containing a predefined set of project files compatible with the biotrainer autoeval module.
"""

import sys
import zipfile
from pathlib import Path

from sanity_check_datasets import sanity_check


def main() -> None:
    # Resolve repository root as the parent of this script's directory
    script_path = Path(__file__).resolve()
    repo_root = script_path.parent.parent  # scripts/ -> project root

    zip_file_name = "AUTOEVAL_PBC.zip"
    # Files to include (relative to repo root)
    include_paths = [
        Path("LICENSE"),
        Path("README.md"),
        Path("supervised/binding/binding_combined.fasta"),
        Path("supervised/binding/binding_metal.fasta"),
        Path("supervised/binding/binding_nuclear.fasta"),
        Path("supervised/binding/binding_small.fasta"),
        Path("supervised/binding/README.md"),
        Path("supervised/conservation/conservation.fasta"),
        Path("supervised/conservation/README.md"),
        Path("supervised/disorder/disorder.fasta"),
        Path("supervised/disorder/README.md"),
        Path("supervised/membrane/membrane.fasta"),
        Path("supervised/membrane/README.md"),
        Path("supervised/scl/scl.fasta"),
        Path("supervised/scl/README.md"),
        Path("supervised/secondary_structure/secondary_structure.fasta"),
        Path("supervised/secondary_structure/README.md"),
    ]
    fasta_file_paths = [Path("..") / file for file in include_paths if file.name.endswith(".fasta")]
    sanity_check(fasta_file_paths)

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


if __name__ == "__main__":
    main()
