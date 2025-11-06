"""
F1 25 Telemetry System - Status Bar Component
Status indicator component voor UDP en systeem status
"""

from datetime import datetime

class StatusBar:
    """Status bar component"""
    
    @staticmethod
    def render_udp_status(udp_stats: dict, width: int = 80):
        """
        Render UDP listener status
        
        Args:
            udp_stats: UDP statistieken dict
            width: Breedte van status bar
        """
        running = udp_stats.get('running', False)
        packets_received = udp_stats.get('packets_received', 0)
        packets_processed = udp_stats.get('packets_processed', 0)
        packets_errors = udp_stats.get('packets_errors', 0)
        
        status_text = "ACTIEF" if running else "GESTOPT"
        status_symbol = "●" if running else "○"
        
        print("\n" + "─" * width)
        print(f"  UDP Status: {status_symbol} {status_text}")
        print(f"  Packets: {packets_received} ontvangen | {packets_processed} verwerkt | {packets_errors} errors")
        print("─" * width)
    
    @staticmethod
    def render_connection_status(connected: bool, last_packet_time: float = 0):
        """
        Render verbindingsstatus
        
        Args:
            connected: Of er verbinding is
            last_packet_time: Tijdstip laatste packet
        """
        if connected:
            status = "✓ Verbonden"
            if last_packet_time > 0:
                status += f" (laatste packet: {last_packet_time:.1f}s)"
        else:
            status = "✗ Geen verbinding"
        
        print(f"  {status}")
    
    @staticmethod
    def render_session_status(session_active: bool, session_time: float = 0):
        """
        Render sessie status
        
        Args:
            session_active: Of sessie actief is
            session_time: Huidige sessie tijd
        """
        if session_active:
            minutes = int(session_time // 60)
            seconds = int(session_time % 60)
            print(f"  Sessie: ACTIEF ({minutes:02d}:{seconds:02d})")
        else:
            print(f"  Sessie: Geen actieve sessie")
    
    @staticmethod
    def render_timestamp():
        """Render huidige timestamp"""
        now = datetime.now().strftime("%H:%M:%S")
        print(f"  Tijd: {now}")
    
    @staticmethod
    def render_compact_status(udp_running: bool, packets: int, session_active: bool):
        """
        Render compacte status op één regel
        
        Args:
            udp_running: UDP listener status
            packets: Aantal packets ontvangen
            session_active: Sessie status
        """
        udp_symbol = "●" if udp_running else "○"
        session_symbol = "●" if session_active else "○"
        
        print(f"  UDP {udp_symbol} | Packets: {packets} | Sessie {session_symbol}")
    
    @staticmethod
    def render_info_message(message: str, message_type: str = "info"):
        """
        Render info/warning/error bericht
        
        Args:
            message: Bericht tekst
            message_type: Type bericht (info/warning/error)
        """
        symbols = {
            'info': 'ℹ',
            'warning': '⚠',
            'error': '✗',
            'success': '✓'
        }
        
        symbol = symbols.get(message_type, 'ℹ')
        print(f"\n  {symbol} {message}")
    
    @staticmethod
    def render_loading_bar(progress: float, width: int = 40):
        """
        Render loading/progress bar
        
        Args:
            progress: Progress (0.0 - 1.0)
            width: Breedte van bar
        """
        filled = int(progress * width)
        bar = "█" * filled + "░" * (width - filled)
        percentage = int(progress * 100)
        
        print(f"  [{bar}] {percentage}%")
    
    @staticmethod
    def render_metric(label: str, value: str, unit: str = ""):
        """
        Render metric (label: value unit)
        
        Args:
            label: Label tekst
            value: Waarde
            unit: Eenheid
        """
        unit_str = f" {unit}" if unit else ""
        print(f"  {label:<20} {value}{unit_str}")