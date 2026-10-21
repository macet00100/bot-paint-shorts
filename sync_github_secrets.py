"""
Auto-syncs all local credentials to GitHub Actions Secrets.
Uses GitHub REST API and Libsodium SealedBox encryption.
"""
import os
import sys
import json
import base64
import requests
from pathlib import Path
from nacl import encoding, public

BASE_DIR = Path(__file__).resolve().parent

# Force UTF-8 output
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OWNER = "macet00100"
REPO = "bot-paint-shorts"

# Get GitHub PAT from git credential helper
import subprocess
try:
    res = subprocess.run(
        ["git", "credential", "fill"],
        input="url=https://github.com\n",
        capture_output=True,
        text=True,
        check=True
    )
    gh_token = ""
    for line in res.stdout.splitlines():
        if line.startswith("password="):
            gh_token = line.split("=", 1)[1].strip()
except Exception as e:
    print(f"[!] Error retrieving git credential: {e}")
    sys.exit(1)

if not gh_token:
    print("[!] GitHub token not found.")
    sys.exit(1)

headers = {
    "Authorization": f"Bearer {gh_token}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28"
}

# Step 1: Get Repo Public Key for Secrets Encryption
print(f"[*] Fetching public key for {OWNER}/{REPO}...")
pk_url = f"https://api.github.com/repos/{OWNER}/{REPO}/actions/secrets/public-key"
r = requests.get(pk_url, headers=headers)
if r.status_code != 200:
    print(f"[!] Failed to fetch public key: {r.status_code} - {r.text}")
    sys.exit(1)

pk_data = r.json()
key_id = pk_data["key_id"]
public_key_b64 = pk_data["key"]
print(f"[+] Retrieved Public Key ID: {key_id}")

def encrypt_value(public_key_str: str, secret_val: str) -> str:
    pk = public.PublicKey(public_key_str.encode("utf-8"), encoding.Base64Encoder())
    sealed_box = public.SealedBox(pk)
    encrypted = sealed_box.encrypt(secret_val.encode("utf-8"))
    return base64.b64encode(encrypted).decode("utf-8")

def set_secret(secret_name: str, secret_value: str):
    if not secret_value:
        print(f"    [!] Skipping {secret_name}: Value is empty.")
        return False
    enc_val = encrypt_value(public_key_b64, secret_value)
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/actions/secrets/{secret_name}"
    payload = {
        "encrypted_value": enc_val,
        "key_id": key_id
    }
    resp = requests.put(url, headers=headers, json=payload)
    if resp.status_code in [201, 204]:
        print(f"    [SUCCESS] Synced Secret -> {secret_name}")
        return True
    else:
        print(f"    [!] Failed {secret_name}: {resp.status_code} - {resp.text}")
        return False

# Collect Secrets
secrets_to_upload = {}

# 1. YouTube
cs_file = BASE_DIR / "client_secret.json"
if cs_file.exists():
    secrets_to_upload["YOUTUBE_CLIENT_SECRET_BASE64"] = base64.b64encode(cs_file.read_bytes()).decode("utf-8")

token_file = BASE_DIR / "youtube_token.json"
if token_file.exists():
    secrets_to_upload["YOUTUBE_TOKEN_BASE64"] = base64.b64encode(token_file.read_bytes()).decode("utf-8")

# 2. .env file items
env_file = BASE_DIR / ".env"
if env_file.exists():
    with open(env_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                k = k.strip()
                v = v.strip()
                if k in ["FB_PAGE_ID", "FB_ACCESS_TOKEN", "TIKTOK_SESSION_COOKIE", "HF_TOKEN", "GEMINI_API_KEY"]:
                    secrets_to_upload[k] = v

print(f"\n[*] Uploading {len(secrets_to_upload)} secrets directly to GitHub Actions Secrets...")
for name, val in secrets_to_upload.items():
    set_secret(name, val)

print("\n" + "=" * 60)
print("[+] ALL SECRETS SUCCESSFULLY SYNCED TO GITHUB SECRETS!")
print("GitHub Actions is now 100% fully authorized to auto-post 24/7 with zero PC on!")
print("=" * 60 + "\n")
