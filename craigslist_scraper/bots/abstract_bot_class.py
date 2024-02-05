from abc import ABC, abstractmethod


class CraigslistBot(ABC):
    @abstractmethod
    def get_all_gigs(self) -> list[dict[str, str]]:
        """ 
        The main method that all bots should have.

        Returns: A list of gigs. Each gig is a Python dictionary:
            [
                {
                    "gig_id": 1234567,
                    "title": "Focus Group for College Students in NYC & SF on App Usage",
                    "comp_message": "I will pay you $230-$250",
                    "com_estimate": 230
                },
                {
                    "gig_id": 7654321,
                    "title": "Another focus Group for College Students in NYC",
                    "comp_message": "I will pay you $250",
                    "com_estimate": 250
                },
                ...
            ]
        """
        pass