"""Tạo giọng đọc (giọng Google) cho app Hệ Mặt Trời.

Dùng:  python -I he-mat-troi/tools/make_audio.py        (tạo file còn thiếu)
       python -I he-mat-troi/tools/make_audio.py --all  (tạo lại hết, khi đã sửa câu trong data.json)

Đọc data.json: mỗi thiên thể có mảng "doc" (các câu đọc) -> audio/<id>.mp3 (ghép các câu lại).
Mục "_cau" là các câu lẻ -> audio/<khoá>.mp3.
"""
import json, os, re, sys, time, urllib.parse, urllib.request
sys.stdout.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUD = os.path.join(ROOT, 'audio')
os.makedirs(AUD, exist_ok=True)


def tts(text):
    q = urllib.parse.quote(text)
    url = f'https://translate.google.com/translate_tts?ie=UTF-8&tl=vi&client=tw-ob&q={q}'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    for i in range(3):
        try:
            data = urllib.request.urlopen(req, timeout=20).read()
            if len(data) > 500:
                return data
        except Exception as e:
            print('  lỗi', e)
        time.sleep(2 + i * 3)
    raise SystemExit('KHÔNG TẠO ĐƯỢC: ' + text)


SAY_FIX = {'Haha': 'Ha Ha', 'Hihi': 'Hi Hi'}   # viết tách cho giọng đọc tự nhiên


def main():
    redo = '--all' in sys.argv
    data = json.load(open(os.path.join(ROOT, 'data.json'), encoding='utf-8'))
    jobs = {k: v['doc'] for k, v in data.items() if not k.startswith('_')}
    jobs.update({k: [v] for k, v in data.get('_cau', {}).items()})
    for name, sentences in jobs.items():
        path = os.path.join(AUD, name + '.mp3')
        if os.path.exists(path) and not redo:
            continue
        print('tạo', name)
        out = b''
        for s in sentences:
            for a, b in SAY_FIX.items(): s = s.replace(a, b)
            for part in re.split(r'(?<=[.!?])\s+', s):   # Google chỉ đọc tối đa ~200 ký tự mỗi lần
                out += tts(part)
            time.sleep(0.4)
        open(path, 'wb').write(out)
    print('xong')


main()
