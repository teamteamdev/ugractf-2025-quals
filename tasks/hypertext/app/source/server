#!/usr/bin/env bash
set -eo pipefail
trap "echo HTTP/1.0 500 internal-server-error && echo" ERR

declare -A ResponseHeaders
declare -A HttpCodes=(
    [200]=ok
    [307]=temporary-redirect
    [400]=bad-request
    [403]=forbidden
    [404]=not-found
    [405]=method-not-allowed
    [410]=gone
    [500]=internal-server-error
    [501]=unimplemented
    [502]=bad-gateway
)

Version=bash/${BASH_VERSINFO[0]}.${BASH_VERSINFO[1]}.${BASH_VERSINFO[2]}

# https://stackoverflow.com/a/3352015
trim() {
    local var="$*"
    # remove leading whitespace characters
    var="${var#"${var%%[![:space:]]*}"}"
    # remove trailing whitespace characters
    var="${var%"${var##*[![:space:]]}"}"
    printf '%s' "$var"
}

reply() {
    echo HTTP/1.1 $1 ${HttpCodes[$1]}
    echo X-Powered-By: $Version
    echo Connection: close
    for Key in "${!ResponseHeaders[@]}"; do
        echo $Key: ${ResponseHeaders[$Key]}
    done
    echo
    exec cat
}

yeet() {
    ResponseHeaders[Content-Type]=text/html
    reply $1 <<<"<head><title>$1 ${HttpCodes[$1]}</title></head><body><h1>$1 ${HttpCodes[$1]}</h1><img src=https://http.cat/$1><hr>$Version</body>"
}
trap "yeet 500" ERR

normalize-path() {
    case $2 in
        /*) printf %q "$2" ;;
        *) printf %q "$(realpath -sm $1/$2)" ;;
    esac
}

try-redirect() {
    local Temp=$(normalize-path $RequestPath $1)
    if [ -f "$Home/$Temp" ]; then
        ResponseHeaders[Location]=/${RequestHeaders[X-Token]}$Temp
        reply 307
    fi
}

# Allow viewing source code of self
case $RequestType in
    "") ;;
    GET) reply 200 <"${BASH_SOURCE[0]}" ;;
    *) yeet 405 ;;
esac

read RequestType RequestPath RequestProto

case x$RequestProto in
    x|xHTTP/*) ;;
    x*) yeet 501 ;;
esac

: ${Home=.}
# All incoming paths are absolute
RequestPath=$(realpath -sm "$RequestPath")
Path=$Home/$RequestPath

declare -A RequestHeaders
while read Line && test -n "$(trim "$Line")" && <<<"$Line" IFS=: read Header Value; do
    Header="$(trim "$Header")"
    Value="$(trim "$Value")"
    [[ -z "$Header" ]] && yeet 400
    RequestHeaders[$Header]=$Value
done

if [ -f $Path ]; then
    if [ ! -x $Path ]; then
        if [ -r $Path ]; then
            case $RequestType in
                HEAD) reply 200 </dev/null ;;
                GET) cat -- $Path | reply 200 ;;
                *) yeet 405 ;;
            esac
        else
            yeet 403
        fi
    elif [ $(file --mime-type -b "$Path") == text/x-shellscript ]; then
        trap "yeet 502" ERR
        source "$Path"
    else
        yeet 502
    fi
elif [ -d $Path ]; then
    case $Path in
        *[^/]) Path=$Path/ ;&
        */) {
                try-redirect "index.sh"
                try-redirect "index.html"
                ResponseHeaders[Content-Type]=text/plain
                reply 200
            } < <(ls -al1 $Path) ;;
    esac
else
    yeet 404
fi
