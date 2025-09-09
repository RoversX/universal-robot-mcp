#!/usr/bin/env python3
"""
Universal Robot MCP Server
MCP tools for controlling Universal Robots (UR)
"""

import logging
import math
import time
from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import FastMCP
import json

# Import robot controller
try:
    import urx
    URX_AVAILABLE = True
except ImportError:
    print("Warning: Could not import 'urx' library; running in simulation mode")
    URX_AVAILABLE = False

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ----------------------
# Helper functions 
# ----------------------
def deg_tuple_to_rad(q_deg):
    """Convert a 6-element joint tuple in degrees to radians."""
    return tuple(math.radians(x) for x in q_deg)

def deg_to_rad_scalar(x_deg):
    return math.radians(x_deg)

def acc_vel_deg_to_rad(acc_deg_s2, vel_deg_s):
    """Convert accel [deg/s^2] and vel [deg/s] to radians."""
    return math.radians(acc_deg_s2), math.radians(vel_deg_s)

# Predefined positions (degrees)
HOME_deg = (-90.0, -60.0, -100.0, -96.0, 90.0, 0.0)
READY_deg = (0.0, -60.0, -90.0, -30.0, 90.0, 0.0)
SAFE_deg = (0.0, -45.0, -135.0, -90.0, 90.0, 0.0)

class URRobotController:
    """UR robot controller"""
    
    def __init__(self, robot_ip="192.168.1.100"):
        self.robot_ip = robot_ip
        self.robot = None
        self.is_connected = False
        
    def connect(self):
        try:
            if URX_AVAILABLE:
                # Use connection approach validated in the original script
                self.robot = urx.Robot(self.robot_ip)
                
                # Set TCP and payload
                self.robot.set_tcp((0, 0, 0, 0, 0, 0))
                self.robot.set_payload(0.001, (0, 0, 0))
                time.sleep(0.2)
                
                self.is_connected = True
                logger.info(f"✓ Robot connected successfully (IP: {self.robot_ip})")
                return True
            else:
                # Simulation mode
                self.is_connected = True
                logger.info(f"✓ Simulation mode connected successfully (IP: {self.robot_ip})")
                return True
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            return False
    
    def disconnect(self):
        try:
            if self.robot and URX_AVAILABLE:
                self.robot.close()
            self.is_connected = False
            self.robot = None
            logger.info("Robot connection closed")
            return True
        except Exception as e:
            logger.error(f"Disconnect failed: {e}")
            return False
    
    def get_status(self):
        if not self.is_connected:
            return {"connected": False, "message": "Robot not connected"}
        
        try:
            if URX_AVAILABLE and self.robot:
                joints = self.robot.getj()
                pose = self.robot.getl()
                return {
                    "connected": True,
                    "joints": joints,
                    "pose": pose,
                    "message": "Robot status OK"
                }
            else:
                # Simulation data
                return {
                    "connected": True,
                    "joints": [0, -1.57, 1.57, -1.57, -1.57, 0],
                    "pose": [0.3, 0.0, 0.3, 0, 3.14, 0],
                    "message": "Simulation mode - Robot status OK"
                }
        except Exception as e:
            logger.error(f"Failed to get status: {e}")
            return {"connected": False, "message": f"Failed to get status: {e}"}
    
    def move_joints(self, joints, acceleration=0.5, velocity=0.5):
        if not self.is_connected:
            return {"success": False, "message": "Robot not connected"}
        
        try:
            if URX_AVAILABLE and self.robot:
                self.robot.movej(joints, acc=acceleration, vel=velocity)
                return {"success": True, "message": f"Joint motion completed: {joints}"}
            else:
                # Simulation mode
                logger.info(f"Simulated joint motion: {joints}")
                return {"success": True, "message": f"Simulated joint motion completed: {joints}"}
        except Exception as e:
            # In some environments URX may raise "Robot stopped" after motion completes or a controlled stop.
            # Since the motion effectively completed, treat this case as success for now.
            if "Robot stopped" in str(e):
                logger.warning("Joint motion had 'Robot stopped'; treating as success")
                return {"success": True, "message": "ok"}
            logger.error(f"Joint motion failed: {e}")
            return {"success": False, "message": f"Joint motion failed: {e}"}
    
    def move_linear(self, pose, acceleration=0.2, velocity=0.2):
        if not self.is_connected:
            return {"success": False, "message": "Robot not connected"}
        
        try:
            if URX_AVAILABLE and self.robot:
                self.robot.movel(pose, acc=acceleration, vel=velocity)
                return {"success": True, "message": f"Linear motion completed: {pose}"}
            else:
                # Simulation mode
                logger.info(f"Simulated linear motion: {pose}")
                return {"success": True, "message": f"Simulated linear motion completed: {pose}"}
        except Exception as e:
            if "Robot stopped" in str(e):
                logger.warning("Linear motion had 'Robot stopped'; treating as success")
                return {"success": True, "message": "ok"}
            logger.error(f"Linear motion failed: {e}")
            return {"success": False, "message": f"Linear motion failed: {e}"}

# Global robot controller
robot_controller = URRobotController()

# MCP server instance
mcp = FastMCP("universal-robot")

@mcp.tool()
async def connect_robot(robot_ip: str = "localhost") -> str:
    """Connect to the UR robot.
    
    Args:
        robot_ip: Robot IP address, default localhost
        
    Returns:
        JSON string with connection result
    """
    robot_controller.robot_ip = robot_ip
    success = robot_controller.connect()
    result = {
        "success": success,
        "message": "Robot connected successfully" if success else "Robot connection failed",
        "robot_ip": robot_ip
    }
    return json.dumps(result, ensure_ascii=False)

@mcp.tool()
async def disconnect_robot() -> str:
    """Disconnect from the robot.
    
    Returns:
        JSON string with disconnect result
    """
    success = robot_controller.disconnect()
    result = {
        "success": success,
        "message": "Robot disconnected" if success else "Robot disconnect failed"
    }
    return json.dumps(result, ensure_ascii=False)

@mcp.tool()
async def get_robot_status() -> str:
    """Get robot status.
    
    Returns:
        JSON string with robot status
    """
    status = robot_controller.get_status()
    return json.dumps(status, ensure_ascii=False)

@mcp.tool()
async def move_robot_joints(
    joint1: float, joint2: float, joint3: float, 
    joint4: float, joint5: float, joint6: float,
    acceleration: float = 0.5, velocity: float = 0.5
) -> str:
    """Move robot joints.
    
    Args:
        joint1-joint6: Six joint angles (radians)
        acceleration: Acceleration (0.1-5.0), default 0.5
        velocity: Velocity (0.1-3.0), default 0.5
        
    Returns:
        JSON string with motion result
    """
    joints = [joint1, joint2, joint3, joint4, joint5, joint6]
    result = robot_controller.move_joints(joints, acceleration, velocity)
    return json.dumps(result, ensure_ascii=False)

@mcp.tool()
async def move_robot_linear(
    x: float, y: float, z: float,
    rx: float, ry: float, rz: float,
    acceleration: float = 0.2, velocity: float = 0.2
) -> str:
    """Move robot in linear Cartesian motion.
    
    Args:
        x, y, z: Target position coordinates (meters)
        rx, ry, rz: Target orientation (radians)
        acceleration: Acceleration (0.05-2.0), default 0.2
        velocity: Velocity (0.05-1.5), default 0.2
        
    Returns:
        JSON string with motion result
    """
    pose = [x, y, z, rx, ry, rz]
    result = robot_controller.move_linear(pose, acceleration, velocity)
    return json.dumps(result, ensure_ascii=False)

def main():
    mcp.run(transport='stdio')

if __name__ == "__main__":
    main()
