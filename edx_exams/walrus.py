def get_context_file(uri):
    # return ""
    return "myurifile"

context = {
    # "uri": "",
    "uri": "myuri",
    "content": "mycontent"
}

(data := (uri := context.get("uri")) and get_context_file(uri) or context.get('content'))
print(data)
