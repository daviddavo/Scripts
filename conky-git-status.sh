#!/bin/bash

function fetch_if_should {
    date_compare="15 minutes ago"
    if [ ! -f .git/FETCH_HEAD ] \
       || [ $(stat -c %Y .git/FETCH_HEAD) -le $(date -d "${date_compare}" +%s) ]; then
           echo ">>> Should fetch $(pwd)">&2
        git fetch -q --all &
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
                statbh=$(echo $line | sed -nr 's/.*\[([[:alpha:]]*)[[:space:]]+([[:digit:]]+)\].*/\1/p')
                statn=$(echo $line | sed -nr 's/.*\[([[:alpha:]]*)[[:space:]]+([[:digit:]]+)\].*/\2/p')
                # echo $statbh
                if [ "${statbh}" = "behind" ]; then
                    echo -n "\${color red}\${alignr}[${statn}]\${color}"
                elif [ "${statbh}" = "ahead" ]; then
                    echo -n "\${color green}\${alignr}[${statn}]\${color}"
                elif [ ! -z "${statbh}" ]; then
                    echo -n "\${color yellow}\${alignr}$statbh\${color}"
                fi
            else
                symbol="${line:0:2}"
                symbol="${symbol// /}"
                str=${line:2}
                str=${str//#/\\#}
                echo
                echo -n "\${alignr}${str} \${color #5F9EA0}${symbol}\${color}"
            fi
            let cnt=$cnt+1
        done <<<"${status}"
        if [ $cnt -le 1 ] && [ -z $statn ]; then
            echo "\${alignr}\${color #5F9EA0}OK\${color}"
        else
            echo
        fi
    else
        echo "\${goto 40}\${color2}${repo}\${alignr}\${color #5F9EA0}OK\${color}"
    fi
}

main () {
    unset LANG
    locale >&2
    process_status "$(yadm status -bs)" "yadm"
    cd ~/.config/yadm/repo.git
    fetch_if_should

    cd ~/Scripts
    process_status "$(git status -bs)" "Scripts"
    fetch_if_should


    local repo status line
    for repo in $(find ~/Documentos -name .git -type d -prune -exec dirname {} \; ); do
        cd "${repo}" || exit 1
        fetch_if_should
        process_status "$(git status -bs)" "${repo#$HOME/Documentos/}"
    done
}

main "$@"
