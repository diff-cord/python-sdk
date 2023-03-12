from diffcord.api import HTTPApi
from diffcord.vote import UserVoteInformation, UserBotVote


class Client(HTTPApi):
    """ Represents a client connection to the Diffcord API.
    """

    def __init__(self, bot, token: str):
        """ Initialize a Client object.
        :param: bot: The bot object
        :param: token: Diffcord API token
        """
        super().__init__(token)
        self.bot = bot
        self.token = token

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

    async def unrewarded_votes(self) -> list[UserBotVote]:
        """ Get a list of unrewarded votes.
        :return: A list of UserBotVote objects representing unrewarded votes
        """
        all_vote_info: list[dict] = await self.make_request("GET", "/v1/votes/unrewarded")
        return [UserBotVote(**vote_info) for vote_info in all_vote_info]

    async def acknowledge_vote_rewards(self, votes: list[UserBotVote]) -> int:
        """ Acknowledge rewards for a list of votes.
        :param: votes: A list of UserVoteInformation objects
        :return: The number of votes that were rewarded
        """
        vote_ids = [vote.vote_id for vote in votes]
        response: dict = await self.make_request("POST", "/v1/votes/unrewarded", json={"vote_ids": vote_ids})
        return response["users_rewarded"]

    async def acknowledge_all_vote_rewards(self) -> int:
        """ Acknowledge rewards for all votes.
        :return: The number of votes that were rewarded
        """
        response: dict = await self.make_request("POST", "/v1/votes/unrewarded/all")
        return response["users_rewarded"]

    async def update_guild_count(self) -> None:
        """ Update the guild count for this bot.
        """
        # TODO - an endpoint is not yet available for this
        raise NotImplementedError

    def __repr__(self):
        return f"<Client bot={self.bot} token={self.token}>"

    def __str__(self):
        return self.__repr__()
