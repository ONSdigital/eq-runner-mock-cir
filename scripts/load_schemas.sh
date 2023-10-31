#!/usr/bin/env bash

set -e

DIR="$(dirname "$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )")" || exit

SCHEMAS_REPO="onsdigital/eq-questionnaire-schemas"
SCHEMAS_TAG=$(curl "https://api.github.com/repos/${SCHEMAS_REPO}/releases" | jq '.[0].name' | tr -d '"')
DOWNLOAD_URL=$(curl "https://api.github.com/repos/${SCHEMAS_REPO}/releases/tags/${SCHEMAS_TAG}" | jq '.assets[0].browser_download_url' | tr -d '"')
RELEASE_NAME=${DOWNLOAD_URL##*/}

echo "Fetching ${DOWNLOAD_URL}"

TEMP_DIR=$(mktemp -d)

curl -L --url "${DOWNLOAD_URL}" --output "${TEMP_DIR}/${RELEASE_NAME}"
unzip -o "${TEMP_DIR}/${RELEASE_NAME}" -d ./
rm -rf "${TEMP_DIR}"
