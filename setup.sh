#!/bin/bash

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Set up environment variables
if [ ! -f .env ]; then
    echo "GROQ_API_KEY=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" > .env
fi

echo "Setup complete! Run 'python run.py' to start the application." 