#!/usr/bin/env python3
from __future__ import unicode_literals
import os
import logging
from urllib.request import urlopen

import youtube_dl
from bs4 import BeautifulSoup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from sqlalchemy.orm import Session

from credentials import ENGINE, TOKEN, CELULAR, IPOD, Ipod_Path
from database import Backup


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

u = Updater(TOKEN)
dp = u.dispatcher


def start(bot, update):
    bot.sendMessage(update.message.chat_id, text="CraraBot <3 \n Usual Telegram bot, YOLO, no UTF-8 characters pls <3")


def music(bot, update):
    title, video_url = search(update.message.text)
    bot.sendMessage(update.message.chat_id, text="Pedido Recebido... Baixando:" + title)
    session = Session(bind=ENGINE)
    session.add(Backup(title=title, video_url=video_url))
    session.commit()
    session.close()
    download(title, video_url)
    if CELULAR == 0:
        print("Telegram sender Disabled / Envio para o telegram desativado, talvez seja algo nas configuracoes")
    else:
        print("Telegram sender Enabled / Enviando para o telegram")
        bot.sendMessage(update.message.chat_id, text="-----------------------\n Convertendo e Enviando ....")
        bot.sendAudio(update.message.chat_id,
         audio=open(title.replace(' ','') + '.mp3', 'rb'),
          title=title)

    ipod()
    os.remove(title.replace(' ','') + '.mp3')

def ipod():
    if IPOD == 0:
        print("Ipod Upload Disabled / Upload para o ipod desativado")
        print("----------------------------------------------------")
        print("./end")
    else:
        comando = "gnupod_addsong -m "+ Ipod_Path +" *.mp3"
        print("Uploading on ipod / Fazendo upload para o ipod")
        os.system(comando)
        print ("Upload Concluido!")
        print("----------------------------------------------------")
        print("./end")

def search(text):
    query = '+'.join(text.lower().split())
    url = 'https://www.youtube.com/results?search_query=' + query
    content = urlopen(url).read()
    soup = BeautifulSoup(content, 'html.parser')
    tag = soup.find('a', {'rel': 'spf-prefetch'})
    title = tag.text
    video_url = 'https://www.youtube.com' + tag.get('href')
    return title, video_url


def download(title, video_url):
    ydl_opts = {
        'outtmpl': title.replace(' ','') + '.%(ext)s',
        'format': 'bestaudio/best', 'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])

def ipod_on(bot, update):
    if(IPOD == 0):
      IPOD = 1
    else:
      IPOD = 0
    bot.sendMessage(update.message.chat_id, text="--------------\nIpod Upload Ativado")

dp.add_handler(CommandHandler("start", start))
#dp.add_handler(CommandHandler("ipod_on", ipod_on))
#dp.add_handler(CommandHandler("ipod_off", ipod_off))
#dp.add_handler(CommandHandler("tele_on", tele_on))
#dp.add_handler(CommandHandler("tele_off", tele_off))
dp.add_handler(MessageHandler([Filters.text], music))

u.start_polling()
u.idle()
