import requests
import urllib.parse
import json
import time
import subprocess
import asyncio

# URL dan headers
headers = {
    'accept': '*/*',
    'accept-language': 'en-US,en;q=0.9',
    'content-type': 'application/json',
    'origin': 'https://ago-wallet.hexacore.io',
    'priority': 'u=1, i',
    'referer': 'https://ago-wallet.hexacore.io/',
    'sec-ch-ua': '"Chromium";v="124", "Microsoft Edge";v="124", "Not-A.Brand";v="99", "Microsoft Edge WebView2";v="124"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'cross-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0',
}

# Fungsi untuk membaca initData dari file
def read_initdata_from_file(filename):
    initdata_list = []
    with open(filename, 'r') as file:
        for line in file:
            initdata_list.append(line.strip())
    return initdata_list

# Fungsi untuk mengambil id dari initData
def get_user_id_from_init_data(init_data):
    parsed_data = urllib.parse.parse_qs(init_data)
    if 'user' in parsed_data:
        user_data = parsed_data['user'][0]
        user_data_json = urllib.parse.unquote(user_data)
        user_data_dict = json.loads(user_data_json)
        if 'id' in user_data_dict:
            return user_data_dict['id']
    return None

# Fungsi untuk mengambil username dari initData
def get_user_from_init_data(init_data):
    parsed_data = urllib.parse.parse_qs(init_data)
    if 'user' in parsed_data:
        user_data = parsed_data['user'][0]
        user_data_json = urllib.parse.unquote(user_data)
        user_data_dict = json.loads(user_data_json)
        if 'username' in user_data_dict:
            return user_data_dict['username']
    return None

# Fungsi untuk mengambil nama lengkap dari initData
def get_nama_from_init_data(init_data):
    parsed_data = urllib.parse.parse_qs(init_data)
    if 'user' in parsed_data:
        user_data = parsed_data['user'][0]
        data = ""
        user_data_json = urllib.parse.unquote(user_data)
        user_data_dict = json.loads(user_data_json)
        if 'first_name' in user_data_dict:
            data = user_data_dict['first_name']
        if 'last_name' in user_data_dict:
            data = data + " " + user_data_dict['last_name']
        if 'username' in user_data_dict:
            data = data + " " + f"({user_data_dict['username']})"
        return data
    return None

# Data taps
taps = {
    'taps': 100,
}

# Fungsi untuk melakukan login menggunakan initData
def login_with_initdata(json_data):
    response = requests.post('https://hexacore-tg-api.onrender.com/api/app-auth', json=json_data, headers=headers)
    if response.status_code == 200:
        # Menambahkan header Authorization dari hasil response login
        auth_token = response.json()["token"]
        headers["Authorization"] = f"{auth_token}"
    else:
        print(f"Failed to login. Error: {response.text}")
    return response

# Fungsi untuk melakukan start session
def start_session():
    response = requests.post('https://hexacore-tg-api.onrender.com/api/mining-complete', headers=headers, json=taps)
    return response

# Fungsi untuk claim daily reward
def claim_daily(user_id):
    payload = {
        'user_id': user_id,
    }
    response = requests.post('https://hexacore-tg-api.onrender.com/api/daily-reward', headers=headers, json=payload)
    return response

# Fungsi untuk menjalankan operasi untuk setiap initData
async def process_initdata(init_data):
    # Login
    ids = get_user_id_from_init_data(init_data)
    username = get_user_from_init_data(init_data)
    nama = get_nama_from_init_data(init_data)
    
    json_data = {
        'user_id': ids,
        'username': username,
    }

    login_response = login_with_initdata(json_data)
    if login_response.status_code == 200:
        print(f"Logged in successfully for user id: {nama}")
        balance = requests.get(f"https://hexacore-tg-api.onrender.com/api/balance/{ids}", headers=headers)
        print(f"Token balance: {balance.json()['balance']}")
        
        # Start session
        start_response = start_session()
        if start_response.status_code == 200:
            print("Tap successfully")
        else:
            print('Energy depleted, waiting 30 minutes')
        
        # Claim daily reward
        daily_response = claim_daily(ids)
        if daily_response.status_code == 200:
            print("Daily reward claimed successfully")
            print(f"Response: {daily_response.json()}")
        else:
            print('Already claimed today, waiting until tomorrow')
         
        print("\n")        
    else:
        print("\n")
        print(f"Failed to login. Error: {login_response.text}")

# Main program
async def main():
    initdata_file = "initdata.txt"
    
    while True:
        initdata_list = read_initdata_from_file(initdata_file)
        
        tasks = []
        for init_data in initdata_list:
            task = asyncio.create_task(process_initdata(init_data.strip()))
            tasks.append(task)
        
        # Jalankan semua task secara async
        await asyncio.gather(*tasks)
        print("\n")
       
        
        # Delay sebelum membaca ulang file initData
        await asyncio.sleep(0)  # Delay 24 jam sebelum membaca kembali file initData

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"An error occurred: {e}")
        subprocess.run(["python3.10", "gamee.py"])
