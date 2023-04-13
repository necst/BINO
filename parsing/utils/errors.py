def manage_errors(e):
    if not (str(e) == "Unknown template argument kind 441" or
        str(e) == "Unknown template argument kind 440"):
        raise Exception(e)
