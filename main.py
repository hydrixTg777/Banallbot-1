import time
import traceback
from pyrogram import Client, idle, filters
import asyncio
from pyrogram.types import *
from chatzo import add_to_bdlist, get_chat_bdlist
from config import *
from loggers import *
from users import add_user_, is_users_banned, rm_user


bot_client = Client("_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@bot_client.on_message(filters.command("start", ["!", "/"]))
async def st(client: Client, message: Message):
    await message.reply(f"<b>Hi, i am @{client.myself.username}!</b>")
    
@bot_client.on_message(filters.command("purge", ["!", "/"]))
async def purge(client: Client, message: Message):
    st_time = time.perf_counter()
    st = await message.reply("`.....`")
    if message.from_user.id not in USERS:
        return await st.edit("<b>You are not a sudo user!</b>")
    if not message.reply_to_message:
        return await st.edit("Reply to a message to start purging!")
    try:
        await message.delete()
    except Exception as e:
        return await st.edit(f"<b>Failed to delete message!</b> \n<b>Error :</b> <code>{e}</code>")
    msg_ids = []
    no_of_msgs_deleted = 0
    for to_del in range(message.reply_to_message.message_id, message.message_id):
        if to_del != st.message_id:
            msg_ids.append(to_del.message_id)
        if len(msg_ids) == 100:
            await client.delete_messages(
                    chat_id=message.chat.id, message_ids=msg_ids, revoke=True
                )
            no_of_msgs_deleted += len(msg_ids)
            msg_ids = []
        if len(msg_ids) > 0:
            await client.delete_messages(
                chat_id=message.chat.id, message_ids=msg_ids, revoke=True
            )
            no_of_msgs_deleted += len(msg_ids)
    end_time = round((time.perf_counter() - st_time), 2)
    await st.edit(f'<b>Purged</b> <code>{no_of_msgs_deleted}</code> <b>in</b> <code>{end_time}</code> <b>seconds!</b>')
    await asyncio.sleep(10)
    await st.delete()
    
@bot_client.on_message(filters.command("banall", ["!", "/"]))
async def ban_all(client: Client, message: Message):
    st = await message.reply("`.....`")
    if message.from_user.id not in USERS:
        return await st.edit("<b>You are not a sudo user!</b>")
    no_of_banned = 0
    async for x in client.iter_chat_members(message.chat.id):
        if x.user and x.user.id:
            await client.ban_chat_member(message.chat.id, x.user.id)
            no_of_banned += 1
    await st.edit(f'<b>Banned</b> <code>{no_of_banned}</code> <b>users!</b>')
    await asyncio.sleep(10)
    await st.delete()
    
@bot_client.on_message(filters.command("unbanall", ["!", "/"]))
async def unban_all(client: Client, message: Message):
    st = await message.reply("`.....`")
    if message.from_user.id not in USERS:
        return await st.edit("<b>You are not a sudo user!</b>")
    _unbanned = 0
    async for y in client.iter_chat_members(message.chat.id, filter='banned'):
        if y.user and y.user.id:
            await client.unban_chat_member(message.chat.id, y.user.id)
            _unbanned += 1
    await st.edit(f'<b>Unbanned</b> <code>{_unbanned}</code> <b>users!</b>')
    await asyncio.sleep(10)
    await st.delete()
    
@bot_client.on_message(filters.command("unmuteall", ["!", "/"]))
async def unmute_all(client: Client, message: Message):
    st = await message.reply("`.....`")
    if message.from_user.id not in USERS:
        return await st.edit("<b>You are not a sudo user!</b>")
    _unmutted = 0
    async for o in client.iter_chat_members(message.chat.id, filter='restricted'):
        if not o.can_send_messages:
            cp = ChatPermissions(can_send_messages=True)
            try: await client.restrict_chat_member(message.chat.id, o.user.id, cp)
            except Exception:
                logging.error(traceback.format_exc())
                continue
            _unmutted += 1
    await st.edit(f'<b>Unmuted</b> <code>{_unmutted}</code> <b>users!</b>')
    await asyncio.sleep(10)
    await st.delete()
    
    
def isdigit_(x):
    try:
        int(x)
        return True
    except ValueError:
        return False 

@bot_client.on_message(filters.command("addbd", ["!", "/"]))
async def add_bd(client: Client, message: Message):
    st = await message.reply("`....`")
    user = await message.from_user.ask("Enter user ID :")
    await user.delete()
    await user.request.delete()
    if not user.text:
        return await st.edit('<b>User ID not found!</b>')
    if not isdigit_(user.text):
        return await st.edit('<b>Invalid user ID!</b>')
    int_ = 0
    while True:
        int_ += 1
        chat = await message.from_user.ask(f"Enter Chat ID {int_} : \nUse /done to stop")
        if not chat.text or (chat.text == "/done"):
            if int_ == 1: return await st.edit('<b>No chat IDs found!</b>')
            break
        if not isdigit_(chat.text):
            await chat.edit("Invalid chat ID!")
            await chat.request.delete()
            int_ -= 1
            continue
        await add_to_bdlist(user.text, chat.text)
        await chat.edit(f'<b>Chat {int_} added!</b>')
        await chat.request.delete()
    return await st.edit('<b>All Done!</b>')
        
@bot_client.on_message(filters.private, group=3)
async def broad_cast(client: Client, message: Message):
    st_ = 0
    st = await message.reply("`....`")
    if not await get_chat_bdlist(message.from_user.id):
        return await st.edit("<b>You don't have any chats saved by sudos!</b>")
    for i in (await get_chat_bdlist(message.from_user.id)):
        await message.copy(int(i))
        st_ += 1
    await st.edit(f"Sent to <b>{st_}</b> chats!")
    
@bot_client.on_message(filters.command("unmuteadmin", ["!", "/"]))
async def unmute_admin(client: Client, message: Message):
    st = await message.reply("`....`")
    if message.from_user.id not in USERS:
        return await st.edit("<b>You are not a sudo user!</b>")
    if not message.reply_to_message or not message.reply_to_message.from_user:
        return await st.edit("Reply to a message to unmute!")
    if not (await is_users_banned(message.reply_to_message.from_user.id)):
       await st.edit("<b>User is not banned!</b>") 
    await rm_user(message.reply_to_message.from_user.id)
    await st.edit("<b>Done! Unbanned Now the user can message in chat!</b>")
    
@bot_client.on_message(filters.command("muteadmin", ["!", "/"]))
async def mute_admin(client: Client, message: Message):
    st = await message.reply("`....`")
    if message.from_user.id not in USERS:
        return await st.edit("<b>You are not a sudo user!</b>")
    if not message.reply_to_message or not message.reply_to_message.from_user:
        return await st.edit("Reply to a message to mute!")
    await add_user_(message.reply_to_message.from_user.id)
    await st.edit("Done! Banned Now the user can't message in chat!")
    
async def admin_filter(_f, c: Client, m: Message):
    if m and m.from_user:
        if m.from_user.id in USERS:
            return False
        elif await is_users_banned(m.from_user.id):
            return True
    return False
    
a_filt = filters.create(admin_filter, 'admin_filter')
  
@bot_client.on_message(a_filt, group=2)
async def delete_admin_msgs(client: Client, message: Message):
    await message.delete()

async def run_bot():
    logging.info('Running Bot...')
    await bot_client.start()
    bot_client.myself = await bot_client.get_me()
    logging.info('Info: Bot Started!')
    logging.info('Idling...')
    await idle()
    logging.warning('Exiting Bot....')
    
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_bot())