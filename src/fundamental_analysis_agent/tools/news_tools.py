import json

from agents import function_tool
from .financial_tools import ticker_obj


def recent_news(ticker: str) -> list[dict]:
    try:
        items = ticker_obj(ticker.upper()).news or []
    except Exception:
        items = []

    results = []
    for item in items[:12]:
        if not isinstance(item, dict):
            continue
        content = item.get("content", item)
        if not isinstance(content, dict):
            continue
        title = content.get("title") or item.get("title")
        if not title:
            continue
        provider = content.get("provider") or {}
        canonical = content.get("canonicalUrl") or {}
        click_through = content.get("clickThroughUrl") or {}
        url = canonical.get("url") if isinstance(canonical, dict) else None
        url = url or (click_through.get("url") if isinstance(click_through, dict) else None)
        results.append({
            "title": title,
            "publisher": provider.get("displayName") if isinstance(provider, dict) else None,
            "url": url,
            "published_at": content.get("pubDate") or item.get("providerPublishTime"),
        })
    return results


@function_tool
def search_recent_news(ticker: str) -> str:
    """Retrieve a small set of recent headlines and source URLs for a public-market ticker."""
    return json.dumps({
        "ticker": ticker.upper(),
        "articles": recent_news(ticker),
        "source": "Yahoo Finance news via yfinance",
        "limitation": "Coverage, publication dates and URLs may be incomplete; verify original articles.",
    })
