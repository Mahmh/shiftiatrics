#!/bin/bash
tmux new-session -d -s appsession
tmux send-keys -t appsession 'bash cmd/run_web.sh' C-m
tmux split-window -h
tmux send-keys -t appsession 'bash cmd/run_db.sh' C-m
tmux split-window -v
tmux send-keys -t appsession 'bash cmd/run_api.sh' C-m
tmux select-layout tiled

# Function to wait for the server and send the signup request
wait_for_server() {
    for i in $(seq 1 14); do
        # Send a request to check readiness at /accounts
        response=$(curl -s -w "%{http_code}" -o /tmp/curl_response.json http://localhost:8000/accounts)
        http_status=$(echo "$response" | tail -c 4) # Extract the last 3 characters (HTTP status)

        # Read response body for additional validation
        body=$(cat /tmp/curl_response.json)

        if [ "$http_status" = "200" ] && ! echo "$body" | grep -q '"error"'; then
            break
        fi

        sleep 1
    done

    # Send a CURL request to the signup endpoint
    echo "Sending signup request..."
    curl -X POST http://localhost:8000/accounts/signup \
        -H "Content-Type: application/json" \
        -d '{"username": "Sam Anderson", "password": "123"}'
    echo "Signup request sent."
}

# Run the server waiting logic in the background. Disable this by passing the -n flag
if [ "$1" != "-n" ]; then
    wait_for_server &
fi

# Attach to the tmux session
tmux select-pane -t appsession:.1
tmux attach-session -t appsession