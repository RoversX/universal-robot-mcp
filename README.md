# Universal Robot MCP Server

A Model Context Protocol (MCP) server that provides AI assistants and LLM applications with secure, controlled access to Universal Robots functionality. This server enables real-time robot control, status monitoring, and motion planning through a standardized MCP interface.

## Features

- **Robot Connection Management** - Connect/disconnect from UR robots safely
- **Real-time Status Monitoring** - Get joint positions, poses, and robot health
- **Joint Motion Control** - Precise angular movement with safety limits
- **Linear Motion Control** - Cartesian path planning and execution
- **Simulation Mode** - Test and develop without physical hardware
- **Safety First** - Built-in collision detection and movement validation

## Installation

### Quick Start with uvx (Recommended)
```bash
uvx universal-robot-mcp
```

### Install via pip
```bash
pip install universal-robot-mcp
```

### Development Installation
```bash
git clone <repository-url>
cd universal-robot-mcp
pip install -e .
```

## Usage

### AI Assistant Integration

**Claude Desktop**
```json
{
  "mcpServers": {
    "universal-robot": {
      "command": "uvx",
      "args": ["universal-robot-mcp"]
    }
  }
}
```

**Cursor / Other MCP Clients**
```json
{
  "mcpServers": {
    "universal-robot": {
      "command": "universal-robot-mcp"
    }
  }
}
```

**VS Code with MCP**
```json
{
  "mcp.servers": {
    "universal-robot": "uvx universal-robot-mcp"
  }
}
```

### Direct Usage
```bash
# Run the server directly
python -m universal_robot_mcp.server

# Or use the installed script
universal-robot-mcp
```

## Available Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `connect_robot` | Establish connection to UR robot | `robot_ip` (default: 192.168.1.100) |
| `disconnect_robot` | Safely disconnect from robot | None |
| `get_robot_status` | Get current joint positions and pose | None |
| `move_robot_joints` | Move to specific joint angles | `joint1-6`, `acceleration`, `velocity` |
| `move_robot_linear` | Linear movement in Cartesian space | `x,y,z,rx,ry,rz`, `acceleration`, `velocity` |

## Example Conversations

Once configured with your AI assistant:

- *"Connect to the robot and show me its current status"*
- *"Move the robot to home position safely"*  
- *"Execute a pick and place motion from coordinates X to Y"*
- *"What are the current joint angles?"*
- *"Move the robot 10cm up in the Z direction"*

## Robot Configuration

### Network Setup
- Default robot IP: `192.168.1.100`
- Ensure robot is connected to your network
- Verify robot is in Remote Control mode

### Safety Features
- Automatic TCP and payload configuration
- Movement speed and acceleration limits
- Connection timeout handling
- Emergency stop capabilities

## Supported Platforms

- **AI Assistants**: Claude Desktop, Cursor, Roo Code, Cline
- **IDEs**: VS Code, JetBrains IDEs (with MCP plugins)
- **Platforms**: macOS, Linux, Windows
- **Python**: 3.8, 3.9, 3.10, 3.11

## License

Apache-2.0

## Contributing

Contributions welcome! See our [contributing guide](CONTRIBUTING.md) for details.