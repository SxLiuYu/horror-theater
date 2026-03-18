# RunwayML API 使用指南

## 📝 准备工作

### 1. 注册账号

访问：https://runwayml.com

- 点击右上角 "Sign Up Free"
- 用 Google 账号或邮箱注册
- 验证邮箱

### 2. 获取 API Key

1. 登录：https://app.runwayml.com
2. 点击左下角头像 → "Settings"
3. 选择 "API Keys" 标签
4. 点击 "Create New Key"
5. 复制 API Key（只显示一次！）

### 3. 设置环境变量

**Linux/Mac:**
```bash
export RUNWAY_API_KEY="你的 API Key"
```

**Windows (PowerShell):**
```powershell
$env:RUNWAY_API_KEY="你的 API Key"
```

**永久设置（推荐）:**
```bash
# 添加到 ~/.bashrc 或 ~/.zshrc
echo 'export RUNWAY_API_KEY="你的 API Key"' >> ~/.bashrc
source ~/.bashrc
```

---

## 🚀 快速开始

### 测试脚本

```bash
# 进入目录
cd horror-theater/tools

# 列出所有可用提示词
python runway_api_test.py list

# 测试生成（陆离卧室场景）
python runway_api_test.py test 陆离_卧室

# 测试其他场景
python runway_api_test.py test 苏晓_登场
python runway_api_test.py test 恐怖_小区

# 使用自定义提示词
python runway_api_test.py "A cat sitting on a windowsill, anime style"
```

---

## 📋 提示词库

脚本内置了 8 个预设提示词：

| 场景名 | 描述 | 推荐 |
|--------|------|------|
| `陆离_卧室` | 第 1 集 - 陆离卧室醒来 | ⭐⭐⭐ |
| `陆离_公交` | 第 1 集 - 末班公交车 | ⭐⭐⭐ |
| `苏晓_登场` | 第 3 集 - 苏晓首次登场 | ⭐⭐⭐ |
| `小太阳_APP` | APP 界面 - 小太阳图标 | ⭐⭐ |
| `恐怖_小区` | 第 2 集 - 槐安小区 | ⭐⭐⭐ |
| `治愈_超度` | 通用 - 鬼魂超度场景 | ⭐⭐⭐ |
| `研究所_培养皿` | 彩蛋 - 心灵研究所 | ⭐⭐ |
| `游乐园_摩天轮` | 第 5/10 集 - 摩天轮 | ⭐⭐⭐ |

---

## 🎬 输出文件

生成成功后会创建：

```
horror-theater/tools/
├── output_陆离_卧室.mp4      # 视频文件
├── output_陆离_卧室.mp4.json  # 元数据（提示词、URL 等）
```

---

## ⚙️ 高级配置

### 修改视频参数

编辑 `runway_api_test.py`，找到 `test_generation` 函数：

```python
# 修改时长（秒）
task_id = create_task(prompt, duration=4, resolution="720p")

# 可选值：
# duration: 4-16 秒
# resolution: "720p" 或 "1080p"
```

### 批量生成

创建批量脚本 `batch_generate.py`：

```python
from runway_api_test import test_generation

scenes = ["陆离_卧室", "苏晓_登场", "恐怖_小区"]

for scene in scenes:
    test_generation(scene)
```

---

## 💰 免费额度说明

- **新用户**：125 积分（约 25 秒视频）
- **消耗**：约 5 积分/秒（720p）
- **刷新**：不刷新，用完需充值或等新号

### 推荐测试顺序

1. `小太阳_APP`（4 秒）- 测试基础功能
2. `陆离_卧室`（4 秒）- 测试角色
3. `治愈_超度`（4 秒）- 测试特效
4. 其他场景...

**总计**：约 12 秒，剩余 13 积分

---

## 🔧 常见问题

### Q: API Key 无效？
A: 检查是否正确复制，确保没有多余空格

### Q: 任务一直处于 QUEUED？
A: Runway 服务器可能繁忙，等待或重试

### Q: 生成失败？
A: 检查提示词是否违规（暴力、成人内容等）

### Q: 视频质量不好？
A: 尝试添加更多细节描述，如 "studio ghibli inspired, detailed"

---

## 📚 API 文档

- 官方文档：https://docs.runwayml.com
- API 参考：https://docs.runwayml.com/reference
- 示例代码：https://github.com/runwayml/python-sdk

---

## 🎯 下一步

1. ✅ 测试基础功能
2. ⏳ 生成角色测试视频
3. ⏳ 生成场景测试视频
4. ⏳ 批量生成各集关键场景
5. ⏳ 导入剪辑软件组装

---

*文档版本：v1.0*
*创建日期：2026-03-18 15:30*
