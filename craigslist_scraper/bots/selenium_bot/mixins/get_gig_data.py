from urllib.parse import urlparse
import logging
import re

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


logger = logging.getLogger(__name__)


class GetGigData:
    def get_gig_data(self) -> tuple[str, str, str]:
        """
        Get the title and compensation for a gig. Must be on a gig page for 
        this method to work.
        
        Returns:
            tuple(title text, compensation text, gig id from url)
        """
        XPATH_COMP = "(//p|//span)[contains(text(), 'compensation')]/b" 
        XPATH_TITLE = "//*[@id='titletextonly']"

        comp_element = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, XPATH_COMP))
        )
        title_element = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, XPATH_TITLE))
        )

        endpoint = urlparse(self.driver.current_url).path
        gig_id = re.search(r'\/(\d+)\.html', endpoint).group(1)

        logger.debug(f'{title_element.text = }\n{comp_element.text}\n{gig_id = }')
        return title_element.text, comp_element.text, gig_id
