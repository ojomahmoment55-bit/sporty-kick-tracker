<START COPY> 
(Scroll to copy everything)

# tracker_bot.py
# SportyKick Telegram Tracker Bot (Safe Play + High Risk Modes)
# Reads TG_BOT_TOKEN from environment variables
# Deploy on Railway / VPS / Any Cloud

import os
import json
from pathlib import Path
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes,
    MessageHandler, filters
)

DATA_FILE = Path("bot_data.json")
DEFAULT_THRESHOLD = 6
DEFAULT_CUTOFF = 1.5

def load_data():
    if DATA_FILE.exists():
        try:
            return json.loads(DATA_FILE.read_text())
        except:
            return {}
    return {}

def save_data(data):
    DATA_FILE.write_text(json.dumps(data, indent=2))

def get_state(data, cid):
    if cid not in data:
        data[cid] = {
            "mode": "A",
            "threshold": DEFAULT_THRESHOLD,
            "low_cutoff": DEFAULT_CUTOFF,
            "consec_low": 0,
            "history": [],
            "alerts": True
        }
    return data[cid]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✅ SportyKick Tracker Activated\n\n"
        "/mode A  = Safe Play\n"
        "/mode B  = High Risk\n"
        "/setthreshold 6\n"
        "/setcutoff 1.5\n"
        "/addround 1.07\n"
        "/status\n"
        "/reset\n"
        "/togglealerts\n"
        "/myid"
    )

async def myid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(str(update.effective_chat.id))

async def mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cid = str(update.effective_chat.id)
    data = load_data()
    s = get_state(data, cid)

    if not context.args or context.args[0].upper() not in ("A", "B"):
        await update.message.reply_text("Use: /mode A or /mode B")
        return

    s["mode"] = context.args[0].upper()
    save_data(data)
    await update.message.reply_text(f"Mode set to {s['mode']}")

async def setthreshold(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cid = str(update.effective_chat.id)
    data = load_data()
    s = get_state(data, cid)

    try:
        n = int(context.args[0])
        s["threshold"] = n
        save_data(data)
        await update.message.reply_text(f"Threshold set to {n}")
    except:
        await update.message.reply_text("Usage: /setthreshold 6")

async def setcutoff(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cid = str(update.effective_chat.id)
    data = load_data()
    s = get_state(data, cid)

    try:
        c = float(context.args[0])
        s["low_cutoff"] = c
        save_data(data)
        await update.message.reply_text(f"Cutoff set to {c}x")
    except:
        await update.message.reply_text("Usage: /setcutoff 1.5")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cid = str(update.effective_chat.id)
    s = get_state(load_data(), cid)
    await update.message.reply_text(
        f"Mode: {s['mode']}\n"
        f"Threshold: {s['threshold']}\n"
        f"Cutoff: {s['low_cutoff']}x\n"
        f"Streak: {s['consec_low']}\n"
        f"Alerts: {s['alerts']}"
    )

async def togglealerts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cid = str(update.effective_chat.id)
    data = load_data()
    s = get_state(data, cid)
    s["alerts"] = not s["alerts"]
    save_data(data)
    await update.message.reply_text(f"Alerts: {s['alerts']}")

async def reset_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cid = str(update.effective_chat.id)
    data = load_data()
    s = get_state(data, cid)
    s["consec_low"] = 0
    s["history"] = []
    save_data(data)
    await update.message.reply_text("Reset done.")

async def addround(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cid = str(update.effective_chat.id)
    data = load_data()
    s = get_state(data, cid)

    try:
        v = float(context.args[0])
    except:
        await update.message.reply_text("Usage: /addround 1.07")
        return

    s["history"].append(v)
    if len(s["history"]) > 200:
        s["history"].pop(0)

    if v < s["low_cutoff"]:
        s["consec_low"] += 1
    else:
        s["consec_low"] = 0

    save_data(data)

    if s["alerts"] and s["consec_low"] >= s["threshold"]:
        if s["mode"] == "A":
            msg = "⚠️ SAFE PLAY SIGNAL\nEntry small\nCashout 1.30x - 1.60x"
        else:
            msg = "🔥 HIGH RISK SIGNAL\nPossible big-run soon\nHold for 3x+ (Only if ready)"

        await update.message.reply_text(msg)
        s["consec_low"] = 0
        save_data(data)

async def text_handler(update: Update, context):
    t = update.message.text.replace("x", "").strip()
    try:
        float(t)
        await addround(update, type("C", (), {"args": [t]})())
    except:
        pass

def main():
    token = os.environ.get("TG_BOT_TOKEN")
    app = ApplicationBuilder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("myid", myid))
    app.add_handler(CommandHandler("mode", mode))
    app.add_handler(CommandHandler("setthreshold", setthreshold))
    app.add_handler(CommandHandler("setcutoff", setcutoff))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("reset", reset_cmd))
    app.add_handler(CommandHandler("togglealerts", togglealerts))
    app.add_handler(CommandHandler("addround", addround))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), text_handler))

    app.run_polling()

if __name__ == "__main__":
    main()

<END COPY>
