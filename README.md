# Revit MCP

## Overview

Revit MCP is a Python package that provides integration with Revit through the Model Context Protocol (MCP). It allows you to send commands to Revit and receive responses, enabling automation and interaction with Revit models.

## Features

- Connect to Revit addon socket server.
- Send commands to create objects in Revit.
- Handle responses and errors from Revit.
- Manage server startup and shutdown lifecycle.

## Installation

To install Revit MCP, you can use pip:from revit_mcp import RevitConnection

```python
from revit_mcp import RevitConnection

# Create a RevitConnection instance
revit_connection = RevitConnection(host="localhost", port=8080)

# Connect to the Revit addon socket server
if revit_connection.connect():
    # Send a command to create an object in Revit
    response = revit_connection.send_command("CreateWalls", [
        {"startX": 0, "startY": 0, "endX": 12000, "endY": 0, "height": 3000, "width": 200},
        {"startX": 12000, "startY": 0, "endX": 12000, "endY": 10000, "height": 3000, "width": 200},
        {"startX": 12000, "startY": 10000, "endX": 0, "endY": 10000, "height": 3000, "width": 200},
        {"startX": 0, "startY": 10000, "endX": 0, "endY": 0, "height": 3000, "width": 200},
    ])

    # Handle the response
    if response.get("status") == "success":
        print("Object created successfully")
    else:
        print(f"Error: {response.get('message')}")

    # Disconnect from the Revit addon socket server
    revit_connection.disconnect()
else:
    print("Failed to connect to Revit")
```

This command will start the server using the main function defined in main.py, which in turn calls the main function from server.py.
