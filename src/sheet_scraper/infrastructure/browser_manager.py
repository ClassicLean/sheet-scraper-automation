"""
Enhanced browser management with improved anti-detection capabilities.
"""

import random
import time

from playwright.sync_api import Browser, BrowserContext, Page
from undetected_playwright.ninja import stealth_sync

from ..logging.geolocation_logger import log_geolocation_debug, log_geolocation_info, log_geolocation_warning, log_geolocation_error

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
        try:
            log_geolocation_debug("Creating browser context with random settings...")
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
                    print(f"DEBUG: Using proxy: {proxy}")

            log_geolocation_debug(f"Context options: {context_options}")
            self.context = self.browser.new_context(**context_options)

            if not self.context:
                raise Exception("Browser failed to create context")

            log_geolocation_debug(f"Browser context created successfully: {type(self.context)}")
            return self.context

        except Exception as e:
            print(f"CRITICAL ERROR: Failed to create browser context: {e}")
            import traceback
            print(f"TRACEBACK: {traceback.format_exc()}")
            raise Exception(f"Browser context creation failed: {e}") from e

    def create_page(self) -> Page:
        """Create a new page with stealth features."""
        try:
            if not self.context:
                log_geolocation_debug("Creating new browser context...")
                self.create_context()
                if not self.context:
                    raise Exception("Failed to create browser context")

            log_geolocation_debug("Creating new page...")
            self.page = self.context.new_page()
            if not self.page:
                raise Exception("Failed to create browser page")

            log_geolocation_debug("Applying stealth features...")
            # Apply stealth features
            stealth_sync(self.page)

            # Add additional anti-detection measures
            log_geolocation_debug("Adding anti-detection measures...")
            self._add_webdriver_overrides()
            self._add_browser_overrides()

            # Ensure geolocation is properly set for Amazon compatibility
            log_geolocation_info("Setting enhanced geolocation for Amazon...")
            self._ensure_us_geolocation()

            log_geolocation_debug(f"Browser page created successfully: {type(self.page)}")
            return self.page

        except Exception as e:
            print(f"CRITICAL ERROR: Failed to create browser page: {e}")
            import traceback
            print(f"TRACEBACK: {traceback.format_exc()}")
            raise Exception(f"Browser page creation failed: {e}")from e

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
        """Generate a random location in the US for Amazon compatibility."""
        # Enhanced US locations with better coverage for Amazon delivery zones
        locations = [
            {"latitude": 40.7128, "longitude": -74.0060},  # New York, NY
            {"latitude": 34.0522, "longitude": -118.2437},  # Los Angeles, CA
            {"latitude": 41.8781, "longitude": -87.6298},  # Chicago, IL
            {"latitude": 29.7604, "longitude": -95.3698},  # Houston, TX
            {"latitude": 39.9526, "longitude": -75.1652},  # Philadelphia, PA
            {"latitude": 33.4484, "longitude": -112.0740},  # Phoenix, AZ
            {"latitude": 32.7767, "longitude": -96.7970},  # Dallas, TX
            {"latitude": 37.7749, "longitude": -122.4194},  # San Francisco, CA
            {"latitude": 39.2904, "longitude": -76.6122},  # Baltimore, MD
            {"latitude": 47.6062, "longitude": -122.3321},  # Seattle, WA
        ]
        location = random.choice(locations)
        log_geolocation_info(f"Selected US location: {location}")
        return location

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

    def _ensure_us_geolocation(self):
        """Ensure geolocation is set to a US location for Amazon compatibility."""
        try:
            if not self.context:
                return

            # Set a specific US location (New York City) as default for Amazon
            us_location = {"latitude": 40.7128, "longitude": -74.0060}  # NYC
            log_geolocation_debug(f"Ensuring US geolocation is set: {us_location}")

            # Use the async version properly in sync context
            import asyncio
            try:
                # Try to run the geolocation setting
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # If we're in an async context, we need to handle this differently
                    # For now, just ensure the initial context setting was applied
                    log_geolocation_debug("Geolocation was set during context creation")
                else:
                    loop.run_until_complete(self.context.set_geolocation(us_location))
                    log_geolocation_debug("US geolocation successfully applied")
            except RuntimeError:
                # If we can't set it due to event loop issues, the context creation setting should suffice
                log_geolocation_debug("Using geolocation from context creation")

            # Add extra JavaScript to ensure location is properly detected
            if self.page:
                self.page.add_init_script(f"""
                    // Override geolocation for Amazon compatibility
                    Object.defineProperty(navigator.geolocation, 'getCurrentPosition', {{
                        value: function(success, error, options) {{
                            const position = {{
                                coords: {{
                                    latitude: {us_location['latitude']},
                                    longitude: {us_location['longitude']},
                                    accuracy: 10,
                                    altitude: null,
                                    altitudeAccuracy: null,
                                    heading: null,
                                    speed: null
                                }},
                                timestamp: Date.now()
                            }};
                            if (success) success(position);
                        }}
                    }});
                """)
                log_geolocation_debug("Added geolocation override script")

        except Exception as e:
            log_geolocation_error(f"Error setting US geolocation: {e}")

    def set_amazon_us_location(self, page: Page):
        """Set Amazon delivery location to US to ensure proper product availability."""
        try:
            log_geolocation_info("Setting Amazon delivery location to US...")

            # Navigate to Amazon and set location
            current_url = page.url if page.url else ""

            # If we're already on Amazon, try to set the delivery location
            if "amazon.com" in current_url:
                try:
                    # Look for location selector and set to US zip code
                    log_geolocation_debug("Looking for Amazon location selector...")

                    # Try to find the delivery location element
                    location_selectors = [
                        '#nav-global-location-popover-link',
                        '[data-id="glow-ingress-block"]',
                        '#glow-ingress-block',
                        '.nav-line-2'
                    ]

                    for selector in location_selectors:
                        try:
                            if page.locator(selector).is_visible(timeout=2000):
                                log_geolocation_debug(f"Found location selector: {selector}")
                                page.locator(selector).click(timeout=5000)
                                page.wait_for_timeout(1000)

                                # Try to set a US zip code
                                zip_selectors = [
                                    '#GLUXZipUpdateInput',
                                    '#GLUXZipUpdate',
                                    'input[name="zipCode"]',
                                    'input[placeholder*="zip"]'
                                ]

                                for zip_selector in zip_selectors:
                                    try:
                                        if page.locator(zip_selector).is_visible(timeout=2000):
                                            log_geolocation_debug(f"Found zip input: {zip_selector}")
                                            page.locator(zip_selector).fill("10001")  # NYC zip code
                                            page.wait_for_timeout(500)

                                            # Submit the location change
                                            submit_selectors = [
                                                '#GLUXZipUpdate-announce',
                                                'button[aria-label*="apply"]',
                                                'input[type="submit"]',
                                                '.a-button-primary'
                                            ]

                                            for submit_selector in submit_selectors:
                                                try:
                                                    if page.locator(submit_selector).is_visible(timeout=2000):
                                                        log_geolocation_debug(f"Clicking submit: {submit_selector}")
                                                        page.locator(submit_selector).click(timeout=3000)
                                                        page.wait_for_timeout(2000)
                                                        log_geolocation_info("Amazon location updated to US (10001)")
                                                        return
                                                except:
                                                    continue

                                            # Try pressing Enter as fallback
                                            page.locator(zip_selector).press("Enter")
                                            page.wait_for_timeout(2000)
                                            log_geolocation_info("Amazon location updated via Enter key")
                                            return
                                    except:
                                        continue
                                break
                        except:
                            continue

                except Exception as e:
                    log_geolocation_warning(f"Could not set Amazon location via UI: {e}")

            # Alternative: Set location via cookies/localStorage
            log_geolocation_debug("Setting Amazon location via browser storage...")
            page.evaluate("""
                // Set Amazon location preferences in localStorage
                try {
                    localStorage.setItem('amazon-location', JSON.stringify({
                        zipCode: '10001',
                        city: 'New York',
                        state: 'NY',
                        country: 'US'
                    }));

                    // Set location in session storage as well
                    sessionStorage.setItem('amazon-delivery-location', '10001');

                    console.log('Amazon location preferences set via storage');
                } catch (e) {
                    console.log('Could not set location via storage:', e);
                }
            """)

        except Exception as e:
            log_geolocation_error(f"Error setting Amazon US location: {e}")

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
