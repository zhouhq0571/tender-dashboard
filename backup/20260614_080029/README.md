# 恒生银信招标看板 - 公共链接部署指南

## 🎯 目标
将 `恒生银信招标需求每日速递_2026年6月8日.html` 变成一个**互联网公共链接**，同事点击即可在任何设备上查看。

---

## 方案一：GitHub Pages（推荐 ⭐）

**优点**：免费、永久、HTTPS、可绑定自定义域名

### 步骤

#### 第 1 步：注册 GitHub 账号（5分钟）
1. 打开 https://github.com/signup
2. 输入邮箱、密码、用户名
3. 验证邮箱

#### 第 2 步：生成 Personal Access Token
1. 打开 https://github.com/settings/tokens/new
2. 勾选 **repo** 权限（完整控制仓库）
3. 点击 **Generate token**
4. **立即复制 Token**（页面关闭后无法再次查看）

#### 第 3 步：运行部署脚本
1. 编辑 `deploy-to-github.sh` 文件：
   ```bash
   GITHUB_USERNAME="你的GitHub用户名"
   GITHUB_TOKEN="刚才复制的Token"
   ```
2. 打开终端，进入此目录：
   ```bash
   cd /Users/zhouhq/Documents/kimi/workspace/research/github-pages-deploy
   ```
3. 运行脚本：
   ```bash
   bash deploy-to-github.sh
   ```

#### 第 4 步：获得公共链接
部署成功后，你会获得类似这样的链接：
```
https://zhangsan.github.io/tender-dashboard/
```

将此链接发给同事，任何设备都能直接打开！

---

## 方案二：Netlify Drop（最简单 🚀）

**优点**：无需注册、无需命令行、拖拽上传、即时获得链接

### 步骤

1. 打开 https://app.netlify.com/drop
2. 将 `index.html` 文件**直接拖拽**到网页上
3. 等待 3 秒，自动获得公共链接：
   ```
   https://xxx-xxx-xxx.netlify.app
   ```
4. 复制链接发给同事

> ⚠️ 注意：Netlify Drop 的链接是随机的，每次重新上传会生成新链接。如果需要固定链接，建议用方案一（GitHub Pages）。

---

## 方案三：腾讯云 COS / 阿里云 OSS

适合已有云账号的用户，上传文件后开启公共读权限即可获得固定链接。

---

## 📱 分享效果

同事收到链接后：
- **手机**：微信/钉钉点击链接 → 浏览器打开 → 完整看板
- **电脑**：点击链接 → 浏览器打开 → 完整看板
- **体验**：与您本地打开完全一致（筛选、排序、标签页均可用）

---

## 🔗 当前文件

| 文件 | 说明 |
|------|------|
| `index.html` | 招标看板网页（已复制到本目录） |
| `deploy-to-github.sh` | GitHub Pages 一键部署脚本 |
| `README.md` | 本说明文件 |

---

## ❓ 常见问题

**Q：为什么本地文件路径不能发给同事？**
A：`file:///Users/zhouhq/...` 是您电脑上的路径，同事的电脑上没有这个文件，所以打不开。

**Q：GitHub Pages 链接是永久的吗？**
A：是的，只要仓库存在，链接就永久有效。您可以随时更新文件重新部署。

**Q：需要付费吗？**
A：GitHub Pages 和 Netlify Drop 都是免费的。

**Q：数据安全吗？**
A：GitHub Pages 是公开仓库，任何人都能访问。如果数据敏感，建议：
1. 使用 GitHub 私有仓库 + 密码保护
2. 或仅在内部网络分享文件（不生成公共链接）
