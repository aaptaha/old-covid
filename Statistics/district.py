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
from typing import Optional, Union


def get_district_stats(
    self,
    district: str,
    state: str = None
) -> Optional[dict[str, Union[int, str]]]:

    if not state or state == "state":  # Empty str, or "state" which is a key
        state = None            # in dict and is anyways not a valid state name

    if district not in self.covid_district_stats:
        # Given string not a district
        return None

    district_stats = self.covid_district_stats[district]

    correct_state = True  # Whether the given district + state combo exists

    if state is None:
        # No state given, i.e., state is None
        # Check if district exists in only one state, otherwise return
        # the stats for any arbitrary state
        if "state" not in district_stats:
            district_stats = next(iter(district_stats.values()))

    else:  # State given
        # There can be multiple dicts in district_stats
        # if a given district name can be found in two or more states.
        # For eg.: There is a district named Aurangabad in both
        #          Maharashtra and Bihar, so there will be 2 dict values
        #          with keys being the respective state name
        if state in district_stats:
            district_stats = district_stats[state]

        elif (state_code := state.upper()) in self.covid_state_codes:
            state = self.covid_state_codes[state_code]

            if state in district_stats:  # Multiple dicts in district_stats
                district_stats = district_stats[state]

            elif "state" in district_stats:  # District X only in 1 state
                if district_stats["state"] != state:
                    correct_state = False

            else:  # Aurangabad, Uttarakhand does not exist
                correct_state = False

        else:  # Invalid state name passed
            correct_state = False

    # Return the data
    return district_stats if correct_state else None
# End of get_district_stats()


# End of file
