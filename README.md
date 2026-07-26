# flyswatter

<p align="center"><img src="./.screens/swatter.gif" alt="flyswatter" width="480"></p>

Skids, scanners, and AI crawlers are internet gnats. **flyswatter** is a drop-in nginx trap that catches them on every domain you host.

Two traps, both reply **`200 OK`** (never a block code, so they can't tell they've been caught):

1. **Bot / scraper / AI-crawler user-agents** get a dynamic mocking page instead of your site.
2. **Scanner paths** (`.env`, `.git/config`, AWS creds, SSH keys, SQL dumps, ...) get believable, bogus, insulting, ever-changing fake secrets.

Everything is generated fresh per request — no two responses are the same.

## Fake endpoints

Any request to these paths gets a plausible-but-bogus dynamic file. Fake keys embed `FUCKYOU` / `madeulook`, IPs come from DoD `/8` ranges, hostnames and passwords are random:

| Path | Fake content |
|------|--------------|
| `/.env`, `/.env.*` | full dotenv: DB, Redis, Mongo, AWS, DO, Cloudflare, Stripe, GitHub, Slack, SendGrid, Twilio, JWT — plus a huge **LLM/AI stack** (OpenAI, Anthropic, Ollama, Groq, Mistral, Cohere, HuggingFace, Replicate, Together, Perplexity, OpenRouter, DeepSeek, Gemini, Azure OpenAI, LangChain/LangSmith, Pinecone, Weaviate, Qdrant, Chroma) |
| `/.git/config`, `/.git/HEAD` | git config with an embedded creds URL |
| `/.git-credentials` | github / gitlab / bitbucket creds |
| `/.aws/credentials` | AWS ini (default / prod profiles) |
| `/.ssh/id_rsa`, `/id_rsa`, `/id_ed25519` | fake OpenSSH private key |
| `/wp-config.php` | WordPress DB creds + auth salts |
| `/config.json` | app config with nested creds |
| `/secrets.json`, `/credentials.json` | JSON secret bundle |
| `/.vscode/sftp.json` | SFTP host / user / password |
| `/docker-compose.yml` | compose file with env secrets |
| `/.npmrc` | npm registry auth tokens |
| `/.pypirc` | PyPI upload tokens |
| `/.netrc` | machine / login / password |
| `/.htpasswd`, `/.htaccess` | htpasswd hashes |
| `/backup.sql`, `/dump.sql`, `/database.sql`, `/db.sql` | SQL dump with fake `users` + password hashes |

## Bot user-agents

A dynamic mocking HTML page (with a hidden garbage payload to poison scrapes) and a pile of obnoxious headers: `X-Fuck-Scrapers`, `X-Do-Not-Train: 1`, `X-Robots-Tag: noai, noimageai`, `X-Training-Data: poisoned`, and more.

## Extra nastiness (random)

- **1 in 5** `.env` hits are **log-bombed** — the whole file repeated 5000× (~19 MB), gzipped so it's tiny for you and huge in their logs/parser.
- **1 in 5** hits get an invalid **UTF-16-LE** tail that crashes naive UTF-8 decoders (the classic "my bot ate a weird-encoded message and died").
- Fake IPs come only from DoD `/8` ranges, so the "infra" looks exotic.

## Why it's safe

- The non-`.env`/`.git` paths are **root-anchored** (`^/...`), so files served *inside* git repos (gitea, gitweb, ...) are never shadowed.
- If a real `.env` or `.git` sits in a webroot, flyswatter **shadows** it — scanners get the fake, never the real file.
- If the trap container is down, those paths return `502` — nginx never falls through to the real file.

## Install

Requires **docker** + **nginx**.

```sh
git clone https://github.com/YOU/flyswatter && cd flyswatter
sudo ./setup.sh
```

`setup.sh` builds and starts the trap container (localhost only) and installs the nginx map + snippet. Then add **two lines** to every `server { }` block you want protected:

```nginx
if ($block_ua) { return 461; }     # bot/AI user-agents -> troll page
include snippets/flyswatter.conf;     # trap routing + fake-secret endpoints
```

Reload:

```sh
sudo nginx -t && sudo systemctl reload nginx
```

See `nginx/EXAMPLE-site.conf` for a full example server block.

## Config

- `FLYSWATTER_PORT` — host port for the trap container (default `8899`).

## Tuning

- Edit the user-agent list in `nginx/conf.d/block-bots.conf`.
- To stop logging trapped traffic, append `if=$loggable` to your `access_log` directive.

## Files

```
app.py                     the trap server (Flask)
Dockerfile                 builds the container
setup.sh                   build + run + install nginx config
nginx/conf.d/block-bots.conf   $block_ua + $loggable maps
nginx/snippets/flyswatter.conf    trap routing (drop-in include)
nginx/EXAMPLE-site.conf        example protected server block
```

---

###### Mirrors: [SuperNETs](https://git.supernets.org/acidvegas/) • [GitHub](https://github.com/acidvegas/) • [GitLab](https://gitlab.com/acidvegas/) • [Codeberg](https://codeberg.org/acidvegas/)
