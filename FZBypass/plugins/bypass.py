from time import time
from re import match
from asyncio import create_task, gather, sleep as asleep, create_subprocess_exec
from pyrogram.filters import create, command, private, user
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultArticle, InputTextMessageContent
from pyrogram.enums import MessageEntityType
from pyrogram.errors import QueryIdInvalid

from FZBypass import Config, Bypass, BOT_START, LOGGER
from FZBypass.core.bypass_checker import direct_link_checker, is_excep_link
from FZBypass.core.bot_utils import AuthChatsTopics, convert_time, BypassFilter
from FZBypass.core.exceptions import DDLException


@Bypass.on_message(command('start'))
async def start_msg(client, message):
    await message.reply(f'''<b><i>CMT Bypass Bot!</i></b>
    
    <i>Bot Multi yang Kuat dan Elegan dibuat dalam code Python, bisa membypass berbagai Link Shortener, Link Scrape, dan lainnya...</i>
    
    <i><b>Bot Dimulai {convert_time(time() - BOT_START)} Lalu...</b></i>

    <b>Gabung di Group Jika Mau Gunakan Bot Ini</b>''',
        quote=True,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton('💻Modif', url='https://www.comelmuewa84.eu.org'), InlineKeyboardButton('📲Channel', url='https://t.me/+LUX4Ppe0-YI4NTk1'), InlineKeyboardButton('🖥Deploy', url="https://github.com/Yyg-Masamba/CMTbypass")]
            ])
    )


@Bypass.on_message(BypassFilter & (user(Config.OWNER_ID) | AuthChatsTopics))
async def bypass_check(client, message):
    uid = message.from_user.id
    if (reply_to := message.reply_to_message) and (reply_to.text is not None or reply_to.caption is not None):
        txt = reply_to.text or reply_to.caption
        entities = reply_to.entities or reply_to.caption_entities
    elif Config.AUTO_BYPASS or len(message.text.split()) > 1:
        txt = message.text
        entities = message.entities
    else:
        return await message.reply('<i>No Link Provided!</i>')
    
    wait_msg = await message.reply("<i>Bypassing...</i>")
    start = time()

    link, tlinks, no = '', [], 0
    atasks = []
    for enty in entities:
        if enty.type == MessageEntityType.URL:
            link = txt[enty.offset:(enty.offset+enty.length)]
        elif enty.type == MessageEntityType.TEXT_LINK:
            link = enty.url
            
        if link:
            no += 1
            tlinks.append(link)
            atasks.append(create_task(direct_link_checker(link)))
            link = ''

    completed_tasks = await gather(*atasks, return_exceptions=True)
    
    parse_data = []
    for result, link in zip(completed_tasks, tlinks):
        if isinstance(result, Exception):
            bp_link = f"\n\n📵 <b><u>Bypass Error:</b></u> {result}"
        elif is_excep_link(link):
            bp_link = result
        elif isinstance(result, list):
            bp_link, ui = "", "♻️"
            for ind, lplink in reversed(list(enumerate(result, start=1))):
                bp_link = f"\n\n{ui} <b><u>{ind}x Hasil Bypass:</b></u> \n{lplink}" + bp_link
                ui = "┠"
        else:
            bp_link = f"\n🖥 <b><u>Bypass Link:</b></u> {result}"
    
        if is_excep_link(link):
            parse_data.append(f"{bp_link}\n\n▬▬▬▬▬▬▬▬▬▬▬▬▬\n\n")
        else:
            parse_data.append(f'🖥 <b><u>Link Sumber:</b></u>\n {link}{bp_link}\n\n▬▬▬▬▬▬▬▬▬▬▬▬▬\n\n')
            
    end = time()

    if len(parse_data) != 0:
        parse_data[-1] = parse_data[-1] + f"📚 <b>Total Links : {no}</b>\n🕰 <b>Waktu <code>{convert_time(end - start)}</code></b> !\n🦹‍♀️ <b>Tugas_Oleh </b>{message.from_user.mention} ( #ID{message.from_user.id} )"
    tg_txt = "𝐏𝐄𝐀 𝐌𝐀𝐒𝐀𝐌𝐁𝐀\n\n"
    for tg_data in parse_data:
        tg_txt += tg_data
        if len(tg_txt) > 4000:
            await wait_msg.edit(tg_txt, disable_web_page_preview=True)
            wait_msg = await message.reply("<i>Fetching...</i>", reply_to_message_id=wait_msg.id)
            tg_txt = ""
            await asleep(2.5)
    
    if tg_txt != "":
        await wait_msg.edit(tg_txt, disable_web_page_preview=True)
    else:
        await wait_msg.delete()


@Bypass.on_message(command('log') & user(Config.OWNER_ID))
async def send_logs(client, message):
    await message.reply_document('log.txt', quote=True)


@Bypass.on_inline_query()
async def inline_query(client, query):
    answers = [] 
    string = query.query.lower()
    if string.startswith("!bp "):
        link = string.strip('!bp ')
        start = time()
        try:
            bp_link = await direct_link_checker(link, True)
            end = time()
            
            if not is_excep_link(link):
                bp_link = f"🖥 <b><u>Link Sumber:</b></u> {link}\n┃\n⚙️ <b><u>Bypass Link:</b></u> {bp_link}"
            answers.append(InlineQueryResultArticle(
                title="✅️ Bypass Link Berhasil !",
                input_message_content=InputTextMessageContent(
                    f'{bp_link}\n\n✎﹏﹏﹏﹏﹏﹏﹏﹏﹏﹏﹏﹏﹏﹏﹏\n\n🧭 <b>Took Only <code>{convert_time(end - start)}</code></b>',
                    disable_web_page_preview=True,
                ),
                description=f"Bypass via !bp {link}",
                reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton('Bypass Lagi', switch_inline_query_current_chat="!bp ")]
                ])
            ))
        except Exception as e:
            bp_link = f"<b>Bypass Error:</b> {e}"
            end = time()

            answers.append(InlineQueryResultArticle(
                title="❌️ Bypass Link Error !",
                input_message_content=InputTextMessageContent(
                    f'🖥 <b>Link Sumber:</b> {link}\n┃\n⏱ {bp_link}\n\n✎﹏﹏﹏﹏﹏﹏﹏﹏﹏﹏﹏﹏﹏﹏﹏\n\n🧭 <b>Took Only <code>{convert_time(end - start)}</code></b>',
                    disable_web_page_preview=True,
                ),
                description=f"Bypass via !bp {link}",
                reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton('Bypass Again', switch_inline_query_current_chat="!bp ")]
                ])
            ))    
        
    else:
        answers.append(InlineQueryResultArticle(
                title="♻️ Bypass Usage: Dalam Antrean",
                input_message_content=InputTextMessageContent(
                    '''<b><i>CMT Bypass Bot!</i></b>
    
    <i>Bot Multi yang Kuat dan Elegan dibuat dalam code Python, bisa membypass berbagai Link Shortener, Link Scrape, dan lainnya...</i>
    
🎛 <b>Inline Use :</b> !bp [Single Link]''',
                ),
                description="Bypass via !bp [link]",
                reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("CMT Channel", url="https://t.me/+LUX4Ppe0-YI4NTk1"),
                        InlineKeyboardButton('Coba Bypass', switch_inline_query_current_chat="!bp ")]
                ])
            ))
    try:
        await query.answer(
            results=answers,
            cache_time=0
        )
    except QueryIdInvalid:
        pass
