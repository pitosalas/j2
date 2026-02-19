$(python3 .j2/runner.py start-task --feature $(echo "$ARGUMENTS" | awk '{print $1}') --task $(echo "$ARGUMENTS" | awk '{print $2}') --root .)
