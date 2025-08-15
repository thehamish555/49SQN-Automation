import json
import pathlib
import re
import time
import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService


class NZCF170CLoader:
    BASE = "https://www.cadetnet.org.nz"
    LOGIN_URL = BASE + "/wp-login.php"
    TARGET_URL = BASE + "/7-training/nzcf-170c/"

    DELAY = 2  # seconds between page fetches

    def __init__(self):
        self.out_path = pathlib.Path(
            st.session_state.BASE_PATH + "/resources/configurations/syllabus.json"
        )

        # Chrome headless for Streamlit Cloud
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")  # modern headless
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--log-level=3")
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/115.0.0.0 Safari/537.36"
        )

        # Use Chromium installed via packages.txt
        chrome_options.binary_location = "/usr/bin/chromium-browser"
        self.driver = webdriver.Chrome(
            service=ChromeService("/usr/bin/chromedriver"),
            options=chrome_options,
        )
        self.wait = WebDriverWait(self.driver, 30)

    def _save_json(self, data):
        self.out_path.parent.mkdir(parents=True, exist_ok=True)
        with self.out_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _get_existing_data(self):
        if self.out_path.exists():
            try:
                with self.out_path.open("r", encoding="utf-8") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {}
        return {}

    def _login(self, username, password):
        self.driver.get(self.LOGIN_URL)

        try:
            self.wait.until(EC.presence_of_element_located((By.ID, "user_login")))
        except:
            st.error("Login form did not appear. Check website or CAPTCHA.")
            return False

        self.driver.find_element(By.ID, "user_login").send_keys(username)
        self.driver.find_element(By.ID, "user_pass").send_keys(password)
        self.driver.find_element(By.ID, "wp-submit").click()

        time.sleep(3)
        return True

    def _extract_lessons(self, username, password):
        lessons = self._get_existing_data()

        if not self._login(username, password):
            return lessons

        self.driver.get(self.TARGET_URL)
        time.sleep(self.DELAY)

        rows = self.driver.find_elements(By.CSS_SELECTOR, "tr")
        for row in rows:
            try:
                a_tag = row.find_element(By.CSS_SELECTOR, "td a[href*='/7-training/nzcf-170c/']")
            except:
                continue

            href = a_tag.get_attribute("href")
            text = a_tag.text.replace("–", "-")
            m = re.match(r"([A-Z]{3})[-\s]?(\d+\.\d+)\s*(?:[-–]\s*)?(.+)", text)
            if not m:
                st.warning(f"Skipped parsing: {text}")
                continue

            module, lesson_num, lesson_title = m.groups()
            year = f"Year {lesson_num.split('.')[0]}"

            if (
                year in lessons
                and module in lessons[year]
                and f"{lesson_num} {lesson_title}" in lessons[year][module]
            ):
                continue

            try:
                periods_td = row.find_element(By.CSS_SELECTOR, "td[style*='text-align:right']")
                periods = int(re.search(r"(\d+)", periods_td.text).group(1))
            except:
                periods = None

            self.driver.get(href)
            time.sleep(self.DELAY)

            pdf_link = None
            pdf_els = self.driver.find_elements(By.CSS_SELECTOR, "a[href$='.pdf']")
            for el in pdf_els:
                link = el.get_attribute("href")
                if "instructor_guides" in link:
                    pdf_link = link
                    break

            if not pdf_link:
                st.warning(f"No instructor guide for {module} {lesson_num}")
                continue

            lessons.setdefault(year, {}).setdefault(module, {})[
                f"{lesson_num} {lesson_title}"
            ] = {"url": pdf_link, "periods": periods}

            self._save_json(lessons)
            print(f"Saved: {lesson_num} {lesson_title}")

        return lessons

    def install(self):
        username = st.secrets["cadetnet"]["USERNAME"]
        password = st.secrets["cadetnet"]["PASSWORD"]
        data = self._extract_lessons(username, password)
        return data
