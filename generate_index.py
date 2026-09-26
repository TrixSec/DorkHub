#!/usr/bin/env python3
"""
Generate index.json manifest for DorkHub.
"""

import os
import glob
import json
from datetime import datetime, timezone

REPO_DIR = os.path.dirname(os.path.abspath(__file__))

def generate_index():
    files = glob.glob(os.path.join(REPO_DIR, "**/*.txt"), recursive=True)
    files = [f for f in files if ".git" not in f]
    
    categories = {}
    total_dorks = 0
    
    for filepath in files:
        rel_path = os.path.relpath(filepath, REPO_DIR).replace('\\', '/')
        cat_name = rel_path.split('/')[0]
        
        dork_count = 0
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                clean = line.strip()
                if clean and not clean.startswith('#'):
                    dork_count += 1
                    
        total_dorks += dork_count
        
        if cat_name not in categories:
            categories[cat_name] = {
                "name": cat_name,
                "dork_count": 0,
                "files": []
            }
            
        categories[cat_name]["dork_count"] += dork_count
        categories[cat_name]["files"].append({
            "path": rel_path,
            "dork_count": dork_count
        })
        
    # Sort files within each category for deterministic output
    for cat in categories.values():
        cat["files"].sort(key=lambda f: f["path"])

    # Sort categories alphabetically for deterministic output
    sorted_categories = sorted(categories.values(), key=lambda c: c["name"])

    manifest = {
        "version": "2.0",
        "last_updated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ"),
        "total_dorks": total_dorks,
        "total_categories": len(categories),
        "categories": sorted_categories
    }
    
    out_path = os.path.join(REPO_DIR, "index.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
        
    print(f"Generated index.json: {total_dorks:,} dorks across {len(categories)} categories.")

if __name__ == "__main__":
    generate_index()
