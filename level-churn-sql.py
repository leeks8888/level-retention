import sqlite3
import pandas as pd
import csv

def create_database(db_name, csv_file):
    """
    CSV 파일을 읽어서 SQLite 데이터베이스를 생성하고 데이터를 입력하는 함수
    """
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    # 테이블 생성
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS game_logs (
        userid TEXT,
        install_date DATE,
        play_date DATE,
        level_cleared INTEGER
    )
    ''')
    
    # CSV 파일 읽어서 데이터베이스에 입력
    with open(csv_file, 'r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            cursor.execute('''
            INSERT INTO game_logs (userid, install_date, play_date, level_cleared)
            VALUES (?, ?, ?, ?)
            ''', (row['userid'], row['install_date'], row['play_date'], row['level_cleared']))
    
    conn.commit()
    return conn

def analyze_level_churn(conn):
    """
    레벨별 이탈율을 분석하는 함수
    """
    cursor = conn.cursor()
    
    # 레벨별 이탈율 분석을 위한 SQL 쿼리
    query = '''
    WITH user_max_level AS (
        -- 유저별 최대 레벨
        SELECT 
            userid, 
            MAX(level_cleared) as max_level
        FROM game_logs
        GROUP BY userid
    ),
    level_stats AS (
        WITH user_max_levels AS (
            SELECT 
                userid,
                MAX(level_cleared) as max_level
            FROM game_logs
            GROUP BY userid
        ),
        level_counts AS (
            SELECT 
                max_level as level,
                COUNT(*) as user_count
            FROM user_max_levels
            GROUP BY max_level
        ),
        running_totals AS (
            SELECT 
                level,
                SUM(user_count) OVER (ORDER BY level DESC) as users_reached
            FROM level_counts
        )
        SELECT 
            level,
            users_reached
        FROM running_totals
        ORDER BY level
    ),
    stopped_users AS (
        -- 각 레벨에서 멈춘 유저 수
        SELECT 
            max_level as level,
            COUNT(*) as users_stopped
        FROM user_max_level
        GROUP BY max_level
    )
    SELECT 
        ls.level,
        ls.users_reached as total_users_reached,
        COALESCE(su.users_stopped, 0) as users_stopped,
        ROUND(CAST(COALESCE(su.users_stopped, 0) AS FLOAT) / ls.users_reached * 100, 2) as churn_rate,
        ROUND(100 - (CAST(COALESCE(su.users_stopped, 0) AS FLOAT) / ls.users_reached * 100), 2) as retention_rate,
        ROUND(CAST(LEAD(ls.users_reached) OVER (ORDER BY ls.level) AS FLOAT) / ls.users_reached * 100, 2) as progression_rate
    FROM level_stats ls
    LEFT JOIN stopped_users su ON ls.level = su.level
    ORDER BY ls.level;
    '''
    
    cursor.execute(query)
    results = cursor.fetchall()
    
    # 결과를 DataFrame으로 변환
    df = pd.DataFrame(results, columns=[
        'level', 'total_users_reached', 'users_stopped', 
        'churn_rate', 'retention_rate', 'progression_rate'
    ])
    
    return df

def get_additional_insights(conn):
    """
    추가적인 인사이트를 얻기 위한 함수
    """
    cursor = conn.cursor()
    
    # 평균 레벨 진행 시간 분석
    level_time_query = '''
    WITH level_times AS (
        SELECT 
            userid,
            level_cleared as level,
            MIN(play_date) as level_start_date
        FROM game_logs
        GROUP BY userid, level_cleared
    )
    SELECT 
        t1.level,
        ROUND(AVG(JULIANDAY(t2.level_start_date) - JULIANDAY(t1.level_start_date)), 1) as avg_days_to_complete
    FROM level_times t1
    JOIN level_times t2 ON t1.userid = t2.userid AND t2.level = t1.level + 1
    GROUP BY t1.level
    ORDER BY t1.level;
    '''
    
    cursor.execute(level_time_query)
    level_time_results = cursor.fetchall()
    
    level_time_df = pd.DataFrame(level_time_results, columns=['level', 'avg_days_to_complete'])
    
    return level_time_df

def main():
    # 데이터베이스 생성 및 분석
    db_name = "game_analytics.db"
    csv_file = "game_data.csv"
    
    try:
        # 데이터베이스 생성 및 데이터 로드
        conn = create_database(db_name, csv_file)

        # 레벨별 이탈율 분석
        churn_results = analyze_level_churn(conn)
        print("\n레벨별 이탈율 분석 결과:")
        print(churn_results.to_string(index=False))
        churn_results.to_csv("churn.csv", index=False)
        
        # 추가 인사이트 분석
        level_time_results = get_additional_insights(conn)
        print("\n레벨별 평균 클리어 시간 (일):")
        print(level_time_results.to_string(index=False))
        
        
        conn.close()
        
    except Exception as e:
        print(f"에러 발생: {str(e)}")

if __name__ == "__main__":
    main()
