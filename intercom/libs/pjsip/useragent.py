"""UserAgent"""

import pjsua2 as pj

from .error import PJError, PJLogging, logger
from .account import Account as ACC

"""enum pj_log_decoration
{
    PJ_LOG_HAS_DAY_NAME   =    1, /**< Include day name [default: no]         */
    PJ_LOG_HAS_YEAR       =    2, /**< Include year digit [no]                */
    PJ_LOG_HAS_MONTH      =    4, /**< Include month [no]                     */
    PJ_LOG_HAS_DAY_OF_MON =    8, /**< Include day of month [no]              */
    PJ_LOG_HAS_TIME       =   16, /**< Include time [yes]                     */
    PJ_LOG_HAS_MICRO_SEC  =   32, /**< Include microseconds [yes]             */
    PJ_LOG_HAS_SENDER     =   64, /**< Include sender in the log [yes]        */
    PJ_LOG_HAS_NEWLINE    =  128, /**< Terminate each call with newline [yes] */
    PJ_LOG_HAS_CR         =  256, /**< Include carriage return [no]           */
    PJ_LOG_HAS_SPACE      =  512, /**< Include two spaces before log [yes]    */
    PJ_LOG_HAS_COLOR      = 1024, /**< Colorize logs [yes on win32]           */
    PJ_LOG_HAS_LEVEL_TEXT = 2048, /**< Include level text string [no]         */
    PJ_LOG_HAS_THREAD_ID  = 4096, /**< Include thread identification [no]     */
    PJ_LOG_HAS_THREAD_SWC = 8192, /**< Add mark when thread has switched [yes]*/
    PJ_LOG_HAS_INDENT     =16384  /**< Indentation. Say yes! [yes]            */
};

25280=64+128+512+8192+16384 
"""


class UserAgent:
    """User Agent（もしくは Endpoint）の操作

    トランスポートタイプはUDPのみとする。
    UserAgentのインスタンスは、登録後のAccountインスタンスを保持する。
    そのAccountに関連付けられたBuddyインスタンスも保持する。
    また、そのAccountインスタンスは、Callインスタンスのリストを保持する。

    アプリケーション側の制限
      UserAgent のインスタンスを１個だけとする。
      libHandleEvents 関数を実装し、pjsua2 のライブラリィ実行を polling する。
      一対一通話の為、SIP サーバに登録するアカウントを１個だけとする。
      一対一通話の為、アカウントと関連付けるバディを１個だけとする。
    """

    # Endpoint のインスタンスをシングルトンとして扱うためにクラス変数とした。
    endpoint = pj.Endpoint()

    def __init__(self):
        try:
            self.endpoint.libCreate()

            # self.endpoint_config = pj.EpConfig()
            endpoint_config = pj.EpConfig()

            # Python 環境用: アプリケーション側でコールバックを処理
            #   設定しなくても動作するけど、処理の取りこぼしが起こる。
            endpoint_config.uaConfig.threadCnt = 0
            endpoint_config.uaConfig.mainThreadOnly = True

            # 通話品質の設定
            endpoint_config.medConfig.ptime = 20

            # loggingの設定
            # 出力するレベルは、loggerで制御
            self.writer = PJLogging()
            endpoint_config.logConfig.msgLogging = 1
            endpoint_config.logConfig.level = 5
            endpoint_config.logConfig.consoleLevel = 5
            endpoint_config.logConfig.decor = 25280
            # endpoint_config.logConfig.filename ="logs/pjsua2.log"
            # endpoint_config.logConfig.fileFlags = pj.PJ_O_APPEND
            endpoint_config.logConfig.writer = self.writer  # loggerへ出力

            self.endpoint.libInit(endpoint_config)

            transport_config = pj.TransportConfig()
            self.endpoint.transportCreate(pj.PJSIP_TRANSPORT_UDP, transport_config)
            self.endpoint.transportCreate(pj.PJSIP_TRANSPORT_TCP, transport_config)

            self.endpoint.libStart()

        except pj.Error as message:
            raise PJError(message)

        except PJError as message:
            raise PJError(f"UserAgent - constructor: {message}")

        else:
            logger.info(f"UserAgentを開始")

    def __del__(self):
        if "self.buddy" in locals():
            del self.buddy
        if "self.account" in locals():
            del self.account
        self.endpoint.libDestroy()

        logger.info(f"UserAgentを破棄")

    def _validateUri(self, uri: str) -> bool:
        """説明

        :param str uri:
        :return:
        :rtype: bool
        """

        return self.endpoint.utilVerifyUri(uri) == pj.PJ_SUCCESS

    def _validateSipUri(self, uri: str) -> bool:
        """説明

        :param str uri:
        :return:
        :rtype: bool
        """

        return self.endpoint.utilVerifySipUri(uri) == pj.PJ_SUCCESS

    def registryAccount(
        self,
        idUri: str = "sip:name@sipserver",
        registrarUri: str = "sip:sipserver",
        name: str = "name",
        data: str = "password",
    ) -> bool:
        """SIP サーバにアカウントを登録

        :param str idUri: "sip:name@sipserver"
        :param str registrarUri: "sip:sipserver"
        :param str name: "name"
        :param str data: "password"
        :return bool: アカウントが有効かどうか
        """

        try:
            if not self._validateSipUri(uri=registrarUri):
                raise PJError(f"PJSIP: 登録するSIP サーバを見つけられない")

            config = pj.AccountConfig()
            config.idUri = idUri
            config.regConfig.registrarUri = registrarUri

            # AuthCredInfo のインスタンスを生成、認証信任情報を設定
            cred = pj.AuthCredInfo("digest", "asterisk", name, 0, data)
            config.sipConfig.authCreds.append(cred)

            # Account サブクラスのインスタンスを生成、SIP サーバに登録
            self.account = ACC()
            self.account.create(config, True)

        except pj.Error as message:
            pass

        except PJError as message:
            raise PJError(f"UserAgent - registryAccount: {message}")

        else:
            logger.info(f"アカウントを登録した")
            return self.account.isValid()

    def registryBuddy(self, idUri: str = "sip:name@sipserver") -> bool:
        """インターホンの通話相手をアカウントに登録

        :param str idUri: "sip:name@sipserver"
        """

        try:
            config = pj.BuddyConfig()
            config.uri = idUri

            # Buddyをサブクラス化するのが推奨されている
            self.buddy = pj.Buddy()
            self.buddy.create(self.account, config)

        except pj.Error as message:
            pass

        except PJError as message:
            raise PJError(f"UserAgent - registryBuddy: {message}")

        else:
            logger.info(f"通話相手を登録した")
            return self.buddy.isValid()


if __name__ == "__main__":
    print(__file__)
