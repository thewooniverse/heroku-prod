import templates


def extract_body(message):
    """
    def extract_body(message): returns the message body of a telegram message
    """
    return " ".join(message.split(' ')[1:])



def start_menu():
    """
    def start_menu(): returns the current template menu message
    """
    return templates.start_menu

