# service

あまり意味無いけど、本アプリ(intercom)をサービス化して自動起動する方法を示します。

* [ユニットファイル](intercom.service)
* [ディスプレイサーバー環境変数ファイル](env.conf)
 
~~~sh
cp config/service/intercom.service ~/.config/systemd/user/

# systemdへ登録
systemctl --user enable intercom
systemctl --user restart intercom

# 動作確認(ログチエック)
systemctl --user status intercom
journalctl --user -u intercom
~~~
> なぜか **intercom1** では、ディスプレイに表示されなかった。
