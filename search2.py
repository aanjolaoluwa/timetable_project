import urllib.request
import json
import urllib.parse
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def search_paper(query, min_year=2015):
    encoded_query = urllib.parse.quote(query)
    # Using openalex filter by year
    url = f"https://api.openalex.org/works?search={encoded_query}&filter=publication_year:{min_year}-2026&per-page=3&sort=cited_by_count:desc"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, context=ctx) as response:
            data = json.loads(response.read().decode())
            results = data.get('results', [])
            print(f"--- Query: {query} ---")
            if not results:
                print("No results found.")
            for res in results:
                authors = [a['author']['display_name'] for a in res.get('authorships', [])]
                author_names = authors[0].split()[-1] if authors else "Unknown"
                if len(authors) == 2:
                    author_names += f" & {authors[1].split()[-1]}"
                elif len(authors) > 2:
                    author_names += " et al."
                print(f"[{author_names}, {res.get('publication_year')}] Title: {res.get('title')}")
                print()
    except Exception as e:
        print(f"Error for {query}: {e}")

search_paper("university course timetabling NP-hard optimization")
search_paper("genetic algorithm university timetabling")
search_paper("simulated annealing timetabling")
search_paper("tabu search timetabling")
search_paper("hyper-heuristic selection university timetabling")
search_paper("natural language processing constraint extraction scheduling requirements")
search_paper("rule-based natural language processing requirements extraction")
