import hmac
import hashlib
import base64
import time
import json
import requests
import urllib.parse
import config

def send_dingtalk_message(title, content):
    """
    发送钉钉webhook消息（支持加签）
    """
    if not config.DINGTALK_WEBHOOK:
        print("未配置钉钉webhook，跳过钉钉推送")
        return False

    webhook_url = config.DINGTALK_WEBHOOK
    secret = config.DINGTALK_SECRET

    # 如果有加签，需要添加签名
    if secret:
        timestamp = str(round(time.time() * 1000))
        secret_enc = secret.encode('utf-8')
        string_to_sign = f'{timestamp}\n{secret}'
        string_to_sign_enc = string_to_sign.encode('utf-8')
        hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
        sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
        webhook_url = f"{webhook_url}&timestamp={timestamp}&sign={sign}"

    # 构造消息内容
    data = {
        "msgtype": "markdown",
        "markdown": {
            "title": title,
            "text": f"### {title}\n\n{content}"
        }
    }

    headers = {
        'Content-Type': 'application/json'
    }

    try:
        response = requests.post(webhook_url, json=data, headers=headers, timeout=10)
        result = response.json()

        if result.get('errcode') == 0:
            print("钉钉消息推送成功")
            return True
        else:
            print(f"钉钉消息推送失败: {result.get('errmsg')}")
            return False
    except Exception as e:
        print(f"钉钉消息推送异常: {e}")
        return False
