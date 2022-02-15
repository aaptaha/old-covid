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


# Import helper function
from .timeseries_statewise import format_state_timeseries


def format_vaccination_stats(
    vaccination_csv: TextIO
) -> dict[str, dict[str, Union[int, str]]]:
    """Make dicts for each state containing vaccination stats"""

    return format_state_timeseries(
        statistics_csv=vaccination_csv, date_field="Vaccinated As of",
        statistic_required="Total Doses Administered"
    )
# End of format_vaccine_stats()


# End of file
