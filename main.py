import os
import time
import discord
from discord import app_commands

# Get token from Replit secrets
TOKEN = os.getenv("TOKEN")

class MyBot(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.none())
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()
        print("Slash commands synced.")

bot = MyBot()

def calculate(value: int):
    if value < 0 or value > 140:
        return "Value must be between **0–140**"

    remaining = 140 - value
    total_minutes = remaining * 5

    hours = total_minutes // 60
    minutes = total_minutes % 60

    timestamp = int(time.time()) + (total_minutes * 60)

    return (
        f"Remaining to 140: **{remaining}**\n"
        f"Total time: **{hours}h {minutes}m**\n"
        f"You will be maxed at: <t:{timestamp}:F>"
    )

@bot.tree.command(name="ap", description="Calculate time until 140 based on AP")
@app_commands.describe(value="AP value between 0–140")
async def ap(interaction: discord.Interaction, value: int):
    await interaction.response.send_message(calculate(value))

# Optional: auto-restart if disconnected
while True:
    try:
        bot.run(TOKEN)
    except Exception as e:
        print("Bot crashed, restarting in 5 seconds...", e)
        time.sleep(5)
