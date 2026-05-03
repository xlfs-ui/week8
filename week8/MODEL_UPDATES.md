# Week7 数据模型升级说明

## 变更目标

- 新增 `Notebook` 模型，支持对 `Note` 做分组管理。
- 完善模型关联，建立 `Notebook -> Note -> ActionItem` 的层级关系。
- 更新后端 API 与前端页面，适配新字段和新关系。

## 数据库模型变更

### 1) 新增模型

- `notebooks`
  - `id`：主键
  - `name`：笔记本名称（唯一）
  - `created_at` / `updated_at`：时间戳

### 2) 关联关系调整

- `notes` 新增 `notebook_id`（非空外键，指向 `notebooks.id`）
- `action_items` 新增 `note_id`（可空外键，指向 `notes.id`）

### 3) ORM 关系

- `Notebook.notes`：一对多，级联删除
- `Note.notebook`：多对一
- `Note.action_items`：一对多，级联删除
- `ActionItem.note`：多对一

## 接口与应用适配

- 新增 `GET /notebooks/`、`POST /notebooks/` 接口。
- `POST /notes/` 支持传入 `notebook_id`；未传时自动绑定默认笔记本 `General`。
- `PATCH /notes/{note_id}` 支持更新 `notebook_id`。
- `POST /action-items/` 支持传入 `note_id`。
- `PATCH /action-items/{item_id}` 支持更新 `note_id`。
- `GET /action-items/` 支持通过 `note_id` 过滤。

## 前端改动

- 新增 Notebook 创建表单与列表展示。
- Note 创建表单新增 Notebook 选择器。
- Action Item 创建表单新增 Note 选择器（可不关联）。
- 列表展示中追加关联信息（`notebook_id` / `note_id`）。

## 种子数据调整

- `seed.sql` 新增 `notebooks` 表与初始化数据。
- `notes`、`action_items` 插入语句改为包含新外键字段。

## 兼容性说明

- 旧数据库如果已存在且结构未迁移，需重建数据库或执行迁移后再运行新版本。
- 新版本默认通过 ORM 的 `create_all` 建表逻辑创建完整结构，首次启动可直接使用。
