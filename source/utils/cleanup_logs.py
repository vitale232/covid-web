from datetime import datetime, timedelta
import os
from pprint import pprint
import re


def main():
    start_time = datetime.now()
    print(f'\nRunning script : {os.path.abspath(__file__)}')
    print(f'Start time     : {start_time}')

    delete_delta = timedelta(days=14)

    log_file_regex = re.compile(
        '^log_(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})_' +
        '(?P<hour>\d{2})(?P<minute>\d{2})(?P<second>\d{2})$'
    )
    logs_dir = os.path.abspath(os.path.join(
        os.path.dirname(__file__),
        '..',
        '..',
        'logs'
    ))

    nyt_logs_dir = os.path.join(logs_dir, 'nyt')
    peese_logs_dir = os.path.join(logs_dir, 'peese')
    utils_logs_dir = os.path.join(logs_dir, 'utils')

    log_files = [
        os.path.join(nyt_logs_dir, file_) for file_ in os.listdir(nyt_logs_dir)
    ] + [
        os.path.join(peese_logs_dir, file_) for file_ in os.listdir(peese_logs_dir)
    ] + [
        os.path.join(utils_logs_dir, file_) for file_ in os.listdir(utils_logs_dir)
    ]

    print(f'\nScanning log dir for files older than {delete_delta}:\n Log Dir : {nyt_logs_dir}')
    deleted_logs = []
    for log_file in log_files:
        base_log_file = os.path.basename(log_file)
        match = log_file_regex.match(base_log_file)
        if not match:
            print(f'  Skip   : {log_file}')
            continue
        match_data = match.groupdict()
        log_datetime = datetime(
            year=int(match_data['year']),
            month=int(match_data['month']),
            day=int(match_data['day']),
            hour=int(match_data['hour']),
            minute=int(match_data['minute']),
            second=int(match_data['second'])
        )

        log_age = start_time - log_datetime
        if log_age > delete_delta:
            deleted_logs.append(log_file)
            print(f'  Delete : {log_file}')
            os.remove(log_file)
        else:
            print(f'  Skip   : {log_file}')
            continue

    print('\nDeleted the following log files:')
    pprint(deleted_logs)

    end_time = datetime.now()
    print(f'\nScript completed : {end_time}')
    print(f'Run time         : {end_time-start_time}\n')


if __name__ == '__main__':
    main()
