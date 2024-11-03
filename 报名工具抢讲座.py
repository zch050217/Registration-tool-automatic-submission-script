import time
import json
import requests
import random
import getpass
import os
from rich.console import Console
from rich.table import Table
from rich.text import Text

console = Console()


def get_random_user_agent():
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
        'Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Mobile Safari/537.36',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1'
    ]
    return random.choice(user_agents)


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')
    console.print(
        "\n[bold cyan]-------------------------------------------[/bold cyan]")
    console.print("        微信报名工具抢讲座小工具v2.2.1")
    console.print("                By C3ngH 2024.10.22")
    console.print(
        "[bold cyan]-------------------------------------------[/bold cyan]\n")


class EnrollmentSubmitter:
    def __init__(self, enrollment_id, access_token, session):
        self.user_extra_info = {}
        self.enrollment_request_data = []
        self.access_token = access_token
        self.enrollment_id = enrollment_id
        self.base_url = 'https://api-xcx-qunsou.weiyoubot.cn/xcx/enroll'
        self.user_info_url = f'{
            self.base_url}/v1/userinfo?access_token={self.access_token}'
        self.request_details_url = f'{
            self.base_url}/v1/req_detail?access_token={self.access_token}&eid={self.enrollment_id}'
        self.submit_url = f'{self.base_url}/v5/enroll'
        self.failed_attempts = 0
        self.failed_attempts_limit = 20
        self.session = session

    def get_headers(self):
        return {'User-Agent': get_random_user_agent()}

    def fetch_user_info(self):
        response = self.session.get(
            self.user_info_url, headers=self.get_headers())
        user_info = response.json()
        for item in user_info['data']['extra_info']:
            names = item['name'] if isinstance(
                item['name'], list) else [item['name']]
            for name in names:
                self.user_extra_info[name] = item['value']
        console.print("\n[green]=== 用户信息已成功获取 ===[/green]")
        console.print("\n[!] 已保存的用户信息如下：")
        for name, value in self.user_extra_info.items():
            console.print(f"  - [yellow]{name}[/yellow]: {value}")
        console.print("\n[green]=== 开始抢讲座 ===[/green]")
        console.print(
            "---------------------------------------------------------")

    def fetch_enrollment_details(self):
        try:
            response = self.session.get(
                self.request_details_url, headers=self.get_headers())
            enrollment_data = response.json()
        except json.JSONDecodeError:
            console.print(f"{time.strftime('%H:%M:%S')
                             } | [red][!] 获取报名详情失败[/red]")
            return False

        if not enrollment_data['data']['req_info']:
            console.print(f"{time.strftime('%H:%M:%S')
                             } | [yellow][-] 报名尚未开始[/yellow]")
            return False

        for item in enrollment_data['data']['req_info']:
            field_value = self.user_extra_info.get(
                item['field_name'], '1' * item.get('min_length', 11))
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
        response = self.session.post(
            self.submit_url, json=body, headers=self.get_headers()).json()

        if response['sta'] == 0:
            console.print(f"{time.strftime('%H:%M:%S')
                             } | [green][+] 报名已成功提交！[/green]")
            return True

        if response['msg'] == '活动期间只允许提交一次':
            console.print(f"{time.strftime('%H:%M:%S')
                             } | [yellow][-] 活动期间只允许提交一次，无法重复提交。[/yellow]")
            return True

        console.print(f"{time.strftime('%H:%M:%S')
                         } | [red][-] 提交失败，返回信息：{response['msg']}[/red]")
        self.failed_attempts += 1
        return False

    def run(self):
        self.fetch_user_info()
        while self.failed_attempts < self.failed_attempts_limit:
            if self.fetch_enrollment_details():
                if self.submit_enrollment():
                    break
            time.sleep(0.25)
        if self.failed_attempts >= self.failed_attempts_limit:
            console.print("[red][!] 提交失败次数已达到%d次，停止运行。[/red]" %
                          self.failed_attempts_limit)


class TokenRetriever:
    def __init__(self):
        self.base_url = 'https://api-xcx-qunsou.weiyoubot.cn/xcx/enroll'
        self.phone_login_url = f'{self.base_url}/v1/login_by_phone'
        self.user_history_url = f'{
            self.base_url}/v1/user/history?access_token='
        self.session = requests.Session()

    def get_headers(self):
        return {'User-Agent': get_random_user_agent()}

    def login_with_phone(self):
        phone = input("[!] 请输入手机号：")
        password = getpass.getpass("[!] 请输入密码(不显示)：")

        credentials = {"phone": phone, "password": password}
        response = self.session.post(
            self.phone_login_url, json=credentials, headers=self.get_headers()).json()

        if response['sta'] == -1:
            console.print(f"[red][!] 登录失败，{response['msg']}[/red]")
            return None

        clear_screen()
        console.print(f"\n[green]=== 登录成功，身份为 {
                      phone[0:3]}****{phone[-4:]} ===[/green]\n")
        return response['data']['access_token']

    def show_user_history(self, history_data):
        console.print('[!] 请选择要提交的表单序号')
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("序号", style="dim")
        table.add_column("名称", style="bold")
        table.add_column("状态", style="green")

        for idx, entry in enumerate(history_data, 1):
            status = entry['status']
            status_text = '进行中' if status == 1 else '未开始'
            table.add_row(str(idx), entry['name'], status_text)

        console.print(table)

    def run(self):
        clear_screen()
#         console.print("""
# [bold cyan]-------------------------------------------
#         微信报名工具抢讲座小工具v2.1.1
#                 By C3ngH 2024.10.22
# -------------------------------------------[/bold cyan]
#         """)
        access_token = self.login_with_phone()
        if not access_token:
            return

        user_history = []
        result = self.session.get(f'{self.user_history_url}{
                                  access_token}', headers=self.get_headers()).json()

        for entry in result['data']:
            if entry['status'] < 2:
                status = '进行中' if entry['status'] else '未开始'
                user_history.append(
                    {'name': entry['title'], 'status': status, 'eid': entry['eid']})

        if not user_history:
            console.print('[red][!] 请将需要提交的报名添加到个人记录中再运行程序[/red]')
            return

        while True:
            self.show_user_history(user_history)
            user_input = input('[!] 请输入序号（输入"r"刷新记录，按回车退出）：')
            if user_input.lower() == 'r':
                # 重新获取记录
                user_history = []
                result = self.session.get(f'{self.user_history_url}{
                                          access_token}', headers=self.get_headers()).json()
                for entry in result['data']:
                    if entry['status'] < 2:
                        status = '进行中' if entry['status'] else '未开始'
                        user_history.append(
                            {'name': entry['title'], 'status': status, 'eid': entry['eid']})
                if not user_history:
                    console.print('[red][!] 请将需要提交的报名添加到个人记录中再运行程序[/red]')
            elif user_input.isdigit() and 0 < int(user_input) <= len(user_history):
                EnrollmentSubmitter(
                    user_history[int(user_input) - 1]['eid'], access_token, self.session).run()
                break
            else:
                console.print('[red][!] 请输入正确的序号[/red]')


if __name__ == '__main__':
    TokenRetriever().run()
    input('[!] 按回车退出...')
