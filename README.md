
# DEFENX: Website Defacement Detection and Response System

## Overview

This project is a **DEFENX: Website Defacement Detection and Response System** developed using **FastAPI**. 
It detects any unauthorized modifications (defacement) on a website's content and responds by notifying administrators or taking corrective actions. 
The system is designed to provide quick detection, automated responses, and detailed reports to ensure the integrity of a website's content.

---

## Features

- **Website Content Monitoring**: Continuously monitors the website's content for any unauthorized changes.
- **FastAPI Integration**: FastAPI framework is used for building the web service and API endpoints.
- **Defacement Detection**: Detects changes in the website’s content by comparing hashes of previous content with the current state.
- **Alert System**: Sends email or system notifications to admins when defacement is detected.
- **Logging**: Keeps logs of website changes and responses for auditing.
- **Web Extension (if applicable)**: A browser extension is used to interact with the system for ease of access.

---

## Installation

### Prerequisites

Before you start, ensure you have the following installed:
- Python 3.8+
- FastAPI
- Uvicorn (for running FastAPI)
- SQLite (or any other database of choice for logging)
- SMTP service for email notifications (optional)
- Web Extension (for browser integration)

You can install the required dependencies by running the following command:

```bash
pip install -r requirements.txt
```

### Setting up the Environment

1. Clone the repository to your local machine:

```bash
git clone https://github.com/Aljin-Jayan/Defenx.git
cd Defenx
```

2. Set up your environment variables for configuration:
   - `DATABASE_URL` (e.g., for SQLite)
   - `SMTP_SERVER`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD` (if using email alerts)
   - `ADMIN_EMAIL` (if using email alerts)

---

## Usage

### Starting the FastAPI Server

Run the following command to start the server:

```bash
uvicorn main:app --reload
```

This will start the FastAPI server on `http://127.0.0.1:8000`.

You can then use the provided API endpoints to interact with the system.

### Available API Endpoints

#### 1. **Check Website Status**
   - **Endpoint**: `GET /status`
   - **Description**: Returns the current status of the monitoring system (active/inactive).
   - **Response**:
     ```json
     {
       "status": "active",
       "last_checked": "2025-05-06T14:30:00"
     }
     ```

#### 2. **Monitor Website**
   - **Endpoint**: `POST /monitor`
   - **Description**: Starts monitoring a specific website for defacement.
   - **Request Body**:
     ```json
     {
       "url": "https://example.com"
     }
     ```
   - **Response**:
     ```json
     {
       "message": "Website monitoring started successfully."
     }
     ```

#### 3. **Detect Changes**
   - **Endpoint**: `GET /detect`
   - **Description**: Checks if there are any defacement changes on a monitored website.
   - **Response**:
     ```json
     {
       "defacement_detected": true,
       "details": "Unauthorized content change detected in header section."
     }
     ```

---

## Web Extension (If Applicable)

### Installation for Browser Extension

1. Install the extension from the browser's extension store (if you have made one) or manually load the extension.
2. The extension allows you to interact with the monitoring system directly through the browser.
3. You can check the status and start monitoring a website directly through the extension.

---

## Logging and Reporting

The system logs all changes, detected defacements, and responses. Logs are stored in a local database or file system for auditing purposes. 
Use the following command to check logs:

```bash
python logs.py
```

---

## Contributing

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-name`).
3. Make changes and commit (`git commit -am 'Add new feature'`).
4. Push to the branch (`git push origin feature-name`).
5. Open a pull request.

---

## License

This project is licensed under the MIT License – see the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- **FastAPI**: For building the backend and API endpoints.
- **Uvicorn**: For running the FastAPI server.
- **SQLite**: For storing logs and monitoring data.
- **SMTP Server**: For sending email notifications.
