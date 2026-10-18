# Part A: the broken padlock

## 1. Real cause

I would blame the new office router or its port-forwarding setup. The DNS answer points to the correct office public IP (check 1), but a request from mobile data gets a `401` from `micro_httpd` with the router's Basic Auth realm (check 6). That means internet traffic on port 80 is reaching the router's own management page instead of Caddy. The ISP replaced the router in early September, before the certificate trouble (check 5).

Caddy uses an HTTP-01 ACME challenge: the certificate service asks for a special file over public HTTP on port 80. The router answers that request with `401`, so the certificate authority cannot verify the domain (check 5). The currently installed certificate expired on Oct 12, 2026 (check 4). This explains the broken padlock.

## 2. Fix it today

1. From the office network, sign in to the router's local admin page. Disable remote administration from the internet. Do not expose the router admin page publicly.
2. Give the Ubuntu computer a reserved LAN address in the router's DHCP settings. Forward TCP ports 80 and 443 to that address. Remove old or duplicate forwards. Check that the ISP has not placed the line behind carrier-grade NAT; the public address must be reachable from outside.
3. From a phone on mobile data, check that `http://app.example.in` no longer shows the router login. It should reach Caddy (or redirect to HTTPS). Confirm `https://app.example.in` and the ACME challenge work from outside. These checks test the path identified by check 6 and the failure in check 5.
4. Check Caddy's logs and confirm it obtains a fresh certificate. Reload Caddy only if needed; a restart alone cannot fix a blocked port. Verify the new certificate's expiry date (check 4).

I choose fixing the port-forward and remote-management settings first. It restores Caddy's normal automatic certificate renewal and has no new recurring service cost. If the ISP uses carrier-grade NAT or blocks inbound port 80, I would ask the ISP for a public routable IP, or use DNS-01 validation with an automated DNS provider API. DNS-01 avoids inbound port 80 for certificate validation, but it does not by itself make the website reachable; visitors still need a working route to Caddy. I would not leave router administration open to the internet.

## 3. Find out before users do

- I would run an external HTTPS check every few minutes from outside the office network. It should check the expected status and response body, not just whether the process is running.
- I would alert the team if the site fails, the certificate has fewer than 21 days left, or HTTP-01 validation fails. I would also send a test alert periodically so a broken alert route is found.
- I would watch Caddy's ACME log and test from mobile data after any router or ISP change. Checks 5 and 6 show that an outside-in check would have caught this early.
- I would record the router port forwards and the Ubuntu computer's reserved address. After a router replacement, I would compare its settings with that record before declaring the change finished.

## 4. What else worries me?

The certificate is already expired (check 4), so users may see a browser warning and some clients will refuse the connection. The `401` from the router (check 6) also suggests its admin page is exposed publicly. That needs to be closed promptly. Private case notes make that exposure especially serious, even though the evidence here does not show that anyone logged in.

Checks 1, 2 and 3 are not the cause. DNS resolves to the correct office IP (check 1). The local API health endpoint succeeds, so the API is alive on the computer (check 2); it does not test public routing or certificates. Caddy is running (check 3), but a running process can still be blocked by the router and can keep serving an expired certificate (checks 4–6).
