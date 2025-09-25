# Mini Flask E‑Commerce (Class Demo)

**Super simple** Flask + SQLite demo (plaintext passwords for class only).
Works great on macOS or Windows + VS Code.

## Quick start for Windows

On Windows, launching this project in VS Code. Here’s what you do step-by-step:

---

## 1. Unzip the project

* Extract the `flask_ecommerce_simple.zip` you downloaded into a folder (e.g., `C:\Users\<YourName>\Documents\flask_ecommerce_simple`).

---

## 2. Open it in VS Code

* In VS Code, go to **File → Open Folder** and select the `flask_ecommerce_simple` folder.

---

## 3. Open the terminal in VS Code

* In VS Code, press <kbd>Ctrl</kbd>+<kbd>\`</kbd> (backtick) or go to **View → Terminal**.

---

## 4. Create and activate a virtual environment

Run these commands in the VS Code terminal:

```powershell
# Create a virtual environment
python -m venv .venv

# Activate the virtual environment (PowerShell syntax)
.venv\Scripts\activate
```

> If you’re using **Command Prompt** instead of PowerShell, the activation command is:
>
> ```
> .venv\Scripts\activate.bat
> ```

---

## 5. Install dependencies

```powershell
pip install -r requirements.txt
```

---

## 6. Run the Flask app

```powershell
python app.py
```

---

## 7. Open in browser

Once it starts, it will say something like:

```
 * Running on http://127.0.0.1:5000 (Press CTRL+C to quit)
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your web browser.

---

✅ You should now see your **Mini Shop** app running.

* Customer signup works.
* Guest checkout works.
* Staff login: `staff / staff` → gives access to **Fulfill** page.


# Quick start for MacOS

```bash
# 1) Open VS Code, then open this folder.
# 2) In VS Code terminal:
python3 -m venv .venv
source ./.venv/bin/activate  # macOS
pip install -r requirements.txt
python app.py
# open http://127.0.0.1:5000
```

- Staff demo user: `staff / staff`
- If `ecommerce.db` is missing, it will be created with sample data on first run.

## Features
- Search products
- Guest checkout (no account)
- Sign up / Login (plaintext passwords — classroom only)
- Update account (name/email/address)
- Cart + Checkout creates orders
- Staff portal to advance order status: Open → Ready → Shipped → Picked-up
