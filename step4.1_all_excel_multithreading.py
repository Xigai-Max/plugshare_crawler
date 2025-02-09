import os
import time
import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import json
from concurrent.futures import ThreadPoolExecutor, as_completed


def initialize_driver():
    """初始化driver"""
    options = Options()
    # options.add_argument("--headless")  # Ensure GUI is off
    caps = {
        "browserName": "chrome",
        'goog:loggingPrefs': {'performance': 'ALL'}  # Enable performance logging
    }

    for key, value in caps.items():
        options.set_capability(key, value)
    service = ChromeService('chrome_driver/chromedriver.exe')
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_window_size(200, 200)
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
        driver.get(url)
        time.sleep(8)  # Allow time for the page to load
    except Exception as e:

        driver.execute_script('window.stop()')  # 手动停止页面加载
        print("超时，直接进入下一步")

    performance_log = driver.get_log('performance')  # 获取performance日志

    for packet in performance_log:
        message = json.loads(packet.get('message')).get('message')
        if message.get('method') != 'Network.responseReceived':
            continue

        packet_type = message.get('params').get('response').get('mimeType')
        url = message.get('params').get('response').get('url')

        if filter_type(_type=packet_type) and is_target_url(url, location_id):
            request_id = message.get('params').get('requestId')

            try:
                resp = driver.execute_cdp_cmd('Network.getResponseBody', {'requestId': request_id})
                # print(f'类型: {packet_type} URL: {url}')
                # print(f'响应: {resp}')
                response_data = json.dumps(resp, ensure_ascii=False)

                # 为响应数据创建并保存文件
                directory = f"{state}"
                if not os.path.exists(directory):
                    os.makedirs(directory)
                file_name = os.path.join(directory, f"{state}_{city}_{location_id}.txt")
                with open(file_name, 'w', encoding='utf-8') as f:
                    f.write(response_data)
                print(f'保存成功: {file_name}')
            except WebDriverException:
                pass


def process_excel_file(excel_file):
    """从Excel文件中提取数据并执行爬取"""
    driver = initialize_driver()
    try:
        df = pd.read_excel(excel_file)
        for _, row in df.iterrows():
            state = row['state']
            city = row['city']
            location_id = row['locationID']
            extract_data_from_location_id(driver, location_id, state, city)
    finally:
        driver.quit()


def main():
    # 获取所有Excel文件路径

    excel_files = [os.path.join(all_location_ids_folder, f) for f in os.listdir(all_location_ids_folder) if
                   f.endswith('.xlsx')]

    # 使用多线程进行爬取
    max_threads = 5  # 设置最大线程数
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = {executor.submit(process_excel_file, excel_file): excel_file for excel_file in excel_files}
        for future in as_completed(futures):
            try:
                future.result()  # 捕获线程中的异常
                print(f"已完成爬取: {futures[future]}")
            except Exception as exc:
                print(f"{futures[future]} 生成了一个异常: {exc}")


if __name__ == '__main__':
    all_location_ids_folder = 'all_missing'
    main()

#  可以在爬取过程中记录通过已经爬取到txt的id验证当前id是否需要爬取
