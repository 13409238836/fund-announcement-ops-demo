from http.server import BaseHTTPRequestHandler
from io import BytesIO
import base64
import hmac
import json
import os

MAX_BODY_BYTES = 4_400_000


class handler(BaseHTTPRequestHandler):
    def _json(self, status, payload):
        body = json.dumps(payload, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        expected = os.environ.get('DEMO_ACCESS_PASSWORD', '')
        supplied = self.headers.get('Authorization', '')
        if not expected and (os.environ.get('VERCEL') == '1' or os.environ.get('NODE_ENV') == 'production'):
            return self._json(503, {'error': '公网环境缺少演示访问口令配置。'})
        if expected and not hmac.compare_digest(supplied, 'Bearer ' + expected):
            return self._json(401, {'error': '演示访问口令错误，请重新输入。'})

        try:
            size = int(self.headers.get('Content-Length', '0'))
            if size <= 0 or size > MAX_BODY_BYTES:
                return self._json(413, {'error': 'PDF 请求过大，请上传 3 MB 以内的文件。'})
            body = json.loads(self.rfile.read(size))
            encoded = body.get('base64', '')
            raw = base64.b64decode(encoded, validate=True)
            if len(raw) > 3_000_000:
                return self._json(413, {'error': 'PDF 文件不能超过 3 MB。'})
            import pdfplumber
            with pdfplumber.open(BytesIO(raw)) as pdf:
                text = '\n\n'.join(page.extract_text(layout=False) or '' for page in pdf.pages)
            if not text.strip():
                return self._json(422, {'error': 'PDF 中没有提取到文本，可能是扫描图片版。请粘贴公告正文后重试。'})
            return self._json(200, {'name': str(body.get('name', '公告.pdf'))[:200], 'text': text[:120000]})
        except ImportError:
            return self._json(500, {'error': 'PDF 提取依赖尚未安装，请检查 Vercel Python Function 构建日志。'})
        except Exception:
            return self._json(422, {'error': 'PDF 解析失败，请检查文件是否为可搜索文本的 PDF，或粘贴公告正文。'})
