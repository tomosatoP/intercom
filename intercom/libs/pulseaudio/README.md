# [PulseAudio API](https://www.freedesktop.org/software/pulseaudio/doxygen/index.html)

音量コントロールのためにPulseAudio(libpulse)をPython言語から利用する。

https://www.freedesktop.org/wiki/Software/PulseAudio/Documentation/<br>
https://www.freedesktop.org/wiki/Software/PulseAudio/Documentation/Developer/<br>
https://www.freedesktop.org/software/pulseaudio/doxygen/index.html

## 特徴

音量コントロールの対象FACILITYは、４種
  * source
  * source output
  * sink input
  * sink

これらのうちで **sink** , **source** が操作対象FACILITYであり、実際の機器に結びつけられている。複数のマイク、スピーカーがある場合、 **default_sink_name**, **default_source_name** で参照できる。

音量値は音圧で扱うことが多いが全ての機器で保証されているわけではないので、**PulseAudio** では独自のスケールを持っている。
そのために機器によっては、不自然な感じになることが考えられる。


## class VolumePulseaudio

### コンストラクタ

引数 **type** は、操作対象FACILITYに応じて **"SINK"** か **"SOURCE"** を指定する。<br>
引数 **name** は、適宜に文字列を指定する。デフォルトは、"VPA"。


### property facility_name

コンストラクタで指定した **type** に応じて、デフォルトのFACILITY名が得られる。

### property facility_type

コンストラクタで指定した **type** に応じて、FACILITYタイプが得られる。

### property value

**PulseAudio** 独自のスケールによる音量値で、範囲は 0 - 65535

---