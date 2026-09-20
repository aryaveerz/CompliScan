import os
import hashlib
import json
from pathlib import Path
from collections import defaultdict

repo_root = Path(r"G:\CompliScan")

file_records = []
hash_to_files = defaultdict(list)
extension_counts = defaultdict(int)
directory_counts = defaultdict(int)

# Skip scanning inside .git and node_modules for deep hashing if huge, but count totals
for root, dirs, files in os.walk(repo_root):
    # Don't recurse into .git
    if ".git" in root.split(os.sep):
        continue
    rel_root = os.path.relpath(root, repo_root)
    top_dir = rel_root.split(os.sep)[0] if rel_root != "." else "<root>"
    
    for f in files:
        full_path = Path(root) / f
        rel_path = os.path.relpath(full_path, repo_root)
        try:
            stat = full_path.stat()
            size = stat.st_size
            ext = full_path.suffix.lower() if full_path.suffix else "<no_ext>"
            
            # SHA-256 for small/medium files (< 50MB)
            sha = ""
            if size < 50 * 1024 * 1024 and not "node_modules" in rel_path:
                try:
                    hasher = hashlib.sha256()
                    with open(full_path, "rb") as fh:
                        while chunk := fh.read(65536):
                            hasher.update(chunk)
                    sha = hasher.hexdigest()
                    hash_to_files[sha].append(rel_path)
                except Exception as e:
                    sha = f"ERR: {e}"
            
            file_records.append({
                "path": rel_path,
                "top_dir": top_dir,
                "size": size,
                "ext": ext,
                "sha256": sha
            })
            extension_counts[ext] += 1
            directory_counts[top_dir] += 1
        except Exception as e:
            file_records.append({
                "path": rel_path,
                "top_dir": top_dir,
                "size": 0,
                "ext": "ERR",
                "sha256": f"ERR: {e}"
            })

# Find duplicates
duplicates = {sha: paths for sha, paths in hash_to_files.items() if len(paths) > 1 and sha}

summary = {
    "total_files": len(file_records),
    "total_size_bytes": sum(r["size"] for r in file_records),
    "extension_counts": dict(sorted(extension_counts.items(), key=lambda x: x[1], reverse=True)),
    "directory_counts": dict(sorted(directory_counts.items(), key=lambda x: x[1], reverse=True)),
    "duplicate_count": len(duplicates),
    "duplicates": duplicates,
}

with open(r"G:\CompliScan\scratch\repo_inventory_raw.json", "w", encoding="utf-8") as out:
    json.dump({"summary": summary, "files": file_records}, out, indent=2)

print("Inventory completed.")
print(f"Total files: {summary['total_files']}")
print(f"Total size: {summary['total_size_bytes'] / (1024*1024):.2f} MB")
print(f"Duplicates (identical SHA-256): {len(duplicates)}")
print("Top directories:", list(summary["directory_counts"].items())[:15])
