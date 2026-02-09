from pathlib import Path

# This is the root directory for the cloud drive where files will be stored and accessed by the GAIA agent.
# Make sure this directory exists and is accessible by the GAIA agent. You can change this path to point to your desired cloud drive location.
# Example: DRIVE_ROOT = Path("/path/to/your/cloud/drive").resolve()
# For default, this will point to our ./Gaia.Engine/Data directory, but you can change it to any directory you want.
DRIVE_ROOT = (Path(__file__).parent / "data").resolve()