"""MySQL 数据库连接"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import logging

from app.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()

# MySQL 连接 URL
MYSQL_URL = f"mysql+pymysql://root:medical123@localhost:3307/medical_assistant?charset=utf8mb4"

# 创建引擎
engine = create_engine(
    MYSQL_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    echo=settings.debug
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基类
Base = declarative_base()


def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """初始化数据库表"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("MySQL tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create MySQL tables: {e}")
        raise
