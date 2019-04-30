import os

ACME_DIR = os.environ.get("ACME_DIR", "/Users/zzf/.acme.sh")
CERT_DIR = os.path.join(ACME_DIR, "mycerts")

# dns_company = ("dnspod", "cloudflare", "aliyun")


dns_api_mode = {
    "dnspod": ["id", "key"],
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

# acme_alias_mode = {
#     "dnspod": {
#         "dns_alias": "dns_dp",
#         "env_key": "DP_Id",
#         "env_token": "DP_Key",
#     },
#     "cloudflare": {
#         "dns_alias": "dns_cf",
#         "env_key": "CF_Key",
#         "env_token": "CF_Email",
#     },
#     "aliyun": {
#         "dns_alias": "dns_ali",
#         "env_key": "Ali_Key",
#         "env_token": "Ali_Secret",
#     }
# }
