# Beautifiul-Chat
Una chat bellissima.

## Come eseguire il progetto
1. `pip install -r requirements.txt`
2. `cd bc_project`
3. <b>Opzionale</b>: Velocizza le route statiche<br>`python3 manage.py collectstatic`
3. `daphne -p PORT bc_project.asgi:application` oppure `python3 manage.py runserver`

## Dettagli sull'implementazione
- Daphne consente di eseguire il server ASGI gestendo le richieste HTTP e WebSocket.
- Channels consente di gestire le connessioni WebSocket.
- Whitenoise consente di servire i file statici