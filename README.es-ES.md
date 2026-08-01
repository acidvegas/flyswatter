

# flyswatter

<p align="center"><img src="./.screens/swatter.gif" alt="flyswatter" width="480"></p>

Los skids, scanners y rastreadores de IA son mosquitos de internet. **flyswatter** es una trampa de integración directa para nginx que los atrapa en cada dominio que alojas.

Dos trampas, ambas responden con **`200 OK`** (nunca con un código de bloqueo, para que no puedan saber que han sido atrapados):

1. Los **user-agents de bots / scrapers / rastreadores de IA** reciben una página de burla dinámica en lugar de tu sitio.
2. Las **rutas de escaneo** (`.env`, `.git/config`, credenciales de AWS, claves SSH, volcados SQL, ...) reciben secretos falsos creíbles, ficticios, insultantes y en constante cambio.

Todo se genera desde cero por solicitud: no hay dos respuestas iguales.

## Endpoints falsos

Cualquier solicitud a estas rutas recibe un archivo dinámico plausible pero ficticio. Las claves falsas incluyen `FUCKYOU` / `madeulook`, las IPs provienen de rangos `/8` del DoD, y los nombres de host y contraseñas son aleatorios:

| Ruta | Contenido falso |
|------|-----------------|
| `/.env`, `/.env.*` | dotenv completo: DB, Redis, Mongo, AWS, DO, Cloudflare, Stripe, GitHub, Slack, SendGrid, Twilio, JWT — más un enorme **stack de LLM/IA** (OpenAI, Anthropic, Ollama, Groq, Mistral, Cohere, HuggingFace, Replicate, Together, Perplexity, OpenRouter, DeepSeek, Gemini, Azure OpenAI, LangChain/LangSmith, Pinecone, Weaviate, Qdrant, Chroma) |
| `/.git/config`, `/.git/HEAD` | configuración de git con una URL de credenciales incrustada |
| `/.git-credentials` | credenciales de github / gitlab / bitbucket |
| `/.aws/credentials` | ini de AWS (perfiles default / prod) |
| `/.ssh/id_rsa`, `/id_rsa`, `/id_ed25519` | clave privada falsa de OpenSSH |
| `/wp-config.php` | credenciales de DB de WordPress + sales de autenticación |
| `/config.json` | configuración de app con credenciales anidadas |
| `/secrets.json`, `/credentials.json` | paquete de secretos en JSON |
| `/.vscode/sftp.json` | host SFTP / usuario / contraseña |
| `/docker-compose.yml` | archivo compose con secretos de entorno |
| `/.npmrc` | tokens de autenticación del registro npm |
| `/.pypirc` | tokens de subida a PyPI |
| `/.netrc` | máquina / inicio de sesión / contraseña |
| `/.htpasswd`, `/.htaccess` | hashes de htpasswd |
| `/backup.sql`, `/dump.sql`, `/database.sql`, `/db.sql` | volcado SQL con `users` falsos + hashes de contraseñas |

## User-agents de bots

Una página HTML dinámica de burla (con una carga útil de basura oculta para envenenar los scrapers) y un montón de encabezados molestos: `X-Fuck-Scrapers`, `X-Do-Not-Train: 1`, `X-Robots-Tag: noai, noimageai`, `X-Training-Data: poisoned`, y más.

## Crueldad extra (aleatoria)

- **1 de cada 5** accesos a `.env` sufre una **bomba de logs** — todo el archivo repetido 5000× (~19 MB), comprimido en gzip para que sea minúsculo para ti y enorme en sus registros/analizadores.
- **1 de cada 5** accesos recibe una cola **UTF-16-LE** inválida que hace fallar a los decodificadores UTF-8 ingenuos (el clásico "mi bot comió un mensaje con codificación rara y murió").
- Las IPs falsas provienen solo de rangos `/8` del DoD, para que la "infraestructura" parezca exótica.

## Por qué es seguro

- Las rutas que no son `.env`/`.git` están **ancladas a la raíz** (`^/...`), por lo que los archivos servidos *dentro* de repositorios de git (gitea, gitweb, ...) nunca se ven ocultos.
- Si un `.env` o `.git` real reside en una webroot, flyswatter lo **oculta** — los scanners obtienen la falsificación, nunca el archivo real.
- Si el contenedor de la trampa está caído, esas rutas devuelven `502` — nginx nunca deriva al archivo real.

## Instalación

Requiere **docker** + **nginx**.

```sh
git clone https://github.com/YOU/flyswatter && cd flyswatter
sudo ./setup.sh
```

`setup.sh` compila e inicia el contenedor de la trampa (solo localhost) e instala el mapa + snippet de nginx. Luego agrega **dos líneas** a cada bloque `server { }` que quieras proteger:

```nginx
if ($block_ua) { return 461; }     # user-agents de bot/IA -> página troll
include snippets/flyswatter.conf;     # enrutamiento de trampa + endpoints de secretos falsos
```

Recargar:

```sh
sudo nginx -t && sudo systemctl reload nginx
```

Consulta `nginx/EXAMPLE-site.conf` para un ejemplo completo de bloque servidor.

## Configuración

- `FLYSWATTER_PORT` — puerto del host para el contenedor de la trampa (por defecto `8899`).

## Ajustes

- Edita la lista de user-agents en `nginx/conf.d/block-bots.conf`.
- Para dejar de registrar el tráfico atrapado, añade `if=$loggable` a tu directiva `access_log`.

## Archivos

```
app.py                     el servidor de la trampa (Flask)
Dockerfile                 compila el contenedor
setup.sh                   compilar + ejecutar + instalar configuración de nginx
nginx/conf.d/block-bots.conf   mapas $block_ua + $loggable
nginx/snippets/flyswatter.conf    enrutamiento de trampa (include de integración directa)
nginx/EXAMPLE-site.conf        ejemplo de bloque servidor protegido
```

---

###### Espejos: [SuperNETs](https://git.supernets.org/acidvegas/) • [GitHub](https://github.com/acidvegas/) • [GitLab](https://gitlab.com/acidvegas/) • [Codeberg](https://codeberg.org/acidvegas/)
