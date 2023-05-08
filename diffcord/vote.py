import datetime


class UserBotVote:
    """  Represents a user vote for a bot.
    """

    def __init__(self, vote_id: str, user_id: str, bot_id: str, since_vote: str, rewarded: bool, test: bool,
                 monthly_votes: int):
        self.vote_id: str = vote_id
        """ The id of the vote. """

        self.user_id: int = int(user_id)
        """ The id of the user who has voted. """

        self.bot_id: int = int(bot_id)
        """ The id of the bot which the user has voted for. """

        self.since_voted: datetime.timedelta = datetime.timedelta(seconds=float(since_vote))
        """ Time when the user voted. """

        self.voted_at: datetime.datetime = datetime.datetime.utcnow() - self.since_voted
        """ Time when the user voted. 
        """

        self.rewarded: bool = rewarded
        """ Whether the user vote has been rewarded and/or acknowledged. """

        self.test: bool = test
        """ Whether this is a testing bot vote (sent as a test via bot/server api dashboard) or not. """

        self.monthly_votes: int = monthly_votes
        """ The number of votes this user has given this month. """

    @property
    def votes_this_month(self) -> int:
        """ Get the number of votes this user has given your bot this month.
        """
        return self.monthly_votes

    def __repr__(self):
        return f"<UserBotVote vote_id={self.vote_id} user_id={self.user_id} bot_id={self.bot_id} voted_at={self.voted_at} rewarded={self.rewarded} testing={self.test} votes={self.monthly_votes}>"

    def __str__(self):
        return self.__repr__()


class UserVoteInformation:
    """ Represents a user vote information.
    """

    def __init__(self, user_id: str, bot_id: str, monthly_votes: int, since_last_vote: int | None, until_next_vote: int):
        self.user_id: str = user_id
        """ The id of the target user. """

        self.bot_id: str = bot_id
        """ The id of the bot which the user has voted for. """

        self.monthly_votes: int = monthly_votes
        """ The number of votes this user has for the given bot this month. """

        self.since_last_vote: datetime.timedelta = datetime.timedelta(seconds=since_last_vote) if since_last_vote is not None else None
        """ Time in seconds since the last vote. """

        self.until_next_vote: datetime.timedelta = datetime.timedelta(seconds=until_next_vote)
        """ Time in seconds till the next vote. """

        self.last_vote: datetime.datetime = datetime.datetime.now() - self.since_last_vote if self.since_last_vote is not None else None
        """ The last time the user voted. """

        self.next_vote: datetime.datetime = datetime.datetime.now() + self.until_next_vote
        """ The next time the user can vote. """

    @property
    def can_vote(self) -> bool:
        """ Whether the user can vote or not.
        """
        return not self.until_next_vote or self.until_next_vote.total_seconds() <= 0

    def __repr__(self):
        return f"<UserVoteInformation user_id={self.user_id} bot_id={self.bot_id} votes_this_month={self.monthly_votes} since_last_vote={self.since_last_vote} until_next_vote={self.until_next_vote}>"

    def __str__(self):
        return self.__repr__()
