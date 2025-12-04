# AWS Quiz Application Handover Document

## 1. Project Overview

This document provides a summary of the AWS Quiz Application deployment and serves as a guide for future development, bug fixes, and maintenance.

The project consists of two main components:
- **Quiz App (`quiz_app.py`):** A Streamlit application that presents a quiz to the user.
- **Aggregator App (`aggregator.py`):** A Streamlit application that allows uploading markdown files to create a JSON database of questions.

The applications are deployed on an EC2 instance and served via Nginx as a reverse proxy, with PM2 managing the application processes.

## 2. Deployment Details

### 2.1. EC2 Instance Information
- **IPv4 Address:** `98.130.128.24`
- **SSH User:** `ubuntu`
- **PEM Key File:** `lift.pem`

### 2.2. Deployed Application URLs
- **Quiz App:** [http://98.130.128.24/quiz](http://98.130.128.24/quiz)
- **Aggregator App:** [http://98.130.128.24/aggregator](http://98.130.128.24/aggregator)

### 2.3. Project Structure on EC2
The project files are located in the `~/quiz_app` directory on the EC2 instance. This includes:
- `aggregator.py`
- `quiz_app.py`
- `requirements.txt`
- `data/questions_db.json`
- `venv/` (Python virtual environment)

## 3. Deployment Steps Performed

1.  **Initial Analysis:**
    *   Reviewed `aggregator.py` and `quiz_app.py` to understand the application logic.
    *   Examined `data/questions_db.json` to understand the data structure.
    *   Created a `requirements.txt` file to define project dependencies (`streamlit`, `pandas`).

2.  **EC2 Instance Setup:**
    *   Connected to the EC2 instance via SSH using the provided IP and PEM key.
    *   Installed necessary packages: `unzip`, `python3-pip`, `python3.12-venv`.

3.  **File Transfer:**
    *   The project directory (containing the python scripts, `requirements.txt`, and the `data` directory) was zipped, transferred to the EC2 instance, and unzipped into the `~/quiz_app` directory.

4.  **Python Environment Setup:**
    *   A Python virtual environment was created at `~/quiz_app/venv`.
    *   The dependencies from `requirements.txt` were installed into this virtual environment.

5.  **Application Process Management (PM2):**
    *   The `aggregator` and `quiz_app` applications were started using PM2 to ensure they run in the background and restart automatically on failure.
    *   The applications are running on ports `8502` and `8501` respectively.
    *   **Start Commands:**
        ```bash
        pm2 start venv/bin/python3 --name quiz_app -- -m streamlit run quiz_app.py --server.port 8501 --server.baseUrlPath /quiz
        pm2 start venv/bin/python3 --name aggregator -- -m streamlit run aggregator.py --server.port 8502 --server.baseUrlPath /aggregator
        ```

6.  **Nginx Configuration:**
    *   A new Nginx configuration file was created at `/etc/nginx/sites-available/quiz_app`.
    *   This configuration sets up a reverse proxy to route requests for `/aggregator` to `localhost:8502` and `/quiz` to `localhost:8501`.
    *   The site was enabled by creating a symbolic link in `/etc/nginx/sites-enabled/`.
    *   Nginx was restarted to apply the new configuration.

## 4. Future Development and Maintenance

### 4.1. Accessing the Server
To access the server, use the following command from the project's root directory on your local machine:
```bash
ssh -i lift.pem ubuntu@98.130.128.24
```

### 4.2. Managing Application Processes with PM2
Once on the server, you can manage the applications with these PM2 commands:
- **List applications:** `pm2 list`
- **Restart an application:** `pm2 restart quiz_app` or `pm2 restart aggregator`
- **View logs:** `pm2 logs quiz_app` or `pm2 logs aggregator`
- **Stop an application:** `pm2 stop quiz_app`

### 4.3. Updating the Application
1.  Make your code changes locally.
2.  Zip the updated project files.
3.  Transfer the zip file to the EC2 instance (e.g., using `scp`).
4.  SSH into the instance, unzip the new files into the `~/quiz_app` directory, overwriting the old ones.
5.  If there are new dependencies, update `requirements.txt`, and run `pip install -r requirements.txt` within the virtual environment.
6.  Restart the relevant application using `pm2 restart <app_name>`.

### 4.4. Nginx Configuration
The Nginx configuration file is located at `/etc/nginx/sites-available/quiz_app`. If you need to make changes (e.g., change ports, add new locations), edit this file and then restart Nginx:
```bash
sudo systemctl restart nginx
```

## 5. Troubleshooting

### 5.1. Common Issues

**Issue: App not loading / 502 Bad Gateway**
*   **Check PM2 status:** Run `pm2 list` to see if the processes are online.
*   **Check Nginx status:** Run `sudo systemctl status nginx`.
*   **Check Logs:** Run `pm2 logs <app_name>` to see application logs.

**Issue: "SyntaxError: Invalid or unexpected token" in PM2 logs**
*   This usually happens if PM2 tries to run the Python script using the Node.js interpreter.
*   **Fix:** Ensure you start the application using the full path to the Python executable in the virtual environment, as shown in the "Start Commands" section.

**Issue: Streamlit "404: Not Found" or path issues**
*   Ensure the `--server.baseUrlPath` argument matches the Nginx location block (e.g., `/quiz` or `/aggregator`).

### 5.2. Verification Steps
To verify the applications are running locally on the server before checking the public URL:
```bash
curl -I http://localhost:8501/quiz/healthz
curl -I http://localhost:8502/aggregator/healthz
```