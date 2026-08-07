import webbrowser
from core.lifecycle import BaseLifecycleComponent
from core.logger import logger

class BrowserPlugin(BaseLifecycleComponent):
    """
    JARVIS Browser Integration Plugin.
    """
    def __init__(self):
        super().__init__("BrowserPlugin")

    def open_url(self, url: str) -> bool:
        try:
            if not url.startswith(("http://", "https://")):
                url = "https://" + url
            logger.info(f"[BrowserPlugin] Opening URL: {url}")
            webbrowser.open(url)
            return True
        except Exception as e:
            logger.error(f"[BrowserPlugin] Failed to open URL {url}: {e}")
            return False

    def search_web(self, query: str) -> bool:
        search_url = f"https://www.google.com/search?q={query}"
        return self.open_url(search_url)
