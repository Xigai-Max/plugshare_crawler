# from _datetime import datetime
# import json
#
#
# def get_all_info(json_file):
#     def format_timestamp_to_ymd(timestamp):
#         dt = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
#         return dt.strftime("%Y-%m-%d")
#     charger_type_dict = {}
#     with open(json_file, 'r', encoding='utf-8') as f:
#         json_data = json.load(f)
#         body = json_data['body']
#         charger_name = body['name']
#         location = body['address']
#         score = body['score']
#         stations = body['stations']
#         operators = []
#         for station in stations:
#             network = station.get('network')
#
#             try:
#                 operator = network.get('name')
#             except KeyError:
#                 operator = 'null'
#             operators.append(operator)
#
#         operators = list(set(operators))
#         for station in stations:
#             outlets = station['outlets']
#             for outlet in outlets:
#                 connector_type = outlet.get('connector_type')
#                 connector_name = outlet.get('connector_name')
#                 if connector_type not in charger_type_dict:
#                     charger_type_dict[connector_type] = connector_name
#
#
#         print('站点名', charger_name)
#         print('地址', location)
#         print('评分', score)
#         print(f'运营商', operators)
#
#
#         reviews = body['reviews']
#         for review in reviews:
#             try:
#                 username = review['user'].get('display_name')
#             except KeyError:
#                 username = 'null'
#             try:
#                 comment = review['comment']
#             except KeyError:
#                 comment = 'null'
#             try:
#                 checkin_type = review['rating']
#             except KeyError:
#                 checkin_type = 'null'
#             try:
#                 time = format_timestamp_to_ymd(review['created_at'])
#             except KeyError:
#                 time = 'null'
#             try:
#                 vehicle = review['vehicle_name']
#             except KeyError:
#                 vehicle = 'null'
#             try:
#                 charger_power = review['kilowatts']
#             except KeyError:
#                 charger_power = 'null'
#
#             try:
#                 charger_type = charger_type_dict.get(review['connector_type'])
#             except KeyError:
#                 charger_type = 'null'
#
#             try:
#                 problem_num = review['problem']
#                 if problem_num != 0:
#                     problem = review['problem_description']
#                 else:
#                     problem = 'null'
#             except KeyError:
#
#                 problem = 'null'
#
#             print('用户名', username)
#             print('车辆类型', vehicle)
#             print('充电器类型', charger_type)
#             print('功率', charger_power)
#             print('评价', checkin_type)
#             print('评论', comment)
#             print('问题反馈', problem)
#
#             print('发布时间', time)
#
#
# json_file = r'all_json\california_san-diego_245918.json'
# get_all_info(json_file)

import os
import csv
import json
from datetime import datetime
from tqdm import tqdm


def format_timestamp_to_ymd(timestamp):
    dt = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
    return dt.strftime("%Y-%m-%d")


def get_all_info(json_file, output_csv):
    charger_type_dict = {}
    with open(json_file, 'r', encoding='utf-8') as f:
        json_data = json.load(f)
        body = json_data['body']
        try:
            charger_name = body['name']
        except KeyError:
            charger_name = 'null'
        try:
            location = body['address']
        except KeyError:
            location = 'null'
        try:
            score = body['score']
        except KeyError:
            score = 'null'
        try:
            stations = body['stations']
        except KeyError:
            stations = []
        operators = []

        for station in stations:
            try:
                network = station.get('network')
                try:
                    operator = network.get('name') if network else None
                except KeyError:
                    operator = 'null'
                operators.append(operator)
            except KeyError:
                operator = 'null'
        operators = [operator if operator is not None else 'null' for operator in set(operators)]
        for station in stations:
            outlets = station['outlets']
            for outlet in outlets:
                connector_type = outlet.get('connector_type')
                connector_name = outlet.get('connector_name')
                if connector_type not in charger_type_dict:
                    charger_type_dict[connector_type] = connector_name

        reviews = body['reviews']
        rows = []
        if not reviews:
            rows.append(
                [charger_name, location, score, ','.join(operators), 'null', 'null', 'null', 'null', 'null', 'null',
                 'null', 'null'])
        for review in reviews:
            try:
                username = review['user'].get('display_name')
            except KeyError:
                username = None
            try:
                comment = review['comment']
            except KeyError:
                comment = None
            try:
                checkin_type = review['rating']
            except KeyError:
                checkin_type = None
            try:
                time = format_timestamp_to_ymd(review['created_at'])
            except KeyError:
                time = None
            try:
                vehicle = review['vehicle_name']
            except KeyError:
                vehicle = None
            try:
                charger_power = review['kilowatts']
            except KeyError:
                charger_power = None
            try:
                charger_type = charger_type_dict.get(review['connector_type'])
            except KeyError:
                charger_type = None
            try:
                problem_num = review['problem']
                if problem_num != 0:
                    problem = review['problem_description'] if 'problem_description' != 'null' else None
                else:
                    problem = None
            except KeyError:
                problem = None

            rows.append([charger_name, location, score, ','.join(operators), username, vehicle, charger_type,
                         charger_power, checkin_type, comment, problem, time])

        # 保存到CSV文件
        with open(output_csv, mode='w', newline='', encoding='utf-8-sig') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(["charger name", "location", "score", "operator", "username", "vehicle",
                             "charger type", "charger power", "checkin type", "comment", "problem", "time"])
            writer.writerows(rows)


def main():
    input_folder = 'all_json'  # JSON 文件的目录
    json_files = []
    for root, _, files in os.walk(input_folder):
        for file in files:
            if file.endswith('.json'):
                json_files.append(os.path.join(root, file))

    for json_file in tqdm(json_files, desc="Processing JSON files"):

        parts = os.path.basename(json_file).replace('.json', '').split('_')
        if len(parts) >= 2:
            state = parts[0]
            city = parts[1]
            output_dir = os.path.join(input_folder, state)
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            output_csv = os.path.join(output_dir, os.path.basename(json_file).replace('.json', '.csv'))
            get_all_info(json_file, output_csv)


if __name__ == "__main__":
    main()
