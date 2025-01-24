#!/bin/bash
tmux new-session -d -s appsession
tmux send-keys -t appsession 'bash cmd/run_web.sh' C-m
tmux split-window -h
tmux send-keys -t appsession 'bash cmd/run_db.sh' C-m
tmux split-window -v
tmux send-keys -t appsession 'bash cmd/run_api.sh' C-m
tmux select-layout tiled

# Attach to the tmux session
tmux select-pane -t appsession:.1
tmux attach-session -t appsession