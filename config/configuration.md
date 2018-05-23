Configuration files
-------------------
Config files files go in this directory, and are shared with Docker
    images. Specifically, this folder will be mounted rw in
    `mechasqueak/config`

The template configuration, `config.template.json` has all the necessary
    keys to run mechasqueak, however is justa stub.

The sections
------------
# IRC
This section contains configuration elements prudent to the pydle
irc client, such as username, server, and channels to connect to.


| Element| description|
|---|---|
| server|  the irc server to connect to|
| presence| the bots username|
| port| irc port to connect to. `3367` for plain, `3397` for ssl|
| tls| set to true to connect to tls, a false setting disables SASL|
|channels| list of channels to connec to|

