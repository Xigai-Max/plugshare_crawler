import os
import json


def convert_txt_to_json(root_directory, output_directory):
    # 创建输出目录（如果不存在）
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # 遍历目录及其子目录
    for dirpath, dirnames, filenames in os.walk(root_directory):
        for filename in filenames:
            # 检查文件扩展名是否为.txt
            if filename.endswith('.txt'):
                txt_file_path = os.path.join(dirpath, filename)
                json_file_path = os.path.join(output_directory, filename[:-4] + '.json')  # 输出到 all_json 文件夹

                try:
                    # 打开并读取TXT文件内容
                    with open(txt_file_path, 'r', encoding='utf-8') as txt_file:
                        content = txt_file.read()
                        # 将内容转换为JSON对象
                        json_data = json.loads(content)

                        # 将 body 的内容解码为 JSON 对象
                        body_json = json.loads(json_data['body'])

                        # 创建输出字典，包含 base64Encoded 字段
                        output_data = {
                            "base64Encoded": json_data["base64Encoded"],
                            "body": body_json
                        }

                    # 写入JSON文件到输出目录
                    with open(json_file_path, 'w', encoding='utf-8') as json_file:
                        json.dump(output_data, json_file, ensure_ascii=False, indent=4)

                    print(f"Converted: {txt_file_path} to {json_file_path}")

                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON from file {txt_file_path}: {e}")
                except Exception as e:
                    print(f"Error processing file {txt_file_path}: {e}")


# 使用程序
directory_to_convert = 'all_location_txt'  # 源文件夹路径
output_directory = 'all_json'  # 输出文件夹路径
convert_txt_to_json(directory_to_convert, output_directory)
