# Snapshot of data/interim

The gathering outputs (`data/interim/`, 2026-10-28) as a tar.gz split into two parts under GitHub's 100 MB file limit. `data/` itself stays gitignored; the raw downloads (`data/raw/`, 16 GB) are not included.

Restore, from the repository root:

    cat snapshots/interim.tgz.part0* | sha256sum   # compare with SHA256SUM.txt
    mkdir -p data
    cat snapshots/interim.tgz.part0* | tar xzf - -C data

See `docs/handover-classifying.md` for what each file is.
