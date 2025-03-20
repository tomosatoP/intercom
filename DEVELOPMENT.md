# 開発環境のメモ

## Python言語用仮想環境(venv)の導入

ラズパイ(SSH接続、あるいは **Raspberry Pi Connect** 接続)で行う。
~~~sh
python3 -m venv venv --upgrade-deps
~~~
> VSCodeリモート接続でも同じことができるけど、こっちの方が好き。

## VSCodeリモート環境導入

ラズパイにリモート接続可能なWindowsPCのVSCodeで行う。コーディングは主に、下記の環境で行う。<br>
VSCodeの **Remote-SSH** 拡張機能の導入から実際のリモート接続までは、ここでは説明しません。


* 言語モードの選択
  * 設定 > コマンドパレット > Python:インタープリンターを選択 > おすすめ
     > { } python 3.**.* ('venv')

* 導入する拡張機能
  * Python (Pylance, Python Debugger を含む)
  * Pip Manager
  * Black Formatter

* 変更する設定
  * editor.defaultformatter > Black Formatter
  * editor.formatonsave > ☑
  * black-formatter.args > ["--config", "pyproject.toml"]

* **Pip Manger** で導入するモジュール
  * black
  * isort
  * mypy
  * flake8
