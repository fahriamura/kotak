import requests
import urllib.parse
import json
import time
import subprocess

# URL dan headers umum
common_headers = {
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

# Fungsi untuk melakukan login menggunakan initData
def login_with_initdata(json_data):
    response = requests.post('https://hexacore-tg-api.onrender.com/api/app-auth', json=json_data, headers=common_headers)
    if response.status_code == 200:
        # Mengembalikan header Authorization dari hasil response login
        auth_token = response.json()["token"]
        return {"Authorization": f"{auth_token}"}
    else:
        print(f"Failed to login. Error: {response.text}")
    return None

def mission(auth_headers):
    response = requests.get('https://hexacore-tg-api.onrender.com/api/missions', headers={**common_headers, **auth_headers})
    missions = response.json()

    # Melakukan perulangan untuk setiap misi dan mengirimkan payload missionId
    for mission in missions:
        mission_id = mission['id']
        json_data = {
            'missionId': mission_id,
        }
        responses = requests.post('https://hexacore-tg-api.onrender.com/api/mission-complete', headers={**common_headers, **auth_headers}, json=json_data)
        print(f"Mission ID: {mission_id}, Response: {responses.json()}")

def buytap(nama, auth_headers):
    json_data = {
        'name': nama,
    }
    response = requests.post('https://hexacore-tg-api.onrender.com/api/buy-tap-passes', headers={**common_headers, **auth_headers}, json=json_data)
    return response

def upgrade(auth_headers):
    response = requests.post('https://hexacore-tg-api.onrender.com/api/upgrade-level', headers={**common_headers, **auth_headers})
    return response

def process_initdata(init_data):
    ids = get_user_id_from_init_data(init_data)
    username = get_user_from_init_data(init_data)
    nama = get_nama_from_init_data(init_data)
    
    json_data = {
        'user_id': ids,
        'username': username,
    }

    auth_headers = login_with_initdata(json_data)
    if auth_headers:
        print(f"Logged in successfully for user id: {nama}")
        balance_response = requests.get(f"https://hexacore-tg-api.onrender.com/api/balance/{ids}", headers={**common_headers, **auth_headers})
        balance = balance_response.json()['balance']
        print(f"Token balance: {balance}")
        return (ids, nama, balance, auth_headers)
    else:
        print(f"Failed to login for user id: {ids}")
    return (ids, nama, 0, None)

def main():
    initdata_file = "initdata.txt"
    initdata_list = read_initdata_from_file(initdata_file)
    
    results = []
    for init_data in initdata_list:
        results.append(process_initdata(init_data.strip()))

    while True:
        print("\nMau Melakukan Apa?")
        print("1. Klaim Misi")
        print("2. Upgrade")
        print("3. Buy Tap")
        print("4. Keluar")
        pilihan = input("Pilih: ")

        if pilihan == '1':
            for ids, nama, balance, auth_headers in results:
                if auth_headers:
                    mission(auth_headers)
                else:
                    print(f"Skipping missions for {nama} due to failed login.")
        elif pilihan == '2':
            print("\nID dan Balance:")
            for idx, (ids, nama, balance, auth_headers) in enumerate(results):
                print(f"{idx + 1}. ID: {ids}, Nama: {nama}, Balance: {balance}")
            
            id_pilihan = input("Masukkan (0 jika mau upgrade semua)\nUpgrade ID Yang Mana: ")
            if id_pilihan == '0':
                for ids, nama, balance, auth_headers in results:
                    if auth_headers:
                        upgrade_response = upgrade(auth_headers)
                        print(f"Upgraded for ID: {ids}, Response: {upgrade_response.json()}")
                    else:
                        print(f"Skipping upgrade for {nama} due to failed login.")
            else:
                idx = int(id_pilihan) - 1
                ids, nama, balance, auth_headers = results[idx]
                if auth_headers:
                    upgrade_response = upgrade(auth_headers)
                    print(f"Upgraded for ID: {ids}, Response: {upgrade_response.json()}")
                else:
                    print(f"Skipping upgrade for {nama} due to failed login.")
        elif pilihan == '3':
            print("\nID dan Balance:")
            for idx, (ids, nama, balance, auth_headers) in enumerate(results):
                print(f"{idx + 1}. ID: {ids}, Nama: {nama}, Balance: {balance}")
            
            id_pilihan = input("Pilih ID untuk Buy Tap: ")
            idx = int(id_pilihan) - 1
            ids, nama, balance, auth_headers = results[idx]

            if auth_headers:
                tap_options = requests.get("https://hexacore-tg-api.onrender.com/api/get-tap-passes", headers={**common_headers, **auth_headers})
                tap_options_data = tap_options.json()
                tap_passes = tap_options_data['tap_passes']
                
                print("\nTap Passes Options:")
                for key, value in tap_passes.items():
                    print(f"{key}: {value['user_cost']} tokens")
                
                tap_choice = input("Input tap yang mana: ")
                if tap_choice in tap_passes:
                    buy_response = buytap(tap_choice, auth_headers)
                    print(f"Buy Tap Response: {buy_response.json()}")
            else:
                print(f"Skipping buy tap for {nama} due to failed login.")
        elif pilihan == '4':
            print("Keluar dari program.")
            break
        else:
            print("Pilihan tidak valid, silakan coba lagi.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"An error occurred: {e}")
        subprocess.run(["python3.10", "gamee.py"])

