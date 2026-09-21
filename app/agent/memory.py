from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import json
from pathlib import Path


class TrajectoryStep(BaseModel):
    step: int
    observation: str
    knowledge_retrieved: List[str] = Field(default_factory=list)
    hypothesis: str
    action: Dict[str, Any]
    result: str
    flag_found: bool = False
    timestamp: datetime = Field(default_factory=datetime.now)


class AgentMemory:
    def __init__(self, challenge_id: str, run_id: str, storage_path: str = "./data/trajectories"):
        self.challenge_id = challenge_id
        self.run_id = run_id
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.trajectory: List[TrajectoryStep] = []

    def add_step(
        self,
        step: int,
        observation: str,
        knowledge_retrieved: List[str],
        hypothesis: str,
        action: Dict[str, Any],
        result: str,
        flag_found: bool = False
    ):
        trajectory_step = TrajectoryStep(
            step=step,
            observation=observation,
            knowledge_retrieved=knowledge_retrieved,
            hypothesis=hypothesis,
            action=action,
            result=result,
            flag_found=flag_found
        )
        self.trajectory.append(trajectory_step)

    def get_trajectory(self) -> List[TrajectoryStep]:
        return self.trajectory

    def save(self):
        trajectory_file = self.storage_path / f"{self.challenge_id}_{self.run_id}.json"
        with open(trajectory_file, "w") as f:
            json.dump(
                {
                    "challenge_id": self.challenge_id,
                    "run_id": self.run_id,
                    "trajectory": [step.model_dump() for step in self.trajectory]
                },
                f,
                indent=2,
                default=str
            )

    def load(self, run_id: str) -> Optional[List[TrajectoryStep]]:
        trajectory_file = self.storage_path / f"{self.challenge_id}_{run_id}.json"
        if not trajectory_file.exists():
            return None

        with open(trajectory_file, "r") as f:
            data = json.load(f)
            self.trajectory = [TrajectoryStep(**step) for step in data["trajectory"]]
            return self.trajectory
