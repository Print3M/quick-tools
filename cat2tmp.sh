#!/usr/bin/env bash
#
# This tool concatenates text files (wordlists) into one file saved in the
# `/tmp/` directory. The final wordlist is sorted and uniqed. STDOUT of the
# this script is a path of the final wordlist file.
#
# It's useful tool to use within one-liners, like so:
# ffuf -u http://test.com/FUZZ -w $(cat2tmp list1.txt list2.txt list3.txt) -ac
#
# Created by Print3M.

set -ueo pipefail

if [[ $# -eq 0 ]]; then
    echo 'Usage: cat2tmp.sh <file1> <file2> <file3> ...'
    exit 1
fi

cmd=()

# Check if all files exist and prepare list of files
for file in "$@"; do
    if ! [[ -f "$file" ]]; then
        echo "cat2tmp: $file file not found!"
        exit 2
    fi

    cmd+=("$file")
done

tmp_file="/tmp/$(date +%s%N).txt"

cat "${cmd[@]}" | sort | uniq >"$tmp_file"

echo -n "$tmp_file"
