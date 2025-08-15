import json
import pathlib
import urllib.parse
import sys
import re
import time
import requests
from bs4 import BeautifulSoup
import streamlit as st


class NZCF170CLoader:
    BASE = "https://www.cadetnet.org.nz"
    LOGIN_URL = BASE + "/wp-login.php"
    TARGET_URL = BASE + "/7-training/nzcf-170c/"
    HEADERS = {"User-Agent": "Mozilla/5.0 (cadetnet-scraper/8.0)"}
    TIMEOUT = 30
    DELAY = 1.5  # seconds between requests to avoid rate limit

    def __init__(self) -> None:
        # Output path based on session state
        self.out_path = pathlib.Path(
            st.session_state.BASE_PATH + "/resources/configurations/syllabus.json"
        )

    def _full_url(self, src: str | None) -> str | None:
        return urllib.parse.urljoin(self.BASE, src) if src else None

    def _hidden_inputs(self, form) -> dict:
        return {i["name"]: i.get("value", "") for i in form.select("input[type=hidden][name]")}

    def _login(self, user: str, pw: str) -> requests.Session:
        s = requests.Session()
        pg = s.get(self.LOGIN_URL, headers=self.HEADERS, timeout=self.TIMEOUT)
        pg.raise_for_status()
        soup = BeautifulSoup(pg.text, "html.parser")
        form = soup.select_one("form#loginform") or sys.exit("Login form missing")

        payload = {"log": user, "pwd": pw, "wp-submit": "Log In", **self._hidden_inputs(form)}
        s.post(self.LOGIN_URL, data=payload, headers=self.HEADERS, timeout=self.TIMEOUT)
        return s

    def _login_and_fetch_html(self, user: str, pw: str, url: str):
        s = self._login(user, pw)
        resp = s.get(url, headers=self.HEADERS, timeout=self.TIMEOUT)
        resp.raise_for_status()
        return resp.text, s

    def _get_existing_data(self) -> dict:
        if self.out_path.exists():
            try:
                with self.out_path.open("r", encoding="utf-8") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {}
        return {}

    def _save_json(self, data: dict) -> None:
        self.out_path.parent.mkdir(parents=True, exist_ok=True)
        with self.out_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _extract_lessons(self, main_html: str, session: requests.Session, username: str, password: str) -> dict:
        soup = BeautifulSoup(main_html, "html.parser")
        lessons = self._get_existing_data()

        for row in soup.select("tr"):
            a_tag = row.select_one("td a[href*='/7-training/nzcf-170c/']")
            if not a_tag:
                continue

            href = self._full_url(a_tag.get("href"))
            text = a_tag.get_text(strip=True).replace("–", "-")

            m = re.match(r"([A-Z]{3})[-\s]?(\d+\.\d+)\s*(?:[-–]\s*)?(.+)", text)
            if not m:
                continue
            module, lesson_num, lesson_title = m.groups()
            year = f"Year {lesson_num.split('.')[0]}"

            # Skip if already in saved data
            if (
                year in lessons
                and module in lessons[year]
                and f"{lesson_num} {lesson_title}" in lessons[year][module]
            ):
                continue

            periods_td = row.select_one("td[style*='text-align:right']")
            try:
                periods = int(re.search(r"(\d+)", periods_td.get_text(strip=True)).group(1))
            except:
                periods = None

            # Delay before request
            time.sleep(self.DELAY)
            sub_html = session.get(href, headers=self.HEADERS, timeout=self.TIMEOUT).text

            # Re-login if session expired
            if "wp-login.php" in sub_html:
                st.warning("Session expired or rate-limited — re-logging in...")
                session = self._login(username, password)
                time.sleep(self.DELAY)
                sub_html = session.get(href, headers=self.HEADERS, timeout=self.TIMEOUT).text

            sub_soup = BeautifulSoup(sub_html, "html.parser")
            pdf_link = None
            for link in sub_soup.select("a[href$='.pdf']"):
                if "instructor_guides" in link.get("href"):
                    pdf_link = self._full_url(link.get("href"))
                    break

            if not pdf_link:
                st.warning(f"Skipped {module} {lesson_num} — no instructor guide found")
                continue

            lessons.setdefault(year, {}).setdefault(module, {})[
                f"{lesson_num} {lesson_title}"
            ] = {
                "url": pdf_link,
                "periods": periods
            }
            self._save_json(lessons)  # Progressive save
            print(f"Saved {lesson_num} {lesson_title}")

        return lessons

    def install(self) -> dict:
        """Logs in, scrapes data with rate-limit handling, saves JSON progressively, and returns the dict."""
        username = st.secrets["cadetnet"]["USERNAME"]
        password = st.secrets["cadetnet"]["PASSWORD"]

        main_html, session = self._login_and_fetch_html(username, password, self.TARGET_URL)
        lessons_data = self._extract_lessons(main_html, session, username, password)
        return lessons_data
