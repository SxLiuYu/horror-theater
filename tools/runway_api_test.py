#!/usr/bin/env python3
"""
RunwayML Gen-2 API 测试脚本
用于生成《治愈系恐怖游戏》动态漫剧测试视频

使用前：
1. 注册 RunwayML: https://runwayml.com
2. 获取 API Key: Settings → API Keys
3. 设置环境变量：export RUNWAY_API_KEY="你的 key"

文档：https://docs.runwayml.com
"""

import os
import requests
import time
import json

# ========== 配置 ==========
API_KEY = os.getenv("RUNWAY_API_KEY", "")
BASE_URL = "https://api.runwayml.com/v1"

# 如果没有 API Key，提示用户
if not API_KEY:
    print("❌ 错误：未设置 RUNWAY_API_KEY 环境变量")
    print("请运行：export RUNWAY_API_KEY=\"你的 key\"")
    print("或者在代码中直接设置：API_KEY = \"你的 key\"")
    exit(1)

# 请求头
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "X-Runway-Version": "2024-11-06"
}


# ========== 提示词库（根据你的漫剧） ==========
PROMPTS = {
    "陆离_卧室": {
        "prompt": "A 21 year old Chinese man with black hair and glasses, wearing dark blue hoodie, waking up in his bedroom, morning sunlight through curtains, reaching for phone on nightstand, anime style, studio ghibli inspired, detailed, soft lighting, cinematic composition --ar 16:9",
        "description": "第 1 集 - 陆离卧室醒来"
    },
    
    "陆离_公交": {
        "prompt": "A young Chinese man sitting alone in empty bus at night, dark street outside, bus driver in front mirror, suspense atmosphere, anime style, cold color palette, dramatic lighting --ar 16:9",
        "description": "第 1 集 - 末班公交车"
    },
    
    "苏晓_登场": {
        "prompt": "A 20 year old Chinese girl with brown shoulder-length hair, orange sweater, white pants, big smile, standing in school campus, sunny day, anime style, makoto shinkai inspired, vibrant colors --ar 16:9",
        "description": "第 3 集 - 苏晓首次登场"
    },
    
    "小太阳_APP": {
        "prompt": "Pixel art style cute sun mascot, yellow circular body, pixel smiley face, radiating light rays, cheerful expression, game UI element, warm yellow glow, white background --ar 1:1",
        "description": "APP 界面 - 小太阳图标"
    },
    
    "恐怖_小区": {
        "prompt": "Old abandoned apartment building at night, dim yellow hallway lights flickering, broken tiles, eerie atmosphere, horror anime style, cold green and blue tones, shadows --ar 16:9",
        "description": "第 2 集 - 槐安小区"
    },
    
    "治愈_超度": {
        "prompt": "Ghost fading away into light particles, warm white glow, peaceful expression, soft focus, healing atmosphere, anime style, golden hour lighting, emotional --ar 16:9",
        "description": "通用 - 鬼魂超度场景"
    },
    
    "研究所_培养皿": {
        "prompt": "Underground laboratory with 107 glass培养皿 in circular arrangement, blue glowing liquid inside, sci-fi atmosphere, cold white lighting, mysterious, anime style, wide shot --ar 16:9",
        "description": "彩蛋 - 心灵研究所"
    },
    
    "游乐园_摩天轮": {
        "prompt": "Amusement park ferris wheel at night, rotating slowly, warm yellow lights, romantic atmosphere, anime style, makoto shinkai inspired, starry sky --ar 16:9",
        "description": "第 5/10 集 - 游乐园摩天轮"
    }
}


def create_task(prompt, duration=4, resolution="720p"):
    """
    创建视频生成任务
    
    Args:
        prompt: 提示词
        duration: 视频时长（秒），默认 4 秒
        resolution: 分辨率，可选 "720p" 或 "1080p"
    
    Returns:
        task_id: 任务 ID，用于查询状态
    """
    url = f"{BASE_URL}/image_generation"
    
    payload = {
        "promptImage": {
            "prompt": prompt,
            "model": "gen2",
            "resolution": resolution,
            "duration": duration
        }
    }
    
    print(f"📤 提交任务...")
    print(f"   提示词：{prompt[:80]}...")
    print(f"   时长：{duration}秒")
    print(f"   分辨率：{resolution}")
    
    response = requests.post(url, headers=HEADERS, json=payload)
    
    if response.status_code == 201:
        data = response.json()
        task_id = data.get("id")
        print(f"✅ 任务提交成功！Task ID: {task_id}")
        return task_id
    else:
        print(f"❌ 提交失败：{response.status_code}")
        print(f"   错误信息：{response.text}")
        return None


def get_task_status(task_id):
    """
    查询任务状态
    
    Args:
        task_id: 任务 ID
    
    Returns:
        status: 任务状态 (QUEUED, RUNNING, COMPLETED, FAILED)
        video_url: 视频 URL（如果完成）
    """
    url = f"{BASE_URL}/tasks/{task_id}"
    
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code == 200:
        data = response.json()
        status = data.get("status")
        
        if status == "SUCCEEDED":
            video_url = data.get("output", [])
            video_url = video_url[0] if video_url else None
            return status, video_url
        elif status == "FAILED":
            error = data.get("error", "未知错误")
            return status, error
        else:
            return status, None
    else:
        print(f"❌ 查询失败：{response.status_code}")
        return "ERROR", None


def wait_for_completion(task_id, interval=10, timeout=300):
    """
    等待任务完成
    
    Args:
        task_id: 任务 ID
        interval: 查询间隔（秒）
        timeout: 超时时间（秒）
    
    Returns:
        video_url: 视频 URL，如果成功
    """
    print(f"⏳ 等待生成完成...")
    
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        status, result = get_task_status(task_id)
        
        if status == "SUCCEEDED":
            print(f"✅ 生成完成！")
            return result
        elif status == "FAILED":
            print(f"❌ 生成失败：{result}")
            return None
        elif status in ["QUEUED", "RUNNING", "PENDING"]:
            print(f"   当前状态：{status}... 等待 {interval}秒")
            time.sleep(interval)
        else:
            print(f"   未知状态：{status}")
            time.sleep(interval)
    
    print(f"⏱️ 超时（{timeout}秒）")
    return None


def download_video(video_url, save_path):
    """
    下载视频到本地
    
    Args:
        video_url: 视频 URL
        save_path: 保存路径
    """
    print(f"📥 下载视频到：{save_path}")
    
    response = requests.get(video_url, stream=True)
    
    with open(save_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    
    print(f"✅ 下载完成！")


def test_generation(prompt_key="陆离_卧室"):
    """
    测试视频生成
    
    Args:
        prompt_key: 提示词库中的键名
    """
    if prompt_key not in PROMPTS:
        print(f"❌ 未找到提示词：{prompt_key}")
        print(f"可用选项：{list(PROMPTS.keys())}")
        return
    
    prompt_info = PROMPTS[prompt_key]
    prompt = prompt_info["prompt"]
    description = prompt_info["description"]
    
    print(f"\n{'='*60}")
    print(f"🎬 开始生成测试视频")
    print(f"   场景：{description}")
    print(f"{'='*60}\n")
    
    # 创建任务
    task_id = create_task(prompt, duration=4, resolution="720p")
    
    if not task_id:
        return
    
    # 等待完成
    video_url = wait_for_completion(task_id, interval=10, timeout=600)
    
    if video_url:
        print(f"\n🎉 视频 URL: {video_url}")
        
        # 下载视频
        save_path = f"output_{prompt_key}.mp4"
        download_video(video_url, save_path)
        
        # 保存信息
        info = {
            "task_id": task_id,
            "prompt": prompt,
            "description": description,
            "video_url": video_url,
            "save_path": save_path
        }
        
        with open(f"{save_path}.json", 'w', encoding='utf-8') as f:
            json.dump(info, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ 全部完成！")
        print(f"   视频：{save_path}")
        print(f"   信息：{save_path}.json")
    else:
        print(f"\n❌ 生成失败")


def list_prompts():
    """列出所有可用提示词"""
    print("\n可用提示词列表：\n")
    
    for key, info in PROMPTS.items():
        print(f"  {key}")
        print(f"    描述：{info['description']}")
        print(f"    提示词：{info['prompt'][:60]}...")
        print()


# ========== 主程序 ==========
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "list":
            # 列出所有提示词
            list_prompts()
        
        elif command == "test":
            # 测试生成（默认第一个）
            prompt_key = sys.argv[2] if len(sys.argv) > 2 else "陆离_卧室"
            test_generation(prompt_key)
        
        else:
            # 直接使用自定义提示词
            custom_prompt = " ".join(sys.argv[1:])
            print(f"使用自定义提示词：{custom_prompt}")
            
            task_id = create_task(custom_prompt)
            if task_id:
                video_url = wait_for_completion(task_id)
                if video_url:
                    print(f"视频 URL: {video_url}")
    else:
        # 默认测试第一个场景
        print("用法:")
        print("  python runway_test.py list          # 列出所有提示词")
        print("  python runway_test.py test [场景名]  # 测试生成")
        print("  python runway_test.py 自定义提示词   # 自定义提示词")
        print()
        print("示例:")
        print("  python runway_test.py test 陆离_卧室")
        print("  python runway_test.py test 苏晓_登场")
        print()
        print("开始默认测试...")
        test_generation("陆离_卧室")
