import logging

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains


logger = logging.getLogger(__name__)


class NavigateSite:
    def navigate_to_first_gig(self) -> None:
        """ Get to the first gig on the page. """
        XPATH_FIRST_GIG = "//div[contains(@class, 'cl-results-page')]//ol/li[1]//a[1]"
        gig_element = WebDriverWait(self.driver, 15).until(
            EC.presence_of_element_located((By.XPATH, XPATH_FIRST_GIG))
        )

        actions = ActionChains(self.driver)
        actions.move_to_element(gig_element).perform()
        logger.info('Navigated to first gig page')
        self.get_to_page(gig_element, gig_element.get_attribute('href'))


    def next_page_available(self) -> bool:
        """ 
        Check if Selenium is able to click on the "next" button to go to the
        next gig.
        
        Returns:
            bool: True if it there is another gig to go to, otherwise False.
        """
        XPATH_NEXT_PAGE_BTN =  "//a[contains(@class, 'next')]"
        next_page_btn = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, XPATH_NEXT_PAGE_BTN))
        )

        return next_page_btn.get_attribute('href') is not None
    
    def navigate_to_next_gig(self) -> None:
        """ Get to the next gig via "clicking" on the "next" button. """
        XPATH_NEXT_PAGE_BTN =  "//a[contains(@class, 'next')]"
        next_page_btn = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, XPATH_NEXT_PAGE_BTN))
        )

        actions = ActionChains(self.driver)
        actions.move_to_element(next_page_btn).perform()
        logger.info('Navigated to next gig button')
        self.get_to_page(next_page_btn, next_page_btn.get_attribute('href'))