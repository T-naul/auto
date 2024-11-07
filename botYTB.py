from g4f.client   import Client
from g4f.Provider import OpenaiChat

async def reply_cmt(cmt: str):
    client = Client(
        proxies = {
            'http': 'http://113.160.214.209:8080'
        },
        provider = OpenaiChat
    )

    messages = [
        {'role': 'user', 'content': f'Đây là 1 nội dung khán giả bình luận dưới video youtube của tôi. Bạn hãy viết giúp tôi một câu trả bằng tiếng Anh phù hợp và cảm ơn khán giả đã góp ý cho nội dung của video.Thêm biểu tượng cảm xúc vào câu trả lời. Chỉ cần đưa tôi câu trả lời. Nội dung bình luận của khán giả như sau: {cmt}'},
    ]

    response = client.chat.completions.create(model='auto',
                                        messages=messages, 
                                        stream=False)
    return response.choices[0].message.content 
# if __name__ == '__main__':
#     import asyncio
#     asyncio.run(reply_cmt("great video"))
