# Server Port Conflict Troubleshooting Guide

## Problem

When running the Live2D Assistant, you may encounter the following error:

```
ERROR: [Errno 10048] error while attempting to bind on address ('0.0.0.0', 1018): only one usage of each socket address (protocol/network address/port) is normally permitted
```

This error occurs because the FastAPI server component is trying to bind to port 1018, but this port is already in use by another process.

## Solution

There are several ways to resolve this issue:

### Option 1: Modify the Server Port

1. Edit `server.py` to use a different port.
2. Edit `.env` to include a PORT variable.

### Option 2: Kill Processes Using the Port

1. Identify processes using port 1018
2. Kill those processes to free up the port

### Option 3: Use the Fixed Port Configuration

We've created a fixed configuration that should resolve this issue automatically.

## Implementation

This guide includes a patch to the `server.py` file that will:

1. Use an environment variable PORT if specified
2. Otherwise try the default port 1018
3. If that fails, automatically try alternative ports (1019, 1020, etc.)
4. Show a clear message about which port it's using
