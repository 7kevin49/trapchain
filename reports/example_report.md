# SOC Summary Report

Time window: **2025-04-29T16:46:36.802811Z** → **2025-04-29T22:46:36.802811Z**

## Event Breakdown

| severity   |   count |
|:-----------|--------:|
| INFO       |       3 |
| MEDIUM     |       2 |
| HIGH       |       1 |
| UNKNOWN    |       1 |
| CRITICAL   |       1 |

## Detailed Events by Severity

### CRITICAL

- **Actor:** external IPs (e.g., 194.0.234.21, 218.92.0.216, etc.) | **Action:** investigate immediately | **Context:** Multiple login attempts with some success, indicating possible credential stuffing or targeted attack. | **Source:** external IPs (e.g., 194.0.234.21, 218.92.0.216, etc.) | **Time:** 2025-04-29T22:40:19+ to 2025-04-29T22:40:21+ | **Technique:** Credential stuffing / brute-force login
    - login attempt [b'root'/b'Aa123456'] succeeded
    - login attempt [b'ethan'/b'ethan123'] failed
    - login attempt [b'daniel'/b'daniel123'] failed
    - login attempt [b'jacob'/b'jacob123'] failed
    - login attempt [b'root'/b'Aa123456'] succeeded
    - login attempt [b'ethan'/b'ethan123'] failed
    - login attempt [b'daniel'/b'daniel123'] failed
    - login attempt [b'jacob'/b'jacob123'] failed
    - login attempt [b'root'/b'Aa123456'] succeeded
    - login attempt [b'ethan'/b'ethan123'] failed
    - login attempt [b'daniel'/b'daniel123'] failed
    - login attempt [b'jacob'/b'jacob123'] failed

### INFO

- **Actor:** cowrie honeypot | **Action:** ignore | **Context:** Repeated connection resets, typical of automated or scanning activity, no successful login attempts. | **Source:** cowrie honeypot | **Time:** 2025-04-29T20:46:38+ | **Technique:** Repeated SSH connection attempts, no successful login
    - [cowrie.ssh.transport.HoneyPotSSHTransport#info] connection lost
    - [HoneyPotSSHTransport,70522,10.244.2.1] Connection lost after 0 seconds
    - [cowrie.ssh.transport.HoneyPotSSHTransport#info] connection lost
    - [HoneyPotSSHTransport,70523,10.244.2.1] Connection lost after 0 seconds
    - ... (many similar logs of connection resets and no moduli)

- **Actor:** cowrie honeypot | **Action:** ignore | **Context:** Multiple connection attempts from external IPs, failed SSH login attempts, typical of brute-force scanning. | **Source:** cowrie honeypot | **Time:** 2025-04-29T20:49:13+ | **Technique:** Brute-force login attempts with failed credentials
    - [cowrie.ssh.transport.HoneyPotSSHTransport#info] connection lost
    - [HoneyPotSSHTransport,70538,165.227.88.67] Connection lost after 1 seconds
    - [cowrie.ssh.transport.HoneyPotSSHTransport#info] connection lost
    - [HoneyPotSSHTransport,70560,164.92.201.86] Connection lost after 1 seconds
    - ... (many similar logs of connection resets)

- **Actor:** internal logs | **Action:** ignore | **Context:** Normal connection resets, no security concern | **Source:** internal logs | **Time:** 2025-04-29T22:42:58 to 2025-04-29T22:46:28 | **Technique:** connection resets
    - [cowrie.ssh.transport.HoneyPotSSHTransport#info] connection lost
    - [HoneyPotSSHTransport,71271,10.244.2.1] Connection lost after 0 seconds
    - [cowrie.ssh.transport.HoneyPotSSHTransport#info] connection lost
    - [HoneyPotSSHTransport,71272,10.244.2.1] Connection lost after 0 seconds
    - [cowrie.ssh.transport.HoneyPotSSHTransport#info] connection lost
    - [HoneyPotSSHTransport,71273,10.244.2.1] Connection lost after 0 seconds
    - [cowrie.ssh.transport.HoneyPotSSHTransport#info] connection lost
    - [HoneyPotSSHTransport,71274,10.244.2.1] Connection lost after 0 seconds
    - [cowrie.ssh.transport.HoneyPotSSHTransport#info] connection lost
    - [HoneyPotSSHTransport,71275,10.244.2.1] Connection lost after 0 seconds
    - [cowrie.ssh.transport.HoneyPotSSHTransport#info] connection lost
    - [HoneyPotSSHTransport,71276,10.244.2.1] Connection lost after 0 seconds
    - [cowrie.ssh.transport.HoneyPotSSHTransport#info] connection lost
    - [HoneyPotSSHTransport,71277,10.244.2.1] Connection lost after 0 seconds
    - [cowrie.ssh.transport.HoneyPotSSHTransport#info] connection lost
    - [HoneyPotSSHTransport,71278,10.244.2.1] Connection lost after 0 seconds
    - [cowrie.ssh.transport.HoneyPotSSHTransport#info] connection lost
    - [HoneyPotSSHTransport,71279,10.244.2.1] Connection lost after 0 seconds
    - [cowrie.ssh.transport.HoneyPotSSHTransport#info] connection lost
    - [HoneyPotSSHTransport,71280,10.244.2.1] Connection lost after 0 seconds
    - [cowrie.ssh.transport.HoneyPotSSHTransport#info] connection lost
    - [HoneyPotSSHTransport,71281,10.244.2.1] Connection lost after 0 seconds
    - [cowrie.ssh.transport.HoneyPotSSHTransport#info] connection lost
    - [HoneyPotSSHTransport,71282,10.244.2.1] Connection lost after 0 seconds
    - [cowrie.ssh.transport.HoneyPotSSHTransport#info] connection lost
    - [HoneyPotSSHTransport,71283,10.244.2.1] Connection lost after 0 seconds
    - [cowrie.ssh.transport.HoneyPotSSHTransport#info] connection lost
    - [HoneyPotSSHTransport,71284,10.244.2.1] Connection lost after 0 seconds
    - [cowrie.ssh.transport.HoneyPotSSHTransport#info] connection lost
    - [HoneyPotSSHTransport,71285,10.244.2.1] Connection lost after 0 seconds
    - [cowrie.ssh.transport.HoneyPotSSHTransport#info] connection lost
    - [HoneyPotSSHTransport,71286,10.244.2.1] Connection lost after 0 seconds
    - [cowrie.ssh.transport.HoneyPotSSHTransport#info] connection lost
    - [HoneyPotSSHTransport,71287,10.244.2.1] Connection lost after 0 seconds
    - [cowrie.ssh.transport.HoneyPotSSHTransport#info] connection lost
    - [HoneyPotSSHTransport,71288,10.244.2.1] Connection lost after 0 seconds
    - [cowrie.ssh.transport.HoneyPotSSHTransport#info] connection lost
    - [HoneyPotSSHTransport,71289,10.244.2.1] Connection lost after 1 seconds
    - [cowrie.ssh.transport.HoneyPotSSHTransport#info] connection lost
    - [HoneyPotSSHTransport,71289,195.178.110.238] Connection lost after 1 seconds
    - [cowrie.ssh.transport.HoneyPotSSHTransport#info] connection lost
    - [HoneyPotSSHTransport,71290,10.244.2.1] Connection lost after 0 seconds
    - [cowrie.ssh.transport.HoneyPotSSHTransport#info] connection lost
    - [HoneyPotSSHTransport,71291,10.244.2.1] Connection lost after 0 seconds
    - [cowrie.ssh.transport.HoneyPotSSHTransport#info] connection lost
    - [HoneyPotSSHTransport,71292,10.244.2.1] Connection lost after 0 seconds
    - [cowrie.ssh.transport.HoneyPotSSHTransport#info] connection lost
    - [HoneyPotSSHTransport,71293,10.244.2.1] Connection lost after 0 seconds

### UNKNOWN

- **Actor:** external IPs (e.g., 195.178.110.238, 218.92.0.103, 124.5.208.87, etc.) | **Action:** investigate | **Context:** Repeated failed SSH login attempts from external IPs, indicating potential brute-force attack. | **Source:** external IPs (e.g., 195.178.110.238, 218.92.0.103, 124.5.208.87, etc.) | **Time:** 2025-04-29T22:11:00+ to 2025-04-29T22:40:21+ | **Technique:** Brute-force SSH login attempts
    - [2025-04-29T21:25:08.285542+00:00] 2025-04-29T21:25:08+0000 [cowrie.ssh.factory.CowrieSSHFactory] No moduli, no diffie-hellman-group-exchange-sha1
    - [2025-04-29T21:25:08.285586+00:00] 2025-04-29T21:25:08+0000 [cowrie.ssh.factory.CowrieSSHFactory] No moduli, no diffie-hellman-group-exchange-sha256
    - [2025-04-29T21:25:08.285905+00:00] 2025-04-29T21:25:08+0000 [cowrie.ssh.factory.CowrieSSHFactory] New connection: 195.178.110.238:50366 (10.244.2.11:2222) [session: 29c7478c62f3]
    - [2025-04-29T21:25:08.286117+00:00] 2025-04-29T21:25:08+0000 [cowrie.ssh.transport.HoneyPotSSHTransport#info] connection lost
    - [2025-04-29T21:25:18.284620+00:00] 2025-04-29T21:25:18+0000 [cowrie.ssh.factory.CowrieSSHFactory] No moduli, no diffie-hellman-group-exchange-sha1
    - [2025-04-29T21:25:18.284681+00:00] 2025-04-29T21:25:18+0000 [cowrie.ssh.factory.CowrieSSHFactory] No moduli, no diffie-hellman-group-exchange-sha256
    - ... (many similar logs of connection attempts from various external IPs, with no successful login)

