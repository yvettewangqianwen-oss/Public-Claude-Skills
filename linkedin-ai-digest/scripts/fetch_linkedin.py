#!/usr/bin/env python3
"""Build LinkedIn WebSearch queries for a list of AI companies.

This script does NOT call LinkedIn. It emits a JSON plan of searches for the
Claude loop to execute with the WebSearch tool (LinkedIn blocks direct scraping,
so the actual fetching happens inside Claude with WebSearch + WebFetch, mirroring
how ai-digest-public handles X/Twitter).
"""

import argparse
import json


def build_plan(companies: list[dict], days: int) -> list[dict]:
    plan = []
    for c in companies:
        slug = c["slug"]
        plan.append({
            "company": c["name"],
            "slug": slug,
            "company_url": f"https://www.linkedin.com/company/{slug}/",
            "posts_url": f"https://www.linkedin.com/company/{slug}/posts/",
            "queries": [
                f'site:linkedin.com/company/{slug} posts',
                f'site:linkedin.com/posts "{c["name"]}"',
            ],
            "window_days": days,
        })
    return plan


def main():
    parser = argparse.ArgumentParser(description="Build LinkedIn fetch plan")
    parser.add_argument(
        "--companies", type=str, required=True,
        help='JSON array of {"name": "...", "slug": "..."} objects',
    )
    parser.add_argument(
        "--days", type=int, default=7,
        help="Lookback window in days (default: 7)",
    )
    args = parser.parse_args()

    companies = json.loads(args.companies)
    plan = build_plan(companies, args.days)
    print(json.dumps(plan, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
