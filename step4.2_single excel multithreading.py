# import os
# import time
# import pandas as pd
# from selenium import webdriver
# from selenium.common.exceptions import WebDriverException
# from selenium.webdriver.chrome.service import Service as ChromeService
# from selenium.webdriver.chrome.options import Options
# from webdriver_manager.chrome import ChromeDriverManager
# import json
# from concurrent.futures import ThreadPoolExecutor, as_completed
#
#
# def initialize_driver():
#     """初始化webdriver实例"""
#     options = Options()
#     # options.add_argument("--headless")  # 确保无图形界面显示
#
#     caps = {
#         "browserName": "chrome",
#         'goog:loggingPrefs': {'performance': 'ALL'}  # 启用性能日志
#     }
#
#     for key, value in caps.items():
#         options.set_capability(key, value)
#
#     driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
#     driver.set_window_size(200, 200)
#     return driver
#
#
# def filter_type(_type: str):
#     """检查MIME类型是否在指定的排除类型列表中。"""
#     types = [
#         'application/json'
#     ]
#     return _type in types
#
#
# def is_target_url(url: str, location):
#     """验证url和api地址是否一致"""
#     target_url = f"https://api.plugshare.com/v3/locations/{location}"
#     return target_url == url
#
#
# def extract_data_from_location_id(driver, location_id, state, city):
#     url = f'https://www.plugshare.com/location/{location_id}'
#     print(f"正在爬取: {url}")
#
#     try:
#         driver.set_page_load_timeout(20)  # 设置页面加载超时时间
#         driver.get(url)
#         time.sleep(8)  # 等待页面加载
#     except Exception as e:
#         driver.execute_script('window.stop()')  # 手动停止页面加载
#         print("超时，直接进入下一步")
#
#     performance_log = driver.get_log('performance')  # 获取性能日志
#
#     for packet in performance_log:
#         message = json.loads(packet.get('message')).get('message')
#         if message.get('method') != 'Network.responseReceived':
#             continue
#
#         packet_type = message.get('params').get('response').get('mimeType')
#         url = message.get('params').get('response').get('url')
#
#         if filter_type(_type=packet_type) and is_target_url(url, location_id):
#             request_id = message.get('params').get('requestId')
#
#             try:
#                 resp = driver.execute_cdp_cmd('Network.getResponseBody', {'requestId': request_id})
#                 # print(f'类型: {packet_type} URL: {url} 响应: {resp}')
#                 response_data = json.dumps(resp, ensure_ascii=False)
#
#                 # 为响应数据创建并保存文件
#                 directory = f"{state}"
#                 if not os.path.exists(directory):
#                     os.makedirs(directory)
#                 file_name = os.path.join(directory, f"{state}_{city}_{location_id}.txt")
#                 with open(file_name, 'w', encoding='utf-8') as f:
#                     f.write(response_data)
#                 print(f'保存成功: {file_name}')
#             except WebDriverException as e:
#                 print(f'获取响应失败: {e}')
#
#
#
# def split_dataframe(df, batch_size):
#     """将 DataFrame 按行分割成若干部分，每部分指定大小"""
#     return [df[i:i + batch_size] for i in range(0, df.shape[0], batch_size)]
#
#
# def process_batch(batch):
#     """处理一批数据中的所有位置ID"""
#     driver = initialize_driver()  # 每个线程初始化独立的 WebDriver
#     try:
#         for _, row in batch.iterrows():
#             state = row['state']
#             city = row['city']
#             location_id = row['locationID']
#             extract_data_from_location_id(driver, location_id, state, city)
#     finally:
#         driver.quit()  # 在处理完这一批后关闭 WebDriver
#
#
# def process_excel_file(excel_file):
#     """从Excel文件中提取数据并执行爬取"""
#     df = pd.read_excel(excel_file)  # 读取Excel文件
#     batches = split_dataframe(df, 10)  # 每十条数据分为一组
#
#     # 可以调整 max_workers 的值来设置最大线程数
#     max_threads = 5  # 设置最大线程数
#     with ThreadPoolExecutor(max_workers=max_threads) as executor:
#         futures = {executor.submit(process_batch, batch): idx for idx, batch in enumerate(batches)}
#         for future in as_completed(futures):
#             try:
#                 future.result()  # 等待线程完成
#                 print(f"已完成爬取批次: {futures[future]}")
#             except Exception as exc:
#                 print(f"批次 {futures[future]} 生成了一个异常: {exc}")
#
#
# def main():
#     # 指定要处理的 Excel 文件
#     excel_file = 'california.xlsx'  # 直接指向的 Excel 文件
#     process_excel_file(excel_file)  # 处理指定的 Excel 文件
#
#
# if __name__ == '__main__':
#     main()


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
from tqdm import tqdm


def initialize_driver():
    """初始化webdriver实例"""
    options = Options()
    # options.add_argument("--headless")  # 确保无图形界面显示

    caps = {
        "browserName": "chrome",
        'goog:loggingPrefs': {'performance': 'ALL'}  # 启用性能日志
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


def extract_data_from_location_id(driver, location_id, state, city, progress_bar):
    url = f'https://www.plugshare.com/location/{location_id}'
    print(f"正在爬取: {url}")

    try:
        driver.set_page_load_timeout(20)  # 设置页面加载超时时间
        driver.get(url)
        time.sleep(8)  # 等待页面加载
    except Exception as e:
        driver.execute_script('window.stop()')  # 手动停止页面加载
        print("超时，直接进入下一步")

    performance_log = driver.get_log('performance')  # 获取性能日志

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
                response_data = json.dumps(resp, ensure_ascii=False)

                # 为响应数据创建并保存文件
                directory = f"{state}"
                if not os.path.exists(directory):
                    os.makedirs(directory)
                file_name = os.path.join(directory, f"{state}_{city}_{location_id}.txt")
                with open(file_name, 'w', encoding='utf-8') as f:
                    f.write(response_data)
                print(f'保存成功: {file_name}')

                # 更新进度条
                progress_bar.update(1)
            except WebDriverException as e:
                print(f'获取响应失败: {e}')


def split_dataframe(df, batch_size):
    """将 DataFrame 按行分割成若干部分，每部分指定大小"""
    return [df[i:i + batch_size] for i in range(0, df.shape[0], batch_size)]


def process_batch(batch, progress_bar):
    """处理一批数据中的所有位置ID"""
    driver = initialize_driver()  # 每个线程初始化独立的 WebDriver
    try:
        for _, row in batch.iterrows():
            state = row['state']
            city = row['city']
            location_id = row['locationID']
            extract_data_from_location_id(driver, location_id, state, city, progress_bar)
    finally:
        driver.quit()  # 在处理完这一批后关闭 WebDriver


def process_excel_file(excel_file):
    """从Excel文件中提取数据并执行爬取"""
    df = pd.read_excel(excel_file)  # 读取Excel文件
    batches = split_dataframe(df, 100)  # 每十条数据分为一组

    # 初始化进度条
    with tqdm(total=len(df)) as progress_bar:
        # 可以调整 max_workers 的值来设置最大线程数
        max_threads = 1  # 设置最大线程数
        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            futures = {executor.submit(process_batch, batch, progress_bar): idx for idx, batch in enumerate(batches)}
            for future in as_completed(futures):
                try:
                    future.result()  # 等待线程完成
                    print(f"已完成爬取批次: {futures[future]}")
                except Exception as exc:
                    print(f"批次 {futures[future]} 生成了一个异常: {exc}")


def main():
    # 指定要处理的 Excel 文件
    excel_file = 'all_missing.xlsx'  # 直接指向的 Excel 文件
    process_excel_file(excel_file)  # 处理指定的 Excel 文件


if __name__ == '__main__':
    main()
