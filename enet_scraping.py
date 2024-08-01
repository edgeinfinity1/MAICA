import re
import traceback
from loadenv import load_env
from search_engines import Google, Bing
from openai import OpenAI # type: ignore


def internet_search_limb(query, esc_aggressive=True):
    success = True
    exception = None
    engine = Bing(load_env('PROXY_ADDR'))
    engine.set_headers({'User-Agent':f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 OPR/109.0.0.0"})
    results = engine.search(query, pages=1)
    slt_full = []
    slt_default = []
    slt_humane = ''
    rank = 0
    for item in results:
        rank += 1
        title = item['title']
        text = re.sub(r'.*?(?=[\u4e00-\u9fa5])', '', item['text'], 1, re.I)
        slt_full.append({'rank': rank, 'title': title, 'text': text})
        if rank <= 5:
            slt_default.append({'rank': rank, 'title': title, 'text': text})
        if rank <= 3:
            slt_humane += f'信息{rank} 标题:{title} 内容:{text}'
    slt_full = str(slt_full)
    slt_default = str(slt_default).strip('[').strip(']')
    if not esc_aggressive:
        return True, None, slt_default, slt_humane
    try:
        client = OpenAI(
            api_key='EMPTY',
            base_url=load_env('MFOCUS_ADDR'),
        )
        model_type = client.models.list().data[0].id
        print(f'MFocus enet addressing model, response is:\n{model_type}\nEnd of MFocus enet addressing model')
        system_init = """你是一个人工智能助手, 你的任务是整理信息. 你接下来会收到一些来自搜索引擎的信息.
请你将这些信息整理为一条简洁的总结, 不要编造信息, 并以单行自然语言的形式, 使用信息中的语言返回.
如果你最终没有找到有意义的信息, 请返回none.
使用以下格式回答:
Thought: 简要地思考以上信息关于何种内容, 以及应当如何整理.
Try: 尝试将你的总结以单行自然语言的形式返回.
Thought Again: 再次思考上面输出的信息. 如果其中存在无意义, 无知识性, 无时效性的内容或广告, 则将其去除.
Answer: 最终将有用的信息以单行自然语言的形式返回.
Begin!
"""
        messages = [{'role': 'system', 'content': system_init}]
        messages.append({'role': 'user', 'content': f'information: {slt_full}'})
        resp = client.chat.completions.create(
            model=model_type,
            messages=messages,
            temperature=0.1,
            top_p = 0.6,
            presence_penalty = 0.0,
            frequency_penalty = 0.0,
            #stop=['<|endoftext|>'],
            seed=42)
        response = resp.choices[0].message.content
        print(f"MFocus enet searching persistent, response is:\n{response}\nEnd of MFocus enet searching persistent")
        answer_re = re.search(r'Answer\s*:\s*(.*)', response, re.I)
        if answer_re:
            if not re.match('none', answer_re[1], re.I):
                slt_humane = answer_re[1]
        # If corrupted we proceed anyway
    except Exception as excepted:
        traceback.print_exc()
        success = False
        exception = excepted
        return success, exception, '', ''
    return True, None, slt_humane, slt_humane

if __name__ == '__main__':
    searched = internet_search_limb('鄂州附近有什么好吃的')
    print(searched[3])