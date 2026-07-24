# Alliance Auth - Leave of Absence (aa-loa)

[![PyPI version](https://img.shields.io/pypi/v/aa-loa)](https://pypi.org/project/aa-loa/)
[![Python versions](https://img.shields.io/pypi/pyversions/aa-loa)](https://pypi.org/project/aa-loa/)
[![Tests](https://github.com/mbroekman/aa-loa/actions/workflows/automated-checks.yml/badge.svg)](https://github.com/mbroekman/aa-loa/actions/workflows/automated-checks.yml)

A complete Leave of Absence (LOA) management module for Alliance Auth. This module allows members to declare periods of absence so that leadership is aware of their inactivity, while seamlessly integrating with other Alliance Auth features (like Discord and Activity Trackers) to prevent accidental purges.

## Features

- **Player Dashboard:** Easy-to-use form for players to submit a start date, end date, and an optional reason. Players can also view their past LOAs, and cancel/revoke an active LOA if they return early.
- **HR Dashboard:** A dedicated view for Directors/HR to see a live table of all active and upcoming LOAs in the alliance.
- **Proxy Submission:** Directors can submit an LOA on behalf of a member who might be unable to access a PC (e.g. emergencies).
- **Discord Role Sync:** Assigns members to a specific Django Group (e.g., `[On Leave]`) when their LOA becomes active. Alliance Auth will automatically sync this to Discord, TS, or Mumble.
- **Purge Protection:** Because the member is in the `[On Leave]` group, audit modules (like `aa-inactives` or `opcalendar`) can simply whitelist this group to exempt the member from activity purges.
- **Webhooks:** Automatically posts a Discord Embed to a webhook URL whenever an LOA is submitted.
- **Welcome Back Notification:** A Celery task automatically removes the member from the LOA group when the end date passes, and sends a "Welcome Back" Alliance Auth notification (which can be forwarded to Discord as a DM if `aa-discordbot` is installed).

---

## Installation

### 1. Install the Python Package
Activate your Alliance Auth virtual environment and install the package:

```bash
pip install -e /path/to/aa-loa/
```

### 2. Update Alliance Auth Settings
Open your `myauth/settings/local.py` file and add `'aa_loa'` to your `INSTALLED_APPS`:

```python
INSTALLED_APPS += [
    # ... other apps
    'aa_loa',
]
```

### 3. Run Database Migrations
Run the migrations to create the database tables:

```bash
python manage.py makemigrations aa_loa
python manage.py migrate
```

### 4. Restart Services
Restart your Alliance Auth web service and Celery workers so they pick up the new code and background tasks:

```bash
sudo systemctl restart supervisor
```
*(Or restart the specific services depending on your hosting environment).*

---

## Configuration

### 1. Setup the LOA Group
1. Go to the **Django Admin Panel** (`/admin/`).
2. Navigate to **Authentication and Authorization** -> **Groups** and create a new group (e.g., `On Leave`).
   - *Optional:* Configure this group in your Discord/TS services to map to a specific `[On Leave]` Discord Role.
3. Navigate to **Leave of Absence Configuration** -> **LOA Config**.
4. Add a new configuration row.
5. Select the `On Leave` group you just created.
6. *(Optional)* Paste a Discord Webhook URL if you want real-time notifications in an HR channel when LOAs are submitted.

### 2. Permissions
Assign the following permissions to the appropriate states or groups in Alliance Auth:

| Permission | Description |
|---|---|
| `aa_loa.basic_access` | Grants access to the LOA module for normal members. Allows them to submit and manage their own LOAs. |
| `aa_loa.manage_loa` | Grants access to the HR Dashboard. Allows users to view all LOAs and submit proxy LOAs for other members. |

### 3. Setup the Celery Periodic Task
To ensure LOA groups are automatically assigned and removed, you need to configure the daily Celery task.

1. Go to the **Django Admin Panel** (`/admin/`).
2. Navigate to **Periodic Tasks** (under `Periodic Tasks`).
3. Create a new task:
   - **Name:** `LOA Group Sync`
   - **Task (registered):** `aa_loa.tasks.sync_loa_groups`
   - **Schedule:** Select `Crontab` and set it to run daily (e.g., `0 0 * * *` for midnight).
4. Save the task. The system will now automatically activate/deactivate LOAs every day!
