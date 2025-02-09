import os
import pandas as pd


def find_missing_files(states_folder, output_folder):
    # 确保输出文件夹存在
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    total_missing = 0
    # 遍历每个州的Excel文件
    for state_file in os.listdir(states_folder):
        if state_file.endswith('.xlsx'):
            state_name = state_file[:-5]  # 去掉文件名的.xlsx后缀
            excel_path = os.path.join(states_folder, state_file)
            txt_folder = f'{state_name}'
            # 读取Excel文件
            df = pd.read_excel(excel_path)

            # 获取州名、城市名和locationID
            missing_location_ids = []

            for index, row in df.iterrows():
                city = row['city']
                location_id = row['locationID']
                # 构建txt文件名
                txt_file_name = f"{state_name}_{city}_{location_id}.txt"
                txt_file_path = os.path.join(txt_folder, txt_file_name)

                # 检查txt文件是否存在
                if not os.path.isfile(txt_file_path):
                    missing_location_ids.append({
                        'state': state_name,
                        'city': city,
                        'locationID': location_id
                    })
                    total_missing += 1

            # 保存缺失的locationID到新的Excel文件
            if missing_location_ids:
                missing_df = pd.DataFrame(missing_location_ids)
                missing_excel_path = os.path.join(output_folder, f"{state_name}.xlsx")
                missing_df.to_excel(missing_excel_path, index=False)
    print(f'缺少{total_missing}个location')

# 使用示例
states_folder = 'all_location_id'  # 替换为州Excel文件的路径

output_folder = 'all_missing'  # 替换为输出缺失文件的Excel的路径

find_missing_files(states_folder, output_folder)