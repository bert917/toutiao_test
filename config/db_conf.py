import os
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, create_async_engine

# 数据库URL，优先读取环境变量，本地开发使用默认值
ASYNC_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+aiomysql://root:my-secret-pw@localhost:3306/news_app?charset=utf8mb4",
)

# 创建异步引擎，配置连接池参数
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=True,  # 可选：输出SQL日志
    pool_size=10,  # 设置连接池中保持的持久连接数
    max_overflow=20  # 设置连接池允许创建的额外连接数
)

# 创建异步会话工厂，绑定引擎并禁用提交后属性过期
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


# 依赖项，用于获取数据库会话
async def get_db():
    """
    获取异步数据库会话的依赖函数，用作 FastAPI 的 Depends() 注入。

    Yields:
        AsyncSession: 异步数据库会话对象。

    Raises:
        Exception: 会话操作异常，发生时会回滚并重新抛出。
    """
    async with AsyncSessionLocal() as session:
        # 会话正常使用时提交，异常时回滚，最终关闭会话
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
