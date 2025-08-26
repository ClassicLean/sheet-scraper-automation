"""
Enhanced browser management with improved anti-detection capabilities.
"""

import random
import time

from playwright.sync_api import Browser, BrowserContext, Page
from undetected_playwright.ninja import stealth_sync

from sheet_scraper.config.constants import USER_AGENTS


class EnhancedBrowserManager:
    """Manages browser instances with enhanced anti-detection features."""

    def __init__(self, browser: Browser, proxy_manager=None):
        self.browser = browser
        self.proxy_manager = proxy_manager
        self.context: BrowserContext | None = None
        self.page: Page | None = None

    def create_context(self) -> BrowserContext:
        """Create a new browser context with random settings."""
        context_options = {
            "viewport": self._get_random_viewport(),
            "user_agent": random.choice(USER_AGENTS),
            "locale": random.choice(["en-US", "en-GB", "en-CA"]),
            "timezone_id": random.choice(
                ["America/New_York", "America/Los_Angeles", "America/Chicago"]
            ),
            "permissions": ["geolocation"],
            "geolocation": self._get_random_location(),
            "color_scheme": random.choice(["light", "dark"]),
            "reduced_motion": random.choice(["reduce", "no-preference"]),
        }

        # Add proxy if available
        if self.proxy_manager:
            proxy = self.proxy_manager.get_proxy()
            if proxy:
                context_options["proxy"] = {"server": proxy}

        self.context = self.browser.new_context(**context_options)
        return self.context

    def create_page(self) -> Page:
        """Create a new page with stealth features."""
        if not self.context:
            self.create_context()

        self.page = self.context.new_page()

        # Apply stealth features
        stealth_sync(self.page)

        # Add additional anti-detection measures
        self._add_webdriver_overrides()
        self._add_browser_overrides()

        return self.page

    def _get_random_viewport(self) -> dict[str, int]:
        """Generate a random but realistic viewport."""
        common_resolutions = [
            (1920, 1080),
            (1366, 768),
            (1440, 900),
            (1536, 864),
            (1280, 720),
            (1600, 900),
            (1024, 768),
            (1680, 1050),
        ]
        width, height = random.choice(common_resolutions)
        return {"width": width, "height": height}

    def _get_random_location(self) -> dict[str, float]:
        """Generate a random location in the US."""
        locations = [
            {"latitude": 40.7128, "longitude": -74.0060},  # New York
            {"latitude": 34.0522, "longitude": -118.2437},  # Los Angeles
            {"latitude": 41.8781, "longitude": -87.6298},  # Chicago
            {"latitude": 29.7604, "longitude": -95.3698},  # Houston
            {"latitude": 39.9526, "longitude": -75.1652},  # Philadelphia
        ]
        return random.choice(locations)

    def _add_webdriver_overrides(self):
        """Add webdriver detection overrides."""
        if not self.page:
            return

        self.page.add_init_script("""
            // Override webdriver property
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });

            // Override plugins length
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5],
            });

            // Override languages
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en'],
            });

            // Override chrome property
            Object.defineProperty(window, 'chrome', {
                get: () => ({
                    runtime: {},
                    loadTimes: function() {},
                    csi: function() {},
                }),
            });

            // Override permissions
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
        """)

    def _add_browser_overrides(self):
        """Add additional browser property overrides."""
        if not self.page:
            return

        self.page.add_init_script("""
            // Add more realistic screen properties
            Object.defineProperty(screen, 'availTop', { get: () => 0 });
            Object.defineProperty(screen, 'availLeft', { get: () => 0 });
            Object.defineProperty(screen, 'availHeight', { get: () => screen.height - 40 });
            Object.defineProperty(screen, 'availWidth', { get: () => screen.width });

            // Add connection property
            Object.defineProperty(navigator, 'connection', {
                get: () => ({
                    effectiveType: '4g',
                    rtt: 50,
                    downlink: 10,
                }),
            });

            // Override hardwareConcurrency
            Object.defineProperty(navigator, 'hardwareConcurrency', {
                get: () => Math.max(2, Math.floor(Math.random() * 8) + 1),
            });
        """)

    def simulate_human_behavior(self):
        """Simulate human-like behavior on the page."""
        if not self.page:
            return

        try:
            # Random mouse movements
            for _ in range(random.randint(1, 3)):
                x = random.randint(100, 800)
                y = random.randint(100, 600)
                self.page.mouse.move(x, y)
                time.sleep(random.uniform(0.1, 0.3))

            # Random scroll
            scroll_amount = random.randint(100, 500)
            self.page.evaluate(f"window.scrollBy(0, {scroll_amount})")
            time.sleep(random.uniform(0.5, 1.0))

            # Sometimes scroll back up
            if random.random() < 0.3:
                scroll_back = random.randint(50, scroll_amount)
                self.page.evaluate(f"window.scrollBy(0, -{scroll_back})")
                time.sleep(random.uniform(0.3, 0.7))

        except Exception as e:
            print(f"DEBUG: Error simulating human behavior: {e}")

    def random_delay(self, min_seconds: float = 1.0, max_seconds: float = 3.0):
        """Add a random delay between actions."""
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)

    def close(self):
        """Clean up browser resources."""
        if self.page:
            self.page.close()
        if self.context:
            self.context.close()
