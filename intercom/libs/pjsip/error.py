"""error & logging"""

import typing as Any
import logging as LPJ
import pjsua2 as pj


#### libpulseAPI用のロギング
logger = LPJ.getLogger(__name__)
logger.setLevel(LPJ.INFO)


class PJLogging(pj.LogWriter):
    """カスタムLogWriter

    PJSUA2のログをPythonのloggingモジュールのloggerへ転送
    """

    def __init__(self):
        super().__init__()

    def write(self, entry):
        match entry.level:
            case 5:  # trace
                logger.debug(entry.msg.strip())
            case 4:  # debug
                logger.debug(entry.msg.strip())
            case 3:  # info
                logger.info(entry.msg.strip())
            case 2:  # warning
                logger.warning(entry.msg.strip())
            case 1:  # error
                logger.error(entry.msg.strip())
            case 0:  # critical
                logger.critical(entry.msg.strip())


class PJError(Exception):
    """pjsua2以外のエラーハンドラー"""

    def __init__(self, *args: object) -> Any:
        super().__init__(*args)

        logger.error(f"PJError: {args}")
