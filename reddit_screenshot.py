# reddit_screenshot.py
# Takes authentic Reddit post screenshots using Playwright headless browser

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
import time

def take_reddit_screenshot(
    post_url: str,
    output_file: str = "post.png",
    width: int = 1080,
    height: int = 1920,
    wait_time: int = 3
) -> str | None:
    """
    Takes a screenshot of a Reddit post using Playwright headless browser.
    
    This captures the REAL Reddit post appearance, not a recreation.
    
    Args:
        post_url: Full Reddit post URL (e.g., https://reddit.com/r/AskReddit/comments/...)
        output_file: Path to save screenshot
        width: Viewport width (default 1080 for 9:16)
        height: Viewport height (default 1920 for 9:16)
        wait_time: Seconds to wait for page load
        
    Returns:
        Path to screenshot file, or None on failure
    """
    print(f"📸 Taking screenshot of Reddit post...")
    
    # Convert to old.reddit.com to avoid network security blocks
    if 'reddit.com' in post_url and 'old.reddit.com' not in post_url:
        post_url = post_url.replace('reddit.com', 'old.reddit.com')
        print(f"   Using old Reddit interface to avoid blocking")
    
    print(f"   URL: {post_url}")
    
    try:
        with sync_playwright() as p:
            # Launch browser in headless mode with args to avoid detection
            browser = p.chromium.launch(
                headless=True,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--no-sandbox',
                    '--disable-web-security'
                ]
            )
            
            # Create context with realistic desktop user agent
            context = browser.new_context(
                viewport={'width': width, 'height': height},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
            )
            
            page = context.new_page()
            
            # Navigate to Reddit post
            print("   Loading Reddit page...")
            page.goto(post_url, wait_until='networkidle', timeout=30000)
            
            # Wait a bit for dynamic content
            time.sleep(wait_time)
            
            # Try to close cookie banner if it appears
            try:
                cookie_button = page.locator('button:has-text("Accept"), button:has-text("Kabul"), button:has-text("Agree")')
                if cookie_button.count() > 0:
                    cookie_button.first.click()
                    time.sleep(1)
            except:
                pass
            
            # Try to dismiss any other popups (login, app download, etc.)
            try:
                # Common close button selectors
                close_buttons = page.locator('[aria-label="Close"], button:has-text("Not now"), button:has-text("Şimdi değil"), [data-testid="close-button"]')
                for i in range(close_buttons.count()):
                    try:
                        close_buttons.nth(i).click(timeout=2000)
                        time.sleep(0.5)
                    except:
                        pass
            except:
                pass
            
            # Find the main post element
            # Reddit uses different selectors, try multiple
            post_selectors = [
                '[data-test-id="post-content"]',
                '[data-testid="post-container"]',
                'shreddit-post',
                '[slot="post"]',
                'article',
                '.Post'
            ]
            
            post_element = None
            for selector in post_selectors:
                try:
                    element = page.locator(selector).first
                    if element.count() > 0:
                        post_element = element
                        print(f"   ✓ Found post using selector: {selector}")
                        break
                except:
                    continue
            
            if not post_element:
                print("   ⚠️  Could not find post element, taking full page screenshot")
                # Fallback: screenshot the whole page
                page.screenshot(path=output_file, full_page=False)
            else:
                # Screenshot just the post element
                post_element.screenshot(path=output_file)
            
            browser.close()
            
            print(f"✅ Screenshot saved: {output_file}")
            return output_file
            
    except PlaywrightTimeout:
        print("❌ Timeout while loading Reddit page")
        print("   The page took too long to load. This can happen if:")
        print("   - Reddit is slow or down")
        print("   - The URL is incorrect")
        print("   - Network connection issues")
        return None
        
    except Exception as e:
        print(f"❌ Error taking screenshot: {e}")
        import traceback
        traceback.print_exc()
        return None


def take_reddit_screenshot_simple(
    post_url: str,
    output_file: str = "post.png"
) -> str | None:
    """
    Simplified version - just takes a full-page screenshot.
    More reliable but captures more than just the post.
    """
    print(f"📸 Taking simple screenshot of: {post_url}")
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={'width': 1080, 'height': 1920})
            
            page.goto(post_url, timeout=30000)
            time.sleep(3)
            
            # Try to dismiss popups
            try:
                page.keyboard.press('Escape')
                time.sleep(0.5)
            except:
                pass
            
            page.screenshot(path=output_file, full_page=False)
            browser.close()
            
            print(f"✅ Screenshot saved: {output_file}")
            return output_file
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


if __name__ == "__main__":
    # Test with a sample Reddit post
    test_url = "https://www.reddit.com/r/AskReddit/comments/1gp8wn5/what_are_you_glad_you_tried_once_but_will/"
    print("Testing Reddit screenshot...")
    result = take_reddit_screenshot(test_url)
    if result:
        print(f"\n✅ Test successful! Screenshot saved to: {result}")
    else:
        print("\n❌ Test failed.")
