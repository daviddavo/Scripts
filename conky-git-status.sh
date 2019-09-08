#!/bin/bash

function process_status {
    local status repo
    status=$1
    repo=$2

    if [ -n "${status}" ]; then
        echo "\${goto 40}\${color2}${repo#$HOME/}\${color}"
        while read -r line; do
            symbol="${line:0:2}"
            symbol="${symbol// /}"
            echo "\${alignr}${line:2} \${color #5F9EA0}${symbol}\${color}"
        done <<<"${status}"
        echo
    fi
}

main () {
    process_status "$(yadm status -s)" "yadm"

    local repo status line
    for repo in "$HOME/Scripts"; do
        cd "${repo}" || exit 1
        process_status "$(git status -s)" "${repo}"
    done
}

main "$@"
