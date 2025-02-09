import os
import time

import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options

from webdriver_manager.chrome import ChromeDriverManager

import json


def initialize_driver():
    """初始化driver"""
    options = Options()
    # options.add_argument("--headless")  # Ensure GUI is off
    # options.page_load_strategy = 'eager'
    caps = {
        "browserName": "chrome",
        'goog:loggingPrefs': {'performance': 'ALL'}  # Enable performance logging
    }

    for key, value in caps.items():
        options.set_capability(key, value)

    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    return driver


def filter_type(_type: str):
    """检查MIME类型是否在指定的排除类型列表中。"""
    types = [
        'application/json'
    ]
    return _type in types


def is_target_url(url: str, location):
    """验证url和api地址是否一致"""
    target_url = f"https://api.plugshare.com/v3/locations/{location}"

    return target_url == url


def extract_data_from_location_id(driver, location_id, state, city):
    url = f'https://www.plugshare.com/location/{location_id}'
    print(f"正在爬取: {url}")

    try:
        driver.set_page_load_timeout(20)  # 设置页面加载时间，超时没完成则捕获异常
        # driver.set_script_timeout(15)
        driver.get(url)
        time.sleep(8)
    except Exception as e:
        print(e)
        driver.execute_script('window.stop()')  # 手动停止页面加载
        print("超时，直接进入下一步")
    # try:
    #     # 等待某个已知的页面元素加载后才继续（例如页面特定元素）
    #     print("进入等待元素")
    #     WebDriverWait(driver, 20).until(
    #         EC.presence_of_element_located((By.CLASS_NAME, 'Chrome windows not_mobile'))
    #     )
    # except Exception as wait_exception:
    #     print(f"等待页面加载失败: {wait_exception}")

    performance_log = driver.get_log('performance')  # 获取performance日志

    # 在等待之后提取所需数据
    for packet in performance_log:

        message = json.loads(packet.get('message')).get('message')  # 获取消息数据
        if message.get('method') != 'Network.responseReceived':  # 只有在方法是 responseReceived 时才继续
            continue

        packet_type = message.get('params').get('response').get('mimeType')  # 获取响应类型
        url = message.get('params').get('response').get('url')  # 获取请求 URL

        # 检查响应是否为 application/json 且 URL 是否是正确的

        if filter_type(_type=packet_type) and is_target_url(url, location_id):

            request_id = message.get('params').get('requestId')  # 获取唯一的请求标识符

            try:
                resp = driver.execute_cdp_cmd('Network.getResponseBody', {'requestId': request_id})  # 获取响应主体
                print(f'类型: {packet_type} URL: {url}')
                print(f'响应: {resp}')
                print()
                response_data = json.dumps(resp, ensure_ascii=False)  # 将响应数据转换为字符串
                # 定义文件夹路径
                directory = f"{state}"

                # 如果文件夹不存在，则创建该文件夹
                if not os.path.exists(directory):
                    os.makedirs(directory)

                # 构建文件名
                file_name = os.path.join(directory, f"{state}_{city}_{location_id}.txt")

                # 保存响应数据
                with open(file_name, 'w', encoding='utf-8') as f:
                    f.write(response_data)

                print(f'保存成功: {file_name}')
            except WebDriverException:
                pass


def main():
    driver = initialize_driver()
    # driver.get('https://www.plugshare.com/')
    # time.sleep(25)
    try:
        df = pd.read_excel('california.xlsx')

        for _, row in df.iterrows():
            state = row['state']
            city = row['city']
            location_id = row['locationID']
            extract_data_from_location_id(driver, location_id, state, city)

    finally:
        driver.quit()


if __name__ == '__main__':
    main()
