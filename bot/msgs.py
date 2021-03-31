import yaml
import discord
from typing import List
from itertools import zip_longest

class MessageTemplates:
    """
    Message template class that allows dot access notation to the templates.
    """

    def __init__(self, filepath):
        with open(filepath) as f:
            self.yaml = yaml.safe_load(f)

    def __getattr__(self, name: str):
        return self.yaml[name]


templates = MessageTemplates("messages.yaml")

ctf_active = True
try:
    ctf_problems = MessageTemplates("problems.yaml")
    ctf_flags = MessageTemplates("flags.yaml")
except FileNotFoundError:
    ctf_active = False


async def send(user: discord.User, msg: str, **kwargs):
    max_size = 2000
    if len(msg) > max_size:
        msg_chunks = chunk(msg, 2000)
        print(msg_chunks)
        print(map(len, msg_chunks))
        for each_msg in msg_chunks[:-1]:
            await user.send(each_msg)

        return await user.send(msg_chunks[-1], **kwargs)
    else:
        return await user.send(msg, **kwargs)


def chunk(msg: str, length: int, tolerance = 200) -> List[str]:
    """
    Chunking with line-wrapping
    TODO: Cleanup more and explain
    """
    chunks = [""]*len(msg)
    msg_lines = msg.splitlines()

    counter = 0
    for count, value in enumerate(msg_lines):
        value += "\n"

        current_chunk = chunks[counter]

        current_length = len(current_chunk)

        if current_length + len(value) <= length:
            current_chunk += value
            chunks[counter] = current_chunk

        elif current_length + tolerance >= length: # within tolerance
            counter += 1

        elif current_length + tolerance < length and current_length + len(value) > length:
            # forced to split text since it is outside the tolernace
            current_chunk += value[:length-current_chunk]
            chunks.append(value[length-current_chunk:])

            counter += 1

        else:
            continue


    return [x for x in chunks if x]

