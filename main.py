# bot.py
import requests
import discord
import os
import re
from keep_alive import keep_alive

TOKEN = os.environ.get('DISCORD_TOKEN')
API_KEY = os.environ.get('API_KEY')


def get_translation(text, target):
    url = "https://microsoft-translator-text.p.rapidapi.com/translate"
    translated_text = ''
    querystring = {"to": "{}".format(target), "api-version": "3.0", "profanityAction": "NoAction", "textType": "plain"}
    payload = [{"Text": "{}".format(text)}]
    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Host": "microsoft-translator-text.p.rapidapi.com",
        "X-RapidAPI-Key": "{}".format(API_KEY)
    }

    try:
        response = requests.request("POST", url, json=payload, headers=headers, params=querystring)
    except requests.exceptions.RequestException as e:
        return e
    except (requests.exceptions.InvalidJSONError, TypeError):
        return "Invalid JSON"

    try:
        translated_text = response.json()[0]["translations"][0]["text"]
    except (KeyError, IndexError, ValueError):
        return "PARSING ERROR"

    if translated_text == '':
        return 'Failed to get Translation'

    return translated_text


client = discord.Client()


def get_translation_log(guild):
    for channel in guild.channels:
        if str(channel.name) == 'translation-log':
            return channel
    return 0


def validate_message_text(text):
    if len(str(text)) == 0 or "https:" in str(text) or "http:" in str(text):
        return False
    return True


def get_target_language(emoji):
    if emoji == '🇪':
        return 'en'
    elif emoji == '🇨':
        return 'zh-CN'
    # elif reaction.emoji == '🇯':
    #     target='ja'
    else:
        return ''


@client.event
async def on_reaction_add(reaction, user):
    if user.bot:
        return

    channel = get_translation_log(reaction.message.guild)
    if channel == 0:
        return

    if reaction.count > 1:
        return

    text = reaction.message.content
    text = re.sub("[:<>].*[:<>]", "", text)  ## remove emojis in text message

    if not validate_message_text(text):
        return

    target = get_target_language(reaction.emoji)
    if len(target) == 0:
        return

    embed = discord.Embed(title="Translation", description="Translation", color=0xffffff)
    embed.add_field(name="Original Text", value=text, inline=False)
    embed.add_field(name="Translated Test", value=get_translation(text, target=target), inline=False)
    await channel.send(embed=embed)

keep_alive()
client.run(TOKEN)
