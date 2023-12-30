import PIL.Image

class Img():
    def __init__(self) -> None:
        self.read_img = None
    def get_img(self, file_path):
        if file_path != "":
            self.read_img = PIL.Image.open(file_path)

class Message():
    def __init__(self, user_name: str, text: str, message_type: str):
        self.user_name = user_name
        self.text = text
        self.message_type = message_type
