from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class AgentStatus(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    SOLVED = "solved"
    FAILED = "failed"
    TIMEOUT = "timeout"


class AgentState(BaseModel):
    challenge_id: str
    objective: str = "find the flag"
    observations: List[str] = Field(default_factory=list)
    hypotheses: List[str] = Field(default_factory=list)
    actions: List[Dict[str, Any]] = Field(default_factory=list)
    successful_actions: List[Dict[str, Any]] = Field(default_factory=list)
    failed_actions: List[Dict[str, Any]] = Field(default_factory=list)
    discovered_urls: List[str] = Field(default_factory=list)
    discovered_files: List[str] = Field(default_factory=list)
    candidate_flags: List[str] = Field(default_factory=list)
    status: AgentStatus = AgentStatus.IDLE
    current_step: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def add_observation(self, observation: str):
        self.observations.append(observation)

    def add_hypothesis(self, hypothesis: str):
        self.hypotheses.append(hypothesis)

    def add_action(self, action: Dict[str, Any], success: bool):
        self.actions.append(action)
        if success:
            self.successful_actions.append(action)
        else:
            self.failed_actions.append(action)

    def add_discovered_url(self, url: str):
        if url not in self.discovered_urls:
            self.discovered_urls.append(url)

    def add_discovered_file(self, file_path: str):
        if file_path not in self.discovered_files:
            self.discovered_files.append(file_path)

    def add_candidate_flag(self, flag: str):
        if flag not in self.candidate_flags:
            self.candidate_flags.append(flag)

    def increment_step(self):
        self.current_step += 1

    def mark_running(self):
        self.status = AgentStatus.RUNNING
        self.start_time = datetime.now()

    def mark_solved(self):
        self.status = AgentStatus.SOLVED
        self.end_time = datetime.now()

    def mark_failed(self):
        self.status = AgentStatus.FAILED
        self.end_time = datetime.now()

    def mark_timeout(self):
        self.status = AgentStatus.TIMEOUT
        self.end_time = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()
