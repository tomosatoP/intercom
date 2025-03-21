# SIPライブラリィ[pjsip version2.15.1](https://www.pjsip.org/)の導入

[PJSIP](https://www.pjsip.org/)は、発着信、保留や再開、切断などの処理も行なう。他に、音声や映像の伝送を行うVoIP機能も持つ。

* [PJSIP](https://www.pjsip.org/)内の主なライブラリィ
  * PJSIPライブラリィ: SIPプロトコル・スタック
  * PJMEDIAライブラリィ: メディアスタック
  * PJNATHライブラリィ: NATトラバーサルスタック

[PJSUA2](https://docs.pjsip.org/en/latest/pjsua2/intro.html)は、[PJSIP](https://www.pjsip.org/)の機能をPythonなどの高水準言語から利用できるようにするために、高水準言語のモジュールを生成するための[SWIG](https://www.swig.org/)インターフェースを提供している。

本アプリも[PJSUA2](https://docs.pjsip.org/en/latest/pjsua2/intro.html)を使ってPython言語で記述している。
Python言語から[PJSUA2](https://docs.pjsip.org/en/latest/pjsua2/intro.html)をモジュールとして追加する際に、仮想環境(venv)を用いている。


> [Asterisk](https://www.asterisk.org/)との衝突を回避するために、**[PJSIP](https://www.pjsip.org/)のバージョン** と **[Asterisk](https://www.asterisk.org/)が含む[PJSIP](https://www.pjsip.org/)のバージョン** とを一致させることが推奨されている。

他にPython用GUIキットの[Kivy](https://kivy.org/)も利用しているので、合わせて導入する。

## ダウンロード

~~~sh
wget https://github.com/pjsip/pjproject/archive/refs/tags/2.15.1.tar.gz
tar xvf 2.15.1.tar.gz
~~~

## システム要件のチェック、および関連パッケージのインストール

~~~sh
sudo apt update
sudo apt full-upgrade

sudo apt install swig fonts-ipaexfont
# python3-dev, python3-setuptools, python3-venv,はインストール済みのはず
~~~


## [PJSIP](https://www.pjsip.org/)のビルド & インストール

~~~sh
cd pjproject-2.15.1

./configure CFLAGS="-fPIC"

make dep
make
sudo make install
~~~

## Python言語用[PJSUA2](https://docs.pjsip.org/en/latest/pjsua2/intro.html)のビルド

~~~sh
cd pjproject-2.15.1/pjsip-apps/src/swig/python

# 結構時間がかかるのに画面表示に変化が無いので、あわてず静かに待つこと!
make
~~~

## Python言語用[PJSUA2](https://docs.pjsip.org/en/latest/pjsua2/intro.html)モジュールの導入

venv仮想環境の構築と、[Kivy](https://kivy.org/)モジュールの導入も合わせて行う。
~~~sh
# 本アプリをダウンロードしたフォルダに移動
# mkdir intercom
cd intercom

python3 -m venv venv --upgrade-deps
. venv/bin/activate

pip install ~/pjproject-2.15.1/pjsip-apps/src/swig/python
pip install kivy[base] kivy-examples

deactivate
~~~

## テスト

~~~sh
cd intercom
. venv/bin/activate

# アカウント情報などの入力待ちになるよ
python libs/pjsip/demo.py

# このテストはSSH経由では動作しない。かならずデスクトップで行うこと。
python venv/share/kivy-examples/demo/showcase/main.py

deactivate
~~~

---
