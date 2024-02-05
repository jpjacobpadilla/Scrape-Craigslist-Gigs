import logging

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

from craigslist_scraper.bots.utils import human_sleep_seconds, gaussian_number_generator


logger = logging.getLogger(__name__)


class SelectOptions:
    def select_only_paid_gigs(self) -> None:
        """
        Select the button on the left hand side of the screen to search for only
        paid options.
        """
        XPATH_PAID_BUTTON = "//*[@name='is_paid']/following-sibling::*//button[text()='paid']"
        XPATH_APPLY_BUTTON = "//button[contains(@class, 'cl-exec-search')]"

        paid_btn_element = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, XPATH_PAID_BUTTON))
        )
        apply_element = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, XPATH_APPLY_BUTTON))
        )

        actions = ActionChains(self.driver)
        actions.move_to_element(paid_btn_element) \
            .pause(gaussian_number_generator(.1, .8)) \
            .click() \
            .move_to_element(apply_element) \
            .pause(gaussian_number_generator(.2, 1.5)) \
            .click() \
            .perform()

        logger.info('Selected only paid gigs option')
        human_sleep_seconds(1, 3)