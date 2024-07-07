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

#Supabase query function
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
        description=f"**{problem_id}. {problem_name}**",
        color=discord.Color.green()
    )
    embed.add_field(name="Solver", value=ctx.author.display_name, inline=True)
    embed.add_field(name="Current Streak", value=f"{streak} days", inline=True)
    embed.set_footer(text=f"Solved on {current_time.strftime('%Y-%m-%d %H:%M:%S')} UTC")

    await ctx.send(embed=embed)

#Command to check the progress of a user
@bot.command(name='progress')
async def check_progress(ctx):
    user_id = str(ctx.author.id)
    query = f'user_id=eq.{user_id}'
    results = await supabase_query(query=query, method='GET')

    if not results:
        await ctx.send("You haven't solved any problems yet!")
        return

    # Constants for pagination
    items_per_page = 6
    pages = [results[i:i + items_per_page] for i in range(0, len(results), items_per_page)]
    current_page = 0

    # Function to create embeds for a specific page
    def get_embed(page_index):
        embed = discord.Embed(
            title=f"Progress for {ctx.author.display_name} (Page {page_index + 1}/{len(pages)})",
            description="Here are the problems you've solved:",
            color=discord.Color.blue()
        )
        embed.set_footer(text=f"Current User Streak: {results[-1]['streak_count']} days")
        for item in pages[page_index]:
            embed.add_field(
                name=item['problem_id'] + ". "+ item['problem_name'],
                value=f"Solved on: {item['solved_date'][:10]}",
                inline=False
            )
        return embed

    # Send the initial embed
    message = await ctx.send(embed=get_embed(current_page))
    await message.add_reaction('⬅️')
    await message.add_reaction('➡️')

    # Check function for reactions
    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in ['⬅️', '➡️']

    while True:
        try:
            reaction, user = await ctx.bot.wait_for('reaction_add', timeout=60.0, check=check)
            if str(reaction.emoji) == '➡️' and current_page < len(pages) - 1:
                current_page += 1
                await message.edit(embed=get_embed(current_page))
                await message.remove_reaction(reaction, user)
            elif str(reaction.emoji) == '⬅️' and current_page > 0:
                current_page -= 1
                await message.edit(embed=get_embed(current_page))
                await message.remove_reaction(reaction, user)
        except asyncio.TimeoutError:
            await message.clear_reactions()
            break

    


bot.run(os.getenv('DISCORD_TOKEN'))
