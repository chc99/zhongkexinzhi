# 保健品商家后台管理系统 — 设计规格说明书

**日期:** 2026-05-11
**版本:** v1.0
**状态:** 待实现

---

## 一、项目概述

保健品专属的商家后台管理系统，支持商家发布合规商品、上传资质、提交审核、驳回重编，审核员审核商品，超管管理品类与用户。

### 角色体系

| 角色 | 职责 |
|------|------|
| 商家 (merchant) | 管理商家资质、发布/编辑/提交商品、查看商品专属资质、查看审核结果、驳回重编 |
| 审核员 (reviewer) | 审核列表多维筛选、审核详情查看、通过/驳回（必填原因）、批量操作 |
| 超管 (admin) | 品类 CRUD、商家管理、审核员管理、资质类型字典维护 |

### 技术栈

- **前端:** Vue3 + TypeScript + Element Plus + Vite + Pinia + Axios
- **后端:** Python + FastAPI + SQLAlchemy + MySQL + Pydantic + Alembic
- **文件存储:** 本地存储
- **认证:** JWT

---

## 二、数据库设计

### 用户与角色

**users** — 用户表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | bigint PK | 自增主键 |
| username | varchar(50) unique | 登录名 |
| password_hash | varchar(255) | 密码哈希 |
| role | enum('merchant','reviewer','admin') | 角色 |
| phone | varchar(20) | 手机号 |
| status | enum('active','disabled') | 账号状态 |
| created_at | datetime | 创建时间 |

### 品类管理

**categories** — 两级品类树

| 字段 | 类型 | 说明 |
|------|------|------|
| id | bigint PK | 自增主键 |
| parent_id | bigint nullable FK→categories.id | 父品类（null=一级） |
| name | varchar(100) | 品类名称 |
| description | varchar(255) | 描述 |
| sort_order | int default 0 | 排序 |
| status | enum('active','inactive') | 状态 |
| created_by | bigint FK→users.id | 创建人 |

### 商家资质

**qualification_types** — 资质类型字典

| 字段 | 类型 | 说明 |
|------|------|------|
| id | bigint PK | 自增主键 |
| name | varchar(100) | 资质名称（如"营业执照"） |
| code | varchar(50) unique | 编码（如"business_license"） |
| description | varchar(255) | 说明 |
| is_required | boolean default true | 是否必传 |
| scope | enum('merchant','product') | 适用维度（商家级/商品级） |
| sort_order | int | 排序 |

**merchant_qualifications** — 商家级资质

| 字段 | 类型 | 说明 |
|------|------|------|
| id | bigint PK | 自增主键 |
| merchant_id | bigint FK→users.id | 商家 |
| qual_type_id | bigint FK→qualification_types.id | 资质类型 |
| file_url | varchar(500) | 文件路径 |
| file_name | varchar(255) | 原始文件名 |
| expire_date | date nullable | 到期日期 |
| status | enum('valid','expiring','expired') | 状态 |
| remark | varchar(500) | 备注 |
| created_at | datetime | 上传时间 |

### 商品核心

**products** — 商品主表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | bigint PK | 自增主键 |
| merchant_id | bigint FK→users.id | 所属商家 |
| category_id | bigint FK→categories.id | 品类 |
| name | varchar(200) | 商品名称 |
| brand | varchar(100) | 品牌 |
| spec | varchar(100) | 规格 |
| price | decimal(10,2) | 价格（元） |
| stock | int | 库存 |
| main_image | varchar(500) | 主图 |
| status | enum('draft','pending_review','approved','rejected') | 商品状态 |
| reject_reason | text nullable | 驳回原因 |
| submit_at | datetime nullable | 提交审核时间 |
| audit_at | datetime nullable | 审核时间 |
| audit_by | bigint nullable FK→users.id | 审核人 |
| version | int default 1 | 当前版本号 |
| created_at | datetime | 创建时间 |
| updated_at | datetime | 更新时间 |

**product_compliances** — 合规信息 (1:1)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | bigint PK | 自增主键 |
| product_id | bigint FK→products.id unique | 商品 |
| approval_number | varchar(100) | 批准文号（蓝帽批号） |
| main_ingredients | text | 主要原料 |
| efficacy_ingredients | text | 功效成分及含量 |
| suitable_population | varchar(500) | 适宜人群 |
| unsuitable_population | varchar(500) | 不适宜人群 |
| health_function | varchar(500) | 保健功能 |
| usage_dosage | varchar(500) | 食用方法及用量 |
| shelf_life | varchar(100) | 保质期 |
| storage_method | varchar(500) | 贮藏方法 |
| precautions | text | 注意事项 |

**product_images** — 商品图片 (1:N)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | bigint PK | 自增主键 |
| product_id | bigint FK→products.id | 商品 |
| image_type | enum('main','detail') | 图片类型 |
| file_url | varchar(500) | 文件路径 |
| sort_order | int | 排序 |

**product_details** — 详情描述 (1:1)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | bigint PK | 自增主键 |
| product_id | bigint FK→products.id unique | 商品 |
| content | longtext | 富文本描述 |

**product_qualifications** — 商品专属资质

| 字段 | 类型 | 说明 |
|------|------|------|
| id | bigint PK | 自增主键 |
| product_id | bigint FK→products.id | 商品 |
| qual_type_id | bigint FK→qualification_types.id | 资质类型 |
| file_url | varchar(500) | 文件路径 |
| file_name | varchar(255) | 原始文件名 |
| expire_date | date nullable | 到期日期 |
| status | enum('valid','expiring','expired') | 状态 |
| created_at | datetime | 上传时间 |

### 版本与审核

**product_versions** — 版本历史

| 字段 | 类型 | 说明 |
|------|------|------|
| id | bigint PK | 自增主键 |
| product_id | bigint FK→products.id | 商品 |
| version | int | 版本号 |
| snapshot_json | json | 完整商品快照（包含合规信息、图片、资质） |
| change_type | enum('submit','approve','reject','resubmit') | 变更类型 |
| changed_by | bigint FK→users.id | 操作人 |
| remark | text | 备注（驳回时存驳回原因） |
| created_at | datetime | 创建时间 |

**audit_logs** — 审核流水

| 字段 | 类型 | 说明 |
|------|------|------|
| id | bigint PK | 自增主键 |
| product_id | bigint FK→products.id | 商品 |
| reviewer_id | bigint FK→users.id | 审核员 |
| action | enum('submit','approve','reject') | 操作 |
| reason | text nullable | 原因（驳回时必填） |
| created_at | datetime | 操作时间 |

---

## 三、状态流转

### 商品生命周期

```
draft ──提交审核──→ pending_review ──审核通过──→ approved (终态)
  ↑                                        │
  │                    ──驳回──────→ rejected
  │                                   │
  └────── 商家重新编辑 ────────────────┘
```

### 资质生命周期

```
valid ──临近到期(30天)──→ expiring ──已到期──→ expired
```

---

## 四、API 接口设计

### 通用约定

- 统一返回格式: `{ "code": 200, "message": "success", "data": {...} }`
- 分页格式: `{ "list": [...], "total": 100, "page": 1, "page_size": 20 }`
- 认证: Header `Authorization: Bearer {token}`
- 角色权限: 后端依赖注入校验当前用户角色

### 通用模块

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/auth/login` | 登录 |
| POST | `/api/auth/logout` | 退出 |

### 商家端 — 商品

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/merchant/products` | 商品列表（status, keyword, page, page_size） |
| POST | `/api/merchant/products` | 新建商品（存为 draft） |
| GET | `/api/merchant/products/{id}` | 商品详情（含合规/图片/资质/详情） |
| PUT | `/api/merchant/products/{id}` | 更新商品 |
| DELETE | `/api/merchant/products/{id}` | 删除草稿商品 |
| POST | `/api/merchant/products/{id}/submit` | 提交审核（draft→pending_review） |
| POST | `/api/merchant/products/{id}/images` | 上传商品图片 |
| DELETE | `/api/merchant/products/{id}/images/{image_id}` | 删除商品图片 |
| GET | `/api/merchant/products/{id}/versions` | 版本历史 |
| GET | `/api/merchant/products/{id}/qualifications` | 商品专属资质列表 |
| POST | `/api/merchant/products/{id}/qualifications` | 上传商品资质 |
| DELETE | `/api/merchant/products/{id}/qualifications/{qid}` | 删除商品资质 |

### 商家端 — 资质 & 设置

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/merchant/qualifications` | 商家资质列表 |
| POST | `/api/merchant/qualifications` | 上传商家资质 |
| PUT | `/api/merchant/qualifications/{id}` | 更新资质 |
| DELETE | `/api/merchant/qualifications/{id}` | 删除资质 |
| GET | `/api/merchant/dashboard` | 工作台数据（资质到期提醒、审核统计） |

### 公共字典

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/categories` | 获取品类树 |
| GET | `/api/qualification-types` | 资质类型字典 |

### 审核员端

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/reviewer/products` | 审核列表（status/category/merchant/date_range/page/page_size/sort） |
| GET | `/api/reviewer/products/{id}` | 审核详情 |
| POST | `/api/reviewer/products/{id}/approve` | 审核通过 |
| POST | `/api/reviewer/products/{id}/reject` | 驳回（body: { reason }） |
| POST | `/api/reviewer/products/batch-approve` | 批量通过 |
| POST | `/api/reviewer/products/batch-reject` | 批量驳回 |
| GET | `/api/reviewer/dashboard` | 审核工作台统计 |

### 超管端

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/admin/categories` | 新增品类 |
| PUT | `/api/admin/categories/{id}` | 编辑品类 |
| DELETE | `/api/admin/categories/{id}` | 删除品类 |
| GET | `/api/admin/merchants` | 商家列表 |
| PUT | `/api/admin/merchants/{id}/status` | 启用/停用商家 |
| GET | `/api/admin/reviewers` | 审核员列表 |
| POST | `/api/admin/reviewers` | 新增审核员 |
| GET | `/api/admin/qualification-types` | 资质类型列表 |
| POST | `/api/admin/qualification-types` | 新增资质类型 |
| PUT | `/api/admin/qualification-types/{id}` | 编辑资质类型 |
| DELETE | `/api/admin/qualification-types/{id}` | 删除资质类型 |

### 文件上传

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/upload/image` | 上传图片（商品图） |
| POST | `/api/upload/file` | 上传文件（资质文件 PDF/图片） |

---

## 五、前端设计

### 路由结构

```
/login

/merchant
  /merchant/dashboard
  /merchant/products
  /merchant/products/create
  /merchant/products/:id/edit
  /merchant/qualifications
  /merchant/settings

/reviewer
  /reviewer/dashboard
  /reviewer/products
  /reviewer/products/:id

/admin
  /admin/categories
  /admin/merchants
  /admin/reviewers
  /admin/qualification-types
```

### 路由守卫

- 未登录 → `/login`
- 角色不匹配 → 403 页面

### 核心组件

**通用组件:**
- `AppLayout` — 侧边栏+顶栏布局
- `StatusTag` — 状态标签
- `UploadImage` — 图片上传（预览/拖拽/删除）
- `UploadFile` — 文件上传（资质文件/到期日）
- `SearchForm` — 搜索筛选
- `PaginationTable` — 分页表格

**商品发布:**
- `ProductBasicForm` — 基本信息
- `ProductComplianceForm` — 合规信息
- `ProductMediaForm` — 图片+详情
- `ProductQualificationForm` — 商品资质
- `ProductPreview` — 提交预览

**审核相关:**
- `AuditActionPanel` — 审核操作（通过/驳回）
- `VersionHistory` — 版本时间线

### 状态管理 (Pinia)

| Store | 用途 |
|-------|------|
| `useAuthStore` | 用户、角色、token |
| `useProductStore` | 当前商品编辑状态、草稿自动保存 |
| `useReviewStore` | 审核列表筛选+数据 |
| `useCategoryStore` | 品类树缓存 |

### 草稿自动保存

- 表单内容变化后 debounce 3 秒触发 PUT 请求
- 保留手动保存按钮

---

## 六、后端目录结构

```
backend/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── dependencies.py
│   ├── models/
│   │   ├── user.py
│   │   ├── category.py
│   │   ├── product.py
│   │   ├── product_compliance.py
│   │   ├── product_image.py
│   │   ├── product_detail.py
│   │   ├── product_qualification.py
│   │   ├── product_version.py
│   │   ├── merchant_qualification.py
│   │   ├── qualification_type.py
│   │   └── audit_log.py
│   ├── schemas/
│   │   ├── auth.py
│   │   ├── product.py
│   │   ├── qualification.py
│   │   ├── category.py
│   │   └── audit.py
│   ├── api/
│   │   ├── auth.py
│   │   ├── upload.py
│   │   ├── categories.py
│   │   ├── merchant/
│   │   │   ├── products.py
│   │   │   └── qualifications.py
│   │   ├── reviewer/
│   │   │   └── products.py
│   │   └── admin/
│   │       ├── categories.py
│   │       ├── merchants.py
│   │       └── qualification_types.py
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── product_service.py
│   │   ├── qualification_service.py
│   │   ├── audit_service.py
│   │   └── version_service.py
│   └── utils/
│       ├── response.py
│       ├── enums.py
│       ├── exceptions.py
│       └── scheduler.py
├── requirements.txt
└── alembic/
```

## 七、前端目录结构

```
frontend/
├── index.html
├── package.json
├── vite.config.ts
└── src/
    ├── main.ts
    ├── App.vue
    ├── router/
    │   ├── index.ts
    │   └── routes/
    │       ├── merchant.ts
    │       ├── reviewer.ts
    │       └── admin.ts
    ├── stores/
    │   ├── auth.ts
    │   ├── product.ts
    │   ├── review.ts
    │   └── category.ts
    ├── api/
    │   ├── index.ts
    │   ├── auth.ts
    │   ├── product.ts
    │   ├── qualification.ts
    │   ├── category.ts
    │   └── audit.ts
    ├── views/
    │   ├── login/
    │   │   └── Login.vue
    │   ├── merchant/
    │   │   ├── Dashboard.vue
    │   │   ├── ProductList.vue
    │   │   ├── ProductCreate.vue
    │   │   ├── ProductEdit.vue
    │   │   ├── QualificationManage.vue
    │   │   └── Settings.vue
    │   ├── reviewer/
    │   │   ├── Dashboard.vue
    │   │   ├── ProductList.vue
    │   │   └── ProductAudit.vue
    │   └── admin/
    │       ├── CategoryManage.vue
    │       ├── MerchantManage.vue
    │       ├── QualificationTypeManage.vue
    │       └── ReviewerManage.vue
    ├── components/
    │   ├── common/
    │   │   ├── AppLayout.vue
    │   │   ├── StatusTag.vue
    │   │   ├── UploadImage.vue
    │   │   ├── UploadFile.vue
    │   │   ├── SearchForm.vue
    │   │   └── PaginationTable.vue
    │   ├── product/
    │   │   ├── ProductBasicForm.vue
    │   │   ├── ProductComplianceForm.vue
    │   │   ├── ProductMediaForm.vue
    │   │   ├── ProductQualificationForm.vue
    │   │   └── ProductPreview.vue
    │   ├── qualification/
    │   │   └── QualificationCard.vue
    │   └── audit/
    │       ├── AuditActionPanel.vue
    │       └── VersionHistory.vue
    ├── types/
    │   ├── product.ts
    │   ├── qualification.ts
    │   ├── category.ts
    │   └── audit.ts
    └── utils/
        ├── enums.ts
        └── validators.ts
```

---

## 八、定时任务

| 任务 | 频率 | 说明 |
|------|------|------|
| `check_qualification_expiry` | 每天 2:00 | 扫描 expire_date，更新 status: valid→expiring (≤30天), expiring→expired (<今天) |

---

## 九、技术决策记录

| 决策 | 选择 | 理由 |
|------|------|------|
| 架构 | 单体前后端 | 开发效率高，当前规模不需要微服务 |
| 审核层级 | 单级审核 | 满足业务需求，保持简洁 |
| 文件存储 | 本地存储 | 开发阶段最直接 |
| 品类管理 | 两级品类树（超管维护） | 灵活可扩展 |
| 商品字段 | 标准合规字段 | 覆盖法规核心要求，填写负担适中 |
| 草稿机制 | 自动保存 + 手动保存 | 防丢失，用户可控 |
| 审核筛选 | 多维筛选 + 批量操作 | 覆盖日常审核工作流 |
| 驳回流程 | 驳回原因 + 版本历史 | 可追溯，交互简洁 |
| 资质提醒 | 页面提示 + 定时检查 | 覆盖核心需求，不引入操作拦截 |
