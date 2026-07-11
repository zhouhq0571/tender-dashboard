# 招标看板 - 新增项目标准化流程

## 一、数据字段规范

### JSON数据字段名（必须与JavaScript渲染代码一致）

| 字段名 | 类型 | 必填 | 说明 | 示例 |
|--------|------|------|------|------|
| `id` | number | ✅ | 唯一ID，连续递增 | 49 |
| `company` | string | ✅ | 招标单位简称 | 吉林信托 |
| `project` | string | ✅ | 项目名称 | 家办系统建设软硬件平台采购项目 |
| `overview` | string | ✅ | 项目概况和招标范围 | 吉林信托公司家办系统建设... |
| `budget` | string | ✅ | 预算金额 | 175万元 |
| `deadline` | string | ✅ | 投标截止日期 | 2026-07-30 9:30 |
| `method` | string | ✅ | 招标方式 | 公开招标 |
| `contact` | string | ✅ | 项目咨询/联系方式 | 董天 13041093518 |
| `region` | string | ✅ | 大区（地理分区） | 东北 |
| `province` | string | ✅ | 省份 | 吉林 |
| `tags` | array | ✅ | 业务标签数组 | ["财富管理", "渠道系统"] |
| `rec` | string | ✅ | 投标建议（带星级） | ⭐ ★★☆ 建议投标 |
| `url` | string | ✅ | 信息来源URL | http://... |
| `source` | string | ✅ | 信息来源名称 | 全国招标采购信息平台 |

### ⚠️ 关键：字段名必须与JavaScript渲染代码一致

JavaScript渲染代码使用的字段名：
- `p.overview` → 项目概况和招标范围
- `p.rec` → 投标建议
- `p.region` → 大区
- `p.province` → 省份
- `p.company` → 招标单位
- `p.project` → 项目名称
- `p.budget` → 预算金额
- `p.deadline` → 投标截止日期
- `p.method` → 招标方式
- `p.contact` → 联系方式
- `p.tags` → 业务标签

**禁止使用的字段名**（会导致undefined）：
- ❌ `description` → 应该用 `overview`
- ❌ `suggestion` → 应该用 `rec`

### 投标建议（rec）取值规范

| 值 | 含义 |
|-----|------|
| `🔥 ★★★ 强烈建议投标` | 最高优先级 |
| `⭐ ★★☆ 建议投标` | 建议投标 |
| `👀 ★☆☆ 可关注` | 可关注 |

---

## 二、新增项目检查清单

在添加新项目前，必须完成以下检查：

### 步骤1：字段完整性检查
- [ ] id 是唯一且连续的
- [ ] company 不为空
- [ ] project 不为空
- [ ] overview 不为空（至少20字）
- [ ] budget 不为空（或填"-"）
- [ ] deadline 格式正确（YYYY-MM-DD HH:MM）
- [ ] method 不为空（通常为"公开招标"）
- [ ] contact 不为空
- [ ] region 不为空（东北/华北/华东/华中/华南/西南/西北）
- [ ] province 不为空
- [ ] tags 是数组且不为空
- [ ] rec 是规范值之一
- [ ] url 不为空且以http开头
- [ ] source 不为空

### 步骤2：URL验证
- [ ] URL可以访问（HTTP 200）
- [ ] URL不是分类页面（URL中不含/industry/、/area/等）
- [ ] URL内容与项目匹配（页面标题或内容包含招标单位/项目名称关键词）
- [ ] URL不与现有项目重复

### 步骤3：字段名验证
- [ ] 使用 `overview` 而不是 `description`
- [ ] 使用 `rec` 而不是 `suggestion`
- [ ] 所有字段名与JavaScript渲染代码一致

### 步骤4：本地验证
- [ ] 在浏览器中打开index.html预览
- [ ] 检查新项目是否显示正常（无undefined）
- [ ] 检查所有字段是否正确显示

### 步骤5：部署
- [ ] 提交到git
- [ ] 推送到gh-pages
- [ ] 等待2分钟后验证线上版本

---

## 三、常见错误及避免方法

| 错误 | 原因 | 避免方法 |
|------|------|----------|
| 显示undefined | 字段名不匹配（如用description而非overview） | 对照本文档字段规范 |
| URL重复 | 新增时未检查URL唯一性 | 使用验证脚本检查 |
| 分类页面URL | URL是列表页而非详情页 | 访问URL验证内容 |
| 缺少字段 | 未按规范填写所有字段 | 使用检查清单 |
| 投标建议显示错误 | rec字段值不规范 | 使用规范值 |

---

## 四、快速参考：新增项目代码模板

```python
new_project = {
    'id': max_id + 1,
    'company': '招标单位简称',
    'project': '项目名称',
    'overview': '项目概况和招标范围（至少20字）',
    'budget': '预算金额（或"-"）',
    'deadline': '2026-07-30 9:30',
    'method': '公开招标',
    'contact': '联系人 电话 / 邮箱',
    'region': '东北',  # 东北/华北/华东/华中/华南/西南/西北
    'province': '吉林',
    'tags': ['财富管理', '渠道系统'],
    'rec': '⭐ ★★☆ 建议投标',  # 或 '👀 ★☆☆ 可关注' 或 '🔥 ★★★ 强烈建议投标'
    'url': 'https://具体项目URL',
    'source': '信息来源名称'
}
```

---

## 五、验证脚本使用

在添加新项目后，运行验证脚本：

```bash
python3 validate_new_projects.py
```

脚本会检查：
1. 字段完整性
2. URL可访问性
3. URL唯一性
4. 字段名正确性

---

*文档版本: v1.0*
*创建日期: 2026-07-11*
