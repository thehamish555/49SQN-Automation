# 49SQN Automation

A streamlined **Streamlit-based dashboard** for New Zealand Cadet Forces Squadron 49, providing tools for managing accounts, training programs, resources, and more — all in one place.

---

## 🚀 Features

- 🔐 **Account Management** – Easily manage cadets and users.
- 📚 **Training Resources** – View documents, manuals, and lesson plans.
- 📅 **Training Program Builder** – Generate or review lesson plans and programs.
- 🌐 **Multi-language Support** – Internationalization via gettext-compatible `.po/.mo` files.
- 🎨 **Custom Theme** – Tailored layout with `style.css` and branding media.

---

## 🗂️ Project Structure

```python

website/
├── app.py                  # Main Streamlit app
├── handlers/               # Data loading and configuration classes
├── resources/              # Static files (CSS, images, locales, configs)
├── sub_pages/              # Page routes (home, tools, account, etc.)
└── .streamlit/config.toml  # Streamlit UI config

```

---

## 📦 Requirements

Install dependencies using:

```bash
pip install -r requirements.txt
````

---

## 🖥️ Running the App

From the `website/` directory, run:

```bash
streamlit run app.py
```

---

## 🌍 Internationalization

Translation files for english are located in:

```txt
resources/locales/en-US/LC_MESSAGES/messages.po
```

---

## 📁 Configurations

- `permission_structure.json` – Ranks and permissions
- `syllabus.json` – Training modules and stages
- `manuals.json` – Official cadet manuals

---

## 🖼️ Branding & Assets

Brand-aligned media is in `resources/media/`:

- `logo.png`, `icon.png`, `cadets_header.png`

---

## 📃 License

This project is licensed under the terms of the MIT License. See [LICENSE](LICENSE) for details.

---

## 🛠️ Contributing

Got a feature idea or found a bug? Open an issue or submit a PR!

---

## ✨ Acknowledgments

Created for 49 Squadron (ATC), Royal New Zealand Air Force Cadet Forces.
