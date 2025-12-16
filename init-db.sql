-- 初始化数据库脚本
-- 创建数据库（如果不存在）
CREATE DATABASE bb2y2b;

-- 创建用户（如果不存在）
DO
$do$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_catalog.pg_roles
      WHERE  rolname = 'bb2y2b') THEN

      CREATE ROLE bb2y2b LOGIN PASSWORD 'bb2y2b';
   END IF;
END
$do$;

-- 授予权限
GRANT ALL PRIVILEGES ON DATABASE bb2y2b TO bb2y2b;

-- 连接到bb2y2b数据库
\c bb2y2b;

-- 授予schema权限
GRANT ALL ON SCHEMA public TO bb2y2b;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO bb2y2b;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO bb2y2b;