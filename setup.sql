create table user_max_level as 
  SELECT
        userid,
        MAX(level_cleared) as max_level
        FROM game_logs
        GROUP BY userid;

create table stopped_users as
  SELECT
        max_level as level,
        COUNT(*) as users_stopped
        FROM (
        SELECT
          userid,
          MAX(level_cleared) as max_level
          FROM game_logs
          GROUP BY userid
        ) max_level
        GROUP BY max_level;

create table level_stats as
  SELECT
        t.level_num as level,
        COUNT(DISTINCT gl.userid) as users_reached
        FROM (
            SELECT DISTINCT level_cleared as level_num
            FROM game_logs
        ) t
        LEFT JOIN game_logs gl ON gl.level_cleared >= t.level_num
        GROUP BY t.level_num;

create table level_stats as
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
ORDER BY level;

create table results as
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

