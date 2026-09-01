#!/usr/bin/env bash
set -euo pipefail
MF="${1:-manifest.tsv}"
[[ -f "$MF" ]] || { echo "no such manifest: $MF" >&2; exit 1; }

while IFS='|' read -r pat action dest slug; do
    [[ -z "$pat" ]] && continue
    sed -i -E "s|^[a-z]+\t[A-Za-z-]*\t([^\t]*${pat}[^\t]*)\t([^\t]*).*$|${action}\t${dest}\t\1\t\2\t${slug}|" "$MF"
done <<'MAP'
Hacking-Bashed|machine|easy|bashed
Shocker--From-403|machine|easy|shocker
Legacy--Smashing-Windows-XP|machine|easy|legacy
Nibbles--Web-Enumeration|machine|easy|nibbles
Knife--The-Invisible-Wound|machine|easy|knife
Devel--Anonymous-FTP|machine|easy|devel
Nothing-Hidden--Exposing-Netmon|machine|easy|netmon
Piercing-the-Veil-of-Timelapse|machine|easy|timelapse
Walking-the-Ancient-Paths|machine|easy|lame
Return-to-Sender--Auditing-Printer|machine|easy|return
From-Login-Form-to-Root-Access|machine|easy|goodgames
Hacking-Windows-Server|machine|easy|optimum
Resurrecting-the-Dead|machine|medium|cascade
From-Anonymous-to-Administrator|machine|medium|monteverde
Trick-HTB-Machine|machine|easy|trick
Fluffy-HTB-Machine|machine|easy|fluffy
Postman-HTB-Machine|machine|easy|postman
Data-HTB-Machine|machine|easy|data
Outbound-HTB-Machine|machine|easy|outbound
Cap-HTB-Machine|machine|easy|cap
Paper-HTB-Machine|machine|easy|paper
Precious-HTB-Machine|machine|easy|precious
Rooting-HTB-Builder|machine|medium|builder
Hack-The-Box-Driver|machine|easy|driver
PROTOCOL-BREACH|machine|medium|escape
The-Breach-in-the-Wall|machine|easy|blue
Jeeves-HTB-Machine|machine|medium|jeeves
Target--Era--Hack-The-Box|machine|medium|era
Cracking-Sysco|ctf|hacksmarter|sysco
Unearthing-the-Truth-in-DC-1|ctf|vulnhub-dc|dc-1
Unearthing-the-Truth-in-DC-2|ctf|vulnhub-dc|dc-2
Unearthing-the-Truth-in-DC-4|ctf|vulnhub-dc|dc-4
Unearthing-the-Truth-in-DC-5|ctf|vulnhub-dc|dc-5
Unearthing-the-Truth-in-DC-9|ctf|vulnhub-dc|dc-9
Git-Hook-Privilege-Escalation|ctf|heroctf|git-hook-privesc
Hacking-Time-Itself--UofTCTF|ctf|uoftctf|guess-the-number
You-re-asking-me-how-to-build|drop||
Thank-you-very-much-ghostyjoe|drop||
MAP

echo "retagged. counts:"
grep -vP '^#' "$MF" | cut -f1 | sort | uniq -c
echo
echo "machines by difficulty:"
grep -P '^machine\t' "$MF" | cut -f2 | sort | uniq -c
echo
echo "still needing review:"
grep -P '\tREVIEW\t' "$MF" | cut -f3 || echo "  none"
