import httpx
from cachetools import TTLCache
from typing import List


# Cache to store PubMed responses, with a 1-hour TTL
pubmed_cache = TTLCache(maxsize=1000, ttl=3600)


async def fetch_pubmed_summaries(pubmed_ids: List[int]) -> dict:
    ids_string = ",".join(map(str, pubmed_ids))
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={ids_string}&retmode=json"

    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()
