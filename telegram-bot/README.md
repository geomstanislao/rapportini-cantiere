# Bot Telegram per le gare

Una chat (o un topic) per gara. Gli agenti fanno domande, tu rispondi con un bottone, un testo o un vocale.

## Setup
1. Crea il bot con @BotFather e copia il token in `.env` (vedi `.env.example`).
2. Scrivi `/id` al bot e metti il tuo ID in `ALLOWED_USER_IDS`.
3. Crea un gruppo con **Topic attivi**, aggiungi il bot come admin, un topic per gara.
   (In alternativa una chat per gara.)
4. In ogni topic scrivi `/collega OFF-001` (nome gara).
5. `pip install -r requirements.txt && python bot.py` (tienilo acceso sul PC o su un server).

## Uso dagli agenti (Bash)
    python ask.py ask OFF-001 "Confermi i Super Capitoli?" -o "Sì" -o "No" -o "Modifica"
    python ask.py notify OFF-001 "Analisi APU completate"
    python ask.py read OFF-001      # messaggi liberi scritti da te nel topic

`ask` resta in attesa e stampa la risposta. Se scrivi testo o vocale nel topic, risponde alla domanda aperta
(o a quella a cui rispondi con "reply"). Vocali: serve `OPENAI_API_KEY` per la trascrizione.

Comandi: `/gare` elenca le gare e le domande in attesa.

## Due PC (lavoro + portatile) con Google Drive
- Crea su Drive la cartella `gare-bot` e imposta **"Mirror files"** (sempre offline) in Google Drive per desktop.
- In `.env` di **ogni** PC: `BOT_QUEUE=<percorso>\gare-bot\queue` e `GARE_FILE=<percorso>\gare-bot\gare.json`.
- Avvia `bot.py` **solo sul PC lavoro**. Sul portatile gli agenti usano solo `ask.py`.
- Telegram accetta una sola istanza del bot: non avviarlo su entrambi.
