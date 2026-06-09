# mail-notifier

Sends an email notification from a Gmail account to any recipient. Useful for alerting when a long-running script or experiment finishes.

## Setup

### 1. Get a Gmail App Password

You need an **App Password** — a special 16-character password that gives this script send-only access to your Gmail account, without exposing your real password.

1. Enable 2-Step Verification on your Google account:
   https://myaccount.google.com/security
2. Generate an App Password:
   https://myaccount.google.com/apppasswords
   - Click "Select app" → choose "Mail" (or type a custom name like "experiment-notifier")
   - Click "Generate" → copy the 16-character password shown

### 2. Configure credentials

Copy the example file and fill in your details:

```
cp .env.example .env
```

Edit `.env`:

```
MAIL_SENDER=you@gmail.com
MAIL_PASSWORD=xxxx xxxx xxxx xxxx   # the App Password from step 1 (spaces are fine)
MAIL_RECIPIENT=recipient@example.com
```

`.env` is gitignored — it will never be committed.

### 3. Install dependencies

```
pip install python-dotenv
```

Or with Conda:

```
conda install -c conda-forge python-dotenv
```

## Usage

### Run directly (smoke test)

```
python notifier.py
python notifier.py --subject "Done" --body "Val loss: 0.42"
```

### Import in your experiment script

```python
import os
from notifier import EmailNotifier

notifier = EmailNotifier(
    sender=os.getenv("MAIL_SENDER"),
    password=os.getenv("MAIL_PASSWORD"),
    recipient=os.getenv("MAIL_RECIPIENT"),
)

# ... your experiment code ...

notifier.send("Training complete", "Final val loss: 0.42, epoch 50.")
```

No terminal setup needed — credentials are loaded automatically from `.env` when the module is imported.
