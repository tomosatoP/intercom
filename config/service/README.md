# service

本アプリ(intercom)をサービス化して自動起動する方法を示します。

* [ユニットファイル](intercom.service)
* [X server 用環境変数ファイル](env.conf)
 
~~~sh
cp config/service/intercom.service ~/.config/systemd/user/

# systemdへ登録
systemctl --user enable intercom
systemctl --user restart intercom

# 動作確認(ログチエック)
systemctl --user status intercom
journalctl --user -u intercom
~~~
