import discord
import aiosqlite
import configparser
from msghelper import MessageHelper
from reddithelper import RedditPost


config = configparser.ConfigParser()
config.read('config.ini')

intents = discord.Intents.default()
intents.message_content = True
bot = discord.Bot(debug_guilds=[config['DISCORD']['guildid']], intents=intents)


database_file = "trademission.db"
fields = ['username', 'station_name', 'system_name', 'quantity',\
    'commodity', 'carrier_name', 'profit', 'pad_size', 'mission_type']
table_trademission_sql = """
CREATE TABLE IF NOT EXISTS trademissions (
	message_id TEXT UNIQUE,
	username VARCHAR,
	station_name VARCHAR,
	system_name VARCHAR,
	quantity VARCHAR,
	commodity VARCHAR,
	carrier_name VARCHAR,
	profit VARCHAR,
    pad_size TEXT,
	mission_type TEXT
);
"""

async def conn(db_file=database_file):
    """
    Create database connection and file
    """
    try:
        return await aiosqlite.connect(db_file)
    except Exception as e:
        print(e)
        exit()


async def create_table(sql_conn, create_table_sql=table_trademission_sql):
    """ 
    Create table with specified table statement
    """
    try:
        c = await sql_conn.cursor()
        await c.execute(create_table_sql)
    except Exception as e:
        print(e)
        exit()


async def insert_data(sql_conn, data, table='trademissions'):
    """
    Sqlite UPSERT funcionality
    Attempt insert, if message_id already exists:
        update every passed field instead
    """

    fields = ','.join(data.keys())
    values_count = ",".join(["?"] * len(data.values()))
    values = [v for v in data.values()]
    conflict = list()
    for d in data:
        if d != 'message_id':
            conflict.append(f'{d}="{data[d]}"')
    conflict = ','.join(conflict)
    
    insert_stmt = f"""
    INSERT INTO {table} ({fields})
    VALUES({values_count}) 
    ON CONFLICT(message_id) 
    DO UPDATE SET {conflict};
    """

    cur = await sql_conn.cursor()
    await cur.execute(insert_stmt, values)
    await sql_conn.commit()


async def select_data(sql_conn, message_id, table='trademissions'):
    """
    Query specified table for specific row based off message_id
    Returns sqlite.Row object which is a dict of 'column_name': 'value'
    """

    cur = await sql_conn.cursor()
    cur.row_factory = aiosqlite.Row
    await cur.execute(f"SELECT * FROM {table} where message_id = ?", [message_id])

    return await cur.fetchone()
 

async def delete_data(sql_conn, message_id, table='trademissions'):
    """
    Delete row from DB based off message_id
    """

    cur = await sql_conn.cursor()
    await cur.execute(f"DELETE FROM {table} where message_id = ?", [message_id])


async def can_we_enable(data):
    """
    Tests to see if all fields have values
    Used in the workflow of enabling the Submit button in the TradeView    
    """
    try:
        if all([data[f] for f in fields]):
            return True
    except KeyError:
        return False
    return False


async def update_select_view(view):
    """
    If the mission_type (select fields) has been selected
    set it to the Default, so it stays selected between modal loads
    """
    if view.data['mission_type'] == 'unloading':
        view.children[0].options[0].default = True 
        view.children[0].options[1].default = False
    elif view.data['mission_type'] == 'loading':
        view.children[0].options[0].default = False
        view.children[0].options[1].default = True
    return view


class TradeModal(discord.ui.Modal):
    """
    Modal containing the fields for related Trade data:
        commodity, carrier_name, profit, quantity (demand|supply)
    Expects the view to be passed in so it can be checked/altered
    """
    def __init__(self, view, *args, **kwargs) -> None:
        self.view = view
        super().__init__(*args, **kwargs)

        self.add_item(discord.ui.InputText(
            label = 'Commodity', 
            placeholder = 'Gold',
            custom_id = 'commodity',
            value = self.view.data['commodity']
            )
        )
        self.add_item(discord.ui.InputText(
            label = 'Carrier Name', 
            placeholder = 'Carrier Name (XYZ-123)',
            custom_id = 'carrier_name',
            value = self.view.data['carrier_name']
            )
        )
        self.add_item(discord.ui.InputText(
            label = 'Profit per ton', 
            placeholder = '12k or 1m',
            custom_id = 'profit',
            value = self.view.data['profit']
            )
        )
        self.add_item(discord.ui.InputText(
            label = 'Demand | Supply', 
            placeholder = '21k',
            custom_id = 'quantity',
            value = self.view.data['quantity']
            )
        )

    async def callback(self, interaction):
        self.view.data['message_id'] = str(interaction.message.id)
        self.view.data['username'] = f'{interaction.user.name}#{interaction.user.discriminator}'
        self.view.data['commodity'] = self.children[0].value.title()
        self.view.data['carrier_name'] = self.children[1].value
        self.view.data['profit'] = self.children[2].value
        self.view.data['quantity'] = self.children[3].value
        
        if await can_we_enable(self.view.data):
            self.view.children[3].disabled = False
        self.view = await update_select_view(self.view)
        await interaction.response.edit_message(view=self.view)


class StationSystemModal(discord.ui.Modal):
    """
    Modal containing the fields for the:
        station_name, system_name, pad_size
    Expects the view to be passed in so it can be checked/altered
    """
    def __init__(self, view, *args, **kwargs) -> None:
        self.view = view
        super().__init__(*args, **kwargs)
        
        self.add_item(discord.ui.InputText(
            label = 'System', 
            placeholder = 'Wally Bei',
            custom_id = 'system_name',
            value = self.view.data['system_name']
            )
        )
        self.add_item(discord.ui.InputText(
            label = 'Station', 
            placeholder = 'Malerba',
            custom_id = 'station_name',
            value = self.view.data['station_name']
            )
        )
        self.add_item(discord.ui.InputText(
            label = 'Pad Size', 
            placeholder = 'L or M or S',
            custom_id = 'pad_size',
            value = self.view.data['pad_size']
            )
        )

    async def callback(self, interaction):
        self.view.data['message_id'] = str(interaction.message.id)
        self.view.data['username'] = f'{interaction.user.name}#{interaction.user.discriminator}'
        self.view.data['system_name'] = self.children[0].value.title()
        self.view.data['station_name'] = self.children[1].value.title()
        self.view.data['pad_size'] = self.children[2].value.upper()

        if await can_we_enable(self.view.data):
            self.view.children[3].disabled = False
        self.view = await update_select_view(self.view)
        await interaction.response.edit_message(view=self.view)


class ConfirmationView(discord.ui.View):
    """
    View for displaying confirmation options while displaying:
        reddit title, reddit body, discord message
    Expects a data dict to be passed and a msg dict containing atleast a msg['dm']
    """
    def __init__(self, msg, data, *args, **kwargs):
        self.msg = msg
        self.data = data
        super().__init__(*args, **kwargs)

    @discord.ui.button(label="Post to Reddit", row=0, style=discord.ButtonStyle.green)
    async def spost_button_callback(self, button, interaction):
        rp = RedditPost(self.msg, self.data['mission_type'])
        submission = await rp.create_post()
        crossposts = await rp.crosspost(submission)
        xposts = [f'https://www.reddit.com{c.permalink}' for c in crossposts if c != None]

        embed = discord.Embed(title="Successfully posted to Reddit", color=discord.Color.green())
        embed.add_field(name='Main Post', value=submission.url, inline=False)
        embed.add_field(name='CrossPosts', value=','.join(xposts), inline=False)
        embed.add_field(name='Discord Paste', value=self.msg['dm'], inline=False)
        
        await insert_data(await conn(), self.data)
        await interaction.response.edit_message(content=None, embed=embed, view=None)
        self.stop()

    @discord.ui.button(label="Save (no Reddit)", row=0, style=discord.ButtonStyle.blurple)
    async def save_button_callback(self, button, interaction):
        await insert_data(await conn(), self.data)
        embed = discord.Embed(title="Trade Mission Saved, no post to Reddit", color=discord.Color.blue())
        embed.add_field(name='Discord Paste', value=self.msg['dm'], inline=False)

        await interaction.response.edit_message(content=None, embed=embed, view=None)
        self.stop()

    @discord.ui.button(label="Delete", row=0, style=discord.ButtonStyle.red)
    async def cancel_button_callback(self, button, interaction):
        embed = discord.Embed(title="Trade Mission Deleted", color=discord.Color.blue())
        await delete_data(await conn(), str(interaction.message.id))
        await interaction.response.edit_message(content=None, embed=embed, view=None)
        self.stop()


class TradeView(discord.ui.View):
    """
    Main trade view containing the:
        select menu, station|system modal, trade data modal
    If self.data is not set, create a dict with default keys set to ''
    """
    def __init__(self, embed=discord.Embed(), *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            self.data = self.data
        except AttributeError:
            self.data = dict.fromkeys(fields, '')

    @discord.ui.select(
        placeholder="Pick your Trade Mission Type",
        row = 0,
        options=[
            discord.SelectOption(
                label="Unload", value='unloading'
            ),
            discord.SelectOption(
                label="Load", value='loading'
            ),
        ],
    )
    async def select_callback(self, select: discord.ui.Select, interaction: discord.Interaction):
        self.data['message_id'] = str(interaction.message.id)
        self.data['mission_type'] = select.values[0]
        self.data['username'] = f'{interaction.user.name}#{interaction.user.discriminator}'

        if await can_we_enable(self.data):
            self.children[3].disabled = False
        view = await update_select_view(self)
        await interaction.response.edit_message(view=view)


    @discord.ui.button(label="Station | System", row=1, custom_id='station_system')
    async def system_button_callback(self, button, interaction):
        await interaction.response.send_modal(StationSystemModal(title='Station | System Info', view=self))

    @discord.ui.button(label="Trade Data", row=1, custom_id='mission_data')
    async def mission_button_callback(self, button, interaction):
        await interaction.response.send_modal(TradeModal(title='Trade Data', view=self))

    @discord.ui.button(label="Submit Trade", row=2, custom_id='submit', style=discord.ButtonStyle.green, disabled=True)
    async def save_button_callback(self, button, interaction):
        msg = MessageHelper(self.data)
        self.msg = {}
        self.msg['dm'] = await msg.build_discord_message()
        self.msg['rb'] = await msg.build_reddit_body()
        self.msg['rt'] = await msg.build_reddit_title()
        
        embed = discord.Embed(title="Review the Data!", color=discord.Color.orange())
        embed.add_field(name='Discord Paste', value=self.msg['dm'], inline=False)
        embed.add_field(name='Reddit Title', value=self.msg['rt'], inline=False)
        embed.add_field(name='Reddit Body', value=self.msg['rb'], inline=False)

        await interaction.response.edit_message(content=None, embed=embed, view=ConfirmationView(msg=self.msg, data=self.data))

    @discord.ui.button(label="Delete", row=2, custom_id='cancel', style=discord.ButtonStyle.red)
    async def quit_button_callback(self, button, interaction):
        embed = discord.Embed(title="Trade Mission Deleted", color=discord.Color.blue())

        await delete_data(await conn(), str(interaction.message.id))
        await interaction.response.edit_message(content=None, embed=embed, view=None)
        self.stop()
        

@bot.slash_command()
async def trademission(ctx: discord.ApplicationContext):
    """
    /trademission slash_command creation
    """
    await ctx.respond("Fill out the Trade Mission Forms", view=TradeView(), ephemeral=True)

@bot.event
async def on_ready():
    """
    Make sure the table is created when bot starts
    """
    await create_table(await conn())

bot.run(config['DISCORD']['bottoken'])