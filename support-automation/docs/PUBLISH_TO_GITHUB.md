# Publishing this repo to GitHub

The shareable URL for this project is a GitHub repository link. Below are three ways to create
it, fastest first. All assume you've downloaded and unzipped `support-automation/` locally.

Before you start: open `LICENSE` and replace `[YOUR NAME]`, and optionally add your name to
the top of `docs/AI_USAGE.md`.

---

## Option A — GitHub website upload (no tools, ~2 minutes)

1. Go to https://github.com/new and create a repository named `support-automation`
   (Public if you want a link anyone can open; Private if you'll invite reviewers).
   Do NOT initialize it with a README/license — this project already has them.
2. On the new empty repo page, click **"uploading an existing file"**.
3. Drag the entire contents of the `support-automation/` folder into the browser
   (or zip → drag → GitHub expands it). Commit.
4. Your shareable URL is `https://github.com/<your-username>/support-automation`.

This is the simplest path and needs nothing installed.

---

## Option B — Git command line (recommended if you have git)

From inside the `support-automation/` folder:

```bash
git init
git add .
git commit -m "Support automation: skills, agents, and the Skill/Agent/Neither reasoning"
git branch -M main

# Create the empty repo on github.com first (see Option A step 1), then:
git remote add origin https://github.com/<your-username>/support-automation.git
git push -u origin main
```

Shareable URL: `https://github.com/<your-username>/support-automation`

---

## Option C — GitHub CLI (fastest if you have `gh`)

From inside the `support-automation/` folder:

```bash
git init && git add . && git commit -m "Initial commit"
gh repo create support-automation --public --source=. --remote=origin --push
```

`gh` creates the remote repo and pushes in one step, then prints the URL.

---

## After pushing

- **Verify it renders:** open the repo URL; `README.md` shows as the landing page with the
  verdicts table, repo layout, and run instructions.
- **Point reviewers at the core:** the two files that matter most are
  [`docs/DECISIONS.md`](DECISIONS.md) (the classification + justification) and
  [`docs/AI_USAGE.md`](AI_USAGE.md) (the AI-usage disclosure).
- **Reviewers can run it** with no setup: `python3 agents/<name>/<agent>.py` and the matching
  `test_*.py`. No dependencies, no API key.
- **If the submission wants a single link**, give them the repo URL. If it wants a specific
  commit, use the URL under the repo's "commits" view so it's pinned.

## Optional: a live page for the README
If you also want a rendered web page (not just the repo), enable **GitHub Pages**:
Settings → Pages → Source: `main` / root. GitHub serves the README-based site at
`https://<your-username>.github.io/support-automation/`. Note this only renders the docs — the
Python still runs locally, not in the browser.
