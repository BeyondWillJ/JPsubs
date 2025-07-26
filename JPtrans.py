import pykakasi

def is_kanji(c):
    """判断字符是否为汉字"""
    return '\u4e00' <= c <= '\u9fff'

# 自动检测中文字符并用pykakasi查找假名，否则留空
def convert_kanji_to_kunyomi(sentences):
    """
    将日文句子列表中的汉字转换为训读，假名保持为空
    
    参数:
        sentences: 日文句子列表
        
    返回:
        转换后的列表，与输入长度相同，汉字被替换为训读，假名位置为空字符串
    """
    kakasi = pykakasi.kakasi()
    result = []
    for sentence in sentences:
        converted = []
        for char in sentence:
            if is_kanji(char):
                conv = kakasi.convert(char)
                if conv:
                    converted.append(conv[0]['hira'])
                else:
                    converted.append('')
            else:
                converted.append('')
        result.append(converted)
    return result


jp = "な,ん,だ,~,も,う,朝,…,か,と,…"
jpstr = "ひとり…ごつ…"
# 转换成列表
# jp_list = jp.split(',')
jp_list = list(jpstr)

# 初始化pykakasi
kks = pykakasi.kakasi()

# 得到其罗马音
romaji_list = []
for char in jp_list:
    result = kks.convert(char)
    # 如果有转换结果，取第一个的'hepburn'字段，否则原样返回
    if result:
        romaji_list.append(result[0]['hepburn'])
    else:
        romaji_list.append(char)

print(jp_list)
print(','.join(jp_list))
print(romaji_list)
print(','.join(romaji_list))


kana_list = convert_kanji_to_kunyomi([jp_list])[0]

print(kana_list)
print(','.join(kana_list))
