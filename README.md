# Revit MCP

[![Last Commit](https://img.shields.io/github/last-commit/ZedMoster/revit-mcp/dev?style=for-the-badge)](https://github.com/ZedMoster/revit-mcp/commits/main)

## Overview

Revit MCP is a Python package that provides integration with Revit through the Model Context Protocol (MCP). It allows you to send commands to Revit and receive responses, enabling automation and interaction with Revit models.

## Features

- Connect to Revit addon socket server.
- Send commands to create objects in Revit.
- Handle responses and errors from Revit.
- Manage server startup and shutdown lifecycle.

## Installation

### Prerequisites

- xml.Revit 1.3.4.3 or newer
- Python 3.10 or newer
- uv package manager:

On Windows install uv as

```bash
pip install uv
```

Otherwise installation instructions are on their website: [Install uv](https://docs.astral.sh/uv/getting-started/installation/)

⚠️ Do not proceed before installing UV

### Claude for Desktop Integration

Watch the setup instruction video (Assuming you have already installed uv)

Go to Claude > Settings > Developer > Edit Config.

edit `claude_desktop_config.json`

 to include the following:

```json
{
    "mcpServers": {
        "RevitMCPServer": {
            "command": "uvx",
            "args": [
                "revit-mcp"
            ]
        }
    }
}
```

### Cursor integration

Run **revit-mcp** without installing it permanently through uvx.

Go to Cursor Settings > MCP and paste this as a command.

edit `mcp.json`

```json
{
    "mcpServers": {
        "RevitMCPServer": {
            "command": "uvx",
            "args": [
                "revit-mcp"
            ]
        }
    }
}
```

### cline

You can use the cline command to run the command line interface of Revit MCP.

edit `cline_mcp_setting.json`

```json
{
    "mcpServers": {
        "RevitMCPServer": {
            "command": "uvx",
            "args": [
                "revit-mcp"
            ]
        }
    }
}
```
