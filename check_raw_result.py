#!/usr/bin/env python3
"""
Check what the raw result looks like
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

    step_2 = data['trajectory'][1]  # Step 2
    result = step_2['result']

    print(f"Result type: {type(result)}")
    print(f"Result: {result}")

    # Check if result is a dict
    if isinstance(result, dict):
        print(f"\nResult is a dict with keys: {result.keys()}")
        if 'structured' in result:
            print(f"Structured data: {result['structured']}")
