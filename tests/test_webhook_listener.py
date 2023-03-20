import random
import unittest
import uuid

import aiohttp

from diffcord import VoteWebhookListener, UserBotVote


class TestWebhookListener(unittest.IsolatedAsyncioTestCase):
    __PORT = 31412

    @staticmethod
    async def open_webhook(*args, **kwargs) -> VoteWebhookListener:
        listener = VoteWebhookListener(TestWebhookListener.__PORT, *args, **kwargs, silent=True)
        await listener.start()
        return listener

    @staticmethod
    async def send_webhook(url: str, method: str, **kwargs) -> aiohttp.ClientResponse:
        async with aiohttp.ClientSession() as session:
            async with session.request(method, url, **kwargs) as response:
                return response

    @staticmethod
    def create_vote(test: bool) -> dict:
        return {
            "vote_id": str(uuid.uuid4()),
            "user_id": str(random.randint(100000000000000000, 999999999999999999)),
            "bot_id": str(random.randint(100000000000000000, 999999999999999999)),
            "voted_at": "2023-03-05T20:29:46.315604-05:00",
            "rewarded": False,
            "test": test,
            "monthly_votes": random.randint(1, 50)
        }

    async def test_expose_port(self):
        created_vote = {
            "vote_id": str(uuid.uuid4()),
            "user_id": str(random.randint(100000000000000000, 999999999999999999)),
            "bot_id": str(random.randint(100000000000000000, 999999999999999999)),
            "voted_at": "2023-03-05T20:29:46.315604-05:00",
            "rewarded": False,
            "test": True,
            "monthly_votes": random.randint(1, 50)
        }

        entered_handle_vote: bool = False

        async def handle_vote(vote: UserBotVote):
            nonlocal entered_handle_vote
            nonlocal created_vote

            entered_handle_vote = True

            self.assertEqual(str(vote.vote_id), created_vote["vote_id"])
            self.assertEqual(str(vote.user_id), created_vote["user_id"])
            self.assertEqual(str(vote.bot_id), created_vote["bot_id"])
            self.assertEqual(vote.voted_at.isoformat(), created_vote["voted_at"])
            self.assertEqual(bool(vote.rewarded), created_vote["rewarded"])
            self.assertEqual(bool(vote.test), created_vote["test"])
            self.assertEqual(int(vote.monthly_votes), created_vote["monthly_votes"])

        await self.open_webhook(handle_vote=handle_vote)

        # make request to see if port is exposed
        response = await self.send_webhook(f"http://localhost:{TestWebhookListener.__PORT}", "POST",
                                           json=created_vote)

        self.assertEqual(response.status, 200)
        self.assertEqual(entered_handle_vote, True)

    async def test_handle_no_verify_vote(self):
        async def handle_vote(vote: UserBotVote):
            pass

        await self.open_webhook(handle_vote=handle_vote)

        response = await self.send_webhook(f"http://localhost:{TestWebhookListener.__PORT}", "POST",
                                           json=self.create_vote(False))

        self.assertEqual(response.status, 200)

    async def test_handle_verify_vote(self):
        enters_handle_vote: int = 0

        async def handle_vote(vote: UserBotVote):
            nonlocal enters_handle_vote
            enters_handle_vote += 1

        verify_code = "thisisanexampleverifycode"
        await self.open_webhook(handle_vote=handle_vote, verify_code=verify_code)

        # --- no verification vote ---

        response = await self.send_webhook(f"http://localhost:{TestWebhookListener.__PORT}", "POST",
                                           json=self.create_vote(False))

        self.assertEqual(response.status, 403)
        self.assertEqual(enters_handle_vote, 0)

        # --- verification vote ---

        response = await self.send_webhook(f"http://localhost:{TestWebhookListener.__PORT}", "POST",
                                           json=self.create_vote(False), headers={"Authorization": verify_code})

        self.assertEqual(response.status, 200)
        self.assertEqual(enters_handle_vote, 1)
