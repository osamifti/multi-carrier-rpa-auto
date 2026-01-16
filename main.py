"""
FastAPI server with Selenium WebDriver bot.
Opens The Zebra insurance website and keeps the browser session active.
"""

from fastapi import FastAPI
from pydantic import BaseModel
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import StaleElementReferenceException
from typing import Optional
import uvicorn
import time
import logging
import random

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Selenium Bot API")

# Global variable to store the browser instance
driver: Optional[uc.Chrome] = None


def human_delay(min_seconds: float = 0.2, max_seconds: float = 0.8):
    """
    Add a random human-like delay between actions.
    
    Args:
        min_seconds: Minimum delay in seconds
        max_seconds: Maximum delay in seconds
    """
    delay = random.uniform(min_seconds, max_seconds)
    time.sleep(delay)


def human_scroll(driver_instance, scroll_pause: float = 0.5):
    """
    Perform human-like scrolling on the page.
    
    Args:
        driver_instance: The WebDriver instance
        scroll_pause: Pause between scrolls
    """
    try:
        # Scroll down a bit
        driver_instance.execute_script("window.scrollBy(0, 300);")
        human_delay(0.2, 0.4)
        # Scroll back up a bit
        driver_instance.execute_script("window.scrollBy(0, -100);")
        human_delay(0.1, 0.3)
    except Exception:
        pass


def human_mouse_move(driver_instance, element):
    """
    Move mouse to element in a human-like way with curved path.
    
    Args:
        driver_instance: The WebDriver instance
        element: The element to move to
    """
    try:
        # Use ActionChains with move_to_element for reliability
        # Add some random small movements first to appear more human
        actions = ActionChains(driver_instance)
        
        # Sometimes add a small random movement before moving to element
        if random.random() > 0.3:
            small_offset_x = random.randint(-10, 10)
            small_offset_y = random.randint(-10, 10)
            actions.move_by_offset(small_offset_x, small_offset_y)
            time.sleep(random.uniform(0.05, 0.15))
        
        # Move to element with slight pause
        actions.move_to_element(element)
        actions.pause(random.uniform(0.1, 0.3))
        actions.perform()
        human_delay(0.2, 0.5)
    except Exception:
        # Fallback to simple movement
        try:
            actions = ActionChains(driver_instance)
            actions.move_to_element(element)
            actions.perform()
            human_delay(0.2, 0.5)
        except Exception:
            pass


def random_page_interaction(driver_instance):
    """
    Perform random human-like page interactions to appear more natural.
    
    Args:
        driver_instance: The WebDriver instance
    """
    try:
        # Random scroll
        scroll_amount = random.randint(100, 400)
        driver_instance.execute_script(f"window.scrollBy(0, {scroll_amount});")
        human_delay(0.2, 0.5)
        
        # Sometimes scroll back a bit
        if random.random() > 0.5:
            scroll_back = random.randint(50, 150)
            driver_instance.execute_script(f"window.scrollBy(0, -{scroll_back});")
            human_delay(0.2, 0.4)
    except Exception:
        pass


def select_custom_dropdown(driver_instance, wait_instance, data_cy_value, value_to_select, field_name):
    """
    Select a value from a custom React Select dropdown.
    
    Args:
        driver_instance: The WebDriver instance
        wait_instance: WebDriverWait instance
        data_cy_value: The data-cy attribute value of the dropdown input
        value_to_select: The value to select from the dropdown
        field_name: Name of the field for logging
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        logger.info(f"Selecting {field_name}: {value_to_select}")
        
        # Find the dropdown input first
        dropdown_input = wait_instance.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, f'[data-cy="{data_cy_value}"]'))
        )
        
        # Find the parent control container to click on
        try:
            # Get the parent control container
            control_container = dropdown_input.find_element(By.XPATH, "./ancestor::div[contains(@class, 'custom-dropdown__control')]")
        except Exception:
            # Fallback: try to find control by searching from input
            control_container = driver_instance.find_element(By.XPATH, f"//input[@data-cy='{data_cy_value}']/ancestor::div[contains(@class, 'custom-dropdown__control')]")
        
        # Scroll to dropdown control
        driver_instance.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", control_container)
        human_delay(0.3, 0.6)
        human_mouse_move(driver_instance, control_container)
        human_delay(0.2, 0.4)
        
        # Click on the control container to open dropdown (not the input directly)
        try:
            control_container.click()
        except Exception:
            # If click fails, use JavaScript click
            driver_instance.execute_script("arguments[0].click();", control_container)
        
        human_delay(0.5, 1.0)  # Wait for dropdown to open
        
        # Now find and interact with the input field
        dropdown_input = wait_instance.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, f'[data-cy="{data_cy_value}"]'))
        )
        
        # Clear and type the value to search
        try:
            dropdown_input.clear()
        except Exception:
            # If clear fails, select all and delete
            dropdown_input.send_keys(Keys.CONTROL + "a")
            dropdown_input.send_keys(Keys.DELETE)
        
        human_delay(0.2, 0.4)
        
        # Type the value character by character
        for char in str(value_to_select):
            try:
                dropdown_input.send_keys(char)
            except StaleElementReferenceException:
                # Re-find input if stale
                dropdown_input = driver_instance.find_element(By.CSS_SELECTOR, f'[data-cy="{data_cy_value}"]')
                dropdown_input.send_keys(char)
            time.sleep(random.uniform(0.05, 0.12))
        
        human_delay(0.8, 1.5)  # Wait for dropdown options to appear and filter
        
        # Press Enter to auto-select the first option
        try:
            dropdown_input.send_keys(Keys.RETURN)
            logger.info(f"{field_name} '{value_to_select}' selected successfully using Enter key")
            human_delay(0.5, 1.0)
            return True
        except StaleElementReferenceException:
            # Re-find input if stale and try again
            try:
                dropdown_input = driver_instance.find_element(By.CSS_SELECTOR, f'[data-cy="{data_cy_value}"]')
                dropdown_input.send_keys(Keys.RETURN)
                logger.info(f"{field_name} '{value_to_select}' selected successfully using Enter key")
                human_delay(0.5, 1.0)
                return True
            except Exception as e:
                logger.error(f"Failed to select {field_name} '{value_to_select}': {str(e)}")
                return False
        except Exception as e:
            logger.error(f"Failed to select {field_name} '{value_to_select}': {str(e)}")
            return False
        
    except Exception as e:
        logger.error(f"Error selecting {field_name}: {str(e)}")
        return False


class StartRequest(BaseModel):
    """Request model for the start endpoint."""
    year: Optional[str] = None
    make: Optional[str] = None
    model: Optional[str] = None


@app.post("/start")
async def start_bot(request: StartRequest):
    """
    Start the Selenium bot and open The Zebra insurance website.
    
    Args:
        request: StartRequest containing vehicle details
        
    Returns:
        dict: Status message and browser info
    """
    global driver
    
    # Hardcoded headless setting
    headless = True
    

    try:
        logger.info(f"Starting bot with headless={headless}")
        
        # Close existing browser if any
        if driver is not None:
            logger.info("Closing existing browser instance")
            try:
                driver.quit()
            except Exception:
                pass
        
        # Initialize undetected Chrome driver (specifically designed to bypass bot detection)
        logger.info("Initializing undetected Chrome driver for maximum stealth")
        try:
            # Configure options for undetected-chromedriver
            options = uc.ChromeOptions()
            
            if headless:
                options.add_argument("--headless=new")  # Use new headless mode
                options.add_argument("--disable-gpu")
                options.add_argument("--disable-software-rasterizer")
                options.add_argument("--disable-extensions")
                logger.info("Headless mode enabled")
            
            # Additional stealth options
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--start-maximized")
            options.add_argument("--disable-infobars")
            options.add_argument("--disable-web-security")
            options.add_argument("--disable-features=IsolateOrigins,site-per-process")
            options.add_argument("--disable-site-isolation-trials")
            options.add_argument("--disable-background-timer-throttling")
            options.add_argument("--disable-backgrounding-occluded-windows")
            options.add_argument("--disable-renderer-backgrounding")
            options.add_argument("--disable-features=TranslateUI")
            options.add_argument("--disable-ipc-flooding-protection")
            
            # Additional preferences
            prefs = {
                "credentials_enable_service": False,
                "profile.password_manager_enabled": False,
                "profile.default_content_setting_values.notifications": 2
                
            }
            options.add_experimental_option("prefs", prefs)
            
            # Initialize undetected Chrome driver
            # version_main can be set to match your Chrome version, or leave None for auto-detection
            # In Docker/headless environments, specify Chrome binary path
            import os
            chrome_binary_path = None
            if os.path.exists("/usr/bin/google-chrome"):
                chrome_binary_path = "/usr/bin/google-chrome"
            elif os.path.exists("/usr/bin/google-chrome-stable"):
                chrome_binary_path = "/usr/bin/google-chrome-stable"
            elif os.path.exists("/usr/bin/chromium"):
                chrome_binary_path = "/usr/bin/chromium"
            elif os.path.exists("/usr/bin/chromium-browser"):
                chrome_binary_path = "/usr/bin/chromium-browser"
            
            if chrome_binary_path:
                options.binary_location = chrome_binary_path
                logger.info(f"Using Chrome binary at: {chrome_binary_path}")
            
            driver = uc.Chrome(
                options=options,
                version_main=None,  # Auto-detect Chrome version
                use_subprocess=True,  # Use subprocess for better isolation
                driver_executable_path=None  # Auto-download chromedriver
            )
            logger.info("Undetected Chrome driver initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize undetected Chrome driver: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to initialize Chrome driver: {str(e)}",
                "error_type": type(e).__name__,
                "suggestion": "Make sure Google Chrome is installed. undetected-chromedriver will auto-download the matching ChromeDriver."
            }
        
        # Additional stealth scripts for extra protection
        logger.info("Applying additional stealth techniques")
        
        # Enhanced anti-detection for headless mode
        if headless:
            # Override navigator.webdriver property
            driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                '''
            })
            
            # Override Chrome runtime
            driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    window.navigator.chrome = {
                        runtime: {},
                        loadTimes: function() {},
                        csi: function() {},
                        app: {}
                    };
                '''
            })
            
            # Override permissions
            driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    const originalQuery = window.navigator.permissions.query;
                    window.navigator.permissions.query = (parameters) => (
                        parameters.name === 'notifications' ?
                            Promise.resolve({ state: Notification.permission }) :
                            originalQuery(parameters)
                    );
                '''
            })
        
        # Enhanced fingerprinting protection
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': '''
                // Remove webdriver property
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                
                // Additional fingerprinting protection
                Object.defineProperty(navigator, 'hardwareConcurrency', {
                    get: () => 8
                });
                Object.defineProperty(navigator, 'deviceMemory', {
                    get: () => 8
                });
                
                // Override plugins
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });
                
                // Override languages
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en']
                });
                
                // Canvas fingerprinting protection
                const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
                HTMLCanvasElement.prototype.toDataURL = function(type) {
                    const context = this.getContext('2d');
                    if (context) {
                        const imageData = context.getImageData(0, 0, this.width, this.height);
                        for (let i = 0; i < imageData.data.length; i += 4) {
                            imageData.data[i] += Math.floor(Math.random() * 3) - 1;
                        }
                        context.putImageData(imageData, 0, 0);
                    }
                    return originalToDataURL.apply(this, arguments);
                };
                
                // WebGL fingerprinting protection
                const getParameter = WebGLRenderingContext.prototype.getParameter;
                WebGLRenderingContext.prototype.getParameter = function(parameter) {
                    if (parameter === 37445) {
                        return 'Intel Inc.';
                    }
                    if (parameter === 37446) {
                        return 'Intel Iris OpenGL Engine';
                    }
                    return getParameter.apply(this, arguments);
                };
                
                // Override headless detection
                Object.defineProperty(navigator, 'maxTouchPoints', {
                    get: () => 0
                });
            '''
        })
        
        # Set user agent override
        driver.execute_cdp_cmd('Network.setUserAgentOverride', {
            "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        })
        
        # Set device metrics to appear as a real window
        if headless:
            driver.execute_cdp_cmd('Emulation.setDeviceMetricsOverride', {
                "width": 1920,
                "height": 1080,
                "deviceScaleFactor": 1,
                "mobile": False
            })
        
        # Navigate to the website AFTER stealth scripts are set up
        url = "https://www.thezebra.com/insurance/car/prefill/start/"
        logger.info(f"Navigating to URL: {url}")
        driver.get(url)
        logger.info("Page navigation initiated")
        
        # Wait for page to load
        logger.info("Waiting for page to load")
        wait = WebDriverWait(driver, 30)
        
        # Wait for the page to be fully loaded
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        logger.info("Page body loaded")
        
        # In headless mode, wait longer for dynamic content to load
        if headless:
            logger.info("Headless mode detected - waiting longer for dynamic content")
            # Wait for page to be fully interactive
            try:
                wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
                logger.info("Page readyState = complete")
            except Exception:
                logger.warning("Could not verify readyState")
            
            # Wait for React/JS to initialize
            try:
                wait.until(lambda d: d.execute_script("return typeof window !== 'undefined' && typeof document !== 'undefined'"))
                logger.info("Window and document objects available")
            except Exception:
                pass
            
            # Wait for any loading indicators to disappear
            human_delay(5.0, 8.0)  # Longer wait in headless mode for JS to execute
            
            # Simulate some page interaction even in headless
            try:
                driver.execute_script("window.scrollTo(0, 100);")
                human_delay(0.5, 1.0)
                driver.execute_script("window.scrollTo(0, 0);")
                human_delay(0.5, 1.0)
            except Exception:
                pass
        else:
            # Human-like behavior: page interaction to appear natural
            logger.info("Performing human-like page interaction")
            random_page_interaction(driver)
            human_delay(0.8, 1.5)  # Faster human-like reading time
            human_scroll(driver)
            human_delay(0.5, 1.0)
        
        logger.info("Additional wait completed for dynamic content")
        
        # Find and click the "I want to compare my current insurance" button
        logger.info("Looking for 'I want to compare my current insurance' button")
        
        # Wait for the page to be interactive before looking for buttons
        try:
            wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
            logger.info("Page is fully loaded (readyState = complete)")
        except Exception:
            logger.warning("Could not verify page readyState, continuing anyway")
        
        # Wait for React components to be mounted
        try:
            # Wait for common React indicators
            wait.until(lambda d: d.execute_script("""
                return document.querySelectorAll('[data-cy], [class*="radio"], button, input').length > 0;
            """))
            logger.info("Interactive elements detected on page")
        except Exception:
            logger.warning("Could not detect interactive elements, continuing anyway")
        
        # Additional wait for React components to render
        human_delay(2.0, 3.0) if headless else human_delay(1.0, 2.0)
        
        # Try multiple methods to find and click the button
        button_clicked = False
        button_wait_timeout = 60 if headless else 30
        button_wait = WebDriverWait(driver, button_wait_timeout)
        
        # Method 1: Try to find by data-cy attribute
        logger.info("Method 1: Trying to find button by data-cy attribute")
        try:
            button = button_wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-cy="radio-text-help_today-compare_current"]'))
            )
            logger.info("Button found by data-cy attribute")
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", button)
            human_delay(0.5, 1.0)
            try:
                button.click()
            except Exception:
                driver.execute_script("arguments[0].click();", button)
            logger.info("Button clicked successfully (method 1)")
            button_clicked = True
            human_delay(0.5, 1.0)
        except Exception as e:
            logger.warning(f"Method 1 failed: {str(e)}")
        
        # Method 2: Try to find by text content (XPath)
        if not button_clicked:
            logger.info("Method 2: Trying to find button by text content (XPath)")
            try:
                button = button_wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'I want to compare my current insurance')]"))
                )
                logger.info("Button found by text content (XPath)")
                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", button)
                human_delay(0.5, 1.0)
                try:
                    button.click()
                except Exception:
                    driver.execute_script("arguments[0].click();", button)
                logger.info("Button clicked successfully (method 2)")
                button_clicked = True
                human_delay(0.5, 1.0)
            except Exception as e:
                logger.warning(f"Method 2 failed: {str(e)}")
        
        # Method 3: Try JavaScript-based finding and clicking
        if not button_clicked:
            logger.info("Method 3: Trying to find button using JavaScript")
            try:
                # Use JavaScript to find the element
                button_found = driver.execute_script("""
                    var elements = document.querySelectorAll('[data-cy="radio-text-help_today-compare_current"]');
                    if (elements.length === 0) {
                        elements = Array.from(document.querySelectorAll('div')).filter(el => 
                            el.textContent && el.textContent.includes('I want to compare my current insurance')
                        );
                    }
                    if (elements.length > 0) {
                        elements[0].scrollIntoView({behavior: 'smooth', block: 'center'});
                        return true;
                    }
                    return false;
                """)
                
                if button_found:
                    human_delay(1.0, 2.0)
                    # Try to click using JavaScript
                    clicked = driver.execute_script("""
                        var elements = document.querySelectorAll('[data-cy="radio-text-help_today-compare_current"]');
                        if (elements.length === 0) {
                            elements = Array.from(document.querySelectorAll('div')).filter(el => 
                                el.textContent && el.textContent.includes('I want to compare my current insurance')
                            );
                        }
                        if (elements.length > 0) {
                            elements[0].click();
                            return true;
                        }
                        return false;
                    """)
                    if clicked:
                        logger.info("Button clicked successfully (method 3 - JavaScript)")
                        button_clicked = True
                        human_delay(0.5, 1.0)
            except Exception as e:
                logger.warning(f"Method 3 failed: {str(e)}")
        
        # Method 4: Try finding by partial text match
        if not button_clicked:
            logger.info("Method 4: Trying to find button by partial text match")
            try:
                button = button_wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//div[contains(., 'compare my current insurance')]"))
                )
                logger.info("Button found by partial text")
                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", button)
                human_delay(0.5, 1.0)
                try:
                    button.click()
                except Exception:
                    driver.execute_script("arguments[0].click();", button)
                logger.info("Button clicked successfully (method 4)")
                button_clicked = True
                human_delay(0.5, 1.0)
            except Exception as e:
                logger.warning(f"Method 4 failed: {str(e)}")
        
        if not button_clicked:
            error_msg = "Failed to find or click the button after trying all methods"
            logger.error(error_msg)
            return {
                "status": "error",
                "message": error_msg,
                "error_type": "ElementNotFoundError"
            }
        
        # Human-like wait after clicking
        logger.info("Waiting for page to process the click")
        human_delay(0.8, 1.5)  # Faster wait
        logger.info(f"Step 1 completed. Current URL: {driver.current_url}")
        
        # Step 2: Click the "Other" button for residence ownership
        logger.info("Step 2: Looking for 'Other' residence ownership button")
        try:
            logger.info("Trying to find button by data-cy attribute: radio-text-residence_ownership-0-3")
            button_step2 = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-cy="radio-text-residence_ownership-0-3"]'))
            )
            logger.info("Step 2 button found")
            
            # Human-like behavior: scroll to element and move mouse
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", button_step2)
            human_delay(0.4, 0.8)  # Faster wait after scroll
            human_mouse_move(driver, button_step2)
            human_delay(0.3, 0.6)  # Faster hesitation before click
            
            logger.info("Clicking Step 2 button...")
            button_step2.click()
            logger.info("Step 2 button clicked successfully")
            
            # Wait after click
            human_delay(0.5, 1.0)
            logger.info(f"Step 2 completed. Current URL: {driver.current_url}")
        except Exception as e:
            logger.error(f"Step 2 failed: Failed to find or click the 'Other' button: {str(e)}")
            return {
                "status": "error",
                "message": f"Step 2 failed: Failed to find or click the 'Other' button: {str(e)}",
                "error_type": type(e).__name__
            }
        
        # Step 3: Click the "Sometime in the future" button for purchase timeframe
        logger.info("Step 3: Looking for 'Sometime in the future' purchase timeframe button")
        try:
            logger.info("Trying to find button by data-cy attribute: radio-text-user_purchase_timeframe-0-FUTURE")
            button_step3 = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-cy="radio-text-user_purchase_timeframe-0-FUTURE"]'))
            )
            logger.info("Step 3 button found")
            
            # Human-like behavior: scroll to element and move mouse
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", button_step3)
            human_delay(0.4, 0.8)  # Faster wait after scroll
            human_mouse_move(driver, button_step3)
            human_delay(0.3, 0.6)  # Faster hesitation before click
            
            logger.info("Clicking Step 3 button...")
            button_step3.click()
            logger.info("Step 3 button clicked successfully")
            
            # Wait after click
            human_delay(0.5, 1.0)
            logger.info(f"Step 3 completed. Current URL: {driver.current_url}")
        except Exception as e:
            logger.error(f"Step 3 failed: Failed to find or click the 'Sometime in the future' button: {str(e)}")
            return {
                "status": "error",
                "message": f"Step 3 failed: Failed to find or click the 'Sometime in the future' button: {str(e)}",
                "error_type": type(e).__name__
            }
        
        # Step 4: Click the "Save & continue" button and wait for new page
        logger.info("Step 4: Looking for 'Save & continue' button")
        try:
            logger.info("Trying to find button by data-cy attribute: primary-button_section-continue")
            
            # Human-like scroll before looking for button
            human_scroll(driver)
            human_delay(0.5, 1.0)
            
            # Wait for button to be present first
            button_step4 = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[data-cy="primary-button_section-continue"]'))
            )
            logger.info("Step 4 button found, waiting for it to be enabled...")
            
            # Wait for button to be enabled (not disabled) with faster checking
            max_wait_time = 10  # 10 seconds to wait for button to enable
            start_time = time.time()
            while time.time() - start_time < max_wait_time:
                try:
                    disabled_attr = button_step4.get_attribute("disabled")
                    if disabled_attr is None:
                        logger.info("Step 4 button is now enabled")
                        break
                    human_delay(0.5, 1.0)  # Faster check intervals
                    button_step4 = driver.find_element(By.CSS_SELECTOR, '[data-cy="primary-button_section-continue"]')
                except Exception:
                    pass
            else:
                logger.warning("Button may still be disabled, but attempting to click anyway")
            
            # Get the button element again to ensure it's clickable
            button_step4 = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-cy="primary-button_section-continue"]'))
            )
            
            # Human-like behavior: scroll to button and move mouse
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", button_step4)
            human_delay(0.5, 1.0)  # Faster wait after scroll
            human_mouse_move(driver, button_step4)
            human_delay(0.4, 0.8)  # Faster pause before clicking
            
            # Store current URL before clicking
            url_before_click = driver.current_url
            logger.info("Clicking Step 4 button...")
            button_step4.click()
            logger.info("Step 4 button clicked successfully")
            
            # Wait for page to change (new page to load)
            logger.info("Waiting for new page to load after clicking 'Save & continue'")
            wait.until(lambda d: d.current_url != url_before_click)
            logger.info("New page loaded")
            
            # Wait for page to fully render
            human_delay(1.0, 1.5)
            logger.info(f"Step 4 completed. New page URL: {driver.current_url}")
        except Exception as e:
            logger.error(f"Step 4 failed: Failed to find, enable, or click the 'Save & continue' button: {str(e)}")
            return {
                "status": "error",
                "message": f"Step 4 failed: Failed to find, enable, or click the 'Save & continue' button: {str(e)}",
                "error_type": type(e).__name__
            }
        
        # Step 5: Fill the garaging address field
        logger.info("Step 5: Looking for garaging address input field")
        try:
            logger.info("Trying to find input field by data-cy attribute: textinput-input-garaging_address")
            
            # Wait for the page to be ready and find the input field
            address_input = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[data-cy="textinput-input-garaging_address"]'))
            )
            logger.info("Address input field found")
            
            # Human-like behavior: scroll to input field
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", address_input)
            human_delay(0.4, 0.8)
            
            # Move mouse to input field
            human_mouse_move(driver, address_input)
            human_delay(0.3, 0.6)
            
            # Helper function to get fresh element reference
            def get_address_input():
                return driver.find_element(By.CSS_SELECTOR, '[data-cy="textinput-input-garaging_address"]')
            
            # Click on the input field to focus it
            logger.info("Clicking on address input field...")
            try:
                address_input.click()
            except StaleElementReferenceException:
                # Re-find element if stale
                logger.info("Element became stale, re-finding...")
                address_input = get_address_input()
                address_input.click()
            human_delay(0.3, 0.6)
            
            # Clear the field if it has any value
            try:
                address_input.clear()
            except StaleElementReferenceException:
                # Re-find element if stale
                logger.info("Element became stale, re-finding...")
                address_input = get_address_input()
                address_input.clear()
            human_delay(0.2, 0.4)
            
            # Type the address with faster human-like typing speed
            address = "3740 LAKE LYNN DR"
            logger.info(f"Typing address: {address}")
            
            # Type character by character with faster random delays
            # Re-find element before typing to avoid stale reference
            address_input = get_address_input()
            for i, char in enumerate(address):
                try:
                    address_input.send_keys(char)
                except StaleElementReferenceException:
                    # Re-find element if it becomes stale during typing
                    logger.debug("Element became stale during typing, re-finding...")
                    address_input = get_address_input()
                    address_input.send_keys(char)
                time.sleep(random.uniform(0.02, 0.08))  # Faster typing speed
                
                # After typing a few characters, check if dropdown appears (but don't select yet)
                if i > 5 and i % 3 == 0:  # Check every 3 chars after first 5
                    try:
                        # Just check if dropdown exists, don't interact yet
                        driver.find_element(By.CSS_SELECTOR, '#ex-list-box, [id="ex-list-box"], ul[role="listbox"]')
                        logger.debug("Dropdown is appearing while typing...")
                    except Exception:
                        pass  # Dropdown not ready yet, continue typing
            
            logger.info("Address typed successfully")
            human_delay(0.8, 1.5)  # Wait a bit longer for dropdown to fully appear
            
            # Wait for dropdown to appear and select first option
            logger.info("Waiting for address dropdown to appear...")
            dropdown_option = None
            
            # Try multiple selectors to find the first dropdown option
            # Prioritize the specific address suggestion element
            selectors = [
                (By.CSS_SELECTOR, '#address-suggestion-0'),  # Specific ID
                (By.CSS_SELECTOR, '.address-suggestion.suggestion-selected'),  # Class combination
                (By.CSS_SELECTOR, '[id="address-suggestion-0"]'),  # ID attribute selector
                (By.CSS_SELECTOR, '[role="option"][id="address-suggestion-0"]'),  # Role and ID
                (By.XPATH, "//div[@id='address-suggestion-0']"),  # XPath by ID
                (By.XPATH, "//div[@class='address-suggestion suggestion-selected']"),  # XPath by class
                (By.XPATH, "//div[@role='option' and @id='address-suggestion-0']"),  # XPath by role and ID
                (By.CSS_SELECTOR, '#ex-list-box li:first-child'),  # Fallback to first list item
                (By.CSS_SELECTOR, '[id="ex-list-box"] li:first-child'),
                (By.CSS_SELECTOR, 'ul[role="listbox"] li:first-child'),
                (By.CSS_SELECTOR, '.autocomplete-option:first-child'),
                (By.XPATH, "//ul[@role='listbox']//li[1]"),
                (By.XPATH, "//div[@id='ex-list-box']//li[1]"),
                (By.XPATH, "//li[@role='option'][1]"),
                (By.XPATH, "//ul[contains(@class, 'autocomplete')]//li[1]"),
            ]
            
            for selector_type, selector in selectors:
                try:
                    logger.info(f"Trying selector: {selector}")
                    dropdown_option = wait.until(
                        EC.element_to_be_clickable((selector_type, selector))
                    )
                    logger.info(f"Dropdown option found with selector: {selector}")
                    break
                except Exception as e:
                    logger.debug(f"Selector {selector} failed: {str(e)}")
                    continue
            
            if dropdown_option is None:
                logger.error("Could not find dropdown option with any selector")
                return {
                    "status": "error",
                    "message": "Step 5 failed: Dropdown did not appear or could not find first option",
                    "error_type": "ElementNotFound"
                }
            
            # Select the first option
            logger.info("Selecting first option from dropdown...")
            try:
                # Scroll to the option if needed
                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", dropdown_option)
                human_delay(0.3, 0.6)
                
                # Move mouse to option and click
                human_mouse_move(driver, dropdown_option)
                human_delay(0.2, 0.4)
                
                dropdown_option.click()
                logger.info("First dropdown option selected successfully")
            except StaleElementReferenceException:
                # Re-find and click if element becomes stale
                logger.info("Dropdown option became stale, re-finding...")
                # Try the specific address-suggestion-0 first
                try:
                    dropdown_option = driver.find_element(By.CSS_SELECTOR, '#address-suggestion-0')
                    dropdown_option.click()
                    logger.info("First dropdown option selected successfully after re-finding")
                except Exception:
                    # Fallback to other selectors
                    for selector_type, selector in selectors:
                        try:
                            dropdown_option = driver.find_element(selector_type, selector)
                            dropdown_option.click()
                            logger.info("First dropdown option selected successfully after re-finding")
                            break
                        except Exception:
                            continue
            
            # Wait for the selection to be processed
            human_delay(0.8, 1.5)
            logger.info(f"Step 5 completed. Current URL: {driver.current_url}")
            
        except Exception as e:
            logger.error(f"Step 5 failed: Failed to find or fill the address field: {str(e)}")
            return {
                "status": "error",
                "message": f"Step 5 failed: Failed to find or fill the address field: {str(e)}",
                "error_type": type(e).__name__
            }
        
        # Step 6: Fill first name, last name, date of birth, and click Save & continue
        logger.info("Step 6: Filling personal information fields")
        try:
            # Helper function to get fresh element reference
            def get_element_by_data_cy(data_cy_value):
                return driver.find_element(By.CSS_SELECTOR, f'[data-cy="{data_cy_value}"]')
            
            # Fill first name
            logger.info("Filling first name field with 'moazam'")
            try:
                first_name_input = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '[data-cy="textinput-input-first_name-0"]'))
                )
                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", first_name_input)
                human_delay(0.3, 0.6)
                human_mouse_move(driver, first_name_input)
                human_delay(0.2, 0.4)
                first_name_input.click()
                human_delay(0.2, 0.4)
                first_name_input.clear()
                human_delay(0.1, 0.3)
                
                # Type first name
                first_name = "moazam"
                for char in first_name:
                    try:
                        first_name_input.send_keys(char)
                    except StaleElementReferenceException:
                        first_name_input = get_element_by_data_cy("textinput-input-first_name-0")
                        first_name_input.send_keys(char)
                    time.sleep(random.uniform(0.02, 0.08))
                logger.info("First name filled successfully")
                human_delay(0.3, 0.6)
                
            except Exception as e:
                logger.error(f"Failed to fill first name: {str(e)}")
                return {
                    "status": "error",
                    "message": f"Step 6 failed: Could not fill first name: {str(e)}",
                    "error_type": type(e).__name__
                }
            
            # Fill last name
            logger.info("Filling last name field with 'ali'")
            try:
                last_name_input = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '[data-cy="textinput-input-last_name-0"]'))
                )
                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", last_name_input)
                human_delay(0.3, 0.6)
                human_mouse_move(driver, last_name_input)
                human_delay(0.2, 0.4)
                last_name_input.click()
                human_delay(0.2, 0.4)
                last_name_input.clear()
                human_delay(0.1, 0.3)
                
                # Type last name
                last_name = "ali"
                for char in last_name:
                    try:
                        last_name_input.send_keys(char)
                    except StaleElementReferenceException:
                        last_name_input = get_element_by_data_cy("textinput-input-last_name-0")
                        last_name_input.send_keys(char)
                    time.sleep(random.uniform(0.02, 0.08))
                logger.info("Last name filled successfully")
                human_delay(0.3, 0.6)
                
            except Exception as e:
                logger.error(f"Failed to fill last name: {str(e)}")
                return {
                    "status": "error",
                    "message": f"Step 6 failed: Could not fill last name: {str(e)}",
                    "error_type": type(e).__name__
                }
            
            # Fill date of birth (just numbers: 11112000)
            logger.info("Filling date of birth field with '11112000'")
            try:
                dob_input = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '[data-cy="textinput-input-date_of_birth-0"]'))
                )
                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", dob_input)
                human_delay(0.3, 0.6)
                human_mouse_move(driver, dob_input)
                human_delay(0.2, 0.4)
                dob_input.click()
                human_delay(0.2, 0.4)
                dob_input.clear()
                human_delay(0.1, 0.3)
                
                # Type date of birth (just numbers, website will format it)
                date_of_birth = "11112000"
                for char in date_of_birth:
                    try:
                        dob_input.send_keys(char)
                    except StaleElementReferenceException:
                        dob_input = get_element_by_data_cy("textinput-input-date_of_birth-0")
                        dob_input.send_keys(char)
                    time.sleep(random.uniform(0.02, 0.08))
                logger.info("Date of birth filled successfully")
                human_delay(0.5, 1.0)
                
            except Exception as e:
                logger.error(f"Failed to fill date of birth: {str(e)}")
                return {
                    "status": "error",
                    "message": f"Step 6 failed: Could not fill date of birth: {str(e)}",
                    "error_type": type(e).__name__
                }
            
            # Click Save & continue button
            logger.info("Step 6: Looking for 'Save & continue' button")
            try:
                logger.info("Trying to find button by data-cy attribute: primary-button_section-continue")
                
                # Wait for button to be present and enabled
                button_step6 = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '[data-cy="primary-button_section-continue"]'))
                )
                logger.info("Step 6 button found, waiting for it to be enabled...")
                
                # Wait for button to be enabled
                max_wait_time = 10
                start_time = time.time()
                while time.time() - start_time < max_wait_time:
                    try:
                        disabled_attr = button_step6.get_attribute("disabled")
                        if disabled_attr is None:
                            logger.info("Step 6 button is now enabled")
                            break
                        human_delay(0.5, 1.0)
                        button_step6 = driver.find_element(By.CSS_SELECTOR, '[data-cy="primary-button_section-continue"]')
                    except Exception:
                        pass
                
                # Get the button element again to ensure it's clickable
                button_step6 = wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-cy="primary-button_section-continue"]'))
                )
                
                # Human-like behavior: scroll to button and move mouse
                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", button_step6)
                human_delay(0.5, 1.0)
                human_mouse_move(driver, button_step6)
                human_delay(0.4, 0.8)
                
                # Store current URL before clicking
                url_before_click = driver.current_url
                logger.info("Clicking Step 6 button...")
                button_step6.click()
                logger.info("Step 6 button clicked successfully")
                
                # Wait for page to change (new page to load)
                logger.info("Waiting for new page to load after clicking 'Save & continue'")
                wait.until(lambda d: d.current_url != url_before_click)
                logger.info("New page loaded")
                
                # Wait for page to fully render
                human_delay(1.0, 1.5)
                logger.info(f"Step 6 completed. New page URL: {driver.current_url}")
                
            except Exception as e:
                logger.error(f"Step 6 failed: Failed to find, enable, or click the 'Save & continue' button: {str(e)}")
                return {
                    "status": "error",
                    "message": f"Step 6 failed: Failed to find, enable, or click the 'Save & continue' button: {str(e)}",
                    "error_type": type(e).__name__
                }
            
        except Exception as e:
            logger.error(f"Step 6 failed: {str(e)}")
            return {
                "status": "error",
                "message": f"Step 6 failed: {str(e)}",
                "error_type": type(e).__name__
            }
        
        # Step 7: Select vehicle information (year, make, model, trim)
        if request.year and request.make and request.model:
            logger.info("Step 7: Selecting vehicle information")
            try:
                # Select year
                if not select_custom_dropdown(driver, wait, "dropdown-search-vehicles-0-year", request.year, "Year"):
                    return {
                        "status": "error",
                        "message": "Step 7 failed: Could not select vehicle year",
                        "error_type": "SelectionError"
                    }
                
                # Select make
                if not select_custom_dropdown(driver, wait, "dropdown-search-vehicles-0-make", request.make, "Make"):
                    return {
                        "status": "error",
                        "message": "Step 7 failed: Could not select vehicle make",
                        "error_type": "SelectionError"
                    }
                
                # Select model
                if not select_custom_dropdown(driver, wait, "dropdown-search-vehicles-0-model", request.model, "Model"):
                    return {
                        "status": "error",
                        "message": "Step 7 failed: Could not select vehicle model",
                        "error_type": "SelectionError"
                    }
                
                # Select trim (same approach as year/make/model: click control and press Enter)
                logger.info("Selecting vehicle trim (first option)...")
                try:
                    # Find the trim dropdown input first (same as year/make/model)
                    trim_input = wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, '[data-cy="dropdown-search-vehicles-0-submodel"]'))
                    )
                    
                    # Find the parent control container to click on (same as year/make/model)
                    try:
                        control_container = trim_input.find_element(By.XPATH, "./ancestor::div[contains(@class, 'custom-dropdown__control')]")
                    except Exception:
                        control_container = driver.find_element(By.XPATH, "//input[@data-cy='dropdown-search-vehicles-0-submodel']/ancestor::div[contains(@class, 'custom-dropdown__control')]")
                    
                    # Check if trim is already selected (has a selected value)
                    try:
                        selected_value_elements = control_container.find_elements(By.CSS_SELECTOR, '.custom-dropdown__single-value')
                        if selected_value_elements and selected_value_elements[0].text.strip():
                            logger.info(f"Trim is already preset to '{selected_value_elements[0].text.strip()}', skipping selection")
                        else:
                            # Trim is not preset, click the dropdown indicator (arrow) first, then press Enter
                            logger.info("Trim field is empty, clicking dropdown indicator to open...")
                            
                            # Scroll to dropdown control
                            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", control_container)
                            human_delay(0.3, 0.6)
                            human_mouse_move(driver, control_container)
                            human_delay(0.2, 0.4)
                            
                            # Click to open dropdown - try multiple methods
                            logger.info("Clicking to open trim dropdown...")
                            dropdown_opened = False
                            
                            # Method 1: Try clicking the indicator (arrow button) using JavaScript
                            try:
                                indicator = control_container.find_element(By.CSS_SELECTOR, '.custom-dropdown__indicator')
                                logger.info("Found dropdown indicator, clicking with JavaScript...")
                                driver.execute_script("arguments[0].click();", indicator)
                                human_delay(0.5, 1.0)
                                # Check if dropdown opened by looking for options
                                try:
                                    driver.find_element(By.CSS_SELECTOR, '.custom-dropdown__option, [role="option"]')
                                    logger.info("Dropdown opened successfully via indicator click")
                                    dropdown_opened = True
                                except Exception:
                                    logger.info("Indicator click may not have opened dropdown, trying other methods...")
                            except Exception as e:
                                logger.debug(f"Indicator click failed: {str(e)}")
                            
                            # Method 2: If indicator didn't work, try clicking the control container
                            if not dropdown_opened:
                                try:
                                    logger.info("Trying to click control container...")
                                    driver.execute_script("arguments[0].click();", control_container)
                                    human_delay(0.5, 1.0)
                                    # Check if dropdown opened
                                    try:
                                        driver.find_element(By.CSS_SELECTOR, '.custom-dropdown__option, [role="option"]')
                                        logger.info("Dropdown opened successfully via control container click")
                                        dropdown_opened = True
                                    except Exception:
                                        logger.info("Control container click may not have opened dropdown, trying input click...")
                                except Exception as e:
                                    logger.debug(f"Control container click failed: {str(e)}")
                            
                            # Method 3: If still not open, try clicking the input field
                            if not dropdown_opened:
                                try:
                                    logger.info("Trying to click input field directly...")
                                    trim_input = driver.find_element(By.CSS_SELECTOR, '[data-cy="dropdown-search-vehicles-0-submodel"]')
                                    driver.execute_script("arguments[0].click();", trim_input)
                                    human_delay(0.5, 1.0)
                                    logger.info("Input field clicked")
                                    dropdown_opened = True
                                except Exception as e:
                                    logger.warning(f"Input field click also failed: {str(e)}")
                            
                            if not dropdown_opened:
                                logger.warning("Could not open dropdown, but will try to proceed with Enter key")
                            
                            # Wait for dropdown to fully open and options to appear
                            logger.info("Waiting for dropdown options to appear...")
                            human_delay(1.0, 1.5)  # Wait longer for dropdown to fully open
                            
                            # Re-find the input field to ensure it's focused
                            trim_input = wait.until(
                                EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-cy="dropdown-search-vehicles-0-submodel"]'))
                            )
                            
                            # Ensure input is focused before pressing Enter
                            try:
                                # Try to focus the input
                                driver.execute_script("arguments[0].focus();", trim_input)
                                logger.info("Trim input field focused")
                                human_delay(0.3, 0.6)
                                
                                # Also try clicking it
                                try:
                                    trim_input.click()
                                    logger.info("Trim input field clicked")
                                    human_delay(0.2, 0.4)
                                except Exception:
                                    pass
                            except Exception as focus_err:
                                logger.warning(f"Could not focus input: {str(focus_err)}")
                            
                            # Press Enter to auto-select the first option
                            logger.info("Pressing Enter to select first trim option...")
                            try:
                                trim_input.send_keys(Keys.RETURN)
                                logger.info("Enter key pressed successfully")
                            except Exception as enter_err:
                                # If send_keys fails, try JavaScript
                                logger.warning(f"Send keys failed: {str(enter_err)}, trying JavaScript")
                                driver.execute_script("arguments[0].dispatchEvent(new KeyboardEvent('keydown', {key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true}));", trim_input)
                                driver.execute_script("arguments[0].dispatchEvent(new KeyboardEvent('keyup', {key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true}));", trim_input)
                                logger.info("Enter key simulated via JavaScript")
                            
                            human_delay(1.0, 1.5)  # Wait longer for selection to process
                            
                            # Verify selection was made
                            try:
                                # Re-find control container to check for selected value
                                control_container = driver.find_element(By.XPATH, "//input[@data-cy='dropdown-search-vehicles-0-submodel']/ancestor::div[contains(@class, 'custom-dropdown__control')]")
                                selected_value = control_container.find_element(By.CSS_SELECTOR, '.custom-dropdown__single-value')
                                if selected_value and selected_value.text.strip():
                                    logger.info(f"Trim successfully selected: '{selected_value.text.strip()}'")
                                else:
                                    logger.warning("Trim selection may not have worked, but continuing...")
                            except Exception:
                                logger.info("Could not verify trim selection, but continuing...")
                    except Exception as e:
                        logger.info(f"Could not check or select trim: {str(e)}, skipping trim selection")
                            
                except Exception as e:
                    logger.info(f"Trim dropdown not found or not available: {str(e)}, skipping trim selection")
                
                logger.info(f"Step 7 completed. Current URL: {driver.current_url}")
                
            except Exception as e:
                logger.error(f"Step 7 failed: {str(e)}")
                return {
                    "status": "error",
                    "message": f"Step 7 failed: {str(e)}",
                    "error_type": type(e).__name__
                }
        else:
            logger.info("Step 7 skipped: Vehicle information (year, make, model) not provided in payload")
        
        # Step 8: Click "No" for adding another vehicle, then click "Save & continue"
        logger.info("Step 8: Clicking 'No' for adding another vehicle")
        try:
            # Click the "No" radio button
            logger.info("Looking for 'No' radio button for adding another vehicle")
            no_button = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-cy="radio-text-addAnother-vehicle-1-0"]'))
            )
            
            # Scroll to button
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", no_button)
            human_delay(0.3, 0.6)
            human_mouse_move(driver, no_button)
            human_delay(0.2, 0.4)
            
            # Click the "No" button
            no_button.click()
            logger.info("'No' button clicked successfully")
            human_delay(0.5, 1.0)
            
            # Click "Save & continue" button
            logger.info("Looking for 'Save & continue' button")
            try:
                # Wait for button to be present and enabled
                save_button = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '[data-cy="primary-button_section-continue"]'))
                )
                logger.info("Save & continue button found, waiting for it to be enabled...")
                
                # Wait for button to be enabled
                max_wait_time = 10
                start_time = time.time()
                while time.time() - start_time < max_wait_time:
                    try:
                        disabled_attr = save_button.get_attribute("disabled")
                        if disabled_attr is None:
                            logger.info("Save & continue button is now enabled")
                            break
                        human_delay(0.5, 1.0)
                        save_button = driver.find_element(By.CSS_SELECTOR, '[data-cy="primary-button_section-continue"]')
                    except Exception:
                        pass
                
                # Get the button element again to ensure it's clickable
                save_button = wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-cy="primary-button_section-continue"]'))
                )
                
                # Human-like behavior: scroll to button and move mouse
                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", save_button)
                human_delay(0.5, 1.0)
                human_mouse_move(driver, save_button)
                human_delay(0.4, 0.8)
                
                # Store current URL before clicking
                url_before_click = driver.current_url
                logger.info("Clicking Save & continue button...")
                save_button.click()
                logger.info("Save & continue button clicked successfully")
                
                # Wait for page to change (new page to load)
                logger.info("Waiting for new page to load after clicking 'Save & continue'")
                wait.until(lambda d: d.current_url != url_before_click)
                logger.info("New page loaded")
                
                # Wait for page to fully render
                human_delay(1.0, 1.5)
                logger.info(f"Step 8 completed. New page URL: {driver.current_url}")
                
            except Exception as e:
                logger.error(f"Step 8 failed: Failed to find, enable, or click the 'Save & continue' button: {str(e)}")
                return {
                    "status": "error",
                    "message": f"Step 8 failed: Failed to find, enable, or click the 'Save & continue' button: {str(e)}",
                    "error_type": type(e).__name__
                }
            
        except Exception as e:
            logger.error(f"Step 8 failed: Failed to click 'No' button: {str(e)}")
            return {
                "status": "error",
                "message": f"Step 8 failed: Failed to click 'No' button: {str(e)}",
                "error_type": type(e).__name__
            }
        
        # Step 9: Fill vehicle ownership, primary use, miles, and ownership duration
        logger.info("Step 9: Filling vehicle ownership and usage information")
        try:
            # 1. Click vehicle ownership radio button (click the label or text element)
            logger.info("Clicking vehicle ownership radio button")
            try:
                # Try clicking the text element first (more reliable)
                ownership_radio = wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-cy="radio-text-vehicle-ownership-0-0"]'))
                )
            except Exception:
                # Fallback: try the label
                try:
                    ownership_radio = wait.until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-cy="radio-vehicle-ownership-0-0"]'))
                    )
                except Exception:
                    # Last fallback: try the input
                    ownership_radio = wait.until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-cy="radio-input-vehicle-ownership-0-0"]'))
                    )
            
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", ownership_radio)
            human_delay(0.3, 0.6)
            human_mouse_move(driver, ownership_radio)
            human_delay(0.2, 0.4)
            
            try:
                ownership_radio.click()
            except Exception:
                # If click fails, use JavaScript click
                driver.execute_script("arguments[0].click();", ownership_radio)
            
            logger.info("Vehicle ownership radio button clicked successfully")
            human_delay(0.5, 1.0)
            
            # 2. Click primary use radio button "Commuting (to work or school)"
            logger.info("Clicking primary use radio button: Commuting (to work or school)")
            primary_use_radio = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-cy="radio-text-vehicle-primary_use-0-0"]'))
            )
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", primary_use_radio)
            human_delay(0.3, 0.6)
            human_mouse_move(driver, primary_use_radio)
            human_delay(0.2, 0.4)
            
            try:
                primary_use_radio.click()
            except Exception:
                # If click fails, use JavaScript click
                driver.execute_script("arguments[0].click();", primary_use_radio)
            
            logger.info("Primary use radio button clicked successfully")
            human_delay(0.5, 1.0)
            
            # 3. Enter miles: 1000
            logger.info("Entering miles: 1000")
            miles_input = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[data-cy="textinput-input-miles-0"]'))
            )
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", miles_input)
            human_delay(0.3, 0.6)
            human_mouse_move(driver, miles_input)
            human_delay(0.2, 0.4)
            miles_input.click()
            human_delay(0.2, 0.4)
            
            # Clear and type miles
            try:
                miles_input.clear()
            except Exception:
                miles_input.send_keys(Keys.CONTROL + "a")
                miles_input.send_keys(Keys.DELETE)
            human_delay(0.2, 0.4)
            
            # Type 1000
            miles_value = "1000"
            for char in miles_value:
                try:
                    miles_input.send_keys(char)
                except StaleElementReferenceException:
                    miles_input = driver.find_element(By.CSS_SELECTOR, '[data-cy="textinput-input-miles-0"]')
                    miles_input.send_keys(char)
                time.sleep(random.uniform(0.02, 0.08))
            logger.info("Miles entered successfully")
            human_delay(0.5, 1.0)
            
            # 4. Find and fill ownership duration dropdown (type "1 month - 1 year" and press Enter)
            logger.info("Filling vehicle ownership duration dropdown")
            try:
                # Use the exact data-cy value for ownership duration
                duration_data_cy = "dropdown-search-vehicle-ownership_length-0"
                logger.info(f"Looking for ownership duration dropdown with data-cy: {duration_data_cy}")
                
                # Find the duration dropdown input
                duration_input = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, f'[data-cy="{duration_data_cy}"]'))
                )
                logger.info("Ownership duration dropdown found")
                
                # Find the control container
                try:
                    control_container = duration_input.find_element(By.XPATH, "./ancestor::div[contains(@class, 'custom-dropdown__control')]")
                except Exception:
                    control_container = driver.find_element(By.XPATH, f"//input[@data-cy='{duration_data_cy}']/ancestor::div[contains(@class, 'custom-dropdown__control')]")
                
                # Click the control container to open dropdown (same as year/make/model)
                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", control_container)
                human_delay(0.3, 0.6)
                human_mouse_move(driver, control_container)
                human_delay(0.2, 0.4)
                
                logger.info("Clicking ownership duration dropdown...")
                try:
                    control_container.click()
                except Exception:
                    driver.execute_script("arguments[0].click();", control_container)
                
                human_delay(0.5, 1.0)  # Wait for dropdown to open
                
                # Re-find input and type the value
                duration_input = wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, f'[data-cy="{duration_data_cy}"]'))
                )
                
                # Clear and type "1 month - 1 year"
                try:
                    duration_input.clear()
                except Exception:
                    duration_input.send_keys(Keys.CONTROL + "a")
                    duration_input.send_keys(Keys.DELETE)
                human_delay(0.2, 0.4)
                
                logger.info("Typing '1 month - 1 year' in ownership duration field...")
                duration_value = "1 month - 1 year"
                for char in duration_value:
                    try:
                        duration_input.send_keys(char)
                    except StaleElementReferenceException:
                        duration_input = driver.find_element(By.CSS_SELECTOR, f'[data-cy="{duration_data_cy}"]')
                        duration_input.send_keys(char)
                    time.sleep(random.uniform(0.05, 0.12))
                
                logger.info("Finished typing, waiting for dropdown options to filter...")
                human_delay(0.8, 1.5)  # Wait for options to filter
                
                # Press Enter to select first option
                logger.info("Pressing Enter to select first option...")
                duration_input.send_keys(Keys.RETURN)
                logger.info("Ownership duration '1 month - 1 year' selected successfully")
                human_delay(0.5, 1.0)
                    
            except Exception as e:
                logger.error(f"Could not fill ownership duration: {str(e)}", exc_info=True)
                logger.warning("Continuing despite ownership duration error...")
            
            # 5. Click "Save & continue" button and wait for new page
            logger.info("Looking for 'Save & continue' button")
            try:
                # Wait for button to be present and enabled
                save_button = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '[data-cy="primary-button_section-continue"]'))
                )
                logger.info("Save & continue button found, waiting for it to be enabled...")
                
                # Wait for button to be enabled
                max_wait_time = 10
                start_time = time.time()
                while time.time() - start_time < max_wait_time:
                    try:
                        disabled_attr = save_button.get_attribute("disabled")
                        if disabled_attr is None:
                            logger.info("Save & continue button is now enabled")
                            break
                        human_delay(0.5, 1.0)
                        save_button = driver.find_element(By.CSS_SELECTOR, '[data-cy="primary-button_section-continue"]')
                    except Exception:
                        pass
                
                # Get the button element again to ensure it's clickable
                save_button = wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-cy="primary-button_section-continue"]'))
                )
                
                # Human-like behavior: scroll to button and move mouse
                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", save_button)
                human_delay(0.5, 1.0)
                human_mouse_move(driver, save_button)
                human_delay(0.4, 0.8)
                
                # Store current URL before clicking
                url_before_click = driver.current_url
                logger.info("Clicking Save & continue button...")
                save_button.click()
                logger.info("Save & continue button clicked successfully")
                
                # Wait for page to change (new page to load)
                logger.info("Waiting for new page to load after clicking 'Save & continue'")
                wait.until(lambda d: d.current_url != url_before_click)
                logger.info("New page loaded")
                
                # Wait for page to fully render
                human_delay(1.0, 1.5)
                logger.info(f"Step 9 completed. New page URL: {driver.current_url}")
                
            except Exception as e:
                logger.error(f"Step 9 failed: Failed to find, enable, or click the 'Save & continue' button: {str(e)}")
                return {
                    "status": "error",
                    "message": f"Step 9 failed: Failed to find, enable, or click the 'Save & continue' button: {str(e)}",
                    "error_type": type(e).__name__
                }
            
        except Exception as e:
            logger.error(f"Step 9 failed: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "message": f"Step 9 failed: {str(e)}",
                "error_type": type(e).__name__,
                "full_error": str(e)
            }
        
        # Step 10: Fill personal information, employment, insurance details, and contact info
        logger.info("Step 10: Filling personal information and insurance details")
        try:
            # Helper function to click radio button (tries text, label, then input)
            def click_radio_button(data_cy_text):
                try:
                    # Try text element first
                    radio = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, f'[data-cy="{data_cy_text}"]')))
                except Exception:
                    # Try label
                    try:
                        radio = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, f'label[data-cy*="{data_cy_text.split("-")[-1]}"]')))
                    except Exception:
                        # Try input
                        radio = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, f'input[data-cy*="{data_cy_text.split("-")[-1]}"]')))
                
                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", radio)
                human_delay(0.3, 0.6)
                human_mouse_move(driver, radio)
                human_delay(0.2, 0.4)
                try:
                    radio.click()
                except Exception:
                    driver.execute_script("arguments[0].click();", radio)
                human_delay(0.3, 0.6)
            
            # 1. Click "Male" radio button
            logger.info("Clicking 'Male' gender radio button")
            click_radio_button("radio-text-gender-0-0")
            logger.info("Gender selected successfully")
            
            # 2. Click "Single" marital status radio button
            logger.info("Clicking 'Single' marital status radio button")
            click_radio_button("radio-text-marital_status-0-0")
            logger.info("Marital status selected successfully")
            
            # 3. Click "Good (680-719)" credit score radio button
            logger.info("Clicking 'Good (680-719)' credit score radio button")
            click_radio_button("radio-text-credit_score-0-1")
            logger.info("Credit score selected successfully")
            
            # 4. Click "No diploma" education radio button (skip if already selected)
            logger.info("Checking education radio button")
            try:
                education_radio = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '[data-cy="radio-text-education-0-0"]')))
                # Check if already selected
                parent_label = education_radio.find_element(By.XPATH, "./ancestor::label")
                if "is-selected" not in parent_label.get_attribute("class"):
                    click_radio_button("radio-text-education-0-0")
                    logger.info("Education selected successfully")
                else:
                    logger.info("Education already selected, skipping")
            except Exception as e:
                logger.warning(f"Could not check/select education: {str(e)}")
            
            # 5. Fill employment dropdown: "Not employed within the last 12 months"
            logger.info("Filling employment status dropdown")
            if select_custom_dropdown(driver, wait, "dropdown-search-employment-0", "Not employed within the last 12 months", "Employment"):
                logger.info("Employment status selected successfully")
            else:
                logger.warning("Could not select employment status, continuing...")
            
            # 6. Fill current carrier dropdown: "other"
            logger.info("Filling current insurance company dropdown")
            if select_custom_dropdown(driver, wait, "dropdown-search-current_carrier-0", "other", "Current Carrier"):
                logger.info("Current carrier selected successfully")
            else:
                logger.warning("Could not select current carrier, continuing...")
            
            # 7. Click "Less than 6 months" insured length radio (skip if already selected)
            logger.info("Checking insured length radio button")
            try:
                insured_length_radio = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '[data-cy="radio-text-insured_length-0-0"]')))
                parent_label = insured_length_radio.find_element(By.XPATH, "./ancestor::label")
                if "is-selected" not in parent_label.get_attribute("class"):
                    click_radio_button("radio-text-insured_length-0-0")
                    logger.info("Insured length selected successfully")
                else:
                    logger.info("Insured length already selected, skipping")
            except Exception as e:
                logger.warning(f"Could not check/select insured length: {str(e)}")
            
            # 8. Click "$15k / $30k" bodily injury radio button
            logger.info("Clicking '$15k / $30k' bodily injury radio button")
            # Note: data-cy has special characters, use XPath or attribute contains
            try:
                # Try XPath first (handles special characters better)
                bodily_injury_radio = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@data-cy='radio-text-current_bodily_injury_per_person-0-$15k / $30k']")))
            except Exception:
                # Fallback: try with contains
                try:
                    bodily_injury_radio = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@data-cy, 'current_bodily_injury_per_person') and contains(@data-cy, '$15k')]")))
                except Exception:
                    # Last fallback: find by text content
                    bodily_injury_radio = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), '$15k / $30k')]")))
            
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", bodily_injury_radio)
            human_delay(0.3, 0.6)
            human_mouse_move(driver, bodily_injury_radio)
            human_delay(0.2, 0.4)
            try:
                bodily_injury_radio.click()
            except Exception:
                driver.execute_script("arguments[0].click();", bodily_injury_radio)
            logger.info("Bodily injury coverage selected successfully")
            human_delay(0.3, 0.6)
            
            # 9. Click "No" violations radio (skip if already selected)
            logger.info("Checking violations radio button")
            try:
                violations_radio = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '[data-cy="radio-text-violations-0"]')))
                parent_label = violations_radio.find_element(By.XPATH, "./ancestor::label")
                if "is-selected" not in parent_label.get_attribute("class"):
                    click_radio_button("radio-text-violations-0")
                    logger.info("Violations selected successfully")
                else:
                    logger.info("Violations already selected, skipping")
            except Exception as e:
                logger.warning(f"Could not check/select violations: {str(e)}")
            
            # 10. Fill email: "moazam@gmail.com"
            logger.info("Filling email field: moazam@gmail.com")
            email_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '[data-cy="textinput-input-email-0"]')))
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", email_input)
            human_delay(0.3, 0.6)
            human_mouse_move(driver, email_input)
            human_delay(0.2, 0.4)
            email_input.click()
            human_delay(0.2, 0.4)
            
            # Clear and type email
            try:
                email_input.clear()
            except Exception:
                email_input.send_keys(Keys.CONTROL + "a")
                email_input.send_keys(Keys.DELETE)
            human_delay(0.2, 0.4)
            
            email_value = "moazam@gmail.com"
            for char in email_value:
                try:
                    email_input.send_keys(char)
                except StaleElementReferenceException:
                    email_input = driver.find_element(By.CSS_SELECTOR, '[data-cy="textinput-input-email-0"]')
                    email_input.send_keys(char)
                time.sleep(random.uniform(0.02, 0.08))
            logger.info("Email entered successfully")
            human_delay(0.5, 1.0)
            
            # 11. Fill phone: "2019756595"
            logger.info("Filling phone number field: 2019756595")
            phone_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '[data-cy="textinput-input-phone-number-input"]')))
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", phone_input)
            human_delay(0.3, 0.6)
            human_mouse_move(driver, phone_input)
            human_delay(0.2, 0.4)
            phone_input.click()
            human_delay(0.2, 0.4)
            
            # Clear and type phone
            try:
                phone_input.clear()
            except Exception:
                phone_input.send_keys(Keys.CONTROL + "a")
                phone_input.send_keys(Keys.DELETE)
            human_delay(0.2, 0.4)
            
            phone_value = "2019756595"
            for char in phone_value:
                try:
                    phone_input.send_keys(char)
                except StaleElementReferenceException:
                    phone_input = driver.find_element(By.CSS_SELECTOR, '[data-cy="textinput-input-phone-number-input"]')
                    phone_input.send_keys(char)
                time.sleep(random.uniform(0.02, 0.08))
            logger.info("Phone number entered successfully")
            human_delay(0.5, 1.0)
            
            # 12. Click "No" military affiliation radio button
            logger.info("Clicking 'No' military affiliation radio button")
            click_radio_button("radio-text-has_military_affiliation-false")
            logger.info("Military affiliation selected successfully")
            
            # 13. Click "Save & continue" button and wait for new page
            logger.info("Looking for 'Save & continue' button")
            try:
                # Wait for button to be present and enabled
                save_button = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '[data-cy="primary-button_section-continue"]'))
                )
                logger.info("Save & continue button found, waiting for it to be enabled...")
                
                # Wait for button to be enabled
                max_wait_time = 10
                start_time = time.time()
                while time.time() - start_time < max_wait_time:
                    try:
                        disabled_attr = save_button.get_attribute("disabled")
                        if disabled_attr is None:
                            logger.info("Save & continue button is now enabled")
                            break
                        human_delay(0.5, 1.0)
                        save_button = driver.find_element(By.CSS_SELECTOR, '[data-cy="primary-button_section-continue"]')
                    except Exception:
                        pass
                
                # Get the button element again to ensure it's clickable
                save_button = wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-cy="primary-button_section-continue"]'))
                )
                
                # Human-like behavior: scroll to button and move mouse
                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", save_button)
                human_delay(0.5, 1.0)
                human_mouse_move(driver, save_button)
                human_delay(0.4, 0.8)
                
                # Store current URL before clicking
                url_before_click = driver.current_url
                logger.info("Clicking Save & continue button...")
                save_button.click()
                logger.info("Save & continue button clicked successfully")
                
                # Wait for page to change (new page to load)
                logger.info("Waiting for new page to load after clicking 'Save & continue'")
                wait.until(lambda d: d.current_url != url_before_click)
                logger.info("New page loaded")
                
                # Wait for page to fully render
                human_delay(1.0, 1.5)
                logger.info(f"Step 10 completed. New page URL: {driver.current_url}")
                
            except Exception as e:
                logger.error(f"Step 10 failed: Failed to find, enable, or click the 'Save & continue' button: {str(e)}")
                return {
                    "status": "error",
                    "message": f"Step 10 failed: Failed to find, enable, or click the 'Save & continue' button: {str(e)}",
                    "error_type": type(e).__name__
                }
            
        except Exception as e:
            logger.error(f"Step 10 failed: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "message": f"Step 10 failed: {str(e)}",
                "error_type": type(e).__name__,
                "full_error": str(e)
            }
        
        # Step 11: Click "Show quotes at this coverage" button and wait for new page
        logger.info("Step 11: Clicking 'Show quotes at this coverage' button")
        try:
            # Find and click the "Show quotes at this coverage" button
            logger.info("Looking for 'Show quotes at this coverage' button")
            show_quotes_button = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-cy="primary-button_show-quotes-minimum-desktop"]'))
            )
            
            # Scroll to button
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", show_quotes_button)
            human_delay(0.5, 1.0)
            human_mouse_move(driver, show_quotes_button)
            human_delay(0.4, 0.8)
            
            # Store current URL before clicking
            url_before_click = driver.current_url
            logger.info("Clicking 'Show quotes at this coverage' button...")
            
            try:
                show_quotes_button.click()
            except Exception:
                # If click fails, use JavaScript click
                driver.execute_script("arguments[0].click();", show_quotes_button)
            
            logger.info("'Show quotes at this coverage' button clicked successfully")
            
            # Wait for page to change (new page to load)
            logger.info("Waiting for new page to load after clicking 'Show quotes at this coverage'")
            wait.until(lambda d: d.current_url != url_before_click)
            logger.info("New page loaded")
            
            # Wait for page to fully render
            human_delay(1.5, 2.5)  # Wait longer for quotes page to load
            logger.info(f"Step 11 completed. New page URL: {driver.current_url}")
            
        except Exception as e:
            logger.error(f"Step 11 failed: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "message": f"Step 11 failed: Failed to click 'Show quotes at this coverage' button: {str(e)}",
                "error_type": type(e).__name__,
                "full_error": str(e)
            }
        
        # Helper function to extract plan details (Bodily Injury and Comprehensive deductible)
        def extract_plan_details(plan_data_cy):
            """Extract Bodily Injury and Comprehensive deductible from a plan card."""
            bi_value = None
            comprehensive_deductible = None
            
            try:
                plan_card = driver.find_element(By.CSS_SELECTOR, f'[data-cy="{plan_data_cy}"]')
                
                # Find the flex-column container that holds all the plan details
                try:
                    flex_container = plan_card.find_element(By.CSS_SELECTOR, ".d-flex.flex-column")
                except Exception:
                    # Fallback: try to find it by class
                    flex_container = plan_card.find_element(By.XPATH, ".//div[contains(@class, 'flex-column')]")
                
                # Get all child divs to find the structure
                all_divs = flex_container.find_elements(By.XPATH, "./div")
                
                # Method: Find the index of label divs and get the next text-bold div
                for i, div in enumerate(all_divs):
                    div_text = div.text.strip()
                    div_class = div.get_attribute('class') or ''
                    
                    # Check if this is the Bodily Injury label
                    if 'Bodily Injury' in div_text and 'BI' in div_text:
                        # Next div should be the BI value
                        if i + 1 < len(all_divs):
                            next_div = all_divs[i + 1]
                            next_class = next_div.get_attribute('class') or ''
                            if 'text-bold' in next_class:
                                bi_value = next_div.text.strip()
                                logger.info(f"Extracted BI value: {bi_value}")
                    
                    # Check if this is the Comprehensive + Collision label
                    if 'Comprehensive' in div_text and 'Collision' in div_text:
                        # Next div should be the comprehensive deductible
                        if i + 1 < len(all_divs):
                            next_div = all_divs[i + 1]
                            next_class = next_div.get_attribute('class') or ''
                            if 'text-bold' in next_class:
                                comprehensive_deductible = next_div.text.strip()
                                logger.info(f"Extracted Comprehensive deductible: {comprehensive_deductible}")
                
                # Fallback: Try XPath if the above method didn't work
                if not bi_value:
                    try:
                        bi_section = plan_card.find_element(By.XPATH, ".//div[contains(text(), 'Bodily Injury (BI)')]/following-sibling::div[contains(@class, 'text-bold')]")
                        bi_value = bi_section.text.strip()
                        logger.info(f"Extracted BI value (XPath fallback): {bi_value}")
                    except Exception:
                        pass
                
                if not comprehensive_deductible:
                    try:
                        comp_section = plan_card.find_element(By.XPATH, ".//div[contains(text(), 'Comprehensive + Collision')]/following-sibling::div[contains(@class, 'text-bold')]")
                        comprehensive_deductible = comp_section.text.strip()
                        logger.info(f"Extracted Comprehensive deductible (XPath fallback): {comprehensive_deductible}")
                    except Exception:
                        pass
                    
            except Exception as e:
                logger.warning(f"Could not find plan card with data-cy='{plan_data_cy}': {str(e)}")
            
            return bi_value, comprehensive_deductible
        
        # Helper function to scrape quotes from current page
        def scrape_quotes_from_page(plan_type, bodily_injury_value, comprehensive_deductible=None):
            """Scrape quotes from the current page."""
            scraped_quotes = []
            
            # Wait for quotes to load - try both old and new structures
            logger.info("Waiting for quote cards to load...")
            try:
                # Try waiting for either old or new card structure
                wait.until(EC.any_of(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '[data-cy*="results-card_carrierCard"]')),
                    EC.presence_of_element_located((By.CSS_SELECTOR, '[data-cy="results-card_price"]')),
                    EC.presence_of_element_located((By.CSS_SELECTOR, '.results-card-v2__body'))
                ))
                logger.info("Quote cards found, waiting for prices to load...")
            except Exception:
                logger.warning("Quote cards not found immediately, continuing anyway...")
            
            human_delay(4.0, 6.0)  # Wait longer for all cards and prices to fully render
            
            # Find all quote cards - try both old and new structures
            logger.info("Finding all quote cards...")
            quote_cards = []
            
            # Try new structure first (results-card-v2)
            try:
                quote_cards = driver.find_elements(By.CSS_SELECTOR, '.results-card-v2__body')
                logger.info(f"Found {len(quote_cards)} cards using new structure (.results-card-v2__body)")
            except Exception:
                pass
            
            # If no cards found, try old structure
            if not quote_cards:
                try:
                    quote_cards = driver.find_elements(By.CSS_SELECTOR, '[data-cy*="results-card_carrierCard"]')
                    logger.info(f"Found {len(quote_cards)} cards using old structure (results-card_carrierCard)")
                except Exception:
                    pass
            
            # If still no cards, try finding by price elements and getting parent
            if not quote_cards:
                try:
                    price_elements = driver.find_elements(By.CSS_SELECTOR, '[data-cy="results-card_price"]')
                    if price_elements:
                        quote_cards = []
                        for price_elem in price_elements:
                            try:
                                parent_card = price_elem.find_element(By.XPATH, "./ancestor::div[contains(@class, 'results-card') or contains(@class, 'card-body')]")
                                quote_cards.append(parent_card)
                            except Exception:
                                continue
                        logger.info(f"Found {len(quote_cards)} cards by finding price elements first")
                except Exception:
                    pass
            
            logger.info(f"Total found: {len(quote_cards)} quote cards")
            
            for idx, card in enumerate(quote_cards):
                try:
                    # Scroll to card to ensure it's loaded
                    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", card)
                    human_delay(0.5, 1.0)
                    
                    # Extract company name - try both old and new structures
                    company_name = "Unknown"
                    try:
                        # Try new structure first
                        try:
                            logo_img = card.find_element(By.CSS_SELECTOR, 'img[data-cy="results-card_logo"]')
                        except Exception:
                            # Try old structure
                            logo_img = card.find_element(By.CSS_SELECTOR, 'img[data-cy*="card-logo"]')
                        
                        alt_text = logo_img.get_attribute("alt") or ""
                        company_name = alt_text.replace(" logo", "").replace("Logo", "").replace("logo", "").strip()
                        if not company_name:
                            company_name = "Unknown"
                    except Exception:
                        pass
                    
                    # Try to find price - try both old and new structures
                    price = None
                    amount = None
                    
                    # Method 1: Try new structure (results-card-v2)
                    try:
                        price_elem = card.find_element(By.CSS_SELECTOR, '[data-cy="results-card_price"]')
                        amount_text = price_elem.text.strip()
                        
                        if amount_text:
                            # Get period from sibling
                            try:
                                period_elem = card.find_element(By.CSS_SELECTOR, '.results-card-v2__currency--period')
                                period = period_elem.text.strip()
                            except Exception:
                                period = "/mo"  # Default for new structure
                            
                            amount = amount_text.replace("$", "").replace(",", "").strip()
                            price = f"${amount_text}{period}".strip()
                            logger.info(f"Card {idx + 1} ({company_name}) - Found price (new structure): {price}")
                    except Exception:
                        pass
                    
                    # Method 2: Try old structure (rate elements)
                    if not price or not amount:
                        try:
                            rate_elements = card.find_elements(By.XPATH, ".//div[contains(@class, 'rate')]")
                            for rate_elem in rate_elements:
                                try:
                                    amount_elem = rate_elem.find_element(By.CSS_SELECTOR, '.rate__amount')
                                    amount_text = amount_elem.text.strip()
                                    
                                    if amount_text:
                                        try:
                                            dollar_elem = rate_elem.find_element(By.CSS_SELECTOR, '.rate__dollar')
                                            dollar_sign = dollar_elem.text.strip() or "$"
                                        except Exception:
                                            dollar_sign = "$"
                                        
                                        try:
                                            period_elem = rate_elem.find_element(By.CSS_SELECTOR, '.rate__period')
                                            period = period_elem.text.strip()
                                        except Exception:
                                            period = ""
                                        
                                        amount = amount_text
                                        price = f"{dollar_sign}{amount}{period}".strip()
                                        logger.info(f"Card {idx + 1} ({company_name}) - Found price (old structure): {price}")
                                        break
                                except Exception:
                                    continue
                        except Exception:
                            pass
                    
                    # Method 3: Try CSS selector search for old structure
                    if not price or not amount:
                        try:
                            rate_amount_elements = card.find_elements(By.CSS_SELECTOR, '.rate__amount')
                            for rate_amount_elem in rate_amount_elements:
                                amount_text = rate_amount_elem.text.strip()
                                if amount_text:
                                    try:
                                        rate_container = rate_amount_elem.find_element(By.XPATH, "./ancestor::div[contains(@class, 'rate')]")
                                        
                                        try:
                                            dollar_elem = rate_container.find_element(By.CSS_SELECTOR, '.rate__dollar')
                                            dollar_sign = dollar_elem.text.strip() or "$"
                                        except Exception:
                                            dollar_sign = "$"
                                        
                                        try:
                                            period_elem = rate_container.find_element(By.CSS_SELECTOR, '.rate__period')
                                            period = period_elem.text.strip()
                                        except Exception:
                                            period = ""
                                        
                                        amount = amount_text
                                        price = f"{dollar_sign}{amount}{period}".strip()
                                        logger.info(f"Card {idx + 1} ({company_name}) - Found price via CSS: {price}")
                                        break
                                    except Exception:
                                        continue
                        except Exception:
                            pass
                    
                    # Only add to results if price is not null
                    if price:
                        quote_data = {
                            "company": company_name,
                            "price": price,
                            "bodily_injury": bodily_injury_value,
                            "comprehensive_deductible": comprehensive_deductible,
                            "plan_type": plan_type
                        }
                        scraped_quotes.append(quote_data)
                        logger.info(f"Scraped quote {len(scraped_quotes)}: {company_name} - {price} (BI: {bodily_injury_value}, Comp: {comprehensive_deductible})")
                    else:
                        logger.info(f"Skipping quote for {company_name} - No price available")
                        
                except Exception as e:
                    logger.warning(f"Error scraping card {idx + 1}: {str(e)}")
                    continue
            
            return scraped_quotes
        
        # Step 12: Scrape quote data from minimum plan
        logger.info("Step 12: Scraping quote data from minimum plan")
        minimum_quotes = []
        try:
            # Wait for quotes page to fully load
            logger.info("Waiting for quotes page to fully load...")
            
            # Set hardcoded plan details for minimum plan
            minimum_bi_value = "$15k/$30k"
            minimum_comp_deductible = "0"
            logger.info(f"Minimum plan - BI: {minimum_bi_value}, Comprehensive: {minimum_comp_deductible}")
            
            # Scrape minimum plan quotes
            minimum_quotes = scrape_quotes_from_page("minimum", minimum_bi_value, minimum_comp_deductible)
            logger.info(f"Step 12 completed. Scraped {len(minimum_quotes)} quotes from minimum plan")
            
        except Exception as e:
            logger.error(f"Step 12 failed: {str(e)}", exc_info=True)
            minimum_quotes = []
        
        # Step 13: Click Basic plan and scrape quotes
        logger.info("Step 13: Clicking Basic plan and scraping quotes")
        basic_quotes = []
        try:
            # Click the Basic plan radio button
            logger.info("Clicking Basic plan radio button")
            basic_plan_radio = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-cy="basic-coverage-card-container"]'))
            )
            
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", basic_plan_radio)
            human_delay(0.3, 0.6)
            human_mouse_move(driver, basic_plan_radio)
            human_delay(0.2, 0.4)
            
            try:
                basic_plan_radio.click()
            except Exception:
                driver.execute_script("arguments[0].click();", basic_plan_radio)
            
            logger.info("Basic plan clicked successfully")
            human_delay(2.0, 3.0)  # Wait for new cards to load
            
            # Set hardcoded plan details for basic plan
            basic_bi_value = "$25k/$50k"
            basic_comp_deductible = "1000"
            logger.info(f"Basic plan - BI: {basic_bi_value}, Comprehensive: {basic_comp_deductible}")
            
            # Scrape Basic plan quotes
            basic_quotes = scrape_quotes_from_page("basic", basic_bi_value, basic_comp_deductible)
            logger.info(f"Step 13 completed. Scraped {len(basic_quotes)} quotes from Basic plan")
            
        except Exception as e:
            logger.error(f"Step 13 failed: {str(e)}", exc_info=True)
            basic_quotes = []
        
        # Step 14: Click Better plan and scrape quotes
        logger.info("Step 14: Clicking Better plan and scraping quotes")
        better_quotes = []
        try:
            # Click the Better plan radio button
            logger.info("Clicking Better plan radio button")
            try:
                better_plan_radio = wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-cy="better-coverage-card-container"]'))
                )
            except Exception:
                # Fallback: find by text content "Better"
                better_plan_radio = wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'coverage-card-title') and contains(text(), 'Better')]/ancestor::label[contains(@class, 'custom-radio')]"))
                )
            
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", better_plan_radio)
            human_delay(0.3, 0.6)
            human_mouse_move(driver, better_plan_radio)
            human_delay(0.2, 0.4)
            
            try:
                better_plan_radio.click()
            except Exception:
                driver.execute_script("arguments[0].click();", better_plan_radio)
            
            logger.info("Better plan clicked successfully")
            human_delay(2.0, 3.0)  # Wait for new cards to load
            
            # Set hardcoded plan details for better plan
            better_bi_value = "$50k/$100k"
            better_comp_deductible = "1000"
            logger.info(f"Better plan - BI: {better_bi_value}, Comprehensive: {better_comp_deductible}")
            
            # Scrape Better plan quotes
            better_quotes = scrape_quotes_from_page("better", better_bi_value, better_comp_deductible)
            logger.info(f"Step 14 completed. Scraped {len(better_quotes)} quotes from Better plan")
            
        except Exception as e:
            logger.error(f"Step 14 failed: {str(e)}", exc_info=True)
            better_quotes = []
        
        logger.info("All steps (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14) completed successfully")
        
        # Close the browser after all steps are completed
        logger.info("Closing browser after completing all steps")
        try:
            if driver is not None:
                driver.quit()
                driver = None
                logger.info("Browser closed successfully")
        except Exception as e:
            logger.warning(f"Error closing browser: {str(e)}")
        
        return {
            "minimum_plan_quotes": minimum_quotes,
            "basic_plan_quotes": basic_quotes,
            "better_plan_quotes": better_quotes,
            "minimum_quotes_count": len(minimum_quotes),
            "basic_quotes_count": len(basic_quotes),
            "better_quotes_count": len(better_quotes)
        }
    except Exception as e:
        logger.error(f"Unexpected error in start_bot: {str(e)}", exc_info=True)
        
        # Close the browser even if there was an error
        try:
            if driver is not None:
                driver.quit()
                driver = None
                logger.info("Browser closed after error")
        except Exception:
            pass
        
        return {
            "status": "error",
            "message": f"Unexpected error: {str(e)}",
            "error_type": type(e).__name__
        }


@app.get("/status")
async def get_status():
    """
    Get the current status of the browser session.
    
    Returns:
        dict: Current browser status
    """
    global driver
    
    if driver is None:
        return {"status": "no_browser", "message": "No browser session active"}
    
    try:
        current_url = driver.current_url
        title = driver.title
        return {
            "status": "active",
            "current_url": current_url,
            "title": title
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Browser session error: {str(e)}"
        }


@app.post("/stop")
async def stop_bot():
    """
    Stop the bot and close the browser.
    
    Returns:
        dict: Status message
    """
    global driver
    
    if driver is None:
        return {"status": "no_browser", "message": "No browser session to close"}
    
    try:
        driver.quit()
        driver = None
        return {"status": "success", "message": "Browser closed successfully"}
    except Exception as e:
        return {"status": "error", "message": f"Error closing browser: {str(e)}"}


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up browser instance on application shutdown."""
    global driver
    if driver is not None:
        try:
            driver.quit()
        except Exception:
            pass


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
