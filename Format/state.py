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
from datetime import datetime
import pickle
from typing import Any, TextIO, Union

# Import external dependencies
import aiofiles


def parsed_json_stats(json: dict[str, Any]) -> dict[str, Union[int, str]]:
    """Parse json data from v4/data.min.json"""
    confirmed = json["total"].get("confirmed", 0)
    recovered = json["total"].get("recovered", 0)
    deaths = json["total"].get("deceased", 0)
    other = json["total"].get("other", 0)
    active = confirmed - recovered - deaths - other

    if "last_updated" in json["meta"]:
        last_updated = datetime.fromisoformat(json["meta"]["last_updated"])
        last_updated_str = last_updated.strftime("%d/%m/%Y %H:%M:%S")
    else:
        last_updated = None
        last_updated_str = ""

    notes = json["meta"].get("notes", "")

    date = json["meta"].get("date", None)
    date = None if date is None else datetime.strptime(date, "%Y-%m-%d").date()
    today = datetime.today().date()

    if (
        "delta" in json  # Don't go ahead if it won't exist
        and date is not None
        and (  # Get only today's data or the prev day data if last_upd < 9 AM
            date == today
            or (
                last_updated is not None
                and (today - date).days == 1
                and (  # Show the previous day stats (if available) till 9 AM
                    last_updated.date() != today
                    or last_updated.hour < 9
                )
            )  # End of or condition
        )
    ):  # End of if condition
        new_cases = json["delta"].get("confirmed", 0)
        new_recoveries = json["delta"].get("recovered", 0)
        new_deaths = json["delta"].get("deceased", 0)
    else:
        new_cases = 0
        new_recoveries = 0
        new_deaths = 0

    return {
        "confirmed": confirmed,
        "recovered": recovered,
        "deaths": deaths,
        "active": active,
        "new_cases": new_cases,
        "new_recoveries": new_recoveries,
        "new_deaths": new_deaths,
        "last_updated": last_updated_str,
        "notes": notes
    }
# End of parsed_json_stats()


async def format_state_stats(
    state_csv: TextIO,
    state_json: dict[str, Any]
) -> dict[str, dict[str, Union[int, str]]]:
    """Make dicts for each state containing the stats"""

    state_stats = {}

    path = "./Cogs/Utility/Covid/Format/Old_notes/state.pickle"
    async with aiofiles.open(path, "rb") as f:
        old_notes = pickle.loads(await f.read())

    state_csv.seek(0)
    for row in csv.DictReader(state_csv):
        state = row["State"]
        state_code = row["State_code"]

        if state_code in state_json:
            json_data = parsed_json_stats(state_json[state_code])
        else:
            json_data = None  # Use outdated data rather than having no data

        state_stats[state] = {
            "state": state,
            "state_code": state_code,

            # Use data from json instead of csv since csv isn't updated as of
            # 19th August, 2021 12:00:00 IST.

            # "confirmed": row["Confirmed"],
            # "recovered": row["Recovered"],
            # "deaths": row["Deaths"],
            # "active": row["Active"],

            # "new_cases": row["Delta_Confirmed"],
            # "new_recoveries": row["Delta_Recovered"],
            # "new_deaths": row["Delta_Deaths"],

            # "last_updated": row["Last_Updated_Time"],
            # "notes": row["State_Notes"]

            "confirmed": (json_data["confirmed"] if json_data is not None
                          else row["Confirmed"]),  # row has csv data
            "recovered": (json_data["recovered"] if json_data is not None
                          else row["Recovered"]),
            "deaths": (json_data["deaths"] if json_data is not None
                       else row["Deaths"]),
            "active": (json_data["active"] if json_data is not None
                       else row["Active"]),

            "new_cases": (json_data["new_cases"] if json_data is not None
                          else row["Delta_Confirmed"]),
            "new_recoveries": (row["Delta_Recovered"] if json_data is None
                               else json_data["new_recoveries"]),
            "new_deaths": (json_data["new_deaths"] if json_data is not None
                           else row["Delta_Deaths"]),

            "last_updated": (json_data["last_updated"] if json_data is not None
                             else row["Last_Updated_Time"]),
            "notes": (json_data["notes"] if json_data is not None
                      else row["State_Notes"]),
        }

        if state in old_notes:
            state_stats[state]["notes"] = (
                state_stats[state]["notes"].removesuffix(old_notes[state])
            )

    return state_stats
# End of format_state_stats()


# End of file
