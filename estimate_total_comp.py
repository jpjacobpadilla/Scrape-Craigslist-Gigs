import sqlite3
import contextlib
import pathlib

JOB_ID: int = 1
DATABASE_FILE: str = 'database.db'

assert pathlib.Path(DATABASE_FILE).exists(), 'Incorrect database file.'

query = '''
    select sum(
            case
                when comp_estimate > 20000 then 0
                when comp_estimate > 1000 then comp_estimate / 40
                when comp_estimate > 200 then comp_estimate / 8
                else comp_estimate
            end
        ) as total_estimate_per_hour,
        sum(
            case
                when comp_estimate > 20000 then 0
                when comp_estimate > 1000 then 40
                when comp_estimate > 200 then 8
                else 1
            end
        ) as total_hours
    from gig_data
    inner join jobs on jobs.id=gig_data.job_id
    where jobs.id = :job_id;
'''

with(contextlib.closing(sqlite3.connect(DATABASE_FILE))) as conn:
    with conn:
        total, hours = conn.execute(query, {'job_id': JOB_ID}).fetchone()

print(f'If you worked 8 hours a day you could make around {(total / hours) * 8:.2f} dollars.')