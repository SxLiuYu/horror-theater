#!/usr/bin/env python3
"""
Replicate API 文生视频测试脚本
使用 Zeroscope 或 Stable Video Diffusion 模型

使用前：
1. 注册 Replicate: https://replicate.com
2. 获取 API Token: Settings → API Tokens
3. 设置环境变量：export REPLICATE_API_TOKEN="你的 token"

文档：https://replicate.com/docs
"""

import os
import time
import requests
import base64

# ========== 配置 ==========
API_TOKEN = os.getenv("REPLICATE_API_TOKEN", "")

if not API_TOKEN:
    print("❌ 错误：未设置 REPLICATE_API_TOKEN 环境变量")
    print("请运行：export REPLICATE_API_TOKEN=\"你的 token\"")
    exit(1)

# Replicate API
BASE_URL = "https://api.replicate.com/v1"
HEADERS = {
    "Authorization": f"Token {API_TOKEN}",
    "Content-Type": "application/json"
}

# 推荐模型
MODELS = {
    "zeroscope": "cerspense/zeroscope_v2xl:9f747673945c62801b13b84701c783929c0ee784e4748ec062204894dda1a351",
    "svd": "stability-ai/stable-video-diffusion:3f0457e4619daac512030b12921598c50fa128a330020611e92e2be3fe548f51",
    "animate": "lucataco/animate-diff:28c08e9115448766f0c0aa6e9991813e10f403784004b6b46f54e36d4f80a0c7"
}


def create_prediction(model_version, prompt, duration=4):
    """
    创建视频生成任务
    
    Args:
        model_version: 模型版本 ID
        prompt: 提示词
        duration: 视频时长（秒）
    
    Returns:
        prediction_id: 任务 ID
    """
    url = f"{BASE_URL}/predictions"
    
    # Zeroscope 模型参数
    payload = {
        "version": model_version,
        "input": {
            "prompt": prompt,
            "num_frames": 24,  # 4 秒 @ 6fps
            "fps": 6,
            "width": 576,
            "height": 320,
            "guidance_scale": 17.5,
            "num_inference_steps": 50
        }
    }
    
    print(f"📤 提交任务...")
    print(f"   模型：zeroscope_v2xl")
    print(f"   提示词：{prompt[:80]}...")
    
    response = requests.post(url, headers=HEADERS, json=payload)
    
    if response.status_code == 201:
        data = response.json()
        prediction_id = data.get("id")
        print(f"✅ 任务提交成功！ID: {prediction_id}")
        return prediction_id
    else:
        print(f"❌ 提交失败：{response.status_code}")
        print(f"   错误：{response.text}")
        return None


def get_prediction_status(prediction_id):
    """
    查询任务状态
    
    Returns:
        status: SUCCEEDED, PROCESSING, FAILED
        output: 视频 URL（如果完成）
    """
    url = f"{BASE_URL}/predictions/{prediction_id}"
    
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code == 200:
        data = response.json()
        status = data.get("status")
        
        if status == "succeeded":
            output = data.get("output")
            return status, output
        elif status == "failed":
            error = data.get("error", "未知错误")
            return status, error
        else:
            return status, None
    else:
        print(f"❌ 查询失败：{response.status_code}")
        return "ERROR", None


def wait_for_completion(prediction_id, interval=5, timeout=300):
    """
    等待任务完成
    
    Args:
        prediction_id: 任务 ID
        interval: 查询间隔（秒）
        timeout: 超时时间（秒）
    """
    print(f"⏳ 等待生成完成...")
    
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        status, output = get_prediction_status(prediction_id)
        
        if status == "succeeded":
            print(f"✅ 生成完成！")
            return output
        elif status == "failed":
            print(f"❌ 生成失败：{output}")
            return None
        elif status in ["starting", "processing"]:
            print(f"   当前状态：{status}... 等待 {interval}秒")
            time.sleep(interval)
        else:
            print(f"   未知状态：{status}")
            time.sleep(interval)
    
    print(f"⏱️ 超时（{timeout}秒）")
    return None


def download_video(video_url, save_path):
    """下载视频到本地"""
    print(f"📥 下载视频到：{save_path}")
    
    response = requests.get(video_url, stream=True)
    
    with open(save_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    
    print(f"✅ 下载完成！")


# ========== 提示词库 ==========
PROMPTS = {
    "陆离_卧室": "A 21 year old Chinese man with black hair and glasses, wearing dark blue hoodie, waking up in his bedroom, morning sunlight through curtains, anime style, studio ghibli inspired, detailed, soft lighting",
    
    "陆离_公交": "A young Chinese man sitting alone in empty bus at night, dark street outside, bus driver in front mirror, suspense atmosphere, anime style, cold color palette",
    
    "苏晓_登场": "A 20 year old Chinese girl with brown shoulder-length hair, orange sweater, white pants, big smile, standing in school campus, sunny day, anime style, vibrant colors",
    
    "恐怖_小区": "Old abandoned apartment building at night, dim yellow hallway lights flickering, broken tiles, eerie atmosphere, horror anime style, cold green and blue tones",
    
    "治愈_超度": "Ghost fading away into light particles, warm white glow, peaceful expression, soft focus, healing atmosphere, anime style, golden hour lighting",
    
    "游乐园_摩天轮": "Amusement park ferris wheel at night, rotating slowly, warm yellow lights, romantic atmosphere, anime style, starry sky"
}


def test_generation(prompt_key="陆离_卧室"):
    """测试视频生成"""
    
    if prompt_key not in PROMPTS:
        print(f"❌ 未找到提示词：{prompt_key}")
        print(f"可用选项：{list(PROMPTS.keys())}")
        return
    
    prompt = PROMPTS[prompt_key]
    
    print(f"\n{'='*60}")
    print(f"🎬 开始生成测试视频")
    print(f"   场景：{prompt_key}")
    print(f"{'='*60}\n")
    
    # 创建任务
    prediction_id = create_prediction(MODELS["zeroscope"], prompt)
    
    if not prediction_id:
        return
    
    # 等待完成
    video_url = wait_for_completion(prediction_id, interval=5, timeout=600)
    
    if video_url:
        print(f"\n🎉 视频 URL: {video_url}")
        
        # 下载视频
        save_path = f"output_{prompt_key}.mp4"
        download_video(video_url, save_path)
        
        print(f"\n✅ 全部完成！")
        print(f"   视频：{save_path}")
        print(f"   消耗：约 $0.05-0.10（根据时长）")
    else:
        print(f"\n❌ 生成失败")


def list_prompts():
    """列出所有可用提示词"""
    print("\n可用提示词列表：\n")
    for key in PROMPTS.keys():
        print(f"  - {key}")
    print()


# ========== 主程序 ==========
if __name__ == "__main__":
    import sys
    
    print("🎬 Replicate API 文生视频测试工具")
    print("="*60)
    print()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "list":
            list_prompts()
        
        elif command == "test":
            prompt_key = sys.argv[2] if len(sys.argv) > 2 else "陆离_卧室"
            test_generation(prompt_key)
        
        else:
            # 自定义提示词
            custom_prompt = " ".join(sys.argv[1:])
            print(f"使用自定义提示词：{custom_prompt}")
            test_generation(custom_prompt)
    
    else:
        print("用法:")
        print("  python replicate_test.py list          # 列出提示词")
        print("  python replicate_test.py test [场景名]  # 测试生成")
        print()
        print("示例:")
        print("  python replicate_test.py test 陆离_卧室")
        print("  python replicate_test.py test 恐怖_小区")
        print()
        print("开始默认测试...")
        print()
        test_generation("陆离_卧室")
