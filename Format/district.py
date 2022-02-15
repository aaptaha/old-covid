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
import csv
import pickle
from typing import TextIO, Union

# Import external dependencies
import aiofiles


async def format_district_stats(
    district_csv: TextIO
) -> dict[str, dict[str, Union[dict[str, Union[int, str]], int, str]]]:
    """Make dicts for each district containing the stats"""
    # We first create a dict of lists pertaining to each district name, so that
    # each value will be a list containing different dicts corresponding to the
    # states having district name under consideration.
    # Then from the dict of lists, we will create a potential dict of dicts,
    # with the inner data being the district data if district name is unique
    # across India, otherwise inner data will be labelled with keys pertaining
    # to the state name and the value being the normal dict containing data

    district_stats_list = {}

    path = "./Cogs/Utility/Covid/Format/Old_notes/district.pickle"
    async with aiofiles.open(path, "rb") as f:
        old_notes = pickle.loads(await f.read())

    district_csv.seek(0)
    for row in csv.DictReader(district_csv):

        district = row["District"]

        if district not in district_stats_list:
            district_stats_list[district] = []

        current_district_stats = {
            "district": district,

            "state": row["State"],
            "state_code": row["State_Code"],
            "district_key": row["District_Key"],

            "confirmed": row["Confirmed"],
            "active": row["Active"],
            "recovered": row["Recovered"],
            "deaths": row["Deceased"],

            "new_cases": row["Delta_Confirmed"],
            "new_active": row["Delta_Active"],
            "new_recoveries": row["Delta_Recovered"],
            "new_deaths": row["Delta_Deceased"],

            "notes": row["District_Notes"],
            "last_updated": row["Last_Updated"],
        }

        if (key := current_district_stats["district_key"]) in old_notes:
            current_district_stats["notes"] = (
                current_district_stats["notes"].removesuffix(old_notes[key])
            )

        district_stats_list[district].append(current_district_stats.copy())

    district_stats_dict = {}

    for district, district_list in district_stats_list.items():
        if len(district_list) == 1:  # Only one district with that name
            district_stats_dict[district] = district_list[0]

        else:  # Multiple districts with same name
            state_dict = {}  # Store with key = state name
            for district_stat in district_list:
                state_dict[district_stat["state"]] = district_stat

            district_stats_dict[district] = state_dict

    return district_stats_dict
# End of format_district_stats()


# End of file
