"""Tạo file giọng đọc tiếng Việt cho game (giọng Google, đọc chuẩn hơn giọng có sẵn của máy).

Dùng:
  python tools/make_audio.py                 -> tạo cho mọi câu trong tools/phrases.json
  python tools/make_audio.py bà bé thuyền    -> thêm giọng cho các từ mới (tự tách: bờ, a, ba, huyền, bà...)

Kết quả: audio/<mã>.mp3 + audio/index.json (khoá = câu đã chuẩn hoá, giống hàm nk() trong index.html).
"""
import hashlib, json, os, re, sys, time, unicodedata, urllib.parse, urllib.request, subprocess
sys.stdout.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUD = os.path.join(ROOT, 'audio')
PHR = os.path.join(ROOT, 'tools', 'phrases.json')
os.makedirs(AUD, exist_ok=True)

def nk(t):
    t = unicodedata.normalize('NFC', str(t).lower())
    t = re.sub(r'[.,!?…“”"\':;()]', ' ', t)
    return re.sub(r'\s+', ' ', t).strip()

# ---- tách tiếng giống parseSyl / expectedParts trong index.html ----
TONE_MARKS = {'́': 'sắc', '̀': 'huyền', '̉': 'hỏi', '̃': 'ngã', '̣': 'nặng'}
ONSETS = ['ngh','ng','nh','ch','gh','gi','kh','ph','th','tr','qu','b','c','d','đ','g','h','k','l','m','n','p','r','s','t','v','x']
ONSET_SAY = {'b':'bờ','c':'cờ','d':'dờ','đ':'đờ','g':'gờ','gh':'gờ','h':'hờ','k':'ca','l':'lờ','m':'mờ','n':'nờ','p':'pờ','r':'rờ','s':'sờ','t':'tờ','v':'vờ','x':'xờ','ch':'chờ','nh':'nhờ','ng':'ngờ','ngh':'ngờ','gi':'di','kh':'khờ','ph':'phờ','th':'thờ','tr':'trờ','qu':'quờ'}
FINAL_SAY = {'c':'cờ','ch':'chờ','m':'mờ','n':'nờ','ng':'ngờ','nh':'nhờ','p':'pờ','t':'tờ'}

def parts(word):
    w = unicodedata.normalize('NFC', word.strip().lower())
    tone, base = None, ''
    for ch in unicodedata.normalize('NFD', w):
        if ch in TONE_MARKS: tone = TONE_MARKS[ch]
        else: base += ch
    base = unicodedata.normalize('NFC', base)
    if not re.fullmatch(r'[a-zđăâêôơư]+', base): return []
    onset = next((o for o in ONSETS if base.startswith(o)), '')
    rime = base[len(onset):]
    if onset == 'gi' and not re.search('[aăâeêoôơuưy]', rime): onset, rime = 'g', 'i' + rime
    if not rime: return []
    p = []
    if onset: p += [ONSET_SAY[onset], rime, base]
    else:
        m = re.fullmatch(r'(.+?)(ch|nh|ng|c|m|n|p|t)', rime)
        p += [m.group(1), FINAL_SAY[m.group(2)], base] if m else [base]
    if tone: p += [tone, w]
    return p

def tts(text, path):
    q = urllib.parse.quote(text)
    url = f'https://translate.google.com/translate_tts?ie=UTF-8&tl=vi&client=tw-ob&q={q}'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    for i in range(3):
        try:
            data = urllib.request.urlopen(req, timeout=20).read()
            if len(data) > 500:
                open(path, 'wb').write(data); return True
        except Exception as e:
            print('  lỗi', e)
        time.sleep(2 + i * 3)
    return False

SAY_FIX = {'Haha': 'Ha Ha', 'Hihi': 'Hi Hi'}   # cách viết cho giọng đọc tự nhiên hơn

def main():
    phrases = json.load(open(PHR, encoding='utf-8')) if os.path.exists(PHR) else {}
    for word in sys.argv[1:]:
        for t in parts(word):
            phrases.setdefault(nk(t), t)
    json.dump(phrases, open(PHR, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    idx_path = os.path.join(AUD, 'index.json')
    idx = json.load(open(idx_path, encoding='utf-8')) if os.path.exists(idx_path) else {}
    made = 0
    for key, text in phrases.items():
        fn = hashlib.md5(key.encode('utf-8')).hexdigest()[:12] + '.mp3'
        path = os.path.join(AUD, fn)
        if not os.path.exists(path):
            say = text
            for a, b in SAY_FIX.items(): say = say.replace(a, b)
            if not tts(say, path):
                print('KHÔNG TẠO ĐƯỢC:', text); continue
            made += 1; time.sleep(0.25)
        idx[key] = fn
    json.dump(idx, open(idx_path, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    sil = os.path.join(AUD, 'silence.mp3')
    if not os.path.exists(sil):
        subprocess.run(['ffmpeg', '-v', 'quiet', '-f', 'lavfi', '-i', 'anullsrc=r=24000:cl=mono', '-t', '0.2', '-q:a', '9', sil])
    print(f'Xong: tạo mới {made}, tổng {len(idx)} câu')

if __name__ == '__main__':
    main()
