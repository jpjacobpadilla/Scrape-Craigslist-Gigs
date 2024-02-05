import time
import logging

from .bots.abstract_bot_class import CraigslistBot
from .logger import configure_logger
from .bots import APIBot, SeleniumBot
from .bots.utils import human_sleep_seconds
from .bots.bot_exceptions import BadRequestError
from .db_manager import DBHandler


configure_logger()
logger = logging.getLogger(__name__)


class Client:
    """
    The main client that lets you interface with the actual bots.

    The main method here is "run". This will attempt to scrape the data from 
    Craigslist. There are two bots that the method has to work with. It first 
    tries to use the API, but if that doesn't work, it will switch to using the
    slower, Selenium scraper.
    """
    def __init__(self, db_file: str = 'database.db'):
        """
        Create the SQLite database if it does not exist and sets self.bots to
        a list of available bots.

        Args:
            db_file: This is where the database will be stored. The db is created
                automatically on first run!
        
        Attrs:
            db: An instance of the database handler.
            bot_in_use: I continence var to signify which bot type (selenium or api)
                is currently being used.
            bots: A dictionary of all of the available bots.
        """
        self.db: DBHandler = DBHandler(db_file)

        self.bot_in_use: str = None
        self.bots: dict[str, str] = {
            'api': APIBot,
            'selenium': SeleniumBot
        }
    
    def run(self) -> None:
        """
        Run the scraper. This method attempts to scrape all of the paid gigs from 
        the Boston Gigs page of Craigslist and then stores the data into the 
        SQLite database.

        Raises:
            This will try to catch the first big bot error and then switch to another
            scraping method. However, if the second attempt to scrape the data
            raises an error, this method won't catch it.
        """
        start_time = time.time()
        bot = self._get_bot('api')

        try:
            logger.info(f'Using {self.bot_in_use} to scrape data')
            data = bot.get_all_gigs()

        except BadRequestError as e:
            logger.exception(e)
            human_sleep_seconds(100, 300) 

            try:
                logger.info(f'Attempting to use {self.bot_in_use} to get data again')
                data = bot.get_all_gigs()

            except Exception as e:
                logger.exception(e)
                logger.warning('Switching to Selenium bot')
                bot = self._get_bot('selenium')
                data = bot.get_all_gigs()

        except Exception as e:
            logger.exception(e)
            logger.warning('Switching to Selenium bot')
            bot = self._get_bot('selenium')
            data = bot.get_all_gigs()

        logger.info(f'Scraped all gigs! Number: {len(data)}')
        self.db.add_gig_scraping_job(
            bot_used=self.bot_in_use,
            duration=str(time.time() - start_time),
            gigs=data
        )
    
    def _get_bot(self, bot_type: str, *args, **kwargs) -> CraigslistBot:
        """
        A convince method used to get and initialize a bot instance and then set
        the instance variable "bot_in_use".

        Args:
            bot_type: One of the keys from self.bots (the dict that 
                stores the bots).
            *args, **kwargs: Any additional arguments for the __init__ of 
                the class.
        
        Returns:
            A CraigslistBot child class instance.
        """
        self.bot_in_use = bot_type
        return self.bots[bot_type](*args, **kwargs)