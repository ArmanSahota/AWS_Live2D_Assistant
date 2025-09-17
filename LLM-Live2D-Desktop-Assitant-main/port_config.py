"""
Global Port Configuration Manager
Ensures consistent port usage across frontend and backend components.
"""
import os
import socket
import atexit
import signal
import sys
from typing import Optional
from loguru import logger

class PortManager:
    """Centralized port management for consistent port allocation and cleanup."""
    
    # Default port configuration
    DEFAULT_BASE_PORT = 1018
    DEFAULT_PORT_RANGE = 10  # Will try ports 1018-1027
    
    def __init__(self):
        self.allocated_ports = set()
        self.base_port = self._get_base_port()
        self.current_port = None
        
        # Register cleanup handlers
        atexit.register(self.cleanup_all_ports)
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _get_base_port(self) -> int:
        """Get base port from environment or use default."""
        try:
            # Try SERVER_PORT first, then PORT, then default
            port = os.environ.get('SERVER_PORT') or os.environ.get('PORT')
            if port:
                return int(port)
        except ValueError:
            logger.warning(f"Invalid port in environment variables, using default {self.DEFAULT_BASE_PORT}")
        
        return self.DEFAULT_BASE_PORT
    
    def find_available_port(self, preferred_port: Optional[int] = None) -> int:
        """
        Find an available port, preferring the specified port or base port.
        
        Args:
            preferred_port: Preferred port to use if available
            
        Returns:
            Available port number
            
        Raises:
            RuntimeError: If no port is available in the range
        """
        start_port = preferred_port or self.base_port
        
        # First try the preferred/base port
        if self._is_port_available(start_port):
            self.current_port = start_port
            self.allocated_ports.add(start_port)
            logger.info(f"Using preferred port: {start_port}")
            return start_port
        
        # If preferred port is not available, search in range
        logger.warning(f"Preferred port {start_port} is in use, searching for alternatives...")
        
        for offset in range(1, self.DEFAULT_PORT_RANGE):
            port = start_port + offset
            if self._is_port_available(port):
                self.current_port = port
                self.allocated_ports.add(port)
                logger.info(f"Found available port: {port}")
                return port
        
        # If no port found in forward range, try backward
        for offset in range(1, self.DEFAULT_PORT_RANGE):
            port = start_port - offset
            if port > 1000 and self._is_port_available(port):  # Don't go below 1000
                self.current_port = port
                self.allocated_ports.add(port)
                logger.info(f"Found available port: {port}")
                return port
        
        raise RuntimeError(f"No available ports found in range {start_port-self.DEFAULT_PORT_RANGE} to {start_port+self.DEFAULT_PORT_RANGE}")
    
    def _is_port_available(self, port: int) -> bool:
        """Check if a port is available for binding."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind(('0.0.0.0', port))
                return True
        except socket.error:
            return False
    
    def release_port(self, port: int):
        """Release a specific port."""
        if port in self.allocated_ports:
            self.allocated_ports.remove(port)
            logger.info(f"Released port: {port}")
            
            # Force close any lingering connections
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    s.bind(('0.0.0.0', port))
            except socket.error:
                pass  # Port might already be released
    
    def cleanup_all_ports(self):
        """Clean up all allocated ports."""
        if self.allocated_ports:
            logger.info(f"Cleaning up ports: {sorted(self.allocated_ports)}")
            for port in list(self.allocated_ports):
                self.release_port(port)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        logger.info(f"Received signal {signum}, cleaning up ports...")
        self.cleanup_all_ports()
        sys.exit(0)
    
    def get_current_port(self) -> Optional[int]:
        """Get the currently allocated port."""
        return self.current_port
    
    def get_base_port(self) -> int:
        """Get the base port configuration."""
        return self.base_port

# Global port manager instance
port_manager = PortManager()

def get_available_port(preferred_port: Optional[int] = None) -> int:
    """Convenience function to get an available port."""
    return port_manager.find_available_port(preferred_port)

def cleanup_ports():
    """Convenience function to cleanup all ports."""
    port_manager.cleanup_all_ports()

def get_current_port() -> Optional[int]:
    """Get the currently allocated port."""
    return port_manager.get_current_port()