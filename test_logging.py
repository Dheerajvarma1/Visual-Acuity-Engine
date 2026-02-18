import csv
import os
from datetime import datetime

def test_logging():
    log_file = 'acuity_logs.csv'
    # Delete if exists to start fresh
    if os.path.exists(log_file):
        os.remove(log_file)
        
    def log_response(acuity, true_ori, user_resp):
        file_exists = os.path.isfile(log_file)
        result = "Correct" if true_ori == user_resp else "Incorrect"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(log_file, 'a', newline='') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(['Timestamp', 'Acuity Level', 'True Orientation', 'User Response', 'Result'])
            writer.writerow([timestamp, acuity, true_ori, user_resp, result])

    log_response('6/6', 'Up', 'Up')
    log_response('6/60', 'Left', 'Right')
    
    if os.path.exists(log_file):
        print(f"Log file {log_file} created.")
        with open(log_file, 'r') as f:
            print(f.read())
    else:
        print("Log file NOT created.")

if __name__ == "__main__":
    test_logging()
