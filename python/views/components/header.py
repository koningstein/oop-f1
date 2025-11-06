"""
F1 25 Telemetry System - Header Component
Herbruikbare header component voor schermen
"""

from utils import get_track_name, get_session_type_name

class Header:
    """Header component voor schermen"""
    
    @staticmethod
    def render_title(title: str, width: int = 80):
        """
        Render scherm titel
        
        Args:
            title: Titel tekst
            width: Breedte van header
        """
        print("=" * width)
        padding = (width - len(title)) // 2
        print(" " * padding + title)
        print("=" * width)
    
    @staticmethod
    def render_section_header(title: str, width: int = 80):
        """
        Render sectie header
        
        Args:
            title: Sectie titel
            width: Breedte van header
        """
        print(f"\n[ {title} ]")
        print("-" * width)
    
    @staticmethod
    def render_session_info(session: dict, compact: bool = False):
        """
        Render sessie informatie header
        
        Args:
            session: Session dict uit database
            compact: Compacte weergave
        """
        if not session:
            return
        
        track = get_track_name(session.get('track_id', 0))
        session_type = get_session_type_name(session.get('session_type', 0))
        
        if compact:
            print(f"  {track} - {session_type}")
        else:
            print(f"\n  Circuit: {track}")
            print(f"  Sessie: {session_type}")
    
    @staticmethod
    def render_divider(width: int = 80, char: str = "-"):
        """
        Render scheidingslijn
        
        Args:
            width: Breedte
            char: Karakter voor lijn
        """
        print(char * width)
    
    @staticmethod
    def render_box_header(title: str, width: int = 80):
        """
        Render box-style header
        
        Args:
            title: Titel
            width: Breedte
        """
        print("\n" + "┌" + "─" * (width - 2) + "┐")
        padding = (width - len(title) - 2) // 2
        print("│" + " " * padding + title + " " * (width - padding - len(title) - 2) + "│")
        print("└" + "─" * (width - 2) + "┘")