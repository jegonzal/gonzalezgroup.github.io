from scholarly import scholarly
import json
import datetime
import time
import random
import os
import yaml
import argparse
import re
from typing import Any, Optional, TypedDict, List, Dict


class Publication(TypedDict):
    """
    A normalized publication record used by the website and preview HTML.

    Keys:
    - title: Paper title.
    - authors: Author string as returned by Google Scholar.
    - venue: Venue/journal/conference/preprint string.
    - year: Publication year as an int.
    - citations: Number of citations as an int.
    - url: Google Scholar citation URL.
    - abstract: Abstract string (may be empty).
    - bib_id: Google Scholar author publication id (stable per author).
    """

    title: str
    authors: str
    venue: str
    year: int
    citations: int
    url: str
    abstract: str
    bib_id: str


class AuthorPublications(TypedDict):
    """
    Publications payload written to `publications.json`, `_data/publications.yml`,
    and used to build `publications_preview.html`.

    Keys:
    - stats: Dict with citation stats for the author.
      - citations: int
      - h_index: int
      - i10_index: int
    - publications: List of `Publication`.
    - last_updated: Timestamp string in '%Y-%m-%d %H:%M:%S' format.
    """

    stats: Dict[str, int]
    publications: List[Publication]
    last_updated: str


def _parse_year_from_pub_bib(pub: Any) -> Optional[int]:
    """
    Extract a publication year from a Scholar publication object (filled or unfilled).

    Expected input:
    - pub: A dict-like object from `scholarly`, potentially containing `bib`.

    Returns:
    - int year if parseable, otherwise None.
    """
    if not isinstance(pub, dict):
        return None
    bib = pub.get("bib")
    if not isinstance(bib, dict):
        return None

    year_value = bib.get("pub_year", bib.get("year"))
    if year_value is None:
        return None
    try:
        return int(year_value)
    except (TypeError, ValueError):
        return None


def _normalize_whitespace(text: str) -> str:
    """
    Normalize whitespace for stable string comparisons.

    Args:
        text: Any string.

    Returns:
        A string with leading/trailing whitespace removed and internal whitespace collapsed.
    """
    return " ".join(text.split())


def _extract_leading_acronym(title: str) -> Optional[str]:
    """
    Extract a leading acronym of the form 'ACRONYM: ...' from a title.

    Examples:
        - "BARE: Something" -> "bare"
        - "S*: Test time scaling" -> "s*"

    Args:
        title: Publication title.

    Returns:
        The leading acronym lowercased, or None if no leading 'X:' pattern exists.
    """
    match = re.match(r"^\s*([A-Za-z0-9\*\-]{2,15})\s*:\s+", title)
    if match is None:
        return None
    return match.group(1).lower()


def _dedupe_publications(publications: List[Publication]) -> List[Publication]:
    """
    Dedupe publications to avoid near-identical entries showing up twice on the homepage.

    Deduping strategy:
    - If a title starts with an acronym like 'BARE: ...', we treat publications with the
      same (year, authors, acronym) as duplicates and keep the first.
    - Otherwise, we dedupe by (year, normalized_title).

    Args:
        publications: List of publication dicts.

    Returns:
        A new list with duplicates removed, preserving the first occurrence.
    """
    seen: set[tuple] = set()
    deduped: List[Publication] = []

    for pub in publications:
        title_norm = _normalize_whitespace(pub["title"]).lower()
        authors_norm = _normalize_whitespace(pub["authors"]).lower()
        acronym = _extract_leading_acronym(pub["title"])

        if acronym is not None:
            key = ("acronym", int(pub["year"]), authors_norm, acronym)
        else:
            key = ("title", int(pub["year"]), title_norm)

        if key in seen:
            continue
        seen.add(key)
        deduped.append(pub)

    return deduped


def get_author_publications(
    scholar_id: str = "B96GkdgAAAAJ",
    since_year: Optional[int] = None,
) -> Optional[AuthorPublications]:
    """
    Fetch publications from Google Scholar for a specific author ID.

    This function is the slow part of the update pipeline because it calls
    `scholarly.fill()` for each publication we include.

    Args:
        scholar_id: Google Scholar author id (e.g. "B96GkdgAAAAJ").
        since_year: If provided, only include publications with year >= since_year.
            This speeds up execution by skipping older publications entirely.

    Returns:
        A dict with keys: `stats`, `publications`, `last_updated`, or None on failure.
    """
    try:
        # Search for author by ID
        author = scholarly.search_author_id(scholar_id)
        
        # Fill in author details
        author = scholarly.fill(author)
        
        # Get citation stats
        stats = {
            'citations': author['citedby'],
            'h_index': author['hindex'],
            'i10_index': author['i10index']
        }
        
        # Get publications
        publications = []
        
        # Fill publication details
        total_pubs = len(author.get("publications", []))
        for i, pub in enumerate(author.get('publications', [])):
            print(f"Processing publication {i+1} of {total_pubs}")
            pub_year_unfilled = _parse_year_from_pub_bib(pub)
            if since_year is not None:
                # If year is missing, skip it to keep the pipeline fast and deterministic.
                if pub_year_unfilled is None:
                    continue
                if pub_year_unfilled < since_year:
                    continue
            try:
                pub_filled = scholarly.fill(pub)

                pub_year_filled = _parse_year_from_pub_bib(pub_filled)
                if since_year is not None:
                    # If year can't be determined even after fill, skip it.
                    if pub_year_filled is None:
                        continue
                    if pub_year_filled < since_year:
                        continue
                
                pub_dict = {
                    'title': pub_filled['bib'].get('title', ''),
                    'authors': pub_filled['bib'].get('author', ''),
                    'venue': pub_filled['bib'].get('journal', pub_filled['bib'].get('conference', '')),
                    'year': pub_year_filled if pub_year_filled is not None else 0,
                    'citations': pub_filled.get('num_citations', 0),
                    'url': f"https://scholar.google.com/citations?view_op=view_citation&citation_for_view={pub_filled['author_pub_id']}",
                    'abstract': pub_filled['bib'].get('abstract', ''),
                    'bib_id': pub_filled['author_pub_id']  # Used for ordering
                }
                publications.append(pub_dict)
                
                # Sleep to avoid hitting rate limits
                time.sleep(random.uniform(1, 3))
                
            except Exception as e:
                print(f"Error processing publication: {e}")
                continue
        
        publications = _dedupe_publications(publications)

        # Sort by year and shuffle publications within the same year (more efficiently than O(n^2) filtering).
        year_to_pubs: Dict[int, List[Publication]] = {}
        for pub in publications:
            year_to_pubs.setdefault(int(pub["year"]), []).append(pub)

        sorted_publications: List[Publication] = []
        for year in sorted(year_to_pubs.keys(), reverse=True):
            year_pubs = year_to_pubs[year]
            random.shuffle(year_pubs)
            sorted_publications.extend(year_pubs)

        publications = sorted_publications

        return {
            'stats': stats,
            'publications': publications,
            'last_updated': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
    except Exception as e:
        print(f"Error fetching author data: {e}")
        return None

# Rest of your code remains the same
def save_publications(data, filename='publications.json'):
    """
    Save publications data to JSON file
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Successfully saved publications to {filename}")
    except Exception as e:
        print(f"Error saving publications: {e}")

def generate_html_preview(data, filename='publications_preview.html'):
    """
    Generate HTML preview of publications
    """
    try:
        html = """
        <html>
        <head>
            <title>Publications Preview</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; }
                .stats { display: flex; justify-content: space-around; margin: 20px 0; padding: 20px; background: #f5f5f5; }
                .stat-item { text-align: center; }
                .stat-number { font-size: 24px; font-weight: bold; color: #2d3c48; }
                .stat-label { color: #666; }
                .publication { margin: 20px 0; padding: 20px; border: 1px solid #eee; border-radius: 5px; }
                .title { font-size: 18px; color: #2d3c48; margin-bottom: 10px; }
                .authors { color: #666; margin-bottom: 5px; }
                .venue { color: #3e8cb7; }
                .citations { color: #72b16e; }
                .year { float: right; color: #666; }
                .last-updated { text-align: center; color: #666; margin-top: 40px; }
            </style>
        </head>
        <body>
        """
        
        # Add stats
        html += """
        <div class="stats">
            <div class="stat-item">
                <div class="stat-number">{}</div>
                <div class="stat-label">Citations</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{}</div>
                <div class="stat-label">h-index</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{}</div>
                <div class="stat-label">i10-index</div>
            </div>
        </div>
        """.format(
            data['stats']['citations'],
            data['stats']['h_index'],
            data['stats']['i10_index']
        )
        
        # Add publications
        for pub in data['publications']:
            html += """
            <div class="publication">
                <div class="year">{}</div>
                <div class="title"><a href="{}" target="_blank">{}</a></div>
                <div class="authors">{}</div>
                <div class="venue">{}</div>
                <div class="citations">{} citations</div>
            </div>
            """.format(
                pub['year'],
                pub['url'],
                pub['title'],
                pub['authors'],
                pub['venue'],
                pub['citations']
            )
            
        # Add last updated
        html += """
        <div class="last-updated">Last updated: {}</div>
        </body>
        </html>
        """.format(data['last_updated'])
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"Successfully generated HTML preview at {filename}")
    except Exception as e:
        print(f"Error generating HTML preview: {e}")

def save_publications_for_jekyll(data, filename='_data/publications.yml'):
    """
    Save publications data in Jekyll-compatible YAML format
    """
    try:
        # Create _data directory if it doesn't exist
        os.makedirs('_data', exist_ok=True)
        
        # Convert the data to YAML format
        yaml_data = {
            'stats': data['stats'],
            'publications': data['publications'],
            'last_updated': data['last_updated']
        }
        
        # Save as YAML
        with open(filename, 'w', encoding='utf-8') as f:
            yaml.dump(yaml_data, f, allow_unicode=True, sort_keys=False)
        print(f"Successfully saved publications to {filename}")
    except Exception as e:
        print(f"Error saving publications: {e}")

def main():
    """
    Main function to update publications
    """
    parser = argparse.ArgumentParser(description="Fetch and write recent publications data from Google Scholar.")
    parser.add_argument(
        "--scholar-id",
        type=str,
        default="B96GkdgAAAAJ",
        help="Google Scholar author id (default: B96GkdgAAAAJ).",
    )
    parser.add_argument(
        "--since-year",
        type=int,
        default=datetime.datetime.now().year - 5,
        help="Only include publications with year >= this value (default: current_year - 5).",
    )
    args = parser.parse_args()

    print("Fetching publications from Google Scholar...")
    data = get_author_publications(scholar_id=args.scholar_id, since_year=args.since_year)
    
    if data:
        # Save JSON (original format)
        save_publications(data)
        
        # Save YAML for Jekyll
        save_publications_for_jekyll(data)
        
        # Generate HTML preview
        generate_html_preview(data)
        
        print("\nStats:")
        print(f"Total citations: {data['stats']['citations']}")
        print(f"h-index: {data['stats']['h_index']}")
        print(f"i10-index: {data['stats']['i10_index']}")
        print(f"\nTotal publications processed: {len(data['publications'])}")
        print(f"Last updated: {data['last_updated']}")
    else:
        print("Failed to fetch publications")

if __name__ == "__main__":
    main()

    