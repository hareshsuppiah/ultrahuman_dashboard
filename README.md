# Ultrahuman Dashboard

A Python web dashboard for visualising and analysing Ultrahuman Ring data locally. View sleep patterns, heart rate, HRV, glucose levels, skin temperature, and daily activity through an interactive web interface.

## How to Cite

If you use this dashboard in your research, please cite it:

### APA Style
```
Suppiah, H., & Driller, M. (2025). Ultrahuman Ring Health Monitoring Dashboard and Analysis Tool (Version 1.0.0) [Computer software]. https://doi.org/10.5281/zenodo.16777849
```

### BibTeX
```bibtex
@software{suppiah_ultrahuman_2025,
  author = {Suppiah, Haresh and Driller, Matthew},
  title = {Ultrahuman Ring Health Monitoring Dashboard and Analysis Tool},
  url = {https://github.com/hareshsuppiah/ultrahuman_dashboard},
  doi = {10.5281/zenodo.16777849},
  version = {1.0.0},
  year = {2025}
}
```

This repository includes a `CITATION.cff` file for automatic citation generation on GitHub.

---

## Dashboard Preview

![Ultrahuman Dashboard Screenshot](assets/images/dashboard-screenshot.png)

---

## Features

- Sleep stage analysis with hypnogram visualisation
- Derived sleep metrics: SOL, WASO, wake episodes (from raw API segments)
- Circular mean algorithm for bedtime/wake time averaging across midnight
- Heart rate and HRV tracking with interactive charts
- Glucose, skin temperature, and daily steps monitoring
- Dual CSV export formats (long and wide)
- Multi-user bulk export across date ranges
- Multi-day statistical summaries (median, SD, range, trend)
- Sleep architecture heatmap for multi-night comparison
- Dark mode
- Date range presets (7, 14, 30 days)
- All data processing occurs locally

---

## Installation

### Option A: pip install

```bash
pip install ultrahuman-dashboard
ultrahuman-dashboard
```

Then open http://localhost:8000 in your browser.

### Option B: From source

```bash
git clone https://github.com/hareshsuppiah/ultrahuman_dashboard.git
cd ultrahuman_dashboard
python3 -m venv venv
source venv/bin/activate    # Mac/Linux
venv\Scripts\activate       # Windows
pip install -r requirements.txt
python src/main.py
```

Then open http://localhost:8000 in your browser.

### Option C: Docker

```bash
docker compose up
```

### Requirements

- Python 3.8 or later
- Ultrahuman Partnership API credentials (contact Ultrahuman Support to request access)

---

## Database Setup

The database (`database.db`) is created automatically on first run. No manual setup is required.

The SQLite database stores user credentials locally:

| Field | Description |
|-------|-------------|
| `email` | Your Ultrahuman account email |
| `api_key` | Your Ultrahuman API key |
| `access_code` | Your Ultrahuman access code |

To reset the database, delete `database.db` and restart the application.

---

## Usage

The dashboard has three tabs:

### User Management
Add, edit, or remove users with their Ultrahuman API credentials.

### Single User Dashboard
1. Select a user from the dropdown
2. Choose Single Day or Date Range mode
3. Select dates (or use the preset buttons: Last 7, 14, or 30 days)
4. Click Fetch Data

The dashboard displays metric cards for sleep, heart rate, HRV, temperature, steps, and glucose. In single-day view, a sleep hypnogram shows stage progression throughout the night. In date range view, statistical summaries and a sleep architecture heatmap are displayed.

### Multi-User Export
Select multiple users, choose a date range, and export combined CSV data.

### CSV Export Formats

Two formats are available for both single-user and multi-user exports:

**Long format**: One row per metric per date. Suited to tidy data workflows in R or Python.

**Wide format**: One row per date with all metrics as columns. Suited to spreadsheet-based analysis in Excel or SPSS. Includes separate bedtime/wake date columns and Unix timestamps.

---

## Technical Notes for Researchers

### Date References

- The `Date` column represents the wake-up date (end of sleep session)
- Bedtime typically occurs on the previous calendar day
- Use `Bedtime_Date` and `Wake_Date` columns for precise date analysis
- `Steps_Daily` represents the full calendar day count (midnight to midnight)

### Total Sleep: API vs Derived

| Column | Source | Calculation |
|--------|--------|-------------|
| `Total_Sleep_API_*` | Ultrahuman quick_metrics | Pre-calculated by Ultrahuman |
| `Total_Sleep_Derived_*` | sleep_graph.data segments | Deep + Light + REM minutes |

These values may differ by a few minutes due to internal Ultrahuman calculations. Both are provided for researcher discretion.

### Sleep Metric Definitions

| Metric | Definition |
|--------|------------|
| `Time_In_Bed` | Total duration from bedtime to wake time |
| `Total_Sleep` | Time spent in sleep stages (Deep + Light + REM) |
| `Sleep_Efficiency` | (Total Sleep / Time In Bed) x 100 |
| `SOL` (Sleep Onset Latency) | Time awake at start of sleep session |
| `WASO` (Wake After Sleep Onset) | Total wake time after first falling asleep |
| `Wake_Episodes` | Number of awakenings after sleep onset |

### Data Validation

Expected relationships:
- `Deep_Sleep + Light_Sleep + REM_Sleep + Awake = Time_In_Bed`
- `SOL + WASO = Awake`
- `Total_Sleep_Derived = Deep_Sleep + Light_Sleep + REM_Sleep`

---

## Project Structure

```
ultrahuman_dashboard/
├── src/
│   ├── main.py               # Flask application entry point
│   ├── algorithms.py          # Circular mean, derived sleep metrics
│   ├── models/
│   │   └── user.py            # SQLAlchemy User model
│   ├── routes/
│   │   ├── user.py            # User CRUD endpoints
│   │   └── metrics.py         # Ultrahuman API integration
│   └── static/
│       └── index.html         # Single-page application frontend
├── tests/
│   ├── test_algorithms.py     # Algorithm tests (circular mean, sleep metrics)
│   └── test_app.py            # Flask route and model tests
├── paper/
│   ├── paper.md               # JOSS manuscript
│   └── paper.bib              # References
├── docs/
│   └── roadmap.md             # Planned features
├── .github/workflows/
│   ├── tests.yml              # CI: pytest on Python 3.10-3.12
│   └── draft-pdf.yml          # JOSS paper PDF compilation
├── CITATION.cff               # Citation metadata
├── CONTRIBUTING.md             # Contribution guidelines
├── Dockerfile                  # Container deployment
├── docker-compose.yml          # Docker Compose configuration
├── pyproject.toml              # Package configuration
├── requirements.txt            # Python dependencies
└── LICENSE                     # MIT licence
```

---

## Running Tests

```bash
source venv/bin/activate
pip install pytest
python -m pytest tests/ -v
```

58 tests covering the circular mean algorithm, derived sleep metrics, Flask routes, user model, and API error handling.

---

## Troubleshooting

**Python not found**: Ensure Python 3.8+ is installed. On Mac, try `python3` instead of `python`.

**No module named flask**: Activate the virtual environment first (`source venv/bin/activate`).

**Cannot access localhost:8000**: Check the terminal for errors. Ensure no other application is using port 8000.

**Database issues**: Delete `database.db` and restart the application.

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on reporting bugs, suggesting features, and submitting changes.

---

## Licence

MIT. See [LICENSE](LICENSE) for details.
