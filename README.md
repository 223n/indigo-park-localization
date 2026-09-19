# Indigo Park 日本語化

[![Apache-2.0](https://custom-icon-badges.herokuapp.com/badge/license-Apache%202.0-8BB80A.svg?logo=law&logoColor=white)](LICENSE)
[![Windows](https://custom-icon-badges.herokuapp.com/badge/Windows-1BB2E4.svg?logo=Windows&logoColor=white)](./)

Steam版のゲーム「Indigo Park」を日本語で遊ぶための、非公式の日本語化MODです。
翻訳した文と、それをゲームへ適用する仕組みをこのリポジトリで管理します。

開発元や販売元とは関わりがありません。
ゲーム本体のファイルも含みません。

- ゲームリンク: [Indigo Park(Steam)](https://store.steampowered.com/app/2504480/Indigo_Park_Chapter_1/)
- ゲーム作者YouTubeチャンネル: [UniqueGeese](https://www.youtube.com/channel/UC9BkT4lu2bby5wdQe1brQHA)

## 対象

| 項目         | 内容                     |
|--------------|--------------------------|
| ゲーム       | Indigo Park（Chapter 1） |
| 入手先       | Steam                    |
| 動く環境     | Windows                  |
| 翻訳する向き | 英語から日本語へ         |

Steamの既定の導入先は`C:\Program Files (x86)\Steam\steamapps\common\Indigo Park`です。
実行ファイルは`RaccoonCh1.exe`で、ゲームのデータは`RaccoonCh1\Content\Paks`にあります。

## 導入する

[Releases](https://github.com/223n/indigo-park-localization/releases)からzipをダウンロードし、展開して`install.bat`を実行します。
Steamからゲームの場所を自動で探します。

言語の一覧に日本語を足すとき、同梱の`retoc`が、ゲームのデータを読むためのライブラリ（`oo2core_9_win64.dll`）を取得して`tools`フォルダーに置きます。
取得先はGitHubの`WorkingRobot/OodleUE`で、このファイルは配布物に含んでいません。
取得にはネットワークへの接続が要ります。

Windowsの表示言語が日本語なら、ゲームを起動するだけで日本語になります。
英語のままのときは、ゲーム内で「OPTIONS」→「GAMEPLAY」→「LANGUAGE」から日本語を選びます。
一覧に日本語がないときは、Deutsch（ドイツ語）を選んでも日本語で表示されます。
ゲームにドイツ語の訳は入っていないため、その枠を使っています。

エンディングの歌詞の訳を字幕で出すため、MOD用の道具[UE4SS](https://github.com/UE4SS-RE/RE-UE4SS)を、ゲームの実行ファイルのフォルダー（`RaccoonCh1\Binaries\Win64`）に置きます。
歌詞の訳がまだない版では置きません。
すでにUE4SSを入れている場合は、UE4SSには触らず、字幕のMODだけを足します。
置きたくないときは`install.bat -NoLyrics`で実行します。

取り外すときは`uninstall.bat`を実行します。
ゲーム本体のファイルは触りません。
導入ツールが置いたUE4SSも消します。
ただし、ほかのUE4SSのMODがあるときは、UE4SSを残します。

手で入れる場合は、`mod`フォルダーの`IndigoParkJP_P.pak`を`RaccoonCh1\Content\Paks\~mods\`にコピーします。
この方法では言語の一覧に日本語が出ないため、Deutschを選びます。

## 何が入っているか

翻訳のデータと、それをゲームへ適用する仕組みが入っています。

| 位置                                                            | 中身                                                                                     |
|-----------------------------------------------------------------|------------------------------------------------------------------------------------------|
| `.textlintrc.js`、`.markdownlint-cli2.jsonc`、`.textlintignore` | 日本語の文書の検査設定です。規則は公開されている共有設定`@223n/lint-config-ja`にあります |
| `package.json`                                                  | 検査に使う道具の依存です。版もここで管理します                                           |
| `.github/`                                                      | ラベル、Dependabot、Issueのフォーム、Pull Requestのテンプレート、ワークフローです        |
| `scripts/setup.sh`、`scripts/setup.ps1`                         | リポジトリを作った直後の設定をまとめて行うスクリプトです。実行は済んでいます             |
| `CONTRIBUTING.md`                                               | 貢献の手引きです。ブランチの運用と文書の書き方があります                                 |
| `CLAUDE.md`                                                     | Claude Codeが読む決まりです。ブランチを消さないための注意があります                      |
| `SECURITY.md`                                                   | 脆弱性の報告先です                                                                       |
| `docs/RESEARCH.md`                                              | 日本語化の調べものの記録です。ゲームの構成と差し替えの経路があります                     |
| `docs/TRANSLATION.md`                                           | 翻訳の指針です。キャラクターの口調と固有名詞の対訳があります                             |
| `tools/`                                                        | 翻訳ファイル、MOD、配布物を作る道具と、それらを検査する道具です。Python 3で動きます      |
| `installer/`                                                    | 配布物に入れる導入と取り外しの道具です                                                   |
| `ue4ss/`                                                        | エンディングの歌詞の訳を字幕で出す、UE4SSのMODです                                       |
| `data/corpus.json`                                              | ゲームから集めた原文の一覧です                                                           |
| `data/ja.po`                                                    | 日本語の訳です。PO形式で管理します                                                       |
| `data/lyrics.ja.srt`                                            | エンディングの歌詞の訳です。字幕のSRT形式で管理します                                    |

## 分かっていること

実際のゲームで調べた結果は[docs/RESEARCH.md](docs/RESEARCH.md)にあります。
要点は次のとおりです。

| 項目               | 状況                                                                                                                 |
|--------------------|----------------------------------------------------------------------------------------------------------------------|
| エンジン           | Unreal Engine 5.2。IoStore形式です                                                                                   |
| 暗号化と署名       | どちらもありません                                                                                                   |
| MODの載せ方        | `Content/Paks/~mods/`に置いたpakが読み込まれます。実機で確認しました                                                 |
| フォント           | `.ufont`は生のTrueTypeです。pakの上書きで差し替えられます                                                            |
| 文章               | ウィジェット内のFTextです。`Content/Localization/Game/<文化>/Game.locres`で差し替えます                              |
| 言語の選択肢       | `DA_GameLanguage`を書き換えたIoStore形式のMODで日本語を足せます                                                      |
| 原文               | 1,230件を収集し、609件を翻訳の対象にしました。うち本編の台詞が212件です                                              |
| エンディングの歌詞 | 曲は動画（`Movies/CreditsSong.mp4`）で、字幕のデータを持ちません。UE4SSのMODで訳を重ねて出します。実機で確認しました |

メニューと設定画面が日本語で表示されるところまで、実機で確認しました。
日本語を出すにはフォントの差し替えも要ります。
手順は[tools/README.md](tools/README.md)にあります。

## 配布物を作る

```bash
python tools/make_release.py
```

`dist/IndigoParkJP_vX.Y.Z.zip`ができます。
版は`package.json`の`version`を使います。

zipの中身は次のとおりです。

| 位置                           | 中身                                               |
|--------------------------------|----------------------------------------------------|
| `install.bat`、`uninstall.bat` | 導入と取り外し                                     |
| `README.txt`                   | 利用者向けの手順                                   |
| `mod/IndigoParkJP_P.pak`       | 翻訳とフォント                                     |
| `ue4ss/`                       | エンディングの歌詞の字幕。UE4SSと、その上で動くMOD |
| `tools/`                       | 導入の中身と`retoc.exe`                            |
| `licenses/`                    | このMODと同梱物のライセンス                        |

Python 3が要ります。
`repak`、`retoc`、UE4SS、フォントは、手元に無ければ取得してSHA256で照合します。
取得にはネットワークへの接続が要ります。
組み立てに使う`repak`は、WindowsではWindows版を、ほかではx86_64のLinux版を取ります。
そのため、macOSなどでは組み立てられません。
`repak`がファイルの順を固定しないため、同じ入力でもzipは毎回変わります。

この組み立ては「リリースを公開する」ワークフローも行います。
ドラフトのReleaseに添付し、本文にSHA256を書き足します。
手元で作るのは、リリースの前にゲームで試したいときです。
手元のzipは添付と同じ物にはなりませんが、中身は`tools/verify_release.py`で同じように確かめられます。

## 翻訳する

翻訳はPO形式で管理します。
Poeditなどの翻訳ツールでそのまま開けます。
手順は[tools/README.md](tools/README.md)、訳し方は[docs/TRANSLATION.md](docs/TRANSLATION.md)にあります。

エンディングの歌詞の訳は、字幕のSRT形式で`data/lyrics.ja.srt`に書きます。
書き方は[docs/TRANSLATION.md](docs/TRANSLATION.md)の「エンディングの歌詞」にあります。

## これからやること

- 本編を通しでプレイしての字幕の確認
- エンディングの歌詞の訳（`data/lyrics.ja.srt`）

## 使ううえでの注意

作業を始める前に知っておくと、あとで困らないものです。

| 場面                   | 何が起きるか                                                                   | どうするか                                                                 |
|------------------------|--------------------------------------------------------------------------------|----------------------------------------------------------------------------|
| ブランチ名             | `release/`、`hotfix/`、`merge/`で始めると、リリースの仕組みが反応します        | 作業ブランチには`feature/`を使います                                       |
| Pull Requestのhead     | `main`や`develop`をheadにすると、「PRのheadブランチを確かめる」が失敗します    | リリースはワークフローに任せます。詳しくは[CLAUDE.md](CLAUDE.md)にあります |
| マージの方法           | squashやrebaseだと、リリースノートにPull Requestが載らず、次の版で衝突します   | マージコミット（Create a merge commit）でマージします                      |
| セルフホストのランナー | `RUNS_ON`のラベルに一致するランナーがないと、失敗せずに待機のまま止まります    | 設定したらCIを手で1回動かして確かめます                                    |
| 改行コード             | `.gitattributes`が全ファイルをLFに固定します                                   | CRLFのファイルを持ち込むと、最初のコミットで全行が差分になります           |
| `RELEASE_TOKEN`の期限  | 切れると、リリースのPull Requestが自動でマージされず、開いたところで止まります | 期限の前にPATを作り直し、`RELEASE_TOKEN`を上書きします                     |

リリースやCIが途中で止まったときは、ワークフローのログに日本語で対処方法が出ます。

## 日本語の文書を検査する

Markdownの書式を`markdownlint`で、日本語の書き方を`textlint`で検査します。
規則は公開されている共有設定[@223n/lint-config-ja](https://www.npmjs.com/package/@223n/lint-config-ja)にあり、このリポジトリには「何を検査するか」だけを書いてあります。
規則の理由は[node_japanese_lint_template](https://github.com/223n/node_japanese_lint_template)にあります。

```bash
npm install
npm run lint          # 書式と日本語をまとめて検査する
npm run lint:md:fix   # 書式の指摘を直す
npm run lint:ja:fix   # 日本語の指摘のうち、機械的に直せるものを直す
```

Node 22以上が要ります。

文体は「ですます調」です。
「である調」にしたい場合や、規則を一部だけ変えたい場合は、`.textlintrc.js`のコメントに書き方があります。

`main`と`develop`への`push`と、すべてのPull Requestで、CIが同じ検査をします。
CIではあわせて、原文の一覧と訳文の突き合わせを`tools/check_translation.py`で検査します。
ワークフローの構文は`actionlint`で、安全性は`zizmor`で検査します。
ワークフローの安全性は、`codeql.yml`もCodeQLの`actions`言語で走査します。
`GITHUB_TOKEN`で開いたPull Request（`RELEASE_TOKEN`が使えないときのリリースのPull Requestなど）では、CIは「承認待ち」で作られます。
書き込み権限のある人が「Approve workflows to run」を押すか、Pull Requestを閉じて開き直すと動きます。
承認せずに閉じたりマージしたりすると、承認待ちの実行は失敗として記録されますが、検査が落ちたわけではありません。

## ラベル

IssueとPull Requestのラベルはすべて日本語です。
`.github/labels.yml`が定義で、「ラベルを同期する」ワークフローがリポジトリのラベルをこの内容に揃えます。
ラベルを足したり変えたりするときは、GitHubの画面ではなくこのファイルを変えてください。
ファイルにないラベルは消えます。
ただし`main`からの同期では消しません。
`main`の`.github/labels.yml`が`develop`より古い期間に、`develop`で足したラベルを消さないためです。

| ラベル           | 用途                                              | 誰が付けるか                     |
|------------------|---------------------------------------------------|----------------------------------|
| バグ             | 期待どおりに動かない                              | Issueフォーム                    |
| 機能追加         | 新しい機能や改善の要望                            | Issueフォーム                    |
| ドキュメント     | 文書の追加や修正                                  | ラベラー、人                     |
| 翻訳             | 訳文の追加や修正                                  | Issueフォーム、ラベラー          |
| 質問             | 使い方や仕様についての質問                        | Issueフォーム                    |
| アクセシビリティ | 障害のある人の利用を妨げるもの                    | 人                               |
| 重複             | すでにあるIssueやPull Requestと同じ内容           | 人                               |
| 無効             | 内容が正しくない、または対象外                    | 人                               |
| 対応しない       | 対応しないと判断したもの                          | 人                               |
| 初心者向け       | はじめて貢献する人に向く課題                      | 人                               |
| 助けが必要       | 手を貸してほしい課題                              | 人                               |
| 依存関係         | 依存パッケージやアクションの更新                  | Dependabot、ラベラー             |
| npm              | npmパッケージの更新                               | Dependabot                       |
| GitHub Actions   | GitHub Actionsの更新                              | Dependabot、ラベラー             |
| リリース         | リリースの準備と公開                              | リリースのワークフロー、ラベラー |
| 自動公開         | このPull Requestをマージしたら、Releaseを公開する | リリースのワークフロー、人       |
| セキュリティ     | 脆弱性やセキュリティに関わる修正                  | 人、ラベラー                     |
| 破壊的変更       | 後方互換性を壊す変更                              | 人                               |

GitHubが最初から用意する英語のラベル（`bug`や`enhancement`など）は、付いているIssueを保ったまま日本語のラベルに改名されます。
Dependabotが作る既定のラベル（`dependencies`、`javascript`、`github_actions`）も同じように改名されます。
対応は`.github/labels.yml`の`from_name`にあります。

「初心者向け」と「助けが必要」は、GitHubの「Contribute」ページが英語名の`good first issue`と`help wanted`で判定するため、改名するとそこには載らなくなります。
その機能を使うなら、この2つは英語名のまま残してください。

Pull Requestには、変えたファイルとブランチ名から`.github/labeler.yml`の規則でラベルが自動で付きます。
このリポジトリの中から出したPull Requestでは、マージ先のブランチにある規則を使います。
フォークから出したPull Requestでは、既定ブランチ（`main`）にある規則を使います。

## Dependabot

`.github/dependabot.yml`で、npmの依存とGitHub Actionsのアクションを毎週月曜の朝に確かめます。
Pull Requestは`develop`に向けて開かれ、「依存関係」と「npm」または「GitHub Actions」のラベルが付きます。
npmではminorとpatchの更新が本番用と開発用の2つのPull Requestにまとまり、majorの更新は個別に開かれます。
GitHub Actionsのアクションは、majorも含めてすべて1つのPull Requestにまとまります。

ワークフローが使うアクションはコミットSHAで固定し、版はコメントに書いてあります。
DependabotはSHAとコメントの両方を更新します。

セキュリティ更新は常に既定ブランチ（`main`）に向けて開かれます。
既定ブランチ向けのエントリも書いてあるため、そこにも同じラベルと接頭辞が付きます。
このエントリは版の更新を開かない設定（`open-pull-requests-limit: 0`）です。
不要に見えても消さないでください。消すとセキュリティ更新からラベルと接頭辞が無くなります。

`develop`をやめて`main`だけで運用する場合は、`.github/dependabot.yml`の`target-branch`を消してください。
`develop`がないまま残っていると、版の更新が一切来なくなります。

## ブランチとリリース

GitFlowに沿って運用します。
ブランチの役割は[CONTRIBUTING.md](CONTRIBUTING.md)にあります。

```text
develop ──▶ release/vX.Y.Z ──(Pull Request)──▶ main ──▶ タグ vX.Y.Z とドラフトの Release ──▶ develop へ戻す ──▶ 配布物を確かめて公開
```

### リリースする

先に「リリース用のトークン」の設定を済ませておきます。

1. Actionsの「リリース」を開き、「Run workflow」を選びます。「Use workflow from」は`develop`にします
1. `version`にリリースする版を入れます。`v`は付けません（例: `1.2.0`、`1.2.0-rc.1`）
1. ワークフローが`develop`から`release/vX.Y.Z`ブランチを切り、`package.json`の版を上げ、`RELEASE_TOKEN`で`main`へのPull Requestを開きます
1. `auto_merge`が有効なら、チェックが済んで通るのを待って、ワークフローがマージコミットでマージします
1. 「リリースを公開する」ワークフローが動きます。タグ`vX.Y.Z`を打ち、**ドラフトの**GitHub Releaseを作って配布物を添付します
1. 同じワークフローが`main`を`develop`に戻し、リリースブランチを消します。戻しがPull Requestになったときは、チェックが通るのを待ってマージします
1. `auto_publish`が有効なら、配布物の中身を確かめてからReleaseを公開します。無効ならドラフトのまま残ります

`auto_merge`と`auto_publish`は、どちらも既定で有効です。
`auto_merge`を無効にすると、Pull Requestを開いたところで止まります。
その場合は中身を確かめてから、マージコミット（Create a merge commit）でマージしてください。
`auto_publish`を無効にすると、Releaseはドラフトで止まります。
その場合は「Releases」でドラフトを開き、添付と本文を確かめてから「Publish release」を押してください。

### リリース用のトークン

リリースのPull Requestの作成とマージには、持ち主のfine-grained personal access token（PAT）を使います。
`GITHUB_TOKEN`で開いたPull RequestはCIが承認待ちのまま動かず、`GITHUB_TOKEN`でマージしても「リリースを公開する」が動かないためです。

右上のアイコンから「Settings」→「Developer settings」→「Personal access tokens」→「Fine-grained tokens」→「Generate new token」で作ります。

| 項目              | 設定                                                                         |
|-------------------|------------------------------------------------------------------------------|
| Repository access | 「Only select repositories」で、このリポジトリだけを選びます                 |
| Contents          | Read and write。Pull Requestのマージに要ります                               |
| Pull requests     | Read and write。Pull Requestの作成に要ります                                 |
| Workflows         | Read and write。ワークフローのファイルを変えるPull Requestのマージに要ります |
| Expiration        | 任意です。期限の少し前に作り直します                                         |

作ったPATは、リポジトリの「Settings」→「Secrets and variables」→「Actions」→「Secrets」に、`RELEASE_TOKEN`という名前で登録します。

`RELEASE_TOKEN`がないときや、期限切れで使えないときは、警告を出して`GITHUB_TOKEN`でPull Requestを開くだけにします。
その場合の進め方は「RELEASE_TOKENが使えないとき」にあります。
期限を延ばすときは、Fine-grained tokensの画面でPATを作り直し、`RELEASE_TOKEN`を上書きします。

このPATは、ワークフローのファイルを書き換えられる強い権限を持ちます。
漏れると、保護していないブランチにワークフローを置いて、secretを読み出せます。
値はどこにも貼らず、要らなくなったらFine-grained tokensの画面で消してください。

ワークフローは、`RELEASE_TOKEN`をnpmの依存や外部の道具を動かすjobには渡しません。
`npm ci`と`npm run lint`は、秘密情報を持たない読み取りだけのjobで動かします。
依存のパッケージが乗っ取られても、PATを抜かれないようにするためです。
ただし、セルフホストのランナーを使い回すと、jobを分けても分離にはなりません。

### 版

版は`package.json`の`version`で管理します。
`develop`と`main`の版、最新のタグのどれよりも大きい版だけを受け付けます。
すでにあるタグや、残っている`release/*`ブランチ（Pull Requestを閉じただけのものも含む）があると止まります。
`-rc.1`のようなプレリリースの版は、GitHub Releaseでもプレリリースになります。

### Releaseの本文

GitHub Releaseの本文は、マージしたPull Requestのタイトルとラベルから自動で作られます。
分類は`.github/release.yml`にあります。

Releaseは**まずドラフトで作られます**。
ワークフローが配布物のzipを組み立てて添付し、本文の先頭にSHA256を書き足します。
`auto_publish`が有効なら、そのあと中身を確かめて公開します。
無効なら、「Releases」の画面で「Publish release」を押してください。

ドラフトのままでもタグは公開されます。
公開を取りやめるときは、ドラフトとタグの両方を消してください。

### 自動で公開する

`auto_publish`を有効にして実行すると、リリースのPull Requestに「自動公開」ラベルが付きます。
そのPull Requestがマージされると、ラベルを見て公開まで進みます。
公開を取りやめたくなったら、マージの前にラベルを外してください。

人が目で確かめる代わりに、`tools/verify_release.py`が添付そのものを落として中身を確かめます。

| 見るところ | 内容                                                                    |
|------------|-------------------------------------------------------------------------|
| 中身       | 要るファイルがそろっているか                                            |
| 版         | zipの中のフォルダー名と`README.txt`の版が、`package.json`と合っているか |
| 訳文       | pakの中に訳文が入っているか                                             |
| 抜け       | 訳文のはずの項目が、英語の原文のまま入っていないか                      |

最後の1つは、設定の説明文が英語のまま出た件（[Issue #16](https://github.com/223n/indigo-park-localization/issues/16)）と同じ形の崩れを捕まえます。
`.locres`を項目ごとに読み解いて`data/ja.po`と突き合わせるため、訳が古いままのpakも見つかります。

この経路はラベルの同期が済んでいることが前提です。
ラベルを付けられなかったときは警告が出て、Releaseはドラフトのまま残ります。

`auto_merge`と併せたときは、チェックが通ると数分でマージされます。
公開を止めたいときは、`auto_publish`を無効にして実行してください。

「自動公開」ラベルは、書き込みの権限がなくても、Triageの権限があれば付け外しできます。
マージする前に、意図したとおりのラベルが付いているかを見てください。

### 確かめが落ちたとき

Releaseはドラフトのまま残り、ワークフローが失敗します。
タグ、配布物の添付、`develop`への戻し、リリースブランチの削除は済んでいます。
確かめは後始末のあとに動かしているためです。

落ちた添付は消します。
残すと、作り直す段が「添付はすでにある」と見て飛ばし、直して再実行しても同じ物を見続けるためです。

直したあとは、次のどちらかを行います。

1. `main`を直さずに済むなら、失敗したワークフローを再実行します。配布物を組み立て直して確かめます
1. `main`を直す必要があるなら、版を上げて出し直します。同じ版のタグは打ち直せません

公開そのものを取りやめるときは、ドラフトとタグの両方を消してください。

### Pull Requestのマージまで任せる

`auto_merge`を有効にし、`RELEASE_TOKEN`も使えるときは、ワークフローがPull Requestをマージします。
マージの前に、次の条件がそろうのを待ちます。

- このリポジトリのブランチから出たPull Requestで、headはワークフローの押したコミットと一致する
- Pull Requestのチェックがすべて済み、失敗がない。Pull Requestのイベントで動いたチェックが1件以上ある
- `RELEASE_TOKEN`から見て、マージできる状態（`CLEAN`）になっている。Code scanningの規則もここで満たされる
- 待っているあいだに、Pull Requestのheadが変わっていない

フォークから同じ名前のブランチで出したPull Requestは、対象から外します。

待つ上限は30分です。
チェックが落ちたときや上限を過ぎたときは、Pull Requestを開いたまま止まります。
直してから人がマージすれば、「リリースを公開する」が続きを行います。

マージさせたくないときは、マージされる前にPull Requestを閉じてください。
閉じたあとは、`release/vX.Y.Z`ブランチも消します（Pull Requestの画面の「Delete branch」か、`git push origin --delete release/vX.Y.Z`）。
残すと、次の「リリース」が止まります。

待ち合わせとマージは`.github/scripts/merge-pr.sh`が行います。
マージできるかどうかは`RELEASE_TOKEN`で読みます。
ワークフローのファイルを変えるPull Requestは、`GITHUB_TOKEN`から見ると、規則を満たしていても`BLOCKED`と返ることがあるためです。

チェックが通っているのに`BLOCKED`のまま待つときは、`RELEASE_TOKEN`のWorkflowsとContentsの権限を確かめてください。
約5分続くと、ログに警告が出ます。
人がマージすれば、続きは進みます。

### developへの戻し

`develop`にはPull Requestを必須にする規則があるため、`main`から`develop`への戻しは毎回Pull Requestになります。
ブランチ名は`merge/vX.Y.Z-into-develop`です。

`RELEASE_TOKEN`が使えれば、「リリースを公開する」がこのPull Requestを`RELEASE_TOKEN`で開き、チェックが通るのを待ってマージします。
配布物の確かめが落ちても、戻しは進めます。
衝突したときは止まるので、Pull Requestの上で衝突を解いてから、マージコミットでマージしてください。

`RELEASE_TOKEN`がないか使えないときは、`GITHUB_TOKEN`でPull Requestを開き、人がマージコミットでマージします。
閉じて開き直す必要はありません。
headは`main`のコミットで、`main`へのpushで動いたCodeQLが解析済みのため、規則を満たせます。
CodeQLが終わるまでの1〜2分は、マージの欄が待ちになることがあります。

マージコミットでマージする理由は「使ううえでの注意」にあります。

### RELEASE_TOKENが使えないとき

`RELEASE_TOKEN`がないときや期限切れのときは、ワークフローが警告を出し、`GITHUB_TOKEN`でPull Requestを開くだけにします。
`auto_merge`を有効にしていても、自動ではマージしません。

`GITHUB_TOKEN`で開いたPull Requestでは、CIの実行は作られますが、承認待ちのままジョブが1つも動きません。
`GITHUB_TOKEN`が起こしたイベントでは、GitHubがワークフローをそのまま動かさないためです。
これは、ワークフローが自分自身を呼び続けるのを防ぐための仕様です。
`main`には「Code scanningの結果」を必須にする規則があるため、このままではマージできません。

Pull Requestの「Approve workflows to run」を押すか、一度閉じてすぐ開き直すと動きます。

```bash
gh pr close <番号>
gh pr reopen <番号>
```

人の操作として記録される`reopened`でワークフローが起動します。
ブランチとコミットは変わりません。
リリースのPull Requestを閉じたときは「リリースを公開する」も起動しますが、マージされていないため何もせずに終わります。

チェックが通ったら、マージコミット（Create a merge commit）でマージします。

### 履歴が繋がっていないとき

テンプレートから「Include all branches」にチェックを入れて作ったリポジトリでは、`main`と`develop`が共通の祖先を持ちません。
このリポジトリの2つは繋がっているため、普段は関係ありません。
リリースのワークフローやセットアップのスクリプトが、共通の祖先がないと言って止まったときに読んでください。

```text
  ! main と develop の履歴が繋がっていない（共通の祖先がない）
```

放っておくと、リリースのワークフローが`main`を取り込むところで止まります。
`main`から`develop`への戻しもできず、版が`develop`に届かなくなります。

直し方は2つあります。
どちらを選ぶかは、`develop`に残したい変更があるかどうかで決まります。

`develop`に残したい変更がない場合は、`develop`を消してからセットアップのスクリプトを実行し直します。
スクリプトが`main`から`develop`を作り直すため、履歴が繋がります。
Windowsでは`scripts/setup.sh`のところを`.\scripts\setup.ps1`に読み替えてください。

```bash
gh api --method DELETE "repos/OWNER/REPO/git/refs/heads/develop"
scripts/setup.sh
```

「ブランチの削除を禁止する」ルールセットがあると、この削除は拒まれます。
「Settings」→「Rules」でそのルールセットの「Enforcement」を「Disabled」にし、作り直したあとで「Active」に戻します。

`develop`にすでに作業がある場合は、`main`を`--allow-unrelated-histories`付きで取り込みます。
`develop`にはPull Requestを必須にする規則があるため、作業用のブランチで取り込んでからPull Requestを開きます。
共通の祖先ができるため、以後は普通に行き来できます。

```bash
git switch --create merge/unrelated-histories origin/develop
git merge --allow-unrelated-histories origin/main
git push --set-upstream origin merge/unrelated-histories
gh pr create --base develop --head merge/unrelated-histories --title "main を develop に取り込む"
```

こちらには副作用が2つあります。
共通の祖先がないため、`main`にしかないファイルは削除ではなく追加として扱われ、`develop`に現れます。
履歴にも、2つの根を繋ぐマージコミットが残ります。

どちらの方法でも、`develop`から切った作業ブランチと、`develop`に向けて開いているPull Requestの扱いは確かめてください。
`develop`を作り直した場合、それらは繋がらなくなります。

### 緊急の修正（hotfix）

リリース済みの内容を急いで直すときは、`main`から`hotfix/名前`ブランチを切ります。
そのブランチで修正し、`package.json`の版も上げます。

```bash
npm version patch --no-git-tag-version
```

`main`へのPull Requestをマージコミットでマージすると、「リリースを公開する」ワークフローが`release/*`と同じように動きます。

ただし公開は自動では行いません。
「自動公開」ラベルを付けるのはリリースのワークフローだけで、hotfixのPull Requestには付かないためです。
公開まで進めたいときは、マージの前にPull Requestへ「自動公開」ラベルを手で付けてください。
版を上げ忘れると、同じ版のタグがすでにあるため止まります。

## GitHub Actionsのランナー

ワークフローは既定でGitHubがホストする`ubuntu-latest`で動きます。
セルフホストのランナーがある場合は、リポジトリまたは組織の変数`RUNS_ON`に、ランナーのラベル（例: `self-hosted`）を設定します。
設定は「Settings」→「Secrets and variables」→「Actions」の「Variables」にあります。
`scripts/setup.sh --runs-on ラベル`でも行えます。
Windowsでは`.\scripts\setup.ps1 -RunsOn ラベル`です。
変数がないときは`ubuntu-latest`に倒れるため、設定しなくても動きます。

セルフホストのランナーには、`git`と`gh`（GitHub CLI）、Dockerが要ります。
Dockerはzizmorの検査（コンテナーで動きます）に使います。
NodeとPythonはワークフローが用意します。
「リリースを公開する」は配布物の組み立てにx86_64のLinux版の`repak`を取るため、x86_64のLinuxのランナーで動かしてください。
公開リポジトリでセルフホストのランナーを使うと、フォークからのPull Requestで任意のコードが動くため、非公開のリポジトリで使ってください。

## ワークフローの一覧

| ファイル              | いつ動くか                                                                         | 何をするか                                                                                                                                                                                                                |
|-----------------------|------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `ci.yml`              | `main`と`develop`への`push`、Pull Request、手動                                    | 日本語の文書、原文と訳文の突き合わせ（`check_translation.py`）、ワークフローの構文（actionlint）、ワークフローの安全性（zizmor）を検査します                                                                              |
| `codeql.yml`          | `main`と`develop`への`push`、Pull Request、毎週月曜、手動                          | ワークフローの安全性をCodeQLで走査します。結果は「Security」→「Code scanning」に出ます                                                                                                                                    |
| `labels.yml`          | `.github/labels.yml`か`.github/workflows/labels.yml`の変更、手動                   | リポジトリのラベルを定義に揃えます。Pull Requestでは差分の表示だけです                                                                                                                                                    |
| `labeler.yml`         | このリポジトリの中から出したPull Requestを開いたとき、更新したとき、開き直したとき | 変えたファイルとブランチ名からラベルを付けます。規則はマージ先のブランチから読みます                                                                                                                                      |
| `labeler-fork.yml`    | フォークから出したPull Requestを開いたとき、更新したとき、開き直したとき           | `labeler.yml`と同じ規則でラベルを付けます。規則は既定ブランチ（`main`）から読みます                                                                                                                                       |
| `branch-guard.yml`    | Pull Requestを開いたとき、更新したとき、開き直したとき                             | headブランチが`main`か`develop`なら失敗します。マージは止めません                                                                                                                                                         |
| `release.yml`         | 手動                                                                               | `develop`からリリースブランチを切り、版を上げ、`RELEASE_TOKEN`で`main`へのPull Requestを開きます。`auto_merge`が有効なら、チェックが通るのを待ってマージします                                                            |
| `release-publish.yml` | `release/*`か`hotfix/*`のPull Requestが`main`にマージされたとき                    | タグを打ち、ドラフトのGitHub Releaseを作って配布物を添付し、`main`を`develop`に戻します。戻しがPull Requestになったときは、チェックが通るのを待ってマージします。「自動公開」が指示されていれば、中身を確かめて公開します |

## 権利について

このリポジトリは非公式です。
ゲームの開発元や販売元とは関わりがなく、承認も受けていません。

ゲームに含まれる文、画像、音声などの権利は権利者にあります。
ゲームから取り出したファイルそのものは、このリポジトリと配布物のどちらにも置きません。

ただし、ゲームの英語の文は含みます。
このリポジトリには、翻訳の原文としてゲームから集めた英語の文があります。
`data/corpus.json`の`source`と、`data/ja.po`の`msgid`です。
配布物のpakに入れる`.locres`は、訳さない項目も書き出します。
そのため、訳さない項目は英語の原文のまま入ります。

`data/lyrics.ja.srt`には、エンディングの曲の歌詞の訳を書きます。
曲と歌詞の権利も権利者にあります。

権利者から求めがあった場合は、公開を取り下げます。

## ライセンス

**Apache License 2.0**です。
[LICENSE](LICENSE)を見てください。

このライセンスが対象とするのは、このリポジトリで作ったものだけです。  
**ゲーム本体のファイルは含みません。**
ゲームから集めた英語の原文も対象外です。

`tools/cityhash.py`は、GoogleのCityHash v1.1をPythonに移したものです。
この部分は、元のライセンスであるMIT Licenseに従います。
元の著作権表示（Copyright (c) 2011 Google, Inc.）と許諾の文は、ファイルの先頭に残しています。
