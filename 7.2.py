import csv
import json
from datetime import datetime

def format_timestamp_to_ymd(timestamp):
    dt = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
    return dt.strftime("%Y-%m-%d")

def get_all_info(json_file, output_csv):
    charger_type_dict = {}
    with open(json_file, 'r', encoding='utf-8') as f:
        json_data = json.load(f)
        body = json_data.get('body', {})
        charger_name = body.get('name', 'null')
        location = body.get('address', 'null')
        score = body.get('score', 'null')

        stations = body.get('stations', [])
        print(stations)
        operators = []

        for station in stations:
            network = station.get('network')
            operator = network.get('name') if network else 'null'
            operators.append(operator)
        operators = [operator if operator is not None else 'null' for operator in set(operators)]
        for station in stations:
            outlets = station.get('outlets', [])
            for outlet in outlets:
                connector_type = outlet.get('connector_type')
                connector_name = outlet.get('connector_name')
                if connector_type not in charger_type_dict:
                    charger_type_dict[connector_type] = connector_name

        reviews = body.get('reviews', [])
        print(reviews)
        rows = []
        for review in reviews:
            username = review.get('user', {}).get('display_name', 'null')
            comment = review.get('comment', 'null')
            checkin_type = review.get('rating', 'null')
            time = format_timestamp_to_ymd(review.get('created_at', 'null')) if review.get('created_at') else 'null'
            vehicle = review.get('vehicle_name', 'null')
            charger_power = review.get('kilowatts', 'null')
            charger_type = charger_type_dict.get(review.get('connector_type'), 'null')
            problem_num = review.get('problem', 0)
            problem = review.get('problem_description', 'null') if problem_num != 0 else 'null'

            print(username, comment, time, vehicle, charger_power)

            rows.append([charger_name, location, score, ','.join(operators), username, vehicle, charger_type,
                         charger_power, checkin_type, comment, problem, time])


        # 保存到CSV文件
        with open(output_csv, mode='w', newline='', encoding='utf-8-sig') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(["charger name", "location", "score", "operator", "username", "vehicle",
                             "charger type", "charger power", "checkin type", "comment", "problem", "time"])
            writer.writerows(rows)

if __name__ == "__main__":
    json_file = 'all_json/idaho_blackfoot_264824.json'  # 需要解析的 JSON 文件路径
    output_csv = 'output.csv'  # 输出的 CSV 文件路径
    get_all_info(json_file, output_csv)
