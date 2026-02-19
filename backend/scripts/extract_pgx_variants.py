import gzip

INPUT_VCF = "C:/Users/KumarShivrajBhakat/Downloads/HG001.gz"

OUTPUT_VCF = "sample_data/filtered/mini_pgx.vcf"

count = 0

TARGET_RSIDS = {
    "rs3892097",
    "rs4244285",
    "rs12248560",
    "rs1057910",
    "rs4149056",
    "rs1142345",
    "rs3918290"
}

def open_vcf(path):
    if path.endswith(".gz"):
        return gzip.open(path, "rt")
    return open(path, "r")

with open_vcf(INPUT_VCF) as fin, open(OUTPUT_VCF, "w") as fout:
    for line in fin:
        # keep header lines
        if line.startswith("#"):
            fout.write(line)
            continue

        parts = line.split("\t")
        rsid = parts[2]

        rsid = parts[2]
        info = parts[7]

        if rsid in TARGET_RSIDS or any(r in info for r in TARGET_RSIDS):
            fout.write(line)
            count += 1



print("Mini VCF created:", OUTPUT_VCF)
