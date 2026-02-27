"""
Dashboard module for visualizing results.
"""

from typing import List, Dict, Any

from utils.logger import get_logger

logger = get_logger("dashboard")


class Dashboard:
    """Manages dashboard for visualizing PII detection results."""

    def __init__(self) -> None:
        """Initialize dashboard."""
        logger.info("Initializing Dashboard...")

    def render(self, incidents: List[Dict[str, Any]]) -> str:
        """
        Render a minimal HTML dashboard for a list of incidents.

        The dashboard expects each incident to contain:
        - incident_id
        - risk_score
        - severity
        - entities (list)
        """
        rows = []
        for inc in incidents:
            rows.append(
                f"<tr>"
                f"<td>{inc.get('incident_id')}</td>"
                f"<td>{inc.get('severity')}</td>"
                f"<td>{inc.get('risk_score')}</td>"
                f"<td>{len(inc.get('entities') or [])}</td>"
                f"</tr>"
            )

        table_body = "\n".join(rows) if rows else "<tr><td colspan='4'>No incidents</td></tr>"

        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>PII Leakage Dashboard</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 2rem; }}
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{ border: 1px solid #ccc; padding: 0.5rem; text-align: left; }}
    th {{ background: #f5f5f5; }}
  </style>
  <script>
    // Simple JS stub; avoids runtime errors in console.
    console.log("Dashboard loaded");
  </script>
</head>
<body>
  <h1>PII Leakage Incidents</h1>
  <table>
    <thead>
      <tr>
        <th>Incident ID</th>
        <th>Severity</th>
        <th>Risk Score</th>
        <th>Entities</th>
      </tr>
    </thead>
    <tbody>
      {table_body}
    </tbody>
  </table>
</body>
</html>
"""
        logger.info("Dashboard rendered")
        return html
