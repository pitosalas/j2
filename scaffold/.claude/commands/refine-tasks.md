$(python3 .planner/runner.py refine-tasks --feature $(echo "$ARGUMENTS" | awk '{print $1}') --request "$(echo "$ARGUMENTS" | cut -d' ' -f2-)" --root .)
