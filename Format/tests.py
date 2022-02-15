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
from typing import TextIO, Union

# Import external dependencies
import pandas as pd

# Import helper function
from .timeseries_statewise import format_state_timeseries


def format_test_stats(
    tests_csv: TextIO,
    icmr_csv: TextIO
) -> dict[str, dict[str, Union[int, str]]]:
    """Make dicts for each state containing testing stats"""

    # First store state statistics, and then add national stats later
    test_stats = format_state_timeseries(
        statistics_csv=tests_csv, date_field="Updated On",
        statistic_required="Total Tested", source_field="Source1"
    )

    # Now parse national stats from ICMR csv

    icmr_csv.seek(0)
    icmr_df = pd.read_csv(icmr_csv,
                          parse_dates=["Tested As Of", "Update Time Stamp"],
                          dayfirst=True)

    # Sort by dates descending
    icmr_df.sort_values(by=["Tested As Of"], ascending=False, inplace=True)
    icmr_df.reset_index(drop=True, inplace=True)  # Top row = 0 index etc.

    # Get the index which has all the values, and more past => more guarantee
    first_index = max([
        icmr_df["Tested As Of"].first_valid_index(),
        icmr_df["Total Samples Tested"].first_valid_index(),
        icmr_df["Sample Reported today"].first_valid_index(),
        icmr_df["Source"].first_valid_index()
    ])

    test_stats["Total"] = {
        "date": icmr_df.iloc[first_index]["Tested As Of"].strftime("%d/%m/%Y"),
        "total": icmr_df.iloc[first_index]["Total Samples Tested"],
        "today": icmr_df.iloc[first_index]["Sample Reported today"],
        "source": icmr_df.iloc[first_index]["Source"]
    }

    # Both state and national stats are now added in the dict
    return test_stats
# End of format_test_stats()


# End of file
