import json
from pathlib import Path

from typing import Optional
from git import Repo
from google.oauth2.service_account import Credentials
from aiogoogle import Aiogoogle
from aiogoogle.auth.creds import ServiceAccountCreds

from . import config

creds = ServiceAccountCreds(
    scopes=["https://www.googleapis.com/auth/script.projects"],
    subject=config.owner_email,
    **json.load(open("google_secrets.json")),
)

async def create_project(parent_id: str) -> dict:
    aiogoogle = Aiogoogle(service_account_creds=creds)
    async with aiogoogle:
        scripts = await aiogoogle.discover("script", "v1")
        payload = {"title": "Puzzle Utils", "parentId": parent_id}
        result = await aiogoogle.as_service_account(
            scripts.projects.create(json=payload)
        )
    return result

async def add_javascript(script_id: str) -> dict:
    aiogoogle = Aiogoogle(service_account_creds=creds)
    async with aiogoogle:
        scripts = await aiogoogle.discover("script", "v1")
        content = await aiogoogle.as_service_account(
            scripts.projects.getContent(
                scriptId=script_id,
            )
        )
        payload = {"files": content["files"] }
        files.append({
            "name": "Code",
            "type": "SERVER_JS",
            "source": get_puzzle_addons_source(),
        })
        result = await aiogoogle.as_service_account(
            scripts.projects.updateContent(
                scriptId=script_id,
                json=payload,
            )
        )
    return result

def get_puzzle_addons_source(filename="Main.gs") -> str:
    if not config.puzzle_addons_path:
        return ""

    repo = Repo(config.puzzle_addons_path)
    repo.remotes.origin.pull()
    with open(Path(config.puzzle_addons_path) / filename, "r") as file:
        data = file.read()
    return data


