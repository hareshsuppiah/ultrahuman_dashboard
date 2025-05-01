# Ultra Human Device Dashboard

This is a Flask-based web application designed to display health metrics from the Ultra Human Device API.

## Features

*   **User Management:** Add, edit, and delete user profiles, storing their email, API key, and access code.
*   **Dashboard:** Select a user and a date to fetch and display metrics from the Ultrahuman API.
*   **Data Visualization:** Displays metrics numerically and visually using Chart.js (line charts for time-series data like HR/HRV/Temp, doughnut chart for sleep stages).
*   **API Integration:** Fetches data from the official Ultrahuman Partner API.

## Project Structure

```
ultra_human_dashboard/
├── venv/                   # Virtual environment
├── src/
│   ├── models/
│   │   └── user.py         # User database model (SQLAlchemy)
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── metrics.py      # API route for fetching Ultrahuman metrics
│   │   └── user.py         # API routes for user CRUD operations
│   ├── static/
│   │   └── index.html      # Main HTML file with CSS and JavaScript
│   └── main.py             # Main Flask application entry point
├── database.db             # SQLite database file (created on first run)
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

## Setup and Running

1.  **Prerequisites:**
    *   Python 3.x
    *   `pip` (Python package installer)

2.  **Clone the Repository (or Unzip the Project):**
    ```bash
    # If cloned from Git
    git clone <repository_url>
    cd ultra_human_dashboard

    # If using the provided zip file
    unzip ultra_human_dashboard.zip
    cd ultra_human_dashboard
    ```

3.  **Create and Activate Virtual Environment:**
    ```bash
    # Create virtual environment (recommended)
    python -m venv venv

    # Activate virtual environment
    # On Windows:
    .\venv\Scripts\activate
    # On macOS/Linux:
    source venv/bin/activate
    ```

4.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

5.  **Run the Application:**
    ```bash
    python src/main.py
    ```
    The application will start, and the database (`database.db`) will be created if it doesn't exist. By default, it runs on `http://localhost:5000` or `http://0.0.0.0:5000`.

6.  **Access the Dashboard:**
    Open your web browser and navigate to `http://localhost:5000`.

## Usage

1.  **User Management:**
    *   Go to the "User Management" section.
    *   Click "Add New User" to add a user's email, Ultrahuman API Key, and Access Code (Partner ID).
    *   Existing users can be edited or deleted using the buttons in the table.
2.  **View Dashboard:**
    *   Go to the "Dashboard" section.
    *   Select a user from the dropdown menu.
    *   Select a date using the date picker.
    *   Click "Fetch Data".
    *   The relevant metrics for the selected user and date will be displayed, including charts where applicable.

## Notes

*   The Ultrahuman API requires the user to enter the provided "Access Code" (Partner ID) into their UH app to enable data sharing.
*   API keys are stored directly in the SQLite database. Ensure appropriate security measures if deploying this application in a production environment.
*   Error handling for API calls is included, but thorough testing with valid and invalid credentials/dates is recommended.

