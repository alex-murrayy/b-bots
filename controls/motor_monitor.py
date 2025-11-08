#!/usr/bin/env python3
"""
Motor Monitor and Benchmarking System
Tracks command execution, timing, and motor performance metrics
"""

import time
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from collections import deque
from dataclasses import dataclass, asdict
from enum import Enum


class CommandType(Enum):
    """Type of command"""
    FORWARD = "forward"
    BACKWARD = "backward"
    LEFT = "left"
    RIGHT = "right"
    STOP = "stop"
    CENTER = "center"
    ALL_OFF = "all_off"
    UNKNOWN = "unknown"


@dataclass
class CommandEvent:
    """Represents a single command event"""
    timestamp: float
    command: str
    command_type: str
    response_time: Optional[float] = None
    success: bool = True
    error: Optional[str] = None


@dataclass
class SessionStats:
    """Statistics for a control session"""
    session_start: float
    session_end: Optional[float] = None
    total_commands: int = 0
    commands_by_type: Dict[str, int] = None
    total_forward_time: float = 0.0
    total_backward_time: float = 0.0
    last_forward_start: Optional[float] = None
    last_backward_start: Optional[float] = None
    total_left_turns: int = 0
    total_right_turns: int = 0
    average_response_time: float = 0.0
    errors: int = 0
    
    def __post_init__(self):
        if self.commands_by_type is None:
            self.commands_by_type = {cmd.value: 0 for cmd in CommandType}


class MotorMonitor:
    """Monitor and benchmark motor control commands"""
    
    def __init__(self, max_history: int = 1000):
        """
        Initialize motor monitor
        
        Args:
            max_history: Maximum number of events to keep in history
        """
        self.max_history = max_history
        self.events: deque = deque(maxlen=max_history)
        self.session_stats = SessionStats(session_start=time.time())
        self.current_drive_state: Optional[str] = None
        self.drive_start_time: Optional[float] = None
        
    def log_command(self, command: str, response_time: Optional[float] = None, 
                   success: bool = True, error: Optional[str] = None):
        """
        Log a command event
        
        Args:
            command: Command string (w, s, a, d, etc.)
            response_time: Time taken to execute (seconds)
            success: Whether command succeeded
            error: Error message if failed
        """
        cmd_type = self._classify_command(command)
        
        event = CommandEvent(
            timestamp=time.time(),
            command=command,
            command_type=cmd_type.value,
            response_time=response_time,
            success=success,
            error=error
        )
        
        self.events.append(event)
        self._update_stats(event)
        
    def _classify_command(self, command: str) -> CommandType:
        """Classify command type"""
        cmd = command.lower().strip()
        if cmd == 'w':
            return CommandType.FORWARD
        elif cmd == 's':
            return CommandType.BACKWARD
        elif cmd == 'a':
            return CommandType.LEFT
        elif cmd == 'd':
            return CommandType.RIGHT
        elif cmd in [' ', 'space', 'stop']:
            return CommandType.STOP
        elif cmd == 'c' or cmd == 'center':
            return CommandType.CENTER
        elif cmd == 'x' or cmd == 'off':
            return CommandType.ALL_OFF
        else:
            return CommandType.UNKNOWN
    
    def _update_stats(self, event: CommandEvent):
        """Update session statistics"""
        self.session_stats.total_commands += 1
        self.session_stats.commands_by_type[event.command_type] += 1
        
        # Update drive time tracking
        current_time = event.timestamp
        
        if event.command_type == CommandType.FORWARD.value:
            # Stop previous drive state if any
            if self.current_drive_state == 'backward' and self.drive_start_time:
                self.session_stats.total_backward_time += current_time - self.drive_start_time
            elif self.current_drive_state == 'forward' and self.drive_start_time:
                # Update forward time
                self.session_stats.total_forward_time += current_time - self.drive_start_time
            
            self.current_drive_state = 'forward'
            self.drive_start_time = current_time
            self.session_stats.last_forward_start = current_time
            
        elif event.command_type == CommandType.BACKWARD.value:
            # Stop previous drive state if any
            if self.current_drive_state == 'forward' and self.drive_start_time:
                self.session_stats.total_forward_time += current_time - self.drive_start_time
            elif self.current_drive_state == 'backward' and self.drive_start_time:
                self.session_stats.total_backward_time += current_time - self.drive_start_time
            
            self.current_drive_state = 'backward'
            self.drive_start_time = current_time
            self.session_stats.last_backward_start = current_time
            
        elif event.command_type == CommandType.STOP.value:
            # Stop current drive state
            if self.current_drive_state == 'forward' and self.drive_start_time:
                self.session_stats.total_forward_time += current_time - self.drive_start_time
            elif self.current_drive_state == 'backward' and self.drive_start_time:
                self.session_stats.total_backward_time += current_time - self.drive_start_time
            
            self.current_drive_state = None
            self.drive_start_time = None
            
        elif event.command_type == CommandType.LEFT.value:
            self.session_stats.total_left_turns += 1
            
        elif event.command_type == CommandType.RIGHT.value:
            self.session_stats.total_right_turns += 1
        
        # Update response time average
        if event.response_time is not None:
            total_response = self.session_stats.average_response_time * (self.session_stats.total_commands - 1)
            total_response += event.response_time
            self.session_stats.average_response_time = total_response / self.session_stats.total_commands
        
        # Update error count
        if not event.success:
            self.session_stats.errors += 1
    
    def get_realtime_stats(self) -> Dict:
        """Get current real-time statistics"""
        current_time = time.time()
        session_duration = current_time - self.session_stats.session_start
        
        # Calculate current drive time if driving
        current_drive_time = 0.0
        if self.current_drive_state and self.drive_start_time:
            current_drive_time = current_time - self.drive_start_time
        
        stats = {
            'session_duration': session_duration,
            'total_commands': self.session_stats.total_commands,
            'commands_per_second': self.session_stats.total_commands / session_duration if session_duration > 0 else 0,
            'commands_by_type': dict(self.session_stats.commands_by_type),
            'total_forward_time': self.session_stats.total_forward_time + (current_drive_time if self.current_drive_state == 'forward' else 0),
            'total_backward_time': self.session_stats.total_backward_time + (current_drive_time if self.current_drive_state == 'backward' else 0),
            'total_left_turns': self.session_stats.total_left_turns,
            'total_right_turns': self.session_stats.total_right_turns,
            'average_response_time': self.session_stats.average_response_time,
            'errors': self.session_stats.errors,
            'current_drive_state': self.current_drive_state,
            'current_drive_duration': current_drive_time if self.current_drive_state else 0,
        }
        
        return stats
    
    def get_summary(self) -> str:
        """Get a formatted summary of the session"""
        stats = self.get_realtime_stats()
        session_duration = stats['session_duration']
        
        summary = f"""
==============================================================
              Motor Control Session Summary                    
==============================================================
  Session Duration:      {session_duration:>8.1f} seconds            
  Total Commands:        {stats['total_commands']:>8}                  
  Commands/Second:       {stats['commands_per_second']:>8.2f}              
  Average Response:      {stats['average_response_time']*1000:>8.1f} ms            
  Errors:                {stats['errors']:>8}                  
==============================================================
  Commands by Type:                                           
    Forward:            {stats['commands_by_type'].get('forward', 0):>8}                  
    Backward:           {stats['commands_by_type'].get('backward', 0):>8}                  
    Left Turns:         {stats['total_left_turns']:>8}                  
    Right Turns:        {stats['total_right_turns']:>8}                  
    Stop:               {stats['commands_by_type'].get('stop', 0):>8}                  
    Center:             {stats['commands_by_type'].get('center', 0):>8}                  
==============================================================
  Drive Time:                                                 
    Forward:            {stats['total_forward_time']:>8.1f} seconds        
    Backward:           {stats['total_backward_time']:>8.1f} seconds        
    Current State:      {stats['current_drive_state'] or 'stopped':>8}            
==============================================================
"""
        return summary
    
    def end_session(self):
        """End the session and finalize statistics"""
        current_time = time.time()
        self.session_stats.session_end = current_time
        
        # Finalize drive time if still driving
        if self.current_drive_state and self.drive_start_time:
            drive_time = current_time - self.drive_start_time
            if self.current_drive_state == 'forward':
                self.session_stats.total_forward_time += drive_time
            elif self.current_drive_state == 'backward':
                self.session_stats.total_backward_time += drive_time
        
        self.current_drive_state = None
        self.drive_start_time = None
    
    def save_session(self, filename: Optional[str] = None) -> str:
        """
        Save session data to JSON file
        
        Args:
            filename: Output filename (auto-generated if None)
        
        Returns:
            Path to saved file
        """
        self.end_session()
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"motor_session_{timestamp}.json"
        
        data = {
            'session_stats': asdict(self.session_stats),
            'events': [asdict(event) for event in self.events]
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        return filename
    
    def print_realtime(self, interval: float = 1.0):
        """
        Print real-time statistics at regular intervals
        
        Args:
            interval: Update interval in seconds
        """
        import sys
        try:
            while True:
                stats = self.get_realtime_stats()
                sys.stdout.write('\r' + ' ' * 80 + '\r')  # Clear line
                sys.stdout.write(f"Commands: {stats['total_commands']} | "
                               f"Forward: {stats['total_forward_time']:.1f}s | "
                               f"Backward: {stats['total_backward_time']:.1f}s | "
                               f"L/R: {stats['total_left_turns']}/{stats['total_right_turns']} | "
                               f"State: {stats['current_drive_state'] or 'stopped'}")
                sys.stdout.flush()
                time.sleep(interval)
        except KeyboardInterrupt:
            sys.stdout.write('\n')
            sys.stdout.flush()


# Example usage
if __name__ == '__main__':
    monitor = MotorMonitor()
    
    # Simulate some commands
    start = time.time()
    monitor.log_command('w', response_time=0.05)
    time.sleep(1.0)
    monitor.log_command(' ', response_time=0.02)
    monitor.log_command('a', response_time=0.03)
    monitor.log_command('d', response_time=0.03)
    monitor.log_command('w', response_time=0.05)
    time.sleep(0.5)
    monitor.log_command(' ', response_time=0.02)
    
    print(monitor.get_summary())
    monitor.save_session("test_session.json")

