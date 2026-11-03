# Dataset

The original processed splits are distributed as gzip archives split into parts of
at most 6 MiB under `archives/`. These parts preserve the exact original JSONL
contents and fit GitHub's file upload limits.

From the repository root, restore all three splits with Python 3 (no additional
packages required):

```bash
python3 scripts/restore_data.py
```

The script verifies the SHA-256 checksum of every archive part, restores
`data/train.jsonl`, `data/val.jsonl`, and `data/test.jsonl`, and checks each output's
checksum, size, and record count against `archives/manifest.json`. Existing matching
files are verified and skipped. Existing different files are preserved unless you
explicitly pass `--force`.

To restore only the test split:

```bash
python3 scripts/restore_data.py --splits test
```

Allow about 3.3 GB of free disk space for restoring all splits, in addition to the
cloned repository. No Git LFS installation is needed. Do not unpack individual
`.partNNN` files separately; the script joins each split's parts in order.

`repos.txt` records the source repository pool. Java source excerpts retain the
licensing and attribution requirements of their respective upstream projects.
