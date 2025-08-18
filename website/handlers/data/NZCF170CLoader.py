import json
import pathlib
import requests
import time
import streamlit as st

class NZCF170CLoader:
    WORKER_URL = "https://wild-lab-6641.hamishlester555.workers.dev/"
    BATCH_SIZE = 15
    DELAY = 1.0  # seconds between requests

    def __init__(self, base_path: str):
        self.out_path = pathlib.Path(base_path) / "resources/configurations/syllabus.json"

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

    def fetch_all_lessons(self) -> dict:
        lessons = self._get_existing_data()
        start = 0

        while True:
            params = {"start": start, "limit": self.BATCH_SIZE, "token": st.secrets["cadetnet"]["TOKEN"]}
            try:
                resp = requests.get(self.WORKER_URL, params=params, timeout=30)
                resp.raise_for_status()
            except requests.RequestException as e:
                st.error(f"[ERROR] Fetching batch starting at {start}: {e}")
                time.sleep(self.DELAY)
                continue

            batch = resp.json()
            if not batch:
                break

            for year, modules in batch.items():
                lessons.setdefault(year, {})
                for module, lessons_dict in modules.items():
                    lessons[year].setdefault(module, {})
                    for lesson_num, data in lessons_dict.items():
                        if lesson_num in lessons[year][module]:
                            continue
                        data['title'] = data['title'].replace('&#8211;', '-').lstrip('- ')
                        lessons[year][module][lesson_num] = data
                        st.info(f"[SAVED] {year} {module} {lesson_num} - {data['title']}")

            self._save_json(lessons)

            start += self.BATCH_SIZE
            time.sleep(self.DELAY)

        return lessons
