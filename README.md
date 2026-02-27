# Strider - PII Leakage Detection System

A modular, distributed system for detecting and analyzing Personally Identifiable Information (PII) leakages across multiple sources.

## Project Structure

```
Strider/
│
├── data/                          # Raw & processed scraped data
│   ├── raw/                       # Raw scraped data
│   └── cleaned/                   # Cleaned/processed data
│
├── scraper/                       # Data collection module
│   ├── github_scraper.py          # GitHub code search
│   ├── pastebin_scraper.py        # Pastebin archive scraping
│   ├── social_scraper.py          # Social media scraping (stub)
│   └── cleaner.py                 # Text cleaning pipeline
│
├── detection/                     # PII detection module
│   ├── regex_detector.py          # Regex-based detection
│   ├── ner_detector.py            # NER-based detection
│   └── pii_combiner.py            # Multi-method combination
│
├── backend/                       # Analysis & classification
│   ├── classifier.py              # PII categorization
│   ├── risk_scoring.py            # Risk assessment
│   └── api.py                     # REST API endpoints
│
├── reports/                       # Reporting & alerting
│   ├── report_generator.py        # Report generation
│   ├── alert_system.py            # Alert management
│   └── dashboard.py               # Dashboard visualization
│
├── deployment/
│   └── Dockerfile                 # Container configuration
│
├── utils/                         # Shared utilities
│   ├── logger.py                  # Logging configuration
│   ├── rate_limiter.py            # Rate limiting
│   ├── schema.py                  # Document schema
│   └── dedup.py                   # Deduplication
│
├── app.py                         # Main application entry point
├── config.py                      # Configuration settings
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

## Team Structure

- **Member 1**: Scraper module (data collection)
- **Member 2**: Detection module (PII detection)
- **Member 3**: Backend module (classification & analysis)
- **Member 4**: Reports module (reporting & visualization)

## Quick Start

### Prerequisites
- Python 3.9+
- pip or conda

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/Strider.git
cd Strider
```

2. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment:
```bash
cp .env.example .env
# Edit .env with your API tokens and settings
```

### Running the Application

```bash
python app.py
python integration_check.py
python generate_dashboard.py
```

### Running Detection Accuracy Demo

To review the detection and classification accuracy on known data samples, run:
```bash
python demo.py
```

### Running in Docker

```bash
docker build -t strider:latest .
docker run -v $(pwd)/data:/app/data strider:latest
```

## Configuration

All configuration is managed through `config.py` and `.env` file:

- `GITHUB_TOKEN`: GitHub API token for authenticated requests
- `PASTEBIN_*`: Pastebin-specific settings
- Rate limiting and retry parameters
- Output and logging directories

## API Endpoints

The backend API provides the following endpoints:

- `GET /health` - Health check
- `POST /analyze` - Submit text for PII analysis
- `GET /reports` - Retrieve generated reports
- `POST /alerts` - Configure alert rules

## Contributing

Please follow these guidelines when contributing:

1. Work within your assigned module
2. Create feature branches: `git checkout -b feature/module-feature`
3. Commit with clear messages
4. Submit pull requests with description
5. Ensure all tests pass before PR submission

## Testing

```bash
pytest tests/ -v
```

## Logging

Logs are written to `logs/` directory. Check `utils/logger.py` for configuration.

## License

This project is licensed under the MIT License - see LICENSE file for details.

## Contact

For questions or support, please contact the development team.
