from telegram.ext import ApplicationBuilder, MessageHandler, filters, CallbackQueryHandler, CommandHandler
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from util import *
import openai
from gpt import *

promt = open("Путь к файлу Ryan Gosling.promt").read()


async def show_main_menu(update, context, commands):
    command_list = [BotCommand(key, value) for key, value in commands.items()]
    await context.bot.set_my_commands(command_list, scope=BotCommandScopeChat(chat_id=update.effective_chat.id))
    await context.bot.set_chat_menu_button(menu_button=MenuButtonCommands(), chat_id=update.effective_chat.id)


async def dialog_mods(update, context):
    if dialog.mode == 'dialog':
        await dialog_gpt(update, context)


def set_prompt(self, prompt_text):
    self.message_list.clear()
    self.message_list.append({"role": "system", "content": prompt_text})


async def add_message(self, message_text):
    self.message_list.append({"role": "user", "content": message_text})
    return await self.send_message_list()


async def send_text(update, context, text):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)


async def start(update, context):
    dialog.mode = "dialog"
    message = ("Добро пожаловать в онлайн диалог с Райаном Гослингом!" + '\n' +
               "Для начала разговора достаточно отправить любое сообщение в чат." +
               '\n' + "Если же вы хотите закончить,"
                      " то просто введите команду /stop. Приятно вам поболтать)")

    await show_main_menu(update, context, {
        "start": "Главное меню",
        "stop": "Закончить диалог",
        "new": "Начать новый диалог"
    })

    await send_text(update, context, message)
    chatgpt.set_prompt(promt)


async def dialog_gpt(update, context):
    text = update.message.text
    answer = await chatgpt.add_message(text)
    await send_text(update, context, answer)


async def dialog_stop(update, context):
    await send_text(update, context, "Диалог закончен!" + '\n' +
                    'Если хотите пообщаться еще, то просто напишите команду /new')


dialog = Dialog()
dialog.mode = None
chatgpt = ChatGptService(token="Ваш токен чата gpt")

app = ApplicationBuilder().token("Ваш токен телеграмм бота").build()
app.add_handler(CommandHandler("new", dialog_gpt))
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("stop", dialog_stop))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, dialog_mods))
app.run_polling()
