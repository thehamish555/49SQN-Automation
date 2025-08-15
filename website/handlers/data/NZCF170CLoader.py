import json
import pathlib
import urllib.parse
import re
import time
import logging
from typing import Dict, Optional, Tuple, Any
from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup
import streamlit as st


@dataclass
class LessonData:
    """Data class for lesson information."""
    url: str
    periods: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {"url": self.url, "periods": self.periods}


class ScrapingError(Exception):
    """Custom exception for scraping-related errors."""
    pass


class NZCF170CLoader:
    """
    Web scraper for NZCF-170C training data from cadetnet.org.nz.
    
    Features:
    - Progressive saving to prevent data loss
    - Rate limiting and session management
    - Comprehensive error handling and logging
    - Structured data handling with type hints
    """
    
    BASE_URL = "https://www.cadetnet.org.nz"
    LOGIN_URL = BASE_URL + "/wp-login.php"
    TARGET_URL = BASE_URL + "/7-training/nzcf-170c/"
    
    # Request configuration
    HEADERS = {"User-Agent": "Mozilla/5.0 (cadetnet-scraper/8.0)"}
    TIMEOUT = 30
    DELAY = 1.5  # seconds between requests
    MAX_RETRIES = 3
    
    # Regex patterns
    LESSON_PATTERN = re.compile(r"([A-Z]{3})\s+(\d+\.\d+)\s*-\s*(.+)")
    PERIODS_PATTERN = re.compile(r"(\d+)")

    def __init__(self, base_path: Optional[str] = None) -> None:
        """
        Initialize the loader.
        
        Args:
            base_path: Custom base path for output file. If None, uses streamlit session state.
        """
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Determine output path
        if base_path:
            self.out_path = pathlib.Path(base_path) / "resources/configurations/nzcf_170c.json"
        else:
            base = getattr(st.session_state, 'BASE_PATH', '.')
            self.out_path = pathlib.Path(base) / "resources/configurations/nzcf_170c.json"

    def _build_full_url(self, relative_url: Optional[str]) -> Optional[str]:
        """Convert relative URL to absolute URL."""
        return urllib.parse.urljoin(self.BASE_URL, relative_url) if relative_url else None

    def _extract_hidden_inputs(self, form) -> Dict[str, str]:
        """Extract hidden input fields from a form."""
        return {
            input_field["name"]: input_field.get("value", "")
            for input_field in form.select("input[type=hidden][name]")
        }

    def _create_session(self) -> requests.Session:
        """Create a requests session with default configuration."""
        session = requests.Session()
        session.headers.update(self.HEADERS)
        return session

    def _login(self, username: str, password: str) -> requests.Session:
        """
        Authenticate with the website and return session.
        
        Args:
            username: Login username
            password: Login password
            
        Returns:
            Authenticated requests session
            
        Raises:
            ScrapingError: If login fails
        """
        session = self._create_session()
        
        try:
            # Get login page
            response = session.get(self.LOGIN_URL, timeout=self.TIMEOUT)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            form = soup.select_one("form#loginform")
            
            if not form:
                raise ScrapingError("Login form not found on page")
            
            # Prepare login payload
            payload = {
                "log": username,
                "pwd": password,
                "wp-submit": "Log In",
                **self._extract_hidden_inputs(form)
            }
            
            # Submit login
            login_response = session.post(
                self.LOGIN_URL, 
                data=payload, 
                timeout=self.TIMEOUT
            )
            login_response.raise_for_status()
            
            self.logger.info("Successfully logged in")
            return session
            
        except requests.RequestException as e:
            raise ScrapingError(f"Login failed: {e}")

    def _fetch_page_with_retry(self, session: requests.Session, url: str, 
                              username: str, password: str) -> str:
        """
        Fetch a page with automatic retry and re-authentication.
        
        Args:
            session: Current session
            url: URL to fetch
            username: Username for re-authentication
            password: Password for re-authentication
            
        Returns:
            Page HTML content
            
        Raises:
            ScrapingError: If all retry attempts fail
        """
        for attempt in range(self.MAX_RETRIES):
            try:
                time.sleep(self.DELAY)  # Rate limiting
                response = session.get(url, timeout=self.TIMEOUT)
                response.raise_for_status()
                
                # Check if we need to re-authenticate
                if "wp-login.php" in response.text:
                    if attempt < self.MAX_RETRIES - 1:
                        self.logger.warning(f"Session expired, re-authenticating (attempt {attempt + 1})")
                        session = self._login(username, password)
                        continue
                    else:
                        raise ScrapingError("Session expired and max retries reached")
                
                return response.text
                
            except requests.RequestException as e:
                if attempt < self.MAX_RETRIES - 1:
                    self.logger.warning(f"Request failed (attempt {attempt + 1}): {e}")
                    time.sleep(self.DELAY * (attempt + 1))  # Exponential backoff
                else:
                    raise ScrapingError(f"Failed to fetch {url} after {self.MAX_RETRIES} attempts: {e}")
        
        raise ScrapingError("Unexpected error in fetch retry loop")

    def _load_existing_data(self) -> Dict[str, Any]:
        """Load existing lesson data from JSON file."""
        if not self.out_path.exists():
            return {}
        
        try:
            with self.out_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
                self.logger.info(f"Loaded existing data with {len(data)} years")
                return data
        except (json.JSONDecodeError, IOError) as e:
            self.logger.warning(f"Could not load existing data: {e}")
            return {}

    def _save_data(self, data: Dict[str, Any]) -> None:
        """Save lesson data to JSON file."""
        try:
            self.out_path.parent.mkdir(parents=True, exist_ok=True)
            with self.out_path.open("w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
        except IOError as e:
            self.logger.error(f"Failed to save data: {e}")
            raise ScrapingError(f"Could not save data to {self.out_path}: {e}")

    def _parse_lesson_text(self, text: str) -> Optional[Tuple[str, str, str, str]]:
        """
        Parse lesson text to extract components.
        
        Args:
            text: Raw lesson text
            
        Returns:
            Tuple of (module, lesson_num, lesson_title, year) or None if parsing fails
        """
        clean_text = text.replace("–", "-").strip()
        match = self.LESSON_PATTERN.match(clean_text)
        
        if not match:
            return None
            
        module, lesson_num, lesson_title = match.groups()
        year = f"Year {lesson_num.split('.')[0]}"
        
        return module, lesson_num, lesson_title.strip(), year

    def _extract_periods(self, periods_cell) -> Optional[int]:
        """Extract number of periods from table cell."""
        if not periods_cell:
            return None
            
        text = periods_cell.get_text(strip=True)
        match = self.PERIODS_PATTERN.search(text)
        
        return int(match.group(1)) if match else None

    def _find_instructor_guide_pdf(self, soup: BeautifulSoup) -> Optional[str]:
        """Find instructor guide PDF link on lesson page."""
        for link in soup.select("a[href$='.pdf']"):
            href = link.get("href", "")
            if "instructor_guides" in href:
                return self._build_full_url(href)
        return None

    def _should_skip_lesson(self, lessons_data: Dict[str, Any], year: str, 
                           module: str, lesson_key: str) -> bool:
        """Check if lesson should be skipped (already exists)."""
        return (
            year in lessons_data and
            module in lessons_data[year] and
            lesson_key in lessons_data[year][module]
        )

    def _process_lesson_row(self, row, session: requests.Session, 
                           lessons_data: Dict[str, Any], username: str, password: str) -> bool:
        """
        Process a single lesson row from the main table.
        
        Args:
            row: BeautifulSoup row element
            session: Requests session
            lessons_data: Current lessons data
            username: Username for authentication
            password: Password for authentication
            
        Returns:
            True if lesson was processed successfully, False otherwise
        """
        # Find lesson link
        link = row.select_one("td a[href*='/7-training/nzcf-170c/']")
        if not link:
            return False

        # Parse lesson information
        lesson_url = self._build_full_url(link.get("href"))
        lesson_text = link.get_text(strip=True)
        
        parsed = self._parse_lesson_text(lesson_text)
        if not parsed:
            self.logger.debug(f"Could not parse lesson text: {lesson_text}")
            return False
            
        module, lesson_num, lesson_title, year = parsed
        lesson_key = f"{lesson_num} {lesson_title}"
        
        # Skip if already processed
        if self._should_skip_lesson(lessons_data, year, module, lesson_key):
            self.logger.debug(f"Skipping existing lesson: {lesson_key}")
            return True

        # Extract periods
        periods_cell = row.select_one("td[style*='text-align:right']")
        periods = self._extract_periods(periods_cell)

        try:
            # Fetch lesson page
            lesson_html = self._fetch_page_with_retry(session, lesson_url, username, password)
            lesson_soup = BeautifulSoup(lesson_html, "html.parser")
            
            # Find instructor guide PDF
            pdf_url = self._find_instructor_guide_pdf(lesson_soup)
            if not pdf_url:
                self.logger.warning(f"No instructor guide found for {module} {lesson_num}")
                return False

            # Store lesson data
            lesson_data = LessonData(url=pdf_url, periods=periods)
            
            lessons_data.setdefault(year, {}).setdefault(module, {})[lesson_key] = lesson_data.to_dict()
            
            # Progressive save
            self._save_data(lessons_data)
            self.logger.info(f"Saved: {lesson_key}")
            
            return True
            
        except ScrapingError as e:
            self.logger.error(f"Failed to process lesson {lesson_key}: {e}")
            return False

    def _extract_all_lessons(self, main_html: str, session: requests.Session, 
                            username: str, password: str) -> Dict[str, Any]:
        """Extract all lessons from the main page."""
        soup = BeautifulSoup(main_html, "html.parser")
        lessons_data = self._load_existing_data()
        
        rows = soup.select("tr")
        total_rows = len(rows)
        processed_count = 0
        
        self.logger.info(f"Processing {total_rows} table rows")
        
        for i, row in enumerate(rows, 1):
            if self._process_lesson_row(row, session, lessons_data, username, password):
                processed_count += 1
                
            if i % 10 == 0:  # Progress logging
                self.logger.info(f"Processed {i}/{total_rows} rows ({processed_count} lessons)")
        
        self.logger.info(f"Completed processing: {processed_count} lessons from {total_rows} rows")
        return lessons_data

    def scrape(self, username: Optional[str] = None, password: Optional[str] = None) -> Dict[str, Any]:
        """
        Main method to scrape NZCF-170C lesson data.
        
        Args:
            username: Login username (optional, uses streamlit secrets if not provided)
            password: Login password (optional, uses streamlit secrets if not provided)
            
        Returns:
            Dictionary containing all lesson data
            
        Raises:
            ScrapingError: If scraping fails
        """
        # Get credentials
        if not username or not password:
            try:
                username = username or st.secrets["cadetnet"]["USERNAME"]
                password = password or st.secrets["cadetnet"]["PASSWORD"]
            except (KeyError, AttributeError):
                raise ScrapingError("Username and password must be provided or available in streamlit secrets")

        try:
            # Login and fetch main page
            self.logger.info("Starting NZCF-170C data scraping")
            session = self._login(username, password)
            
            main_html = self._fetch_page_with_retry(session, self.TARGET_URL, username, password)
            
            # Extract lessons
            lessons_data = self._extract_all_lessons(main_html, session, username, password)
            
            # Final save
            self._save_data(lessons_data)
            self.logger.info(f"Scraping completed successfully. Data saved to {self.out_path}")
            
            return lessons_data
            
        except Exception as e:
            self.logger.error(f"Scraping failed: {e}")
            raise ScrapingError(f"Failed to scrape NZCF-170C data: {e}")

    # Maintain backward compatibility
    def install(self) -> Dict[str, Any]:
        """Legacy method name for backward compatibility."""
        return self.scrape()