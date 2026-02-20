import json
import requests

BASE = 'http://127.0.0.1:5000'


def main():
    print('Todo API Demo\n' + '-' * 40)

    # Register
    r = requests.post(f'{BASE}/register', json={'user_name': 'testuser', 'password': 'test123'})
    print(f'Register: {r.status_code} - {r.json()}')

    # Login
    r = requests.post(f'{BASE}/login', json={'user_name': 'testuser', 'password': 'test123'})
    print(f'Login:    {r.status_code} - {r.json()}')

    print('-' * 40 + '\nDone. Open http://127.0.0.1:5000 for the web UI.')


if __name__ == '__main__':
    try:
        main()
    except requests.exceptions.ConnectionError:
        print('Error: Server not running. Start with: python app.py')
