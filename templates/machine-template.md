# Executive Summary

{% hint style="info" %}
**Quick Reference**

| | |
| --- | --- |
| **Machine** | NAME |
| **OS** | Linux / Windows |
| **Difficulty** | Easy |
| **Retired** | YYYY-MM-DD |
| **Initial Foothold** | CWE-XXX — short description |
| **Privilege Escalation** | short description |
{% endhint %}

One paragraph on what the box is, what the intended path was, and what the
root cause of each finding was in business terms.

## Skills/Concepts Improved

- 
- 
- 

## Tools Used

- 
- 

---

#### Provided Files / Target:

| Item | Value |
| --- | --- |
| Target | 10.10.10.X |
| Hostname | |
| Provided credentials | none |

---

# I. Enumeration

```bash

```

---

# II. Foothold

```bash

```

---

# III. Lateral Movement

```bash

```

---

# IV. Privilege Escalation

```bash

```

---

## Remediation

| Finding | Severity | Remediation |
| --- | --- | --- |
| | | |

## References

- 

## Mind Map

```
NAME
├── [>] 22/tcp  ssh
├── [>] 80/tcp  http
│   ├── [X] /admin — 403, no bypass
│   └── [>] /upload — unauthenticated file upload
│       └── [>] php reverse shell → www-data
├── [X] 445/tcp smb — anonymous denied
└── [>] www-data
    ├── [X] sudo -l — nothing
    └── [>] SUID /usr/bin/BINARY → root
```
