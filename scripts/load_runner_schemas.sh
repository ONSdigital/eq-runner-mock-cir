#!/usr/bin/env bash

set -e

DIR="$(dirname "$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )")" || exit

REPO_NAME="eq-questionnaire-runner"
RUNNER_REPO="onsdigital/${REPO_NAME}"
RUNNER_TAG=$(curl "https://api.github.com/repos/${RUNNER_REPO}/releases" | jq '.[0].name' | tr -d '"')
DOWNLOAD_URL="https://github.com/${RUNNER_REPO}/archive/refs/tags/${RUNNER_TAG}.zip"
DOWNLOAD_NAME="${REPO_NAME}-${RUNNER_TAG##*v}"

echo "Fetching ${DOWNLOAD_URL}"

TEMP_DIR=$(mktemp -d)

curl -L --url "${DOWNLOAD_URL}" --output "${TEMP_DIR}/${DOWNLOAD_NAME}"
unzip -o "${TEMP_DIR}/${DOWNLOAD_NAME}" "${DOWNLOAD_NAME}/schemas/test/*" -d ./schemas
rm -rf "${TEMP_DIR}"

# files get extracted to schemas/runner-vx.x.x/schemas/test so move to schemas/test deleting any existing folder
if [ -d ./schemas/test ]; then
    rm -rf ./schemas/test
fi
mv -f "schemas/${DOWNLOAD_NAME}/schemas/test" ./schemas/test
rm -rf "schemas/${DOWNLOAD_NAME}"
