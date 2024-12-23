#!/bin/bash

SSL_DIR="./ssl"
KEY_FILE="${SSL_DIR}/key.pem"
CERT_FILE="${SSL_DIR}/cert.pem"

if [[ $(basename $(pwd)) != "srcs" ]]; then
    cd srcs || exit 1
fi

check_certs() {
    if [ -f "$KEY_FILE" ] && [ -f "$CERT_FILE " ]; then
        echo "SSL Certificates already exist in $SSL_DIR"
        echo "If you want to regenerate these, you'll have to remove them"
        exit 0
    fi
}

create_ssl_dir() {
    if [ ! -d "$SSL_DIR" ]; then
        echo "Creating ssl directory"
        mkdir -p "$SSL_DIR"
    fi
}

generate_certs() {
    echo "Generate new certificates"
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout "$KEY_FILE" \
        -out "$CERT_FILE" \
        -subj "/C=FR/ST=PACA/L=NICE/O=42/CN=localhost"

    chmod 600 "$KEY_FILE"
    chmod 644 "$CERT_FILE"

    echo "SSL certificates successfully generated"
    echo " - Private key : $KEY_FILE"
    echo " - Certificate : $CERT_FILE"
}

# Execute functions
check_certs
create_ssl_dir
generate_certs