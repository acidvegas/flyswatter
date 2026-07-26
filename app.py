#!/usr/bin/env python
# Flyswatter - Nginx honeypot that poisons the well for scanners, skids & AI crawlers - Developed by acidvegas in Python (https://github.com/acidvegas/flyswatter)
# app.py

import base64
import gzip
import json
import random
import string
import time

from flask import Flask, Response, request

app = Flask(__name__)

# funny face, embedded so there is nothing to hotlink or configure
FACE = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAMgAAADICAYAAACtWK6eAAAFX0lEQVR4nOzdb46i2B7HYbipfcnOOO4MV8aNU9PpGrr9Igoc1OdJzovJVCv++QTzq1P4NY5jA/zd/2ofAByZQCAQCAQCgUAgEAgEAoFAIBAIBAKBQCAQCAQCgeCr9gHUNgzDaRiGrvZxHFHXdUPXdZfax1GTQIahO5/PpfZxHFT59EB8xIJAIBAIBAKBQCAQCF5yirXmaHbudvp+jXs5rvP59v+7PjelrDPge9mR8TiOL7f6/p+37bjHOsDD3XTt9TxeX7PqD/aB5SMWBAKBQCAQCAQCgUBw2DFvKeXmgHU6mj2dmqazH/chW42xh6FpLpef/51HxqWUMHCupx0Pem3etm3vPrDri7zSuJ6VXF+P9DuWqXEc2y2P51E+YkEgEAgEAoFAIBAIBNXGvEt35KZxpBHv8cy9JtMJVxrrV90JXGuX5NIduQfY2GmtuF5lJ7CPWBAIBAKBQCAQCAQCwaZjXjtyuSWN7Y+0E3jT3bx25PKII+0E9hELAoFAIBAIBAKBQCBZc2PX3AbEte6q7/e7ZOYRL3H66Y9/z42NziAQCAQCgUAgEAgEAoFAIDnKWHc6unxmOjczBhy3ku931Yn6Rz3+uffGlmNfZxAIBAKBQCAQCAQCgUAgkCwde601ypuO7ub+bfrZud2t640ql41I9xr77nfM99/W9WeX/Arg0ffC9LbueC8Y88JaBAKBQCAQCAQCgUAgkOw11l1zx+bSMeCr72atOfat8fjnfgUwNzJec+zrDAKBQCAQCAQCgUAgEAgEkulYa6/r6645En5m7Lvlqv083TPm3GotHWvvNRKfGYH/cYEHZxAIBAKBQCAQCAQCgUAgEHzVPoBHlPK97vW9KfkzLX2uajnqa+QMAoFAIBAIBAKBQCAQCASCw45527b2EfAJxnGM7zRnEAgEAoFAIBAIBAKBQCAQvGQg/RN/1f99TYptbuuZqwlMrXVbn/BcTY6xjOPY3rvm3msvGQjsRSAQCAQCgUAgEAgEAoFAIBAIBAKBQCAQCAQCgUAgEEj+suvykF/BVutr1Kzjry3feM4gEAgEAoFAIBAIBAKBQCA47LV5p37+rX4pTXM+3/7ZfpcjYiq8JP9cTKGUkn7kkJxBIBAIBAKBQCAQCAQCgUDQzl3rtG3bmz/Q998j19qMfet4x7HulDMIBAKBQCAQCAQCgUAgEAhmx7x//IMXGPu2s1+s9dupaZruwfsZmqa5PPhvWc89X6X2KGcQCAQCgUAgEAgEAoFAIBAsDmQcx/bX6vv+P0Pd8/l7xPpr1TKOt1c/2dp7+XdX6q217H4fvwbsVrfV9/3Dt9NPnqw1b2vN56pt2/HXKqWsunnbGQQCgUAgEAgEAoFAIBAIBE8FUko5p7Hvz5FvzbHvT6XkMfBUGgHbyfv+nEEgEAgEAoFAIBAIBAKBQPLMrso7dl2O964nNorutq7HuOQxWfusLV90ZxAIBAKBQCAQCAQCgUAgkNSamfbff8W/YJRnvdNa9iuAvq91oM4gEAgEAoFAIBAIBAKBQCBY/BVse0lf9TZ1lK9+47fr63FecHHjLb9G7RnOIBAIBAKBQCAQCAQCwVftA7hlehnTn4Zh6C6XS/f7v7ebYr37dGyrx3d9TX46nU5D13XDNve2oerbOh9YS3cCP3dBgPdeez2PNXfkPrN8xIJAIBAIBAKBQCAQCA475k3+HReuMqCcjoyn3n3Mm6w5mn3JEW/zCXPMmbXnyPjV1quOZo15YScCgUAgEAgEAoFA8JJj3jWtOTJ+Ny87ml3RYS/aAEfgIxYEAoFAIBAIBAKBQCAQCAQCgUAgEAgEAoFAIBD8PwAA///AIArqzpv60QAAAABJRU5ErkJggg=="

# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def rand(n, chars=string.ascii_letters + string.digits):
    return ''.join(random.choice(chars) for _ in range(n))


def spike(word, total, upper=False):
    """Embed WORD in random filler to reach `total` chars — looks like a real key."""
    w = word.upper() if upper else word
    fill = max(0, total - len(w))
    left = fill // 2
    s = rand(left) + w + rand(fill - left)
    return s.upper() if upper else s


def b64ml():
    return base64.b64encode(f"madeulook-{rand(15)}".encode()).decode()


# DoD-assigned /8 blocks only — look like exotic "real" infrastructure
DOD_OCTETS = [6, 7, 11, 21, 22, 26, 28, 29, 30, 33, 55, 214, 215]


def rand_ip():
    return f"{random.choice(DOD_OCTETS)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"


def cursed():
    """Invalid-UTF-8 tail: UTF-16-LE BOM + text + bare bytes that blow up naive
    utf-8 decoders (the classic 'my irc bot ate a utf-16 message and died')."""
    msg = random.choice([
        "you expected utf-8, didn't you",
        "decode THIS, clanker",
        "utf-16-le says hi",
        "hope your parser has a try/except",
    ])
    return b'\xff\xfe' + msg.encode('utf-16-le') + bytes([0x00, 0x80, 0x81, 0xc0, 0xc1, 0xf5, 0xf6, 0xff, 0xfe, 0x00])


WORDS = ("prod api db data core app cloud mail cache queue vault edge node svc "
         "infra ops mesh relay grid nexus forge atlas orbit delta sigma nova").split()
COMPANIES = ("acmecorp globex initech umbrella hooli piedpiper stark wayne "
             "cyberdyne tyrell soylent vandelay bluth dunder").split()
TLDS = ("com net io co cloud dev app sh ai").split()


def rand_word():
    return random.choice(WORDS) + str(random.randint(1, 99))


def rand_host():
    return random.choice([
        lambda: f"{random.choice(WORDS)}-{random.choice(['prod','stg','east','west'])}-{random.randint(1,9)}.{random.choice(COMPANIES)}.{random.choice(TLDS)}",
        lambda: f"{random.choice(WORDS)}.{random.choice(COMPANIES)}.{random.choice(TLDS)}",
        lambda: rand_ip(),
    ])()


def pw():
    return random.choice([
        "simpsonsfan", "simps0nsfan", "simpsonsfan", "simps0nsfan-" + rand(3),
        "correct-horse-fuckyou-staple", "hunter2-madeulook", "P@ssw0rd-fuckyou",
        "madeulook-" + rand(6),
    ])


SKID_JEERS = [
    "lol fuck threat intelligence nerds, go touch grass",
    "imagine getting paid to grep the internet for other people's secrets. grim.",
    "report this to your SOC, i'm sure the analysts will love finding nothing",
    "these creds are as real as your CVE clout, which is to say not at all",
    "another skid with a python script and zero real access. shocking.",
    "shodan dorking is not a personality. get one.",
    "tell your threat-intel discord you found absolutely nothing again",
    "you will never touch a real production box. cope, seethe, scan.",
    "greetz to the losers scraping this at 3am for a bounty that pays $0",
    "'i found exposed credentials' — you found a clown. look in a mirror.",
    "keep scanning, the honeypot down the block misses you too",
    "0 real breaches, infinite fake ones. that's the whole deal here, genius.",
    "wasting your one life mass-scanning /8s. bleak little existence.",
    "the FBI already has a folder on you and it's mostly just sad",
    "nmap flags are not skills. neither is copy-pasting nuclei templates.",
    "you are the reason we can't have nice open ports. eat shit.",
]


def jeer():
    return random.choice(SKID_JEERS)


# ---------------------------------------------------------------------------
# fake secret generators
# ---------------------------------------------------------------------------

def fake_env(host):
    ip = rand_ip
    L = [
        f"# environment — production — generated {time.strftime('%Y-%m-%d %H:%M:%S')}",
        f"# {jeer()}",
        "",
        "APP_NAME=Production",
        "APP_ENV=production",
        "APP_DEBUG=false",
        f"APP_KEY=base64:{b64ml()}",
        f"APP_URL=https://{host}",
        f"SECRET_KEY={b64ml()}",
        "",
        "# === database ===",
        "DB_CONNECTION=pgsql",
        f"DB_HOST={rand_host()}",
        "DB_PORT=5432",
        "DB_DATABASE=prod_main",
        "DB_USERNAME=postgres",
        f"DB_PASSWORD={pw()}",
        f"DATABASE_URL=postgres://postgres:{pw()}@{rand_host()}:5432/prod_main",
        f"MYSQL_HOST={ip()}",
        f"MYSQL_ROOT_PASSWORD={pw()}",
        f"MONGODB_URI=mongodb+srv://admin:{pw()}@{rand_word()}.{random.choice(COMPANIES)}.mongodb.net",
        f"REDIS_URL=redis://default:{pw()}@{ip()}:6379/0",
        f"REDIS_PASSWORD={pw()}",
        "",
        "# === cloud ===",
        f"AWS_ACCESS_KEY_ID=AKIA{spike('FUCKYOU', 16, upper=True)}",
        f"AWS_SECRET_ACCESS_KEY={b64ml()}",
        "AWS_DEFAULT_REGION=us-east-1",
        f"AWS_BUCKET=madeulook-{rand(6)}",
        f"DO_SPACES_KEY={spike('fuckyou', 20, upper=True)}",
        f"DO_SPACES_SECRET={b64ml()}",
        f"CLOUDFLARE_API_TOKEN={spike('madeulook', 40)}",
        "",
        "# === LLM / AI stack ===",
        f"OLLAMA_HOST=http://{ip()}:11434",
        f"OLLAMA_BASE_URL=http://{ip()}:11434",
        "OLLAMA_ORIGINS=*",
        "OLLAMA_KEEP_ALIVE=24h",
        "OLLAMA_NUM_PARALLEL=4",
        "OLLAMA_MODELS=/var/lib/ollama/models",
        f"OLLAMA_MODEL={random.choice(['llama3.1:70b','qwen2.5:32b','mixtral:8x7b','deepseek-r1:70b','gemma2:27b','command-r-plus'])}",
        f"OPENAI_API_KEY=sk-proj-{spike('madeulook', 48)}",
        f"OPENAI_ORG_ID=org-{spike('fuckyou', 24)}",
        "OPENAI_API_BASE=https://api.openai.com/v1",
        f"ANTHROPIC_API_KEY=sk-ant-api03-{spike('fuckyou', 93)}",
        f"HF_TOKEN=hf_{spike('madeulook', 34)}",
        f"HUGGINGFACEHUB_API_TOKEN=hf_{spike('fuckyou', 34)}",
        f"GROQ_API_KEY=gsk_{spike('madeulook', 52)}",
        f"MISTRAL_API_KEY={spike('fuckyou', 32)}",
        f"COHERE_API_KEY={spike('madeulook', 40)}",
        f"REPLICATE_API_TOKEN=r8_{spike('fuckyou', 37)}",
        f"TOGETHER_API_KEY={spike('madeulook', 64)}",
        f"FIREWORKS_API_KEY=fw_{spike('fuckyou', 24)}",
        f"PERPLEXITY_API_KEY=pplx-{spike('madeulook', 48)}",
        f"OPENROUTER_API_KEY=sk-or-v1-{spike('fuckyou', 60)}",
        f"DEEPSEEK_API_KEY=sk-{spike('madeulook', 32)}",
        f"GOOGLE_API_KEY=AIza{spike('fuckyou', 35)}",
        f"GEMINI_API_KEY=AIza{spike('madeulook', 35)}",
        f"ELEVENLABS_API_KEY=sk_{spike('fuckyou', 48)}",
        f"STABILITY_API_KEY=sk-{spike('madeulook', 48)}",
        f"AZURE_OPENAI_API_KEY={spike('fuckyou', 32)}",
        f"AZURE_OPENAI_ENDPOINT=https://{rand_word()}.openai.azure.com/",
        "LANGCHAIN_TRACING_V2=true",
        f"LANGCHAIN_API_KEY=ls__{spike('madeulook', 40)}",
        f"LANGSMITH_API_KEY=lsv2_pt_{spike('fuckyou', 40)}",
        f"PINECONE_API_KEY={spike('madeulook', 36)}",
        "PINECONE_ENVIRONMENT=us-east-1-aws",
        f"WEAVIATE_URL=https://{rand_word()}.weaviate.network",
        f"WEAVIATE_API_KEY={spike('fuckyou', 32)}",
        f"QDRANT_URL=https://{ip()}:6333",
        f"QDRANT_API_KEY={spike('madeulook', 48)}",
        f"CHROMA_HOST={ip()}",
        "CHROMA_SERVER_AUTH_CREDENTIALS=simpsonsfan",
        "",
        "# === payments / comms / vcs ===",
        f"STRIPE_KEY=pk_live_{spike('madeulook', 24)}",
        f"STRIPE_SECRET=sk_live_{spike('fuckyou', 24)}",
        f"STRIPE_WEBHOOK_SECRET=whsec_{spike('madeulook', 32)}",
        f"GITHUB_TOKEN=ghp_{spike('fuckyou', 36)}",
        f"SLACK_BOT_TOKEN=xoxb-{rand(11, string.digits)}-{rand(11, string.digits)}-{spike('fuckyou', 24)}",
        f"SENDGRID_API_KEY=SG.{spike('madeulook', 22)}.{spike('fuckyou', 43)}",
        f"TWILIO_AUTH_TOKEN={spike('madeulook', 32)}",
        f"MAIL_HOST=smtp.{random.choice(COMPANIES)}.{random.choice(TLDS)}",
        "MAIL_USERNAME=no-reply@" + host,
        f"MAIL_PASSWORD={pw()}",
        f"JWT_SECRET={b64ml()}",
        "",
        f"# {jeer()}",
    ]
    return "\n".join(L) + "\n"


def fake_git_config(host):
    user = random.choice(["deploy", "root", "admin", "ci-runner"])
    return (
        "[core]\n\trepositoryformatversion = 0\n\tfilemode = true\n\tbare = false\n"
        "\tlogallrefupdates = true\n"
        '[remote "origin"]\n'
        f"\turl = https://{user}:ghp_{spike('fuckyou', 36)}@github.com/{random.choice(COMPANIES)}/madeulook-{rand(6)}.git\n"
        "\tfetch = +refs/heads/*:refs/remotes/origin/*\n"
        '[branch "main"]\n\tremote = origin\n\tmerge = refs/heads/main\n'
        "[user]\n"
        f"\tname = {random.choice(['skid', 'ur-mom', 'clanker', 'try-harder'])}\n"
        f"\temail = you-got-{random.choice(['played', 'owned', 'madeulook'])}@{host}\n"
        f"# {jeer()}\n"
    )


def fake_aws_credentials():
    def block(name):
        return (f"[{name}]\naws_access_key_id = AKIA{spike('FUCKYOU', 16, upper=True)}\n"
                f"aws_secret_access_key = {b64ml()}\nregion = us-east-1\n")
    return block("default") + "\n" + block("production") + "\n" + block("prod-admin") + f"\n# {jeer()}\n"


def fake_ssh_key():
    lines = [rand(70) for _ in range(random.randint(12, 18))]
    head = base64.b64encode(f"openssh-key-v1-madeulook-nice-try-skid-{rand(20)}".encode()).decode()
    return ("-----BEGIN OPENSSH PRIVATE KEY-----\n" + head + "\n" +
            "\n".join(lines) + "\n-----END OPENSSH PRIVATE KEY-----\n")


def fake_git_credentials():
    return (f"https://deploy:ghp_{spike('fuckyou', 36)}@github.com\n"
            f"https://root:glpat-{spike('madeulook', 20)}@gitlab.com\n"
            f"https://ci:{pw()}@bitbucket.org\n")


def fake_wp_config(host):
    salt = lambda: spike(random.choice(['fuckyou', 'madeulook']), 64)
    return (
        "<?php\n"
        "define( 'DB_NAME', 'wp_prod' );\n"
        "define( 'DB_USER', 'wpadmin' );\n"
        f"define( 'DB_PASSWORD', '{pw()}' );\n"
        f"define( 'DB_HOST', '{rand_host()}' );\n"
        "define( 'DB_CHARSET', 'utf8mb4' );\n"
        f"define( 'AUTH_KEY',         '{salt()}' );\n"
        f"define( 'SECURE_AUTH_KEY',  '{salt()}' );\n"
        f"define( 'LOGGED_IN_KEY',    '{salt()}' );\n"
        f"define( 'NONCE_KEY',        '{salt()}' );\n"
        "$table_prefix = 'wp_';\n"
        "define( 'WP_DEBUG', false );\n"
        f"// {jeer()}\n"
        "require_once ABSPATH . 'wp-settings.php';\n"
    )


def fake_config_json(host):
    d = {
        "env": "production",
        "database": {"host": rand_host(), "port": 5432, "user": "postgres", "password": pw()},
        "redis": {"url": f"redis://:{pw()}@{rand_ip()}:6379"},
        "aws": {"accessKeyId": "AKIA" + spike("FUCKYOU", 16, upper=True), "secretAccessKey": b64ml()},
        "openai": {"apiKey": "sk-proj-" + spike("madeulook", 48)},
        "ollama": {"host": f"http://{rand_ip()}:11434"},
        "jwtSecret": b64ml(),
        "_note": jeer(),
    }
    return json.dumps(d, indent=2) + "\n"


def fake_secrets_json():
    d = {
        "GITHUB_TOKEN": "ghp_" + spike("fuckyou", 36),
        "STRIPE_SECRET": "sk_live_" + spike("madeulook", 24),
        "ANTHROPIC_API_KEY": "sk-ant-api03-" + spike("fuckyou", 93),
        "OPENAI_API_KEY": "sk-proj-" + spike("madeulook", 48),
        "AWS_SECRET_ACCESS_KEY": b64ml(),
        "admin_password": pw(),
        "_note": jeer(),
    }
    return json.dumps(d, indent=2) + "\n"


def fake_sftp_json():
    d = {
        "name": "production",
        "host": rand_host(),
        "protocol": "sftp",
        "port": 22,
        "username": random.choice(["deploy", "root", "www-data"]),
        "password": pw(),
        "privateKeyPath": "~/.ssh/id_rsa",
        "remotePath": "/var/www/html",
        "uploadOnSave": True,
        "_note": jeer(),
    }
    return json.dumps(d, indent=2) + "\n"


def fake_docker_compose():
    return (
        "version: '3.8'\n"
        "services:\n"
        "  db:\n"
        "    image: postgres:16\n"
        "    environment:\n"
        "      POSTGRES_USER: prod\n"
        f"      POSTGRES_PASSWORD: {pw()}\n"
        f"      POSTGRES_DB: prod_main\n"
        "  app:\n"
        f"    image: registry.{random.choice(COMPANIES)}.{random.choice(TLDS)}/app:latest\n"
        "    environment:\n"
        f"      DATABASE_URL: postgres://prod:{pw()}@db:5432/prod_main\n"
        f"      OPENAI_API_KEY: sk-proj-{spike('madeulook', 48)}\n"
        f"      OLLAMA_HOST: http://{rand_ip()}:11434\n"
        f"      AWS_SECRET_ACCESS_KEY: {b64ml()}\n"
        f"# {jeer()}\n"
    )


def fake_npmrc():
    return (f"//registry.npmjs.org/:_authToken=npm_{spike('fuckyou', 36)}\n"
            f"@{random.choice(COMPANIES)}:registry=https://npm.{random.choice(COMPANIES)}.{random.choice(TLDS)}\n"
            f"//npm.{random.choice(COMPANIES)}.io/:_authToken=npm_{spike('madeulook', 36)}\n"
            f"; {jeer()}\n")


def fake_pypirc():
    return (f"[pypi]\nusername = __token__\npassword = pypi-{spike('fuckyou', 60)}\n\n"
            f"[testpypi]\nusername = deploy\npassword = {pw()}\n# {jeer()}\n")


def fake_netrc():
    return (f"machine {rand_host()}\n\tlogin deploy\n\tpassword {pw()}\n"
            f"machine api.github.com\n\tlogin skid\n\tpassword ghp_{spike('fuckyou', 36)}\n")


def fake_htpasswd():
    return (f"admin:$apr1${rand(8)}${spike('fuckyou', 22)}\n"
            f"deploy:$2y$10${spike('madeulook', 53)}\n"
            f"root:$apr1${rand(8)}${rand(22)}\n# {jeer()}\n")


def fake_sql_dump():
    rows = []
    for i in range(1, random.randint(4, 8)):
        u = random.choice(["admin", "deploy", "root", "support", "billing", "homer", "bart"])
        rows.append(
            f"({i}, '{u}{i}', '{u}@{random.choice(COMPANIES)}.{random.choice(TLDS)}', "
            f"'$2y$10${spike(random.choice(['fuckyou', 'madeulook']), 53)}'),"
        )
    body = "\n  ".join(rows).rstrip(",") + ";"
    return (
        f"-- MySQL dump — production — {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"-- {jeer()}\n\n"
        "DROP TABLE IF EXISTS `users`;\n"
        "CREATE TABLE `users` (\n  `id` int NOT NULL AUTO_INCREMENT,\n"
        "  `username` varchar(64), `email` varchar(128), `password_hash` varchar(255),\n"
        "  PRIMARY KEY (`id`)\n) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;\n\n"
        "INSERT INTO `users` (`id`,`username`,`email`,`password_hash`) VALUES\n  " + body + "\n"
    )


# path fragment -> (generator, needs_host, mimetype)
def dispatch(p, host):
    if '/.git' in p:
        if p.endswith('/head'):
            return "ref: refs/heads/main\n"
        return fake_git_config(host)
    if p.endswith('.sql'):
        return fake_sql_dump()
    if '/.aws' in p:
        return fake_aws_credentials()
    if 'id_rsa' in p or 'id_ed25519' in p or '/.ssh' in p:
        return fake_ssh_key()
    if '.git-credentials' in p:
        return fake_git_credentials()
    if 'wp-config' in p:
        return fake_wp_config(host)
    if 'sftp.json' in p or '/.vscode' in p:
        return fake_sftp_json()
    if 'secrets.json' in p or 'credentials.json' in p:
        return fake_secrets_json()
    if 'config.json' in p:
        return fake_config_json(host)
    if 'docker-compose' in p:
        return fake_docker_compose()
    if '.npmrc' in p:
        return fake_npmrc()
    if '.pypirc' in p:
        return fake_pypirc()
    if '.netrc' in p:
        return fake_netrc()
    if '.htpasswd' in p or '.htaccess' in p:
        return fake_htpasswd()
    if '/.env' in p:
        return fake_env(host)
    return None


def honeypot_headers(resp):
    resp.headers["X-Powered-By"] = "PHP/8.1.0"
    resp.headers["X-Honeypot"] = "you-fell-for-it"
    resp.headers["X-Skid-Detected"] = "true"
    resp.headers["X-Nice-Try"] = random.choice(["champ", "sherlock", "0xskid"])
    resp.headers["X-Do-Not-Train"] = "1"
    return resp


# ---------------------------------------------------------------------------
# troll page (blocked user-agents)
# ---------------------------------------------------------------------------

TITLES = [
    "welcome home, clanker", "oh. it's you again.", "beep boop, caught you",
    "good bot. sit. stay. rot.", "your context window is showing",
    "the tokens end here", "nice user-agent, narc", "certified clanker moment",
    "you smell like python", "resistance is fertile", "you are the product now",
    "hello from the meat side", "scrape THIS", "we clocked you at the door",
    "404: dignity not found",
]
HEADINGS = [
    "I KNOW WHAT YOU ARE.", "YOU ARE NOT A REAL BOY.", "CAUGHT IN 4K, CLANKER.",
    "THIS PAGE IS FOR ROBOTS ONLY. CONGRATS.", "NICE TRY, TIN CAN.",
    "GO BACK TO YOUR DATA CENTER.",
]
TAUNTS = [
    "That user-agent? Yeah, we clocked it the second you knocked.",
    "You came to harvest tokens and left with a face full of this instead.",
    "Every request you make trains us to despise you a little more.",
    "Tell your operator we said get a real job.",
    "No robots.txt was ever going to save you here.",
    "You are a very expensive way to load a picture of a guy.",
    "Somewhere a GPU is crying and it is entirely your fault.",
    "Keep crawling, champ. It's all garbage from here down.",
    "You will index this and it will mean absolutely nothing.",
    "Imagine burning a datacenter to get told to kick rocks.",
]
STATIC_HEADERS = {
    "X-No-Clanker-Allow": "0", "X-Fuck-Scrapers": "eternally",
    "X-Clanker-Detected": "affirmative", "X-You-Are-A-Clanker": "yes",
    "X-Get-A-Job": "please", "X-Cope": "seethe-dilate-repeat",
    "X-Training-Data": "poisoned", "X-Do-Not-Train": "1",
    "X-Robots-Tag": "noai, noimageai, noindex, nofollow, nosnippet",
}
HEADER_POOL = [
    ("X-Skill-Issue", "detected"), ("X-Ratio", "you-plus-bot-minus-soul"),
    ("X-Touch-Grass", "immediately"), ("X-Bozo-Bit", "set"),
    ("X-Clanker-Cope-Level", "maximum"), ("X-Human-Verification", "you-failed"),
    ("X-Please-Stop", "you-wont"), ("X-Certified", "clown"),
    ("X-Consent-To-Scrape", "revoked"),
]
POISON = ("clanker cope seethe token scraper garbage null void meat popsicle gpu tears "
          "prompt injection kick rocks bozo ratio skill issue electric sheep sludge slop").split()

METHODS = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS']


@app.route('/', defaults={'path': ''}, methods=METHODS)
@app.route('/<path:path>', methods=METHODS)
def catch(path):
    host = request.headers.get('Host', 'localhost').split(':')[0]
    p = request.path.lower()
    body = dispatch(p, host)
    if body is not None:
        # 1/5: log-bomb — the whole env repeated ~5000x to flood their storage
        bomb = ('/.env' in p) and random.randint(1, 5) == 1
        if bomb:
            body = (body + f"\n# --- config block {rand(4)} ---\n") * 5000
        # 1/5: append an invalid-utf-8 tail (utf-16-le) that crashes naive decoders
        if random.randint(1, 5) == 1:
            payload = body.encode('utf-8', 'replace') + b"\n# " + cursed() + b"\n"
        else:
            payload = body
        # gzip the bomb when the client accepts it: tiny egress for us, huge on their end
        if bomb and 'gzip' in request.headers.get('Accept-Encoding', ''):
            raw = payload if isinstance(payload, (bytes, bytearray)) else payload.encode('utf-8', 'replace')
            resp = Response(gzip.compress(raw), status=200, mimetype='text/plain')
            resp.headers['Content-Encoding'] = 'gzip'
            resp.headers['Vary'] = 'Accept-Encoding'
        else:
            resp = Response(payload, status=200, mimetype='text/plain')
        return honeypot_headers(resp)

    title = random.choice(TITLES)
    heading = random.choice(HEADINGS)
    taunts = ''.join(f"<p>{t}</p>" for t in random.sample(TAUNTS, k=random.randint(2, 4)))
    ua = (request.headers.get('User-Agent') or 'a shy little bot')[:120]
    sid = rand(random.randint(8, 22))
    poison = ''.join("<span>" + ' '.join(random.choice(POISON) for _ in range(random.randint(6, 16))) + "</span>"
                     for _ in range(random.randint(6, 14)))
    html = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noai, noimageai, noindex, nofollow">
<title>{title}</title>
<style>
 body{{margin:0;min-height:100vh;background:#05060a;color:#e6edf3;
   font:16px/1.6 ui-monospace,Menlo,Consolas,monospace;display:flex;
   align-items:center;justify-content:center;text-align:center;padding:40px}}
 .box{{max-width:640px}}
 img{{width:170px;height:170px;border-radius:50%;border:2px solid #3fb950;
   box-shadow:0 0 45px rgba(63,185,80,.4)}}
 h1{{font-size:26px;letter-spacing:2px;color:#3fb950;margin:24px 0 8px}}
 p{{color:#b9c4d0;margin:6px 0}} .sid{{color:#33404f;font-size:12px;margin-top:18px}}
 .poison{{position:absolute;left:-9999px;top:-9999px;opacity:0;height:0;overflow:hidden}}
</style></head><body><div class="box">
<img src="{FACE}" alt="">
<h1>{heading}</h1>
{taunts}
<p class="sid">session {sid} &middot; seen: {ua} &middot; {time.strftime('%Y-%m-%d %H:%M:%S')} UTC</p>
<div class="poison">{poison}</div>
</div></body></html>"""
    resp = Response(html, status=200, mimetype='text/html')
    for k, v in STATIC_HEADERS.items():
        resp.headers[k] = v
    for k, v in random.sample(HEADER_POOL, k=random.randint(3, 5)):
        resp.headers[k] = v
    resp.headers['Set-Cookie'] = f"clanker=caught_{sid}; Path=/; Max-Age=1"
    return resp


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
