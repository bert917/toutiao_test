import asyncio
import random
from datetime import datetime, timedelta
from sqlalchemy import insert
from config.db_conf import AsyncSessionLocal
from models.news import News


async def seed():
    base_time = datetime(2024, 1, 1)
    rows = []
    for i in range(100):
        publish_time = base_time + timedelta(days=random.randint(0, 365), hours=random.randint(0, 23))
        rows.append({
            "title": f"分类1测试新闻_{i+1}",
            "description": f"这是第{i+1}条测试新闻的摘要内容",
            "content": f"这是第{i+1}条测试新闻的正文内容，用于填充详细的文本数据。" * 3,
            "image": f"https://picsum.photos/id/{random.randint(1, 200)}/200/200",
            "author": random.choice(["新华社", "人民日报", "央视新闻", "光明日报", "中新网"]),
            "category_id": 1,
            "views": random.randint(100, 50000),
            "publish_time": publish_time,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        })

    async with AsyncSessionLocal() as session:
        await session.execute(insert(News), rows)
        await session.commit()
        print(f"成功插入 {len(rows)} 条分类为1的新闻数据")


if __name__ == "__main__":
    asyncio.run(seed())
