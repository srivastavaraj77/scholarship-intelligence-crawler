"""
CLI Runner for the Scholarship Intelligence Crawler.
Demonstrates automated crawler execution, re-verification, and Run 1 -> Run 2 Change Detection.
"""
import sys
import argparse
import asyncio
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database import init_db, get_metrics, get_history, get_all_scholarships
from app.crawler.pipeline import CrawlerPipeline
from scripts.seed_data import seed_initial_database


console = Console()


def display_dashboard():
    """Prints a summary metrics table to the terminal."""
    metrics = get_metrics()
    
    table = Table(title="📊 Scholarship Intelligence Crawler - Current Repository Status", style="bold cyan")
    table.add_column("Metric", style="bold white")
    table.add_column("Value", justify="right", style="bold green")
    
    table.add_row("Total Discovered Scholarships", str(metrics["total_discovered"]))
    table.add_row("Verified Opportunities (Confidence ≥ 95%)", f"[bold green]{metrics['verified_count']}[/bold green]")
    table.add_row("Review Required Opportunities", f"[bold yellow]{metrics['review_required_count']}[/bold yellow]")
    table.add_row("Active Scholarships", str(metrics["active_count"]))
    table.add_row("Expiring Soon (≤ 15 days)", str(metrics["expiring_soon_count"]))
    table.add_row("Expired / Archived Schemes", f"[bold red]{metrics['expired_count']}[/bold red]")
    table.add_row("Average Evidentiary Confidence", f"{metrics['avg_confidence']}%")
    table.add_row("Total Detected History Mutations", str(metrics["total_changes_detected"]))
    
    console.print(table)


async def main():
    parser = argparse.ArgumentParser(description="Scholarship Intelligence Crawler CLI")
    parser.add_argument("--mode", choices=["seed", "crawl", "simulate-run2", "status", "history"], default="status",
                        help="Action to perform")
    args = parser.parse_args()
    
    init_db()
    pipeline = CrawlerPipeline(simulate_network=True)
    
    if args.mode == "seed":
        console.print(Panel("[bold green]🌱 Seeding 24 Authentic Indian Scholarships...[/bold green]"))
        seed_initial_database()
        display_dashboard()
        
    elif args.mode == "crawl":
        console.print(Panel("[bold cyan]🔄 Running Automated Crawler & Verification Cycle (Run 1)...[/bold cyan]"))
        summary, changes = await pipeline.run_full_crawler_cycle()
        console.print(f"[bold green]✓ Crawler Finished:[/bold green] Discovered: {summary.total_discovered} | Verified: {summary.total_verified} | Changes: {summary.changes_detected}")
        display_dashboard()
        
    elif args.mode == "simulate-run2":
        console.print(Panel("[bold magenta]⚡ Executing Run 2: Portal Update & Change Detection Engine...[/bold magenta]"))
        summary, diffs = pipeline.simulate_run_2_changes()
        
        diff_table = Table(title="🔍 Detected Live Portal Mutations (Run 1 -> Run 2)", style="bold yellow")
        diff_table.add_column("Scholarship", style="bold white")
        diff_table.add_column("Field Changed", style="bold cyan")
        diff_table.add_column("Old Value", style="bold red")
        diff_table.add_column("New Value", style="bold green")
        diff_table.add_column("Evidence Snippet", style="italic")
        
        for d in diffs:
            diff_table.add_row(
                d.scholarship_name[:35],
                d.field_name,
                str(d.old_value)[:30],
                str(d.new_value)[:30],
                (d.evidence_snippet[:50] + "...") if d.evidence_snippet else "N/A"
            )
            
        console.print(diff_table)
        console.print(f"\n[bold green]✓ Change Detection Logged {len(diffs)} mutations to database history audit table without overwriting past lineage.[/bold green]")
        display_dashboard()
        
    elif args.mode == "history":
        history = get_history(limit=25)
        hist_table = Table(title="📜 Audit Trail & Change Detection Log", style="bold blue")
        hist_table.add_column("Time (UTC)", style="dim")
        hist_table.add_column("Scholarship", style="bold white")
        hist_table.add_column("Mutation Type", style="bold cyan")
        hist_table.add_column("Field", style="yellow")
        hist_table.add_column("Old Value -> New Value", style="bold green")
        
        for h in history:
            old_display = h.old_value if h.old_value else "[NEW RECORD]"
            hist_table.add_row(
                h.detected_at,
                h.scholarship_name[:30],
                h.change_type,
                h.field_name,
                f"{old_display[:25]} ➜ {h.new_value[:25]}"
            )
        console.print(hist_table)
        
    elif args.mode == "status":
        display_dashboard()


if __name__ == "__main__":
    asyncio.run(main())
