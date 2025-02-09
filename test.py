import os
import csv

def count_total_rows(csv_folder):
    total_rows = 0
    for root, _, files in os.walk(csv_folder):
        for file in files:
            if file.endswith('.csv'):
                csv_file = os.path.join(root, file)
                with open(csv_file, 'r', encoding='utf-8-sig') as f:
                    reader = csv.reader(f)
                    next(reader)  # Skip the header
                    total_rows += sum(1 for row in reader)
    return total_rows

def main():
    csv_folder = 'all_json'  # CSV 文件所在的目录
    total_rows = count_total_rows(csv_folder)
    print(f'Total rows (excluding headers): {total_rows}')

if __name__ == "__main__":
    main()
