from __future__ import annotations

import logging

import undetected_chromedriver as uc

from craigslist_scraper.bots.bot_exceptions import UnableToGetToPageError
from craigslist_scraper.bots.utils import human_sleep_seconds

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from selenium.webdriver.remote.webelement import WebElement


logger = logging.getLogger(__name__)


class Clicker:
    def get_to_page(self, element: WebElement, get_to: str = None):
        """
        Attempt to get to another page by using four different methods.

        Methods (in order):
            1. element.click()
            2. Javascript click
            3. load page with driver.get() via load_page() mixin
            4. Sleep for a few minutes, create a new Selenium instance, then load_page().
            *3 and 4 only work if you specify the url that you are trying to get to @href*
        
        Args:
            element: The element to click on.
            get_to: probably the href of the a tag... The url that you want to get to.
        """
        old_url: str = self.driver.current_url

        try:
            element.click()

        except Exception as e:
            logger.exception(e)
            human_sleep_seconds(40, 120)
        
        else:
            if self.check_new_page(old_url, get_to): 
                logger.info('Successful click via method 1!')
                return 
        
        logger.error('Failed to click on element with element.click()')
        human_sleep_seconds(5, 7)

        try:
            self.driver.execute_script("arguments[0].click();", element)
        
        except Exception as e:
            logger.exception(e)
            human_sleep_seconds(40, 120)
        
        else:
            if self.check_new_page(old_url, get_to): 
                logger.info('Successful click via method 2!')
                return 

        logger.error('Failed to click on element with Javascript')

        if get_to:
            human_sleep_seconds(5, 10)
            self.driver.load_page(get_to)
            if self.check_new_page(old_url, get_to): 
                logger.info('Successful click via method 3!')
                return 

            logger.critical('Unable to get to url. Restarting WebDriver')
            human_sleep_seconds(120, 240)

            self.driver.quit()
            self.driver = uc.Chrome(headless=True)
            self.load_page(get_to)

            if self.check_new_page(old_url, get_to): 
                logger.info('Successful click via method 4!')
                return 

        raise UnableToGetToPageError()
    
    def check_new_page(self, old_url: str, get_to: str | None) -> bool:
        """ 
        Checks if the url has changed. If get_to is not None, 
        it will check that the new url is equal to get_to.

        Args:
            old_url: The old url.
            get_to: An optional url which is the url that you want to get to.
        """
        if (url := self.driver.current_url) != old_url:
            if not get_to:
                return True
            
            if url == get_to:
                return True
            
        return False