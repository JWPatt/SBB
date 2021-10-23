import sys


def status_bar_printer(count, total, suffix):
    """Prints status of an iterative process of known length.

    Args:
        count (int): The number of queries performed already
        total (int): The number of total destinations to be queried
        suffix (str): A bit of text at the end of the output

    Returns:
        None - prints status bar, percentage completion, and # of queries performed
    """
    sys.stdout.write('\r')
    progress = count / total * 20
    sys.stdout.write("[%-20s] %d%% - %i of %i %s" % ('=' * int(progress), progress * 5, count, total, suffix))
    sys.stdout.flush()


# def status_bar_printer(count, n_destinations):
#     """Prints status of OSRM queries: percentage and # of queries.
#
#     Args:
#         count (int): The number of queries performed already
#         n_destinations (int): The number of total destinations to be queried
#
#     Returns:
#         None - prints status bar, percentage completion, and # of queries performed
#     """
#     sys.stdout.write('\r')
#     progress = count / n_destinations * 20
#     sys.stdout.write("[%-20s] %d%% - No. queries: %i" % ('=' * int(progress), progress * 5, count))
#     sys.stdout.flush()