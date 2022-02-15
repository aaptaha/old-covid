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


def format_state_timeseries(
    *,
    statistics_csv: TextIO,
    date_field: str,
    statistic_required: str,
    source_field: str = None
) -> dict[str, dict[str, Union[int, str]]]:
    """
    Make dicts for each state with csv containing the stats in timeseries.
    That is, every row of CSV has data for a particular date and state.
    """
    columns_needed = ["State", date_field, statistic_required]
    if source_field is not None:
        columns_needed.append(source_field)

    statistics_csv.seek(0)
    statistics_df = pd.read_csv(statistics_csv, parse_dates=[date_field],
                                dayfirst=True, usecols=columns_needed)

    # Sort by dates descending
    statistics_df.sort_values(by=[date_field], ascending=False, inplace=True)

    statistics = {}

    for state in statistics_df["State"].unique():
        state_df = statistics_df[statistics_df["State"] == state]
        state_df.reset_index(drop=True, inplace=True)  # Top row = 0 index etc.

        first_index = state_df[statistic_required].first_valid_index()

        if isinstance(first_index, int):
            next_index = first_index + 1

            date_total = state_df.iloc[first_index][date_field]
            stats_total = int(state_df.iloc[first_index][statistic_required])
            stats_prev = state_df.iloc[next_index][statistic_required]

            if pd.isnull(stats_prev):
                stats_today = ""
            else:
                stats_today = stats_total - int(stats_prev)

            statistics[state] = {
                "date": (date_total if isinstance(date_total, str)
                         else date_total.strftime("%d/%m/%Y")),
                "total": stats_total,
                "today": stats_today,
                "source": (None if source_field is None
                           else state_df.iloc[first_index][source_field])
            }

            # TODO: Investigate! date_total was str once, but that should not
            # happen. The above is just a dirty fix.

    return statistics
# End of format_state_timeseries()


# End of file
