#!/bin/bash

function fetch_if_should {
    date_compare="15 minutes ago"
    if [ ! -f .git/FETCH_HEAD ] || [ $(stat -c %Y .git/FETCH_HEAD) -le $(date -d "${date_compare}" +%s) ]; then
        # echo "Should fetch"
        git fetch -q --all
    fi
}

function process_status {
    local status repo symbol cnt
    status=$1
    repo=$2

    if [ -n "${status}" ]; then
        echo -n "\${goto 40}\${color2}${repo}\${color}"
        let cnt=0
        while read -r line; do
            if [ $cnt -eq 0 ]; then
                cbehind=$(echo $line | sed -nr 's/.*\[[[:alpha:]]*[[:space:]]+([[:digit:]]+)\].*/\1/p')
                if [ -n "${cbehind}" ]; then
                    echo -n "\${color red}\${alignr}[${cbehind}]\${color}"
                fi
            else
                symbol="${line:0:2}"
                symbol="${symbol// /}"
                echo 
                echo -n "\${alignr}${line:2} \${color #5F9EA0}${symbol}\${color}"
            fi
            let cnt=$cnt+1
        done <<<"${status}"
        if [ $cnt -le 1 ] && [ -z $cbehind ]; then
            echo "\${alignr}\${color #5F9EA0}OK\${color}"
        else
            echo
        fi
    else
        echo "\${goto 40}\${color2}${repo}\${alignr}\${color #5F9EA0}OK\${color}"
    fi
}

main () {
    process_status "$(yadm status -bs)" "yadm"

    cd ~/Scripts
    process_status "$(git status -bs)" "Scripts"

    local repo status line
    for repo in $(find ~/Documentos -name .git -type d -prune -exec dirname {} \; ); do
        cd "${repo}" || exit 1
        fetch_if_should
        process_status "$(LC_ALL=en_GB.UTF-8 git status -bs)" "${repo#$HOME/Documentos/}"
    done
}

main "$@"
