import os

# ssl cert的主配置文件

ACME_DIR = os.environ.get("ACME_DIR", "/Users/zzf/.acme.sh")
CERT_DIR = os.path.join(ACME_DIR, "mycerts")

dns_api_mode = {
    "dnspod": ["id", "token"],
    "cloudflare": ["key", "email"],
    "aliyun": ["key", "secret"],
}

acme_alias_mode = {
    "dnspod": [
        "dns_dp",
        "DP_Id",
        "DP_Key"
    ],
    "cloudflare": [
        "dns_cf",
        "CF_Key",
        "CF_Email",
    ],
    "aliyun": [
        "dns_ali",
        "Ali_Key",
        "Ali_Secret"
    ]
}

# 是否开启acme测试模式, False不开启， True开启
ACME_STAGING = False if os.environ.get("STAGING") == "False" else True
