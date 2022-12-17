import logging
import os
import random
from unicodedata import name
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
import atoma, requests, datetime, dateutil


groupChatID = "<groupChatID (in my example it was a unique number, you can grab it from the debug info)>"
TOKEN = "<your token from the botfather(should look similar to XXXX:YYYYYYYYYYY)>"

#set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)

feeds = [] #Initialize empty array for feeds

#pre-populate feeds from a local file named "atom-feeds (format needs to be one atom url/line)"
with open('atom-feeds', 'r') as file:
    for line in file:
        line = line.strip()
        feeds.append(line)


#async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
 #   await context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)

#async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
   # await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")

#async def caps(update: Update, context: ContextTypes.DEFAULT_TYPE):
  #  text_caps = ' '.join(context.args).upper()
  #  await context.bot.send_message(chat_id=update.effective_chat.id, text=text_caps)

### Feed parser stuff goes here

#linkstosend = []

async def parse_a_feed(current_feed):
    #print("Current date is: " + str(datetime.datetime.utcnow()))
    now_date = datetime.datetime.utcnow()
    #print("WTFFFFFFFFF")
    print("###### NOW DATE: " + str(now_date))
    for j in current_feed.entries:
        naivetime = j.updated.replace(tzinfo=None)
        publishedWithinThreshold = now_date - naivetime < datetime.timedelta(seconds=30)
        if publishedWithinThreshold:
            element = j.links[0]
            href = element.href
            print("###### Naivetime from feed is : " + str(naivetime))
            print("###### now_date is currently: " + str(now_date))
            print("###### PublishedWithinThreshold is currently: " + str(publishedWithinThreshold))
            print("###### This is what we are sending to the chat if we triggered it now: " + str(href) + "\n### END OF MESSAGE")
            textToSend = "New Github update just dropped! Check it out: " + str(href) + "."
            tempbot = Bot(TOKEN)
            await tempbot.send_message(chat_id=groupChatID, text=textToSend)
            #sendtest(update: Update, context: DEFAULT_TYPE, message: href)

#def parse_all(feeds):
async def parse_all(feeds):
    print("###### Fetching feeds for the following urls: " + str(feeds))
    for i in feeds:
        response = requests.get(i)
        feed = atoma.parse_atom_bytes(response.content)
        print("Current feed is: " + str(feed.title))
        await parse_a_feed(feed)

#Function to send arbitrary message to group chat
async def sendtest(update: Update, context: ContextTypes.DEFAULT_TYPE, message):   
    await context.bot.send_message(chat_id=groupChatID, text=message)

### Async functions go here

async def githubpage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="your project's github page can be found here ==> https://www.github.com/your-project")

## Media functions
async def meme(update: Update, context: ContextTypes.DEFAULT_TYPE):
    random_file = 'memes/' + random.choice(os.listdir('memes'))
    print('this should be printing your random filename')
    print(random_file)
    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=random_file)

### Job functions
async def dojob(context: ContextTypes.DEFAULT_TYPE) -> None:
  #just a test to see if we can set jobs
  print("####### JOB TRIGGERED #######")
  values = await parse_all(feeds)

async def github(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
      onOff = str(context.args[0])
      if (onOff == "on"):
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Ok, I'll watch github for updates.")
        #This next line actually creates/schedules a job called "dojob" to run every 30 seconds.
        context.job_queue.run_repeating(dojob, 30, name=str(dojob))
        return

      if (onOff == "off"):
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Ok, I'll stop watching github for updates.")
        ##Add logic here to kill any jobs that are running related to githubparser stuff
        #print("Let's try another way of looking at jobs to schedule for removal: " + str(context.job_queue.jobs()))
        #This next for loop ctually clears the jobs queue
        for job in context.job_queue.jobs():
          job.schedule_removal()
        return

      else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Not a valid option. Usage: /github <on/off>")
        return

    except (IndexError, ValueError):
      await context.bot.send_message(chat_id=update.effective_chat.id, text="Usage: /github <on/off>")
      return

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Unknown command. While I'm still learning commands, why not sudo make me a sandwich?")

if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()
    job_queue = application.job_queue

    ##Main handlers
  #  echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
  #  caps_handler = CommandHandler('caps', caps)
  #  start_handler = CommandHandler('start', start)
    github_handler = CommandHandler('github', github)
    meme_handler = CommandHandler('meme', meme)
    githubpage_handler = CommandHandler('githubpage', githubpage)
    sendtest_handler = CommandHandler('sendtest', sendtest)

    #Other handlers
    unknown_handler = MessageHandler(filters.COMMAND, unknown)

  #  application.add_handler(start_handler)
  #  application.add_handler(echo_handler)
  #  application.add_handler(caps_handler)
    application.add_handler(github_handler)
    application.add_handler(meme_handler)
    application.add_handler(githubpage_handler)
    application.add_handler(sendtest_handler)

    application.add_handler(unknown_handler)
    
    application.run_polling()
