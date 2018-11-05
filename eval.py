import discord
import random
import json
from discord.ext import commands
import unicodedata
from contextlib import redirect_stdout
import textwrap
import io
import traceback
import asyncio
import time
import datetime

@client.command(pass_context=True, hidden = True, name="eval")
async def _eval(ctx, *, body: str):
    if ctx.message.author.id == "Your ID here.":
        def cleanup_code(content):
            """Automatically removes code blocks from the code."""
            if content.startswith('```') and content.endswith('```'):
                return '\n'.join(content.split('\n')[1:-1])
            return content.strip('` \n')
        embed = discord.Embed(title = "Running Code", color = 0x0080c0)
        embed.add_field(name = "**Output:**", value = f'```\n...\n```')
        m = await client.say(embed = embed)
        client._last_result = None 
        env = {
	    'self': client,
            'bot': client,
            'ctx': ctx,
            '_': client._last_result
        }
        env.update(globals())
        body = cleanup_code(body)
        stdout = io.StringIO()
        to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'
        try:
            exec(to_compile, env)
        except Exception as e:
            embed = discord.Embed(title = "error message", description = "error ocurred", color = 0xff0000)
            embed.add_field(name = "error", value = f'```\n{e.__class__.__name__}: {e}\n```')
            return await client.edit_message(m, embed = embed)
        func = env['func']
            
        try:
            with redirect_stdout(stdout):
                ret = await func()
        except Exception as e:
            value = stdout.getvalue()
            embed = discord.Embed(title = "Error", description = "An Error Occured", color = 0xff0000)
            embed.add_field(name = "error", value = f'```\n{value}{traceback.format_exc()}\n```')
            await client.edit_message(m, embed = embed)
        else:
            value = stdout.getvalue()
                
        if ret is None:
            if value:
                if len(value) <= 1016:
                    embed = discord.Embed(title = "Sucess!", description = "The code that was runned, was right!", color = 0x0080c0)
                    embed.add_field(name="**Input :inbox_tray:**", value=f"```\n{body}\n```")
                    embed.add_field(name = "**Output :outbox_tray:**", value = f"```\n{value}\n```")
                    await client.edit_message(m, embed = embed)
                    pass
                else:
                    embed = discord.Embed(title = "success message", description = "The function completed successfully", color = 0x0080c0)
                    embed.add_field(name = ":", value = f'```\nsending in file\n```')
                    await client.edit_message(m, embed = embed)
                    with open("out.txt", 'w') as f:
                        f.write(f"{value}")
                        f.close()
                        pass
                    with open("out.txt", 'r') as f:   
                        await client.send_file(ctx.message.channel, f)
                    pass
            else:
                embed = discord.Embed(title = "Blank", description = "You're code was Blank :(", color = 0x0080c0)
                embed.add_field(name = "Output", value = "```\n Blank :(\n```")
                await client.edit_message(m, embed = embed)
        else:
            if len(f"{value}{ret}") <= 1016:
                client._last_result = ret
                embed = discord.Embed(title = "Sucessful!", description = "Code was sucessful", color = 0x0080c0)
                embed.add_field(name = "Code:", value = f'```\n{value}{ret}\n```')
                await client.edit_message(m, embed = embed)
            else:
                client._last_result = ret
                embed = discord.Embed(title = "Error", description = "Error was found", color = 0x0080c0)
                embed.add_field(name = "Error:", value = f'```\nOutput too long to display, sending in file\n```')
                await client.edit_message(m, embed = embed)
                with open("out.txt", 'w') as f:
                    f.write(f"{value}{ret}")
                    f.close()
                    pass
                with open("out.txt", 'r') as f:   
                    await client.send_file(ctx.message.channel, f)
                    pass
    else:
        await client.say("**Owner command only!**")
