from typing import List, Tuple


def group_tickers(
    tickers: List[str], increment: int = 5
) -> Tuple[List[str], List[str]]:
    """return of five tickers and returns those in message format"""
    group_to_work = tickers[:increment]
    remaining_tickers = tickers[increment:]
    return group_to_work, remaining_tickers


test = [1, 2, 3, 4, 5, 6]
test_1 = [6]
print(group_tickers(test_1))
