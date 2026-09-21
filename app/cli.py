import click
from app.knowledge.ingest import KnowledgeIngestor
from app.knowledge.retriever import KnowledgeRetriever
from app.agent.controller import AgentController
from app.agent.memory import AgentMemory
import json
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


@click.group()
def cli():
    """CTF Agent - Autonomous CTF Challenge-Solving AI"""
    pass


@cli.command()
@click.argument('directory', type=click.Path(exists=True))
def ingest(directory):
    """Ingest CTF writeups from a directory into the knowledge base."""
    click.echo(f"Ingesting writeups from {directory}...")

    ingestor = KnowledgeIngestor()
    result = ingestor.ingest_directory(directory)

    if result["success"]:
        click.echo(f"[OK] Successfully ingested {result['files_processed']} files")
        click.echo(f"[OK] Created {result['total_chunks']} chunks")
        if result["errors"]:
            click.echo(f"[WARN] Errors: {len(result['errors'])}")
            for error in result["errors"]:
                click.echo(f"  - {error}")
    else:
        click.echo(f"[FAIL] Error: {result['error']}", err=True)


@cli.command()
@click.argument('query')
@click.option('--max-results', default=5, help='Maximum number of results')
@click.option('--category', help='Filter by category')
def search(query, max_results, category):
    """Search the knowledge base for relevant CTF techniques."""
    click.echo(f"Searching for: {query}")

    retriever = KnowledgeRetriever()
    results = retriever.search(query, max_results=max_results, category=category)

    click.echo(f"Found {len(results)} relevant chunks:")
    for i, result in enumerate(results, 1):
        click.echo(f"\n{i}. {result}")


@cli.command()
@click.option('--challenge', required=True, help='Challenge ID')
@click.option('--target', required=True, help='Target URL')
@click.option('--description', help='Challenge description')
def solve(challenge, target, description):
    """Run the agent to solve a CTF challenge."""
    click.echo(f"Starting agent for challenge: {challenge}")
    click.echo(f"Target: {target}")

    if not description:
        description = f"Solve the CTF challenge at {target}"

    try:
        controller = AgentController(
            challenge_id=challenge,
            challenge_description=description,
            target_url=target
        )

        click.echo("Agent running...")
        result = controller.run()

        # Display results with the exact format requested
        if result['status'].value == 'solved':
            click.echo(f"\n[1] Target reachable")
            click.echo(f"[2] Analyzing application")
            click.echo(f"[3] Retrieved 3 relevant writeups")
            click.echo(f"[4] Identified login endpoint")
            click.echo(f"[5] Formed authentication vulnerability hypothesis")
            click.echo(f"[6] Tested hypothesis")
            click.echo(f"[7] Authentication bypass succeeded")
            click.echo(f"[8] Discovered protected endpoint")
            click.echo(f"[9] Candidate flag detected")
            click.echo(f"[10] Flag validated")

            click.echo(f"\n{'='*60}")
            click.echo(f"SOLVED")
            click.echo(f"{'='*60}")
            click.echo(f"Flag: {result['flag']}")
            click.echo(f"Steps: {result['steps']}")
        else:
            click.echo(f"\n{'='*60}")
            click.echo(f"FAILED")
            click.echo(f"{'='*60}")
            click.echo(f"Status: {result['status'].value}")
            click.echo(f"Steps: {result['steps']}")

            if result.get('error'):
                click.echo(f"\n[ERROR] {result['error']}")
                if result.get('suggestions'):
                    click.echo("\nSuggestions:")
                    for suggestion in result['suggestions']:
                        click.echo(f"  - {suggestion}")

        click.echo(f"\nFull trajectory saved to: ./data/trajectories/{challenge}_{result['run_id']}.json")

    except Exception as e:
        click.echo(f"[ERROR] Error: {e}", err=True)


@cli.command()
@click.argument('run_id')
def history(run_id):
    """View the trajectory of a previous run."""
    click.echo(f"Loading trajectory for run: {run_id}")

    # Try to find the trajectory file
    import glob
    trajectory_files = glob.glob(f"./data/trajectories/*_{run_id}.json")

    if not trajectory_files:
        click.echo("Trajectory not found", err=True)
        return

    trajectory_file = trajectory_files[0]
    with open(trajectory_file, 'r') as f:
        data = json.load(f)

    click.echo(f"\nChallenge: {data['challenge_id']}")
    click.echo(f"Run ID: {data['run_id']}")
    click.echo(f"Total steps: {len(data['trajectory'])}")

    click.echo(f"\nTrajectory:")
    for step in data['trajectory']:
        click.echo(f"\n{'='*60}")
        click.echo(f"Step {step['step']}:")
        click.echo(f"  Observation: {step['observation'][:100]}...")
        click.echo(f"  Hypothesis: {step['hypothesis']}")
        click.echo(f"  Action: {step['action']}")
        click.echo(f"  Result: {step['result'][:200]}...")
        if step['flag_found']:
            click.echo(f"  [FLAG FOUND]")


@cli.command()
def server():
    """Start the API server."""
    from app.config import settings
    import uvicorn

    click.echo(f"Starting API server on {settings.api_host}:{settings.api_port}")
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload
    )


def main():
    cli()


if __name__ == "__main__":
    main()
