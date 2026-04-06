#!/bin/bash

# Generate SSL certificates for local development
mkdir -p devops/ssl

openssl req -x509 -newkey rsa:4096 -keyout devops/ssl/key.pem \
    -out devops/ssl/cert.pem -days 365 -nodes \
    -subj "/C=MA/ST=Casablanca/L=Casablanca/O=MedicalFactCheck/CN=localhost"

echo "✅ SSL certificates generated in devops/ssl/"
