# 恒生电子银信事业群招标市场需求监控看板 — UI/UED设计审查报告

> **审查对象**：`tender_dashboard_v3.html`  
> **审查日期**：2026年6月8日  
> **审查人**：资深UI/UED设计专家  
> **审查维度**：整体视觉 / 封面设计 / 表格体验 / 筛选交互 / 移动端适配 / 动效微交互 / 信息层级

---

## 一、问题清单（按优先级排序）

| 优先级 | 问题类别 | 具体问题 | 影响程度 |
|:---:|---|---|---|
| **P0** | 封面设计 | 封面高度100vh，用户反馈"太大"，首屏无法直接看到数据 | 🔴 严重 |
| **P0** | 信息层级 | 投标截止日期、恒生建议等关键决策信息不够突出 | 🔴 严重 |
| **P1** | 表格体验 | 文字密度过高，行高/字重不舒适，长文本展示方式原始 | 🟠 高 |
| **P1** | 筛选交互 | 无空状态提示、无筛选结果动画反馈、多条件组合易用性不足 | 🟠 高 |
| **P1** | 品牌感知 | 缺少恒生电子HUNDSUN品牌元素，专业感不足 | 🟠 高 |
| **P2** | 移动端适配 | 响应式断点单一，小屏幕表格横向滚动体验差 | 🟡 中 |
| **P2** | 动效微交互 | 标签页切换生硬、统计卡片hover单一、无加载状态 | 🟡 中 |
| **P2** | 视觉设计 | 配色偏冷偏暗，长时间阅读易产生视觉疲劳 | 🟡 中 |
| **P3** | 细节打磨 | 链接hover缩放突兀、部分列宽分配不合理、缺少操作引导 | 🟢 低 |

---

## 二、专项优化建议

### 【专项A】缩小封面 + 品牌升级

#### 现状问题
- `min-height: 100vh` 导致封面占满整个视口，用户必须滚动才能看到核心数据
- 缺少恒生电子品牌标识（Logo、品牌色、品牌口号）
- 免责声明在封面底部，与核心内容争夺视觉焦点

#### 优化方案

**1. 封面高度缩减为 `min-height: 420px; max-height: 520px`**

```css
/* ===== 封面优化 ===== */
.cover {
  background: linear-gradient(145deg, #0a2540 0%, #1e3a5f 50%, #2c5282 100%);
  min-height: 420px;
  max-height: 520px;
  height: auto;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  color: white;
  padding: 48px 40px 64px;  /* 底部留足空间 */
  position: relative;
  overflow: hidden;
}

/* 品牌Logo区域 */
.cover-brand {
  position: relative;
  z-index: 2;
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 24px;
}

.cover-brand-logo {
  width: 36px;
  height: 36px;
  background: var(--gold);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 14px;
  color: #1e3a5f;
  letter-spacing: 1px;
}

.cover-brand-text {
  font-size: 15px;
  font-weight: 600;
  letter-spacing: 3px;
  opacity: 0.95;
}

/* 标题层级优化 */
.cover h1 {
  font-size: 32px;        /* 从42px缩小 */
  font-weight: 700;
  margin-bottom: 12px;
  letter-spacing: 1px;
  line-height: 1.3;
}

.cover-subtitle {
  font-size: 16px;
  opacity: 0.85;
  margin-bottom: 8px;
  font-weight: 400;
}

.cover-meta {
  font-size: 13px;
  opacity: 0.65;
  margin-bottom: 8px;
}

/* 编制单位卡片优化 */
.cover-author {
  font-size: 14px;
  margin-top: 20px;
  padding: 10px 24px;
  background: rgba(255,255,255,0.08);
  border-radius: 8px;
  border-left: 3px solid var(--gold);
  display: inline-block;
}

/* 移除底部免责声明（移至封底）和滚动提示 */
.scroll-hint { display: none; }
.cover-disclaimer { display: none; }
```

**2. HTML封面结构调整**

```html
<!-- 优化后的封面 -->
<div class="cover">
  <div class="cover-content">
    <div class="cover-brand">
      <div class="cover-brand-logo">HS</div>
      <div class="cover-brand-text">HUNDSUN · 恒生电子</div>
    </div>
    <div class="cover-badge">CONFIDENTIAL · INTERNAL USE ONLY</div>
    <h1>恒生电子银信事业群<br>招标市场需求监控看板</h1>
    <div class="cover-subtitle">银行信托事业群销售 / 解决方案 / 售前专用</div>
    <div class="cover-meta">覆盖银行 / 银行系科技子公司 / 银行理财子公司 / 信托公司</div>
    <div class="cover-meta">数据更新时间：2026年6月8日</div>
    <div class="cover-author">编制单位：恒生电子银信解决方案部</div>
  </div>
</div>
```

**3. 将免责声明移至封底**

```html
<!-- 封底增加完整免责声明 -->
<div class="footer-section">
  <div class="footer-brand">
    <div class="cover-brand-logo">HS</div>
    <span>恒生电子 HUNDSUN</span>
  </div>
  <h2>恒生电子银信事业群招标市场需求监控看板</h2>
  <p>编制单位：恒生电子银信解决方案部 · 数据更新时间：2026年6月8日</p>
  <div class="footer-disclaimer">
    <strong>重要声明：</strong>本看板所有数据和信息均由AI辅助生成...（完整声明）
  </div>
</div>
```

---

### 【专项B】筛选体验全面升级

#### 现状问题
- 筛选后无空状态提示，用户不知道是没有数据还是筛选错误
- 筛选结果计数更新生硬，无动画反馈
- 多条件组合时，用户不清楚当前激活了哪些条件
- 业务标签筛选与下拉筛选之间无联动提示
- 搜索框placeholder使用emoji，不够专业

#### 优化方案

**1. 筛选面板布局重构 — 增加"已选条件"展示栏**

```css
/* ===== 筛选面板优化 ===== */
.filter-panel {
  background: var(--card);
  border-radius: var(--radius);
  padding: 20px 24px;
  margin: 0 20px 20px;
  box-shadow: var(--shadow);
  max-width: 1400px;
  margin-left: auto;
  margin-right: auto;
}

/* 筛选条件分组 */
.filter-section {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 14px;
  align-items: center;
}

.filter-section:last-child {
  margin-bottom: 0;
}

.filter-section-title {
  font-size: 12px;
  color: var(--text-light);
  font-weight: 500;
  min-width: 80px;
  text-align: right;
}

/* 下拉框优化 */
.filter-row select,
.filter-row input {
  padding: 8px 32px 8px 12px;  /* 右侧留空间给自定义箭头 */
  border: 1px solid var(--border);
  border-radius: 8px;
  font-size: 13px;
  background: white;
  min-width: 160px;
  cursor: pointer;
  outline: none;
  transition: all 0.2s;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg width='10' height='6' viewBox='0 0 10 6' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M1 1l4 4 4-4' stroke='%23718096' stroke-width='1.5' fill='none'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 12px center;
}

.filter-row select:focus,
.filter-row input:focus {
  border-color: var(--primary-light);
  box-shadow: 0 0 0 3px rgba(30, 58, 95, 0.08);
}

/* 搜索框优化 */
.filter-row input[type="text"] {
  min-width: 240px;
  padding-left: 36px;
  background-image: url("data:image/svg+xml,%3Csvg width='16' height='16' viewBox='0 0 16 16' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M11.7422 10.3439C12.5329 9.2673 13 7.9382 13 6.5C13 2.91015 10.0899 0 6.5 0C2.91015 0 0 2.91015 0 6.5C0 10.0899 2.91015 13 6.5 13C7.9382 13 9.2673 12.5329 10.3439 11.7422L14.1464 15.5446C14.3417 15.7399 14.6583 15.7399 14.8536 15.5446L15.5446 14.8536C15.7399 14.6583 15.7399 14.3417 15.5446 14.1464L11.7422 10.3439ZM6.5 11C4.01472 11 2 8.98528 2 6.5C2 4.01472 4.01472 2 6.5 2C8.98528 2 11 4.01472 11 6.5C11 8.98528 8.98528 11 6.5 11Z' fill='%23718096'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: left 12px center;
}

.filter-row input::placeholder {
  color: #a0aec0;
}

/* 按钮优化 */
.filter-btn {
  padding: 8px 18px;
  background: var(--primary);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
  font-weight: 500;
}

.filter-btn:hover {
  background: var(--primary-light);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(30, 58, 95, 0.2);
}

.reset-btn {
  padding: 8px 18px;
  background: transparent;
  color: var(--text-light);
  border: 1px solid var(--border);
  border-radius: 8px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
  font-weight: 500;
}

.reset-btn:hover {
  background: #edf2f7;
  color: var(--text);
  border-color: #cbd5e0;
}

/* 已选条件展示栏 */
.active-filters {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  min-height: 32px;
  padding: 8px 0;
  border-top: 1px dashed var(--border);
  margin-top: 8px;
}

.active-filters-label {
  font-size: 12px;
  color: var(--text-light);
  font-weight: 500;
}

.active-filter-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  background: #ebf8ff;
  color: #2b6cb0;
  border-radius: 16px;
  font-size: 12px;
  font-weight: 500;
  border: 1px solid #bee3f8;
  animation: tagIn 0.25s ease;
}

.active-filter-tag .remove {
  cursor: pointer;
  width: 14px;
  height: 14px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: rgba(43, 108, 176, 0.15);
  font-size: 10px;
  transition: background 0.2s;
}

.active-filter-tag .remove:hover {
  background: rgba(43, 108, 176, 0.3);
}

@keyframes tagIn {
  from { opacity: 0; transform: scale(0.8) translateY(-4px); }
  to   { opacity: 1; transform: scale(1) translateY(0); }
}

/* 业务标签筛选优化 */
.biz-tag-filter {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  align-items: center;
}

.filter-tag-btn {
  padding: 6px 14px;
  border: 1px solid var(--border);
  border-radius: 20px;
  background: white;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
  color: var(--text-light);
  font-weight: 500;
  white-space: nowrap;
}

.filter-tag-btn:hover {
  background: var(--primary);
  color: white;
  border-color: var(--primary);
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(30, 58, 95, 0.15);
}

.filter-tag-btn.active {
  background: var(--primary);
  color: white;
  border-color: var(--primary);
  box-shadow: 0 2px 8px rgba(30, 58, 95, 0.2);
}
```

**2. 空状态设计**

```css
/* ===== 空状态 ===== */
.empty-state {
  display: none;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
  color: var(--text-light);
}

.empty-state.show {
  display: flex;
  animation: fadeIn 0.4s ease;
}

.empty-state-icon {
  width: 64px;
  height: 64px;
  background: #f7fafc;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  margin-bottom: 16px;
}

.empty-state h4 {
  font-size: 16px;
  color: var(--text);
  margin-bottom: 8px;
  font-weight: 600;
}

.empty-state p {
  font-size: 13px;
  color: var(--text-light);
  margin-bottom: 16px;
  max-width: 400px;
  line-height: 1.6;
}

.empty-state .reset-link {
  color: var(--primary-light);
  font-size: 13px;
  cursor: pointer;
  text-decoration: underline;
  font-weight: 500;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to   { opacity: 1; transform: translateY(0); }
}
```

**3. 筛选结果计数动画**

```css
/* ===== 结果计数优化 ===== */
.result-count {
  padding: 14px 20px;
  font-size: 13px;
  color: var(--text-light);
  border-bottom: 1px solid var(--border);
  background: #fafbfc;
  display: flex;
  align-items: center;
  gap: 6px;
}

.result-count span {
  font-weight: 700;
  color: var(--primary);
  font-size: 15px;
  display: inline-block;
  min-width: 20px;
  text-align: center;
  transition: all 0.3s ease;
}

.result-count span.changed {
  color: var(--accent);
  transform: scale(1.2);
}
```

**4. 筛选JS增强**

```javascript
// ===== 筛选交互增强 =====

// 更新已选条件展示
function updateActiveFilters() {
  const container = document.getElementById('active-filters-bar');
  if (!container) return;
  
  const province = document.getElementById('filter-province').value;
  const method = document.getElementById('filter-method').value;
  const rec = document.getElementById('filter-rec').value;
  const search = document.getElementById('filter-search').value;
  
  let html = '<span class="active-filters-label">已选条件：</span>';
  let hasFilter = false;
  
  const filters = [];
  if (province) filters.push({ type: 'province', label: '省份：' + province });
  if (method) filters.push({ type: 'method', label: '方式：' + method });
  if (rec) filters.push({ type: 'rec', label: '建议：' + rec.split(' ')[0] });
  if (activeTag) filters.push({ type: 'tag', label: '标签：' + activeTag });
  if (search) filters.push({ type: 'search', label: '搜索：' + search });
  
  if (filters.length === 0) {
    html += '<span style="font-size:12px;color:#a0aec0">无</span>';
  } else {
    filters.forEach(f => {
      html += `<span class="active-filter-tag" data-type="${f.type}">${f.label}<span class="remove" onclick="removeFilter('${f.type}')">✕</span></span>`;
    });
    hasFilter = true;
  }
  
  container.innerHTML = html;
  container.style.display = hasFilter ? 'flex' : 'none';
}

// 移除单个筛选条件
function removeFilter(type) {
  if (type === 'province') document.getElementById('filter-province').value = '';
  if (type === 'method') document.getElementById('filter-method').value = '';
  if (type === 'rec') document.getElementById('filter-rec').value = '';
  if (type === 'search') document.getElementById('filter-search').value = '';
  if (type === 'tag') {
    activeTag = '';
    document.querySelectorAll('.filter-tag-btn').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.tag === '');
    });
  }
  applyFilters();
}

// 增强版 applyFilters
function applyFilters() {
  const province = document.getElementById('filter-province').value;
  const method = document.getElementById('filter-method').value;
  const rec = document.getElementById('filter-rec').value;
  const search = document.getElementById('filter-search').value.toLowerCase();
  
  const tabPrefix = 'tab-' + currentTab + '-row-';
  const allRows = document.querySelectorAll('[id^="' + tabPrefix + '"]');
  let visibleCount = 0;
  
  allRows.forEach(row => {
    const rowProvince = row.dataset.province || '';
    const rowMethod = row.dataset.method || '';
    const rowRec = row.dataset.rec || '';
    const rowProject = row.dataset.project || '';
    const rowTags = row.dataset.tags || '';
    
    let show = true;
    if (province && rowProvince !== province) show = false;
    if (method && rowMethod !== method) show = false;
    if (rec && rowRec !== rec) show = false;
    if (search && !rowProject.toLowerCase().includes(search)) show = false;
    if (activeTag && !rowTags.includes(activeTag)) show = false;
    
    row.style.display = show ? '' : 'none';
    if (show) visibleCount++;
  });
  
  // 更新计数（带动画）
  const countEl = document.getElementById('count-' + currentTab);
  if (countEl) {
    countEl.classList.add('changed');
    countEl.textContent = visibleCount;
    setTimeout(() => countEl.classList.remove('changed'), 300);
  }
  
  // 空状态控制
  const emptyState = document.getElementById('empty-' + currentTab);
  const tableWrap = document.querySelector('#tab-' + currentTab + ' .table-wrap');
  if (emptyState) {
    if (visibleCount === 0) {
      emptyState.classList.add('show');
      if (tableWrap) tableWrap.style.display = 'none';
    } else {
      emptyState.classList.remove('show');
      if (tableWrap) tableWrap.style.display = 'block';
    }
  }
  
  // 更新已选条件展示
  updateActiveFilters();
}

// 重置筛选增强
function resetFilters() {
  document.getElementById('filter-province').value = '';
  document.getElementById('filter-method').value = '';
  document.getElementById('filter-rec').value = '';
  document.getElementById('filter-search').value = '';
  activeTag = '';
  document.querySelectorAll('.filter-tag-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.tag === '');
  });
  applyFilters();
}
```

---

## 三、各维度详细优化方案

### 1. 整体视觉设计优化

#### 问题
- 主色 `#1e3a5f` 偏冷偏暗，长时间阅读易产生视觉疲劳
- 背景色 `#f0f4f8` 偏灰，缺少金融企业应有的稳重与高级感
- 阴影 `0 4px 20px rgba(0,0,0,0.08)` 偏淡，卡片层次感不足

#### 优化CSS

```css
:root {
  /* 品牌色优化 — 更沉稳的金融科技蓝 */
  --primary: #0f2a4a;           /* 加深，更有分量 */
  --primary-light: #1e4a7a;     /* 提亮变体 */
  --primary-soft: #e8f0f8;      /* 柔和背景 */
  
  /* 强调色优化 */
  --accent: #c41e3a;            /* 更纯正的金融红 */
  --accent-light: #e85d75;
  --accent-soft: #fef2f2;
  
  /* 金色优化 */
  --gold: #b8860b;              /* 更沉稳的金色 */
  --gold-light: #d4a843;
  --gold-soft: #fffbeb;
  
  /* 中性色优化 */
  --bg: #f5f7fa;                /* 更干净的灰白 */
  --card: #ffffff;
  --text: #1a202c;              /* 更深的正文，提升对比度 */
  --text-light: #64748b;        /* 更柔和的次要文字 */
  --text-muted: #94a3b8;
  --border: #e2e8f0;
  --border-light: #f1f5f9;
  
  /* 阴影优化 — 更有层次感 */
  --shadow-sm: 0 1px 3px rgba(0,0,0,0.04);
  --shadow: 0 4px 16px rgba(15, 42, 74, 0.08);
  --shadow-lg: 0 8px 30px rgba(15, 42, 74, 0.12);
  
  --radius: 10px;               /* 稍微收敛圆角 */
  --radius-sm: 6px;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
  background: var(--bg);
  color: var(--text);
  line-height: 1.6;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
```

---

### 2. 表格阅读体验优化

#### 问题
- 字体12.5px偏小，行高仅20px（padding 10px），阅读疲劳
- 项目概况列220px宽度不足以展示长文本，大量依赖title tooltip
- 列宽分配不合理：序号/大区/省份过窄，招标单位100px对长名称不够
- 所有列居中对齐，左对齐列用inline style，维护混乱
- hover状态仅背景色变化，信息定位感弱

#### 优化CSS

```css
/* ===== 表格全面优化 ===== */
.table-wrap {
  overflow-x: auto;
  padding: 0;
  /* 增加滚动提示阴影 */
  background: linear-gradient(to right, white 30%, transparent),
              linear-gradient(to left, white 30%, transparent),
              linear-gradient(to right, rgba(0,0,0,0.04), transparent 10px),
              linear-gradient(to left, rgba(0,0,0,0.04), transparent 10px);
  background-position: left center, right center, left center, right center;
  background-repeat: no-repeat;
  background-size: 20px 100%, 20px 100%, 10px 100%, 10px 100%;
  background-attachment: local, local, scroll, scroll;
}

table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  font-size: 13px;              /* 从12.5px提升 */
  min-width: 1200px;            /* 保证最小宽度 */
}

/* 表头优化 */
th {
  background: #f8fafc;
  padding: 14px 12px;           /* 增加垂直padding */
  text-align: center;
  font-weight: 600;
  color: var(--primary);
  border-bottom: 2px solid var(--primary-light);
  white-space: nowrap;
  font-size: 12px;
  position: sticky;
  top: 0;
  z-index: 10;
  letter-spacing: 0.5px;
  text-transform: uppercase;    /* 英文标签大写 */
}

/* 单元格优化 */
td {
  padding: 14px 12px;           /* 从10px增加到14px */
  border-bottom: 1px solid var(--border-light);
  vertical-align: top;
  text-align: center;
  transition: background 0.15s;
  line-height: 1.5;             /* 增加行高 */
}

/* 行hover优化 — 增加左侧指示条 */
tr {
  position: relative;
  transition: all 0.15s;
}

tr:hover {
  background: #f8fafc;
}

tr:hover td:first-child::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
  background: var(--primary-light);
  border-radius: 0 2px 2px 0;
}

/*  zebra striping 增加可读性 */
tbody tr:nth-child(even) {
  background: #fafbfc;
}

tbody tr:nth-child(even):hover {
  background: #f0f4f8;
}

/* ===== 列宽重新分配 ===== */
/* 序号 */
th:nth-child(1), td:nth-child(1) { width: 48px; min-width: 48px; text-align: center; }
/* 大区 */
th:nth-child(2), td:nth-child(2) { width: 56px; min-width: 56px; text-align: center; }
/* 省份 */
th:nth-child(3), td:nth-child(3) { width: 64px; min-width: 64px; text-align: center; }
/* 招标单位 — 加宽 */
th:nth-child(4), td:nth-child(4) { width: 130px; min-width: 130px; text-align: left; }
/* 项目名称 — 加宽 */
th:nth-child(5), td:nth-child(5) { width: 240px; min-width: 240px; text-align: left; font-weight: 500; }
/* 项目概况 — 加宽并限制行数 */
th:nth-child(6), td:nth-child(6) { 
  width: 280px; 
  min-width: 280px; 
  text-align: left;
  max-width: 280px;
}
/* 预算金额 */
th:nth-child(7), td:nth-child(7) { width: 100px; min-width: 100px; text-align: right; font-weight: 500; }
/* 投标截止日期 — 关键信息加宽 */
th:nth-child(8), td:nth-child(8) { width: 120px; min-width: 120px; text-align: center; }
/* 招标方式 */
th:nth-child(9), td:nth-child(9) { width: 100px; min-width: 100px; text-align: center; }
/* 联系人 */
th:nth-child(10), td:nth-child(10) { width: 140px; min-width: 140px; text-align: left; font-size: 12px; color: var(--text-light); }
/* 业务标签 */
th:nth-child(11), td:nth-child(11) { width: 180px; min-width: 180px; text-align: left; }
/* 恒生投标建议 — 关键信息 */
th:nth-child(12), td:nth-child(12) { width: 120px; min-width: 120px; text-align: center; }
/* 来源 */
th:nth-child(13), td:nth-child(13) { width: 48px; min-width: 48px; text-align: center; }

/* ===== 长文本处理 — 多行省略 + 展开 ===== */
.cell-ellipsis {
  display: -webkit-box;
  -webkit-line-clamp: 3;        /* 限制3行 */
  -webkit-box-orient: vertical;
  overflow: hidden;
  line-height: 1.6;
  position: relative;
}

.cell-ellipsis.can-expand {
  cursor: pointer;
}

.cell-ellipsis.expanded {
  -webkit-line-clamp: unset;
  display: block;
}

/* 项目概况列专用样式 */
td:nth-child(6) {
  font-size: 12.5px;
  color: var(--text-light);
  line-height: 1.6;
}

/* 招标单位名称样式 */
td:nth-child(4) strong {
  color: var(--text);
  font-weight: 600;
}

/* 项目名称样式 */
td:nth-child(5) {
  color: var(--text);
  font-weight: 500;
}
```

**项目概况展开交互JS**

```javascript
// 项目概况展开/收起
document.querySelectorAll('td:nth-child(6)').forEach(cell => {
  const fullText = cell.getAttribute('title') || cell.textContent;
  if (cell.textContent.length > 80) {
    cell.classList.add('cell-ellipsis', 'can-expand');
    cell.addEventListener('click', function() {
      this.classList.toggle('expanded');
      if (this.classList.contains('expanded')) {
        this.textContent = fullText;
      } else {
        this.textContent = fullText.substring(0, 80) + '...';
      }
    });
  }
});
```

---

### 3. 信息层级优化

#### 问题
- 投标截止日期、恒生建议等关键决策信息未做视觉突出
- "强烈建议投标"与"不建议"的视觉差异不够明显
- 预算金额、截止日期等数字信息未使用等宽字体

#### 优化CSS

```css
/* ===== 关键信息突出 ===== */

/* 投标截止日期 — 增加紧迫感标识 */
td:nth-child(8) {
  font-weight: 500;
  white-space: nowrap;
}

td:nth-child(8).urgent {
  color: var(--accent);
  font-weight: 700;
  background: var(--accent-soft);
  border-radius: 4px;
  padding: 4px 8px;
  display: inline-block;
  margin: 6px 0;
}

td:nth-child(8).deadline-soon::before {
  content: '⏰ ';
}

/* 预算金额 — 等宽字体 + 右对齐 */
td:nth-child(7) {
  font-family: "SF Mono", Monaco, "Cascadia Code", "Roboto Mono", Consolas, "Courier New", monospace;
  font-weight: 600;
  color: var(--text);
  text-align: right;
  white-space: nowrap;
}

/* ===== 恒生投标建议强化 ===== */
.rec-strong {
  color: var(--accent);
  font-weight: 700;
  background: var(--accent-soft);
  padding: 5px 12px;
  border-radius: 6px;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  border: 1px solid #fecaca;
  font-size: 12px;
  white-space: nowrap;
}

.rec-strong::before {
  content: '🔥';
  font-size: 11px;
}

.rec-suggest {
  color: #b45309;
  font-weight: 600;
  background: var(--gold-soft);
  padding: 5px 12px;
  border-radius: 6px;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  border: 1px solid #fde68a;
  font-size: 12px;
  white-space: nowrap;
}

.rec-suggest::before {
  content: '★';
  color: var(--gold);
}

.rec-watch {
  color: var(--text-light);
  font-weight: 500;
  background: #f1f5f9;
  padding: 5px 12px;
  border-radius: 6px;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  border: 1px solid #e2e8f0;
  font-size: 12px;
  white-space: nowrap;
}

.rec-no {
  color: var(--text-muted);
  font-weight: 400;
  background: #f8fafc;
  padding: 5px 12px;
  border-radius: 6px;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  border: 1px solid var(--border);
  font-size: 12px;
  white-space: nowrap;
  opacity: 0.7;
}

/* 强烈建议行整体高亮 */
tr.has-strong-rec td {
  background: rgba(196, 30, 58, 0.02);
}

tr.has-strong-rec:hover td {
  background: rgba(196, 30, 58, 0.04);
}
```

---

### 4. 移动端适配优化

#### 问题
- 仅有一个768px断点，对平板（768px-1024px）无优化
- 小屏幕下表格横向滚动无视觉提示
- 筛选面板在移动端堆叠后过于冗长
- 统计卡片在移动端可能换行不整齐

#### 优化CSS

```css
/* ===== 响应式优化 ===== */

/* 平板断点 */
@media (max-width: 1024px) {
  .stats-bar {
    gap: 12px;
    padding: 24px 16px;
  }
  
  .stat-card {
    min-width: 140px;
    padding: 20px 24px;
  }
  
  .stat-card .number {
    font-size: 30px;
  }
  
  .filter-panel {
    margin: 0 12px 16px;
    padding: 16px 20px;
  }
  
  .container {
    padding: 0 12px 32px;
  }
  
  /* 表格最小宽度保证 */
  .table-wrap {
    margin: 0 -12px;
    padding: 0 12px;
  }
}

/* 手机断点 */
@media (max-width: 768px) {
  .cover {
    min-height: 320px;
    padding: 32px 20px 48px;
  }
  
  .cover h1 {
    font-size: 22px;
  }
  
  .cover-subtitle {
    font-size: 14px;
  }
  
  .cover-brand-text {
    font-size: 13px;
  }
  
  /* 统计卡片优化 */
  .stats-bar {
    gap: 8px;
    padding: 16px 12px;
  }
  
  .stat-card {
    min-width: calc(50% - 4px);   /* 两列布局 */
    padding: 16px;
    flex: 1 1 calc(50% - 4px);
  }
  
  .stat-card .number {
    font-size: 28px;
  }
  
  .stat-card .label {
    font-size: 12px;
  }
  
  /* 筛选面板优化 */
  .filter-panel {
    margin: 0 10px 12px;
    padding: 14px 16px;
    border-radius: 10px;
  }
  
  .filter-section {
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
  }
  
  .filter-section-title {
    text-align: left;
    min-width: auto;
  }
  
  .filter-row select,
  .filter-row input {
    width: 100%;
    min-width: auto;
  }
  
  /* 标签筛选横向滚动 */
  .biz-tag-filter {
    flex-wrap: nowrap;
    overflow-x: auto;
    padding-bottom: 4px;
    -webkit-overflow-scrolling: touch;
    scrollbar-width: none;
  }
  
  .biz-tag-filter::-webkit-scrollbar {
    display: none;
  }
  
  .filter-tag-btn {
    flex-shrink: 0;
  }
  
  /* 标签页优化 */
  .group-tabs {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
    scrollbar-width: none;
  }
  
  .group-tabs::-webkit-scrollbar {
    display: none;
  }
  
  .group-tab {
    padding: 12px 16px;
    font-size: 13px;
    flex-shrink: 0;
  }
  
  /* 表格优化 */
  .table-wrap {
    margin: 0 -10px;
    padding: 0 10px;
  }
  
  table {
    font-size: 12px;
  }
  
  th, td {
    padding: 10px 8px;
  }
  
  /* 结果计数 */
  .result-count {
    padding: 12px 14px;
    font-size: 12px;
  }
  
  /* 容器 */
  .container {
    padding: 0 10px 24px;
  }
  
  .section {
    border-radius: 10px;
    margin-bottom: 16px;
  }
}

/* 小手机断点 */
@media (max-width: 480px) {
  .stat-card {
    min-width: 100%;              /* 单列 */
    flex: 1 1 100%;
  }
  
  .cover h1 {
    font-size: 20px;
  }
  
  .cover-badge {
    font-size: 11px;
    padding: 6px 16px;
  }
}
```

---

### 5. 动效与微交互优化

#### 问题
- 标签页切换无过渡动画，生硬跳变
- 筛选结果变化无反馈
- 统计卡片hover只有位移，缺少精致感
- 无加载状态提示
- 链接hover缩放1.2过于突兀

#### 优化CSS + JS

```css
/* ===== 标签页切换动画 ===== */
.tab-content {
  display: none;
  opacity: 0;
  transform: translateY(8px);
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.tab-content.active {
  display: block;
  opacity: 1;
  transform: translateY(0);
  animation: tabFadeIn 0.35s ease;
}

@keyframes tabFadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to   { opacity: 1; transform: translateY(0); }
}

/* 标签指示器滑动效果 */
.group-tab {
  position: relative;
  transition: color 0.2s, background 0.2s;
}

.group-tab::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 50%;
  width: 0;
  height: 3px;
  background: var(--primary);
  transition: all 0.3s ease;
  transform: translateX(-50%);
  border-radius: 2px 2px 0 0;
}

.group-tab.active::after {
  width: 60%;
}

/* ===== 统计卡片hover优化 ===== */
.stat-card {
  position: relative;
  overflow: hidden;
  transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1), 
              box-shadow 0.3s ease;
}

.stat-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: var(--primary-light);
  transform: scaleX(0);
  transition: transform 0.3s ease;
  transform-origin: left;
}

.stat-card:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow-lg);
}

.stat-card:hover::before {
  transform: scaleX(1);
}

.stat-card.strong::before {
  background: var(--accent);
}

.stat-card.suggest::before {
  background: var(--gold);
}

/* 数字变化动画 */
@keyframes numberPop {
  0%   { transform: scale(1); }
  50%  { transform: scale(1.15); }
  100% { transform: scale(1); }
}

.stat-card:hover .number {
  animation: numberPop 0.4s ease;
}

/* ===== 链接hover优化 ===== */
.url-link {
  color: var(--primary-light);
  text-decoration: none;
  font-size: 14px;
  transition: all 0.2s ease;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 8px;
}

.url-link:hover {
  background: var(--primary-soft);
  transform: scale(1.05);
  color: var(--primary);
}

/* ===== 加载状态 ===== */
.loading-overlay {
  display: none;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255,255,255,0.85);
  backdrop-filter: blur(4px);
  z-index: 1000;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  gap: 16px;
}

.loading-overlay.show {
  display: flex;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--border);
  border-top-color: var(--primary-light);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-text {
  font-size: 14px;
  color: var(--text-light);
  font-weight: 500;
}

/* ===== 筛选按钮点击反馈 ===== */
.filter-tag-btn:active,
.filter-btn:active,
.reset-btn:active {
  transform: scale(0.96);
}

/* ===== 行出现动画 ===== */
tr {
  animation: rowIn 0.3s ease;
}

@keyframes rowIn {
  from { opacity: 0; transform: translateX(-8px); }
  to   { opacity: 1; transform: translateX(0); }
}
```

**加载状态HTML**

```html
<!-- 加载遮罩 -->
<div class="loading-overlay" id="loading-overlay">
  <div class="loading-spinner"></div>
  <div class="loading-text">数据加载中...</div>
</div>
```

---

## 四、整体优化后的完整CSS样式建议

以下是整合所有优化后的完整CSS，可直接替换原文件中的`<style>`内容：

```css
:root {
  --primary: #0f2a4a;
  --primary-light: #1e4a7a;
  --primary-soft: #e8f0f8;
  --accent: #c41e3a;
  --accent-light: #e85d75;
  --accent-soft: #fef2f2;
  --gold: #b8860b;
  --gold-light: #d4a843;
  --gold-soft: #fffbeb;
  --bg: #f5f7fa;
  --card: #ffffff;
  --text: #1a202c;
  --text-light: #64748b;
  --text-muted: #94a3b8;
  --border: #e2e8f0;
  --border-light: #f1f5f9;
  --shadow-sm: 0 1px 3px rgba(0,0,0,0.04);
  --shadow: 0 4px 16px rgba(15, 42, 74, 0.08);
  --shadow-lg: 0 8px 30px rgba(15, 42, 74, 0.12);
  --radius: 10px;
  --radius-sm: 6px;
}

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
  background: var(--bg);
  color: var(--text);
  line-height: 1.6;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* ===== 封面 ===== */
.cover {
  background: linear-gradient(145deg, #0a2540 0%, #1e3a5f 50%, #2c5282 100%);
  min-height: 420px;
  max-height: 520px;
  height: auto;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  color: white;
  padding: 48px 40px 64px;
  position: relative;
  overflow: hidden;
}

.cover::before {
  content: "";
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(255,255,255,0.03) 1px, transparent 1px);
  background-size: 40px 40px;
  opacity: 0.5;
}

.cover-content { position: relative; z-index: 2; max-width: 800px; }

.cover-brand {
  position: relative;
  z-index: 2;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-bottom: 24px;
}

.cover-brand-logo {
  width: 36px;
  height: 36px;
  background: var(--gold);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 14px;
  color: #1e3a5f;
  letter-spacing: 1px;
}

.cover-brand-text {
  font-size: 15px;
  font-weight: 600;
  letter-spacing: 3px;
  opacity: 0.95;
}

.cover-badge {
  display: inline-block;
  background: rgba(255,255,255,0.12);
  backdrop-filter: blur(10px);
  padding: 6px 18px;
  border-radius: 30px;
  font-size: 12px;
  letter-spacing: 2px;
  margin-bottom: 20px;
  border: 1px solid rgba(255,255,255,0.15);
}

.cover h1 {
  font-size: 32px;
  font-weight: 700;
  margin-bottom: 12px;
  letter-spacing: 1px;
  line-height: 1.3;
}

.cover-subtitle {
  font-size: 16px;
  opacity: 0.85;
  margin-bottom: 8px;
  font-weight: 400;
}

.cover-meta {
  font-size: 13px;
  opacity: 0.65;
  margin-bottom: 8px;
}

.cover-author {
  font-size: 14px;
  margin-top: 20px;
  padding: 10px 24px;
  background: rgba(255,255,255,0.08);
  border-radius: 8px;
  border-left: 3px solid var(--gold);
  display: inline-block;
}

.scroll-hint, .cover-disclaimer { display: none; }

/* ===== 统计栏 ===== */
.stats-bar {
  display: flex;
  justify-content: center;
  gap: 16px;
  padding: 30px 20px;
  flex-wrap: wrap;
  max-width: 1400px;
  margin: 0 auto;
}

.stat-card {
  background: var(--card);
  border-radius: var(--radius);
  padding: 24px 32px;
  text-align: center;
  box-shadow: var(--shadow);
  min-width: 160px;
  position: relative;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1), box-shadow 0.3s ease;
}

.stat-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: var(--primary-light);
  transform: scaleX(0);
  transition: transform 0.3s ease;
  transform-origin: left;
}

.stat-card:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow-lg);
}

.stat-card:hover::before { transform: scaleX(1); }
.stat-card.strong::before { background: var(--accent); }
.stat-card.suggest::before { background: var(--gold); }

.stat-card .number {
  font-size: 36px;
  font-weight: 700;
  color: var(--primary-light);
  margin-bottom: 4px;
  transition: all 0.3s;
}

.stat-card:hover .number { animation: numberPop 0.4s ease; }

.stat-card .label {
  font-size: 13px;
  color: var(--text-light);
}

.stat-card.strong .number { color: var(--accent); }
.stat-card.suggest .number { color: var(--gold); }

@keyframes numberPop {
  0%   { transform: scale(1); }
  50%  { transform: scale(1.15); }
  100% { transform: scale(1); }
}

/* ===== 筛选栏 ===== */
.filter-panel {
  background: var(--card);
  border-radius: var(--radius);
  padding: 20px 24px;
  margin: 0 20px 20px;
  box-shadow: var(--shadow);
  max-width: 1400px;
  margin-left: auto;
  margin-right: auto;
}

.filter-section {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 14px;
  align-items: center;
}

.filter-section:last-child { margin-bottom: 0; }

.filter-section-title {
  font-size: 12px;
  color: var(--text-light);
  font-weight: 500;
  min-width: 80px;
  text-align: right;
}

.filter-row select,
.filter-row input {
  padding: 8px 32px 8px 12px;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  font-size: 13px;
  background: white;
  min-width: 160px;
  cursor: pointer;
  outline: none;
  transition: all 0.2s;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg width='10' height='6' viewBox='0 0 10 6' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M1 1l4 4 4-4' stroke='%23718096' stroke-width='1.5' fill='none'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 12px center;
}

.filter-row select:focus,
.filter-row input:focus {
  border-color: var(--primary-light);
  box-shadow: 0 0 0 3px rgba(30, 74, 122, 0.08);
}

.filter-row input[type="text"] {
  min-width: 240px;
  padding-left: 36px;
  background-image: url("data:image/svg+xml,%3Csvg width='16' height='16' viewBox='0 0 16 16' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M11.7422 10.3439C12.5329 9.2673 13 7.9382 13 6.5C13 2.91015 10.0899 0 6.5 0C2.91015 0 0 2.91015 0 6.5C0 10.0899 2.91015 13 6.5 13C7.9382 13 9.2673 12.5329 10.3439 11.7422L14.1464 15.5446C14.3417 15.7399 14.6583 15.7399 14.8536 15.5446L15.5446 14.8536C15.7399 14.6583 15.7399 14.3417 15.5446 14.1464L11.7422 10.3439ZM6.5 11C4.01472 11 2 8.98528 2 6.5C2 4.01472 4.01472 2 6.5 2C8.98528 2 11 4.01472 11 6.5C11 8.98528 8.98528 11 6.5 11Z' fill='%23718096'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: left 12px center;
}

.filter-row input::placeholder { color: #a0aec0; }

.filter-btn {
  padding: 8px 18px;
  background: var(--primary);
  color: white;
  border: none;
  border-radius: var(--radius-sm);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
  font-weight: 500;
}

.filter-btn:hover {
  background: var(--primary-light);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(30, 58, 95, 0.2);
}

.reset-btn {
  padding: 8px 18px;
  background: transparent;
  color: var(--text-light);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
  font-weight: 500;
}

.reset-btn:hover {
  background: #edf2f7;
  color: var(--text);
  border-color: #cbd5e0;
}

.filter-btn:active, .reset-btn:active { transform: scale(0.96); }

/* 已选条件 */
.active-filters {
  display: none;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  min-height: 32px;
  padding: 10px 0 0;
  border-top: 1px dashed var(--border);
  margin-top: 10px;
}

.active-filters.show { display: flex; }

.active-filters-label {
  font-size: 12px;
  color: var(--text-light);
  font-weight: 500;
}

.active-filter-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  background: var(--primary-soft);
  color: var(--primary-light);
  border-radius: 16px;
  font-size: 12px;
  font-weight: 500;
  border: 1px solid #cbd5e1;
  animation: tagIn 0.25s ease;
}

.active-filter-tag .remove {
  cursor: pointer;
  width: 14px;
  height: 14px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: rgba(30, 74, 122, 0.12);
  font-size: 10px;
  transition: background 0.2s;
}

.active-filter-tag .remove:hover { background: rgba(30, 74, 122, 0.25); }

@keyframes tagIn {
  from { opacity: 0; transform: scale(0.8) translateY(-4px); }
  to   { opacity: 1; transform: scale(1) translateY(0); }
}

/* 业务标签筛选 */
.biz-tag-filter {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  align-items: center;
}

.filter-tag-btn {
  padding: 6px 14px;
  border: 1px solid var(--border);
  border-radius: 20px;
  background: white;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
  color: var(--text-light);
  font-weight: 500;
  white-space: nowrap;
}

.filter-tag-btn:hover {
  background: var(--primary);
  color: white;
  border-color: var(--primary);
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(15, 42, 74, 0.15);
}

.filter-tag-btn.active {
  background: var(--primary);
  color: white;
  border-color: var(--primary);
  box-shadow: 0 2px 8px rgba(15, 42, 74, 0.2);
}

.filter-tag-btn:active { transform: scale(0.96); }

/* ===== 标签页 ===== */
.container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 20px 40px;
}

.section {
  background: var(--card);
  border-radius: var(--radius);
  margin-bottom: 24px;
  box-shadow: var(--shadow);
  overflow: hidden;
}

.group-tabs {
  display: flex;
  gap: 0;
  border-bottom: 1px solid var(--border);
  background: #f8fafc;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none;
}

.group-tabs::-webkit-scrollbar { display: none; }

.group-tab {
  padding: 14px 28px;
  cursor: pointer;
  border-bottom: 3px solid transparent;
  font-weight: 500;
  font-size: 14px;
  color: var(--text-light);
  transition: all 0.2s;
  white-space: nowrap;
  position: relative;
}

.group-tab.active {
  border-bottom-color: var(--primary);
  color: var(--primary);
  background: white;
}

.group-tab:hover {
  color: var(--primary);
  background: rgba(30, 74, 122, 0.03);
}

.group-tab::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 50%;
  width: 0;
  height: 3px;
  background: var(--primary);
  transition: all 0.3s ease;
  transform: translateX(-50%);
  border-radius: 2px 2px 0 0;
}

.group-tab.active::after { width: 60%; }

.tab-content {
  display: none;
  opacity: 0;
  transform: translateY(8px);
}

.tab-content.active {
  display: block;
  opacity: 1;
  transform: translateY(0);
  animation: tabFadeIn 0.35s ease;
}

@keyframes tabFadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to   { opacity: 1; transform: translateY(0); }
}

/* ===== 表格 ===== */
.table-wrap {
  overflow-x: auto;
  padding: 0;
  background:
    linear-gradient(to right, white 30%, transparent),
    linear-gradient(to left, white 30%, transparent),
    linear-gradient(to right, rgba(0,0,0,0.04), transparent 10px),
    linear-gradient(to left, rgba(0,0,0,0.04), transparent 10px);
  background-position: left center, right center, left center, right center;
  background-repeat: no-repeat;
  background-size: 20px 100%, 20px 100%, 10px 100%, 10px 100%;
  background-attachment: local, local, scroll, scroll;
}

table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  font-size: 13px;
  min-width: 1200px;
}

th {
  background: #f8fafc;
  padding: 14px 12px;
  text-align: center;
  font-weight: 600;
  color: var(--primary);
  border-bottom: 2px solid var(--primary-light);
  white-space: nowrap;
  font-size: 12px;
  position: sticky;
  top: 0;
  z-index: 10;
  letter-spacing: 0.5px;
}

td {
  padding: 14px 12px;
  border-bottom: 1px solid var(--border-light);
  vertical-align: top;
  text-align: center;
  transition: background 0.15s;
  line-height: 1.5;
}

tr { position: relative; transition: all 0.15s; }

tr:hover { background: #f8fafc; }

tr:hover td:first-child::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
  background: var(--primary-light);
  border-radius: 0 2px 2px 0;
}

tbody tr:nth-child(even) { background: #fafbfc; }
tbody tr:nth-child(even):hover { background: #f0f4f8; }

/* 列宽 */
th:nth-child(1), td:nth-child(1) { width: 48px; min-width: 48px; text-align: center; }
th:nth-child(2), td:nth-child(2) { width: 56px; min-width: 56px; text-align: center; }
th:nth-child(3), td:nth-child(3) { width: 64px; min-width: 64px; text-align: center; }
th:nth-child(4), td:nth-child(4) { width: 130px; min-width: 130px; text-align: left; }
th:nth-child(5), td:nth-child(5) { width: 240px; min-width: 240px; text-align: left; font-weight: 500; }
th:nth-child(6), td:nth-child(6) { width: 280px; min-width: 280px; text-align: left; max-width: 280px; font-size: 12.5px; color: var(--text-light); }
th:nth-child(7), td:nth-child(7) { width: 100px; min-width: 100px; text-align: right; font-weight: 600; font-family: "SF Mono", Monaco, "Cascadia Code", "Roboto Mono", Consolas, "Courier New", monospace; }
th:nth-child(8), td:nth-child(8) { width: 120px; min-width: 120px; text-align: center; font-weight: 500; }
th:nth-child(9), td:nth-child(9) { width: 100px; min-width: 100px; text-align: center; }
th:nth-child(10), td:nth-child(10) { width: 140px; min-width: 140px; text-align: left; font-size: 12px; color: var(--text-light); }
th:nth-child(11), td:nth-child(11) { width: 180px; min-width: 180px; text-align: left; }
th:nth-child(12), td:nth-child(12) { width: 120px; min-width: 120px; text-align: center; }
th:nth-child(13), td:nth-child(13) { width: 48px; min-width: 48px; text-align: center; }

/* 长文本省略 */
.cell-ellipsis {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  line-height: 1.6;
  cursor: pointer;
  transition: all 0.2s;
}

.cell-ellipsis:hover { color: var(--text); }
.cell-ellipsis.expanded {
  -webkit-line-clamp: unset;
  display: block;
}

/* 标签样式 */
.biz-tag {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 12px;
  font-size: 11px;
  margin: 2px;
  cursor: pointer;
  transition: all 0.2s;
  background: var(--primary-soft);
  color: var(--primary-light);
  border: 1px solid #cbd5e1;
  font-weight: 500;
}

.biz-tag:hover {
  background: var(--primary-light);
  color: white;
  transform: scale(1.05);
  box-shadow: 0 2px 6px rgba(15, 42, 74, 0.15);
}

/* 建议样式 */
.rec-strong {
  color: var(--accent);
  font-weight: 700;
  background: var(--accent-soft);
  padding: 5px 12px;
  border-radius: 6px;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  border: 1px solid #fecaca;
  font-size: 12px;
  white-space: nowrap;
}

.rec-suggest {
  color: #b45309;
  font-weight: 600;
  background: var(--gold-soft);
  padding: 5px 12px;
  border-radius: 6px;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  border: 1px solid #fde68a;
  font-size: 12px;
  white-space: nowrap;
}

.rec-watch {
  color: var(--text-light);
  font-weight: 500;
  background: #f1f5f9;
  padding: 5px 12px;
  border-radius: 6px;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  border: 1px solid var(--border);
  font-size: 12px;
  white-space: nowrap;
}

.rec-no {
  color: var(--text-muted);
  font-weight: 400;
  background: #f8fafc;
  padding: 5px 12px;
  border-radius: 6px;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  border: 1px solid var(--border);
  font-size: 12px;
  white-space: nowrap;
  opacity: 0.7;
}

/* 链接 */
.url-link {
  color: var(--primary-light);
  text-decoration: none;
  font-size: 14px;
  transition: all 0.2s ease;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 8px;
}

.url-link:hover {
  background: var(--primary-soft);
  transform: scale(1.05);
  color: var(--primary);
}

/* ===== 空状态 ===== */
.empty-state {
  display: none;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
  color: var(--text-light);
}

.empty-state.show {
  display: flex;
  animation: fadeIn 0.4s ease;
}

.empty-state-icon {
  width: 64px;
  height: 64px;
  background: #f7fafc;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  margin-bottom: 16px;
}

.empty-state h4 {
  font-size: 16px;
  color: var(--text);
  margin-bottom: 8px;
  font-weight: 600;
}

.empty-state p {
  font-size: 13px;
  color: var(--text-light);
  margin-bottom: 16px;
  max-width: 400px;
  line-height: 1.6;
}

.empty-state .reset-link {
  color: var(--primary-light);
  font-size: 13px;
  cursor: pointer;
  text-decoration: underline;
  font-weight: 500;
}

/* ===== 结果计数 ===== */
.result-count {
  padding: 14px 20px;
  font-size: 13px;
  color: var(--text-light);
  border-bottom: 1px solid var(--border);
  background: #fafbfc;
  display: flex;
  align-items: center;
  gap: 6px;
}

.result-count span {
  font-weight: 700;
  color: var(--primary);
  font-size: 15px;
  display: inline-block;
  min-width: 20px;
  text-align: center;
  transition: all 0.3s ease;
}

.result-count span.changed {
  color: var(--accent);
  transform: scale(1.2);
}

/* ===== 封底 ===== */
.footer-section {
  background: linear-gradient(145deg, #0a2540 0%, #1e3a5f 100%);
  color: white;
  padding: 60px 40px;
  text-align: center;
  margin-top: 40px;
}

.footer-brand {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-bottom: 20px;
}

.footer-brand .cover-brand-logo {
  background: var(--gold);
  color: #1e3a5f;
}

.footer-brand span {
  font-size: 16px;
  font-weight: 600;
  letter-spacing: 2px;
}

.footer-section h2 {
  font-size: 22px;
  margin-bottom: 16px;
  font-weight: 600;
}

.footer-section p {
  font-size: 14px;
  opacity: 0.8;
  line-height: 2;
  max-width: 700px;
  margin: 0 auto;
}

.footer-disclaimer {
  font-size: 12px;
  opacity: 0.6;
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid rgba(255,255,255,0.2);
  max-width: 800px;
  margin-left: auto;
  margin-right: auto;
  line-height: 1.8;
}

/* ===== 加载状态 ===== */
.loading-overlay {
  display: none;
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(255,255,255,0.85);
  backdrop-filter: blur(4px);
  z-index: 1000;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  gap: 16px;
}

.loading-overlay.show { display: flex; }

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--border);
  border-top-color: var(--primary-light);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }

.loading-text {
  font-size: 14px;
  color: var(--text-light);
  font-weight: 500;
}

/* ===== 响应式 ===== */
@media (max-width: 1024px) {
  .stats-bar { gap: 12px; padding: 24px 16px; }
  .stat-card { min-width: 140px; padding: 20px 24px; }
  .stat-card .number { font-size: 30px; }
  .filter-panel { margin: 0 12px 16px; padding: 16px 20px; }
  .container { padding: 0 12px 32px; }
  .table-wrap { margin: 0 -12px; padding: 0 12px; }
}

@media (max-width: 768px) {
  .cover { min-height: 320px; padding: 32px 20px 48px; }
  .cover h1 { font-size: 22px; }
  .cover-subtitle { font-size: 14px; }
  .cover-brand-text { font-size: 13px; }
  
  .stats-bar { gap: 8px; padding: 16px 12px; }
  .stat-card { min-width: calc(50% - 4px); padding: 16px; flex: 1 1 calc(50% - 4px); }
  .stat-card .number { font-size: 28px; }
  .stat-card .label { font-size: 12px; }
  
  .filter-panel { margin: 0 10px 12px; padding: 14px 16px; border-radius: 10px; }
  .filter-section { flex-direction: column; align-items: stretch; gap: 8px; }
  .filter-section-title { text-align: left; min-width: auto; }
  .filter-row select, .filter-row input { width: 100%; min-width: auto; }
  
  .biz-tag-filter { flex-wrap: nowrap; overflow-x: auto; padding-bottom: 4px; -webkit-overflow-scrolling: touch; scrollbar-width: none; }
  .biz-tag-filter::-webkit-scrollbar { display: none; }
  .filter-tag-btn { flex-shrink: 0; }
  
  .group-tabs { overflow-x: auto; -webkit-overflow-scrolling: touch; scrollbar-width: none; }
  .group-tabs::-webkit-scrollbar { display: none; }
  .group-tab { padding: 12px 16px; font-size: 13px; flex-shrink: 0; }
  
  .table-wrap { margin: 0 -10px; padding: 0 10px; }
  table { font-size: 12px; }
  th, td { padding: 10px 8px; }
  .result-count { padding: 12px 14px; font-size: 12px; }
  .container { padding: 0 10px 24px; }
  .section { border-radius: 10px; margin-bottom: 16px; }
}

@media (max-width: 480px) {
  .stat-card { min-width: 100%; flex: 1 1 100%; }
  .cover h1 { font-size: 20px; }
  .cover-badge { font-size: 11px; padding: 6px 16px; }
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to   { opacity: 1; transform: translateY(0); }
}
```

---

## 五、HTML结构调整建议

### 1. 封面结构

```html
<div class="cover">
  <div class="cover-content">
    <div class="cover-brand">
      <div class="cover-brand-logo">HS</div>
      <div class="cover-brand-text">HUNDSUN · 恒生电子</div>
    </div>
    <div class="cover-badge">CONFIDENTIAL · INTERNAL USE ONLY</div>
    <h1>恒生电子银信事业群<br>招标市场需求监控看板</h1>
    <div class="cover-subtitle">银行信托事业群销售 / 解决方案 / 售前专用</div>
    <div class="cover-meta">覆盖银行 / 银行系科技子公司 / 银行理财子公司 / 信托公司</div>
    <div class="cover-meta">数据更新时间：2026年6月8日</div>
    <div class="cover-author">编制单位：恒生电子银信解决方案部</div>
  </div>
</div>
```

### 2. 筛选面板结构（增加已选条件栏和空状态）

```html
<div class="filter-panel">
  <div class="filter-section">
    <span class="filter-section-title">基础筛选</span>
    <div class="filter-row">
      <select id="filter-province" onchange="applyFilters()">...</select>
      <select id="filter-method" onchange="applyFilters()">...</select>
      <select id="filter-rec" onchange="applyFilters()">...</select>
      <input type="text" id="filter-search" placeholder="搜索项目名称..." oninput="applyFilters()">
      <button class="reset-btn" onclick="resetFilters()">重置筛选</button>
    </div>
  </div>
  <div class="filter-section">
    <span class="filter-section-title">业务标签</span>
    <div class="biz-tag-filter">...</div>
  </div>
  <!-- 已选条件动态展示 -->
  <div class="active-filters" id="active-filters-bar"></div>
</div>
```

### 3. 每个标签页内容增加空状态

```html
<div id="tab-all" class="tab-content active">
  <div class="result-count">显示 <span id="count-all">72</span> 条记录</div>
  <div class="empty-state" id="empty-all">
    <div class="empty-state-icon">🔍</div>
    <h4>未找到匹配的记录</h4>
    <p>当前筛选条件下没有符合条件的招标项目，请尝试调整筛选条件或重置筛选。</p>
    <span class="reset-link" onclick="resetFilters()">重置所有筛选条件</span>
  </div>
  <div class="table-wrap">...</div>
</div>
```

### 4. 封底增加品牌元素

```html
<div class="footer-section">
  <div class="footer-brand">
    <div class="cover-brand-logo">HS</div>
    <span>恒生电子 HUNDSUN</span>
  </div>
  <h2>恒生电子银信事业群招标市场需求监控看板</h2>
  <p>编制单位：恒生电子银信解决方案部<br>数据更新时间：2026年6月8日<br>每天早上 8:00 自动更新推送</p>
  <div class="footer-disclaimer">...</div>
</div>
```

---

## 六、实施优先级建议

### 第一阶段（立即实施）
1. **缩小封面**：将 `min-height: 100vh` 改为 `min-height: 420px`
2. **增加品牌元素**：在封面和封底增加恒生电子Logo标识
3. **表格行高优化**：td padding从10px增加到14px
4. **修复筛选空状态**：增加空状态提示HTML和JS逻辑

### 第二阶段（本周内）
5. **筛选体验升级**：增加已选条件展示栏、搜索图标、计数动画
6. **信息层级强化**：投标建议标签视觉差异化、预算金额等宽字体
7. **链接hover优化**：替换scale(1.2)为更精致的背景高亮

### 第三阶段（后续迭代）
8. **移动端全面适配**：增加1024px和480px断点
9. **动效打磨**：标签页切换动画、行出现动画
10. **项目概况展开交互**：实现点击展开长文本功能

---

## 七、设计原则总结

| 原则 | 在本看板中的体现 |
|---|---|
| **效率优先** | 首屏直接展示数据，减少滚动；筛选反馈即时 |
| **信息降噪** | 弱化"不建议"项目；空状态清晰引导 |
| **品牌一致** | 恒生电子蓝金配色；Logo标识贯穿首尾 |
| **金融质感** | 沉稳配色、等宽数字、清晰层级、专业排版 |
| **细节精致** | 微交互动画、hover反馈、加载状态、滚动提示 |

---

> **报告完成**。以上所有CSS代码片段均经过兼容性考虑，支持现代浏览器（Chrome 90+、Edge 90+、Safari 14+、Firefox 88+）。如需进一步细化任何模块，可继续深入讨论。
