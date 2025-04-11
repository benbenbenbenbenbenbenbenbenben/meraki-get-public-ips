# Meraki Public IP & NAT Report Tool

This is a command-line tool that connects to the Cisco Meraki Dashboard API, retrieves appliance uplink statuses and NAT configurations, and exports them into a CSV report. The CSV includes all public/private IP mappings across MX devices in a selected organization.

---

## 📦 Features

- Lists all networks and MX devices in a selected Meraki organization
- Displays uplink interface public/private IPs
- Retrieves One-to-Many and One-to-One NAT rules
- Exports all data to a CSV file (`/reports/public_ips_report.csv`)
- Prompts user securely for API key if not configured
- CLI-based selection of organization if more than one is available
- Compatible with Python and PyInstaller executables

---

## 🚀 Getting Started

### 1. Install Dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

### 2. Run the Script

```bash
python app.py
```

---

## 🔐 API Key

You can set the Meraki API key as an environment variable to skip the prompt:

```bash
export MERAKI_DASHBOARD_API_KEY=your_api_key_here
```

Or simply enter it when prompted — input is hidden for security.

---

## 🛠️ Build Executable (Optional)

You can package this tool into a standalone `.exe` with [PyInstaller](https://pyinstaller.org/):

```bash
pip install pyinstaller
pyinstaller --onefile --name meraki-report app.py
```

This will output:

```
dist/
└── meraki-report.exe
```

When run, the `.exe` behaves the same as the script — generating reports locally.

---

## 📁 Output Location

CSV reports are always saved to:

```
<same folder as the script or .exe>/reports/public_ips_report.csv
```

---

## 📌 Requirements

- Python 3.12+
- Meraki Dashboard API with read access to organization

---
