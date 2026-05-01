# 导入 datetime 模块，用于生成数据库记录的创建/更新时间
from datetime import datetime

# 导入 SQLAlchemy 核心字段类型：用于定义数据库表的列
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
# 导入 ORM 基类生成器 + 表关系定义工具
from sqlalchemy.orm import declarative_base, relationship

# 创建所有数据库模型的基类，所有表都必须继承它
Base = declarative_base()

# 时间戳公共类：给所有数据表自动添加 创建时间、更新时间
class TimestampMixin:
    # 记录创建时间，默认值为当前 UTC 时间，不允许为空
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    # 记录更新时间，创建/更新时自动刷新为当前时间，不允许为空
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

# 笔记本表模型：对应数据库表名 notebooks
class Notebook(Base, TimestampMixin):
    __tablename__ = "notebooks"  # 指定数据库中的表名

    # 表主键 ID，自增整数，建立索引加速查询
    id = Column(Integer, primary_key=True, index=True)
    # 笔记本名称，最长120字符，不能为空，不能重复，建立索引
    name = Column(String(120), nullable=False, unique=True, index=True)

    # 定义一对多关系：一个笔记本包含多篇笔记
    notes = relationship(
        "Note",                        # 关联的模型类
        back_populates="notebook",     # 反向关联字段
        cascade="all, delete-orphan",  # 删除笔记本时，自动删除所有笔记
        passive_deletes=True,          # 启用数据库级联删除
    )

# 笔记表模型：对应数据库表名 notes
class Note(Base, TimestampMixin):
    __tablename__ = "notes"  # 指定数据库表名

    # 笔记主键 ID
    id = Column(Integer, primary_key=True, index=True)
    # 笔记标题，最长200字符，不能为空
    title = Column(String(200), nullable=False)
    # 笔记内容，长文本类型，不能为空
    content = Column(Text, nullable=False)
    # 外键：关联到所属笔记本的 ID
    notebook_id = Column(
        Integer,
        ForeignKey("notebooks.id", ondelete="CASCADE"),  # 笔记本删除，笔记自动删除
        nullable=False,  # 笔记必须归属一个笔记本
        index=True,      # 建立索引，查询更快
    )

    # 反向关系：一篇笔记属于一个笔记本
    notebook = relationship("Notebook", back_populates="notes")
    # 一对多关系：一篇笔记可以生成多个行动项
    action_items = relationship(
        "ActionItem",
        back_populates="note",
        cascade="all, delete-orphan",  # 删除笔记时，自动删除行动项
        passive_deletes=True,
    )

# 行动项（代办事项）表模型：对应数据库表名 action_items
class ActionItem(Base, TimestampMixin):
    __tablename__ = "action_items"  # 指定数据库表名

    # 行动项主键 ID
    id = Column(Integer, primary_key=True, index=True)
    # 行动项描述内容，长文本，不能为空
    description = Column(Text, nullable=False)
    # 是否完成，布尔类型，默认值为未完成（False）
    completed = Column(Boolean, default=False, nullable=False)
    # 外键：关联到所属笔记 ID，允许为空
    note_id = Column(Integer, ForeignKey("notes.id", ondelete="CASCADE"), nullable=True, index=True)

    # 反向关系：一个行动项属于一篇笔记
    note = relationship("Note", back_populates="action_items")