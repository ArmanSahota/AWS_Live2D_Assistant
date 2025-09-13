# Configuration Files Fix

This document explains the changes made to fix the issue with empty configuration files in the context menu.

## Problem

The application was not properly displaying configuration files in the context menu. This was due to issues with the WebSocket connection stability and how configuration files were being loaded and displayed.

## Changes Made

1. **Enhanced WebSocket Connection Reliability**:
   - Added a reconnection mechanism in `reconnect.js` to automatically reconnect when the WebSocket connection is lost
   - Improved error handling and logging in the WebSocket connection code
   - Added periodic connection checks to ensure the WebSocket stays connected

2. **Improved Configuration File Loading**:
   - Enhanced the `_scan_config_alts_directory()` method in `server.py` to properly detect both `.yaml` and `.yml` files
   - Added error handling and logging to help diagnose issues
   - Added directory existence check to prevent errors when the config_alts directory doesn't exist

3. **Enhanced WebSocket Message Handling**:
   - Added better error handling and logging for WebSocket messages
   - Improved the handling of configuration files in the WebSocket client
   - Added retry logic for fetching configurations when the initial attempt fails

4. **Added Diagnostic Tools**:
   - Created `test_config_loading.py` to verify Python-side configuration loading
   - Created `test_electron_config.js` to verify Node.js-side configuration loading
   - Added a `restart_app.bat` script to easily restart the application with a clean state

## How to Test

1. Run the `restart_app.bat` script to restart the application with a clean state:
   ```
   cd LLM-Live2D-Desktop-Assitant-main
   .\restart_app.bat
   ```

2. Right-click on the application window to open the context menu

3. The "Switch Config" submenu should now show both configuration files:
   - `claude_aws.yaml`
   - `mashiro.yaml`

4. Select a configuration file to switch to that configuration

## Troubleshooting

If the configuration files still don't appear in the context menu:

1. Check the browser console for any error messages (press F12 to open the developer tools)

2. Run the diagnostic scripts to verify that the configuration files are being loaded correctly:
   ```
   cd LLM-Live2D-Desktop-Assitant-main
   python test_config_loading.py
   node test_electron_config.js
   ```

3. Check the server logs for any error messages related to configuration file loading

4. Try manually restarting the WebSocket connection by refreshing the page or restarting the application

## Files Modified

- `server.py`: Improved configuration file scanning and loading
- `static/desktop/websocket.js`: Enhanced WebSocket connection reliability and error handling
- `static/desktop.html`: Added reconnect.js script
- `static/desktop/reconnect.js`: Added WebSocket reconnection mechanism

## Files Added

- `config_alts/claude_aws.yaml`: Added a new configuration file for Claude AWS
- `test_config_loading.py`: Added a script to test Python-side configuration loading
- `test_electron_config.js`: Added a script to test Node.js-side configuration loading
- `restart_app.bat`: Added a script to restart the application with a clean state
- `CONFIG_FIX_README.md`: This documentation file
