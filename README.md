# 49SQN Automation

## Overview
49SQN Automation is a project designed to streamline tasks using automation. It features a **backend** (currently non-functional) and a **frontend** built with Streamlit for a user-friendly interface.

## Features
- **Frontend Portal** using Streamlit
  - Upload, download, and view Lesson Plans
  - Future feature: Automate training program creation for Officers
- **Frontend configuration via `.streamlit/config.toml`**
- **Dependency management** via `requirements.txt`

## Project Structure
```
49SQN-Automation/
│-- .streamlit/               # Streamlit configuration files
│-- backend/                  # Backend logic (currently inactive)
│   ├── facebook/             # Placeholder for Facebook automation module
│-- frontend/                 # Frontend using Streamlit
│   ├── website/              # Web interface files
│   │   ├── app.py            # Main Streamlit app
│   │   ├── resources/media/  # Media assets (e.g., logo.png)
│   │   ├── sub_pages/        # Sub-page modules
│-- requirements.txt          # Python dependencies
│-- LICENSE                   # GPL-3.0 License
```

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/thehamish555/49SQN-Automation.git
   ```
2. Navigate into the project directory:
   ```bash
   cd 49SQN-Automation
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the frontend:
   ```bash
   streamlit run frontend/website/app.py
   ```

## License
This project is licensed under the **GPL-3.0 License**, as specified in the `LICENSE` file.

## Contributing
Feel free to submit issues or pull requests to improve the project!

