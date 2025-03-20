"""intercom"""

from contextlib import contextmanager
from pathlib import Path

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty

import pjsua2 as pj
from libs.pjsip.useragent import UserAgent as UA
from libs.pjsip.account import Account as ACC
from libs.pjsip.call import Call as CALL

from libs.pulseaudio.libpulse import VolumePulseaudio as VPA

from configparser import ConfigParser

ini_dir = str(Path().absolute()) + "/config"
config = ConfigParser()
config.read(ini_dir + "/intercom.ini")


class MainBoxLayout(BoxLayout):
    """メインビュー

    このビューをrootとして全画面モードで表示する。
    """

    # タイトルバー(終了ボタンを含む)
    titlebar = ObjectProperty()
    # マイク音量調整
    micvolume = ObjectProperty()
    # スピーカー音量調整
    speakervolume = ObjectProperty()
    # 通話ボタン
    calltogglebutton = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.user_agent = UA()

        # PJSUA2ライブラリィの実行をポーリング開始
        Clock.schedule_interval(self.polling_pjlib, 0.01)

        # アカウント登録
        self.user_agent.registryAccount(
            config["DEFAULT"]["AccountUri"],
            config["DEFAULT"]["SipServer"],
            config["DEFAULT"]["AccountName"],
            config["DEFAULT"]["AccountData"],
        )

        # 接続可の通話先登録
        self.user_agent.registryBuddy(config["DEFAULT"]["BuddyUri"])

        # 通話状態の監視を開始(通話中かどうか、通話可能かどうか)
        self.event = Clock.schedule_interval(self.notify_invite, 0.1)
        Clock.schedule_interval(self.notify_callabled, 0.1)

        # マイクの音量コントロールを登録
        self.micvolume.device.text = "マイク"
        self.vpa_mic = VPA("SOURCE", "mic")
        Clock.schedule_interval(self.get_micvolume_value, 0.1)
        self.micvolume.slider.bind(value=self.set_micvolume_value)

        # スピーカーの音量コントロールを登録
        self.speakervolume.device.text = "スピーカー"
        self.vpa_speaker = VPA("SINK", "speaker")
        Clock.schedule_interval(self.get_speakervolume_value, 0.1)
        self.speakervolume.slider.bind(value=self.set_speakervolume_value)

    def polling_pjlib(self, dt):
        """callback: pjsua2ライブラリィの実行をpolling

        :param float dt: 呼び出しの秒間隔
        """

        # 引数: 最大待機時間（ミリ秒単位）
        # 利用上の注意点－呼び出し元のスレッドをブロックする。
        self.user_agent.endpoint.libHandleEvents(10)

    def get_micvolume_value(self, dt):
        """callback: マイクの音量値をビューに反映

        :param float dt: 呼び出しの秒間隔
        """
        self.micvolume.slider.value = self.vpa_mic.value

    def get_speakervolume_value(self, dt):
        """callback: スピーカーの音量値をビューに反映

        :param float dt: 呼び出しの秒間隔
        """
        self.speakervolume.slider.value = self.vpa_speaker.value

    def set_micvolume_value(self, obj, value: int):
        """ビューからマイクの音量値を設定

        :param int value: 音量値
        """

        self.vpa_mic.value = int(value)

    def set_speakervolume_value(self, obj, value: int):
        """ビューからスピーカーの音量値を設定

        :param int value: 音量値
        """

        self.vpa_speaker.value = int(value)

    @contextmanager
    def pause_clockevent(self, clockevent):
        """ClockEvent を一時中断

        :param clockevent event: 中断したいclockイベント
        """

        def clockEventPause(clockevent):
            clockevent.cancel()

        try:
            yield
        finally:
            clockevent()

    def on_press_calltogglebutton(self, state):
        """通話ボタン(calltogglebutton)をpressした際の操作

        normal(非通話) <- down(通話中): 着信の通話／発信の通話を切断する
        down(通話中) <- normal(非通話): 発信する

        :param str state: calltogglebutton.state
        """

        # この処理中、Clockイベント(notify_inviteルーチン) を一時停止する
        with self.pause_clockevent(self.event):
            if state == "normal":
                # down(通話中) -> normal(非通話)
                self.hang_up()
            else:
                # normal(非通話) -> down(発信)
                self.make_call()

    def hang_up(self):
        """通話の切断

        発信の通話でも着信の通話でも切断します。
        """

        call = self.user_agent.account.call_list[-1]
        prm = pj.CallOpParam()
        call.hangup(prm)

        self.user_agent.account.call_list.pop()

    def make_call(self):
        """通話の発信

        接続可の通話先への発信
        """

        prm = pj.CallOpParam()
        prm.opt.audioCount = 1
        prm.opt.videoCount = 0

        call = CALL(self.user_agent.account)
        call.makeCall(self.user_agent.buddy.getInfo().uri, prm)

        self.user_agent.account.call_list.append(call)

    def notify_invite(self, dt):
        """callback: 通話状態(通話[INVITE]/切断[not INVITE])をビューに反映

        通話状態に応じて、calltogglebutton.stateを変更します。
        * 通話中: calltogglebutton.state を"down"にする。
        * 切断状態(無CALLを含む): calltogglebutton.state を"normal"にする。

        :param float dt: 呼び出しの秒間隔
        """

        if self.user_agent.account.call_list:
            values = [
                self.calltogglebutton.state,
                self.user_agent.account.call_list[-1].isActive(),
            ]
            match values:
                case ["normal", True]:
                    self.calltogglebutton.state = "down"
                case ["down", False]:
                    self.calltogglebutton.state = "normal"
                case _:
                    pass
        else:
            self.calltogglebutton.state = "normal"

    def notify_callabled(self, dt):
        """callback: 通話可能かどうかをビューに反映

        True & ONLINE時に通話可能とする。
        * アカウントが登録されている True/False
        * バディがオンライン ONLINE/OFFLINE/UNKNOWN

        :param float dt: 呼び出しの秒間隔
        """

        self.user_agent.buddy.updatePresence()

        values = []
        values.append(self.user_agent.account.getInfo().regIsActive)
        values.append(self.user_agent.buddy.getInfo().presStatus.status)
        match values:
            case [True, pj.PJSUA_BUDDY_STATUS_ONLINE]:
                self.titlebar.title.text = "インターホン: OK"
            case [True, pj.PJSUA_BUDDY_STATUS_OFFLINE]:
                self.titlebar.title.text = "インターホン: True, OFFLINE"
            case [True, pj.PJSUA_BUDDY_STATUS_UNKNOWN]:
                self.titlebar.title.text = "インターホン: True, UNKNOWN"
            case [False, pj.PJSUA_BUDDY_STATUS_ONLINE]:
                self.titlebar.title.text = "インターホン: False, ONLINE"
            case [False, pj.PJSUA_BUDDY_STATUS_OFFLINE]:
                self.titlebar.title.text = "インターホン: False, OFFLINE"
            case [False, pj.PJSUA_BUDDY_STATUS_UNKNOWN]:
                self.titlebar.title.text = "インターホン: False, UNKNOWN"
            case _:
                self.titlebar.title.text = "インターホン: NO"


class IntercomApp(App):
    def build(self):
        self.root = MainBoxLayout()
        return self.root

    def on_stop(self):
        super().on_stop()


if __name__ == "__main__":
    IntercomApp().run()
