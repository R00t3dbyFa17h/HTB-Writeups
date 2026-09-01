# Target: Era (Hack The Box) OS: Linux Difficulty: Medium Attack Vectors: LFI / IDOR -\> PHP Stream…

⚠️ Disclaimer: This article is for educational and security auditing purposes only. All demonstrations were performed on the “Era” machine…

---

### \

\

**Target:** *Era (Hack The Box)* **OS:** *Linux* **Difficulty:** *Medium* **Attack Vectors:** *LFI / IDOR -\> PHP Stream Wrappers -\> Insecure ELF Signing.*

\

⚠️ **Disclaimer:** This article is for educational and security auditing purposes only. All demonstrations were performed on the “Era” machine within the Hack The Box lab environment. Never attempt to access or modify systems without explicit written permission from the owner.

### Executive Summary

**Assessment Target:** Era (10.129.237.233) **Risk Level:** CRITICAL **Assessment Date:** January 28, 2026 **Author:** Nicholas Mullenski

#### Overview

As part of a routine penetration test, an assessment was conducted on the “Era” server to evaluate its security posture. The objective was to identify vulnerabilities that could allow an attacker to compromise the integrity, confidentiality, or availability of the system. The assessment resulted in a total system compromise, identifying critical flaws in the web application’s input handling and a custom internal security tool.

#### Key Findings

The server was hosting a web application that suffered from improper access control and logic flaws. Specifically, the application allowed for the enumeration of hidden resources via IDOR (Insecure Direct Object Reference), leading to the exposure of database credentials. This access allowed us to retrieve source code backups via FTP. Furthermore, the application was vulnerable to Remote Code Execution (RCE) via **PHP Stream Wrappers**, allowing us to execute arbitrary system commands. Privilege escalation was achieved by exploiting a flaw in a custom “ELF Signing” binary used for system monitoring, allowing us to run malicious code as the root user.

#### Business Impact

- <span id="cf41">**Confidentiality Loss:** Database dumps and source code were fully accessible to unauthorized users.</span>
- <span id="4fec">**Total System Takeover:** The RCE vulnerability combined with the privilege escalation vector granted complete control (Root) over the server.</span>
- <span id="bd95">**Integrity Violation:** Attackers could modify system binaries, sign malicious executables, and alter logs.</span>

#### Strategic Recommendations

- <span id="05bb">**Input Validation:** Implement strict sanitization on all user-supplied input, specifically regarding file handling and PHP wrappers.</span>
- <span id="f1d7">**Access Control:** Audit all IDOR vectors and ensure sensitive database dumps are not web-accessible.</span>
- <span id="c6ee">**Code Review:** The custom ELF signing binary should be patched to enforce rigorous cryptographic verification rather than relying on easily bypassed headers.</span>

\

---

### 1.0 Initial Foothold

#### 1.1 Reconnaissance & Enumeration

**1.1.1 Nmap Scan** We began the assessment with a comprehensive Nmap scan to identify open ports and services on `10.129.237.233`.

```
nmap -sC -sV -A -vvv 10.129.237.233
PORT   STATE SERVICE REASON         VERSION
21/tcp open  ftp     syn-ack ttl 63 vsftpd 3.0.5
80/tcp open  http    syn-ack ttl 63 nginx 1.18.0 (Ubuntu)
|_http-server-header: nginx/1.18.0 (Ubuntu)
|_http-title: Did not follow redirect to http://era.htb/
| http-methods:
|_  Supported Methods: GET HEAD POST OPTIONS
Service Info: OSs: Unix, Linux; CPE: cpe:/o:linux:linux_kernel
```

**Findings:**

- <span id="a124">**Port 21 (FTP):** `vsftpd 3.0.5`</span>
- <span id="b9f7">**Port 80 (HTTP):** `nginx 1.18.0`</span>
- <span id="9ddd">**OS:** Linux (Ubuntu)</span>

**1.1.2 Web Enumeration** The initial web scan on `http://era.htb` revealed a standard landing page. `Gobuster` enumeration identified standard assets (`/img`, `/css`), but no obvious entry points. We escalated to subdomain enumeration to identify hidden virtual hosts.

1.  <span id="d7fc">**1.3 Virtual Host Discovery** With the primary domain enumerating standard assets, we suspected the presence of virtual hosts. We utilized gobuster in vhost mode to fuzz for subdomains against the target IP.</span>

```
gobuster vhost -u http://era.htb -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt --append-domain
```

**Findings:** The scan successfully identified a single sub-domain returning a 200 status code:

- <span id="ea97">`file.era.htb`</span>

![](https://cdn-images-1.medium.com/max/800/1*gaJ-STzakEvMijgjca0eCg.png)

\

[View original.](https://medium.com/p/41fba6bf6a0a)

Exported from [Medium](https://medium.com) on September 1, 2026.
