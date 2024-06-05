import interactions
from interactions import Task, IntervalTrigger,listen
import sqlite3



class ServerinfoBackup(interactions.Extension):
    module_base: interactions.SlashCommand = interactions.SlashCommand(
        name="show",
        description=" "
    )
    
    def __init__(self,bot):
        self.bot=bot 
        self.guild_id=1181895594265030776
        self.off_role_id=1181914967746818099
        self.tem_role_id=1181915800727199744
        self.dm_id=1247786071387930626
        # initiate the db for storing off_role members'ids and tem_roles'
        
        self.create_tables()

    @module_base.subcommand("ping", sub_cmd_description="ping me")
    @interactions.slash_option(
        name = "option_name",
        description = "Option description",
        required = True,
        opt_type = interactions.OptionType.STRING
    )
    async def ping(self, ctx: interactions.SlashContext, option_name: str):
        await ctx.send(f"Pong {option_name}!")
    

    @module_base.subcommand("official_members",sub_cmd_description="show the official member list at last check! ")
    async def offi_members(self,ctx:interactions.SlashContext):
        pass
    

    @listen(interactions.events.MessageCreate)
    async def start_backing_up(self,message):
        if not self.backing_up.running:
            await self.backing_up.start()
            return

    @Task.create(IntervalTrigger(hours=12))
    async def backing_up(self):
        guild=self.bot.get_guild(self.guild_id)
        try:
            off_role=await guild.fetch_role(self.off_role_id)
            tem_role=await guild.fetch_role(self.tem_role_id)
            off_role_member_id_list=[member.id for member in off_role.members]
            tem_role_member_id_list=[member.id for member in tem_role.members]

            # store into date base
            with sqlite3.connect('backup.db') as conn:
                cursor = conn.cursor()
                # Clear old data
                cursor.execute('DELETE FROM off_role_members')
                cursor.execute('DELETE FROM tem_role_members')
                    
                # Insert new data
                cursor.executemany('INSERT INTO off_role_members (member_id) VALUES (?)', [(mid,) for mid in off_role_member_id_list])
                cursor.executemany('INSERT INTO tem_role_members (member_id) VALUES (?)', [(mid,) for mid in tem_role_member_id_list])
                conn.commit()
        except:
            channel=await self.bot.fetch_channel(self.dm_id)
            embed=interactions.Embed(description="Role deleted!Pleaze Check!",color=interactions.Color.r)
            await channel.send(embed=embed)
        

    def create_tables(self):
        with sqlite3.connect('backup.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS off_role_members (
                                id INTEGER PRIMARY KEY,
                                member_id INTEGER)''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS tem_role_members (
                                id INTEGER PRIMARY KEY,
                                member_id INTEGER)''')
            conn.commit()
