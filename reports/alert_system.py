"""
Alert system module for notifying on critical findings.
"""

from utils.logger import get_logger

logger = get_logger("alert_system")


class AlertSystem:
    """Manages alerts for critical PII findings."""
    
    def __init__(self):
        """Initialize alert system."""
        logger.info("Initializing Alert System...")
    
    def send_alert(self, severity: str, message: str) -> bool:
        """
        Send an alert. Logs to log file if severity is high or critical.
        """
        import os
        from pathlib import Path
        
        logger.warning(f"Alert [{severity.upper()}]: {message}")
        
        # Only persist high or critical severity alerts
        if severity.lower() in ["high", "critical"]:
            try:
                alert_dir = Path("logs")
                alert_dir.mkdir(exist_ok=True)
                alert_file = alert_dir / "alerts.log"
                
                with open(alert_file, "a", encoding="utf-8") as f:
                    import datetime
                    ts = datetime.datetime.now().isoformat()
                    f.write(f"[{ts}] [{severity.upper()}] {message}\n")
            except Exception as e:
                logger.error(f"Failed to write alert to log file: {e}")
                return False
                
        return True
        return True
