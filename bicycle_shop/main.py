import importlib
import os
import sys
from pathlib import Path

# # Check Python version is correct, commented out till tested
# if sys.version_info < (3, 6):
#     sys.exit("This script requires Python 3.6 or higher!")

import subprocess

# Keep import names aligned with installed package names from requirements.
REQUIRED_MODULES = {
    "PIL": "Pillow",
    "colorama": "colorama",
    "qrcode": "qrcode",
    "numpy": "numpy",
    "cv2": "opencv-python",
}


def _in_virtual_environment():
    """Return True when running inside a virtual environment."""
    return (
        hasattr(sys, "real_prefix")
        or sys.prefix != getattr(sys, "base_prefix", sys.prefix)
        or bool(os.environ.get("VIRTUAL_ENV"))
    )


def _project_venv_python(project_root):
    """Return the project virtualenv Python path when available."""
    candidates = [
        project_root / ".venv" / "bin" / "python3",
        project_root / ".venv" / "bin" / "python",
        project_root / ".venv" / "Scripts" / "python.exe",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def install_requirements():
    """Validate required dependencies and optionally install them.

    By default this function only checks imports and provides setup guidance.
    Set BICYCLE_SHOP_AUTO_INSTALL_DEPS=1 to enable runtime installation.
    """
    missing_modules = []
    for module_name in REQUIRED_MODULES:
        try:
            importlib.import_module(module_name)
        except ImportError:
            missing_modules.append(module_name)

    if not missing_modules:
        return

    requirements_path = Path(__file__).resolve().parents[1] / "requirements.txt"
    project_root = requirements_path.parent
    project_venv_python = _project_venv_python(project_root)
    missing_packages = [REQUIRED_MODULES[name] for name in missing_modules]

    if os.environ.get("BICYCLE_SHOP_AUTO_INSTALL_DEPS") == "1":
        if not _in_virtual_environment():
            raise RuntimeError(
                "Refusing auto-install outside a virtual environment.\n"
                f"Current interpreter: {sys.executable}\n"
                "Activate a venv first, then run again."
            )
        print(f"Missing dependencies detected ({', '.join(missing_packages)}). Installing...")
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-r", str(requirements_path)]
        )
        return

    package_list = ", ".join(missing_packages)
    interpreter_hint = ""
    if project_venv_python:
        interpreter_hint = (
            "\nProject virtual environment detected.\n"
            f"Run with:\n  {project_venv_python} {Path(__file__).resolve()}"
        )

    raise RuntimeError(
        "Missing required dependencies: "
        f"{package_list}\n"
        f"Current interpreter: {sys.executable}\n"
        "Install them in your active environment using one of:\n"
        f"  uv pip install -r {requirements_path}\n"
        f"  {sys.executable} -m pip install -r {requirements_path}\n"
        f"{interpreter_hint}\n"
        "Optional: set BICYCLE_SHOP_AUTO_INSTALL_DEPS=1 to auto-install at startup."
    )


install_requirements()

from src.file_system.directory.directory_manager import initialize
from src.database.core.schema import create_tables
from src.database.users.user_manager import initialize_admin
from src.gui.core import start_app

"""Main entry point for the Bicycle Shop Management application.

This module initializes the application by:
1. Checking for first-time setup
2. Creating database tables
3. Ensuring admin user exists
4. Starting the GUI

The application will exit after creating config.ini on first run.
"""

def main():
    """Initialize and start the Bicycle Shop Management application.
    
    Returns:
        None: If first-time setup (exits after config creation)
        
    Note:
        Performs initialization in specific order:
        1. First-time setup check/config creation
        2. Database table creation
        3. Admin user initialization
        4. GUI startup
    """
    # Check if first run
    if initialize():
        return  # Exit after creating config.ini

    # Ensure database tables are created before starting the app
    create_tables()

    # Ensure an admin user exists on startup
    initialize_admin()

    # Start the GUI application
    start_app()

if __name__ == "__main__":
    main()
