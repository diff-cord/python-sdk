from diffcord import Client, VoteWebhookListener, UserBotVote, UserVoteInformation

import discord

intents = discord.Intents.default()

bot = discord.Bot(intents=intents)


async def send_stats_success():
    """ Handle stats successfully sent to Diffcord
    """
    print("Stats sent successfully!")


async def send_stats_failure(e: Exception) -> None:
    """ Handle stats failed to send to Diffcord error
    """
    print("Stats failed to send:", e)


async def on_vote(vote: UserBotVote) -> None:
    """ Handle the vote.
    """
    # LOGIC HERE... (give rewards, etc.)

    # example: send a DM to the user who voted
    user = await bot.fetch_user(vote.user_id)  # Get the discord user object from the user id
    await user.send("Thanks for voting!")  # Send a DM to the user who voted


# create Diffcord client & webhook listener

# "port" represents the port to listen on for incoming vote webhooks from Diffcord, choose any port you would like which is not in use
diff_webhook_listener = VoteWebhookListener(port=8080, handle_vote=on_vote, verify_code="WEBHOOK_AUTH_CODE_HERE")

diff_client = Client(bot, "YOUR_DIFFCORD_API_TOKEN", diff_webhook_listener,
                     send_stats_success=send_stats_success, send_stats_failure=send_stats_failure)


# on startup event
@bot.event
async def on_ready():
    # start the webhook listener & start send stats
    await diff_client.start()  # required


@bot.slash_command(name="example")
async def example_command(ctx):
    # get user vote info
    user_vote_info: UserVoteInformation = await diff_client.get_user_vote_info(ctx.author.id)

    # get amount of bot votes this month
    bot_votes_this_month: int = await diff_client.bot_votes_this_month()

    # respond
    message = f"You have voted {user_vote_info.monthly_votes} times this month! This bot has {bot_votes_this_month} votes this month!"
    await ctx.respond(message)


bot.run("YOUR_BOT_TOKEN")
