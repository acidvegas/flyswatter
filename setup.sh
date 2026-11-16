#!/usr/bin/env bash
# flyswatter - build & run the trap server, install the nginx map + snippet.
# Run as root (writes to /etc/nginx). Requires: docker, nginx.
set -e
cd "$(dirname "$0")"

PORT="${FLYSWATTER_PORT:-8899}"

echo "==> building & starting flyswatter on 127.0.0.1:${PORT}"
docker build -t flyswatter .
docker rm -f flyswatter 2>/dev/null || true
docker run -d --name flyswatter --restart unless-stopped --user 10001:10001 -e HOME=/tmp \
	-p 127.0.0.1:"${PORT}":5000 \
	flyswatter

echo "==> installing nginx config"
mkdir -p /etc/nginx/snippets
install -m 644 nginx/conf.d/block-bots.conf /etc/nginx/conf.d/block-bots.conf
install -m 644 nginx/snippets/flyswatter.conf  /etc/nginx/snippets/flyswatter.conf
sed -i "s|127.0.0.1:8899|127.0.0.1:${PORT}|g" /etc/nginx/snippets/flyswatter.conf

cat <<'NEXT'

==> Done. Add these TWO lines to every server{} block you want protected:

        if ($block_ua) { return 461; }     # bot/AI user-agents -> troll page
        include snippets/flyswatter.conf;     # trap routing + fake-secret endpoints

    Then reload nginx:

        nginx -t && systemctl reload nginx

NEXT
