# SIPサーバーソフト[Asterisk version22.2.0](https://www.asterisk.org/)の導入

SIP(Session Initiation Protocol／複数の端末をつなぐ通信プロトコルの一つ)サーバーは、通信経路を確立する機能を持つ。例えば、AからBへIP電話をかけた場合、まずSIPサーバー経由で端末同士の通信経路を確立する。その他、保留や再開、切断などの処理も行なう。

ただし、音声・映像のやり取りにはVoIPなどの他のデータ伝送プロトコルが必要になる。[Asterisk](https://www.asterisk.org/)に含まれる[PJSIP](https://www.pjsip.org/)（およびPJSUA2）ライブラリィは、SIPの他にVoIPの機能を持っている。

## ダウンロード

~~~sh
wget https://downloads.asterisk.org/pub/telephony/asterisk/asterisk-22.2.0.tar.gz

tar xvf asterisk-22.2.0.tar.gz
~~~

## システム要件のチェック、および関連パッケージのインストール

~~~sh
sudo apt update
sudo apt full-upgrade

cd asterisk-22.2.0/contrib/scripts
sudo ./install_prereq test
sudo ./install_prereq install

## 必要なし
# sudo ./install_prereq install-unpackaged
~~~

## ビルド & インストール

~~~sh
cd asterisk-22.2.0

./configure

## 構成の設定(判らなかったので、デフォルトのまま)
make menuselect

make
sudo make install
sudo make samples
sudo make basic-pbx

## 必要ないかも？
# sudo make progdocs
# sudo make install-headers

## 初期化スクリプトの導入
sudo make config
sudo make install-logrotate
~~~

## 設定ファイルの編集

最低限編集が必要なのは、次の二つ。
> 既定の設定ファイルは、バックアップを取っておくこと
* [/etc/asterisk/extensions.conf](config/asterisk/extensions.conf)
* [/etc/asterisk/pjsip.conf](config/asterisk/pjsip.conf)

## 起動などの主要コマンドのリスト

~~~sh
sudo systemctl daemon-reload
sudo systemctl enable asterisk
sudo systemctl restart asterisk
sudo systemctl status asterisk
sudo systemctl stop asterisk
sudo journalctl -u asterisk
~~~

asterisk コンソール
~~~sh
sudo asterisk -rvvvv
~~~
---