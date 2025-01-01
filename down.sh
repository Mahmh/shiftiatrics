# #!/bin/bash
SESSION_NAME=appsession

# Check if the tmux session exists
if tmux has-session -t $SESSION_NAME 2>/dev/null; then
    echo "Cleaning up tmux session: $SESSION_NAME"
    # Loop through each pane in the session and send SIGINT
    tmux list-panes -t $SESSION_NAME -F "#{pane_pid}" | while read -r pane_pid; do
        echo "Sending SIGINT to process with PID $pane_pid"
        kill -INT "$pane_pid" 2>/dev/null
    done
    # Wait for processes to terminate gracefully
    sleep 2
    # Kill the tmux session if it's still running
    tmux kill-session -t $SESSION_NAME
    # Stop DB container
    cd src
    sudo docker-compose down

    echo "Tmux session $SESSION_NAME terminated."
else
    echo "Tmux session $SESSION_NAME does not exist."
fi