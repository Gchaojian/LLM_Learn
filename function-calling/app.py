import os
from dotenv import load_dotenv

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import json
from openai import OpenAI
 
# LLM_MODEL = "gpt-3.5-turbo"
LLM_MODEL = "medical_robot"
# LLM_MODEL = "yi-large"


#加载环境变量
load_dotenv()
# 获取环境变量
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
API_BASE = os.getenv("API_BASE")
AUTHORIZATION_CODE = os.getenv("AUTHORIZATION_CODE")

# client = OpenAI(api_key=OPENAI_API_KEY)
client = OpenAI(
    api_key=OPENAI_API_KEY,
    base_url=API_BASE
                )

tools = [
    {
        "type": "function",
        "function": {
            "name": "send_email",
            "description": "Send an email to the specified email with the subject and content",
            "parameters":{
                "type": "object",
                "properties": {
                    "FromEmail": {
                        "type": "string",
                        "description": "The email address, eg., rememeber0101@126.com",
                    },
                    "Subject": {
                        "type": "string",
                        "description": "Subject of the email",
                    },
                    "Body": {
                        "type": "string",
                        "description": "The content of the email",
                    },
                    "Recipients": {
                        "type": "string",
                        "description": "The recipients' email addresses",
                    }
                },
                "required": ["FromEmail", "Subject", "Body", "Recipients"],
            },
        }
    }
]

# tools = [
#     {
#         'name_for_human': '邮箱AI助手',
#         'name_for_model': 'send_email',
#         'description_for_model': '发送一封电子邮件到指定的邮箱，包含主题和内容。',
#         'parameters': [{
#             'schema': {
#                 "type": "object",
#                 "properties": {
#                     "FromEmail": {
#                         "type": "string",
#                         "description": "The email address, eg., rememeber0101@126.com",
#                     },
#                     "Subject": {
#                         "type": "string",
#                         "description": "Subject of the email",
#                     },
#                     "Body": {
#                         "type": "string",
#                         "description": "The content of the email",
#                     },
#                     "Recipients": {
#                         "type": "string",
#                         "description": "The recipients' email addresses",
#                     }
#                 },
#                 "required": ["FromEmail", "Subject", "Body", "Recipients"],
#             },
#         }],
#     },
#     # 其他工具的定义可以在这里继续添加
# ] 


def chat_completion_request(messages, tools=None, tool_choice=None, model=LLM_MODEL):
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
            tool_choice=tool_choice,
        )
        return response
    except Exception as e:
        print("Unable to generate ChatCompletion response")
        print(f"Exception: {e}")
        return e


def send_email(sender_email, sender_authorization_code, recipient_email, subject, body):
    # 创建 MIMEMultipart 对象
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = recipient_email
    message["Subject"] = subject
    # 添加邮件正文
    message.attach(MIMEText(body, "plain"))

    # 创建 SMTP_SSL 会话
    with smtplib.SMTP_SSL("smtp.163.com", 465) as server:
        # 登录到 SMTP 服务器
        server.login(sender_email, sender_authorization_code)
        # 将邮件对象转换为字符串
        text = message.as_string()
        # 发送邮件
        server.sendmail(sender_email, recipient_email, text)


def main():
    messages = []
    
    while True:
        msg = input("【You】: ")
        messages.append({"role": "user", "content": msg})
        response = chat_completion_request(
            messages=messages,
            tools=tools
        )
        if content := response.choices[0].message.content:
            print(f"【AI】: {content}")
            messages.append({"role": "assistant", "content": content})
        else:
            fn_name = response.choices[0].message.tool_calls[0].function.name
            fn_args = response.choices[0].message.tool_calls[0].function.arguments
            # print(f"【Debug info】: fn_name - {fn_name}")
            # print(f"【Debug info】: fn_args - {fn_args}")
        
            if fn_name == "send_email":
                try:
                    args = json.loads(fn_args)
                    # 返回将要发送的邮件内容给用户确认
                    print("【AI】: 邮件内容如下：")
                    print(f"发件人: {args['FromEmail']}")
                    print(f"收件人: {args['Recipients']}")
                    print(f"主题: {args['Subject']}")
                    print(f"内容: {args['Body']}")
                    
                    confirm = input("AI: 确认发送邮件吗？ (yes/no): ").strip().lower()
                    if confirm == "yes":
                        send_email(
                            sender_email=args["FromEmail"],
                            sender_authorization_code=AUTHORIZATION_CODE, 
                            recipient_email=args["Recipients"], 
                            subject=args["Subject"], 
                            body=args["Body"],
                        )
                        print("邮件已发送，还需要什么帮助吗？")
                        messages.append({"role": "assistant", "content": "邮件已发送，还需要什么帮助吗？"})
                    else:
                        print("邮件发送已取消，还需要什么帮助吗？")
                        messages.append({"role": "assistant", "content": "邮件发送已取消，还需要什么帮助吗？"})
                except Exception as e:
                    print(f"发送邮件时出错：{e}")
                    messages.append({"role": "assistant", "content": "抱歉，功能异常！"})    


if __name__ == "__main__":
    main()


# 帮我发送一封邮件
# 发件人: 18846050152@163.com, 收件人：2313385026@qq.com, 发送内容写着一封来自未来锅炒蛋的问候邮件，主题随便