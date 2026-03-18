#!/bin/bash
# 批量上传文件到 GitHub

GITHUB_TOKEN="${GITHUB_TOKEN:-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}"
REPO="SxLiuYu/horror-theater"
BRANCH="main"
BASE_URL="https://api.github.com/repos/$REPO/contents"

echo "📤 批量上传文件到 GitHub..."
echo "   仓库：$REPO"
echo "   分支：$BRANCH"
echo ""

# 文件列表
FILES=(
    "season1/outline.md"
    "season1/episode01.md"
    "season1/episode02.md"
    "season1/episode03.md"
    "season1/episode04.md"
    "season1/episode05.md"
    "season1/episode06.md"
    "season1/episode07.md"
    "season1/episode08.md"
    "season1/episode09.md"
    "season1/episode10.md"
    "season1/episode11.md"
    "season1/episode12.md"
    "season1/production_progress.md"
    "setting.md"
    "README.md"
    "assets/characters/prompts.md"
    "production/art/README.md"
    "production/bgm/README.md"
    "production/storyboard/README.md"
    "production/storyboard/episodes_03-05.md"
    "production/storyboard/episodes_06-8.md"
    "production/storyboard/episodes_09-12.md"
    "tools/runway_api_test.py"
    "tools/replicate_api_test.py"
    "tools/generate_video.py"
    "tools/batch_generate.py"
    "tools/retry_failed.py"
    "tools/RUNWAY_API_GUIDE.md"
    ".gitignore"
)

cd /home/admin/.openclaw/workspace/horror-theater

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "📄 $file..."
        
        # 读取文件内容并 base64 编码
        content=$(base64 -w 0 "$file")
        
        # 获取文件名和路径
        filename=$(basename "$file")
        filepath=$(dirname "$file")
        
        # 创建/更新文件
        message="Update $file"
        
        if [ "$filepath" = "." ]; then
            path="$filename"
        else
            path="$file"
        fi
        
        # API 请求
        response=$(curl -s -X PUT \
            -H "Authorization: token $GITHUB_TOKEN" \
            -H "Accept: application/vnd.github.v3+json" \
            "$BASE_URL/$path" \
            -d "{
                \"message\": \"$message\",
                \"content\": \"$content\",
                \"branch\": \"$BRANCH\"
            }")
        
        # 检查结果
        if echo "$response" | grep -q '"commit"'; then
            echo "   ✅ 成功"
        else
            echo "   ⚠️ $response" | head -c 200
        fi
    else
        echo "⚠️ $file (不存在)"
    fi
done

echo ""
echo "✅ 批量上传完成！"
echo "📥 查看：https://github.com/$REPO"
