#!/bin/bash

# Run any setup steps or pre-processing tasks here
echo "starting the covid-19 consultation chatbot service fastAPI..."

# Start the main application
uvicorn main:app --host 0.0.0.0 --port 8000