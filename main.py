import flet as ft
from module.gemini import GeminiApi
from module.deepl import Deepl
from main_types import Message, Img


# メッセージの表示作成
class ChatMessage(ft.Row):
    def __init__(self, message: Message):
        super().__init__()
        self.vertical_alignment="start"
        # questionとanswerを分ける
        match message.message_type:
            case 'question':
                messages = ft.Text(message.text, selectable=True)
                icon_color = ft.colors.CYAN
            case 'answer':
                messages = ft.Markdown(
                                message.text,
                                selectable=True,
                                extension_set="gitHubFlavored",
                                code_theme="a11y-dark",
                                code_style=ft.TextStyle(font_family="Roboto Mono"),
                                # on_tap_link=lambda e: page.launch_url(e.data),
                            )
                icon_color = ft.colors.GREEN

        self.controls=[
                ft.CircleAvatar(
                    content=ft.Text(message.user_name[:1].capitalize()),
                    color=ft.colors.WHITE,
                    bgcolor=icon_color,
                ),
                ft.Column(
                    [
                        ft.Text(message.user_name, weight="bold"),
                        messages,
                    ],
                    tight=True,
                    spacing=5,
                    expand=True,
                ),
            ]


class Partner(ft.View):
    def __init__(self):
        # ---------- 初回のみ実行する処理 ----------
        # 初期gemini
        self.gemini = GeminiApi()
        # img
        self.img = Img()
        # deepl
        self.deepl = Deepl()
        self.lang_dict_keys = self.deepl.lang_dict.keys()


        # ---------- head ----------
        self.main_title = ft.Text("gemini-pro")
        # head
        head_area = ft.Row(
            controls=[
                self.main_title
            ]
        )


        # ---------- body ----------
        # メッセージの型
        # Chat messages
        self.chat = ft.ListView(
            expand=True,
            spacing=10,
            auto_scroll=True,
        )
        view_area = ft.Container(
                content=self.chat,
                border=ft.border.all(1, ft.colors.OUTLINE),
                border_radius=5,
                padding=10,
                expand=True,
            )

        # 入力の型
        # A new message entry form
        self.new_message = ft.TextField(
            label="je/ ej/ j/ cm/ dc/ dh/",
            autofocus=True,
            # shift_enter=True,
            multiline=True,
            min_lines=1,
            max_lines=5,
            filled=True,
            expand=True,
            on_submit=self.send_message_click,
        )

        # 送るボタン
        self.send_btn = ft.IconButton(
                        icon=ft.icons.SEND_SHARP,
                        selected_icon=ft.icons.CANCEL_SCHEDULE_SEND_SHARP,
                        tooltip="Send message",
                        on_click=self.send_message_click,
                        selected=False,
                        disabled=False,
                        style=ft.ButtonStyle(color={"selected": ft.colors.GREY_400, "": ft.colors.BLUE}),
                    )

        # ダイアログの設定
        self.pick_files_dialog = ft.FilePicker(on_result=self.pick_files_result)
        # file button
        self.file_btn = ft.IconButton(
                        icon=ft.icons.UPLOAD_FILE,
                        tooltip="Up file",
                        visible=False,
                        on_click=lambda _: self.pick_files_dialog.pick_files(
                            file_type='IMAGE',
                            ),
                    )

        input_area = ft.Row(
                controls=[
                    self.new_message,
                    self.file_btn,
                    self.send_btn,
                ]
            )

        super().__init__(controls=[head_area,view_area,input_area,])


    # ---------- message関数 ----------
    # 送信したら
    def send_message_click(self,e):
        # 拡張期のは/を付ける
        text = self.new_message.value
        # command check
        index = text[:4].find('/')
        if index != -1:  # '/'が/見つかった場合
            command = text[:index]
            # 言語に一致するか（追加コマンドはここに追加していく）
            if command in self.lang_dict_keys:
                self.on_message(Message('Katsumori', text, message_type="question"))
                self.clear_message()

                answer = self.deepl.transform(command,text[index+1:])
                self.on_message(Message('Deepl', answer, message_type="answer"))
                return
            elif command == "cm":
                self.clear_message()
                self.change_mode(e)
                return
            elif command == "dc":
                self.clear_message()
                self.delete_chat(e)
                return
            elif command == "dh":
                self.clear_message()
                self.delete_history(e)
                return

        match self.main_title.value:
            case "gemini-pro":   # 文字モード
                self.gemini_pro(text)

            case "gemini-pro-vision":   #画像モード
                self.gemini_pro_vision(text)


    # メッセージの表示
    def on_message(self,message: Message):
        self.send_btn.selected = not self.send_btn.selected
        self.send_btn.disabled = not self.send_btn.disabled
        m = ChatMessage(message)
        self.chat.controls.append(m)
        self.clear_message()

    def clear_message(self):
        self.new_message.value = ""
        self.new_message.focus()
        self.update()


    # ---------- header関数 ----------
    # 画面をリセット
    def delete_chat(self,e):
        self.chat.controls.clear()
        self.update()

    # mode変更
    def change_mode(self,e):
        current_model = self.main_title.value
        match current_model:
            case "gemini-pro":
                model_name = "gemini-pro-vision"
                self.main_title.value = model_name
            case "gemini-pro-vision":
                model_name = "gemini-pro"
                self.main_title.value = model_name

        self.gemini.change_model(model_name)
        self.file_btn.visible = not self.file_btn.visible
        self.chat.controls.clear()
        self.update()

    # 履歴のリセット
    def delete_history(self,e):
        self.gemini.clear_chat()


    # ---------- GPT系の操作関数 ----------
    # gemini-pro
    def gemini_pro(self, text):
        if text != "":
            # 送信した文字を送信リセット
            self.on_message(Message('Katsumori', text, message_type="question"))
            self.clear_message()
            # text送信
            self.gpt_communication(text)

    # gemini-pro-vision
    def gemini_pro_vision(self,text):
        if self.img.read_img != None:
                    # image and text
                    if text != "":
                        self.on_message(Message('Katsumori', text, message_type="question"))
                        self.clear_message()
                        self.gpt_communication(text,img_flg=True)
                    # image only
                    else:
                        self.on_message(Message('Katsumori', '画像送信', message_type="question"))
                        self.gpt_communication(text,img_flg=True)

    # gemini起動
    def gpt_communication(self,text,img_flg=False):
        if img_flg:
            # text and image
            answer = self.gemini.run(text=text, file=self.img.read_img)
            self.on_message(Message('Gemini', answer, message_type="answer"))
            self.img.read_img=None
        else:
            # text only
            answer = self.gemini.run(text)
            self.on_message(Message('Gemini', answer, message_type="answer"))

    # fileのセット
    def pick_files_result(self,e: ft.FilePickerResultEvent):
        if e.files:
            self.img.get_img(e.files[0].path)

def main(page: ft.Page):
    # ---------- 画面の設定 ----------
    page.horizontal_alignment = "stretch"
    page.title = "Partner"
    page.update()
    pt = Partner()
    # hide all dialogs in overlay
    page.overlay.extend([pt.pick_files_dialog])
    
    page.views.append(pt)
    page.update()

ft.app(main)

