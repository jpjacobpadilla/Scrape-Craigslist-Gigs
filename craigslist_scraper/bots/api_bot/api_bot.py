from datetime import datetime, timezone
import logging

from curl_cffi import requests

from craigslist_scraper.bots.utils import estimate_compensation, human_sleep_milliseconds
from craigslist_scraper.bots.abstract_bot_class import CraigslistBot
from craigslist_scraper.bots.bot_exceptions import (
    MismatchingAPIVersionError, BadRequestError)


logger = logging.getLogger(__name__)


class APIBot(CraigslistBot):
    """
    A class which uses Craigslist's private API the same way that the browser does.
    The main method is get_public_gigs() which handles everything.

    Class Attrs:
        REQUIRES_API_VERSION: The Craigslist API version (sent in the API responses). 
    """
    REQUIRES_API_VERSION: int = 8

    def __init__(self):
        """
        Attrs:
            param_cc: A query string parameter representing the country that the gigs are in.
            param_lang: A query string parameter establishing the language.
            param_search_path: 'ggg' is for Craigslist Gigs.
            param_is_paid: A query string parameter that affects the cacheId from the /full endpoint
                and only returns paid gigs.
            location_code: The location code of the Craigslist Gigs. 4 is for boston and 3 is
                for New York.
            batch_size: The default API result length (how many Gigs is returned per request).
            batch_sort_id: How the data is sorted.
            location: Used in the format-strings of some headers to create subdomains.
            tls_fingerprint: curl_cffi is a package that allows you to mimic the TLS fingerprint
                of different browsers during the TLS handshake process.
            user_agent: A user agent that aligns with the TLS fingerprint.
            session: A curl_cffi session object; mainly to store cookies.
            max_posted_ts: A timestamp that is returned from the /full endpoint.
            cache_ts: Another timestamp returned from the /full endpoint.
            cache_id: The CacheId value from the response of the /full endpoint.
            gig_count: The total number of gigs for a location returned in the
                response of the /.../full endpoint.
        """
        # Standard parameters for API requests
        self.param_cc: str = 'US'
        self.param_lang: str = 'en'
        self.param_search_path: str = 'ggg'
        self.param_is_paid: str = 'yes'
        self.location_code: int = 4
        self.batch_size: int = 1080
        self.batch_sort_id: int = 1
        self.location: str  = 'boston'

        # Initializing session object defaults
        self.tls_fingerprint: str = 'safari15_5'
        self.user_agent = (
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
            'AppleWebKit/605.1.15 (KHTML, like Gecko) '
            'Version/15.5 Safari/605.1.15'
        )

        self.session = requests.Session()

        # Tokens that are set later
        self.max_posted_ts: str = None
        self.cache_ts: str = None
        self.cache_id: str = None

        # Other instance variables to be initialized later
        self.gig_count: int = None

    def get_all_gigs(self) -> list[dict[str, str]]:
        """
        This is the main method which returns a list of all Craigslist Gigs.
        It initializes the self.session with the appropriate cookies,
        and then sends a few requests in the same manner as a real browser.

        Returns:
            More documentation about this in the abstract base class.
        """ 
        self.initialize_session()
        human_sleep_milliseconds(30, 200)
        return self.gather_data()
        
    def initialize_session(self) -> None:
        """ 
        Initializes the self.session request object 
        and the instance variables from the /.../full endpoint.
        """
        self.initialize_cookie()

        api_version: int = self.get_tokens_from_search_full_endpoint()
        logger.info(f'Using Craigslist API version {api_version}')

        if api_version != APIBot.REQUIRES_API_VERSION:
            raise MismatchingAPIVersionError(
                f'API version {api_version}, but expected {APIBot.REQUIRES_API_VERSION}'
            )

    def initialize_cookie(self) -> None:
        """
        Sends a request to the main css file of Craigslist which sets a cookie
        """
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9",
            "Host": f"{self.location}.craigslist.org",
            "Referer": f"https://www.google.com/",
            "Sec-Fetch-Dest": "script",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            'User-Agent': self.user_agent
        }
        param = {'is_paid': self.param_is_paid}
        url = f'https://{self.location}.craigslist.org/search/ggg'

        resp = self.session.get(url, impersonate=self.tls_fingerprint, headers=headers, params=param)

        logger.info(f'Sent request to base url get cookie. Status code: {resp.status_code}')

        if resp.status_code != 200 or 'cl_b' not in self.session.cookies:
            raise BadRequestError({
                'status_code': resp.status_code,
                'resp': resp.text,
                'session_cookies': self.session.cookies
            })
        
        self.session.cookies.update({'cl_tocmode': 'ggg%3Apic'})
        logger.debug(f'Initialized Session cookies: {self.session.cookies}')

    def get_tokens_from_search_full_endpoint(self) -> int:
        """
        Sends a request to the /.../full endpoint and then collects the necessary data
        from the response to populate the rest of the instance variables..

        Returns:
            The Craigslist private API version number (int).
        """
        params = {
            'CC': self.param_cc,
            'batch': f'{self.location_code}-{self.get_current_time()}-0-{self.batch_sort_id}-0',
            'lang': self.param_lang,
            'searchPath': self.param_search_path,
            'is_paid': self.param_is_paid
        }
        headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9",
            "Host": "sapi.craigslist.org",
            "Referer": f"https://{self.location}.craigslist.org",
            "Sec-Fetch-Dest": "script",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            'User-Agent': self.user_agent
        }
        url = 'https://sapi.craigslist.org/web/v8/postings/search/full' 

        resp = self.session.get(url, impersonate=self.tls_fingerprint, params=params, headers=headers)

        logger.info(f'Sent request to /.../full endpoint to get tokens. Status code: {resp.status_code}')
        if resp.status_code != 200:
            raise BadRequestError({
                'status_code': resp.status_code,
                'resp': resp.text,
                'session_cookies': self.session.cookies
            })
        
        data = resp.json()
        
        self.cache_id = data['data']['cacheId']
        self.cache_ts = data['data']['cacheTs']
        self.max_posted_ts = data['data']['maxPostedTs']
        self.gig_count = data['data']['totalResultCount']

        logger.debug(f''' Collected tokens: 
            {self.cache_id = } 
            {self.cache_ts = } 
            {self.max_posted_ts = } 
            {self.gig_count = }''')

        return data.get('apiVersion', '-1')
    
    def gather_data(self) -> list[dict[str, str]]:
        """
        Handles the task of calling the method to get the data.
        If the batch-size is say 1080 but the gig-count is 2000, 
        this is the method that would handle sending two requests to 
        the /.../batch endpoint to retrieve all of the data.

        Returns:
            More documentation about this in the abstract base class.
        """
        data = []

        for i in range(0, self.gig_count, self.batch_size):
            gigs = self.get_batch_data(i, self.batch_size)
            data.extend(gigs)
            human_sleep_milliseconds(5, 20)
            
        return data


    def get_batch_data(self, start: int, count: int) -> list[dict[str, str]]:
        """
        Send a request to /.../batch API endpoint and get some gigs.

        Args:
            start: This is the first gig that will be returned. 
            count: This is the number of gigs that will be returned;
                generally, this should be self.batch_size.

        Returns:
            More documentation about this in the abstract base class.
        """
        logger.info(f'Sending request to /../batch endpoint to get data. Gigs: {start = } {count = }')

        params = {
            'batch': f'{self.location_code}-{start}-{count}-1-0-{self.max_posted_ts}-{self.cache_ts}',
            'cacheId': self.cache_id,
            'CC': self.param_lang,
            'lang':self.param_lang,
        }
        headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9",
            "Host": "sapi.craigslist.org",
            "Referer": f"https://{self.location}.craigslist.org",
            "Sec-Fetch-Dest": "script",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            'User-Agent': self.user_agent
        }
        url = 'https://sapi.craigslist.org/web/v8/postings/search/batch'

        resp = self.session.get(url, impersonate=self.tls_fingerprint, params=params, headers=headers)

        logger.info(f'Sent request to /.../batch endpoint. Status code: {resp.status_code}')
        if resp.status_code != 200:
            raise BadRequestError({
                'status_code': resp.status_code,
                'resp': resp.text,
                'session_cookies': self.session.cookies
            })

        data = resp.json()
        base_id = int(data['data']['minPostingId'])

        gigs = []
        for posting in data['data']['batch']:
            gigs.append({
                'gig_id': int(posting[0]) + base_id,
                'title': posting[1],
                'comp_message': '$0' if len(posting) < 5 else posting[4][1],
                'comp_estimate': estimate_compensation('$0' if len(posting) < 5 else posting[4][1]) 
            })

        return gigs

    @staticmethod
    def get_current_time() -> int:
        """
        Return a number representing the time in Unix format.
        Many of the request's use need this.

        Returns:
            An integer - Used as a query string parameter.
        """
        current_utc_datetime = datetime.now(timezone.utc)
        return int(current_utc_datetime.timestamp())
