import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import aiohttp
import asyncio
import datetime

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
                print("Status Code:", resp.status)
                print("Content Type:", resp.headers.get('Content-Type'))
                try:
                    response = await resp.json()
                    print("Response:", response)
                except aiohttp.ContentTypeError:
                    response = await resp.text()  # Fallback to raw text if JSON parsing fails
                    print("Failed to decode JSON, response was:", response)
                return response
        elif method == 'GET':
            async with session.get(f'{SUPABASE_URL}/rest/v1/leetcode_progress?{query}', headers=headers) as resp:
                try:
                    response = await resp.json()
                except aiohttp.ContentTypeError:
                    response = await resp.text()
                    print("Failed to decode JSON, response was:", response)
                return response

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

#Command to log that a problem has been solved by a user
@bot.command(name='solve')
async def solve_problem(ctx, problem_id, *, problem_name):
    user_id = str(ctx.author.id)
    current_time = datetime.datetime.now(datetime.timezone.utc)  # Timezone-aware datetime
    query = f"user_id=eq.{user_id}"
    result = await supabase_query(query=query, method='GET')
    
    if result and result[0]['last_solved_date']:
        last_solved_date = result[0]['last_solved_date']
        last_solved_date = datetime.datetime.fromisoformat(last_solved_date.replace('Z', '+00:00'))
        if (current_time - last_solved_date).days == 1:
            streak = result[0]['streak_count'] + 1
        elif (current_time - last_solved_date).days > 1:
            streak = 1
    else:
        streak = 1
    
    data = {
        'user_id': user_id,
        'problem_id': problem_id,
        'problem_name': problem_name,
        'solved_date': current_time.isoformat(),
        'streak_count': streak,
        'last_solved_date': current_time.isoformat()
    }
    await supabase_query(data=data)

    # Creating the embed
    embed = discord.Embed(
        title="Problem Solved!",
        description=f"**{problem_name}** (ID: {problem_id})",
        color=discord.Color.green()
    )
    embed.add_field(name="Solver", value=ctx.author.display_name, inline=True)
    embed.add_field(name="Current Streak", value=f"{streak} days", inline=True)
    embed.set_footer(text=f"Solved on {current_time.strftime('%Y-%m-%d %H:%M:%S')} UTC")

    await ctx.send(embed=embed)

    
@bot.command(name='progress')
async def check_progress(ctx):
    user_id = str(ctx.author.id)
    query = f'user_id=eq.{user_id}'
    result = await supabase_query(query=query, method='GET')
    if result:
        # Assuming all entries for a user should have the same streak count,
        # we can take the streak count from the last entry.
        current_streak = result[-1]['streak_count']
        
        # Create an embed object
        embed = discord.Embed(
            title=f"Progress for {ctx.author.display_name}",
            description=f"Here are the problems you've solved:\nCurrent streak: {current_streak} days",
            color=discord.Color.blue()  # You can choose any color
        )

        # Adding fields to the embed
        for item in result:
            embed.add_field(
                name=item['problem_id'] + ". " + item['problem_name'],
                value=f"Solve on: {item['solved_date'][:10]}",
                inline=False  # Each problem in a new line
            )

        await ctx.send(embed=embed)
    else:
        await ctx.send("You haven't solved any problems yet!")

    


bot.run(os.getenv('DISCORD_TOKEN'))
