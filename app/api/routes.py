from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from app.agent.controller import AgentController
from app.knowledge.ingest import KnowledgeIngestor
from app.knowledge.retriever import KnowledgeRetriever
import uuid


router = APIRouter()


class ChallengeCreate(BaseModel):
    challenge_id: str
    description: str
    target_url: str
    category: Optional[str] = "web"
    difficulty: Optional[str] = "medium"


class ChallengeResponse(BaseModel):
    challenge_id: str
    description: str
    target_url: str
    category: str
    difficulty: str


class RunCreate(BaseModel):
    challenge_id: str
    target_url: str


class RunResponse(BaseModel):
    run_id: str
    challenge_id: str
    status: str
    flag: Optional[str] = None
    steps: int


class KnowledgeIngestRequest(BaseModel):
    directory: str


class KnowledgeSearchRequest(BaseModel):
    query: str
    max_results: Optional[int] = 5
    category: Optional[str] = None


class KnowledgeSearchResponse(BaseModel):
    results: List[str]


# In-memory storage for MVP (would use database in production)
challenges: Dict[str, ChallengeResponse] = {}
runs: Dict[str, Dict[str, Any]] = {}


@router.post("/challenges", response_model=ChallengeResponse)
async def create_challenge(challenge: ChallengeCreate):
    """Create a new challenge."""
    if challenge.challenge_id in challenges:
        raise HTTPException(status_code=400, detail="Challenge already exists")

    challenge_response = ChallengeResponse(
        challenge_id=challenge.challenge_id,
        description=challenge.description,
        target_url=challenge.target_url,
        category=challenge.category,
        difficulty=challenge.difficulty
    )

    challenges[challenge.challenge_id] = challenge_response
    return challenge_response


@router.get("/challenges", response_model=List[ChallengeResponse])
async def list_challenges():
    """List all challenges."""
    return list(challenges.values())


@router.get("/challenges/{challenge_id}", response_model=ChallengeResponse)
async def get_challenge(challenge_id: str):
    """Get a specific challenge."""
    if challenge_id not in challenges:
        raise HTTPException(status_code=404, detail="Challenge not found")
    return challenges[challenge_id]


@router.post("/runs", response_model=RunResponse)
async def create_run(run: RunCreate, background_tasks: BackgroundTasks):
    """Start a new agent run."""
    run_id = str(uuid.uuid4())

    # Store initial run state
    runs[run_id] = {
        "run_id": run_id,
        "challenge_id": run.challenge_id,
        "status": "running",
        "flag": None,
        "steps": 0,
        "trajectory": []
    }

    # Start agent in background
    background_tasks.add_task(run_agent, run_id, run.challenge_id, run.target_url)

    return RunResponse(
        run_id=run_id,
        challenge_id=run.challenge_id,
        status="running",
        steps=0
    )


async def run_agent(run_id: str, challenge_id: str, target_url: str):
    """Run the agent in the background."""
    try:
        # Get challenge description
        if challenge_id not in challenges:
            runs[run_id]["status"] = "failed"
            runs[run_id]["error"] = "Challenge not found"
            return

        description = challenges[challenge_id].description

        # Create and run controller
        controller = AgentController(
            challenge_id=challenge_id,
            challenge_description=description,
            target_url=target_url
        )

        result = controller.run()

        # Update run state
        runs[run_id].update(result)

    except Exception as e:
        runs[run_id]["status"] = "failed"
        runs[run_id]["error"] = str(e)


@router.get("/runs/{run_id}", response_model=RunResponse)
async def get_run(run_id: str):
    """Get run status."""
    if run_id not in runs:
        raise HTTPException(status_code=404, detail="Run not found")

    run_data = runs[run_id]
    return RunResponse(
        run_id=run_data["run_id"],
        challenge_id=run_data["challenge_id"],
        status=run_data["status"],
        flag=run_data.get("flag"),
        steps=run_data["steps"]
    )


@router.get("/runs/{run_id}/trajectory")
async def get_trajectory(run_id: str):
    """Get run trajectory."""
    if run_id not in runs:
        raise HTTPException(status_code=404, detail="Run not found")

    return {"trajectory": runs[run_id].get("trajectory", [])}


@router.post("/knowledge/ingest")
async def ingest_knowledge(request: KnowledgeIngestRequest):
    """Ingest CTF writeups into the knowledge base."""
    try:
        ingestor = KnowledgeIngestor()
        result = ingestor.ingest_directory(request.directory)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/knowledge/search", response_model=KnowledgeSearchResponse)
async def search_knowledge(request: KnowledgeSearchRequest):
    """Search the knowledge base."""
    try:
        retriever = KnowledgeRetriever()
        results = retriever.search(
            query=request.query,
            max_results=request.max_results,
            category=request.category
        )
        return KnowledgeSearchResponse(results=results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
