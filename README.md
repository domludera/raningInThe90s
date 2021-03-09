```
                     _             ____    ________         ____  ____
   _________ _____  (_)___  ____ _/  _/___/_  __/ /_  ___  / __ \/ __ \_____
  / ___/ __ `/ __ \/ / __ \/ __ `// // __ \/ / / __ \/ _ \/ /_/ / / / / ___/
 / /  / /_/ / / / / / / / / /_/ // // / / / / / / / /  __/\__, / /_/ (__  )
/_/   \__,_/_/ /_/_/_/ /_/\__, /___/_/ /_/_/ /_/ /_/\___//____/\____/____/
                         /____/
            ---+ Yes, I want to know. Yes, I want to see. +---

Simple IRC client and server



## SERVER

usage: server/irc_server.py [-h] [--server '<SERVER>' --port '<PORT>']

optional arguments:
    -h, --help              Show this help message and exit
    --server '<SERVER>'     Target server to bind to
    --port <PORT>           Target port to use
    


## CLIENT

usage: client/irc_client.py [-h] [--server '<SERVER>' --port '<PORT>'] [-m]

optional arguments:
    -h, --help              Show this help message and exit
    --server '<SERVER>'     Target server to initiate a connection to
    --port <PORT>           Target port to use
    -m                      Enable music
    
using IRC commands, after launching the client use:
  USER <username> to initialize your username
  NICK <nickname> to set your nickname
after that you will automatically join the #global channel
and you can start chatting!
    
```
