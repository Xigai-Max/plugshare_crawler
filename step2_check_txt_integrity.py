import os
import pandas as pd

# 文件夹路径和Excel路径
folder_path = '/all_response'
excel_path = 'state_cities_all.xlsx'

output_path = 'missing_files.xlsx'

# 读取Excel文件
df = pd.read_excel(excel_path)

# 获取Excel中的State_City组合
state_city_list = df.apply(lambda row: f"{row['State']}_{row['City']}.txt", axis=1).tolist()

# 获取文件夹中的txt文件名
file_list = [f for f in os.listdir(folder_path) if f.endswith('.txt')]

# 找出缺少的txt文件
missing_files = [f for f in state_city_list if f not in file_list]

# 将缺少的文件形成新的DataFrame，移除.txt扩展名
missing_df = pd.DataFrame([file[:-4].split('_') for file in missing_files], columns=['State', 'City'])

# 保存缺少文件的信息到新的Excel文件中
missing_df.to_excel(output_path, index=False)

print(f"缺少的文件信息已保存到 {output_path}。")
