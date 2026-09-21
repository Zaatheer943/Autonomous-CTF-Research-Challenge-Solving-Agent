from typing import List, Dict, Any, Optional
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.agent.llm import get_llm_provider
from app.agent.state import AgentState


class Planner:
    def __init__(self):
        self.llm = get_llm_provider()
        self.system_prompt = """You are an autonomous CTF challenge-solving agent.

Your objective is to solve the configured CTF challenge and retrieve its flag.

You have access only to the tools provided by the environment.

Operate only within the configured CTF sandbox.

Before taking an action:
1. Analyze the current evidence.
2. Identify plausible hypotheses.
3. Choose an experiment that provides useful information.
4. Execute the minimum necessary action.
5. Analyze the result.
6. Update your state.

Do not assume that a technique works simply because a retrieved writeup used it.

Use retrieved writeups as evidence and examples, not as ground truth.

When a candidate flag is found, verify it before reporting success.

Provide your response in the following structured format:
hypothesis: [your current hypothesis about the challenge]
reason: [your reasoning for the next action]
action: [the tool you want to use]
parameters: [JSON object with tool parameters]
next_step: [what you plan to do after this action]"""

    def choose_action(
        self,
        challenge_description: str,
        current_state: AgentState,
        knowledge: List[str],
        available_tools: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": self._build_prompt(challenge_description, current_state, knowledge)}
        ]

        # Format tools for LLM
        tool_definitions = [
            {
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": tool["arguments_schema"]
                }
            }
            for tool in available_tools
        ]

        response = self.llm.generate_with_tools(messages, tool_definitions)

        # Parse the response
        result = {
            "hypothesis": "",
            "reason": "",
            "action": None,
            "parameters": {},
            "next_step": ""
        }

        if response["content"]:
            # Parse structured content
            content = response["content"]
            for line in content.split("\n"):
                if line.startswith("hypothesis:"):
                    result["hypothesis"] = line.replace("hypothesis:", "").strip()
                elif line.startswith("reason:"):
                    result["reason"] = line.replace("reason:", "").strip()
                elif line.startswith("action:"):
                    result["action"] = line.replace("action:", "").strip()
                elif line.startswith("parameters:"):
                    params_str = line.replace("parameters:", "").strip()
                    try:
                        import json
                        result["parameters"] = json.loads(params_str)
                    except:
                        result["parameters"] = {}
                elif line.startswith("next_step:"):
                    result["next_step"] = line.replace("next_step:", "").strip()

        # If tool calls were made, use them
        if response["tool_calls"]:
            tool_call = response["tool_calls"][0]
            result["action"] = tool_call["function"]["name"]
            try:
                import json
                result["parameters"] = json.loads(tool_call["function"]["arguments"])
            except:
                result["parameters"] = {}

        return result

    def _build_prompt(self, challenge_description: str, state: AgentState, knowledge: List[str]) -> str:
        prompt = f"""Challenge Description:
{challenge_description}

Current State:
- Status: {state.status}
- Step: {state.current_step}
- Observations: {len(state.observations)}
- Hypotheses: {len(state.hypotheses)}
- Discovered URLs: {state.discovered_urls}
- Discovered Files: {state.discovered_files}
- Candidate Flags: {state.candidate_flags}

Recent Observations:
"""
        for obs in state.observations[-5:]:
            prompt += f"- {obs}\n"

        if knowledge:
            prompt += f"\nRelevant Knowledge from Writeups:\n"
            for k in knowledge[:3]:
                prompt += f"- {k}\n"

        return prompt
