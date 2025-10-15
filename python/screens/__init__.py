"""
Screens package - All screen modules for the F1 25 Telemetry Menu System

This package contains all the functionality for the 6 main screens.
Each screen module is independent and contains all its own functions.

Usage:
    from screens import screen1
    screen1.toon_alle_data()
"""

# Import alle screen modules
from . import screen1
# from . import screen2  # Nog niet gemaakt
# from . import screen3  # Nog niet gemaakt
# from . import screen4  # Nog niet gemaakt
# from . import screen5  # Nog niet gemaakt
# from . import screen6  # Nog niet gemaakt

__all__ = [
    'screen1',
    # 'screen2',
    # 'screen3',
    # 'screen4',
    # 'screen5',
    # 'screen6',
]

__version__ = '1.0.0'