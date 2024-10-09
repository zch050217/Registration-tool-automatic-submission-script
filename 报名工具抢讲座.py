import time
import json
import requests
import random

def get_random_user_agent():
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
        'Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Mobile Safari/537.36',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1'
    ]
    return random.choice(user_agents)

class EnrollmentSubmitter:
    def __init__(self, enrollment_id, access_token):
        self.user_extra_info = {}
        self.enrollment_request_data = []
        self.access_token = access_token
        self.enrollment_id = enrollment_id
        self.base_url = 'https://api-xcx-qunsou.weiyoubot.cn/xcx/enroll'
        self.user_info_url = f'{self.base_url}/v1/userinfo?access_token={self.access_token}'
        self.request_details_url = f'{self.base_url}/v1/req_detail?access_token={self.access_token}&eid={self.enrollment_id}'
        self.submit_url = f'{self.base_url}/v5/enroll'
        self.failed_attempts = 0
        self.failed_attempts_limit = 20

    def get_headers(self):
        return {'User-Agent': get_random_user_agent()}

    def fetch_user_info(self):
        user_info = requests.get(self.user_info_url, headers=self.get_headers()).json()
        for item in user_info['data']['extra_info']:
            names = item['name'] if isinstance(item['name'], list) else [item['name']]
            for name in names:
                self.user_extra_info[name] = item['value']
        print("\n=== 用户信息已成功获取 ===")
        print("\n已保存的用户信息如下：")
        for name, value in self.user_extra_info.items():
            print(f"  - {name}: {value}")
        print("\n=== 开始抢讲座 ===")
        print("---------------------------------------------------------")

    def fetch_enrollment_details(self):
        try:
            enrollment_data = requests.get(self.request_details_url, headers=self.get_headers()).json()
        except json.JSONDecodeError:
            print(f"{time.strftime('%H:%M:%S', time.localtime())} | [!] 获取报名详情失败")
            return False
        
        if not enrollment_data['data']['req_info']:
            print(f"{time.strftime('%H:%M:%S', time.localtime())} | [-] 报名尚未开始")
            return False
        
        for item in enrollment_data['data']['req_info']:
            field_value = self.user_extra_info.get(item['field_name'], '1' * item.get('min_length', 11))
            self.enrollment_request_data.append({
                "field_name": item['field_name'], 
                "field_value": field_value,
                "field_key": item["field_key"]
            })
        return bool(self.enrollment_request_data)

    def submit_enrollment(self):
        body = {
            "access_token": self.access_token, 
            "eid": self.enrollment_id, 
            "info": self.enrollment_request_data,
            "on_behalf": 0, 
            "items": [], 
            "referer": "", 
            "fee_type": ""
        }
        response = requests.post(self.submit_url, json=body, headers=self.get_headers()).json()
        
        if response['sta'] == 0:
            print(f"{time.strftime('%H:%M:%S', time.localtime())} | [+] 报名已成功提交！")
            return True
        
        if response['msg'] == '活动期间只允许提交一次':
            print(f"{time.strftime('%H:%M:%S', time.localtime())} | [-] 活动期间只允许提交一次，无法重复提交。")
            return True
        
        print(f"{time.strftime('%H:%M:%S', time.localtime())} | [-] 提交失败，返回信息：{response['msg']}")
        self.failed_attempts += 1
        return False

    def run(self):
        self.fetch_user_info()
        while self.failed_attempts < self.failed_attempts_limit:
            if self.fetch_enrollment_details():
                if self.submit_enrollment():
                    break
            time.sleep(0.2)
        if self.failed_attempts >= self.failed_attempts_limit:
            print("提交失败次数已达到%d次，停止运行。" % int(self.failed_attempts_limit))

class TokenRetriever:
    def __init__(self):
        self.base_url = 'https://api-xcx-qunsou.weiyoubot.cn/xcx/enroll'
        self.phone_login_url = f'{self.base_url}/v1/login_by_phone'
        self.user_history_url = f'{self.base_url}/v1/user/history?access_token='

    def get_headers(self):
        return {'User-Agent': get_random_user_agent()}

    def login_with_phone(self):

        # phone = ""           # 输入报名工具手机号
        # password = ""      # 输入报名工具密码
        phone = input("请输入手机号：")
        password = input("请输入密码：")
        
        credentials = {"phone": phone, "password": password}
        response = requests.post(self.phone_login_url, json=credentials, headers=self.get_headers()).json()
        
        if response['sta'] == -1:
            print(f"登录失败，{response['msg']}")
            return None
        
        print("\n=== 登录成功，身份为%d****%d ===\n" % (int(phone[0:3]), int(phone[-4:])))
        return response['data']['access_token']

    def show_user_history(self, history_data):
        print('请选择要提交的表单序号')
        for idx, entry in enumerate(history_data, 1):
            print(f"序号：{idx}\t名称：{entry['name']}\t状态：{entry['status']}")

    def run(self):
        access_token = self.login_with_phone()
        if not access_token:
            return

        user_history = []
        result = requests.get(f'{self.user_history_url}{access_token}', headers=self.get_headers()).json()
        
        for entry in result['data']:
            if entry['status'] < 2:
                status = '进行中' if entry['status'] else '未开始'
                user_history.append({'name': entry['title'], 'status': status, 'eid': entry['eid']})

        if not user_history:
            print('请将需要提交的报名添加到个人记录中再运行程序')
            return

        self.show_user_history(user_history)
        while True:
            user_input = input('请输入序号：')
            if user_input.isdigit() and 0 < int(user_input) <= len(user_history):
                EnrollmentSubmitter(user_history[int(user_input) - 1]['eid'], access_token).run()
                break
            print('请输入正确的序号')

if __name__ == '__main__':
    TokenRetriever().run()
    input('按回车退出...')