#!/bin/bash

function process_status {
    local status repo symbol
    status=$1
    repo=$2

    if [ -n "${status}" ]; then
        echo "\${goto 40}\${color2}${repo}\${color}"
        while read -r line; do
            symbol="${line:0:2}"
            symbol="${symbol// /}"
            echo "\${alignr}${line:2} \${color #5F9EA0}${symbol}\${color}"
        done <<<"${status}"
        echo
    else
        echo "\${goto 40}\${color2}${repo}\${alignr}\${color #5F9EA0}OK\${color}"
    fi
}

main () {
    process_status "$(yadm status -s)" "yadm"

    cd ~/Scripts
    process_status "$(git status -s)" "Scripts"

    local repo status line
    for repo in "$(find ~/Documentos -name .git -type d -prune -exec dirname {} \; )"; do
        cd "${repo}" || exit 1
        process_status "$(git status -s)" "${repo#$HOME/Documentos/}"
    done
}

main "$@"
