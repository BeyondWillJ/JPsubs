import pykakasi
import re

def is_kanji(c):
    """判断字符是否为汉字"""
    return '\u4e00' <= c <= '\u9fff'

def convert_kanji_to_kunyomi(sentences):
    """
    将日文句子列表中的汉字转换为训读，假名保持为空
    
    参数:
        sentences: 日文句子列表
        
    返回:
        转换后的列表，与输入长度相同，汉字被替换为训读，假名位置为空字符串
    """
    # 初始化pykakasi转换器，设置为汉字转平假名(训读优先)
    kakasi = pykakasi.kakasi()
    kakasi.setMode("J", "H")  # J(汉字) to H(平假名)
    conv = kakasi.getConverter()
    
    result = []
    
    for sentence in sentences:
        converted = []
        for char in sentence:
            if is_kanji(char):
                # 对汉字进行转换，获取训读
                reading = conv.do(char)
                converted.append(reading)
            else:
                # 非汉字(假名、符号等)添加空字符串
                converted.append('')
        
        result.append(converted)
    
    return result

# 示例用法
if __name__ == "__main__":
    # 测试用的日文句子列表
    test_sentences = [
        "私は山に行きます",
        "朝食はパンと卵です",
        "水を飲みました"
    ]
    
    # 转换处理
    converted_results = convert_kanji_to_kunyomi(test_sentences)
    
    # 输出结果
    for i, (original, converted) in enumerate(zip(test_sentences, converted_results)):
        print(f"原句 {i+1}: {original}")
        print(f"转换后: {converted}")
        print("-" * 50)
    