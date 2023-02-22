"""
Format danbooru tag input for desu.ai

Able to format danbooru URLs, tags and files (including nested ones).

Usage: desuai_formatter.py <input>
Input can be:
  - A danbooru post URL
  - A file
  - Unformatted tags

Thanks parabirb for regex and LuqueDaniel for pybooru. 
Nothing in here is remotely pythonic, please dont expect it to be.
"""

import sys
import re
import os
from pybooru import Danbooru

client = Danbooru('danbooru')

def detection(input_str):
    # Regular expression to match a file or path
    path_regex = r'^([^:]+\..+)|(\/.*)|([A-Za-z]:\\.*)$'
    # Regular expression to match a URL
    url_regex = r'^https?://danbooru\.donmai\.us/posts/\d+.*$'
    # Check if the input matches either regular expression
    if re.match(path_regex, input_str):
        return "File"
    elif re.match(url_regex, input_str):
        return "URL"
    else:
        return "Tags"

def file_format(nested_file = None):
    if nested_file == None:
        input_file = r"" + sys.argv[1]
        output_file = os.path.splitext(sys.argv[1])[0] + "_formatted.txt"
        nstd = False
    else:
        input_file = r"" + nested_file
        output_file = os.path.splitext(nested_file)[0] + "_formatted.txt"
        nstd = True

    with open(input_file, "r") as f_in, open(output_file, "w") as f_out:
        for line in f_in:
            if detection(line) == "URL":
                print((f"[NESTED FILE] ({os.path.basename(input_file)}) " if nstd else f"[BASE FILE] ({os.path.basename(input_file)}) ") + f"Detected as a URL: {line.rstrip()}")
                postidregex = r"/posts/(\d+)"
                # Use regex to extract the post ID from the URL
                match = re.search(postidregex, line)
                if match:
                    post_id = match.group(1)
                    print((f"[NESTED FILE] ({os.path.basename(input_file)}) " if nstd else f"[BASE FILE] ({os.path.basename(input_file)}) ") + f"Post ID: {post_id}")
                    post = client.post_show(post_id)
                    # Extract the tags from the post information
                    tags = post['tag_string']
                    tag = tags.replace(" ", ", ")
                    tag = tag.replace("_", " ")
                    f_out.write(tag+"\n")
                else:
                    print((f"[NESTED FILE] ({os.path.basename(input_file)}) " if nstd else f"[BASE FILE] ({os.path.basename(input_file)}) ") + f"No post ID found in URL: {line}")
            elif detection(line) == "File":
                print((f"[NESTED FILE] ({os.path.basename(input_file)}) " if nstd else f"[BASE FILE] ({os.path.basename(input_file)}) ") + f"Nested file detected: {line.strip()}")
                file_format(line.strip())
            elif detection(line) == "Tags":
                print((f"[NESTED FILE] ({os.path.basename(input_file)}) " if nstd else f"[BASE FILE] ({os.path.basename(input_file)}) ") + f"Tags detected: {(line[:103] + '...')}") # Limit to 100 chars (excluding the ...)
                tag = line.replace(" ", ", ")
                tag = tag.replace("_", " ")
                f_out.write(tag+"\n")
        print((f"[NESTED FILE] ({os.path.basename(input_file)}) " if nstd else f"[BASE FILE] ({os.path.basename(input_file)}) ") + "Formatted tags saved to: " + output_file)

def main():
    try:
        input = sys.argv[1]
    except IndexError:
        print("Usage: desuai_formatter.py <input>\nInput can be:\n  - A danbooru post URL\n  - A file\n  - Unformatted tags")
        exit(1)

    if detection(input) == "File":
        file_format()
    elif detection(input) == "Tags":
        print(f"Tags detected: {(input[:103] + '...')}")
        tag = input.replace(" ", ", ")
        tag = tag.replace("_", " ")
        print("Formatted tags: " + tag)
    elif detection(input) == "URL":
        print(f"Detected as a URL: {input.rstrip()}")
        postidregex = r"/posts/(\d+)"
        # Use regex to extract the post ID from the URL
        match = re.search(postidregex, input)
        if match:
            post_id = match.group(1)
            print(f"Post ID: {post_id}")
            post = client.post_show(post_id)
            # Extract the tags from the post information
            tags = post['tag_string']
            tag = tags.replace(" ", ", ")
            tag = tag.replace("_", " ")
            print("Formatted tags: " + tag)
        else:
            print(f"No post ID found in URL: {input}")

main()