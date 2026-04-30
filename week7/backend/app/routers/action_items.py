# 从typing模块导入Optional，用于定义可选类型的参数
from typing import Optional

# 从fastapi导入路由、依赖、HTTP异常、查询参数工�?
from fastapi import APIRouter, Depends, HTTPException, Query
# 从sqlalchemy导入升序、降序、查询语句构造函�?
from sqlalchemy import asc, desc, select
from sqlalchemy.exc import SQLAlchemyError
# 从sqlalchemy导入ORM会话类，用于数据库操�?
from sqlalchemy.orm import Session

# 从上级包的db模块导入数据库会话依赖函�?
from ..db import get_db
# 从上级包的models模块导入ActionItem数据库模型类
from ..models import ActionItem
# 从上级包的schemas模块导入ActionItem的创建、部分更新、读取数据模�?
from ..schemas import ActionItemCreate, ActionItemPatch, ActionItemRead

# 创建API路由实例，设置路由前缀�?/action-items，接口文档标签为action_items
router = APIRouter(prefix="/action-items", tags=["action_items"])
ALLOWED_SORT_FIELDS = {"id", "description", "completed", "created_at", "updated_at"}


# 定义GET请求接口，路径为/，返回数据模型为ActionItemRead列表
@router.get("/", response_model=list[ActionItemRead])
# 定义获取任务列表的接口函�?
def list_items(
    # 注入数据库会话依赖，自动管理数据库连�?
    db: Session = Depends(get_db),
    # 可选查询参数：筛选是否完成的任务
    completed: Optional[bool] = None,
    # 分页参数：跳过前N条数据，默认0
    skip: int = Query(0, ge=0),
    # 分页参数：限制返回条数，默认50，最大不超过200
    limit: int = Query(50, ge=1, le=200),
    # 排序参数，默认按创建时间倒序排序
    sort: str = Query("-created_at"),
) -> list[ActionItemRead]:
    # 构造查询所有ActionItem数据的SQL语句
    stmt = select(ActionItem)
    # 如果传入了completed参数，添加筛选条�?
    if completed is not None:
        stmt = stmt.where(ActionItem.completed.is_(completed))

    # 去除排序字段前的-符号，获取纯字段�?
    sort_field = sort.lstrip("-")
    if sort_field not in ALLOWED_SORT_FIELDS:
        raise HTTPException(status_code=400, detail=f"Invalid sort field: {sort_field}")
    # 判断排序方式：以-开头为降序，否则为升序
    order_fn = desc if sort.startswith("-") else asc
    # 按指定字段排�?
    stmt = stmt.order_by(order_fn(getattr(ActionItem, sort_field)))

    # 执行SQL语句，应用分页，获取查询结果的标量（对象）列�?
    rows = db.execute(stmt.offset(skip).limit(limit)).scalars().all()
    # 将数据库模型对象转换为响应模型，返回列表
    return [ActionItemRead.model_validate(row) for row in rows]


# 定义POST请求接口，路径为/，返回数据模型为ActionItemRead，状态码201表示创建成功
@router.post("/", response_model=ActionItemRead, status_code=201)
# 定义创建任务的接口函数，接收创建数据模型和数据库会话
def create_item(payload: ActionItemCreate, db: Session = Depends(get_db)) -> ActionItemRead:
    try:
        # 创建ActionItem实例，描述来自请求体，默认未完成
        item = ActionItem(description=payload.description, completed=False)
        # 将新对象添加到数据库会话
        db.add(item)
        # 刷新会话，同步数据库状态（不提交事务）
        db.flush()
        # 刷新对象，获取数据库自动生成的字段（如id、创建时间）
        db.refresh(item)
        # 转换为响应模型并返回
        return ActionItemRead.model_validate(item)
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create action item") from exc


# 定义PUT请求接口，路径为/{item_id}/complete，标记任务完�?
@router.put("/{item_id}/complete", response_model=ActionItemRead)
# 定义标记任务完成的接口函数，接收任务ID和数据库会话
def complete_item(item_id: int, db: Session = Depends(get_db)) -> ActionItemRead:
    # 根据ID从数据库查询任务对象
    item = db.get(ActionItem, item_id)
    # 如果任务不存在，抛出404异常
    if not item:
        raise HTTPException(status_code=404, detail="Action item not found")
    try:
        # 将任务状态设置为已完�?
        item.completed = True
        # 将修改后的对象添加到会话
        db.add(item)
        # 刷新会话，同步修�?
        db.flush()
        # 刷新对象数据
        db.refresh(item)
        # 返回更新后的任务数据
        return ActionItemRead.model_validate(item)
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to complete action item") from exc


# 定义PATCH请求接口，路径为/{item_id}，用于部分更新任�?
@router.patch("/{item_id}", response_model=ActionItemRead)
# 定义部分更新任务的接口函数，接收任务ID、更新数据模型、数据库会话
def patch_item(item_id: int, payload: ActionItemPatch, db: Session = Depends(get_db)) -> ActionItemRead:
    # 根据ID查询任务对象
    item = db.get(ActionItem, item_id)
    # 任务不存在则抛出404异常
    if not item:
        raise HTTPException(status_code=404, detail="Action item not found")
    try:
        # 如果请求体传入了描述，更新任务描�?
        if payload.description is not None:
            item.description = payload.description
        # 如果请求体传入了完成状态，更新完成状�?
        if payload.completed is not None:
            item.completed = payload.completed
        # 保存修改到会�?
        db.add(item)
        # 同步数据�?
        db.flush()
        # 刷新对象
        db.refresh(item)
        # 返回更新后的任务数据
        return ActionItemRead.model_validate(item)
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update action item") from exc