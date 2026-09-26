#!/usr/bin/env python3
"""
DorkHub CLI Tool
----------------
Command-line interface to search, list, and export dorks from the DorkHub repository.
"""

import os
import sys
import json
import glob
import random
import argparse

REPO_DIR = os.path.dirname(os.path.abspath(__file__))

def get_all_dork_files():
    files = glob.glob(os.path.join(REPO_DIR, "**/*.txt"), recursive=True)
    return [f for f in files if ".git" not in f]

def load_dorks():
    dorks = []
    files = get_all_dork_files()
    for filepath in files:
        rel_path = os.path.relpath(filepath, REPO_DIR)
        parts = rel_path.split(os.sep)
        category = parts[0]
        
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f, 1):
                clean = line.strip()
                if clean and not clean.startswith('#'):
                    dorks.append({
                        "dork": clean,
                        "category": category,
                        "file": rel_path,
                        "line": line_num
                    })
    return dorks

def cmd_search(args):
    dorks = load_dorks()
    query = args.query.lower()
    results = [d for d in dorks if query in d["dork"].lower()]
    
    print(f"Found {len(results)} dorks matching '{args.query}':\n")
    for r in results[:args.limit]:
        print(f"[{r['category']}] {r['dork']}")
        print(f"  |- File: {r['file']}:{r['line']}\n")
        
    if len(results) > args.limit:
        print(f"... and {len(results) - args.limit} more results. Use --limit to see more.")

def cmd_categories(args):
    dorks = load_dorks()
    categories = {}
    for d in dorks:
        cat = d['category']
        categories[cat] = categories.get(cat, 0) + 1
        
    print(f"DorkHub Categories ({len(categories)} total):\n")
    for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        print(f"  * {cat:<25} ({count:,} dorks)")

def cmd_random(args):
    dorks = load_dorks()
    if args.category:
        dorks = [d for d in dorks if d['category'].lower() == args.category.lower()]
        
    if not dorks:
        print(f"No dorks found for category '{args.category}'.")
        return
        
    choice = random.choice(dorks)
    print(f" Random Dork [{choice['category']}]:\n")
    print(f"  {choice['dork']}\n")
    print(f"  File: {choice['file']}:{choice['line']}")

def cmd_export(args):
    dorks = load_dorks()
    if args.category:
        dorks = [d for d in dorks if d['category'].lower() == args.category.lower()]
        
    if args.format == "json":
        output = json.dumps(dorks, indent=2)
    else:
        output = "\n".join(d['dork'] for d in dorks)
        
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"Exported {len(dorks)} dorks to {args.output}")
    else:
        print(output)

def main():
    parser = argparse.ArgumentParser(description="DorkHub CLI - Security Researcher's Dork Database")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Search
    p_search = subparsers.add_parser("search", help="Search dorks by keyword")
    p_search.add_argument("query", help="Keyword or pattern to search for")
    p_search.add_argument("--limit", type=int, default=20, help="Maximum results to display (default: 20)")
    
    # Categories
    p_cats = subparsers.add_parser("categories", help="List all categories and counts")
    
    # Random
    p_rand = subparsers.add_parser("random", help="Get a random dork")
    p_rand.add_argument("--category", help="Filter by specific category")
    
    # Export
    p_exp = subparsers.add_parser("export", help="Export dorks in JSON or TXT format")
    p_exp.add_argument("--category", help="Filter by category")
    p_exp.add_argument("--format", choices=["json", "txt"], default="txt", help="Output format")
    p_exp.add_argument("--output", "-o", help="Output file path")
    
    args = parser.parse_args()
    
    if args.command == "search":
        cmd_search(args)
    elif args.command == "categories":
        cmd_categories(args)
    elif args.command == "random":
        cmd_random(args)
    elif args.command == "export":
        cmd_export(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
