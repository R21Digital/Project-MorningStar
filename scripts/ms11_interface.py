#!/usr/bin/env python3
"""
DEPRECATED: This wrapper will be removed in a future version.
Please use: python scripts/deploy/ms11_interface.py
"""

import os
import sys
import warnings
from pathlib import Path

# Show deprecation warning
warnings.warn(
    "scripts/ms11_interface.py is deprecated. "
    "Please use: python scripts/deploy/ms11_interface.py",
    DeprecationWarning,
    stacklevel=2
)

# Add the new location to path and import
new_script_path = Path(__file__).parent / "deploy" / "ms11_interface.py"

if new_script_path.exists():
    # Execute the new script in the same process
    with open(new_script_path, 'r') as f:
        script_code = f.read()
    
    # Set up the execution environment
    script_globals = {
        '__file__': str(new_script_path),
        '__name__': '__main__' if __name__ == '__main__' else __name__,
    }
    
    exec(script_code, script_globals)
else:
    print(f"ERROR: Could not find {new_script_path}")
    print("The project structure may have changed.")
    sys.exit(1)