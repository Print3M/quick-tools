#!/usr/bin/python3
#
# JavaScript `String.fromCharCode()` generator.
# Example: from-char-code.py TEST 
# Output:  String.fromCharCode(84,69,83,84)
import sys


def make_js_payload(string: str) -> str:
    result = "String.fromCharCode("

    for char in string:
        result += str(ord(char)) + ","

    # Remove last comma and add parenthesis at the end
    result = result[:-1] + ")"

    return result


if __name__ == '__main__':
    if len(sys.argv) < 2 or len(sys.argv[1]) == 0:
        sys.exit('usage: from-char-code.py <string>')

    payload = make_js_payload(sys.argv[1])
    sys.stdout.write(payload + '\n')
