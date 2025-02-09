import os
import json
import pandas as pd

# 文件夹路径
folder_path = 'all_response'


# 初始化用于存储结果的字典，键为州的名称
state_data = {}

# 初始化计数器以统计locationID的总数
total_location_ids = 0

# 遍历文件夹中的每一个txt文件
for file_name in os.listdir(folder_path):
    if file_name.endswith('.txt'):
        # 提取文件名中的州和城市
        parts = file_name[:-4].split('_')
        state = parts[0].lower()
        city = parts[1].lower()

        # 打开并读取JSON内容
        with open(os.path.join(folder_path, file_name), 'r') as file:
            content = file.read()
            # 提取json部分，从 "body" 键中解析
            json_data = json.loads(content)['body']
            locations = json.loads(json_data)
            # 使用集合来跟踪已见过的locationID，以便去重
            seen_location_ids = set()
            # 从每个位置提取url中的locationID
            for location in locations:
                if 'url' in location:
                    # 提取数字ID通过拆分URL
                    location_id = location['url'].split('/')[-1]
                    # 仅当未见过locationID时才添加
                    if location_id not in seen_location_ids:
                        seen_location_ids.add(location_id)
                        # 如果该州还没有在字典中，初始化
                        if state not in state_data:
                            state_data[state] = []
                        # 添加州、城市和locationID到列表中
                        state_data[state].append({'state': state, 'city': city, 'locationID': location_id})
                        # 增加计数器
                        total_location_ids += 1

# 为每个州创建一个DataFrame，并写入一个单独的Excel表格
for state, data in state_data.items():
    df = pd.DataFrame(data)
    # 生成Excel文件路径
    output_path = os.path.join('output_directory', f'{state}.xlsx')
    # 确保输出目录存在
    os.makedirs('output_directory', exist_ok=True)
    # 写入Excel
    df.to_excel(output_path, index=False)

print(f"Excel文件已生成，总共解析出 {total_location_ids} 个唯一的locationID。")
