import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait


logger = logging.getLogger(__name__)


class LoadPage:
    def load_page(self, url: str) -> None:
        """ 
        driver.get and then wait until the page is loaded.

        Args:
            url: The url for driver.get(HERE).
        """
        self.driver.get(url)

        wait = WebDriverWait(self.driver, 15)
        wait.until(
            lambda driver: driver.execute_script('return document.readyState') == 'complete'
        )
        logger.info(f'Loaded page: {url}')