"""
F1 25 Telemetry System - Data Table Component
Herbruikbare tabel component voor data weergave
"""

from typing import List, Dict, Any

class DataTable:
    """Data table component voor gestructureerde weergave"""
    
    @staticmethod
    def render_table(headers: List[str], rows: List[List[Any]], 
                    column_widths: List[int] = None, 
                    alignment: List[str] = None):
        """
        Render data tabel
        
        Args:
            headers: Lijst met header labels
            rows: Lijst met rijen (elke rij is lijst met waarden)
            column_widths: Optionele breedte per kolom
            alignment: Optionele alignment per kolom ('<', '>', '^')
        """
        if not headers or not rows:
            print("  Geen data beschikbaar")
            return
        
        # Bepaal kolom breedtes
        if column_widths is None:
            column_widths = [len(str(h)) for h in headers]
            for row in rows:
                for i, cell in enumerate(row):
                    if i < len(column_widths):
                        column_widths[i] = max(column_widths[i], len(str(cell)))
        
        # Default alignment is links
        if alignment is None:
            alignment = ['<'] * len(headers)
        
        # Print header
        header_line = "  "
        for i, (header, width, align) in enumerate(zip(headers, column_widths, alignment)):
            header_line += f"{header:{align}{width}}  "
        print(header_line)
        
        # Print separator
        total_width = sum(column_widths) + len(headers) * 2
        print("  " + "-" * total_width)
        
        # Print rows
        for row in rows:
            row_line = "  "
            for i, (cell, width, align) in enumerate(zip(row, column_widths, alignment)):
                row_line += f"{str(cell):{align}{width}}  "
            print(row_line)
    
    @staticmethod
    def render_key_value_table(data: Dict[str, Any], label_width: int = 20):
        """
        Render key-value tabel
        
        Args:
            data: Dictionary met key-value pairs
            label_width: Breedte van label kolom
        """
        if not data:
            print("  Geen data beschikbaar")
            return
        
        for key, value in data.items():
            print(f"  {key:<{label_width}} {value}")
    
    @staticmethod
    def render_comparison_table(labels: List[str], values1: List[Any], 
                               values2: List[Any], headers: List[str]):
        """
        Render vergelijkings tabel (twee kolommen met waarden)
        
        Args:
            labels: Rij labels
            values1: Waarden voor eerste kolom
            values2: Waarden voor tweede kolom
            headers: Headers voor de twee waarde kolommen
        """
        if len(values1) != len(labels) or len(values2) != len(labels):
            print("  Error: Ongelijke aantal waarden")
            return
        
        # Header
        print(f"  {'Metric':<20} {headers[0]:<15} {headers[1]:<15} {'Delta':<10}")
        print("  " + "-" * 60)
        
        # Rows
        for label, val1, val2 in zip(labels, values1, values2):
            # Bereken delta indien numeriek
            try:
                delta = float(val2) - float(val1)
                delta_str = f"+{delta:.3f}" if delta >= 0 else f"{delta:.3f}"
            except (ValueError, TypeError):
                delta_str = "-"
            
            print(f"  {label:<20} {str(val1):<15} {str(val2):<15} {delta_str:<10}")
    
    @staticmethod
    def render_leaderboard(entries: List[Dict[str, Any]], 
                          columns: List[str],
                          highlight_index: int = None):
        """
        Render leaderboard tabel
        
        Args:
            entries: List met entry dicts
            columns: Kolommen om te tonen
            highlight_index: Index van te highlighten entry
        """
        if not entries:
            print("  Geen data beschikbaar")
            return
        
        # Header
        header = f"  {'Pos':<5}"
        for col in columns:
            header += f"{col:<20}"
        print(header)
        print("  " + "-" * 80)
        
        # Entries
        for idx, entry in enumerate(entries):
            position = idx + 1
            prefix = "► " if idx == highlight_index else "  "
            
            row = f"{prefix}{position:<5}"
            for col in columns:
                value = entry.get(col, '-')
                row += f"{str(value):<20}"
            print(row)
    
    @staticmethod
    def render_grid(data: List[List[str]], cell_width: int = 15):
        """
        Render grid layout (bijv. voor telemetrie data)
        
        Args:
            data: 2D lijst met cell waarden
            cell_width: Breedte per cell
        """
        for row in data:
            row_str = "  "
            for cell in row:
                row_str += f"{cell:<{cell_width}}"
            print(row_str)
    
    @staticmethod
    def render_vertical_bar_chart(labels: List[str], values: List[float], 
                                  max_width: int = 40):
        """
        Render verticale bar chart
        
        Args:
            labels: Labels voor elke bar
            values: Waarden (0.0 - 1.0)
            max_width: Maximum breedte van bar
        """
        for label, value in zip(labels, values):
            # Clamp value tussen 0 en 1
            value = max(0.0, min(1.0, value))
            
            bar_length = int(value * max_width)
            bar = "█" * bar_length + "░" * (max_width - bar_length)
            percentage = int(value * 100)
            
            print(f"  {label:<15} [{bar}] {percentage:3d}%")
    
    @staticmethod
    def render_split_screen(left_data: str, right_data: str, 
                          split_pos: int = 40, total_width: int = 80):
        """
        Render split screen layout
        
        Args:
            left_data: Data voor linker helft
            right_data: Data voor rechter helft
            split_pos: Split positie
            total_width: Totale breedte
        """
        left_lines = left_data.split('\n')
        right_lines = right_data.split('\n')
        
        max_lines = max(len(left_lines), len(right_lines))
        
        for i in range(max_lines):
            left_line = left_lines[i] if i < len(left_lines) else ""
            right_line = right_lines[i] if i < len(right_lines) else ""
            
            # Pad left line
            left_line = left_line[:split_pos].ljust(split_pos)
            
            print(f"{left_line} │ {right_line}")