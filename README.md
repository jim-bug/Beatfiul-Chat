# Beautifiul-Chat
Una chat bellissima.

## Come eseguire il progetto
1. `pip install -r requirements.txt`
2. `cd bc_project`
3. `daphne -p PORT bc_project.asgi:application`

## Dettagli sull'implementazione
- Daphne consente di eseguire il server ASGI gestendo le richieste HTTP e WebSocket.
- Channels consente di gestire le connessioni WebSocket.
- Whitenoise consente di servire i file statici