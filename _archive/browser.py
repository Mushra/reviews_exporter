from playwright.sync_api import sync_playwright


DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/138.0.0.0 Safari/537.36"
)


class BrowserSession:

    def __init__(
        self,
        playwright,
        browser,
        context,
        page
    ):

        self.playwright = playwright
        self.browser = browser
        self.context = context
        self.page = page


    def close(self):

        self.context.close()

        self.browser.close()

        self.playwright.stop()



def create_browser(

    headless=True,

    browser_name="chromium",

    viewport=(1600, 900),

    user_agent=DEFAULT_USER_AGENT

):

    playwright = sync_playwright().start()


    if browser_name == "firefox":

        browser = playwright.firefox.launch(
            headless=headless
        )

    elif browser_name == "webkit":

        browser = playwright.webkit.launch(
            headless=headless
        )

    else:

        browser = playwright.chromium.launch(
            headless=headless
        )


    context = browser.new_context(

        viewport={

            "width": viewport[0],

            "height": viewport[1]

        },

        user_agent=user_agent,

        locale="en-US",

        java_script_enabled=True

    )


    page = context.new_page()


    return BrowserSession(

        playwright,

        browser,

        context,

        page

    )