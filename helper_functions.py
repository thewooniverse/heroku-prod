import templates
import os


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



# def delete_temp(path):
#     """
#     def delete_temp(path): Takes a temporary file at Pathlib Path and tries to delete it, returns deleted or not.
#     """
#     if os.path.isfile(path):
#         print("Removed file")
#         os.remove(path)
#     else:
#         print("Failed to remove file, file does not exist")
#         return None




