#!/usr/bin/env python3
"""Bot Telegram: un topic/chat per ogni gara. Gli agenti fanno domande (ask.py),
Stanislao risponde con un bottone, un testo o un vocale."""
import json, logging, os
import httpx
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (Application, CallbackQueryHandler, CommandHandler,
                          ContextTypes, MessageHandler, filters)
from common import QUEUE, load_env, load_gare, save_gare, write_json

load_env()
logging.basicConfig(level=logging.INFO)
ALLOWED = {int(x) for x in os.environ.get("ALLOWED_USER_IDS", "").split(",") if x.strip()}


def ok(update: Update) -> bool:
    u = update.effective_user
    return bool(u) and u.id in ALLOWED


def gara_of(chat_id, thread_id):
    for name, g in load_gare().items():
        if g["chat_id"] == chat_id and g.get("thread_id") == thread_id:
            return name


def target(name):
    g = load_gare().get(name)
    return (g["chat_id"], g.get("thread_id")) if g else (None, None)


def sent_for(gara):
    out = []
    for f in sorted((QUEUE / "sent").glob("*.json"), key=lambda p: p.stat().st_mtime):
        q = json.loads(f.read_text())
        if q["gara"] == gara:
            out.append(q)
    return out


def answer(qid, text):
    write_json(QUEUE / "answers" / f"{qid}.json", {"answer": text})
    (QUEUE / "sent" / f"{qid}.json").unlink(missing_ok=True)


async def pump(ctx: ContextTypes.DEFAULT_TYPE):
    """Spedisce su Telegram le domande messe in coda dagli agenti."""
    for f in sorted((QUEUE / "inbox").glob("*.json")):
        q = json.loads(f.read_text())
        chat, thread = target(q["gara"])
        if chat is None:
            logging.warning("Gara sconosciuta: %s", q["gara"])
            if q.get("wait"):
                write_json(QUEUE / "answers" / f"{q['id']}.json",
                           {"answer": f"ERRORE: gara {q['gara']} non configurata"})
            f.unlink()
            continue
        markup = None
        if q["options"]:
            rows = [[InlineKeyboardButton(o, callback_data=f"a:{q['id']}:{i}")]
                    for i, o in enumerate(q["options"])]
            markup = InlineKeyboardMarkup(rows)
        text = f"❓ {q['text']}" if q.get("wait") else f"ℹ️ {q['text']}"
        m = await ctx.bot.send_message(chat, text, message_thread_id=thread, reply_markup=markup)
        f.unlink()
        if q.get("wait"):
            q["message_id"] = m.message_id
            write_json(QUEUE / "sent" / f"{q['id']}.json", q)


async def on_button(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    cq = update.callback_query
    if not ok(update):
        return await cq.answer("Non autorizzato", show_alert=True)
    _, qid, idx = cq.data.split(":")
    f = QUEUE / "sent" / f"{qid}.json"
    if not f.exists():
        return await cq.answer("Domanda già chiusa")
    q = json.loads(f.read_text())
    choice = q["options"][int(idx)]
    answer(qid, choice)
    await cq.answer("Inviato")
    await cq.edit_message_text(f"❓ {q['text']}\n✅ {choice}")


async def transcribe(update: Update) -> str | None:
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        return None
    tg = await (update.message.voice or update.message.audio).get_file()
    data = bytes(await tg.download_as_bytearray())
    async with httpx.AsyncClient(timeout=60) as c:
        r = await c.post("https://api.openai.com/v1/audio/transcriptions",
                         headers={"Authorization": f"Bearer {key}"},
                         files={"file": ("voce.ogg", data)},
                         data={"model": "whisper-1", "language": "it"})
    r.raise_for_status()
    return r.json()["text"]


async def on_message(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ok(update):
        return
    msg = update.message
    gara = gara_of(msg.chat_id, msg.message_thread_id)
    if not gara:
        return await msg.reply_text("Questa chat non è collegata a una gara. Usa /collega NOME")
    text = msg.text
    if msg.voice or msg.audio:
        text = await transcribe(update)
        if text is None:
            return await msg.reply_text("Vocale ricevuto ma trascrizione non attiva (manca OPENAI_API_KEY).")
        await msg.reply_text(f"🎙 {text}")
    pending = sent_for(gara)
    target_q = None
    if msg.reply_to_message:  # risposta diretta a una domanda precisa
        target_q = next((q for q in pending if q["message_id"] == msg.reply_to_message.message_id), None)
    target_q = target_q or (pending[0] if pending else None)
    if target_q:
        answer(target_q["id"], text)
        await msg.reply_text(f"✅ Risposta inviata: {text}")
    else:  # messaggio libero: l'agente lo legge con `ask.py read GARA`
        with open(QUEUE / "messages" / f"{gara}.jsonl", "a") as fh:
            fh.write(json.dumps({"text": text}, ensure_ascii=False) + "\n")
        await msg.reply_text("📥 Annotato per l'agente.")


async def cmd_collega(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ok(update):
        return
    if not ctx.args:
        return await update.message.reply_text("Uso: /collega NOME_GARA (nel topic o chat della gara)")
    gare = load_gare()
    gare[ctx.args[0]] = {"chat_id": update.message.chat_id, "thread_id": update.message.message_thread_id}
    save_gare(gare)
    await update.message.reply_text(f"🔗 Collegata la gara {ctx.args[0]} a questa chat.")


async def cmd_gare(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ok(update):
        return
    gare = load_gare()
    lines = []
    for n in gare:
        k = len(sent_for(n))
        lines.append(f"• {n}" + (f" — {k} domande in attesa" if k else ""))
    await update.message.reply_text("\n".join(lines) or "Nessuna gara collegata.")


async def cmd_id(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"user_id: {update.effective_user.id}")


def main():
    app = Application.builder().token(os.environ["TELEGRAM_BOT_TOKEN"]).build()
    app.add_handler(CommandHandler("id", cmd_id))
    app.add_handler(CommandHandler("collega", cmd_collega))
    app.add_handler(CommandHandler("gare", cmd_gare))
    app.add_handler(CallbackQueryHandler(on_button, pattern="^a:"))
    app.add_handler(MessageHandler((filters.TEXT & ~filters.COMMAND) | filters.VOICE | filters.AUDIO, on_message))
    app.job_queue.run_repeating(pump, interval=2, first=1)
    app.run_polling()


if __name__ == "__main__":
    main()
