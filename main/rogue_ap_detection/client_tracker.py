"""
Client Tracker - Database Layer for Rogue AP Detection
======================================================

Manages SQLite database of connected clients.
"""

import sqlite3
import json
import csv
import threading
from datetime import datetime
from .constants import (
    DATABASE_PATH, SQL_CREATE_CLIENTS_TABLE, SQL_CREATE_LOGS_TABLE,
    SQL_CREATE_INDEX_MAC, SQL_CREATE_INDEX_TIMESTAMP, SQL_CREATE_INDEX_EVENT,
    DB_BATCH_SIZE
)
from .exceptions import DatabaseError, DatabaseConnectionError
from .utils import validate_mac_address, format_timestamp


class ClientTracker:
    """Database tracker for connected clients."""
    
    def __init__(self, db_path=None):
        """
        Initialize client tracker.
        
        Args:
            db_path (str): Database path (None = use default)
        """
        self.db_path = db_path or DATABASE_PATH
        self.connection = None
        self.lock = threading.Lock()  # FIX PR-013: Add threading lock
        self.write_buffer = []
        self._init_database()
    
    def _init_database(self):
        """Initialize database and create tables."""
        try:
            with self.lock:  # FIX PR-013: Use lock for initialization
                self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
                self.connection.row_factory = sqlite3.Row
                cursor = self.connection.cursor()
                
                # Create tables
                cursor.execute(SQL_CREATE_CLIENTS_TABLE)
                cursor.execute(SQL_CREATE_LOGS_TABLE)
                
                # Create indices
                cursor.execute(SQL_CREATE_INDEX_MAC)
                cursor.execute(SQL_CREATE_INDEX_TIMESTAMP)
                cursor.execute(SQL_CREATE_INDEX_EVENT)
                
                self.connection.commit()
        except sqlite3.Error as e:
            raise DatabaseConnectionError(self.db_path)
    
    def add_client(self, mac_address, signal_strength, manufacturer=None, device_type=None):
        """
        Add or update client in database.
        
        Args:
            mac_address (str): Client MAC address
            signal_strength (int): Signal in dBm
            manufacturer (str): Device manufacturer (optional)
            device_type (str): Device type (optional)
            
        Returns:
            dict: Client record
        """
        validate_mac_address(mac_address)
        
        try:
            with self.lock:  # FIX PR-013: Use lock for write operation
                cursor = self.connection.cursor()
                
                # Check if client exists
                cursor.execute(
                    "SELECT * FROM connected_clients WHERE mac_address = ?",
                    (mac_address,)
                )
                existing = cursor.fetchone()
                
                if existing:
                    # Update existing client
                    cursor.execute("""
                        UPDATE connected_clients 
                        SET last_seen = CURRENT_TIMESTAMP, 
                            signal_strength = ?,
                            is_active = 1
                        WHERE mac_address = ?
                    """, (signal_strength, mac_address))
                else:
                    # Insert new client
                    cursor.execute("""
                        INSERT INTO connected_clients 
                        (mac_address, signal_strength, manufacturer, device_type, is_active)
                        VALUES (?, ?, ?, ?, 1)
                    """, (mac_address, signal_strength, manufacturer, device_type))
                
                # Log event
                self._log_event('connected', mac_address, signal_strength)
                self.connection.commit()
            
            return {
                'mac_address': mac_address,
                'signal_strength': signal_strength,
                'manufacturer': manufacturer,
                'device_type': device_type,
                'status': 'added' if not existing else 'updated'
            }
        
        except sqlite3.Error as e:
            raise DatabaseError('add_client', str(e))
    
    def update_client_signal(self, mac_address, signal_strength):
        """
        Update client signal strength.
        
        Args:
            mac_address (str): Client MAC
            signal_strength (int): New signal value
        """
        validate_mac_address(mac_address)
        
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                UPDATE connected_clients 
                SET signal_strength = ?, last_seen = CURRENT_TIMESTAMP
                WHERE mac_address = ?
            """, (signal_strength, mac_address))
            
            self._log_event('signal_update', mac_address, signal_strength)
            self.connection.commit()
        
        except sqlite3.Error as e:
            raise DatabaseError('update_signal', str(e))
    
    def update_data_transmission(self, mac_address, data_bytes, frame_count=1):
        """
        Update data transmission stats.
        
        Args:
            mac_address (str): Client MAC
            data_bytes (int): Bytes transmitted
            frame_count (int): Number of frames
        """
        validate_mac_address(mac_address)
        
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                UPDATE connected_clients 
                SET data_frames = data_frames + ?,
                    last_seen = CURRENT_TIMESTAMP
                WHERE mac_address = ?
            """, (frame_count, mac_address))
            
            self._log_event('data_transmission', mac_address, data_bytes=data_bytes)
            self.connection.commit()
        
        except sqlite3.Error as e:
            raise DatabaseError('update_transmission', str(e))
    
    def mark_disconnected(self, mac_address):
        """
        Mark client as disconnected.
        
        Args:
            mac_address (str): Client MAC
        """
        validate_mac_address(mac_address)
        
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                UPDATE connected_clients 
                SET is_active = 0
                WHERE mac_address = ?
            """, (mac_address,))
            
            self._log_event('disconnected', mac_address)
            self.connection.commit()
        
        except sqlite3.Error as e:
            raise DatabaseError('mark_disconnected', str(e))
    
    def get_client(self, mac_address):
        """
        Get client record.
        
        Args:
            mac_address (str): Client MAC
            
        Returns:
            dict: Client record or None
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT * FROM connected_clients WHERE mac_address = ?",
                (mac_address,)
            )
            row = cursor.fetchone()
            return dict(row) if row else None
        
        except sqlite3.Error as e:
            raise DatabaseError('get_client', str(e))
    
    def get_all_clients(self, active_only=True):
        """
        Get all clients.
        
        Args:
            active_only (bool): Only return active clients
            
        Returns:
            list: Client records
        """
        try:
            cursor = self.connection.cursor()
            
            if active_only:
                cursor.execute(
                    "SELECT * FROM connected_clients WHERE is_active = 1 ORDER BY last_seen DESC"
                )
            else:
                cursor.execute(
                    "SELECT * FROM connected_clients ORDER BY last_seen DESC"
                )
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        
        except sqlite3.Error as e:
            raise DatabaseError('get_all_clients', str(e))
    
    def get_clients_count(self, active_only=True):
        """
        Get count of clients.
        
        Args:
            active_only (bool): Count only active
            
        Returns:
            int: Client count
        """
        try:
            cursor = self.connection.cursor()
            
            if active_only:
                cursor.execute("SELECT COUNT(*) as count FROM connected_clients WHERE is_active = 1")
            else:
                cursor.execute("SELECT COUNT(*) as count FROM connected_clients")
            
            result = cursor.fetchone()
            return result['count'] if result else 0
        
        except sqlite3.Error as e:
            raise DatabaseError('count_clients', str(e))
    
    def get_client_stats(self, mac_address):
        """
        Get detailed stats for a client.
        
        Args:
            mac_address (str): Client MAC
            
        Returns:
            dict: Statistics
        """
        validate_mac_address(mac_address)
        
        try:
            client = self.get_client(mac_address)
            if not client:
                return None
            
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT COUNT(*) as event_count, 
                       GROUP_CONCAT(event_type) as events
                FROM session_logs 
                WHERE mac_address = ?
            """, (mac_address,))
            
            events_row = cursor.fetchone()
            
            return {
                'mac_address': client['mac_address'],
                'first_seen': client['first_seen'],
                'last_seen': client['last_seen'],
                'signal_strength': client['signal_strength'],
                'data_frames': client['data_frames'],
                'manufacturer': client['manufacturer'],
                'device_type': client['device_type'],
                'total_events': events_row['event_count'] if events_row else 0,
                'is_active': bool(client['is_active'])
            }
        
        except sqlite3.Error as e:
            raise DatabaseError('get_stats', str(e))
    
    def _log_event(self, event_type, mac_address, signal_strength=None, data_bytes=None):
        """
        Log event to session_logs table.
        
        Args:
            event_type (str): Type of event
            mac_address (str): Client MAC
            signal_strength (int): Signal level (optional)
            data_bytes (int): Data bytes (optional)
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO session_logs 
                (event_type, mac_address, signal_strength, data_bytes, details)
                VALUES (?, ?, ?, ?, ?)
            """, (
                event_type,
                mac_address,
                signal_strength,
                data_bytes,
                json.dumps({'timestamp': format_timestamp()})
            ))
            self.connection.commit()
        
        except sqlite3.Error:
            pass  # Non-critical, don't raise
    
    def export_to_json(self):
        """
        Export all clients to JSON.
        
        Returns:
            str: JSON string
        """
        try:
            clients = self.get_all_clients(active_only=False)
            return json.dumps(clients, indent=2, default=str)
        
        except Exception as e:
            raise DatabaseError('json_export', str(e))
    
    def export_to_csv(self):
        """
        Export all clients to CSV.
        
        Returns:
            str: CSV string
        """
        try:
            clients = self.get_all_clients(active_only=False)
            
            if not clients:
                return "mac_address,manufacturer,device_type,first_seen,last_seen,signal_strength,data_frames\n"
            
            fieldnames = clients[0].keys()
            lines = []
            lines.append(','.join(fieldnames))
            
            for client in clients:
                values = [str(client[field]) for field in fieldnames]
                lines.append(','.join(f'"{v}"' for v in values))
            
            return '\n'.join(lines)
        
        except Exception as e:
            raise DatabaseError('csv_export', str(e))
    
    def clear_all(self):
        """Clear all data from database (use with caution)."""
        try:
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM session_logs")
            cursor.execute("DELETE FROM connected_clients")
            self.connection.commit()
        except sqlite3.Error as e:
            raise DatabaseError('clear_all', str(e))
    
    def close(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()
    
    def __del__(self):
        """Cleanup on deletion."""
        self.close()
