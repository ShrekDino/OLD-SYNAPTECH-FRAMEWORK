# ==============================================================================
# WEB UTILITIES - Web scraping and search functions
# ==============================================================================

import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))
from config import *

import urllib.request
from bs4 import BeautifulSoup 
from duckduckgo_search import DDGS

def scrape_url(url, max_chars=8000):
    """Extract clean text from a URL."""
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as res:
            soup = BeautifulSoup(res.read(), "html.parser")
            for s in soup(["script", "style", "nav", "footer", "header"]):
                s.extract()
            return soup.get_text(separator=' ', strip=True)[:max_chars]
    except Exception as e:
        print(f"Scrape fail {url}: {e}")
        return ""

def search_reputable_sources(query, max_results=3):
    """
    Forces the search to look for high-authority data.
    Uses 'DSM-5' and 'NCBI' as benchmarks for accuracy.
    """
    refined_query = f"{query} site:.gov OR site:.edu OR 'DSM-5' OR 'NCBI' OR site:archive.org"
    sources = []
    try:
        with DDGS() as ddgs:
            results = ddgs.text(refined_query, max_results=max_results)
            for r in results:
                sources.append(f"- **{r['title']}**: {r['body']} \n  [Link]({r['href']})")
    except Exception as e:
        return f"Web search failed: {e}"
    return "\n".join(sources)

def verify_scientific_link(source, target, max_results=2):
    """Verifies consensus between two topics using DDGS and logic model."""
    from ai_utils import run_ollama
    
    query = f"scientific link between {source} and {target}"
    try:
        results = list(DDGS().text(query, max_results=max_results))
        context = " ".join([r['body'] for r in results])
        
        prompt = (
            f"SYSTEM: Scientific Fact-Checker. Respond ONLY 'YES' or 'NO'.\n"
            f"Is there a recognized academic or technical connection between '{source}' and '{target}'?\n"
            f"Search Context: {context}"
        )
        res = run_ollama(prompt, model=LOGIC_MODEL)
        return "YES" in res['clean'].upper()
    except Exception as e:
        print(f"   ⚠️ Search bypass for {target}: {e}")
        return False
