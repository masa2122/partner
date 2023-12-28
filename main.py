import flet as ft
from gemini import GeminiApi
import PIL.Image

# メッセージの型
class Message():
    def __init__(self, user_name: str, text: str, message_type: str):
        self.user_name = user_name
        self.text = text
        self.message_type = message_type

# 画像の入れ物
class Img():
    def __init__(self) -> None:
        self.read_img = None
    def get_img(self, file_path):
        if file_path != "":
            self.read_img = PIL.Image.open(file_path)
    
# メッセージの表示作成
class ChatMessage(ft.Row):
    def __init__(self, message: Message):
        super().__init__()
        self.vertical_alignment="start"
        # questionとanswerを分ける
        if message.message_type == 'question':
            messages = ft.Text(message.text, selectable=True)
            icon_color = ft.colors.CYAN
        else:
            messages = ft.Markdown(
                            message.text,
                            selectable=True,
                            extension_set="gitHubWeb",
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

# mainの関数
def main(page: ft.Page):
    # ---------- 画面の設定 ----------
    page.horizontal_alignment = "stretch"
    page.title = "Flet Chat"
    page.update()


    # ---------- message関数 ----------
    # 送信したら
    def send_message_click(e):
        # 文字モード
        if mode_switch.value == "gemini-pro":
            if new_message.value != "":
                text = new_message.value
                on_message(Message('Katsumori', text, message_type="question"))
                new_message.value = ""
                new_message.focus()
                page.update()
                gpt_communication(text)
        # 画像モード
        else:
            if img.read_img != None:
                # image and text
                if new_message.value != "":
                    text = new_message.value
                    on_message(Message('Katsumori', text, message_type="question"))
                    new_message.value = ""
                    new_message.focus()
                    page.update()
                    gpt_communication(text,img_flg=True)
                # image only
                else:
                    on_message(Message('Katsumori', '画像送信', message_type="question"))
                    gpt_communication(new_message.value,img_flg=True)

    # メッセージの表示
    def on_message(message: Message):
        m = ChatMessage(message)
        chat.controls.append(m)
        page.update()


    # ---------- header関数 ----------
    # 画面をリセット
    def delete_chat(e):
        chat.controls.clear()
        page.update()

    # mode変更
    def change_mode(e):
        gemini.change_model(mode_switch.value)
        chat.controls.clear()
        page.update()

    # 履歴のリセット
    def delete_history(e):
        gemini.clear_chat()


    # ---------- GPT系の操作関数 ----------
    # gemini起動
    def gpt_communication(text,img_flg=False):
        if img_flg:
            # text and image
            answer = gemini.run(text=text, file=img.read_img)
            on_message(Message('Gemini', answer, message_type="answer"))
            img.read_img=None
        else:
            # text only
            answer = gemini.run(text)
            on_message(Message('Gemini', answer, message_type="answer"))

    # fileのセット
    def pick_files_result(e: ft.FilePickerResultEvent):
        if e.files:
            img.get_img(e.files[0].path)
    pick_files_dialog = ft.FilePicker(on_result=pick_files_result)
    # hide all dialogs in overlay
    page.overlay.extend([pick_files_dialog])

    # ---------- 型の定義 ----------
    # メッセージの型
    # Chat messages
    chat = ft.ListView(
        expand=True,
        spacing=10,
        auto_scroll=True,
    )

    # 入力の型
    # A new message entry form
    new_message = ft.TextField(
        hint_text="質問をどうぞ！",
        autofocus=True,
        # shift_enter=True,
        min_lines=1,
        max_lines=5,
        filled=True,
        expand=True,
        on_submit=send_message_click,
    )


    # ---------- 初回のみ実行する処理 ----------
    # 初期gemini
    gemini = GeminiApi()
    # img
    img = Img()

    # ---------- 表示の設定 ----------
    # chat_model切り替え
    mode_switch = ft.Dropdown(
        on_change=change_mode,
        options=[
            ft.dropdown.Option("gemini-pro"),
            ft.dropdown.Option("gemini-pro-vision"),
        ],
        value="gemini-pro",
        width=200,
    )

    # head
    head = ft.Row(
        controls=[
            mode_switch,
            ft.IconButton(
                    icon=ft.icons.DELETE_FOREVER_ROUNDED,
                    icon_color="pink600",
                    icon_size=40,
                    tooltip="Delete chat",
                    on_click=delete_chat,
                ),
            ft.IconButton(
                    icon=ft.icons.CLEAR,
                    icon_color="pink600",
                    icon_size=40,
                    tooltip="Delete history",
                    on_click=delete_history,
                ),
        ]
    )


    # ---------- 全体の構造 ----------
    page.add(
        head,
        ft.Container(
            content=chat,
            border=ft.border.all(1, ft.colors.OUTLINE),
            border_radius=5,
            padding=10,
            expand=True,
        ),
        ft.Row(
            controls=[
                new_message,
                ft.IconButton(
                    icon=ft.icons.UPLOAD_FILE,
                    on_click=lambda _: pick_files_dialog.pick_files(
                        file_type='IMAGE',
                        ),
                ),
                ft.IconButton(
                    icon=ft.icons.SEND_ROUNDED,
                    tooltip="Send message",
                    on_click=send_message_click,
                ),
            ]
        ),
    )


ft.app(main)