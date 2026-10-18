# IT Infrastructure Inventory

A small web application for keeping a list of servers.
Built with Python, Flask, SQLite, HTML and CSS.

## What it does

- Shows a list of servers
- Adds a server (hostname, IP address, operating system)
- Shows the details of one server
- Edits a server
- Deletes a server
- Stores everything in a SQLite database file (`inventory.db`)

## Project layout

    inventory/
    ├── app.py              The Python application (Flask)
    ├── requirements.txt    List of Python packages the app needs
    ├── README.md           This file
    ├── templates/          HTML pages
    │   ├── base.html       Shared page layout
    │   ├── index.html      Server list
    │   ├── add.html        Add-server form
    │   ├── detail.html     One server's details
    │   └── edit.html       Edit-server form
    └── static/
        └── css/
            └── style.css   Colours and layout
    (inventory.db is created automatically the first time the app starts)

## Run it on Linux (Ubuntu / Debian)

    sudo apt update
    sudo apt install -y python3 python3-venv python3-pip
    cd inventory
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    python app.py

Then open http://127.0.0.1:5000 in a browser.
Press Ctrl+C in the terminal to stop the app.

## Notes

- The app listens on 127.0.0.1 only, so only your own computer can reach it.
- The secret key in app.py is for learning only.
