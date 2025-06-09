# Browser AI Agent

This is a personal automation agent that lets you control a browser using natural language. You tell it what to do in plain English, and it figures out how to do that by parsing your request into a plan, executing it step-by-step in a real browser, and reporting back the results.

No special commands. Just type something like:

```text
Search for "machine learning" on Wikipedia and take a screenshot
```

And it will:
- Open Wikipedia
- Fill in the search box
- Press Enter
- Scroll and wait if needed
- Capture the page

---

## 🎥 Demo

[![Watch the Demo](https://cdn.loom.com/sessions/thumbnails/5fd6f10d394a46eb80567f09b1cd07f3-00001.gif)](https://www.loom.com/share/5fd6f10d394a46eb80567f09b1cd07f3)

## ⚙️ Installation

[![Watch the Installation](https://cdn.loom.com/sessions/thumbnails/1e232cfd926942b48b09da2f5da11a51-00001.gif)](https://www.loom.com/share/1e232cfd926942b48b09da2f5da11a51)


## How it works

The app is made of two parts:

### 1. The Brain (Backend)
- Built with **FastAPI** and **Playwright**
- Uses **Ollama + Mistral** to turn natural language into action plans (like fill, click, goto)
- Keeps a live browser session open using Chromium
- Parses the DOM into structured elements
- Can solve captchas (like Amazon image captchas) using Tesseract OCR
- Every action is executed one by one with clear logs returned

### 2. The Face (Frontend)
- Built with **React + TailwindCSS**
- Simple text box to enter commands
- Scrollable log of everything the agent is doing
- Handles errors, failed clicks, selectors not found, etc.

---

## Installation

This assumes you're running on macOS with Python 3.10+ and Node.js 18+ installed.

### 1. Clone the repo

```bash
git clone https://github.com/aarshitaacharya/browser-agent.git
cd browser-agent
```

### 2. Set up Python backend

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install
```

Install Tesseract if you want CAPTCHA solving:

```bash
brew install tesseract
```

Start the backend:

```bash
PYTHONPATH=$(pwd) python -m uvicorn main:app --reload
```

### 3. Set up React frontend

```bash
cd frontend
npm install
npm start
```

Make sure this runs on port 3000.

---

## Usage

Once both frontend and backend are running:

- Open `http://localhost:3000`
- Type a command like:

```text
Log in to saucedemo.com with username standard_user and password secret_sauce
```

- Watch the steps show up in the log box as the agent acts

You can:
- Take screenshots
- Solve captchas (Amazon image-based ones)
- Scroll, click, fill forms
- Use ordinal commands like "click the second product"
- Click links, images, buttons, etc.

---

## Project structure

```text
browser-agent/
├── actions/            # All atomic browser actions (click, fill, scroll...)
├── agents/             # Command parser + execution controller
├── api/                # FastAPI routes (like /interact, /extract)
├── browser_session.py  # Browser session manager
├── frontend/           # React frontend (UI)
├── utils/              # Logger and helper functions
├── main.py             # FastAPI app entry point
├── requirements.txt    # Python dependencies
├── build.sh            # Dev script to launch frontend + backend
```

---

## Why this is fun

This app is fun because it's not just a chatbot. It actually does stuff. It clicks. It scrolls. It fills. It sees a CAPTCHA and tries to solve it. It's a little browser assistant that doesn't need hand-holding.

The coolest part? You can teach it new behaviors by just improving the LLM prompt or extracting more structure from the page.

And yeah, it's still a work in progress. But it's real. And it works.

---

## Coming soon

- Better CAPTCHA solving
- Memory of previous pages
- Keyboard shortcuts
- Screenshot gallery
