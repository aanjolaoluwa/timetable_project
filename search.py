import urllib.request
import json
import urllib.parse
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def search_paper(query):
    encoded_query = urllib.parse.quote(query)
    url = f"https://api.openalex.org/works?search={encoded_query}&per-page=3"
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
                print(f"Title: {res.get('title')}")
                print(f"Year: {res.get('publication_year')}")
                print(f"Authors: {', '.join(authors)}")
                print()
    except Exception as e:
        print(f"Error for {query}: {e}")

search_paper("university course timetabling Babaei Karimpour Hadidi")
search_paper("A survey of university course timetabling problem Chen Sze Goh Sabar Kendall")
search_paper("hyper-heuristics Drake Kheiri Özcan Burke")
search_paper("Al-Betar Khader Zaman university course timetabling")
search_paper("Abdipoor Yaakob Goh Abdullah timetabling")
search_paper("Dunke Nickel timetabling")
search_paper("Xiang Hu Yu Wang timetabling")
search_paper("Kiefer Hartl Schnell timetabling")
search_paper("Ceschia timetabling")
search_paper("Thepphakorn timetabling")
search_paper("Milani Fitria timetabling")
search_paper("Pallagani natural language scheduling")
search_paper("Abgaryan scheduling")
