
# Elite Dangerous Carrier Mission Trader

A discord bot that allows you to generate pastable messages
and reddit posts/xposts.  
Leverages the [pycord](https://docs.pycord.dev/en/v2.2.2/) python library


## Installation
#TODO Dockerfile

### Python
Developed on **Python 3.8.10**

### Manual Install requirements  
`pip install -r requirements.txt`

### Create Discord Bot account
https://docs.pycord.dev/en/v2.2.2/discord.html  
https://docs.pycord.dev/en/v2.2.2/intents.html   
You will need to enable `message_content` intent
### Create Reddit Application
Navigate to https://www.reddit.com/prefs/apps, scroll to the bottom and
select `create another app`  
*  fill in the name
*  select `script` as the type
*  `redirect uri` may require a value, even though we don't use it, you can put in `http://localhost:8080`
Take note of your `secret`, the client_id is not as nicely labeled, but under the name

## Configuration
Copy the **config.ini.example** to **config.ini**  
Copy the **praw.ini.example** to **praw.ini**

### config.ini
```
[DISCORD]
guildid = 1234455667788
bottoken = asd987sdf987df9s87fs98df7
```
**guildid** is your discord servers unique id. Right click your servers icon
in a discord client and select `Copy ID`  
**bottoken** obtained after creating your bot in the discord developer UI

```
[REDDIT]
main_sr = your_main_subreddit
main_sr_flair_buy = asdf8-asd9f8asdf-asd9f8asd9f7
main_sr_flair_sell = fgf78g7f8-fg8f7g8f-f7g8fg7
secondary_srs = second_subreddit
secondary_flairs_buy = 8d7fd87f8d-we76w7e67-df67
secondary_flairs_sell = 87676df7-d8f7d8-we67w6e
```
**main_sr** is the main subreddit to post your message to ie: elitetraders  
**main_sr_flair_buy** the flair id to assign to the post in the main subreddit
when the mission type is `Loading`  
**main_sr_flair_sell** the flair id to assign to the post in the main subreddit
when the mission type is `Unloading`  
**secondary_srs** secondary subreddit(s) to cross post your main post to.
This can be a comma separated list of multiple ie: `elitecarriers,anothertrade`  
**secondary_flairs_buy** flair for the secondary subreddits when the mission
type is `Loading`. If you have 2 secondary subreddits, you should have 2
flairs comma separated as well
**secondary_flairs_sell** flair for the secondary subreddits when the mission
type is `Unloading`. If you have 2 secondary subreddits, you should have 2
flairs comma separated as well

Use the `/trade flairs subreddit` command to look up flair ids for any subreddit  

### praw.ini
```
user_agent=a_cool_and_unique_useragent_name
client_id=12345567
client_secret=asdf87d7f8df7d87f8df
password=your_reddit_password
username=your_reddit_username
```
**user_agent** identifying name for your api requests to reddit  
**client_id** client id obtained from the reddit app
**client_secret** client secret obtained from your reddit app
**password** your reddit login password
**username** your reddit username

## Startup
Make sure:
*  discord bot has been created
*  bot invited to your discord server
*  reddit app created
*  both config files created and updated

Run the following `python3 bot.py`  
Your bot should now have registered the `/trade` slash command(s) on your discord. Try it out!  

`/trade mission`  
`/trade flairs subreddit`

![demo](demo/demo.gif)