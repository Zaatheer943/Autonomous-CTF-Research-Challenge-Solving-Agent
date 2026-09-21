#!/usr/bin/env python3
"""
Check the latest trajectory to see what happened
"""
import json
import glob
import os

# Find the most recent trajectory
trajectory_files = glob.glob('./data/trajectories/*.json')
if trajectory_files:
    latest_file = max(trajectory_files, key=lambda x: os.path.getmtime(x))
    print(f"Analyzing trajectory: {latest_file}")

    with open(latest_file, 'r') as f:
        data = json.load(f)

    print(f"\nChallenge: {data['challenge_id']}")
    print(f"Run ID: {data['run_id']}")
    print(f"Total Steps: {len(data['trajectory'])}")

    print(f"\n=== Step 2 (SQL Injection Attempt) ===")
    step_2 = data['trajectory'][1]  # Step 2
    print(f"Hypothesis: {step_2['hypothesis']}")
    print(f"Action: {step_2['action']}")
    print(f"Result: {step_2['result'][:200]}...")
    print(f"Flag Found: {step_2['flag_found']}")

    # Check if flag is in the result
    result_str = str(step_2['result'])
    if 'CTF{' in result_str:
        print(f"\n[DETECTED] Flag appears to be in the result!")
        import re
        flags = re.findall(r'CTF\{[^}]+\}', result_str)
        print(f"Flags found: {flags}")
    else:
        print(f"\n[NOT DETECTED] Flag not found in result")

else:
    print("No trajectory files found")
