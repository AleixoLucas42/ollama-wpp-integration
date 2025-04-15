#!/bin/python3
import sched
import time
import requests
import json
import os
import logging
import sys
import threading

logging.basicConfig(
    level=f"{os.getenv('LOG_LEVEL', 'INFO')}",
    format="%(asctime)s - %(levelname)s - %(message)s",
)

global last_prompt
global last_prompt_message_id
global last_message_from

last_prompt_message_id = ""
last_prompt = ""
last_message_from = ""

scheduler = sched.scheduler(time.time, time.sleep)


def spinner_loading(message, stop_event):
    spinner = ["|", "/", "-", "\\"]
    idx = 0
    while not stop_event.is_set():
        sys.stdout.write(f"\r{message} {spinner[idx % len(spinner)]}")
        sys.stdout.flush()
        time.sleep(0.1)
        idx += 1
    sys.stdout.write("\r" + " " * (len(message) + 2) + "\r")


def check_messages():
    global last_prompt
    global last_prompt_message_id
    global last_message_from

    logging.info("Looking for new prompt")
    url = f"{os.environ['WHATSAPP_URL']}/chat/fetchMessages/{os.environ['WHATSAPP_SESSION']}"
    payload = json.dumps({
        "chatId": f"{os.environ['WHATSAPP_CHAT_ID']}",
    })
    headers = {"accept": "*/*", "Content-Type": "application/json"}

    response = requests.request(
        "POST", url, headers=headers, data=payload, verify=False
    )
    data = response.json()
    logging.debug(response.text)

    if data.get("messages"):
        last_prompt_message_id = data["messages"][-1]["id"]["id"]
        last_message = data["messages"][-1]["body"]
        last_message_from = data["messages"][-1]["from"]
        if (
            last_message == last_prompt
            or last_message_from == os.environ["WHATSAPP_NUMBER_ID"]
        ):
            logging.info("No new prompts")
        else:
            logging.info(f"Prompt: {last_message}")
            logging.info(f"Requester: {last_message_from}")
            send_typing_state()
            ask_ollama(last_message)
            last_prompt = last_message
    else:
        logging.error(response.text)
        send_wpp_msg("Something went wrong")

    logging.info("Waiting 10s")
    scheduler.enter(10, 1, check_messages)


def ask_ollama(prompt):
    logging.info("Asking Ollama")
    stop_event = threading.Event()
    spinner_thread = threading.Thread(
        target=spinner_loading, args=("Loading...", stop_event)
    )
    spinner_thread.start()
    url = f"{os.environ['OLLAMA_URL']}/api/chat/completions"

    payload = json.dumps({
        "model": f"{os.environ['OLLAMA_MODEL']}",
        "messages": [{"role": "user", "content": f"{prompt}"}],
    })
    headers = {
        "Authorization": f"Bearer {os.environ['OLLAMA_TOKEN']}",
        "Content-Type": "application/json",
    }

    response = requests.request(
        "POST", url, headers=headers, data=payload, verify=False
    )

    logging.debug(response.text)
    data = response.json()
    stop_event.set()
    spinner_thread.join()
    send_wpp_msg(data["choices"][0]["message"]["content"])


def send_typing_state():
    logging.debug("Sending typing state")
    url = f"{os.environ['WHATSAPP_URL']}/chat/sendStateTyping/{os.environ['WHATSAPP_SESSION']}"

    payload = json.dumps({"chatId": f"{os.environ['WHATSAPP_CHAT_ID']}"})
    headers = {"accept": "*/*", "Content-Type": "application/json"}

    response = requests.request(
        "POST", url, headers=headers, data=payload, verify=False
    )
    logging.debug(response.text)


def send_wpp_msg(msg):
    global last_message_from

    # Verificando se o número está na lista de contatos
    user_name = contacts.get(last_message_from, "Usuário Desconhecido")  # Valor padrão se não encontrar o número

    logging.info(f"Sending whatsapp message tagging {user_name}")
    url = f"{os.environ['WHATSAPP_URL']}/message/reply/{os.environ['WHATSAPP_SESSION']}"

    # Formato de menção no WhatsApp
    mention_placeholder = f"@{user_name}"  # Usando o nome do usuário como placeholder
    content_with_mention = f"{mention_placeholder} {msg}"

    # A menção precisa ser o ID completo do usuário, por exemplo, '5511999999999@c.us'
    # Adicionando o número de telefone completo no campo 'mentions'
    payload = json.dumps({
        "chatId": f"{os.environ['WHATSAPP_CHAT_ID']}",
        "messageId": f"{last_prompt_message_id}",
        "contentType": "string",
        "content": content_with_mention,
        "mentions": [last_message_from],  # Isso é o identificador do número, ex: '5511999999999@c.us'
    })
    headers = {"accept": "*/*", "Content-Type": "application/json"}

    response = requests.request(
        "POST", url, headers=headers, data=payload, verify=False
    )

    if response.status_code != 200:
        logging.error(response.text)

    logging.debug(response.text)


if __name__ == "__main__":
    scheduler.enter(5, 1, check_messages)
    scheduler.run()
