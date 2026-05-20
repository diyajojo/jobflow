# Extension — JobFlow Chrome Extension

A Manifest V3 Chrome Extension that automatically fills job application forms using your parsed resume profile and AI-generated answers.

---

## What It Does

1. You click "Apply on LinkedIn" from the JobFlow dashboard → your `job_id` is saved
2. You navigate to the actual application form on any website
3. You click **"Auto-fill Application Form"** in the extension popup
4. The extension:
   - Scans the page for all form fields (inputs, textareas, selects, radio groups, checkboxes)
   - Sends the question labels + your `resume_id` + `job_id` to the backend
   - The backend uses Groq Llama 3.3 to generate tailored answers
   - The extension fills every field automatically

---

## Files

| File | Purpose |
|------|---------|
| `manifest.json` | Extension config — permissions, scripts, popup declaration |
| `background.js` | Service worker — receives messages, calls the backend REST API |
| `content.js` | Injected into all pages — scrapes form fields, fills answers |
| `popup.html` | Extension UI (320px wide panel) |
| `popup.js` | Popup logic — button handler, status display |
| `sync.js` | Injected on `localhost:3000` only — syncs localStorage → chrome.storage |
| `styles.css` | Injected alongside `content.js` |

---

## How to Load the Extension (Development)

1. Open Chrome and go to `chrome://extensions/`
2. Enable **Developer mode** (toggle in the top-right corner)
3. Click **Load unpacked**
4. Select the `extension/` folder from this repository

After loading, pin the extension to your toolbar by clicking the puzzle icon → pin JobFlow.

### Reloading After Code Changes

The extension does **not** hot-reload. After editing any file:

1. Go to `chrome://extensions/`
2. Find "JobFlow" and click the **refresh icon** (↺)
3. If you edited `manifest.json`, you must remove and re-add the extension

---

## How It Works — Technical Detail

### Data Bridge (`sync.js`)

Chrome Extensions cannot read a webpage's `localStorage` directly due to the [isolated world](https://developer.chrome.com/docs/extensions/develop/concepts/content-scripts#isolated_world) security model.

`sync.js` is a content script injected **only on `http://localhost:3000`** (the frontend). It reads `resume_id` and `job_id` from `localStorage` and writes them to `chrome.storage.local`, which `background.js` can then access.

```js
// sync.js — runs on localhost:3000
chrome.storage.local.set({ resume_id, job_id });
```

### Form Field Detection (`content.js`)

`getLabelForInput()` uses a 6-strategy cascade to find a form field's question label:

| Priority | Strategy | Handles |
|----------|----------|---------|
| 1 | `aria-label` attribute | Most accessible forms |
| 2 | `aria-labelledby` (resolved IDs) | ARIA-rich forms |
| 3 | `input.labels` HTMLCollection | Standard `<label>` associations |
| 4 | `label[for="id"]` DOM query | Classic HTML forms |
| 5 | **Ancestor DOM traversal** (8 levels) | Google Forms, React-rendered forms |
| 6 | `placeholder` attribute | Last resort fallback |

Strategy 5 is the most important — it's how the extension handles **Google Forms** and modern JavaScript-rendered ATS platforms where the question title is a sibling/ancestor of the input, not a `<label>` element.

### Message Flow

```
popup.js
  chrome.tabs.sendMessage({ type: "TRIGGER_AUTOFILL" })
    ↓
content.js
  scrapeQuestions() → finds all form fields
  chrome.runtime.sendMessage({ type: "GENERATE_ANSWERS", questions, resume_id, job_id })
    ↓
background.js
  POST http://localhost:8000/extension/answers
    ↓
FastAPI → ExtensionService → Groq Llama 3.3
    ↑
  { answers: [{ question, answer }] }
    ↑
content.js
  fillField(field, answer) for each field
    ↑
popup.js shows "Form successfully auto-filled!"
```

---

## Supported Form Types

| Type | How it's handled |
|------|----------------|
| `input[type="text/email/tel/url/date"]` | Direct `.value` assignment + input/change events |
| `textarea` | Direct `.value` assignment |
| `select` | Direct `.value` assignment |
| `input[type="radio"]` (native) | Matched by value or label, `.checked = true` + change event |
| `div[role="radiogroup"]` (ARIA) | Google Forms style — matched by `aria-label`, `.click()` |
| `input[type="checkbox"]` | Set based on affirmative answer (yes/true/1/checked) |

---

## Testing the Extension

Since there's no automated test suite yet (see [open issues](https://github.com/mehrinshamim/mini-project/issues)), test manually:

### Full Flow Test

1. Start the backend (`uv run uvicorn app.main:app --reload`)
2. Start the frontend (`npm run dev` in `frontend/`)
3. Upload a resume in the dashboard
4. Run a job search and click "Apply on LinkedIn" on a result
5. Navigate to any job application page
6. Click the extension popup → "Auto-fill Application Form"
7. Verify fields are filled correctly

### Quick Form Test (no backend needed)

Create a simple HTML file locally:
```html
<form>
  <label for="name">Full Name</label>
  <input id="name" type="text">
  <label for="email">Email Address</label>
  <input id="email" type="email">
  <textarea aria-label="Tell us about yourself"></textarea>
</form>
```
Open it in Chrome, load the extension, and trigger autofill to test field detection.

### ATS Platforms to Test On

- Google Forms (`docs.google.com/forms`)
- Lever (`jobs.lever.co`)
- Greenhouse (`boards.greenhouse.io`)
- Standard HTML forms (LinkedIn Easy Apply, Workday)

---

## Contributing to the Extension

### Before You Start

- Read [`docs/ARCHITECTURE.md`](../docs/ARCHITECTURE.md) — especially the "Data Bridge" section
- Understand Chrome Extension MV3 — service workers replace background pages, `chrome.storage` replaces `localStorage`
- Reference: [Chrome Extension MV3 docs](https://developer.chrome.com/docs/extensions/mv3/intro/)

### Common Contribution Areas

| Area | Description | Difficulty |
|------|-------------|-----------|
| Error messages | Replace `alert()` in `content.js` with popup feedback | Beginner |
| Name consistency | Fix "Job Autofiller" → "JobFlow" in `manifest.json` | Beginner |
| Host permissions | Narrow `<all_urls>` to specific job board domains | Intermediate |
| sync.js optimization | Replace polling interval with MutationObserver | Intermediate |
| HTTPS localhost support | Fix `sync.js` match pattern to include `https://localhost` | Beginner |
| Field fill events | Verify React-controlled inputs get proper synthetic events | Advanced |
| Extension tests | Create a manual test checklist document | Beginner |

### Running Without the Full Backend

For UI-only changes to `popup.html` / `popup.js`:
- You can edit and reload without any backend
- Trigger autofill on a simple local HTML form to test field detection in `content.js`
- Mock the API response in `background.js` to test the fill logic without Groq

---

## Permissions Explained

| Permission | Why it's needed |
|------------|----------------|
| `storage` | Access `chrome.storage.local` (resume_id, job_id) |
| `activeTab` | Send messages to the currently open tab |
| `scripting` | Inject content scripts programmatically |
| `host_permissions: <all_urls>` | Fill forms on any job application website |

> ⚠️ `<all_urls>` is intentionally broad for now. Narrowing this to specific domains is an open contributor issue.

---

## Known Issues & Open Tasks

- [ ] `alert()` in `content.js` blocks the page — should use popup messaging instead
- [ ] Extension name inconsistency ("Job Autofiller" in manifest vs "JobFlow" in popup)  
- [ ] `sync.js` matches `http://localhost:*/*` — won't work on `https://localhost`
- [ ] `sync.js` polls every 1s indefinitely — should use `storage` event or MutationObserver
- [ ] `<all_urls>` host permission is overly broad
- [ ] No automated tests exist yet

See the [issues page](https://github.com/mehrinshamim/mini-project/issues) for full details and to claim one.
