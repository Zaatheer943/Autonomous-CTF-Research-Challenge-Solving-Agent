#!/usr/bin/env python3
"""
Analyze the agent trajectory from the last run
"""
import json
import glob
import sys
sys.path.append('.')

# Find the most recent trajectory
trajectory_files = glob.glob('./data/trajectories/*.json')
if trajectory_files:
    # Sort by modification time to get the most recent
    import os
    latest_file = max(trajectory_files, key=lambda x: os.path.getmtime(x))
    print(f"Analyzing trajectory: {latest_file}")

    with open(latest_file, 'r') as f:
        data = json.load(f)

    print(f"\nChallenge: {data['challenge_id']}")
    print(f"Run ID: {data['run_id']}")
    print(f"Total Steps: {len(data['trajectory'])}")

    print(f"\n=== First Step ===")
    first_step = data['trajectory'][0]
    print(f"Hypothesis: {first_step['hypothesis']}")
    print(f"Action: {first_step['action']['action']}")
    print(f"Parameters: {first_step['action']['parameters']}")
    print(f"Knowledge Retrieved: {len(first_step['knowledge_retrieved'])} chunks")
    print(f"Result: {first_step['result'][:100] if first_step['result'] else 'Empty (target not available)'}...")

    print(f"\n=== Last Step ===")
    last_step = data['trajectory'][-1]
    print(f"Step: {last_step['step']}")
    print(f"Hypothesis: {last_step['hypothesis']}")
    print(f"Action: {last_step['action']['action']}")
    print(f"Flag Found: {last_step['flag_found']}")

    print(f"\n=== Knowledge Retrieved (Sample) ===")
    if first_step['knowledge_retrieved']:
        print(f"First chunk preview: {first_step['knowledge_retrieved'][0][:200]}...")

else:
    print("No trajectory files found")
