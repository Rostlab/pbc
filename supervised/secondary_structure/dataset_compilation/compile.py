import pandas as pd

sec_struct_flip = "sec_struct_flip.fasta"  # Training, Validation and new_pisces test set
casp12 = "CASP12.csv"  # CASP 12 Test Set
casp13 = "CASP13.csv"  # CASP 13 Test Set
casp14 = "CASP14.csv"  # CASP 14 Test Set
sec_struct_output = "secondary_structure.fasta"

def disorder_to_mask(disorder: str):
    cleaned_disorder = disorder.replace("[", "").replace("]", "").replace("\"", "")
    disorder_values = cleaned_disorder.split(", ") if "," in cleaned_disorder else cleaned_disorder.split(" ")
    return "".join([str(int(float(val))) for val in disorder_values])

# Append CASP Test Sets to FLIP dataset
test_lines = ""
for casp_name, casp_path in [("casp12", casp12), ("casp13", casp13), ("casp14", casp14)]:
    casp_df = pd.read_csv(casp_path)
    casp_idx = 0
    for _, row in casp_df.iterrows():
        sequence = row["input"]
        if sequence == "MNVDPHFDKFMESGIRHVYMLFENKSVESSEQFYSFMRTTYKNDPCSSDFECIERGAEMAQSYARIMNIKLETE":
            continue  # Duplicated sequence in CASP 14 and newPISCES364 - keep in newPISCES364

        dssp3 = row["dssp3"]  # secondary structure prediction in 3 states
        disorder = row["disorder"]
        mask = disorder_to_mask(disorder)
        assert len(sequence) == len(mask)
        assert len(sequence) == len(dssp3)
        assert len(mask) == len(dssp3)
        test_lines += f">{casp_name}-{casp_idx} TARGET={dssp3} SET={casp_name} MASK={mask}\n{sequence}\n"
        casp_idx += 1

with open(sec_struct_flip, "r") as sec_struct_flip_file, open(sec_struct_output, "w") as sec_struct_output_file:
    sec_struct_output_file.write(sec_struct_flip_file.read())
    sec_struct_output_file.write(test_lines)


# Replace old test set name with newPISCES364
with open(sec_struct_output, "r") as sec_struct_output_file:
    content = sec_struct_output_file.read()
    content = content.replace(" SET=test ", " SET=newPISCES364 ")

with open(sec_struct_output, "w") as sec_struct_output_file:
    sec_struct_output_file.write(content)


# Validate dataset
# Invariants
LEN_PISCES = 364
LEN_CASP12 = 20
LEN_CASP13 = 12
LEN_CASP14 = 18-1  # DUPLICATE
N_SEQUENCES = 22410/2
with open(sec_struct_output, "r") as sec_struct_output_file:
    lines = sec_struct_output_file.readlines()
    new_pisces = []
    casp12 = []
    casp13 = []
    casp14 = []
    sequences = []
    for line in lines:
        if "SET=" in line:
            set_name = line.split("SET=")[1].split(" ")[0].strip().upper()
            match set_name:
                case "NEWPISCES364":
                    new_pisces.append(line)
                case "CASP12":
                    casp12.append(line)
                case "CASP13":
                    casp13.append(line)
                case "CASP14":
                    casp14.append(line)
                case _:
                    assert set_name in ["TRAIN", "VAL"], f"Invalid set name: {set_name}"
        else:
            sequences.append(line)

    assert len(new_pisces) == LEN_PISCES, f"Invalid newPISCES length: {len(new_pisces)}"
    assert len(casp12) == LEN_CASP12, f"Invalid CASP12 length: {len(casp12)}"
    assert len(casp13) == LEN_CASP13, f"Invalid CASP13 length: {len(casp13)}"
    assert len(casp14) == LEN_CASP14, f"Invalid CASP14 length: {len(casp14)}"
    assert len(sequences) == len(set(sequences)), f"Duplicate sequences found!"
    assert len(sequences) == N_SEQUENCES, f"Invalid number of sequences: {len(sequences)}"