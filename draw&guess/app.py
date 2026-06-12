"""
你画我猜 — 局域网抽词小程序
基于 Flask 的轻量级 Web 服务，手机扫码/访问即可使用。

启动方式：
    python app.py
启动后访问终端打印的地址（如 http://192.168.x.x:5000）。
"""

import csv
import random
import socket
from pathlib import Path

from flask import Flask, jsonify, render_template

# ---------------------------------------------------------------------------
# 配置
# ---------------------------------------------------------------------------
# 优先读取根目录的主词库文件，回退到 draw&guess/ 下的副本
_csv_root = Path(__file__).parent.parent / "你画我猜词库.csv"
_csv_local = Path(__file__).parent / "你画我猜词库.csv"
CSV_FILE = _csv_root if _csv_root.exists() else _csv_local
DRAW_COUNT = 3          # 每次抽取的词数
HOST = "0.0.0.0"        # 绑定所有网卡，允许局域网访问
PORT = 5000

# ---------------------------------------------------------------------------
# Flask 应用初始化
# ---------------------------------------------------------------------------
app = Flask(__name__)


# ---------------------------------------------------------------------------
# 核心：动态读取 CSV 词库（支持热更新，无需重启服务）
# ---------------------------------------------------------------------------
def load_words() -> list[dict]:
    """从 CSV 文件中读取全部词条，每次调用都重新读取以实现热更新。

    文件格式容忍：CSV 由 Excel 生成，列名和数据可能带有多余空格，
    本函数会自动去除所有字段的首尾空白。
    """
    words = []
    with open(CSV_FILE, "r", encoding="utf-8-sig") as f:
        raw_reader = csv.reader(f)

        # 第一行是标题，strip 掉前后空格（Excel 会在宽列中填充空格）
        raw_headers = next(raw_reader, None)
        if raw_headers is None:
            return words
        headers = [h.strip() for h in raw_headers]

        # 用清理后的标题构造 DictReader，后续数据行也自动 strip
        for raw_row in raw_reader:
            row = [v.strip() for v in raw_row]
            # 补齐缺失的列（有些行末尾为空）
            while len(row) < len(headers):
                row.append("")
            record = dict(zip(headers, row))

            word = record.get("词", "")
            hint = record.get("解释（若有）", "") or record.get("解释", "")
            if word:
                words.append({"word": word, "hint": hint})
    return words


def draw_words(count: int = DRAW_COUNT) -> list[dict]:
    """从词库中随机抽取 `count` 个不重复的词语。"""
    words = load_words()
    if not words:
        return []
    return random.sample(words, min(count, len(words)))


# ---------------------------------------------------------------------------
# API 路由
# ---------------------------------------------------------------------------
@app.route("/api/draw")
def api_draw():
    """抽取 3 个随机词语，返回 JSON。"""
    try:
        result = draw_words()
        return jsonify({"success": True, "words": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/word-count")
def api_word_count():
    """返回当前词库总数（调试/状态展示用）。"""
    words = load_words()
    return jsonify({"success": True, "count": len(words)})


# ---------------------------------------------------------------------------
# 前端页面
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html")


# ---------------------------------------------------------------------------
# 启动
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # 打印本机局域网 IP，方便手机访问
    lan_ip = "127.0.0.1"
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        lan_ip = s.getsockname()[0]
        s.close()
    except Exception:
        pass

    words = load_words()
    print(f"\n{'='*50}")
    print(f"  你画我猜抽词小程序 已启动")
    print(f"  词库数量: {len(words)} 条")
    print(f"  本机访问: http://127.0.0.1:{PORT}")
    print(f"  手机访问: http://{lan_ip}:{PORT}")
    print(f"{'='*50}\n")

    app.run(host=HOST, port=PORT, debug=False)
