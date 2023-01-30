# API Server

Ralph comes with an API server that aims to implement the Learning Record Store
(LRS) specification (still a work in progress).

## Getting started

The API server supports the following authentication methods:

- Http Basic Authentication (default method)
- OpenID Connect authentication on top of OAuth2.0

### HTTP Basic Authentication

The default method for securing Ralph API server is with HTTP basic authentication.

The API server can be started up with the following command:

```bash
$ ralph runserver --backend es
```

The `--backend` (or `-b`) option specifies which database backend to use for
LRS data storage and retrieval. See Ralph's [backends
documentation](./backends.md) for more details.

However, before you can start your API server and make requests against it, you
need to set up your credentials.

#### Creating a credentials file

The credentials file is expected to be a valid JSON file. Its location is
specified by the `RALPH_AUTH_FILE` configuration value. By default, `ralph`
will look for the `auth.json` file in the application directory (see [click
documentation for
details](https://click.palletsprojects.com/en/8.1.x/api/#click.get_app_dir)).

The expected format is a list of entries (JSON objects) each containing the
username, the user's `bcrypt` hashed+salted password and scopes they can
access:

```json
[
  {
    "username": "john.doe@example.com",
    "hash": "$2b$12$yBXrzIuRIk6yaft5KUgVFOIPv0PskCCh9PXmF2t7pno.qUZ5LK0D2",
    "scopes": ["example_scope"]
  },
  {
    "username": "simon.says@example.com",
    "hash": "$2b$12$yBXrzIuRIk6yaft5KUgVFOIPv0PskCCh9PXmF2t7pno.qUZ5LK0D2",
    "scopes": ["second_scope", "third_scope"]
  }
]
```

To create a new user credentials, Ralph's CLI provides a dedicated command:

```bash
$ ralph auth \
    --username janedoe \
    --password supersecret \
    --scope janedoe_scope \
    -w
```

This command updates your credentials file with the new `janedoe` user.

> Note that running this command requires that you installed Ralph with the CLI
> optional dependencies, _e.g._ `pip install ralph-malph[cli]` (which we highly
> recommend).

#### Scopes

(Work In Progress)

#### Making a GET request

The first request that can be answered by the ralph API server is a `whoami` request, which checks if the user is authenticated and returns their username and permission scopes.

Use curl to get `http://localhost:8100/whoami`:

```bash
$ curl http://localhost:8100/whoami
< HTTP/1.1 401 Unauthorized
< {"error":"Not authenticated"}
```

Send your username and password to the API server through HTTP Basic Auth:

```bash
$ curl --user john.doe@example.com:PASSWORD http://localhost:8100/whoami
< HTTP/1.1 200 OK
< {"username":"john.doe@example.com","scopes":["authenticated","example_scope"]}
```

### OpenID Connect authentication

Ralph LRS API server supports OpenID Connect (OIDC) on top of OAuth 2.0 for authentication and authorization.

To enable OIDC auth, you should set the `RALPH_RUNSERVER_AUTH_BACKEND` environment variable as follows:
```bash
RALPH_RUNSERVER_AUTH_BACKEND=oidc
```
and you should define the `RALPH_RUNSERVER_AUTH_OIDC_ISSUER_URI` environment variable with your identity provider's Issuer Identifier URI as follows:
```bash
RALPH_RUNSERVER_AUTH_OIDC_ISSUER_URI=http://{provider_host}:{provider_port}/auth/realms/{realm_name}
```

This address must be accessible to the LRS on startup as it will perform OIDC Discovery to retrieve public keys and other information about the OIDC environment.

It is also strongly recommended that you set the optional `RALPH_RUNSERVER_AUTH_OIDC_AUDIENCE` environment variable to the origin address of the LRS itself (ex. "http://localhost:8100") to enable verification that a given token was issued specifically for the LRS.

#### Identity Providers

OIDC support is currently developed and tested against [Keycloak](https://www.keycloak.org/) but may work with other identity providers that implement the specification.

The [Learning analytics playground](https://github.com/openfun/learning-analytics-playground/) repository contains a Docker Compose file and configuration for a demo instance of Keycloak with a `ralph` client.

#### Scopes

(Work In Progress)

#### Making a GET request

The first request that can be answered by the ralph API server is a `whoami` request, which checks if the user is authenticated and returns their username and permission scopes.

Use curl to get `http://localhost:8100/whoami`:

```bash
$ curl http://localhost:8100/whoami
< HTTP/1.1" 401 Unauthorized
< {"detail":"Could not validate credentials"}
```
With the Keycloak instance running, use curl to get access token from Keycloak:
```bash
curl --request POST 'http://localhost:8080/auth/realms/fun-mooc/protocol/openid-connect/token' \
--header 'Content-Type: application/x-www-form-urlencoded' \
--data-urlencode 'client_id=ralph' \
--data-urlencode 'client_secret=super-secret' \
--data-urlencode 'username=ralph_admin' \
--data-urlencode 'password=funfunfun' \
--data-urlencode 'grant_type=password'
```

which outputs (tokens truncated for example purpose):

```json
{ 
  "access_token":"eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJSTWlLM",
  "expires_in":300,
  "refresh_expires_in":1800,
  "refresh_token":"eyJhbGciOiJIUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICI4MDc5NjExM",
  "token_type":"Bearer",
  "not-before-policy":0,
  "session_state":"22a36735-e35f-496b-a243-152d32ebff45",
  "scope":"profile email"
}
```

Send the access token to the API server as a Bearer header:

```bash
$ curl http://localhost:8100/whoami --header "Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJSTWlLM"
< HTTP/1.1 200 OK
< {"username":"ralph_admin","scopes":["all"]}
```

## Forwarding statements

Ralph's API server can be configured to forward xAPI statements it receives to other
LRSes.

To configure statement forwarding, you need to create a `.env` file in the current
directory and define the `RALPH_XAPI_FORWARDINGS` variable or define the
`RALPH_XAPI_FORWARDINGS` environment variable.

The value of the `RALPH_XAPI_FORWARDINGS` variable should be a JSON encoded list of
dictionaries where each dictionary defines a forwarding configuration and consists of
the following key/value pairs:

| key              | value type | description                                                                   |
|:-----------------|:-----------|:------------------------------------------------------------------------------|
| `is_active`      | `boolean`  | Specifies whether or not this forwarding configuration should take effect.    |
| `url`            | `URL`      | Specifies the endpoint URL where forwarded statements should be send.         |
| `basic_username` | `string`   | Specifies the basic auth username.                                            |
| `basic_password` | `string`   | Specifies the basic auth password.                                            |
| `max_retries`    | `number`   | Specifies the number of times a failed forwarding request should be retried.  |
| `timeout`        | `number`   | Specifies the duration in seconds of network inactivity leading to a timeout. |

> Note that for a forwarding configuration to be valid it is required that all key/value
> pairs are defined.

Example of a valid forwarding configuration:

```bash
RALPH_XAPI_FORWARDINGS='
[
  {
    "is_active": true,
    "url": "http://lrs1.example.com/xAPI/statements/",
    "basic_username": "admin1@example.com",
    "basic_password": "PASSWORD1",
    "max_retries": 1,
    "timeout": 5
  },
  {
    "is_active": true,
    "url": "http://lrs2.example.com/xAPI/statements/",
    "basic_username": "admin2@example.com",
    "basic_password": "PASSWORD2",
    "max_retries": 5,
    "timeout": 0.2
  }
]
'
```
