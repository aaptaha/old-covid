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


def get_state_stats(self, state: str) -> Optional[dict[str, Union[int, str]]]:

    if state in self.covid_state_stats:
        return self.covid_state_stats[state]

    # Given string not a key, check if it's a state code

    if (code := state.upper()) in self.covid_state_codes:
        if (state := self.covid_state_codes[code]) in self.covid_state_stats:
            return self.covid_state_stats[state]

    # else not even a state code
    return None
# End of get_state_stats()


# End of file
