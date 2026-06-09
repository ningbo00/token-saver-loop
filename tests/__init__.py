import sys
from pathlib import Path

# Allow tests to import token_saver_loop from src/ without installing the package.
_SRC = Path(__file__).parent.parent / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))


