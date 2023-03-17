import asyncio
import datetime
from typing import Any, Callable, Awaitable

from aiohttp import web

from diffcord import InvalidTokenException
from diffcord.api import HTTPApi
from diffcord.vote import UserVoteInformation, UserBotVote


class VoteWebhookListener:
    """ Handles incoming POST requests from Diffcord.
    """

    def __init__(self, port: int, handle_vote: Callable[[UserBotVote], Awaitable[None]], host: str = None,
                 silent: bool = False,
                 verify_code: str = None, listener_sleep: int = 60):
        self.port = port
        self.handle_vote = handle_vote
        self.silent = silent
        self.verify_code = verify_code
        self.listener_sleep = listener_sleep
        self.__app = web.Application()
        self.__server = None

        if host is None:
            self.host = "0.0.0.0"
        else:
            self.host = host

    async def start(self) -> None:
        """ Start the webhook listener.
        """
        self.__app.router.add_post("/", self.handle_vote_webhook)

        app = web.AppRunner(self.__app)

        await app.setup()

        self.__server = web.TCPSite(app, self.host, self.port)
        await self.__server.start()

        if not self.silent:
            print("Diffcord webhook listener started. Listening on port", self.port)

    async def handle_vote_webhook(self, request: web.Request) -> web.Response:
        """ Handle the POST request from Diffcord.
        """
        if self.verify_code is not None and request.headers.get("Authorization") != self.verify_code:
            return web.Response(status=403)

        payload = await request.json()

        try:
            await self.handle_vote(UserBotVote(**payload))
        except Exception as e:
            if not self.silent:
                print("Error handling vote:", e)

            return web.Response(status=500)

        return web.Response(status=200)

    def __repr__(self):
        return f"<WebhookListener port={self.port}>"

    def __str__(self):
        return self.__repr__()


class Client(HTTPApi):
    """ Represents a client connection to the Diffcord API.
    """
    __SEND_STATS_SLEEP_DURATION = datetime.timedelta(hours=1)

    def __init__(self, bot: Any, token: str, vote_listener: VoteWebhookListener, send_stats: bool = True,
                 send_stats_success: Callable[[], Awaitable[None]] = None,
                 send_stats_failure: Callable[[Exception], Awaitable[None]] = None) -> None:
        """ Initialize a Client object.
        :param: bot: The bot object
        :param: token: Diffcord API token
        :param: vote_listener: The webhook vote listener which listens to incoming vote webhooks from Diffcord
        :param: send_stats: Whether to send bot stats to Diffcord
        :param: send_stats_success: A function to call when sending stats to Diffcord is successful
        :param: send_stats_failure: A function to call when sending stats to Diffcord fails
        """
        super().__init__(token)
        self.bot = bot
        self.token = token
        self.vote_listener = vote_listener
        self.send_stats = send_stats
        self.send_stats_success = send_stats_success
        self.send_stats_failure = send_stats_failure

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

    async def __update_bot_stats(self, guild_count: int) -> None:
        """ Update bot stats
        :param: guild_count: The new guild count
        """
        await self.make_request("POST", "/v1/stats", params={"guilds": guild_count})

    async def start(self) -> None:
        """ Start the client
        """
        # start listener for incoming votes
        await self.vote_listener.start()

        # make a request to validate the token

        try:
            await self.bot_votes_this_month()
        except InvalidTokenException:
            raise InvalidTokenException("Invalid Diffcord API token provided")

        if self.send_stats:

            # send stats to Diffcord
            while True:

                try:
                    await self.__update_bot_stats(guild_count=len(self.bot.guilds))
                except Exception as e:
                    if self.send_stats_failure is not None:
                        await self.send_stats_failure(e)
                else:
                    if self.send_stats_success is not None:
                        await self.send_stats_success()

                await asyncio.sleep(Client.__SEND_STATS_SLEEP_DURATION.total_seconds())

    def __repr__(self):
        return f"<Client bot={self.bot} token={self.token}>"

    def __str__(self):
        return self.__repr__()
