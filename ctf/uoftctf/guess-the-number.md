# Hacking Time Itself: UofTCTF 2026 “Guess the Number” Writeup

Event: UofTCTF 2026 Category: Cryptography / Side-Channel Team: w4llz Rank: 48th out of 1,225 Teams (Top 4%!) 🚀 Author:K70n0s510\Nicholas…

---

### Hacking Time Itself: UofTCTF 2026 “Guess the Number” Writeup

**Event:** *UofTCTF 2026* **Category:** *Cryptography / Side-Channe*l **Team:** *w4llz* **Rank:** *48th out of 1,225 Teams (Top 4%!*) 🚀 **Author:**K70n0s510\Nicholas Mullenski

![](https://cdn-images-1.medium.com/max/800/1*Rjq2kE9IG6bNs5dvB1WVLA.png)
<figcaption>Image taken by Nicholas Mullenski</figcaption>

> <a href="https://medium.com/bugbountywriteup/hacking-time-itself-uoftctf-2026-guess-the-number-writeup-7ccd4651e72d?sk=bb9e7ff52147822264d5b5b0d1e3bd27" class="markup--anchor markup--pullquote-anchor" data-href="https://medium.com/bugbountywriteup/hacking-time-itself-uoftctf-2026-guess-the-number-writeup-7ccd4651e72d?sk=bb9e7ff52147822264d5b5b0d1e3bd27" target="_blank">**Not a Member Click Here to Read Full-Story**</a>

### The Event

This weekend, The team that i am apart of, **w4llz**, participated in the University of Toronto CTF (UofTCTF) 2026. It was a massive event with over 1,200 teams competing from around the world. We pushed hard and secured a **48th place finish**, landing us squarely in the top 4%.

While my teammates were doing the heavy lifting on the Web and Pwn challenges **(huge shoutout to the whole squad for carrying the load!)**, I dove into a Cryptography challenge that looked impossible at first glance.

### The Challenge: Guess the Number

**Points:** *179 (Dynamic Scoring)* **Difficulty:** *Medium*

The premise was deceptively simple. The server generates a random **100-bit integer** (x). We have to guess it.

**The Catch:**

- <span id="f640">We can send expressions to the server to be evaluated.</span>
- <span id="285d">We only have **50 queries** allowed.</span>
- <span id="b576">We need to find a 100-bit number.</span>

In a standard binary search (asking “Is x\>y?”), you eliminate half the possibilities with each question. This yields **1 bit of information** per query. To find a 100-bit number, you mathematically need **100 queries**.

We only had 50.

Mathematically, this should be impossible. We needed to extract **2 bits of information** for every single query we sent.

### The Vulnerability: Timing Side-Channel

The server was executing our input using Python’s **`literal_eval`**. This meant that if we sent a computationally expensive mathematical operation, the server would take longer to process it.

We realized we could ask two questions at once:

1.  <span id="3a29">**The Explicit Question (Bit 0):** “Is the k-th bit a 1?” (The server replies “Yes” or “No”).</span>
2.  <span id="a7a9">**The Implicit Question (Bit 1):** “Is the (k+1)-th bit a 1?” (We measure *how long* the server takes to reply).</span>

If the (k+1)-th bit is 1, we force the server to calculate `3**600000` (a massive number). If it's 0, we skip the calculation.

- <span id="7045">**Fast Response (\< 0.2s):** The hidden bit is 0.</span>
- <span id="dc2b">**Slow Response (\> 1.5s):** The hidden bit is 1.</span>

![](https://cdn-images-1.medium.com/max/800/1*8uWUODp1wA0RefXp7bgieA.png)

### The Exploit Script

I wrote this solver using **`pwntools`** to automate the timing attack. It recovers 2 bits per query, solving the 100-bit integer in exactly 50 requests.

```
#!/usr/bin/env python3
from pwn import *
import time

# Target Configuration
HEAVY_BASE = 3
HEAVY_EXP = 600000  # Tuned to force a >1.5s delay on the target server
TIME_THRESHOLD = 0.5

def get_payload(bit_index_k):
    # Logic: ((Next_Bit == 1) AND (Heavy_Calc)) OR (Curr_Bit == 1)

    # Check the (k+1)-th bit
    bit_next_check = {
        'op': '%',
        'arg1': {'op': '/', 'arg1': 'x', 'arg2': 2**(bit_index_k + 1)},
        'arg2': 2
    }

    # Check the k-th bit
    bit_current_check = {
        'op': '%',
        'arg1': {'op': '/', 'arg1': 'x', 'arg2': 2**bit_index_k},
        'arg2': 2
    }

    # Heavy calculation to cause delay (evaluates to 0)
    heavy_zero = {
        'op': '-',
        'arg1': {'op': '**', 'arg1': HEAVY_BASE, 'arg2': HEAVY_EXP},
        'arg2': {'op': '**', 'arg1': HEAVY_BASE, 'arg2': HEAVY_EXP}
    }

    # Construct the side-channel logic
    payload = {
        'op': 'or',
        'arg1': {
            'op': 'and',
            'arg1': bit_next_check,
            'arg2': heavy_zero
        },
        'arg2': bit_current_check
    }
    return str(payload)

def solve():
    # Connect to challenge
    r = remote('35.231.13.90', 5000)

    final_number = 0
    print("[*] Starting Side-Channel Extraction...")

    for i in range(50):
        k = i * 2
        payload = get_payload(k)

        # Send payload and measure execution time
        r.recvuntil(b"Input your expression")
        start_time = time.time()
        r.sendline(payload.encode())
        response = r.recvline().decode().strip()
        duration = time.time() - start_time

        # Analyze results
        bit_k = 1 if "Yes!" in response else 0
        bit_next = 1 if duration > TIME_THRESHOLD else 0

        # Reconstruct the integer
        final_number += (bit_k * (2**k))
        final_number += (bit_next * (2**(k+1)))

        print(f"Query {i+1}: Time={duration:.2f}s -> Bits: {bit_next}{bit_k}")

    print(f"[*] Recovered Number: {final_number}")
    r.sendline(str(final_number).encode())
    print(r.recvall().decode())

if __name__ == "__main__":
    solve()
```

**Flag:** **`uoftctf{h0w_did_y0u_gu3ss_7h3_numb3r}`**

### Rooted in Faith

As I was working on this challenge, staring at the screen and trying to figure out how to see a number that was invisible, this verse came to mind:

> ***“It is the glory of God to conceal a matter; to search out a matter is the glory of kings.”**** — *Proverbs 25:2

In this CTF, the flag was concealed behind strict limitations — it was “hidden” from plain sight. But the joy of cybersecurity (and life) isn’t just in knowing the answer; it’s in the *search*. Just as we had to look at the invisible “timing” of the server to find the truth, we often have to look past the surface level in our spiritual lives to find the wisdom God has hidden for us. He doesn’t hide things to keep them *from* us, but to invite us to seek Him deeper.

By <a href="https://medium.com/@nicholasmullenski" class="p-author h-card">Nicholas Mullenski</a> on [January 15, 2026](https://medium.com/p/7ccd4651e72d).

<a href="https://medium.com/@nicholasmullenski/hacking-time-itself-uoftctf-2026-guess-the-number-writeup-7ccd4651e72d" class="p-canonical">Canonical link</a>

Exported from [Medium](https://medium.com) on September 1, 2026.
