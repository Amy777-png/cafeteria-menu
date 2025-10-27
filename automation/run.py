import os, re, io, json, datetime, time
def build_db(blocks: dict) -> dict:
today = datetime.datetime.now(tz=KST)
mon = monday_of_target_week(today)
db = {}
for i, w in enumerate(['월','화','수','목','금']):
if w in blocks:
d = mon + datetime.timedelta(days=i)
key = d.strftime('%Y-%m-%d')
db[key] = {
'items': blocks[w],
'meta': {
'source': 'ocr',
'updated': datetime.datetime.now(tz=KST).isoformat()
}
}
return db




def load_current_gist_json() -> dict:
r = requests.get(GISTS_API, headers=HEADERS, timeout=20)
r.raise_for_status()
data = r.json()
files = data.get('files', {})
if 'cafeteria.json' in files and files['cafeteria.json'].get('content'):
try:
return json.loads(files['cafeteria.json']['content'])
except Exception:
return {}
return {}




def merge_db(new: dict, old: dict) -> dict:
# 새로 인식된 날짜만 덮어쓰기 (기존 주차 데이터는 유지)
out = dict(old)
out.update(new)
return out




def update_gist(final_db: dict):
payload = {
'files': {
'cafeteria.json': {
'content': json.dumps(final_db, ensure_ascii=False, indent=2)
}
}
}
r = requests.patch(GISTS_API, headers=HEADERS, data=json.dumps(payload))
if r.status_code >= 300:
raise SystemExit(f"[ERROR] Gist 업데이트 실패: {r.status_code} {r.text}")
log("Gist 업데이트 완료")




def main():
img_bytes = fetch_image_bytes()
text = ocr_kor(img_bytes)
blocks = parse_week(text)
if not blocks:
raise SystemExit("[ERROR] OCR 텍스트에서 월~금 블록을 찾지 못했습니다.")


new_db = build_db(blocks)
old_db = load_current_gist_json()
final_db = merge_db(new_db, old_db)
update_gist(final_db)


if __name__ == '__main__':
main()
