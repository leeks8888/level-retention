import pandas as pd
from datetime import datetime

def analyze_level_churn(data_path):
    """
    게임의 레벨별 이탈율을 분석하는 함수
    
    Parameters:
    data_path (str): CSV 파일 경로
    
    Returns:
    DataFrame: 레벨별 이탈율 분석 결과
    """
    # 데이터 로드
    df = pd.read_csv(data_path)
    
    # 날짜 컬럼을 datetime으로 변환
    df['install_date'] = pd.to_datetime(df['install_date'])
    df['play_date'] = pd.to_datetime(df['play_date'])
    
    # 유저별 최대 레벨과 마지막 플레이 날짜 확인
    user_max_level = df.groupby('userid')['level_cleared'].max().reset_index()
    user_last_play = df.groupby('userid')['play_date'].max().reset_index()
    
    # 분석 결과를 저장할 DataFrame 생성
    level_stats = pd.DataFrame()
    
    # 각 레벨별 통계 계산
    all_levels = sorted(df['level_cleared'].unique())
    
    for level in all_levels:
        # 해당 레벨에 도달한 유저 수
        users_reached = len(user_max_level[user_max_level['level_cleared'] >= level])
        
        # 해당 레벨이 최대인 유저 수 (다음 레벨로 진행하지 않은 유저)
        users_stopped = len(user_max_level[user_max_level['level_cleared'] == level])
        
        # 이탈율 계산
        churn_rate = (users_stopped / users_reached * 100) if users_reached > 0 else 0
        
        level_stats = pd.concat([level_stats, pd.DataFrame({
            'level': [level],
            'total_users_reached': [users_reached],
            'users_stopped': [users_stopped],
            'churn_rate': [churn_rate]
        })])
    
    # 인덱스 리셋
    level_stats = level_stats.reset_index(drop=True)
    
    # 추가 정보 계산
    level_stats['retention_rate'] = 100 - level_stats['churn_rate']
    level_stats['progression_rate'] = level_stats['total_users_reached'].shift(-1) / level_stats['total_users_reached'] * 100
    
    # 결과 포맷팅
    level_stats['churn_rate'] = level_stats['churn_rate'].round(2)
    level_stats['retention_rate'] = level_stats['retention_rate'].round(2)
    level_stats['progression_rate'] = level_stats['progression_rate'].round(2)
    
    return level_stats

# 사용 예시
if __name__ == "__main__":
    # CSV 파일 경로
    file_path = "playlog.csv"
    
    try:
        results = analyze_level_churn(file_path)
        print("\n레벨별 이탈율 분석 결과:")
        print(results.to_string(index=False))
        results.to_csv("churn.csv", index=False)
        
    except Exception as e:
        print(f"에러 발생: {str(e)}")
