# import time
# from selenium.common import WebDriverException
# from selenium.webdriver.chrome.service import Service as ChromeService
# from selenium.webdriver.chrome.options import Options
# from webdriver_manager.chrome import ChromeDriverManager
# import json
# from selenium import webdriver
#
#
# def filter_type(_type: str):
#     """Check if the MIME type is not in the specified list of excluded types."""
#     types = [
#         'application/javascript', 'application/x-javascript', 'application/octet-stream'
#     ]
#     return _type not in types
#
#
# def is_target_url(url: str):
#     """Check if the URL matches the one you are interested in."""
#     target_url = "https://api.plugshare.com/v3/locations/region"
#     return target_url in url
#
#
# # Initialize the Chrome driver
# options = Options()
#
# caps = {
#     "browserName": "chrome",
#     'goog:loggingPrefs': {'performance': 'ALL'}  # Enable performance logging
# }
#
# # Add capabilities to options
# for key, value in caps.items():
#     options.set_capability(key, value)
#
# # Launch browser
# driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
#
# try:
#     # Access the target page
#     driver.get('https://www.plugshare.com/directory/us/alaska/fairbanks')  # Replace with your target URL
#
#     # Retrieve and process performance logs to find specific request and get response
#     performance_log = driver.get_log('performance')  # Get logs with name 'performance'
#
#     for packet in performance_log:
#         message = json.loads(packet.get('message')).get('message')  # Get the message data
#         if message.get('method') != 'Network.responseReceived':  # Continue only if method is responseReceived
#             continue
#
#         packet_type = message.get('params').get('response').get('mimeType')  # Get response type
#         url = message.get('params').get('response').get('url')  # Get request URL
#
#         # Check if the response is JSON and the URL is the one we're interested in
#         if filter_type(_type=packet_type) and is_target_url(url):
#             requestId = message.get('params').get('requestId')  # Get unique request identifier
#
#             try:
#                 resp = driver.execute_cdp_cmd('Network.getResponseBody', {'requestId': requestId})  # Get response body
#                 print(f'type: {packet_type} url: {url}')
#                 print(f'response: {resp}')
#                 print()
#             except WebDriverException:
#                 pass
#
# except Exception as e:
#     print(e)
# finally:
#     driver.quit()
#
import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
import json


def filter_type(_type: str):
    """Check if the MIME type is not in the specified list of excluded types."""
    types = [
        'application/javascript', 'application/x-javascript', 'application/octet-stream'
    ]
    return _type not in types


def is_target_url(url: str):
    """Check if the URL matches the one you are interested in."""
    target_url = "https://api.plugshare.com/v3/locations/region"
    return target_url in url


def initialize_driver():
    """Initialize a Chrome driver once for use across multiple page visits."""
    options = Options()
    # options.add_argument("--headless")  # Ensure GUI is off

    caps = {
        "browserName": "chrome",
        'goog:loggingPrefs': {'performance': 'ALL'}  # Enable performance logging
    }

    # Add capabilities to options
    for key, value in caps.items():
        options.set_capability(key, value)

    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    return driver


def extract_data_from_city(driver, state: str, city: str):
    """提取并处理指定州和城市的数据，并将其保存到文本文件中。"""
    try:
        # 构建目标 URL
        url = f'https://www.plugshare.com/directory/us/{state.lower()}/{city.lower()}'
        print(f"Processing: {url}")
        driver.get(url)

        # 等待网络请求通过等待页面中特定条件/元素的完成
        try:
            # 等待某个已知的页面元素加载后才继续（例如页面特定元素）
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.ID, 'some_element_id'))  # 示例条件，需替换为实际元素
            )
        except Exception as wait_exception:
            print(f"等待页面加载失败: {wait_exception}")

        performance_log = driver.get_log('performance')  # 获取名为 'performance' 的日志

        # 在等待之后提取所需数据
        for packet in performance_log:
            message = json.loads(packet.get('message')).get('message')  # 获取消息数据
            if message.get('method') != 'Network.responseReceived':  # 只有在方法是 responseReceived 时才继续
                continue

            packet_type = message.get('params').get('response').get('mimeType')  # 获取响应类型
            url = message.get('params').get('response').get('url')  # 获取请求 URL

            # 检查响应是否为 JSON 且 URL 是否是我们感兴趣的
            if filter_type(_type=packet_type) and is_target_url(url):
                requestId = message.get('params').get('requestId')  # 获取唯一的请求标识符

                try:
                    resp = driver.execute_cdp_cmd('Network.getResponseBody', {'requestId': requestId})  # 获取响应主体
                    print(f'类型: {packet_type} URL: {url}')
                    print(f'响应: {resp}')
                    print()
                    response_data = json.dumps(resp, ensure_ascii=False)  # 将响应数据转换为字符串
                    file_name = f"{state}_{city}.txt"
                    with open(file_name, 'w', encoding='utf-8') as f:
                        f.write(response_data)
                except WebDriverException:
                    pass

    except Exception as e:
        print(f"处理 {city}, {state} 时出错: {e}")

def main():
    # Initialize the driver
    driver = initialize_driver()

    try:
        # Read the Excel file containing states and cities
        df = pd.read_excel('state_cities_all.xlsx')  # Ensure this file is in the correct path
        # df = pd.read_excel('missing_files.xlsx')  # Ensure this file is in the correct path

        # Iterate over each row in the DataFrame
        for _, row in df.iterrows():
            state = row['State']
            city = row['City']
            extract_data_from_city(driver, state=state, city=city)

    finally:
        driver.quit()


if __name__ == "__main__":
    main()
