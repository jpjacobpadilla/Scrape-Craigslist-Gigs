class BotError(Exception):
    """Base Exception"""

    START_COLOR = "\033[95m"
    END_COLOR = "\033[0m"

    def __init__(self, message: str = ''):
        if not message:
            formatted_docstring = self.__doc__.replace('\n', '\n    ') 
            message = f'\n\n\t{formatted_docstring}'
        super().__init__(f'{self.START_COLOR}{message}{self.END_COLOR}')

class APIBotError(BotError):
    """ An error originating from the API based bot. """
    pass

class SeleniumBotError(BotError):
    """ An error originating from the use of Selenium via the Selenium bot. """
    pass

class MismatchingAPIVersionError(APIBotError):
    """
    This error occurs when the Craigslist private API is updated.
    """
    pass

class BadRequestError(APIBotError):
    """ A generic bad request exception. """
    pass

class UnableToGetToPageError(SeleniumBotError):
    """ Unable to get to next page. You are probably blocked. Change proxy? """
    pass

