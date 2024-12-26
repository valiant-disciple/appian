import streamlit.web.cli as stcli
import sys
import os

def main():
    # Get the absolute path to the app.py file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    app_path = os.path.join(current_dir, "src", "app.py")
    
    # Set the command line arguments for streamlit
    sys.argv = [
        "streamlit",
        "run",
        app_path,
        "--server.port=8502",
        "--server.address=localhost"
    ]
    
    # Run streamlit
    sys.exit(stcli.main())

if __name__ == "__main__":
    main() 