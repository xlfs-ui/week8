# 导入日期时间模块，用于记录创建/更新时间
from datetime import datetime

# 从 SQLAlchemy 导入数据库字段类型（ORM 映射工具）
# Boolean: 布尔类型（是/否）
# Column: 定义数据库表的一列
# DateTime: 日期时间类型
# ForeignKey: 外键，用于建立表与表之间的关系
# Integer: 整数类型（常用于ID）
# String: 字符串类型
# Text: 长文本类型
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text

# 导入 ORM 基类和关系定义工具
# declarative_base: 创建数据库模型的基类
# relationship: 定义表与表之间的关联关系（一对多、多对一）
from sqlalchemy.orm import declarative_base, relationship

# 创建 SQLAlchemy ORM 基类，所有数据库模型都要继承这个类
Base = declarative_base()

# 时间戳混入类：给所有表自动添加创建时间、更新时间
# 被其他类继承，避免重复写时间字段
class TimestampMixin:
    # 创建时间：默认值为当前 UTC 时间，不允许为空
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    # 更新时间：创建时自动设为当前时间，更新时自动刷新为最新时间
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

# 笔记本表模型：对应数据库表 notebooks
class Notebook(Base, TimestampMixin):
    # 指定数据库表名
    __tablename__ = "notebooks"

    # 主键ID，自增，建立索引加快查询速度
    id = Column(Integer, primary_key=True, index=True)
    # 笔记本名称，最长120字符，不允许为空，不能重复，建立索引
    name = Column(String(120), nullable=False, unique=True, index=True)

    # 与笔记 Note 建立一对多关系
    # 一个笔记本 包含 多个笔记
    notes = relationship(
        "Note",                  # 关联的表模型
        back_populates="notebook",# 反向关联字段
        cascade="all, delete-orphan", # 级联操作：删除笔记本时，自动删除所有笔记
        passive_deletes=True,    # 数据库级联删除
    )

# 笔记表模型：对应数据库表 notes
class Note(Base, TimestampMixin):
    __tablename__ = "notes"

    # 笔记主键ID
    id = Column(Integer, primary_key=True, index=True)
    # 笔记标题，最长200字符，不允许为空
    title = Column(String(200), nullable=False)
    # 笔记内容，长文本，不允许为空
    content = Column(Text, nullable=False)
    # 外键：关联到所属笔记本的 ID
    notebook_id = Column(
        Integer,
        ForeignKey("notebooks.id", ondelete="CASCADE"), # 删除笔记本时，笔记一并删除
        nullable=False,  # 每篇笔记必须属于某个笔记本
        index=True,      # 加索引，查询更快
    )

    # 反向关联：每篇笔记属于哪个笔记本
    notebook = relationship("Notebook", back_populates="notes")
    # 一对多关系：一篇笔记 可以生成 多个行动项
    action_items = relationship(
        "ActionItem",
        back_populates="note",
        cascade="all, delete-orphan",  # 删除笔记时，自动删除对应的行动项
        passive_deletes=True,
    )

# 行动项表模型：对应数据库表 action_items
class ActionItem(Base, TimestampMixin):
    __tablename__ = "action_items"

    # 行动项主键ID
    id = Column(Integer, primary_key=True, index=True)
    # 行动项描述（代办内容），长文本，不能为空
    description = Column(Text, nullable=False)
    # 是否完成：布尔值，默认未完成（False）
    completed = Column(Boolean, default=False, nullable=False)
    # 外键：关联到所属笔记 ID
    # 允许为空：表示行动项可以不属于任何笔记
    note_id = Column(Integer, ForeignKey("notes.id", ondelete="CASCADE"), nullable=True, index=True)

    # 反向关联：每个行动项属于哪篇笔记
    note = relationship("Note", back_populates="action_items")