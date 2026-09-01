# 🎯Unearthing the Truth in DC-2 \| Breaking Barriers & Restricted Shells 🛡️

From DNS misdirections to restricted environments, we analyze the path to root. 100% completion rooted in precision and faith. 🎯🙏

---

### 🎯Unearthing the Truth in DC-2 \| Breaking Barriers & Restricted Shells 🛡️

#### From DNS misdirections to restricted environments, we analyze the path to root. 100% completion rooted in precision and faith. 🎯🙏

**Target:** *DC-2 (192.168.211.194) \[PG OffSec\]* **OS:** *Linux (Debian)* **Difficulty:** *Easy/Intermediate* **Attack Vectors:** *DNS Mapping -\> WordPress Enumeration (CeWL) -\> RBASH Escape (`vi`) -\> Sudo Abuse (`git`)*

![](https://cdn-images-1.medium.com/max/800/1*KzEwtnRQzkGzVt352onwJg.png)

> <a href="https://medium.com/the-first-digit/unearthing-the-truth-in-dc-2-breaking-barriers-restricted-shells-%EF%B8%8F-71e3969cc096?sk=dcb84ef9cf9e98e7542bca6aae8f7b0b" class="markup--anchor markup--pullquote-anchor" data-href="https://medium.com/the-first-digit/unearthing-the-truth-in-dc-2-breaking-barriers-restricted-shells-%EF%B8%8F-71e3969cc096?sk=dcb84ef9cf9e98e7542bca6aae8f7b0b" target="_blank">**Not a Member?? Click Here to Read the Full-Story**</a>

### Executive Summary

**Assessment Date**: *January 23, 2026* **Risk Level:** *CRITICAL* **Author:** *R00t3dbyFa17h\Nicholas Mullenski*

#### Overview

An initial assessment of the “DC-2” server has identified a web server configuration intended to obscure access via DNS redirection. The host, running on a Linux Debian environment, exposes an Apache web server on Port 80 but restricts direct IP access, forcing a redirection to the hostname dc-2. This indicates a need for local DNS mapping to proceed with further enumeration.

#### Key Findings (Preliminary):

- <span id="af3d">DNS Redirection: The web server is configured to redirect all traffic to <a href="http://dc-2/" class="markup--anchor markup--li-anchor" data-href="http://dc-2/" rel="nofollow noopener" target="_blank">http://dc-2/</a>. Without modification to the attacker’s local /etc/hosts file, the attack surface remains inaccessible.</span>
- <span id="e4d8">Web Server Version: The target is running Apache httpd 2.4.10, a version that will require further scrutiny for misconfigurations once the application layer is accessible.</span>

**Strategic Recommendation (Phase 1):** Immediate modification of the local host file is required to map the target IP to the dc-2 hostname. Once accessible, a full web application vulnerability scan (CMS identification, user enumeration) must be conducted.

![](https://cdn-images-1.medium.com/max/800/1*E4LeuF-_aC0GMJmn-t-s8g.png)
<figcaption>K70n0s510=OffSec handle..</figcaption>

> I’m climbing the leaderboard, 📈 one root at a time! 🛡️ With 11 hosts down and roughly 250+ more on the roadmap, the journey is just beginning.

> Iron sharpens iron — I’m actively looking for dedicated partners to tackle these labs with. If you’re looking for a teammate to grind through machines, share knowledge, and sharpen skills, let’s connect. Drop a comment or send me a DM. Let’s get to work! 🤝💻

### 1.0 Initial Foothold

#### 1.1 Enumeration & Reconnaissance

- <span id="d6b6">The objective of this phase was to identify the attack surface of the target machine and pinpoint specific service versions that may contain known vulnerabilities.</span>

**1.1.1 Nmap Scan** full service and script scan was performed to identify open ports and the software versions running on them.

```
nmap -sCV -vvv -Pn 192.168.211.194
PORT   STATE SERVICE REASON         VERSION
80/tcp open  http    syn-ack ttl 61 Apache httpd 2.4.10 ((Debian))
|_http-server-header: Apache/2.4.10 (Debian)
|_http-title: Did not follow redirect to http://dc-2/
| http-methods:
|_  Supported Methods: GET HEAD POST OPTIONS
```

**Results:** The scan identified Port 80 as open but returned a redirect error in the script output, confirming the need for hostname resolution.

- <span id="f6be">**Port 80 (HTTP):** Apache httpd 2.4.10 (Debian)</span>
- <span id="de55">**Observation:** **`http-title: Did not follow redirect to http://dc-2/`**</span>
- <span id="8de0">**Action Required:** Add **`192.168.211.194 dc-2`** to **`/etc/hosts`**.</span>

#### 1.1.2 Directory Enumeration

- <span id="5f60">Following the DNS configuration, a directory brute-force scan was initiated to map the application structure and identify the Content Management System (CMS).</span>

Command: **`gobuster dir -u`**` `<a href="http://dc-2" class="markup--anchor markup--p-anchor" data-href="http://dc-2" rel="noopener" target="_blank"><strong><code class="markup--code markup--p-code u-paddingRight0 u-marginRight0">http://dc-2</code></strong></a>` `**`-w /usr/share/wordlists/dirb/common.txt`**

**Key Findings:** The scan returned HTTP 301 redirects for several standard WordPress directories, confirming the CMS in use.

![](https://cdn-images-1.medium.com/max/800/1*VbZd01HNWsxASzPsWUmHbg.png)

**Analysis:** The presence of standard WordPress directories confirms that <a href="http://HTTP://dc-2" class="markup--anchor markup--p-anchor" data-href="http://HTTP://dc-2" rel="noopener" target="_blank"><strong>HTTP://dc-2</strong></a> is powered by WordPress. Additionally, the discovery of **/xmlrpc.php** (returning a 405 Method Not Allowed) suggests a potential secondary attack vector if standard login brute-forcing fails, though xmlrpc attacks are often noisier. The primary focus shifts to enumerating users and identifying vulnerable plugins.

#### 1.1.3 User Enumeration

- <span id="35c1">Using WPScan, I enumerated the valid users on the WordPress instance to identify potential targets for a brute-force attack.</span>

**Command**:

```

wpscan --url http://dc-2 --enumerate u
```

**Key Findings:** The scan identified three valid users via the WP JSON API and Author ID brute forcing:

- <span id="bac2">**admin**</span>
- <span id="b9a8">**jerry**</span>
- <span id="ed22">**tom**</span>

Additionally, the scan revealed that the site is running **WordPress 4.7.10** (an outdated version) and has **XML-RPC enabled**, which could serve as an alternative attack vector for brute-forcing if the login page is rate-limited.

#### 1.2 Custom Dictionary Generation

**1.2.1** During the web enumeration, a clue on the “Flag 1” page suggested that standard wordlists would be ineffective (**`"your usual wordlists won't work"`**). This indicated that valid passwords were likely derived from the website's content.

**1.2.2** To address this, I utilized **CeWL** (Custom Word List generator) to spider the site and extract unique words into a targeted dictionary file.

**Command:**

```
cewl http://dc-2 -w dc2-dict.txt
```

#### 1.3 Credential Harvesting

**1.3.1** With the custom wordlist prepared, I launched a targeted password brute-force attack against the identified users (`admin`, `jerry`, `tom`) using **WPScan**.

**Command:**

```
wpscan --url http://dc-2 -U admin,jerry,tom -P dc2-dict.txt
```

**Key Findings:** The attack successfully compromised two accounts:

- <span id="f6e8">**jerry**: **`aXXXXXXXXX`**</span>
- <span id="350c">**tom**: **`pXXXXXXXX`**</span>

![](https://cdn-images-1.medium.com/max/800/1*2zZ_p7U7t-eyXa8c7mfuXg.png)

### 2.0 Internal Compromise (SSH Access)

- <span id="a8b4">An extensive port scan revealed that SSH was running on a non-standard port (**7744**). I leveraged the compromised credentials for the user **tom** to gain initial access.</span>

**Command:**

```
ssh tom@192.168.211.194 -p 7744
```

#### 2.1 Restricted Shell Escape (RBASH)

**2.1.1** Upon logging in, I discovered the environment was a Restricted Bash (rbash) shell. Standard system commands (like cat, cd, grep) were restricted or “not found.”

![](https://cdn-images-1.medium.com/max/800/1*CUmNMDrsQsZXE4U8sWr3tQ.png)

**2.1.2** I enumerated the allowed binaries by listing the user’s path directory: **Command:**

```
ls usr/bin
```

**Allowed Binaries:** **`less`,** **`ls`,** **`scp`,** **`vi`.**

**Exploitation:** The presence of the vi text editor presented a known breakout vulnerability. I utilized vi to spawn a fresh, unrestricted shell.

**Escape Sequence:**

1.  <span id="7685">**Launched** **`vi`**.</span>

2\. Executed **`:set shell=/bin/sh`** inside the editor.

3\. Executed** `:shell`** to spawn the shell.

4\. Once out, I restored the environment path to enable standard commands:

```
export PATH=/bin:/usr/bin:$PATH
```

**Result:** Full shell access was achieved. I was then able to read local.txt to capture the user flag.

![](https://cdn-images-1.medium.com/max/800/1*pmcZbeMv8a5DB-VVi1ZGMg.png)

### 3.0 Privilege Escalation (Root)

#### 3.1 Sudo -l

**3.1.1** After pivoting to the user jerry, I checked for administrative privileges using the sudo -l command.

Command:

```
sudo -l
```

![](https://cdn-images-1.medium.com/max/800/1*23ZB2hyO2ixuxIjDJShfMQ.png)

**3.1.2 Exploitation (GTFOBins):** I leveraged the git binary to spawn a privileged shell. By invoking the help command, git launches a pager (typically less) to display the text. This pager allows for shell command execution.

- <span id="bb10">Command: **`sudo git -p help config`**.</span>
- <span id="00c8">Payload: Inside the pager interface, I typed **`!/bin/sh`** and pressed Enter.</span>

**Outcome:** The pager executed the shell request with the permissions of the parent process (Root), resulting in a complete system compromise. I successfully navigated to /root and retrieved **`proof.txt`** flag.

![](https://cdn-images-1.medium.com/max/800/1*ljAifUmWPZ-9uifVJgY7nQ.png)

![](https://cdn-images-1.medium.com/max/800/1*-CdMPZihtw5J8ztWmFZvZQ.png)

### 4.0 Red Team Mandate & Remediation

**Assessment Summary:** The compromise of DC-2 demonstrates that “Security by Obscurity” is a failed strategy. While the administrator attempted to hide access points (moving SSH to port 7744) and restrict user movements (Restricted Bash), these measures were easily bypassed through standard enumeration and misconfiguration abuse. The most critical failure was the **Principle of Least Privilege**: allowing a restricted user access to a tool (**`vi`**) that spawns shells, and allowing an unprivileged user (**`jerry`**) to run a system binary (**`git`**) as root.

**Immediate Remediation Steps:**

1.  <span id="f7af">**Patch Management:** The WordPress installation (v4.7.10) is severely outdated. Immediate updating to the latest stable version is required to mitigate known vulnerabilities.</span>
2.  <span id="3ba2">**Password Policy Enforcement:** Two user passwords were cracked using words found on the company’s own public website. Implement strict password complexity requirements that reject dictionary words associated with the organization.</span>
3.  <span id="222f">**Restricted Shell Hardening:** The current **`rbash`** configuration is ineffective.</span>

- <span id="6eac">**Remove** **`vi`:** Text editors like **`vi`** allow for shell spawning. Replace with restricted editors (like **`rvim`**) or remove them entirely from the allowed binary list.</span>
- <span id="1cac">**Secure Path:** Ensure the user cannot modify their own environment variables.</span>

1.  <span id="9ad0">**Sudoers Misconfiguration:** The user **`jerry`** has **`NOPASSWD`** access to **`/usr/bin/git`**. This binary contains known privilege escalation vectors (GTFOBins). This entry must be removed from the **`/etc/sudoers`** file immediately.</span>

### ✝️ The Spiritual Root

> “And I will walk at liberty: for I seek thy precepts.”* — ****Psalm 119:45 (KJV)***

**Connection to the Tool:** In this assessment, we faced the **Restricted Shell (rbash)** — a digital prison designed to limit our movement, silence our commands, and keep us from the full power of the system. We were “locked in,” unable to see or do what we were created to do.

However, the restriction was an illusion that could not withstand knowledge. By understanding the “precepts” of the system — how `vi` handles processes and how the shell interprets commands—we broke the chains. We did not use brute force to escape the restricted shell; we used **truth**.

**The Lesson:** Spiritually, we often find ourselves in a “restricted shell” of our own — limited by fear, bound by past mistakes, or constrained by the lies the world tells us about who we are. We feel trapped, unable to move forward. But just as technical knowledge liberated us from `rbash`, seeking God's precepts liberates us from spiritual bondage. When we seek His truth, the restrictions fall away, and we are free to "walk at liberty," fully accessing the purpose and power He has designed for us.

**Rooted in Faith,** *R00t3dbyFa17h\Nicholas Mullenski.*

### 🚀 Join the Mission

I don’t want to do this alone. I want to build a community of people who are hungry to learn, build, and break things (ethically). I am constantly looking for the next challenge.

- <span id="2dfe">Is there a specific tool you wish existed?</span>
- <span id="c828">Is there a hacking concept you want me to learn and explain?</span>
- <span id="cbdc">Do you have a “brick wall” you’re hitting in your own research?</span>

Jump into the server, drop a message, and tell me what I should build or learn next. Let’s sharpen each other.

<a href="https://discord.gg/FjWpMW9SUX" class="markup--anchor markup--mixtapeEmbed-anchor" data-href="https://discord.gg/FjWpMW9SUX" title="https://discord.gg/FjWpMW9SUX"><strong>Join the Iron-Breach Discord Server!</strong><br />
<em>Welcome to Iron Breach. A community where iron sharpens iron. Join us for ethical hacking, CTF challenges, and…</em>discord.gg</a><a href="https://discord.gg/FjWpMW9SUX" class="js-mixtapeImage mixtapeImage mixtapeImage--empty u-ignoreBlock" data-media-id="fd4a28d0f7710c400275a7d63c666614"></a>

By <a href="https://medium.com/@nicholasmullenski" class="p-author h-card">Nicholas Mullenski</a> on [January 24, 2026](https://medium.com/p/71e3969cc096).

<a href="https://medium.com/@nicholasmullenski/unearthing-the-truth-in-dc-2-breaking-barriers-restricted-shells-%EF%B8%8F-71e3969cc096" class="p-canonical">Canonical link</a>

Exported from [Medium](https://medium.com) on September 1, 2026.
