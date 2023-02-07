import enum
import time
from typing import Generator

import betconnect.resources


class SportEnum(enum.Enum):
    FOOTBALL = 10


def selection_generator(
    sport: SportEnum, client: betconnect.APIClient, delay_between_requests: float = 0.2
) -> Generator[betconnect.resources.SelectionsForMarket, None, None]:
    """
    For the given sport, iterate the active regions and for each region, iterate the active fixtures, then for each
    fixture iterate the active markets and yield the selections on that market

    :param sport: The sport as a SportEnum object
    :param client: A (logged in) betconnect client
    :param delay_between_requests: How many seconds to wait between making calls to selections_for_market
    :return: Yields betconnect SelectionsForMarket objects
    """
    try:
        from tqdm.auto import tqdm
    except ImportError:

        def tqdm(x, desc, leave, position):
            return x

    sport_id = sport.value
    active_regions = client.betting.active_regions(sport_id=sport_id)
    for active_region in tqdm(active_regions, desc="Regions", position=0):
        active_fixtures = client.betting.active_fixtures(
            sport_id=sport_id, region_id=active_region.region_id
        )
        for active_fixture in tqdm(
            active_fixtures, desc="Fixtures", leave=False, position=1
        ):
            active_markets = client.betting.active_markets(
                fixture_id=active_fixture.fixture_id
            )
            for active_market in tqdm(
                active_markets, desc="Markets", leave=False, position=2
            ):
                active_selections = client.betting.selections_for_market(
                    fixture_id=active_fixture.fixture_id,
                    market_type_id=active_market.market_type_id,
                )
                yield from active_selections
                time.sleep(delay_between_requests)
