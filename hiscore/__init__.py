__version__ = '1.6.0'

from .engine import create, HiScoreEngine, Point
from .errors import MonotoneError, MonotoneBoundsError, ScoreCreationError