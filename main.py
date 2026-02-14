import os
import time
import discord
from discord import app_commands
from discord.ext import tasks

TOKEN = os.getenv("TOKEN")
GUILD_ID = 123456789012345678  # your server ID

intents = discord.Intents.default()

class APBot(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.timers = {}
        self.bg_task_started = False

    async def setup_hook(self):
        guild = discord.Object(id=GUILD_ID)
        await self.tree.sync(guild=guild)
        print(f"Slash commands synced to guild {GUILD_ID}")

    async def on_ready(self):
        print(f"Logged in as {self.user}")
        if not self.bg_task_started:
            self.check_timers.start()
            self.bg_task_started = True

    @tasks.loop(seconds=60)
    async def check_timers(self):
        now = time.time()
        to_remove = []
        for user_id, (end_timestamp, channel) in self.timers.items():
            if now >= end_timestamp:
                if channel:
                    await channel.send(f"<@{user_id}> Your AP is now full!")
                to_remove.append(user_id)
        for user_id in to_remove:
            del self.timers[user_id]

bot = APBot()

def calculate_timer(value: int):
    if value < 0 or value > 140:
        return None, "Value must be between 0–140"
    remaining = 140 - value
    total_minutes = remaining * 5
    hours = total_minutes // 60
    minutes = total_minutes % 60
    timestamp = int(time.time()) + (total_minutes * 60)
    return timestamp, (
        f"Remaining to 140: **{remaining}**\n"
        f"Total time: **{hours}h {minutes}m**\n"
        f"You will be maxed at: <t:{timestamp}:F>"
    )

@bot.tree.command(name="ap", description="Calculate time until 140 based on AP")
@app_commands.describe(value="AP value between 0–140")
async def ap(interaction: discord.Interaction, value: int):
    print(f"Command received: {interaction.user} -> {value}")
    timestamp, msg = calculate_timer(value)
    if timestamp:
        bot.timers[interaction.user.id] = (timestamp, interaction.channel)
    await interaction.response.send_message(msg)

bot.run(TOKEN)
