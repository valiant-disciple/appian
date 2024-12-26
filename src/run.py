import sys
import streamlit.web.cli as stcli
import os

def main():
    # Get the absolute path to this file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Set the command line arguments for streamlit
    sys.argv = [
        "streamlit",
        "run",
        os.path.join(current_dir, "app.py"),
        "--server.port=8501",
        "--server.address=localhost"
    ]
    
    # Run streamlit
    sys.exit(stcli.main())

if __name__ == "__main__":
    main()