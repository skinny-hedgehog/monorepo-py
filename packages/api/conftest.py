import sys
from pathlib import Path

# Add the src directory to Python path so tests can import from domain, routes, etc.
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Add the package root to Python path so tests can import from tests module
package_root = Path(__file__).parent
sys.path.insert(0, str(package_root))
