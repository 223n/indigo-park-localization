Indigo Park 日本語化 __VERSION__
====================================

Steam版のゲーム「Indigo Park」を日本語で遊ぶための、非公式の日本語化MODです。
開発元や販売元とは関わりがなく、承認も受けていません。


導入のしかた
------------

1. install.bat をダブルクリックします。
2. 「済みました」と出たら閉じます。
3. ゲームを起動します。

Windows の表示言語が日本語なら、これだけで日本語になります。
英語のままのときは、ゲーム内で次の順に選びます。

     OPTIONS → GAMEPLAY → LANGUAGE → 日本語 → APPLY

Steam からゲームの場所を自動で探します。
見つからないときは、その場で入力を求めます。


取り外しかた
------------

uninstall.bat をダブルクリックします。
置いたファイルを消します。言語の設定が日本語なら、英語に戻します。
ゲーム本体のファイルは触りません。

install.bat が置いた UE4SS も消します。
ただし、ほかの UE4SS の MOD があるときは、UE4SS を残します。

ゲームが見つからないときは、uninstall.bat のあるフォルダで、
PowerShell から場所を指定して実行してください。

  powershell -NoProfile -ExecutionPolicy Bypass -File tools\uninstall.ps1 -GamePath "<ゲームのフォルダ>"


手で入れる場合
--------------

mod フォルダの中の IndigoParkJP_P.pak を、次の場所にコピーします。
フォルダが無ければ作ってください。

  <ゲームのフォルダ>\RaccoonCh1\Content\Paks\~mods\

Windows の表示言語が日本語なら、これだけで日本語になります。

この方法では、言語の一覧に「日本語」は出ません。
英語のままのときは Deutsch（ドイツ語）を選んでください。
ドイツ語の訳はゲームに入っていないため、その枠を使っています。


言語の一覧について
------------------

言語の一覧に「日本語」を足すファイルは、配布物に含んでいません。
ゲームのデータそのものを書き換えたものになるためです。
install.bat が、お使いのゲームからその場で作ります。

作るときは、同梱の retoc が、ゲームのデータを読むためのライブラリ
（oo2core_9_win64.dll）をインターネットから取得し、tools フォルダに置きます。
取得先は GitHub の WorkingRobot/OodleUE です。
このファイルは配布物に含んでいません。
retoc は取得したファイルを照合してから使い、次からは置いたものを使います。
取得できないときは、言語の一覧を足す処理に失敗することがあります。
その場合も、Deutsch を選べば日本語で表示されます。


エンディングの歌詞の字幕について
--------------------------------

エンディングの曲の歌詞の訳を、画面の中央下に字幕で出します。
そのために install.bat は、MOD 用の道具 UE4SS を、ゲームの実行ファイルの
フォルダに置きます。

  <ゲームのフォルダ>\RaccoonCh1\Binaries\Win64\

置くのは dwmapi.dll、UE4SS.dll、UE4SS-settings.ini と、Mods フォルダです。
dwmapi.dll はゲームの起動時に読み込まれ、UE4SS を動かします。
ウイルス対策ソフトが、この仕組みを怪しいものとして止めることがあります。

歌詞の訳が入っていない版では、UE4SS は置きません。
UE4SS をすでに入れている場合は、UE4SS には触らず、字幕の MOD だけを足します。
字幕が要らないときは、install.bat のあるフォルダで、PowerShell から
-NoLyrics を付けて実行してください。

  powershell -NoProfile -ExecutionPolicy Bypass -File tools\install.ps1 -NoLyrics

字幕の位置や大きさは、次のファイルで変えられます。
メモ帳で開き、書き換えて保存します。

  <ゲームのフォルダ>\RaccoonCh1\Binaries\Win64\Mods\IndigoParkJP_Lyrics\settings.ini

  position = bottom   中央下に出す
  position = top      中央上に出す

install.bat をもう一度実行すると、このファイルは元に戻ります。


うまくいかないとき
------------------

・文字が表示されない
    フォントの差し替えが効いていません。IndigoParkJP_P.pak が
    ~mods フォルダに入っているか確かめてください。

・英語のまま
    OPTIONS → GAMEPLAY → LANGUAGE で日本語を選び、APPLY を押します。
    日本語が選べないときは Deutsch を選びます。

・install.bat が何も表示せずに閉じる
    PowerShell の実行が止められている可能性があります。
    install.bat のあるフォルダで、PowerShell から次を実行してください。

      powershell -NoProfile -ExecutionPolicy Bypass -File tools\install.ps1

・言語の一覧を足すところで「できませんでした」と出る
    インターネットにつながっているか確かめ、install.bat をもう一度
    実行してください。それでも出るときは Deutsch を選びます。

・ゲームが更新された
    言語の一覧を足す処理が失敗することがあります。
    その場合も、Deutsch を選べば日本語で表示されます。

・エンディングで歌詞の字幕が出ない
    install.bat の「エンディングの歌詞の字幕を入れる」の結果を確かめてください。
    ゲームのフォルダの場所に英数字以外の文字（日本語など）が入っていると、
    UE4SS が字幕の MOD を読み込めないため、入れません。
    ウイルス対策ソフトが dwmapi.dll を止めていないかも確かめてください。
    UE4SS が動いていれば、次のファイルに記録が残ります。

      <ゲームのフォルダ>\RaccoonCh1\Binaries\Win64\UE4SS.log


ライセンス
----------

このMODは Apache License 2.0 です。licenses\LICENSE を見てください。

同梱しているものと、その権利は次のとおりです。

  M PLUS 1p          SIL Open Font License 1.1   licenses\OFL.txt
  retoc              MIT License                 licenses\retoc-LICENSE
  UE4SS              MIT License                 licenses\UE4SS-LICENSE

ゲームに含まれる文、画像、音声などの権利は権利者にあります。
ゲームから取り出したファイルそのものは、この配布物に含んでいません。


連絡先
------

  https://github.com/223n/indigo-park-localization
