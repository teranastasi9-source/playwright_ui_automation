#!/bin/sh
set -e

# Fresh, unattended install on every container start (no persisted volumes, no
# committed DB dump by design - see README's "Self-hosted OrangeHRM" section for why).
# OrangeHRM's official web installer has no documented env-var bypass, but the image
# also ships a Symfony console command that takes the exact same answers over stdin:
# `php installer/console install:on-new-database`. That's what this script drives.

CONF_FILE=/var/www/html/lib/confs/Conf.php

DB_HOST_NAME="${DB_HOST_NAME:-orangehrm-db}"
DB_HOST_PORT="${DB_HOST_PORT:-3306}"
DB_NAME="${DB_NAME:-orangehrm}"
DB_PRIVILEGED_USER="${DB_PRIVILEGED_USER:-root}"
DB_PRIVILEGED_PASSWORD="${DB_PRIVILEGED_PASSWORD:-orangehrm}"
ORG_NAME="${ORG_NAME:-QA Playground}"
ORG_COUNTRY="${ORG_COUNTRY:-united states}"
ADMIN_FIRST_NAME="${ADMIN_FIRST_NAME:-QA}"
ADMIN_LAST_NAME="${ADMIN_LAST_NAME:-Playground}"
ADMIN_EMAIL="${ADMIN_EMAIL:-admin@example.com}"
ADMIN_USERNAME="${ADMIN_USERNAME:-Admin}"
ADMIN_PASSWORD="${ADMIN_PASSWORD:?ADMIN_PASSWORD must be set}"

wait_for_db() {
    echo "Waiting for database at ${DB_HOST_NAME}:${DB_HOST_PORT}..."
    i=0
    while [ "$i" -lt 60 ]; do
        if php -r "exit(@fsockopen('${DB_HOST_NAME}', ${DB_HOST_PORT}) ? 0 : 1);"; then
            echo "Database is reachable."
            return 0
        fi
        i=$((i + 1))
        sleep 2
    done
    echo "Timed out waiting for the database." >&2
    exit 1
}

if [ ! -f "$CONF_FILE" ]; then
    wait_for_db
    echo "Running OrangeHRM's unattended CLI installer..."
    cd /var/www/html
    # Answer order/count must match InstallOnNewDatabaseCommand's exact prompt sequence
    # (verified by reading installer/Command/InstallOnNewDatabaseCommand.php in the image -
    # it has no --no-interaction support, so this is the only scriptable path). Three blank
    # lines total: the first two are Language/Timezone Group, which the command accepts
    # empty (Timezone itself does not, hence the explicit "UTC" after them); the third,
    # right after ${ADMIN_EMAIL}, answers a separate optional prompt in the Admin User step.
    php installer/console install:on-new-database -v <<ANSWERS
yes
${DB_HOST_NAME}
${DB_HOST_PORT}
${DB_NAME}
${DB_PRIVILEGED_USER}
${DB_PRIVILEGED_PASSWORD}
yes
no
${ORG_NAME}
${ORG_COUNTRY}


UTC
${ADMIN_FIRST_NAME}
${ADMIN_LAST_NAME}
${ADMIN_EMAIL}

${ADMIN_USERNAME}
${ADMIN_PASSWORD}
${ADMIN_PASSWORD}
no
yes
ANSWERS
    echo "OrangeHRM installation complete."
fi

exec docker-php-entrypoint apache2-foreground
