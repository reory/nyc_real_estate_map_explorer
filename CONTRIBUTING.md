# Contributing to NYC Real Estate Explorer

Welcome! Whether it's reporting a bug, improving the documentation, or adding a new feature, your help is appreciated.

---

## How to Contribute

1. **Fork the Repository**: Click the 'Fork' button on GitHub to create your own copy of the project.
2. **Create a Feature Branch**: Work on your changes in a new branch (e.g., `git checkout -b feature/my-awesome-feature`).
3. **Commit Changes**: Make your changes and commit them with descriptive messages.
4. **Push to Branch**: Push your changes to your forked repository.
5. **Submit a Pull Request**: Submit a Pull Request (PR) to the main repository.

---

## Project Structure & Standards

Please respect the existing modular architecture:
* **`app.py`**: Avoid adding heavy logic here. Keep it as the UI orchestrator.
* **`src/engine.py`**: New data analysis logic belongs here. Please add unit tests if possible.
* **`src/database.py`**: Any new database queries or models should follow existing patterns.
* **`src/mapping.py`**: New map visualizations or layer logic go here.

---

## Reporting Bugs
If you find a bug, please open an issue on the GitHub repository. Be sure to include:
* A clear description of the issue.
* Steps to reproduce it.
* Screenshots or logs if applicable.

---

## Development Setup
Ensure you have the environment set up as per the `README.md`:
1. `python -m venv venv`
2. `source venv/bin/activate`
3. `pip install -r requirements.txt`
4. `streamlit run app.py`

---

- Thank you for helping make this project better! 🙂