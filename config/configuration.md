Configuration files
-------------------
Config files files go in this directory, and are shared with Docker
    images. Specifically, this folder will be mounted rw in
    `mechasqueak/config`

The template configuration, `config.template.json` has all the necessary
    keys to run mechasqueak, however it's just a stub.

The sections
------------
# IRC
This section contains configuration elements prudent to the pydle
irc client, such as username, server, and channels to connect to.


| Element| description |
|--------|-------------|
| server|  the irc server to connect to|
| nickname| the bots username|
| port| irc port to connect to. `6667` for plain, `6697` for ssl|
| tls| set to true to connect to tls, a false setting disables SASL|
|channels| list of channels to connect to|

# Authentication
This section contains details relavent to authenticating against the
    the irc server via SASL

| Element| description |
|--------|-------------|
|  method| SASL mechanism to use. supported options are `PLAIN` and `EXTERNAL` |
|plain|configuration options for SASL PLAIN (see below)|
|external|configuration options for SASL EXTERNAL(See below)|

## plain
Authentication settings for SASL plain (username + password)

| Element| description |
|--------|-------------|
| username | nickserv username |
| password | nickserv password|
| identity  | nickserv account|

## external
Authentication settings for SASL external (client certificate)

| Element| description |
|--------|-------------|
| tls_client_cert | name of the certificate file, relative to `certs/`|

------------------
# logging
Logging settings

| Element| description |
|--------|-------------|
| base_logger| mecha's parent logger|
|log_file|name of the log file to write logs into, relative to `logs/`|

------------------
# commands
Command specific settings

| Element| description |
|--------|-------------|
|trigger|string that must prefix messages recieved from IRC to be processed as commands|

------------------
# API
API configuration elements
**note**: this section is currently unimplemented

| Element| description |
|--------|-------------|
|online_mode|should mecha start up in online mode?|
|url|base url for the API|
|tokenfile|name of the API token file, relative to `certs/`|
