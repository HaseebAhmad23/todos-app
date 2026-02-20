import argparse
import datetime
import statistics
from collections import defaultdict
from datetime import timedelta


def parse_log_line(line):
    """Parse a log line: 'timestamp - method - url - status'."""
    try:
        parts = line.strip().split(' - ', 3)
        if len(parts) < 4:
            return None
        timestamp_str, method, url, status_part = parts[0], parts[1], parts[2], parts[3]
        timestamp = datetime.datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
        # Handle "200" or "200 OK" format
        status = int(status_part.split()[0])
        return timestamp, method, url, status
    except (ValueError, IndexError):
        return None


def parse_log_file(log_file, start_time, end_time):
    """Extract timestamps and status codes from log file in time range."""
    timestamps = []
    status_codes = defaultdict(int)

    with open(log_file, 'r') as f:
        for line in f:
            result = parse_log_line(line)
            if result:
                timestamp, _, _, status = result
                if start_time <= timestamp <= end_time:
                    timestamps.append(timestamp)
                    status_codes[status] += 1

    return timestamps, status_codes


def compute_statistics(timestamps):
    """Compute RPM statistics from timestamps."""
    if not timestamps:
        return 0, 0, 0, 0

    min_time = min(timestamps)
    max_time = max(timestamps)
    total_minutes = (max_time - min_time).total_seconds() / 60
    if total_minutes == 0:
        total_minutes = 1

    rpm = defaultdict(int)
    for timestamp in timestamps:
        minute = timestamp.replace(second=0, microsecond=0)
        rpm[minute] += 1

    rpm_values = list(rpm.values())
    max_rpm = max(rpm_values)
    avg_rpm = len(timestamps) / total_minutes
    perc_95_rpm = statistics.quantiles(rpm_values, n=100)[94]

    return max_rpm, avg_rpm, perc_95_rpm, total_minutes


def main():
    parser = argparse.ArgumentParser(description='Parse log file and compute statistics.')
    parser.add_argument('--from', dest='from_time', type=str, help='Start time (YYYY-MM-DD HH:MM:SS)')
    parser.add_argument('--to', dest='to_time', type=str, help='End time (YYYY-MM-DD HH:MM:SS)')
    parser.add_argument('--logfile', type=str, default='app.log', help='Path to log file')

    args = parser.parse_args()

    now = datetime.datetime.now()
    end_time = now
    start_time = now - timedelta(hours=1)

    if args.from_time:
        start_time = datetime.datetime.strptime(args.from_time, '%Y-%m-%d %H:%M:%S')
    if args.to_time:
        end_time = datetime.datetime.strptime(args.to_time, '%Y-%m-%d %H:%M:%S')

    timestamps, status_codes = parse_log_file(args.logfile, start_time, end_time)
    max_rpm, avg_rpm, perc_95_rpm, total_minutes = compute_statistics(timestamps)

    print(f'Statistics from {start_time} to {end_time}')
    print(f'Maximum RPM: {max_rpm}')
    print(f'Average RPM: {avg_rpm:.2f}')
    print(f'95 percentile RPM: {perc_95_rpm}')

    print('\nHTTP Status Code Rate per Minute:')
    for status, count in sorted(status_codes.items()):
        print(f'  Status {status}: {count / total_minutes:.2f} per minute')


if __name__ == '__main__':
    main()
