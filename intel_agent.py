from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Dict, Any
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
import argparse

load_dotenv()
console = Console()

class IntelState(TypedDict):
    competitor: str
    target_urls: List[str]
    job_data: List[Dict[str, Any]]
    news_data: List[Dict[str, Any]]
    insights: str
    use_mcp: bool

def intelligence_planner(state):
    """Decides what to monitor for each competitor"""
    competitor = state["competitor"]
    console.print(f"[blue]🎯 Planning intelligence gathering for {competitor}[/blue]")
    
    # Define target URLs based on competitor
    target_urls = [
        f"https://www.{competitor.lower()}.com/careers",
        f"https://www.{competitor.lower()}.com/blog",
        f"https://www.{competitor.lower()}.com/changelog"
    ]
    
    return {
        **state,
        "target_urls": target_urls
    }

def job_scout(state):
    """Scrapes job listings - will fail on complex sites without MCP"""
    competitor = state["competitor"]
    console.print(f"[yellow]🔍 Scouting jobs for {competitor}...[/yellow]")
    
    job_data = []
    
    # Simple scraping (will fail on protected sites)
    try:
        careers_url = f"https://www.{competitor.lower()}.com/careers"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(careers_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Try to find job listings (this will be very basic)
        job_elements = soup.find_all(['div', 'li'], class_=lambda x: x and ('job' in x.lower() or 'position' in x.lower()))
        
        for job in job_elements[:3]:  # Limit to 3 for demo
            title = job.get_text(strip=True)
            if title and len(title) > 10:  # Basic filtering
                job_data.append({
                    "title": title[:100],  # Truncate long titles
                    "source": "careers_page"
                })
        
        console.print(f"[green]✅ Found {len(job_data)} job listings[/green]")
        
    except Exception as e:
        console.print(f"[red]❌ Job scraping failed: {str(e)}[/red]")
        job_data = []
    
    return {**state, "job_data": job_data}

def news_hunter(state):
    """Monitors press releases and product updates"""
    competitor = state["competitor"]
    console.print(f"[yellow]📰 Hunting news for {competitor}...[/yellow]")
    
    news_data = []
    
    try:
        # Try to scrape blog/news (basic approach)
        blog_url = f"https://www.{competitor.lower()}.com/blog"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(blog_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Look for article titles
        articles = soup.find_all(['h1', 'h2', 'h3'], limit=3)
        
        for article in articles:
            title = article.get_text(strip=True)
            if title and len(title) > 10:
                news_data.append({
                    "title": title[:100],
                    "source": "blog"
                })
        
        console.print(f"[green]✅ Found {len(news_data)} news items[/green]")
        
    except Exception as e:
        console.print(f"[red]❌ News scraping failed: {str(e)}[/red]")
        news_data = []
    
    return {**state, "news_data": news_data}

def insight_generator(state):
    """AI summarizes key changes and trends"""
    console.print("[yellow]🧠 Generating insights...[/yellow]")
    
    if not state["job_data"] and not state["news_data"]:
        return {**state, "insights": "No data available for analysis"}
    
    # Skip AI for now in basic version
    insights = "Basic scraping completed - limited insights available without MCP"
    
    return {**state, "insights": insights}

def dashboard_builder(state):
    """Creates visual terminal reports"""
    competitor = state["competitor"]
    
    # Create a rich panel for the report
    table = Table(title=f"🎯 COMPETITIVE INTELLIGENCE REPORT - {competitor.upper()}")
    table.add_column("Category", style="cyan", no_wrap=True)
    table.add_column("Data", style="white")
    
    table.add_row("Target", competitor)
    table.add_row("Scan Time", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    table.add_row("Jobs Found", str(len(state["job_data"])))
    table.add_row("News Found", str(len(state["news_data"])))
    
    console.print(table)
    
    # Show job data
    if state["job_data"]:
        console.print("\n[bold cyan]📊 HIRING ACTIVITY:[/bold cyan]")
        for job in state["job_data"]:
            console.print(f"• {job['title']}")
    else:
        console.print("\n[red]📊 No job data available[/red]")
    
    # Show news data
    if state["news_data"]:
        console.print("\n[bold cyan]🚀 RECENT NEWS:[/bold cyan]")
        for news in state["news_data"]:
            console.print(f"• {news['title']}")
    else:
        console.print("\n[red]🚀 No news data available[/red]")
    
    # Show insights
    console.print(f"\n[bold cyan]💡 KEY INSIGHTS:[/bold cyan]")
    console.print(state["insights"])
    
    console.print("\n" + "="*60)
    
    return state

# Build the workflow
def create_workflow():
    workflow = StateGraph(IntelState)
    
    # Add nodes
    workflow.add_node("planner", intelligence_planner)
    workflow.add_node("jobs", job_scout) 
    workflow.add_node("news", news_hunter)
    workflow.add_node("insight_gen", insight_generator)
    workflow.add_node("dashboard", dashboard_builder)
    
    # Define edges
    workflow.set_entry_point("planner")
    workflow.add_edge("planner", "jobs")
    workflow.add_edge("jobs", "news")
    workflow.add_edge("news", "insight_gen")
    workflow.add_edge("insight_gen", "dashboard")
    workflow.add_edge("dashboard", END)
    
    return workflow.compile()

def main():
    parser = argparse.ArgumentParser(description='Competitive Intelligence Agent')
    parser.add_argument('--competitor', required=True, help='Competitor name to analyze')
    args = parser.parse_args()
    
    console.print(Panel.fit(
        f"[bold blue]🤖 COMPETITIVE INTELLIGENCE AGENT[/bold blue]\n"
        f"Target: {args.competitor}",
        border_style="blue"
    ))
    
    # Create and run the workflow
    app = create_workflow()
    
    initial_state = {
        "competitor": args.competitor,
        "target_urls": [],
        "job_data": [],
        "news_data": [],
        "insights": "",
        "use_mcp": False
    }
    
    result = app.invoke(initial_state)
    
    console.print("\n[green]✅ Intelligence gathering complete![/green]")

if __name__ == "__main__":
    main()