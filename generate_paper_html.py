from scholarly import scholarly
import json
import datetime
import pandas as pd
import time
import random
import os
import yaml

def get_author_publications(scholar_id="B96GkdgAAAAJ"):
    """
    Fetch publications from Google Scholar for a specific author ID
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
        for i, pub in enumerate(author['publications']):
            print(f"Processing publication {i+1} of {len(author['publications'])}")
            try:
                pub_filled = scholarly.fill(pub)
                
                pub_dict = {
                    'title': pub_filled['bib'].get('title', ''),
                    'authors': pub_filled['bib'].get('author', ''),
                    'venue': pub_filled['bib'].get('journal', pub_filled['bib'].get('conference', '')),
                    'year': pub_filled['bib'].get('pub_year', 0),
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
        
        # srt by year
        publications.sort(key=lambda x: int(x['year']), reverse=True)
        
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
    print("Fetching publications from Google Scholar...")
    data = get_author_publications()
    
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