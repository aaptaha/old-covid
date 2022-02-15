###############################################################################

# Copyright (C) 2022  Gouenji Shuuya

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# The online repository may be found at <https://github.com/aaptaha/old-covid>.

###############################################################################


# Import standard library dependencies
from io import StringIO

# Import external dependencies
import aiohttp
import pendulum

# Import helper/formatter functions
from .Format.state import format_state_stats
from .Format.district import format_district_stats
from .Format.tests import format_test_stats
from .Format.vaccination import format_vaccination_stats


async def covid_stats_update(self, *, restart_loop: bool = False) -> None:
    """Fetches latest data from covid19india.org API."""

    # URLs for getting data
    host = "https://data.covid19india.org/csv/latest/"
    state_url = host + "state_wise.csv"
    district_url = host + "district_wise.csv"
    tests_url = host + "statewise_tested_numbers_data.csv"
    icmr_url = host + "tested_numbers_icmr_data.csv"
    vaccination_url = host + "vaccine_doses_statewise_v2.csv"

    # state_wise.csv has not been updated for a week, so use json
    state_json_url = "https://data.covid19india.org/v4/min/data.min.json"

    # Now fetch the data
    async with aiohttp.ClientSession() as session:
        # Get state-wise and national case data
        async with session.get(state_url) as resp:
            state_csv = StringIO(await resp.text())

        async with session.get(state_json_url) as resp:
            state_json = await resp.json()

        # Get district-wise data
        async with session.get(district_url) as resp:
            district_csv = StringIO(await resp.text())

        # Get testing data for all states
        async with session.get(tests_url) as resp:
            tests_csv = StringIO(await resp.text())

        # Get national (India's) testing data from ICMR csv
        async with session.get(icmr_url) as resp:
            icmr_csv = StringIO(await resp.text())

        # Get data on vaccine doses administered in a state
        async with session.get(vaccination_url) as resp:
            vaccination_csv = StringIO(await resp.text())

    # Format and store the data
    self.covid_state_stats = await format_state_stats(state_csv, state_json)
    self.covid_district_stats = await format_district_stats(district_csv)
    self.covid_test_stats = format_test_stats(tests_csv, icmr_csv)
    self.covid_vaccination_stats = format_vaccination_stats(vaccination_csv)

    # Make state code -> state mapping
    self.covid_state_codes = {}
    for state, state_data in self.covid_state_stats.items():
        state_code = state_data["state_code"]
        self.covid_state_codes[state_code] = state

    # Set the time of last fetch
    self.covid_last_fetched = pendulum.now()

    # Restart the update task loop of the cog if requested
    # This is put at the end instead of start so that data is at least fetched
    # once when called.
    if restart_loop:
        if self.corona_stats_update.is_running():
            self.corona_stats_update.restart()
        else:
            self.corona_stats_update.start()
# End of covid_stats_update()


# End of file
