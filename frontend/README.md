# Mini SOC — Frontend

React (Vite) dashboard for the Mini SOC backend.

## Stack

- React 18 + Vite
- React Router v6
- Axios with JWT interceptor
- CSS Modules — no external UI library

## Features

- Login page with terminal-style command output
- JWT stored in localStorage, auto-cleared on 401
- Live auto-refresh every 10 seconds (toggle on/off)
- Alerts table — color-coded by action type
- Blocked IPs list with one-click unblock
- Health status bar with pulsing live indicator
- Summary stat cards (total alerts, blocks, DDoS, port scans)

## Setup

### 1. Install dependencies

```bash
cd soc-frontend
npm install
```

### 2. Backend must be running

```bash
# In your mini-soc-lab directory
python api.py
```

API must be on `http://127.0.0.1:5000`. The Vite dev server proxies `/api/*` to it.

### 3. Run the frontend

```bash
npm run dev
```

Opens at `http://localhost:3000`.

### 4. Login

Use the credentials from your `.env` file:
- `ADMIN_USERNAME`
- Password you hashed with bcrypt

## Project structure

```
soc-frontend/
├── index.html
├── vite.config.js
├── package.json
└── src/
    ├── main.jsx
    ├── App.jsx              # routing + auth guards
    ├── index.css            # global design tokens
    ├── api.js               # axios client with JWT
    ├── AuthContext.jsx      # login/logout state
    ├── hooks/
    │   └── useAutoRefresh.js
    ├── pages/
    │   ├── LoginPage.jsx
    │   ├── LoginPage.module.css
    │   ├── DashboardPage.jsx
    │   └── DashboardPage.module.css
    └── components/
        ├── Navbar.jsx
        ├── Navbar.module.css
        ├── HealthBar.jsx
        ├── HealthBar.module.css
        ├── StatCards.jsx
        ├── StatCards.module.css
        ├── AlertsTable.jsx
        ├── AlertsTable.module.css
        ├── BlockedIPs.jsx
        └── BlockedIPs.module.css
```

## Build for production

```bash
npm run build
```

Output in `dist/`. Serve with any static host or nginx.

## Notes

- Auto-refresh polls every 10 seconds. Toggle the `live` button in the navbar to pause.
- Unblocking an IP calls `POST /unblock` and removes it from local state immediately without waiting for the next refresh cycle.
- If the backend is unreachable, an error banner appears — the UI does not crash.
- On 401 from any protected route, the token is cleared and the user is redirected to `/login` automatically.
