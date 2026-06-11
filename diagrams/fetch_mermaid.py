import base64
import urllib.request
import os
import glob
import json

def render_mermaid(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        graph = f.read()

    # Create the state object for mermaid.ink
    state = {
        "code": graph,
        "mermaid": json.dumps({"theme": "default"})
    }
    
    # encode the state object as a string, then base64 encode
    state_str = json.dumps(state)
    b64 = base64.urlsafe_b64encode(state_str.encode('utf-8')).decode('utf-8')
    
    # URL for mermaid.ink
    url = f"https://mermaid.ink/img/{b64}?type=jpeg"
    
    output_filepath = filepath.replace('.mmd', '.jpeg')
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response, open(output_filepath, 'wb') as out_file:
            out_file.write(response.read())
        print(f"Successfully downloaded {output_filepath}")
    except Exception as e:
        print(f"Failed to download {output_filepath}: {e}")

import time
if __name__ == '__main__':
    # Process all mmd files in current directory
    for file in glob.glob('*.mmd'):
        if not os.path.exists(file.replace('.mmd', '.jpeg')):
            render_mermaid(file)
            time.sleep(2)
