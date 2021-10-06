import sys


def status_bar_printer(count, total, suffix):
    """Prints status of OSRM queries: percentage and # of queries.

    Args:
        count (int): The number of queries performed already
        total (int): The number of total destinations to be queried

    Returns:
        None - prints status bar, percentage completion, and # of queries performed
    """
    sys.stdout.write('\r')
    progress = count / total * 20
    sys.stdout.write("[%-20s] %d%% - %i of %i %s" % ('=' * int(progress), progress * 5, count, total, suffix))
    sys.stdout.flush()
    #
    # progress = count / total * 20
    # print("[%-20s] %d%% - %i of %i" % ('=' * int(progress), progress * 5, count, total), end='\r')

