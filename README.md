# xml.Revit.MCP Tools Overview

[English](./README.md) | [中文文档](./README-zh.md)

xml.Revit.MCP provides a comprehensive set of tools for integrating with Autodesk Revit through the Model Context Protocol (MCP). This library serves as a bridge between AI assistants and Revit, enabling powerful automation capabilities and programmatic interaction with building models.

![xml.Revit.png](imgs/xml.Revit.png)

## Key Features

The tool library includes numerous functions for Revit automation and interaction:

**Basic Operations:**

- Get available commands from Revit plugin
- Execute specified commands in Revit
- Call specific Revit functions with parameters
- Retrieve view data and selected elements

**Element Management:**

- Find elements by category
- Get element parameters and locations
- Update element parameters
- Delete elements
- Show/highlight elements in current view
- Move elements to new positions

**Creation Tools:**

- Create levels/floors
- Create floor plan views
- Create grid lines
- Create walls and floors
- Create rooms and room tags
- Create doors and windows
- Create MEP elements (ducts, pipes, cable trays)
- Create family instances
- Link DWG files
- Create sheets

## Installation Requirements

- **xml.Revit**: Version 1.3.4.3 or newer
- **Python**: 3.10 or newer
- **UV Package Manager**: Required for installation
- **Revit**: Compatible with versions 2019-2024 (with plugin)

## Installation Process

1. First, install the UV package manager:

   ```bash
   pip install uv
   ```

2. Install the revit-mcp package:

   ```bash
   pip install revit-mcp
   ```

3. Test the installation:
   ```bash
   uvx revit-mcp
   ```
   You should see: `RevitMCPServer - INFO - Successfully connected to Revit on startup`

## Integration with AI Assistants

### Claude for Desktop

Edit `claude_desktop_config.json` to include:

### Cursor

Edit `mcp.json` to include:

### Cline

Edit `cline_mcp_setting.json` to include:

```json
{
  "mcpServers": {
    "RevitMCPServer": {
      "disabled": false,
      "timeout": 30,
      "command": "uvx",
      "args": ["revit-mcp"],
      "transportType": "stdio",
      "autoApprove": [
        "active_view",
        "call_func",
        "create_cable_trays",
        "create_door_windows",
        "create_ducts",
        "create_family_instances",
        "create_floors",
        "create_floor_plan_views",
        "create_grids",
        "create_levels",
        "create_pipes",
        "create_room_separation_lines",
        "create_room_tags",
        "create_rooms",
        "create_sheets",
        "create_walls",
        "delete_elements",
        "execute_commands",
        "find_elements",
        "get_commands",
        "get_locations",
        "get_selected_elements",
        "get_view_data",
        "link_dwg_and_activate_view",
        "move_elements",
        "parameter_elements",
        "show_elements",
        "update_elements"
      ]
    }
  }
}
```

## Extending Functionality

You can create custom MCP DLL files to implement additional functionality by:

1. Implementing the `xml.Revit.MCP.Public.IMCPMethod` interface
2. Following JSON-RPC 2.0 specification for communication
3. Compiling to a DLL and placing it in the designated MCP folder

## Plugin Configuration

When using the revit-mcp-plugin:

1. Register the plugin with Revit
2. Configure commands through: Add-in Modules → Revit MCP Plugin → Settings
3. Enable the service: Add-in → Revit MCP Plugin → Revit MCP Switch

Once enabled, AI assistants can discover and control your Revit program, executing the various commands provided by the xml.Revit.MCP tools library.
