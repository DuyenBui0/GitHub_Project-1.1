import os
import csv
import time
from datetime import datetime, timedelta

LOG_FILE = r"D:\A.log"
CSV_FILE = r"D:\B.csv"

# ---------------------------------------
# Ghi MAX của mỗi giờ vào B.csv
# ---------------------------------------
def save_hourly_max():

    if not os.path.exists(LOG_FILE):
        return

    hourly_data = {}

    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:

            for line in f:
                line = line.strip()

                if not line:
                    continue

                try:
                    parts = line.split(",")

                    if len(parts) < 3:
                        continue

                    timestamp = datetime.strptime(
                        parts[0],
                        "%Y-%m-%d %H:%M:%S"
                    )

                    value1 = float(parts[1])
                    value2 = float(parts[2])

                    # Gom theo giờ
                    hour = timestamp.replace(
                        minute=0,
                        second=0,
                        microsecond=0
                    )

                    if hour not in hourly_data:
                        hourly_data[hour] = [value1, value2]
                    else:
                        hourly_data[hour][0] = max(
                            hourly_data[hour][0],
                            value1
                        )

                        hourly_data[hour][1] = max(
                            hourly_data[hour][1],
                            value2
                        )

                except (ValueError, IndexError):
                    continue

        # Tạo file B.csv nếu chưa có
        file_exists = os.path.exists(CSV_FILE)

        with open(
            CSV_FILE,
            "a",
            newline="",
            encoding="utf-8"
        ) as f:

            writer = csv.writer(f)

            if not file_exists:
                writer.writerow([
                    "Hour",
                    "Max_Value_1",
                    "Max_Value_2"
                ])

            # Ghi theo thứ tự thời gian
            for hour in sorted(hourly_data):

                writer.writerow([
                    hour.strftime("%Y-%m-%d %H:00:00"),
                    hourly_data[hour][0],
                    hourly_data[hour][1]
                ])

    except Exception as e:
        print("Lỗi khi ghi B.csv:", e)


# ---------------------------------------
# Xóa các dòng cũ hơn 2 giờ
# ---------------------------------------
def delete_old_lines():

    if not os.path.exists(LOG_FILE):
        return

    cutoff_time = datetime.now() - timedelta(hours=2)

    temp_file = LOG_FILE + ".tmp"

    try:

        with open(
            LOG_FILE,
            "r",
            encoding="utf-8"
        ) as source, open(
            temp_file,
            "w",
            encoding="utf-8"
        ) as target:

            for line in source:

                try:
                    parts = line.strip().split(",")

                    if len(parts) < 3:
                        continue

                    timestamp = datetime.strptime(
                        parts[0],
                        "%Y-%m-%d %H:%M:%S"
                    )

                    # Chỉ giữ dòng trong vòng 2 giờ
                    if timestamp >= cutoff_time:
                        target.write(line)

                except ValueError:
                    # Nếu dòng không đúng format thì bỏ qua
                    continue

        # Thay A.log bằng file mới
        os.replace(temp_file, LOG_FILE)

        print(
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "-> Đã xóa dữ liệu quá 2 giờ"
        )

    except Exception as e:

        print("Lỗi khi xóa A.log:", e)

        if os.path.exists(temp_file):
            os.remove(temp_file)


# ---------------------------------------
# Chương trình chính
# ---------------------------------------
print("Monitoring A.log...")
print("Nhấn Ctrl+C để dừng.")

last_hour = datetime.now().replace(
    minute=0,
    second=0,
    microsecond=0
)

last_delete = time.time()

while True:

    try:

        now = datetime.now()

        # --------------------------------
        # Mỗi khi sang giờ mới:
        # ghi MAX của giờ trước
        # --------------------------------
        current_hour = now.replace(
            minute=0,
            second=0,
            microsecond=0
        )

        if current_hour > last_hour:

            print(
                now.strftime("%Y-%m-%d %H:%M:%S"),
                "-> Ghi MAX vào B.csv"
            )

            save_hourly_max()

            last_hour = current_hour

        # --------------------------------
        # Mỗi 2 giờ xóa A.log
        # --------------------------------
        if time.time() - last_delete >= 2 * 60 * 60:

            delete_old_lines()

            last_delete = time.time()

        time.sleep(10)

    except KeyboardInterrupt:

        print("\nĐã dừng chương trình.")
        break

    except Exception as e:

        print("Lỗi:", e)
        time.sleep(10)