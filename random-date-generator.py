from datetime import datetime, timedelta
import random
import uuid

def generate_uuid():
    return uuid.uuid4()

def random_date(start_year=2024, end_year=2024):
    # 시작일과 종료일 설정
    start_date = datetime(start_year, 1, 1)
    end_date = datetime(end_year, 3, 31)
    
    # 두 날짜 사이의 일수 계산
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    
    # 랜덤한 일수 선택
    random_number_of_days = random.randint(0, days_between_dates)
    
    # 랜덤 날짜 생성
    random_date = start_date + timedelta(days=random_number_of_days)
    
    return random_date

def format_date(date, format_string="%Y-%m-%d"):
    return date.strftime(format_string)

# 예시 사용
if __name__ == "__main__":
    # 여러 개의 랜덤 날짜 생성
    install_date = random_date()
    myuuid = generate_uuid()
    for i in range(random.randint(1, 100)):
        # 다양한 형식으로 출력
        next_day = install_date + timedelta(i)
        print(f"{myuuid},{format_date(install_date)},{format_date(next_day)},{i}")
