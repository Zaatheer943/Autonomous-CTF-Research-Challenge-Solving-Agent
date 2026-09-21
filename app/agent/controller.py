from typing import Dict, Any, Optional
from app.agent.state import AgentState
from app.agent.memory import AgentMemory
from app.agent.planner import Planner
from app.tools.executor import ToolExecutor
from app.knowledge.retriever import KnowledgeRetriever
from app.flags.detector import FlagDetector
from app.flags.validator import FlagValidator
from app.config import settings
import uuid
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class AgentController:
    def __init__(self, challenge_id: str, challenge_description: str, target_url: str):
        self.challenge_id = challenge_id
        self.challenge_description = challenge_description
        self.target_url = target_url
        self.run_id = str(uuid.uuid4())

        self.state = AgentState(challenge_id=challenge_id)
        self.memory = AgentMemory(challenge_id=challenge_id, run_id=self.run_id)
        self.planner = Planner()
        self.tool_executor = ToolExecutor(target_url=target_url)
        self.knowledge_retriever = KnowledgeRetriever()
        self.flag_detector = FlagDetector()
        self.flag_validator = FlagValidator()

    def run(self) -> Dict[str, Any]:
        self.state.mark_running()
        solved = False
        flag = None

        try:
            while not solved and self.state.current_step < settings.max_agent_steps:
                # Observe current state
                observation = self._observe()

                # Retrieve relevant knowledge
                knowledge = self.knowledge_retriever.search(
                    query=self.challenge_description,
                    context=observation
                )

                # Choose action
                action = self.planner.choose_action(
                    challenge_description=self.challenge_description,
                    current_state=self.state,
                    knowledge=knowledge,
                    available_tools=self.tool_executor.get_available_tools()
                )

                # Execute action
                result = self.tool_executor.execute(
                    tool_name=action["action"],
                    parameters=action["parameters"]
                )

                # Update state
                self.state.add_observation(observation)
                self.state.add_hypothesis(action["hypothesis"])
                self.state.add_action(action, success=result["success"])
                self.state.increment_step()

                # Detect flag
                flag = self.flag_detector.detect(result["output"])
                if flag:
                    self.state.add_candidate_flag(flag)

                    # Validate flag
                    if self.flag_validator.validate(self.challenge_id, flag):
                        solved = True
                        self.state.mark_solved()
                        flag = flag
                    else:
                        # Invalid flag, continue
                        pass

                # Log trajectory
                self.memory.add_step(
                    step=self.state.current_step,
                    observation=observation,
                    knowledge_retrieved=knowledge,
                    hypothesis=action["hypothesis"],
                    action=action,
                    result=result["output"],
                    flag_found=bool(flag)
                )

            if not solved:
                self.state.mark_failed()

        except Exception as e:
            self.state.mark_failed()
            print(f"Error during execution: {e}")

        finally:
            self.memory.save()

        return {
            "run_id": self.run_id,
            "challenge_id": self.challenge_id,
            "status": self.state.status,
            "flag": flag,
            "steps": self.state.current_step,
            "trajectory": [step.model_dump() for step in self.memory.get_trajectory()]
        }

    def _observe(self) -> str:
        if self.state.current_step == 0:
            return f"Starting challenge {self.challenge_id} at {self.target_url}"
        else:
            return f"Step {self.state.current_step}: {len(self.state.observations)} observations, {len(self.state.hypotheses)} hypotheses"
