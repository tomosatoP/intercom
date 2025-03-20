"""account, buddy"""

import pjsua2 as pj

from .error import PJError, PJLogging, logger
from .call import Call as CALL


class Account(pj.Account):
    """アカウントを操作

    アカウントをSIPサーバへ登録する。
    着信を待機し、応答もしくは切断する。
    """

    def __init__(self):
        super().__init__()

        # 切断するまで、callインスタンスを保持する。
        self.call_list = []

    def __del__(self):
        super().shutdown()

    def onIncomingCall(self, prm):
        """着信時の通知

        着信相手を確認し、セッションを開始する。
        :param onIncomingCallParam prm: コールバック変数
        """

        try:
            call = CALL(self, prm.callId)
            call_info = call.getInfo()
            call_prm = pj.CallOpParam()

            # 着信相手をbuddyに限定
            # 書式が異なるので、変換: CallInfo.remoteUri <= BuddyInfo.uri
            buddy_uri_list = map(
                lambda buddy: "<" + buddy.getInfo().uri + ">", self.enumBuddies2()
            )

            if call_info.remoteUri in buddy_uri_list:

                call_prm.statusCode = pj.PJSIP_SC_RINGING
                call.answer(call_prm)

                call_prm.statusCode = pj.PJSIP_SC_OK
                call.answer(call_prm)

                self.call_list.append(call)

            else:
                call.hangup(call_prm)

        except pj.Error as message:
            pass

        except PJError as message:
            raise PJError(f"account - onIncomingCall: {message}")

        else:
            logger.info(f"着信を確認")


if __name__ == "__main__":
    print(__file__)
