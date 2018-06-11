# Client-side certificates for SASL EXTERNAL

Client-side certificates should be placed in this directory
    for use by mechasqueak.

This directory will be excluded from git, and will **NOT** be copied
into the Docker image, instead it will be **mounted**

Your certificate can be a single file containing both the key and
the certeficate, or they can be as two seperate files.
In either case, you will need to set the `Authentication>EXTERNAL`
fields of the config file to point at your certificate and set
`authentication>method` to `"EXTERNAL"`.

a example configuration is provided below
```json
  "authentication": {
    "method":"EXTERNAL",
    "plain": {
      "username": "",
      "password": "",
      "SASL": true,
      "identity": ""
    },
    "external":{
      "tls_client_key":"mecha3.pem",
      "tls_client_cert":"mecha3.pem"
    }
  },
```