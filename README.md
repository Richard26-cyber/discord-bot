# Discord-Bot

Ein Discord-Bot in Python, den ich für meinen eigenen Server gebaut und
nach und nach erweitert habe. Jede Funktion liegt als eigenes Cog vor,
alles was gespeichert werden muss, landet in einer SQLite-Datei.

## Funktionen

| Cog | Was es tut |
|---|---|
| `antispam.py` | Erkennt und bremst Spam im Chat |
| `begruessung.py` | Begrüßt neue Mitglieder |
| `geburtstage.py` | Speichert Geburtstage und gratuliert automatisch |
| `erinnerung.py` | Erinnerungen mit Zeitangabe |
| `quiz.py` | Quiz-Runden mit Punktewertung |
| `poll.py` | Abstimmungen |
| `radio.py` | Spielt Webradio-Streams im Sprachkanal |
| `rollen.py` | Rollenvergabe per Reaktion |
| `zitate.py` | Zitatsammlung |
| `wins.py` | Punktestand der Mitglieder |
| `aktivitaet.py`, `fancy_name.py`, `info.py`, `ping.py`, `vogel.py` | Kleinere Befehle |

## Technik

- **discord.py** mit Cog-Architektur — jede Funktion ist ein eigenes Modul und
  lässt sich einzeln nachladen, ohne den Bot neu zu starten
- **SQLite** über `database.py` für alles, was Bestand haben muss
- **Konfiguration über Umgebungsvariablen** — das Token steht in einer `.env`,
  die nie ins Repository gelangt

## Selbst starten

```bash
pip install -r requirements.txt
```

```bash
cp .env.example .env
```

Eigenes Token aus dem [Discord Developer Portal](https://discord.com/developers/applications)
in die `.env` eintragen, dann:

```bash
python main.py
```

## Zum Token

Wer das Bot-Token hat, steuert den Bot. Es steht deshalb nur in der lokalen
`.env`, die von `.gitignore` ausgeschlossen ist — im Code steht ausschließlich
`os.getenv()`. Fehlt der Wert, bricht der Bot beim Start mit einer klaren
Meldung ab, statt sich mit leerem Token zu verbinden.

---

[@Richard26-cyber](https://github.com/Richard26-cyber) · Cyber-Security-Student
