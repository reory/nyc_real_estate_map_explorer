# Contributing to NYC Real Estate Explorer

Thank you for your interest in contributing to NYC Real Estate Explorer! Whether you're fixing a bug, improving documentation, expanding test coverage, or proposing new features, contributions are welcome.

## 👨🏽‍💻 Development Setup

### Prerequisites
- Python 3.11+
- uv package manager

### Clone the Repository

```bash
git clone https://github.com/reory/nyc_real_estate_map_explorer.git
cd nyc_real_estate_map_explorer
```

### Create a Virtual Environment

```bash
uv venv --python 3.11
# Linux/MacOS
source .venv/bin/activate
# Windows
.venv\Scripts\activate
```

### Install Dependencies

```bash
uv sync
```

### Launch the Application

```bash
streamlit run app.py
```

---

## 🧪 Running Tests

Run the full test suite:

```bash
pytest
```

Generate a coverage report:

```bash
pytest
```

---

## 📁 Project Structure

Please follow the existing modular architecture:

- **app.py** - Streamlit UI and application orchestration.
- **src/database.py** - SQLAlchemy models and database access.
- **src/engine.py** - Pandas and SciPy analysis logic.
- **src/mapping.py** - Folium map generation and visualisation.
- **src/ingest_data.py** - Data ingestion pipeline.
- **src/create_nyc_csv.py** - Dataset preparation utilities.
- **tests/** - Pytest test suite.

## Coding Standards

- Keep functions focused and single-purpose.
- Add or update tests when introducing new functionality.
- Use concise docstrings and comments.
- Maintain existing formatting and project structure.
- Run tests before submitting changes.

## Pull Request Process

1. Fork the repository.
2. Create a feature branch.

```bash
git checkout -b feature/my-new-feature
```

3. Commit your changes with a clear commit message.
4. Push your branch.
5. Open a Pull Request describing your changes.

## Reporting Issues

When reporting bugs, please include:

- A clear description of the issue.
- Steps to reproduce it.
- Expected behaviour.
- Screenshots or logs where applicable.

---

Thank you for helping improve NYC Real Estate Explorer! 🙂

---