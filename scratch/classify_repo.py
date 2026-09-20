import os
import hashlib
import json
from pathlib import Path
from collections import defaultdict

repo_root = Path(r"G:\CompliScan")

def classify_file(rel_path, size, ext):
    norm = rel_path.replace("\\", "/")
    
    # 1. Node modules, dist, build artifacts, caches
    if "node_modules" in norm:
        return "GENERATED_ARTIFACT"
    if "__pycache__" in norm or ".pytest_cache" in norm:
        return "GENERATED_ARTIFACT"
    if norm.startswith("frontend/dist"):
        return "GENERATED_ARTIFACT"
    if norm.endswith((".db", ".db-journal", ".log", ".tmp")):
        return "TEMPORARY_ARTIFACT"

    # 2. Local uploads in backend
    if "uploads/" in norm or norm.startswith("backend/uploads") or norm.startswith("backend/backend/uploads"):
        return "TEMPORARY_ARTIFACT"

    # 3. Dependencies & Deployment config
    if norm in ["backend/requirements.txt", "requirements.txt", "render.yaml", "vercel.json", "Dockerfile", "docker-compose.yml"]:
        return "DEPLOYMENT_CONFIGURATION"
    if norm in [".env.example", "frontend/.env.example"]:
        return "ENVIRONMENT_TEMPLATE"
    if norm in [".env", ".env.local"]:
        return "SECURITY_ARTIFACT"

    # 4. Production backend source
    if norm.startswith("backend/app/"):
        return "BACKEND_SOURCE"
    if norm == "backend/__init__.py":
        return "BACKEND_SOURCE"
    if norm.startswith("shared/"):
        return "PRODUCTION_SOURCE"
    if norm.startswith("worker/"):
        return "WORKER_SOURCE"

    # 5. Production frontend source
    if norm.startswith("frontend/src/") or norm.startswith("frontend/public/"):
        return "FRONTEND_SOURCE"
    if norm.startswith("frontend/") and norm.split("/")[-1] in ["package.json", "package-lock.json", "tsconfig.json", "tsconfig.node.json", "vite.config.ts", "tailwind.config.js", "postcss.config.js", "index.html"]:
        return "FRONTEND_SOURCE"

    # 6. Database schema & migrations
    if norm.startswith("alembic/") or norm.startswith("migrations/") or norm == "alembic.ini":
        return "DATABASE_MIGRATION"

    # 7. Test code & fixtures
    if norm.startswith("backend/tests/"):
        if ext == ".py":
            return "TEST_CODE"
        return "TEST_FIXTURE"
    if norm.startswith("Test_Images/"):
        return "VALIDATED_TEST_FIXTURE"
    if norm.startswith("qa_screenshots/"):
        return "HISTORICAL_AUDIT_ARTIFACT"

    # 8. Legal references
    if norm.startswith("Legal_References/"):
        return "DOCUMENTATION_CURRENT"

    # 9. Scripts
    if norm.startswith("backend/scripts/"):
        return "DEVELOPMENT_SCRIPT"
    if norm.startswith("scratch/runs/"):
        return "HISTORICAL_AUDIT_ARTIFACT"
    if norm.startswith("scratch/"):
        if norm.endswith((".jpg", ".png", ".pdf", ".docx", ".webp")):
            return "TEMPORARY_ARTIFACT"
        if "pipeline" in norm or "verification" in norm or "audit" in norm or "e2e" in norm:
            return "FORENSIC_ARTIFACT"
        return "DEVELOPMENT_SCRIPT"

    # 10. Documentation
    if norm.startswith("docs/"):
        if "phase7_" in norm:
            return "DOCUMENTATION_CURRENT"
        if any(f"phase{i}_" in norm for i in range(7)):
            return "DOCUMENTATION_HISTORICAL"
        return "DOCUMENTATION_CURRENT"
    if norm.startswith("Documentation/"):
        return "DOCUMENTATION_HISTORICAL"

    # 11. Root level files
    if "/" not in norm:
        if norm in [".gitignore"]:
            return "DEPLOYMENT_CONFIGURATION"
        if norm in ["README.md", "PRODUCT.md", "DESIGN.md"]:
            return "DOCUMENTATION_CURRENT"
        if "audit" in norm or "report" in norm or "validation" in norm or norm.startswith("phase"):
            return "HISTORICAL_AUDIT_ARTIFACT"
        if norm.endswith(".txt") or norm.endswith(".md"):
            return "DOCUMENTATION_CURRENT"
        if norm.endswith(".webp") or norm.endswith(".png"):
            return "FRONTEND_SOURCE"

    # 12. Tool configs (.agent, .impeccable)
    if norm.startswith(".agent/") or norm.startswith(".impeccable/"):
        return "DEVELOPMENT_TOOL"

    return "UNKNOWN"

with open(r"G:\CompliScan\scratch\repo_inventory_raw.json", "r", encoding="utf-8") as fh:
    raw_data = json.load(fh)

classified_counts = defaultdict(int)
classified_files = []

for item in raw_data["files"]:
    p = item["path"]
    cat = classify_file(p, item["size"], item["ext"])
    classified_counts[cat] += 1
    classified_files.append({**item, "category": cat})

with open(r"G:\CompliScan\scratch\classified_inventory.json", "w", encoding="utf-8") as out:
    json.dump({
        "counts": dict(sorted(classified_counts.items(), key=lambda x: x[1], reverse=True)),
        "files": classified_files
    }, out, indent=2)

print("Classification counts:")
for cat, count in sorted(classified_counts.items(), key=lambda x: x[1], reverse=True):
    print(f"  {cat}: {count}")
