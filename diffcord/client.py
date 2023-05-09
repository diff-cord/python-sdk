import json
from typing import Union
import asyncio
import datetime
from typing import Any, Callable, Awaitable

from diffcord import InvalidTokenException
from diffcord.api import HTTPApi
from diffcord.vote import UserVoteInformation, UserBotVote

import tornado.ioloop
import tornado.web
from tornado.httpserver import HTTPServer
import logging


class VoteWebhookListener:
    """ Handles incoming POST requests from Diffcord.
    """

    def __init__(self, port: int, handle_vote: Callable[[UserBotVote], Awaitable[None]], host: str = None,
                 silent: bool = False, verify_code: str = None, listener_sleep: int = 60,
                 log_level: int = logging.CRITICAL):
        self.port = port
        """ The port of the webhook listener. """

        self.handle_vote = handle_vote
        """ The function that will be called when a vote is received. (must be async with one parameter which is of type UserBotVote) """

        self.silent = silent
        """ Whether to print various httpserver messages to the console. """

        self.verify_code = verify_code
        """ The verification code for the webhook listener. """

        self.listener_sleep = listener_sleep
        """ The amount of time to sleep between each stat update. """

        self.log_level = log_level
        """ The log level of the httpserver. """

        self.host = host
        """ The host of the webhook listener. """

        if host is None:
            self.host = "0.0.0.0"

        self.__app = tornado.web.Application([(r"/", self.__handler_class(self.handle_vote))], debug=False)
        self.__server = HTTPServer(self.__app)
        self.__server.bind(self.port, self.host)

    def __handler_class(self, handler):

        verify_code = self.verify_code
        silent = self.silent

        class Handler(tornado.web.RequestHandler):

            VERIFY_CODE = verify_code
            SILENT = silent

            async def post(self):
                if self.VERIFY_CODE is not None and self.request.headers.get("Authorization") != self.VERIFY_CODE:
                    self.set_status(403)
                    return

                # payload as dict
                payload = json.loads(self.request.body.decode("utf-8"))

                vote = UserBotVote(**payload)

                try:
                    await handler(vote)
                except Exception as e:
                    if not self.SILENT:
                        print("Error handling vote:", e)

                    self.set_status(500)
                    return

                self.set_status(200)

        return Handler

    async def start(self) -> None:
        """ Start the webhook listener.
        """
        logging.getLogger("tornado.access").setLevel(self.log_level)

        self.__server.start()

        if not self.silent:
            print("Webhook listener started on port", self.port)

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
                 send_stats_failure: Callable[[Exception], Awaitable[None]] = None, base_url: str = None) -> None:
        super().__init__(token, "https://www.diffcord.com/api" if base_url is None else base_url)

        self.bot: Any = bot
        """ The bot object. """

        self.token: str = token
        """ The Diffcord API token. """

        self.vote_listener: VoteWebhookListener = vote_listener
        """ The webhook vote listener which listens to incoming vote webhooks from Diffcord. """

        self.send_stats: bool = send_stats
        """ Whether to send bot stats to Diffcord. """

        self.send_stats_success: Callable[[], Awaitable[None]] = send_stats_success
        """ A function to call when sending stats to Diffcord is successful (must be async). """

        self.send_stats_failure: Callable[[Exception], Awaitable[None]] = send_stats_failure
        """ A function to call when sending stats to Diffcord fails (must be async). """

    async def get_user_vote_info(self, user_id: Union[str, int]) -> UserVoteInformation:
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
        if self.vote_listener is not None:
            await self.vote_listener.start()

        # make a request to validate the token
        try:
            await self.bot_votes_this_month()
        except InvalidTokenException:
            raise InvalidTokenException(error={"message": "Invalid token provided.", "code": "ERR_INVALID_API_KEY"},
                                        response=None)

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
