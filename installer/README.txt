Indigo Park - 日本語化Mod __VERSION__
====================================

Steam版のゲーム「Indigo Park」を日本語で遊ぶための、非公式の日本語化MODです。
開発元や販売元とは関わりがなく、承認も受けていません。


導入のしかた
------------

1. install.batをダブルクリックします。
2. "済みました"と表示されたら閉じます。
3. ゲームを起動します。

Windowsの表示言語が日本語なら、これだけで日本語になります。

Steamからゲームの場所を自動で探します。
見つからないときは、その場で入力を求めます。


取り外しかた
------------

uninstall.batをダブルクリックします。
置いたファイルを消します。言語の設定が日本語なら、英語に戻します。
ゲーム本体のファイルは触りません。

install.batが置いたUE4SSも消します。
ただし、ほかのUE4SSのMODがあるときは、UE4SSを残します。

ゲームが見つからないときは、uninstall.batのあるフォルダーで、
PowerShellから場所を指定して実行してください。

  powershell -NoProfile -ExecutionPolicy Bypass -File tools\uninstall.ps1 -GamePath "<ゲームのフォルダー>"


手で入れる場合
--------------

modフォルダーの中のIndigoParkJP_P.pakを、次の場所にコピーします。
フォルダーがなければ作ってください。

  <ゲームのフォルダー>\RaccoonCh1\Content\Paks\~mods\

Windowsの表示言語が日本語なら、これだけで日本語になります。


言語の一覧について
------------------

言語の一覧に「日本語」を足すファイルは、配布物に含んでいません。
ゲームのデータそのものを書き換えたものになるためです。
install.batが、お使いのゲームからその場で作ります。

作るときは、同梱のretocが、ゲームのデータを読むためのライブラリ
（oo2core_9_win64.dll）をインターネットから取得し、toolsフォルダーに置きます。
取得先はGitHubのWorkingRobot/OodleUEです。
このファイルは配布物に含んでいません。
retocは取得したファイルを照合してから使い、次からは置いたものを使います。
取得できないときは、言語の一覧を足す処理に失敗することがあります。


エンディングの歌詞の字幕について
--------------------------------

エンディングの曲の歌詞の訳を、画面の中央下に字幕で出します。
そのためにinstall.batは、MOD用の道具UE4SSを、ゲームの実行ファイルの
フォルダーに置きます。

  <ゲームのフォルダー>\RaccoonCh1\Binaries\Win64\

置くのはdwmapi.dll、UE4SS.dll、UE4SS-settings.iniと、Modsフォルダーです。
dwmapi.dllはゲームの起動時に読み込まれ、UE4SSを動かします。
ウイルス対策ソフトが、この仕組みを怪しいものとして止めることがあります。

UE4SSをすでに入れている場合は、UE4SSには触らず、字幕のMODだけを足します。
字幕が要らないときは、install.batのあるフォルダーで、PowerShellから
-NoLyricsを付けて実行してください。

  powershell -NoProfile -ExecutionPolicy Bypass -File tools\install.ps1 -NoLyrics

字幕の位置や大きさは、次のファイルで変えられます。
メモ帳で開き、書き換えて保存します。

  <ゲームのフォルダー>\RaccoonCh1\Binaries\Win64\Mods\IndigoParkJP_Lyrics\settings.ini

  position = bottom   中央下に出す
  position = top      中央上に出す

install.batをもう一度実行すると、このファイルは元に戻ります。


うまくいかないとき
------------------

・文字が表示されない
    フォントの差し替えが効いていません。IndigoParkJP_P.pakが
    ~modsフォルダーに入っているか確かめてください。

・英語のまま
    "OPTIONS" → "GAMEPLAY" → "LANGUAGE" で "日本語" を選び、 "APPLY" を押します。
    日本語が選べないときはDeutschを選びます。

・install.batが何も表示せずに閉じる
    PowerShellの実行が止められている可能性があります。
    install.batのあるフォルダーで、PowerShellから次を実行してください。

      powershell -NoProfile -ExecutionPolicy Bypass -File tools\install.ps1

・言語の一覧を足すところで「できませんでした」と出る
    インターネットにつながっているか確かめ、install.batをもう一度
    実行してください。それでも出るときはDeutschを選びます。

・ゲームが更新された
    言語の一覧を足す処理が失敗することがあります。
    その場合も、Deutschを選べば日本語で表示されます。

・エンディングで歌詞の字幕が出ない
    install.batの「エンディングの歌詞の字幕を入れる」の結果を確かめてください。
    ゲームのフォルダーの場所に英数字以外の文字（日本語など）が入っていると、
    UE4SSが字幕のMODを読み込めないため、入れません。
    ウイルス対策ソフトがdwmapi.dllを止めていないかも確かめてください。
    UE4SSが動いていれば、次のファイルに記録が残ります。

      <ゲームのフォルダー>\RaccoonCh1\Binaries\Win64\UE4SS.log


ライセンス
----------

このMODはApache License 2.0です。
licenses\LICENSEを見てください。

同梱しているものと、その権利は次のとおりです。

  M PLUS 1p          SIL Open Font License 1.1   licenses\OFL.txt
  retoc              MIT License                 licenses\retoc-LICENSE
  UE4SS              MIT License                 licenses\UE4SS-LICENSE

ゲームに含まれる文、画像、音声などの権利は権利者にあります。
ゲームから取り出したファイルそのものは、この配布物に含んでいません。


連絡先
------

  https://github.com/223n/indigo-park-localization
