"""
Report generation module.
"""

from utils.logger import get_logger

logger = get_logger("report_generator")


class ReportGenerator:
    """Generates reports from PII detection results."""
    
    def __init__(self):
        """Initialize report generator."""
        logger.info("Initializing Report Generator...")
    
    def generate(self, incidents: list) -> dict:
        """
        Generate a report from detection results.
        """
        import datetime
        
        total_incidents = len(incidents)
        critical_count = sum(1 for inc in incidents if inc.get("severity") == "critical")
        high_count = sum(1 for inc in incidents if inc.get("severity") == "high")
        
        summary = {
            "total_incidents": total_incidents,
            "critical_risk_count": critical_count,
            "high_risk_count": high_count,
            "total_entities_detected": sum(len(inc.get("entities", [])) for inc in incidents)
        }
        
        report = {
            'timestamp': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'summary': summary,
            'details': incidents,
            'format': 'json'
        }
        
        logger.info(f"Report generated successfully. Found {high_count + critical_count} critical/high incidents.")
        return report
