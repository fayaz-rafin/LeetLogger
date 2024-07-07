import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import aiohttp
import asyncio

load_dotenv()
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

intents = discord.Intents.all()  # Adjust the intents as necessary
intents.messages = True
bot = commands.Bot(command_prefix='!', intents=intents)

async def supabase_query(query='', method='POST', data=None):
    async with aiohttp.ClientSession() as session:
        headers = {
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}',
            'Content-Type': 'application/json'
        }
        if method == 'POST':
            async with session.post(f'{SUPABASE_URL}/rest/v1/leetcode_progress', headers=headers, json=data) as resp:
                print("Status Code:", resp.status)  # Print status code
                response = await resp.json()
                print("Response:", response)  # Print response data
                return response
        elif method == 'GET':
            async with session.get(f'{SUPABASE_URL}/rest/v1/leetcode_progress?{query}', headers=headers) as resp:
                response = await resp.json()
                return response



@bot.command(name='solve')
async def solve_problem(ctx, problem_id, *, problem_name):
    user_id = str(ctx.author.id)
    data = {
        'user_id': user_id,
        'problem_id': problem_id,
        'problem_name': problem_name,
        'solved_date': 'now()'
    }
    result = await supabase_query(data=data)
    await ctx.send(f"Problem '{problem_name}' (ID: {problem_id}) solved and recorded for {ctx.author.name}!")


@bot.command(name='progress')
async def check_progress(ctx):
    user_id = str(ctx.author.id)
    query = f'user_id=eq.{user_id}'
    result = await supabase_query(query=query, method='GET')
    if result:
        # Create an embed object
        embed = discord.Embed(
            title=f"Progress for {ctx.author.display_name}",
            description="Here are the problems you've solved:",
            color=discord.Color.blue()  # You can choose any color
        )

        # Adding fields to the embed
        for item in result:
            embed.add_field(
                name= item['problem_id'] + ". " + item['problem_name'],
                value=f"Solved on: {item['solved_date'][:10]}",
                inline=False  # Each problem in a new line
            )

        await ctx.send(embed=embed)
    else:
        await ctx.send("You haven't solved any problems yet!")


bot.run(os.getenv('DISCORD_TOKEN'))
