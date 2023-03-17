from typing import Any, Callable

from aiohttp import web

from diffcord.api import HTTPApi
from diffcord.vote import UserVoteInformation, UserBotVote


class VoteWebhookListener:

    def __init__(self, port: int, handle_vote: Callable[[UserBotVote], None], host: str = None, silent: bool = False,
                 verify_code: str = None):
        self.port = port
        self.handle_vote = handle_vote
        self.silent = silent
        self.verify_code = verify_code

        if host is None:
            self.host = "0.0.0.0"

    async def start(self) -> None:
        """ Start the webhook listener.
        """
        app = web.Application()
        app.router.add_post("/", self.handle_vote_webhook)
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, self.host, self.port)
        await site.start()

        if not self.silent:
            print(f"Diffcord webhook listener started on {self.host}:{self.port}")

    async def handle_vote_webhook(self, request: web.Request) -> web.Response:
        """ Handle the POST request from Diffcord.
        """
        if self.verify_code is not None and request.headers.get("Authorization") != self.verify_code:
            return web.Response(status=403)

        payload = await request.json()

        try:
            self.handle_vote(UserBotVote(**payload["data"]))
        except:
            return web.Response(status=500)

        return web.Response(status=200)

    def __repr__(self):
        return f"<WebhookListener port={self.port}>"

    def __str__(self):
        return self.__repr__()


class Client(HTTPApi):
    """ Represents a client connection to the Diffcord API.
    """

    def __init__(self, bot: Any, token: str, vote_listener: VoteWebhookListener):
        """ Initialize a Client object.
        :param: bot: The bot object
        :param: token: Diffcord API token
        :param: vote_listener: The webhook vote listener which listens to incoming vote webhooks from Diffcord
        """
        super().__init__(token)
        self.bot = bot
        self.token = token
        self.vote_listener = vote_listener

    async def start(self) -> None:
        """ Start the client.
        """
        if self.vote_listener is not None:
            await self.vote_listener.start()

    async def get_user_vote_info(self, user_id: str | int) -> UserVoteInformation:
        """ Get the vote information for a user.
        :param: user_id: The id of the user whose vote information is being fetched
        :return: A UserVoteInformation object
        """
        vote_info: dict = await self.make_request("GET", f"/v1/users/{user_id}/votes")
        return UserVoteInformation(**vote_info)

    async def bot_votes_this_month(self) -> int:
        """ Get the number of votes this bot has received this month.
        :return: The number of votes this bot has received this month
        """
        bot_info: dict = await self.make_request("GET", f"/v1/votes")
        return bot_info["month_votes"]

    async def update_bot_stats(self, guild_count: int) -> None:
        """ Update bot stats
        :param: guild_count: The new guild count
        """
        await self.make_request("POST", "/v1/stats", params={"guilds": guild_count})

    def __repr__(self):
        return f"<Client bot={self.bot} token={self.token}>"

    def __str__(self):
        return self.__repr__()
