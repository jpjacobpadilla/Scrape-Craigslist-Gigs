import sqlite3
import contextlib
from pathlib import Path
import logging


logger = logging.getLogger(__name__)


class DBHandler:
    def __init__(self, path: str = 'database.db'):
        """
        An object to handle the database requests

        Args:
            Path: The file path of the SQLite database.
        
        Attrs:
            db: This is the path to the SQLite database file.
        """
        self.db: str = path
        if not Path(path).exists():
            self.create_db()
    
    def add_gig_scraping_job(self, bot_used: str, duration: int, gigs: list[dict[str, str]]) -> None:
        """ 
        Adds a scraping job to the database.

        Args:
            gigs: This is a list of dictionaries which contain one gig each.
            bot_used: The bot used to scrape the data.
            duration: The time to complete the scraping job (in seconds).
        """
        job_query = '''
            insert into jobs
            (duration, bot_used)
            values
            (:duration, :bot_used);
        '''
        gig_query = '''
            insert into gig_data
            (job_id, gig_id, title, comp_message, comp_estimate)
            values
            (:job_id, :gig_id, :title, :comp_message, :comp_estimate);
        ''' 

        with contextlib.closing(sqlite3.connect(self.db)) as conn:
            try:
                cur = conn.cursor()
                cur.execute('begin')

                cur.execute(job_query, {'duration': duration, 'bot_used': bot_used})
                self.update_gigs_with_job_id(gigs, job_id=cur.lastrowid)
                cur.executemany(gig_query, gigs)

            except Exception as e:
                conn.rollback()
                raise e
            
            else:
                conn.commit()
                logger.info('Finished updating database')
            
            finally:
                cur.close()

    @staticmethod
    def update_gigs_with_job_id(gigs: list[dict[str, str]], *, job_id: int) -> None:
        """
        Update each row with the new job id (part of the composite primary key).

        Args:
            gigs: A list of gigs,
            job_id: The primary key of the newly created job in the "jobs" table.
        """
        for gig in gigs:
            gig['job_id'] = job_id

    def create_db(self) -> None:
        """
        Creates a new SQLite database with the correct schema.
        I took this code from an article I wrote about user authentication.
        """
        self.create_connection()
        self.create_table()

        logger.info(f'Created new database at {self.db}')

    def create_connection(self) -> None:
        """ Create a database connection to a SQLite database """
        try:
            conn = sqlite3.connect(self.db)
        finally:
            conn.close()

    def create_table(self) -> None:
        """ Creates a simple schema to store gig data """
        queries = [
            '''
            create table if not exists jobs (
                id integer primary key autoincrement, 
                duration text,
                bot_used text,
                date_scraped text default current_timestamp
            );
            ''',
            '''
            create table if not exists gig_data (
                job_id integer,
                gig_id integer,
                title text,
                comp_message text,
                comp_estimate integer,
                foreign key (job_id) references jobs(job_id),
                primary key (job_id, gig_id)
            );
            '''
        ] 

        with contextlib.closing(sqlite3.connect(self.db)) as conn:
            with conn:
                for query in queries:
                    conn.execute(query)