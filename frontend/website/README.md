# 49SQN Website

## Overview
The 49SQN Website is a **Streamlit-based portal** designed to manage and automate squadron-related tasks. The website allows users to upload, download, and view **Lesson Plans**, with future plans to automate the **training program creation** for Officers.

## Features
- **Upload, download, and view Lesson Plans**
- **Future feature:** Training program automation for Officers
- **Media resources** stored under `resources/media/`
- **Modular sub-pages** for structured navigation

## Project Structure
```
frontend/website/
│-- app.py                   # Main Streamlit app
│-- resources/
│   ├── media/               # Media assets (e.g., logo.png)
│-- sub_pages/               # Additional pages for structured navigation
```

## Installation & Usage
1. Ensure you have the required dependencies installed:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the website:
   ```bash
   streamlit run frontend/website/app.py
   ```

## License
This website is part of the **49SQN Automation Project**, licensed under **GPL-3.0**.

## Contributing
Contributions are welcome! Please submit issues or pull requests to improve the website functionality.

## Version Meanings
__xx__.xx.xx - Full Release
xx.__xx__.xx - Major Version (New Features etc)
xx.xx.__xx__ - Minor Version (Bug Fixes etc)