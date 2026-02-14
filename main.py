import os
import time
import discord
from discord import app_commands
from discord.ext import tasks

# ---------------------
# Config
# ---------------------
TOKEN = os.getenv("TOKEN")
GUILD_ID = 1472244399416021023  # <-- replace with your Discord server ID
CARL_BOT_ID = 235148962103951360  # Carl Bot's user ID, replace if different

intents = discord.Intents.default()
intents.messages = True
intents.dm_messages = True

# ---------------------
# Bot Class
# ---------------------
class APBot(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.timers = {}  # {user_id: (end_timestamp, channel, total_minutes)}
        self.pending_channel = {}  # {user_id: channel}
        self.bg_task_started = False

    async def setup_hook(self):
        guild = discord.Object(id=GUILD_ID)
        await self.tree.sync(guild=guild)  # instant registration
        print(f"Slash commands synced to guild {GUILD_ID}")

    async def on_ready(self):
        print(f"Logged in as {self.user}")

    async def on_message(self, message):
        # Triggered when bot receives a DM
        if isinstance(message.channel, discord.DMChannel):
            if message.author.id == CARL_BOT_ID:
                # Attempt to parse user ID from message
                # For simplicity, ping all stored pending channels
                for user_id, channel in self.pending_channel.items():
                    await channel.send(f"<@{user_id}> Your AP is now full! @everyone")
                self.pending_channel.clear()

# ---------------------
# Bot Instance
# ---------------------
bot = APBot()

# ---------------------
# Helper: AP Calculation
# ---------------------
def calculate_timer(value: int):
    if value < 0 or value > 140:
        return None, None, "Value must be between 0–140"

    remaining = 140 - value
    total_minutes = remaining * 5
    hours = total_minutes // 60
    minutes = total_minutes % 60
    timestamp = int(time.time()) + (total_minutes * 60)

    msg = (
        f"Remaining to 140: **{remaining}**\n"
        f"Total time: **{hours}h {minutes}m**\n"
        f"You will be maxed at: <t:{timestamp}:F>"
    )

    return timestamp, total_minutes, msg

# ---------------------
# Slash Command: /AP
# ---------------------
@bot.tree.command(name="ap", description="Calculate time until 140 based on AP")
@app_commands.describe(value="AP value between 0–140")
async def ap(interaction: discord.Interaction, value: int):
    timestamp, total_minutes, msg = calculate_timer(value)
    if timestamp:
        # Store for later channel ping
        bot.pending_channel[interaction.user.id] = interaction.channel

        # Send Carl Bot reminder to DM the bot later
        await interaction.channel.send(f"!remindme {total_minutes}m Your AP is full!")

    await interaction.response.send_message(msg)

# ---------------------
# Run the bot
# ---------------------
bot.run(TOKEN)
