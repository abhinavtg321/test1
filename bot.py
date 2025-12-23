import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from pymongo import MongoClient

BOT_TOKEN = os.getenv("BOT_TOKEN")
MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI)
db = client["gbanbot"]
gban_db = db["gbans"]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ GBAN Bot is running")

async def gban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /gban user_id")
        return

    user_id = int(context.args[0])
    gban_db.update_one(
        {"user_id": user_id},
        {"$set": {"user_id": user_id}},
        upsert=True
    )
    await update.message.reply_text(f"🚫 User {user_id} globally banned")

async def ungban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /ungban user_id")
        return

    user_id = int(context.args[0])
    gban_db.delete_one({"user_id": user_id})
    await update.message.reply_text(f"✅ User {user_id} unbanned")

async def check_gban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    user = update.message.from_user
    if gban_db.find_one({"user_id": user.id}):
        await update.message.chat.ban_member(user.id)

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("gban", gban))
    app.add_handler(CommandHandler("ungban", ungban))
    app.add_handler(CommandHandler(None, check_gban))

    app.run_polling()

if __name__ == "__main__":
    main()
