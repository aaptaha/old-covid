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
from inspect import cleandoc

# Import external dependencies
import pendulum

# Import discord.py stuff
from discord.ext import commands

# Import factory functions
from Factory.embed import create_embed
from Factory.numbers import format_number  # Just adds commas and sign here.

# Import helper functions
from .covid_stats_update import covid_stats_update
from .Statistics.state import get_state_stats
from .Statistics.district import get_district_stats


# Define strings to use later
DESCRIPTION_COVID = cleandoc("""
Get COVID-19 statistics for India (both national and state statistics).

Usage: `@@covid <optional state/UT name/full district name>.`

Examples:
```
@@covid --> Would send national statistics.
@@covid Odisha --> Would send statistics for Odisha.
@@covid UK --> Would send statistics for Uttarakhand.
@@covid maharashtra --> Would send statistics for Maharashtra.
@@covid tn --> Would send statistics for Tamil Nadu.
```
```
@@covid Gurugram --> Would send statistics for Gurugram, Haryana.
@@covid Aurangabad, br --> Would send statistics for Aurangabad, Bihar.
@@covid aurangabad, mh --> Would send statistics for Maharashtra one.
``` \

Bot fetches data every 15 minutes from API provided by covid19india.org.

To prevent spam, there's a cooldown period of 5 seconds for users.
""")


# Command decorators
@commands.cooldown(1, 5, commands.BucketType.member)
@commands.command(
    name="covid",
    description=DESCRIPTION_COVID,
    brief="Get COVID-19 statistics for India",
    aliases=["corona", "कोरोना", "कोविड"]
)
@commands.guild_only()
# Command definition starts
async def corona(
    self, ctx: commands.Context,
    *, location: str = "Total"
) -> None:

    # Check if we have data (See last variable set in update loop)
    if not hasattr(self, "covid_state_codes"):
        fail = "Try again after some time.\nFetching data..."
        await ctx.send(embed=create_embed(ctx, error=True, description=fail))
        self.corona_stats_update.start()  # Starts corona_stats_update() loop
        return

    # Allow owner to force update
    if self.bot.owner_id == ctx.author.id and location == "--force-update":
        await ctx.send("Okay, fetching....")
        await covid_stats_update(self, restart_loop=True)
        await ctx.send("Fetched.")
        return

    # If the fetch task failed/stopped, we need to start it back
    # We can determine it stopped, if it didn't update after 15 minutes
    if pendulum.now().subtract(minutes=15) > self.covid_last_fetched:
        msg = await ctx.send("Seems like I had problems fetching data. "
                             "Fetching again...\nIf this problem "
                             "persists, please report in the meta server.")
        await covid_stats_update(self, restart_loop=True)
        await msg.delete()

    # Capitalise starting letter of each word (except "and")
    location = location.lower().title().replace(" And ", " and ")

    num_plate_codes = {
        # State codes to state (capitalised first letter in line with above)
        "Uk": "Uttarakhand",
        "Cg": "Chhattisgarh",
        "Ts": "Telangana",
        "Dd": "Dadara and Nagar Haveli and Daman and Diu"
    }

    district = False  # If a district's data is requested

    # Note: National statistics are assigned state "Total"
    # Replace "India" with "Total" if someone tries to specify state as India
    if location == "India":
        location = "Total"
    elif location == "Unassigned":  # Since this seems to be a practical query
        location = "State Unassigned"
    elif "," in location:  # State name supplied with given district
        district = True
    elif location in num_plate_codes:
        location = num_plate_codes[location]

    stats, state_stats = None, None

    # Now get data

    if district:  # Inferred query to be district, so get district stats
        district_name = location.split(",")[0].strip(" ")
        state = location.split(",")[1].strip(" ")

        if state in num_plate_codes:
            state = num_plate_codes[state]

        stats = get_district_stats(self, district_name, state)

        if stats is not None:
            # Get data related to the state of district
            state_stats = get_state_stats(self, stats["state"])
        else:
            fail = (f"District `{location}` doesn't exist! Make sure to:\n"
                    "- Specify full name of the district,\n"
                    "- Specify correct district + state combo, and\n"
                    "- Remember P.O. names aren't called districts.")
            await ctx.send(embed=create_embed(ctx, error=True,
                                              description=fail))
            return

    else:  # No comma in location, so try both state and district
        stats = get_state_stats(self, location)

        if stats is None:  # No data found for state, try district
            stats = get_district_stats(self, location)

            if stats is not None:
                # Get data related to the state of district
                state_stats = get_state_stats(self, stats["state"])
                district = True
            else:
                # No state or district found for the given query
                fail = (f"State/Union Territory/District `{location}` "
                        "doesn't exist!\nIf you meant to search a "
                        "district, use its full name. Note that P.O. "
                        "names aren't called districts.")
                await ctx.send(embed=create_embed(ctx, error=True,
                                                  description=fail))
                return

        else:  # We have the state stats
            state_stats = stats

    # Now, make the embed to send data

    title = "COVID-19 statistics for "
    if district:
        title += stats["district"] + ", " + stats["state"]
    elif stats["state"] == "Total":
        title += "India"
    else:
        title += stats["state"]

    description = cleandoc("""
        • Follow the precautions strictly & cooperate with authorities.
        • Strive to encourage vaccination irrespective of brand.
        • Refrain from spreading panic and misinformation.
        \u200b
    """)  # Used \u200b to add newline in end

    last_fetched = ("⦿ Last fetched from API "
                    f"{ self.covid_last_fetched.diff_for_humans() }.")
    # Difference between now and covid_last_updated time with "ago" text

    data = create_embed(ctx, title=title, description=description,
                        footer=f"+{last_fetched}",
                        thumbnail=self.get_asset_url("yellow_biohazard.png"))

    # Now, add embed fields corresponding to the data

    rec_val = format_number(stats["recovered"])
    data.add_field(name="**😊 Recovered**", value=rec_val)

    deaths_val = format_number(stats["deaths"])
    data.add_field(name="**🇫 Deceased**", value=deaths_val)

    daily_inf_val = format_number(stats["new_cases"])
    data.add_field(name="**📊 Infected today**", value=daily_inf_val)

    daily_rcv_val = format_number(stats["new_recoveries"])
    data.add_field(name="**📊 Cured today**", value=daily_rcv_val)

    daily_deaths_val = format_number(stats["new_deaths"])
    data.add_field(name="**📊 Departed today**", value=daily_deaths_val)

    # Add active cases stats at start, with increase in parentheses
    if district:
        up = stats["new_active"]
    else:
        up = (int(stats["new_cases"]) - int(stats["new_recoveries"])
              - int(stats["new_deaths"]))
    active_cases = format_number(stats["active"])
    active_cases += " (" + format_number(up, sign_req=True) + ")"
    data.insert_field_at(0, name="**🤒 Active cases**", value=active_cases)

    # Helper function

    def no_data_available(data: str) -> str:
        """Use if no data available for testing, vaccination, etc."""

        no_data = f"No {data} data currently available for this state/UT. "
        no_data += "Try again after "

        when_upd = self.covid_last_fetched.diff_for_humans().split(" ")[0]

        if "minute" in self.covid_last_fetched.diff_for_humans():
            when_upd = 15 - int(when_upd)
        else:  # Takes care of the "a few seconds ago" case
            when_upd = 15

        no_data += f"{when_upd} minutes when data will be fetched again."

        return no_data
    # End of no_data_available()

    state = state_stats["state"]

    # Add state's testing data

    if state not in self.covid_test_stats:
        tests_val = no_data_available("testing")
    else:
        tests = self.covid_test_stats[state]
        tests_val = format_number(tests["total"]) + " "

        if increase := tests["today"]:  # Not an empty string
            tests_val += "(" + format_number(increase, sign_req=True) + ") "

        tests_val += f"[[up to {tests['date']}]({tests['source']})]"

    if state == "Total":
        tests_place = "**🧪 Samples tested nationally**"
    elif state == "State Unassigned":
        tests_place = "**🧪 Samples tested not assigned to any state**"
    else:
        tests_place = f"**🧪 Samples tested in {state}**"

    data.add_field(name=tests_place, value=tests_val, inline=False)

    # Get the vaccine doses administered
    vaccine_val = ""

    if state not in self.covid_vaccination_stats:
        vaccination_stats = no_data_available("vaccination")
    else:
        vaccination_stats = self.covid_vaccination_stats[state]
        vaccine_val = format_number(vaccination_stats["total"]) + " "

        if increase := vaccination_stats["today"]:
            vaccine_val += "(" + format_number(increase, sign_req=True) + ") "

        vaccine_val += f"[up to {vaccination_stats['date']}]"

    if state == "Total":
        vaccine_location = "nationally"
    elif state == "State Unassigned":
        vaccine_location = "not assigned to any state"
    else:
        vaccine_location = "in " + state

    vaccine_name = f"**💉 Vaccine doses administered {vaccine_location}**"
    data.add_field(name=vaccine_name, value=vaccine_val, inline=False)

    total_cases = format_number(stats["confirmed"])
    data.add_field(name="**😷 Total cases**", value=total_cases)

    if stats["notes"]:  # Add notes at the start
        data.insert_field_at(0, name=f"**📝 Notes (for {location})**",
                             value=stats["notes"], inline=False)

    last_updated = "**⌛ Last updated "
    if state != "Total":
        last_updated += "(for " + state_stats["state_code"] + ") "
    last_updated += "on**"
    data.add_field(name=last_updated, value=state_stats["last_updated"])

    await ctx.send(embed=data)
# End of corona()


# End of file
