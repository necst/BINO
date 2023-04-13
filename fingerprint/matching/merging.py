def blocks_equality(b1, b2):
    if b1.color != b2.color:
        return False
    if b1.is_plt != b2.is_plt:
        return False
    if b1.has_function_call != b2.has_function_call:
        return False
    if b1.function_call_path != b2.function_call_path:
        return False
    if b1.function_call_name != b2.function_call_name:
        return False
    return True


def node_match(node_1, node_2):
    if node_1["type"] == node_2["type"]:
        return True
    return False