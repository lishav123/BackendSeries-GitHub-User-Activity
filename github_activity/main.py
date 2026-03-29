import asyncio
import itertools

import httpx
from httpx import AsyncClient
from rich import print
import argparse

parser = argparse.ArgumentParser(
    description="Fetch and beautifully display a user's recent GitHub activity."
)

parser.add_argument(
    "username",
    type=str,
    help="The GitHub username to look up (e.g., lishav123)"
)

args = parser.parse_args()

def parse(data: dict, count: int = 1) -> str:
    event_type = data.get("type")

    actor = data.get("actor", {}).get("login", "Unknown user")
    repo = data.get("repo", {}).get("name", "an unknown repository")

    # Pre-formatting for rich to keep the f-strings clean
    r_actor = f"[bold cyan]{actor}[/bold cyan]"
    r_repo = f"[bold blue]{repo}[/bold blue]"

    # A small helper string to append if an event happened multiple times consecutively
    times = f" ({count}x)" if count > 1 else ""

    if event_type == "CommitCommentEvent":
        return f"{r_actor} [yellow]commented on a commit{times} in[/yellow] {r_repo}"

    elif event_type == "CreateEvent":
        return f"{r_actor} [green]created{times}[/green] {r_repo}"

    elif event_type == "DeleteEvent":
        return f"{r_actor} [red]deleted a branch or tag{times} in[/red] {r_repo}"

    elif event_type == "DiscussionEvent":
        return f"{r_actor} [yellow]interacted with a discussion{times} in[/yellow] {r_repo}"

    elif event_type == "ForkEvent":
        return f"{r_actor} [green]forked{times}[/green] {r_repo}"

    elif event_type == "GollumEvent":
        return f"{r_actor} [yellow]created or updated a wiki page{times} in[/yellow] {r_repo}"

    elif event_type == "IssueCommentEvent":
        return f"{r_actor} [yellow]commented on an issue{times} in[/yellow] {r_repo}"

    elif event_type == "IssuesEvent":
        action = data.get("payload", {}).get("action", "interacted with")
        color = "green" if action == "opened" else "red" if action == "closed" else "yellow"
        return f"{r_actor} [{color}]{action} an issue{times} in[/{color}] {r_repo}"

    elif event_type == "MemberEvent":
        return f"{r_actor} [yellow]added or modified a collaborator{times} in[/yellow] {r_repo}"

    elif event_type == "PublicEvent":
        return f"{r_actor} [green]made public{times}[/green] {r_repo}"

    elif event_type == "PullRequestEvent":
        action = data.get("payload", {}).get("action", "interacted with")
        color = "green" if action == "opened" else "red" if action == "closed" else "yellow"
        return f"{r_actor} [{color}]{action} a pull request{times} in[/{color}] {r_repo}"

    elif event_type == "PullRequestReviewEvent":
        return f"{r_actor} [yellow]reviewed a pull request{times} in[/yellow] {r_repo}"

    elif event_type == "PullRequestReviewCommentEvent":
        return f"{r_actor} [yellow]commented on a pull request review{times} in[/yellow] {r_repo}"

    elif event_type == "PushEvent":
        if count > 1:
            return f"{r_actor} [yellow]pushed {count} commits to[/yellow] {r_repo}"
        return f"{r_actor} [yellow]pushed commits to[/yellow] {r_repo}"

    elif event_type == "ReleaseEvent":
        return f"{r_actor} [green]published a release{times} in[/green] {r_repo}"

    elif event_type == "WatchEvent":
        return f"{r_actor} [yellow]starred{times}[/yellow] {r_repo}"

    else:
        return f"{r_actor} [red]triggered a {event_type}{times} on[/red] {r_repo}"


async def fetchGh(name):
    async with AsyncClient() as client:
        response = await client.get(f"https://api.github.com/users/{name}/events")
        print(response.status_code)
        if response.status_code == 404:
            return ["[red]User not found, probably, Username Incorrect[/red]"]

        if response.status_code != 200:
            return ["[red]Something went wrong, try again[/red]"]

        events = response.json()

        # Helper to group by event type, repo, and action (so 'opened' isn't grouped with 'closed')
        def get_group_key(event):
            e_type = event.get("type")
            repo = event.get("repo", {}).get("name")
            action = event.get("payload", {}).get("action", "")
            return (e_type, repo, action)

        parsed_results = []

        # Group consecutive matching events
        for key, group in itertools.groupby(events, key=get_group_key):
            group_list = list(group)
            count = len(group_list)
            # Pass the first event of the group and how many times it repeated
            parsed_results.append(parse(group_list[0], count))

        return parsed_results


async def main():
    try:
        resps = await fetchGh(args.username)
    except httpx.ConnectError:
        resps = ["[red]Something is wrong with your internet connection![/red]"]

    for resp in resps:
        print(resp)

def cli():
    asyncio.run(main())

if __name__ == '__main__':
    cli()