# OrangeHRM Automation Framework

A clean, maintainable test automation framework for [OrangeHRM Demo](https://opensource-demo.orangehrmlive.com/) built with **Python + Playwright + Pytest + Requests**.

---

## Project Structure

```
OrangeHRM-Automation-Abdel/
├── .github/workflows/ci.yml   # GitHub Actions CI
├── api/
│   └── client.py              # Reusable HTTP client (Requests)
├── config/
│   └── settings.py            # Base URL, credentials, browser config
├── pages/
│   ├── base_page.py           # Shared Playwright helpers
│   ├── login_page.py          # Login page object
│   └── admin_page.py          # Admin user management page object
├── tests/
│   ├── conftest.py            # Pytest fixtures (browser, login, API client)
│   ├── ui/
│   │   └── test_admin_users.py   # End-to-end UI test
│   └── api/
│       └── test_candidates.py    # API tests (candidates)
├── utils/
│   └── helpers.py             # Utilities: username generator, log config
├── pytest.ini
├── requirements.txt
└── README.md
```

---

## Setup

### Prerequisites

- Python 3.10+

### Install dependencies

```bash
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
```

---

## Running Tests

### All tests
```bash
pytest
```

### UI tests only
```bash
pytest -m ui
```

### API tests only
```bash
pytest -m api
```

### Run headed (visible browser)
```bash
pytest -m ui --headed
```

### Slow motion (useful for debugging)
```bash
pytest -m ui --headed --slowmo 500
```

---

## Configuration

All settings live in `config/settings.py`:

| Key | Default | Description |
|-----|---------|-------------|
| `BASE_URL` | `https://opensource-demo.orangehrmlive.com` | Target application URL |
| `CREDENTIALS` | `Admin / admin123` | Login credentials |
| `HEADLESS` | `True` | Run browser without UI |
| `DEFAULT_PASSWORD` | `Admin1234!` | Password used for created test users |

---

## Design Decisions

- **Page Object Model (POM)** — each page has its own class; tests only call high-level methods
- **Dynamic test data** — usernames are generated at runtime to avoid conflicts
- **No hard sleeps** — all waits use Playwright's built-in network/selector waits
- **Session-based API auth** — the API client logs in once and reuses the cookie session
- **pytest fixtures** — browser setup, login, and API client are injected via fixtures

---

## Test Coverage

### UI Test — Admin User Management (`tests/ui/test_admin_users.py`)

End-to-end flow covering all 13 steps from the QA assessment:

| Step | Action |
|------|--------|
| 1–4 | Navigate to OrangeHRM and log in as Admin |
| 5 | Click the Admin tab → User Management → Users |
| 6 | Capture current record count |
| 7–9 | Click **Add**, fill in user details with a dynamic username, click **Save** |
| 10 | Assert record count increased by 1 |
| 11 | Search for the new user by username, assert exactly 1 result |
| 12 | Delete the user from search results |
| 13 | Reset search, assert record count returned to original |

### Bonus — API Candidate Management (`tests/api/test_candidates.py`)

Exercises the OrangeHRM REST API directly using `requests`, bypassing the UI entirely.

**Why this matters:** REST API tests are faster (no browser overhead), run in parallel with UI suites in CI, and catch backend regressions that the UI layer might mask.

**Authentication challenge solved:** OrangeHRM is a Vue.js SPA — the login form and CSRF token are rendered by JavaScript, so a plain `requests.Session` cannot authenticate directly. The `OrangeHRMApiClient` solves this by driving a headless Playwright browser to complete the login flow, then extracting the resulting session cookie and injecting it into the `requests.Session`. From that point all API calls are fully authenticated with no manual token handling.

**Tests:**

| Test | What it covers |
|------|---------------|
| `test_add_and_delete_candidate` | POST → assert `id` / `firstName` / `lastName` / `email` → DELETE → verify removed from list |
| `test_add_candidate_returns_correct_structure` | POST → validate full response schema → cleanup |

**API endpoints used:**

```
POST   /web/index.php/api/v2/recruitment/candidates   — create candidate
DELETE /web/index.php/api/v2/recruitment/candidates   — body: {"ids": [<id>]}
GET    /web/index.php/api/v2/recruitment/candidates   — list candidates
```

---

## CI/CD

GitHub Actions runs on every push/PR to `main`:
1. Installs Python 3.13 and dependencies
2. Installs Chromium via Playwright
3. Runs UI tests then API tests
4. Uploads test artifacts on failure
