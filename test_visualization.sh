#!/bin/bash
# Test script for the new CPU visualization feature

echo "=== Testing CPU Visualization Feature ==="
echo ""
echo "This will run the fibonacci example in step mode with CPU view"
echo "Press 's' or Enter to step through instructions"
echo "Press 'q' to quit"
echo ""
read -p "Press Enter to start..."

uv run python main.py -s --cpu-view examples/fibonacci.asm
