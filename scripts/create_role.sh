#!/bin/bash
ROLE_NAME=$1
DIR_NAMES=(defaults handlers tasks vars)
if [ ${#ROLE_NAME} -gt 0 ]; then
    if [ -d ./roles/$ROLE_NAME ]; then
        echo "[ERROR] Role $ROLE_NAME exist" 1>&2
        exit 1
    else
        for name in ${DIR_NAMES[@]}; do
            mkdir -p ./roles/$ROLE_NAME/$name
            cat << EOF > ./roles/$ROLE_NAME/$name/main.yml
---
...
EOF
        done
    fi
else
    echo "[ERROR] You didn't specify role name" 1>&2
    exit 1
fi