$(python3 .j2/runner.py tasks-refine --feature $(echo "$ARGUMENTS" | awk '{print $1}') --request "$(echo "$ARGUMENTS" | cut -d' ' -f2-)" --root .)
