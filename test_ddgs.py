from duckduckgo_search import DDGS

print("Testing DDGS directly...")
try:
    with DDGS() as ddgs:
        results = list(ddgs.text("茅台 2023 年报 PDF", max_results=5))
        if results:
            print(f"Found {len(results)} results.")
            for r in results:
                print(f"- {r['title']}: {r['href']}")
        else:
            print("No results found via DDGS.")
except Exception as e:
    print(f"DDGS Error: {e}")
