import sys
from pathlib import Path

path = str((Path(__file__).parent / ".." / "src").resolve())
if path not in sys.path:
    sys.path.append(path)
del path
