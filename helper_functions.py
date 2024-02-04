def extract_body(message):
    """
    def extract_body(message): returns the message body of a telegram message
    """
    return " ".join(message.split(' ')[1:])