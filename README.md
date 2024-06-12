# Discord Bot for Sloopertroup
This is a fork of a [bot originally by Ladder Dogs](https://github.com/azjps/ladder_dogs_discord_bot)

Simple discord bot which manages puzzle channels for puzzle hunts via discord commands, used by a small-to-medium sized team.

This was initially created from [`cookiecutter-discord.py-postgres`](https://github.com/makupi/cookiecutter-discord.py-postgres) and uses [`aiogoogle`](https://aiogoogle.readthedocs.io/en/latest/)/[`gspread_asyncio`](https://gspread-asyncio.readthedocs.io/en/latest/index.html) for (optional) Google Drive integration.

To keep things very simple (and because I started this a week before Hunt starts), currently this is not using a postgres DB, and is just storing some simple puzzle metadata via JSON files and [`dataclasses_json`](https://pypi.org/project/dataclasses-json/). If this bot works well enough, might switch to postgres/gino/alembic for next time.

# Usage

## Creating a hunt

For example, run the command

`!hunt MysteryHunt2021:https://perpendicular.institute/`

This hunt URL will be used to guess the link to the puzzle when new puzzles are posted. If the generated
puzzle link is wrong, it can be updated by posting `!link https://correct-hunt-website-link` in the puzzle channel.

Users with the `manage_channel` role can update administrative settings via `!update_setting {key} {value}`, where
all of the settings can be viewed via `!show_settings`.

There are also various settings and links to Google Drive that should be updated prior to the start of hunt,
like

- `drive_parent_id`: the Google drive ID of the parent folder the hunt will be created under
- `drive_resources_id`: optional, Google drive ID of a resources Google doc
- `discord_bot_channel`: if set, most bot commands must be entered in that channel name
- `discord_use_voice_channels`: false by default; if true, voice channels are created alongside text channels

## During hunt

Most users will just need to become familiar with two commands:
1. To post a new puzzle channel, post `!p puzzle-name` in the `#meta` channel of the corresponding puzzle round.
   This will create a new text channel where puzzle discussion can take place, as well as
   a new Google Spreadsheet with a handy `Quick Links` worksheet.
   You can scroll the sidebar or use `Ctrl + K` to help search for existing puzzle channels.
2. When Hunt HQ has confirmed that the puzzle has been solved, post `!solve SOLUTION` in the puzzle channel.
   The channels will be automatically archived afterwards.

----

For a new round/world of puzzles, first start by posting `!round` in the `#bot` channel:
```
!r puzzle-round-name
```
This will create a `#puzzleround-name` [category](https://support.discord.com/hc/en-us/articles/115001580171-Channel-Categories-101)
along with a `#meta` puzzle text for the round. The `#meta` channels are the place for general discussion about the round,
as well as discussion about the meta puzzle (if there is more than one meta, creating new puzzle channels would be prudent).

For a new puzzle, one can either post the puzzle via `!puzzle` in the `#bot` channel:
```
!p puzzle-round-name: puzzle-name
```
Or simply `!p puzzle-name` in the corresponding round's `#meta` channel. This will create a `#puzzle-name` text and voice channel
where discussion of the puzzle can take place.

When the puzzle is solved, post `!solve SOLUTION` in the puzzle's channel. The text channel will automatically get archived (moved
to the `#solved-puzzles` category) after ~5 minutes, and the voice channel will be deleted. If this is mistakenly entered,
this can be undone by posting `!unsolve`.

There are various other commands for updating the status, type, priority, and notes associated with a puzzle.
These fields are mainly for others to easily find out about the status of other puzzles. They can be retrieved
on the discord channels using the corresponding commands (see `!info` for the available commands), or viewed
in aggregate on the Nexus spreadsheet, where all puzzles and links are listed.

## Google Drive

When a puzzle channel is created, if Google Drive integration is enabled, a corresponding spreadsheet is created
in the folder for the puzzle round in the root Google Drive directory. The spreadsheet will have a secondary
"Quick Links" tab created for convenience.

![Puzzle spreadsheet Quick Links tab example](docs/gsheet_puzzle_quick_links.png)

The bot periodically updates a "nexus spreadsheet" which shows a list of all puzzles along with relevant information
such as the puzzle url, spreadsheet link. (The formatting of the nexus spreadsheet can be done manually by the user;
the bot only populates the contents of the spreadsheet cells.)

![Nexus spreadsheet example](docs/gsheet_nexus_example.png)

# Setup

Clone this repository
```
git clone https://github.com/sloop-puzzles/puzzlehunt-discordbot
```
Create a [discord application, bot](https://realpython.com/how-to-make-a-discord-bot-python/), and add the bot's token to a [`config.json` file](https://github.com/makupi/cookiecutter-discord.py-postgres/blob/master/%7B%7Bcookiecutter.bot_slug%7D%7D/config.json) in the root directory of this project:
```json
{
  "discord_bot_token": "{{discord_bot_token}}",
  "prefix": "!",
  "database": "postgresql://postgres:postgres@localhost:5432/postgres"
}
```
(The database URI can be omitted as its currently not supported.)

For the Google Drive integration (optional), create a [Google service account (for example see these instructions from `gspread`)](
https://gspread.readthedocs.io/en/latest/oauth2.html#enable-api-access), and save the service account key JSON file as `google_secrets.json`.

Now you can run the bot by running the following in a shell:
```bash
# Setup python3 environment
pip install pipenv
pipenv install  # creates a new virtualenv
pipenv shell
# Start bot
python run.py
```
The environment variable `$LADDER_SPOT_DATA_DIR` can be used to control the directory where guild settings and puzzle data are stored.

## Tests

Use `pipenv install --dev` to install dev packages, and in the repo root directory, run
```bash
python -m pytest
```

# Credits

Inspired by various open source discord bot python projects like [cookiecutter-discord.py-postgres](https://github.com/makupi/cookiecutter-discord.py-postgres) and [discord-pretty-help](https://github.com/stroupbslayen/discord-pretty-help/). Licensed under [GPL 3.0](https://choosealicense.com/licenses/gpl-3.0/) (due to the aforementioned `cookiecutter`).
