"""call"""

import pjsua2 as pj

from .error import PJError, PJLogging, logger


class Call(pj.Call):
    """通話のAudioMediaを操作

    通話のAudioMedia の状態がReady（またはActive）時、その通話のAudioMediaを操作できる。
    インターホンなので、次の２通りのみ接続する。
      [capture device -> conference bridge]
      [conference bridge -> playback device]
    VideoMedia は、取り扱わない。
    """

    def __init__(self, account, call_id=pj.PJSUA_INVALID_ID):
        super().__init__(account, call_id)

    def onCallMediaState(self, prm):
        """通話のメディア状態の変更を通知：必ず実装

        PJSUA2 のPYGUI（Python用サンプルコード）を参照した。
        通話時に、メディアを接続する。
          [capture device -> conference bridge]
          [conference bridge -> playback device]
        :param onCallMediaStateParam prm: コールバック変数
        """

        try:
            audio_device_manager = pj.Endpoint.instance().audDevManager()

            call_info = self.getInfo()
            for call_media_info in call_info.media:
                if call_media_info.type == pj.PJMEDIA_TYPE_AUDIO and (
                    call_media_info.status
                    in [pj.PJSUA_CALL_MEDIA_ACTIVE, pj.PJSUA_CALL_MEDIA_REMOTE_HOLD]
                ):
                    media = self.getMedia(call_media_info.index)
                    audio_media = pj.AudioMedia.typecastFromMedia(media)
                    # capture device -> conference bridge
                    audio_device_manager.getCaptureDevMedia().startTransmit(audio_media)
                    # conference bridge -> playback device
                    audio_media.startTransmit(
                        audio_device_manager.getPlaybackDevMedia()
                    )

        except pj.Error as message:
            pass

        except PJError as message:
            raise PJError(f"call - onCallMediaState: {message}")

        else:
            logger.info(f"音声メディアを接続しました")


if __name__ == "__main__":
    print(__file__)
