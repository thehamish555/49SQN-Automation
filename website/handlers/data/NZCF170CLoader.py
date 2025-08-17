import json
import pathlib
import urllib.parse
import re
import time
import requests
from bs4 import BeautifulSoup
import streamlit as st


class NZCF170CLoader:
    WORKER_URL = "https://wild-lab-6641.hamishlester555.workers.dev/"
    HEADERS = {"User-Agent": "Mozilla/5.0 (cadetnet-scraper/10.0)"}
    TIMEOUT = 30
    DELAY = 1.5   # seconds between requests to avoid rate limit

    def __init__(self) -> None:
        self.out_path = pathlib.Path(
            st.session_state.BASE_PATH + "/resources/configurations/syllabus.json"
        )

    # ---------------------- Utilities ----------------------

    def _log(self, msg: str, level: str = "info") -> None:
        if hasattr(st, level):
            getattr(st, level)(msg)
        else:
            print(f"[{level.upper()}] {msg}")

    def _full_url(self, src: str | None) -> str | None:
        return urllib.parse.urljoin("https://www.cadetnet.org.nz", src) if src else None

    def _get_existing_data(self) -> dict:
        if self.out_path.exists():
            try:
                with self.out_path.open("r", encoding="utf-8") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                self._log("Corrupt JSON detected, starting fresh", "warning")
                return {}
        return {}

    def _save_json(self, data: dict) -> None:
        self.out_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with self.out_path.open("w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self._log(f"Error saving JSON: {e}", "error")

    # ---------------------- Fetch HTML ----------------------

    def _fetch_from_worker(self) -> tuple[str, requests.Session]:
        s = requests.Session()
        resp = s.get(self.WORKER_URL, headers=self.HEADERS, timeout=self.TIMEOUT)
        resp.raise_for_status()
        return resp.text, s

    # ---------------------- Scraping ----------------------

    def _parse_lesson_row(self, row):
        a_tag = row.select_one("td a[href*='/7-training/nzcf-170c/']")
        if not a_tag:
            return None

        text = a_tag.get_text(strip=True).replace("–", "-")
        href = self._full_url(a_tag.get("href"))

        m = re.match(r"([A-Z]{2,4})[-\s]?(\d+(?:\.\d+)?)\s*(?:[-–]\s*)?(.+)", text)
        if not m:
            return None

        module, lesson_num, lesson_title = m.groups()
        year = f"Year {lesson_num.split('.')[0]}"

        periods_td = row.select_one("td[style*='text-align:right']")
        try:
            periods = int(re.search(r"(\d+)", periods_td.get_text(strip=True)).group(1))
        except Exception:
            periods = None

        return {
            "module": module,
            "num": lesson_num,
            "title": lesson_title,
            "href": href,
            "year": year,
            "periods": periods,
        }

    def _extract_lessons(self, main_html: str, session: requests.Session) -> dict:
        soup = BeautifulSoup(main_html, "html.parser")
        lessons = self._get_existing_data()

        for row in soup.select("tr"):
            info = self._parse_lesson_row(row)
            if not info:
                continue

            key = info["num"]
            year, module = info["year"], info["module"]

            if year in lessons and module in lessons[year] and key in lessons[year][module]:
                continue

            # Fetch subpage
            time.sleep(self.DELAY)
            try:
                sub_resp = session.get(info["href"], headers=self.HEADERS, timeout=self.TIMEOUT)
                sub_resp.raise_for_status()
                sub_html = sub_resp.text
            except Exception as e:
                self._log(f"Failed to fetch {info['href']}: {e}", "warning")
                continue

            sub_soup = BeautifulSoup(sub_html, "html.parser")
            pdf_link = None
            for link in sub_soup.select("a[href$='.pdf']"):
                candidate = link.get("href")
                if candidate:
                    pdf_link = self._full_url(candidate)
                    break

            if not pdf_link:
                self._log(f"Skipped {module} {key} — no instructor guide", "warning")
                continue

            lessons.setdefault(year, {}).setdefault(module, {})[key] = {
                "title": info["title"],
                "url": pdf_link,
                "periods": info["periods"],
            }
            self._save_json(lessons)
            self._log(f"Saved {module} {key} {info['title']}", "info")

        return lessons

    # ---------------------- Public ----------------------

    def install(self) -> dict:
        main_html, session = self._fetch_from_worker()
        return self._extract_lessons(main_html, session)
