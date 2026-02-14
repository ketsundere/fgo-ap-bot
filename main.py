import os
import time
import discord
from discord import app_commands
from discord.ext import tasks

TOKEN = os.getenv("TOKEN")  # Make sure you added this in Railway Secrets

class APBot(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.tree = app_commands.CommandTree(self)
        self.timers = {}  # Stores timers: {user_id: (timestamp, channel)}
        self.check_timers.start()  # Start background task

    async def setup_hook(self):
        await self.tree.sync()
        print("Slash commands synced.")

    # Background task to check timers every minute
    @tasks.loop(seconds=60)
    async def check_timers(self):
        now = time.time()
        to_remove = []
        for user_id, (end_timestamp, channel) in self.timers.items():
            if now >= end_timestamp:
                await channel.send(f"<@{user_id}> Your AP is now full!")
                to_remove.append(user_id)
        for user_id in to_remove:
            del self.timers[user_id]

bot = APBot()

# Helper function to calculate AP time
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

# Slash command
@bot.tree.command(name="ap", description="Calculate time until 140 based on AP")
@app_commands.describe(value="AP value between 0–140")
async def ap(interaction: discord.Interaction, value: int):
    timestamp, msg = calculate_timer(value)
    if timestamp:
        # Store timer with channel reference
        bot.timers[interaction.user.id] = (timestamp, interaction.channel)
    await interaction.response.send_message(msg)

# Optional auto-restart if bot crashes
import time as t
while True:
    try:
        bot.run(TOKEN)


