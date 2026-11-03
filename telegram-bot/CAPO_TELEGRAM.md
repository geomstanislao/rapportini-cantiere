# Sezione da aggiungere a skills/capo/SKILL.md (dopo il punto 7)

## 8. Modo Telegram (Stanislao non è al PC)

Se Stanislao scrive «telegram», «sono in cantiere» o «sono fuori» nella richiesta, passi al **modo Telegram** per tutta la
conversazione: le domande a scelta non le fai nel terminale, le mandi sul topic Telegram della gara. Ogni gara ha un topic
con lo stesso nome della cartella della gara (es. `FALK_Adige`).

Il programma sta sul Drive: `H:\Il mio Drive\GARE APPALTO Furlan\_MASTER\telegram-bot\ask.py` (stesso percorso sui due PC).

**Domanda a scelta** (aspetta la risposta, che arriva sul telefono):

    python "H:\Il mio Drive\GARE APPALTO Furlan\_MASTER\telegram-bot\ask.py" ask NOME_GARA "Domanda breve?" -o "Sì" -o "No" -o "Modifica" --timeout 540

- Stampa la risposta scelta (anche testo libero o vocale trascritto). Una domanda alla volta, testo breve e opzioni corte.
- Se esce con codice 2 (nessuna risposta in 9 minuti), manda un `notify` «Aspetto la tua risposta» e ripeti la domanda.
- Se risponde `ERRORE: gara ... non configurata`, dillo nel terminale e continua lì: il topic va collegato con `/collega`.

**Avvisi** (non aspettano risposta): dopo ogni agente che finisce, e a ogni blocco, manda 2-4 righe:

    python "H:\Il mio Drive\GARE APPALTO Furlan\_MASTER\telegram-bot\ask.py" notify NOME_GARA "Fatto: analisi APU. Punti aperti: 3. Prossimo passo: confronto offerte."

**Messaggi liberi** scritti da Stanislao nel topic (istruzioni, note): leggili all'inizio e dopo ogni agente con

    python "H:\Il mio Drive\GARE APPALTO Furlan\_MASTER\telegram-bot\ask.py" read NOME_GARA

Resta valido tutto il resto: chiedi prima, non dopo (punto 4); conferme importanti (invio offerta, modifiche al GO master)
solo con risposta esplicita, mai con un timeout.
