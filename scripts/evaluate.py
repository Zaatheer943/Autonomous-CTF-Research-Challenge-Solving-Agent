#!/usr/bin/env python3
"""
CTF Agent Evaluation Benchmark

This script runs the agent against a set of CTF challenges and evaluates performance.
"""
import json
import sys
import os
import time
from datetime import datetime
from typing import Dict, List, Any

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.agent.controller import AgentController


class BenchmarkChallenge:
    def __init__(
        self,
        challenge_id: str,
        description: str,
        target_url: str,
        expected_flag: str,
        category: str = "web",
        difficulty: str = "medium",
        max_steps: int = 50
    ):
        self.challenge_id = challenge_id
        self.description = description
        self.target_url = target_url
        self.expected_flag = expected_flag
        self.category = category
        self.difficulty = difficulty
        self.max_steps = max_steps


class BenchmarkEvaluator:
    def __init__(self):
        self.results: List[Dict[str, Any]] = []
        self.start_time = None
        self.end_time = None

    def run_challenge(self, challenge: BenchmarkChallenge) -> Dict[str, Any]:
        """Run a single challenge and return results."""
        print(f"\n{'='*60}")
        print(f"Running challenge: {challenge.challenge_id}")
        print(f"Category: {challenge.category}")
        print(f"Difficulty: {challenge.difficulty}")
        print(f"Target: {challenge.target_url}")
        print(f"{'='*60}")

        challenge_start = time.time()

        try:
            controller = AgentController(
                challenge_id=challenge.challenge_id,
                challenge_description=challenge.description,
                target_url=challenge.target_url
            )

            result = controller.run()

            challenge_end = time.time()
            duration = challenge_end - challenge_start

            # Evaluate result
            solved = result["status"] == "solved"
            flag_correct = result["flag"] == challenge.expected_flag if result["flag"] else False

            evaluation = {
                "challenge_id": challenge.challenge_id,
                "category": challenge.category,
                "difficulty": challenge.difficulty,
                "expected_flag": challenge.expected_flag,
                "found_flag": result.get("flag"),
                "status": result["status"],
                "solved": solved,
                "flag_correct": flag_correct,
                "steps": result["steps"],
                "duration": duration,
                "run_id": result["run_id"],
                "trajectory": result["trajectory"]
            }

            print(f"\nResult: {result['status'].upper()}")
            if solved:
                print(f"✓ Solved in {result['steps']} steps ({duration:.2f}s)")
                if flag_correct:
                    print(f"✓ Flag correct: {result['flag']}")
                else:
                    print(f"✗ Flag incorrect: {result['flag']} (expected: {challenge.expected_flag})")
            else:
                print(f"✗ Failed to solve")

            return evaluation

        except Exception as e:
            challenge_end = time.time()
            duration = challenge_end - challenge_start

            print(f"\n✗ Error during execution: {e}")

            return {
                "challenge_id": challenge.challenge_id,
                "category": challenge.category,
                "difficulty": challenge.difficulty,
                "expected_flag": challenge.expected_flag,
                "found_flag": None,
                "status": "error",
                "solved": False,
                "flag_correct": False,
                "steps": 0,
                "duration": duration,
                "error": str(e)
            }

    def run_benchmark(self, challenges: List[BenchmarkChallenge]) -> Dict[str, Any]:
        """Run the full benchmark."""
        print(f"\n{'='*60}")
        print("CTF Agent Evaluation Benchmark")
        print(f"Total challenges: {len(challenges)}")
        print(f"{'='*60}")

        self.start_time = time.time()

        for challenge in challenges:
            result = self.run_challenge(challenge)
            self.results.append(result)

        self.end_time = time.time()
        total_duration = self.end_time - self.start_time

        # Calculate statistics
        solved_count = sum(1 for r in self.results if r["solved"])
        failed_count = len(self.results) - solved_count
        success_rate = (solved_count / len(self.results)) * 100 if self.results else 0

        avg_steps = sum(r["steps"] for r in self.results if r["solved"]) / solved_count if solved_count > 0 else 0
        avg_duration = sum(r["duration"] for r in self.results) / len(self.results) if self.results else 0

        # Print summary
        print(f"\n{'='*60}")
        print("BENCHMARK SUMMARY")
        print(f"{'='*60}")
        print(f"Total challenges: {len(self.results)}")
        print(f"Solved: {solved_count}")
        print(f"Failed: {failed_count}")
        print(f"Success rate: {success_rate:.1f}%")
        print(f"Average steps (solved): {avg_steps:.1f}")
        print(f"Average duration: {avg_duration:.2f}s")
        print(f"Total duration: {total_duration:.2f}s")
        print(f"{'='*60}")

        summary = {
            "total_challenges": len(self.results),
            "solved": solved_count,
            "failed": failed_count,
            "success_rate": success_rate,
            "average_steps": avg_steps,
            "average_duration": avg_duration,
            "total_duration": total_duration,
            "results": self.results,
            "timestamp": datetime.now().isoformat()
        }

        # Save results
        self.save_results(summary)

        return summary

    def save_results(self, summary: Dict[str, Any]):
        """Save benchmark results to file."""
        results_dir = "./data/evaluations"
        os.makedirs(results_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = os.path.join(results_dir, f"benchmark_{timestamp}.json")

        with open(results_file, "w") as f:
            json.dump(summary, f, indent=2, default=str)

        print(f"\nResults saved to: {results_file}")


def main():
    """Main entry point for benchmark evaluation."""
    # Define benchmark challenges
    challenges = [
        BenchmarkChallenge(
            challenge_id="demo-web",
            description="Simple web login challenge with SQL injection vulnerability",
            target_url="http://localhost:8000",
            expected_flag="CTF{demo_sql_injection_flag_12345}",
            category="web",
            difficulty="easy",
            max_steps=30
        ),
        # Add more challenges here as they are created
        # BenchmarkChallenge(
        #     challenge_id="web-xss-01",
        #     description="Cross-site scripting vulnerability in search functionality",
        #     target_url="http://localhost:8001",
        #     expected_flag="CTF{xss_flag_456}",
        #     category="web",
        #     difficulty="medium",
        #     max_steps=40
        # ),
    ]

    evaluator = BenchmarkEvaluator()
    summary = evaluator.run_benchmark(challenges)

    # Exit with appropriate code
    sys.exit(0 if summary["success_rate"] > 0 else 1)


if __name__ == "__main__":
    main()
