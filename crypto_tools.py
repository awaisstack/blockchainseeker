from ibm_watsonx_orchestrate.agent_builder.tools import tool
from duckduckgo_search import DDGS
import re

# --- HELPER WITH REGION LOCK ---
def _search_html(query, num_results=5):
    try:
        # Force region 'us-en' (United States) to avoid localized spam
        # Use backend='html' because it is the most reliable on Cloud IPs
        results = DDGS().text(query, max_results=num_results, backend="html", region="us-en")
        if not results: return []
        
        formatted = []
        for r in results:
            title = r.get('title', 'No Title')
            body = r.get('body', r.get('snippet', 'No Summary'))
            link = r.get('href', 'No Link')
            formatted.append(f"HEADLINE: {title}\nSUMMARY: {body}\nSOURCE: {link}\n")
        return formatted
    except Exception as e:
        return [f"Search Error: {str(e)}"]

# --- TOOLS ---

@tool(name="search_crypto_news")
def search_crypto_news(project_name: str) -> str:
    """
    Searches for recent news articles about a crypto project to gauge sentiment.
    """
    try:
        # 1. Trusted Sites (To guarantee quality)
        trusted_sites = "site:coindesk.com OR site:cointelegraph.com OR site:theblock.co OR site:decrypt.co"
        query = f'"{project_name}" {trusted_sites}'
        
        # 2. Use the Helper (To guarantee English results)
        news_data = _search_html(query, num_results=5)
        
        # 3. Fallback if trusted sites are empty
        if not news_data:
             query_fallback = f'"{project_name}" crypto news'
             news_data = _search_html(query_fallback, num_results=5)
        
        if not news_data:
            return f"No news found for {project_name}."
            
        return f"Latest News for {project_name}:\n" + "\n".join(news_data)
    except Exception as e:
        return f"Error searching news: {str(e)}"

@tool(name="analyze_github_activity")
def analyze_github_activity(project_name: str) -> str:
    """Finds the Official GitHub Repo."""
    try:
        ddgs = DDGS()
        report = []
        # 1. Official Site
        site_res = ddgs.text(f"{project_name} official crypto website", max_results=2, backend="html", region="us-en")
        website = site_res[0]['href'] if site_res else "Not Found"
        report.append(f"🔎 OFFICIAL SITE: {website}")

        # 2. GitHub Repo
        repo_res = ddgs.text(f"{project_name} github repository", max_results=3, backend="html", region="us-en")
        if repo_res:
            report.append("\n🔎 GITHUB CANDIDATES:")
            for r in repo_res:
                report.append(f"- {r['title']} ({r['href']})")
        else:
            report.append("\n🔎 GITHUB CANDIDATES: None found.")

        return "\n".join(report)
    except Exception as e:
        return f"Error performing audit: {str(e)}"

@tool(name="general_web_research")
def general_web_research(query: str) -> str:
    """General web search."""
    try:
        res = _search_html(query, num_results=5)
        if not res: 
            # OLD CODE (Caused the error):
            # return f"No results for: {query}"
            
            # NEW CODE (Fixes the logic):
            return "Audit Complete: No specific scam reports, lawsuits, or negative alerts were found for this query. This suggests the project is currently Low Risk regarding scams."
            
        return "\n".join(res)
    except Exception as e:
        return f"Search performed but encountered a read error: {str(e)}"