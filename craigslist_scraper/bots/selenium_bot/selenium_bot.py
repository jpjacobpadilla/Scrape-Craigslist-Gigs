from __future__ import annotations

import random
import logging

import undetected_chromedriver as uc

from .mixins.clicker import Clicker
from .mixins.get_gig_data import GetGigData
from .mixins.navigate import NavigateSite
from .mixins.load_page import LoadPage
from .mixins.select_options import SelectOptions
from craigslist_scraper.bots.abstract_bot_class import CraigslistBot
from craigslist_scraper.bots.utils import estimate_compensation, human_sleep_seconds

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from selenium.webdriver.chrome.webdriver import WebDriver


logger = logging.getLogger(__name__)


class SeleniumBot(
    CraigslistBot,
    Clicker,
    GetGigData,
    NavigateSite,
    LoadPage,
    SelectOptions
):
    """
        Selenium-based Craigslist Boston Gigs scraper. Uses mixin classes to 
        keep the everything organized.
    """
    def __init__(self):
        """
        Attrs:
            driver: An instance of UndetectedChromeDriver, which is just
                an instance of the Chrome WebDriver with a few patches to make
                it more stealthy.
            base_url: The base Craigslist url.
        """
        self.driver: WebDriver = uc.Chrome(headless=True)
        self.base_url: int = 'https://boston.craigslist.org/search/ggg'

    def get_all_gigs(self) -> list[dict[str, str]]:
        """
        The client facing method to get all of the gigs and then shut down the driver.

        Returns:
            More documentation about this in the abstract base class.
        """
        try:
            return self._get_all_gigs()
        finally:
            self.driver.quit()
    
    def _get_all_gigs(self) -> list[dict[str, str]]:
        """ 
        Gets data on all of the paid gigs in Boston.

        Steps:
            1. Load the Craigslist page
            2. Select the button to search for only paid gigs
            3. Go to the Gig on the top of the first page
            4. Get the data on the gig
            5. If it can click the "next" button on the gig page, click it
            6. Repeat steps 4-5 until the "next" button is disabled  

        Returns:
            More documentation about this in the abstract base class.
        """
        self.load_page(self.base_url)
        self.select_only_paid_gigs()
        self.navigate_to_first_gig()

        data = []
        another_gig = self.next_page_available()
        while another_gig:
            title, comp, gig_id = self.get_gig_data()
            logger.info(f'Scraped gig: "{title}"')
            data.append({
                'gig_id': gig_id,
                'title': title,
                'comp_message': comp,
                'comp_estimate': estimate_compensation(comp) 
            })

            human_sleep_seconds(3, 10)
            if random.randint(1, 20) == 1: human_sleep_seconds(10, 50)
            if random.randint(1, 200) == 1: human_sleep_seconds(50, 250)

            another_gig = self.next_page_available()
            if another_gig: self.navigate_to_next_gig()
                
        return data