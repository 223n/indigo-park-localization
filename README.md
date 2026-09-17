# Indigo Park 日本語化

Steam版のゲーム「Indigo Park」を日本語で遊ぶための、非公式の日本語化MODです。
翻訳した文と、それをゲームへ適用する仕組みをこのリポジトリで管理します。

開発元や販売元とは関わりがありません。
ゲーム本体のファイルも含みません。

## 対象

| 項目 | 内容 |
| ---- | ---- |
| ゲーム | Indigo Park（Chapter 1） |
| 入手先 | Steam |
| 動く環境 | Windows |
| 翻訳する向き | 英語から日本語へ |

Steamの既定の導入先は`C:\Program Files (x86)\Steam\steamapps\common\Indigo Park`です。
実行ファイルは`RaccoonCh1.exe`で、ゲームのデータは`RaccoonCh1\Content\Paks`にあります。

## 導入する

[Releases](https://github.com/223n/indigo-park-localization/releases)からzipをダウンロードし、展開して`install.bat`を実行します。
Steamからゲームの場所を自動で探します。

Windowsの表示言語が日本語なら、ゲームを起動するだけで日本語になります。
英語のままのときは、ゲーム内で「OPTIONS」→「GAMEPLAY」→「LANGUAGE」から日本語を選びます。

取り外すときは`uninstall.bat`を実行します。
ゲーム本体のファイルは触りません。

手で入れる場合は、`mod`フォルダの`IndigoParkJP_P.pak`を`RaccoonCh1\Content\Paks\~mods\`にコピーします。

## 何が入っているか

いまはリポジトリの土台だけがあります。
翻訳のデータと適用の仕組みは、これから足します。

| 位置 | 中身 |
| ---- | ---- |
| `.textlintrc.js`、`.markdownlint-cli2.jsonc`、`.textlintignore` | 日本語の文書の検査設定です。規則は公開されている共有設定`@223n/lint-config-ja`にあります |
| `package.json` | 検査に使う道具の依存です。版もここで管理します |
| `.github/` | ラベル、Dependabot、Issueのフォーム、Pull Requestのテンプレート、ワークフローです |
| `scripts/setup.sh`、`scripts/setup.ps1` | リポジトリを作った直後の設定をまとめて行うスクリプトです。実行は済んでいます |
| `CONTRIBUTING.md` | 貢献の手引きです。ブランチの運用と文書の書き方があります |
| `CLAUDE.md` | Claude Codeが読む決まりです。ブランチを消さないための注意があります |
| `SECURITY.md` | 脆弱性の報告先です |
| `docs/RESEARCH.md` | 日本語化の調べものの記録です。ゲームの構成と差し替えの経路があります |
| `docs/TRANSLATION.md` | 翻訳の指針です。キャラクターの口調と固有名詞の対訳があります |
| `tools/` | 翻訳ファイルとMODを作る道具です。Python 3で動きます |
| `installer/` | 配布物に入れる導入と取り外しの道具です |
| `data/corpus.json` | ゲームから集めた原文の一覧です |
| `data/ja.po` | 日本語の訳です。PO形式で管理します |

## 分かっていること

実際のゲームで調べた結果は[docs/RESEARCH.md](docs/RESEARCH.md)にあります。
要点は次のとおりです。

| 項目 | 状況 |
| ---- | ---- |
| エンジン | Unreal Engine 5.2。IoStore形式です |
| 暗号化と署名 | どちらもありません |
| MODの載せ方 | `Content/Paks/~mods/`に置いたpakが読み込まれます。実機で確認しました |
| フォント | `.ufont`は生のTrueTypeです。pakの上書きで差し替えられます |
| 文章 | ウィジェット内のFTextです。`Content/Localization/Game/<文化>/Game.locres`で差し替えます |
| 言語の選択肢 | `DA_GameLanguage`を書き換えたIoStore形式のMODで日本語を足せます |
| 原文 | 881件を収集済みです。うち本編の台詞が212件です |

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

| 位置 | 中身 |
| ---- | ---- |
| `install.bat`、`uninstall.bat` | 導入と取り外し |
| `README.txt` | 利用者向けの手順 |
| `mod/IndigoParkJP_P.pak` | 翻訳とフォント |
| `tools/` | 導入の中身と`retoc.exe` |
| `licenses/` | このMODと同梱物のライセンス |

`repak`と`retoc`は取得してSHA256で照合します。
`repak`がファイルの順を固定しないため、同じ入力でもzipは毎回変わります。
公開するときは、出力されたSHA256をReleaseに載せてください。

## これから決めること

- 本編を通しでプレイしての字幕の確認

翻訳はPO形式で管理します。
Poeditなどの翻訳ツールでそのまま開けます。
手順は[tools/README.md](tools/README.md)、訳し方は[docs/TRANSLATION.md](docs/TRANSLATION.md)にあります。

## 使ううえでの注意

作業を始める前に知っておくと、あとで困らないものです。

| 場面 | 何が起きるか | どうするか |
| ---- | ---- | ---- |
| ブランチ名 | `release/`、`hotfix/`、`merge/`で始めると、リリースの仕組みが反応します | 作業ブランチには`feature/`を使います |
| Pull Requestのhead | `main`や`develop`をheadにすると、「PRのheadブランチを確かめる」が失敗します | リリースはワークフローに任せます。詳しくは[CLAUDE.md](CLAUDE.md)にあります |
| マージの方法 | squashやrebaseだと、リリースノートにPull Requestが載らず、次の版で衝突します | マージコミット（Create a merge commit）でマージします |
| セルフホストのランナー | `RUNS_ON`のラベルに一致するランナーがないと、失敗せずに待機のまま止まります | 設定したらCIを手で1回動かして確かめます |
| 改行コード | `.gitattributes`が全ファイルをLFに固定します | CRLFのファイルを持ち込むと、最初のコミットで全行が差分になります |

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
CIではあわせて、ワークフローの構文を`actionlint`で、安全性を`zizmor`で検査します。
ワークフローの安全性は、`codeql.yml`もCodeQLの`actions`言語で走査します。
ワークフローが開いたPull Request（リリースのPull Requestなど）では、CIは「承認待ち」で作られます。
書き込み権限のある人が「Approve workflows to run」を押すと動きます。
承認せずにマージすると、承認待ちの実行は失敗として記録されますが、検査が落ちたわけではありません。

## ラベル

IssueとPull Requestのラベルはすべて日本語です。
`.github/labels.yml`が定義で、「ラベルを同期する」ワークフローがリポジトリのラベルをこの内容に揃えます。
ラベルを足したり変えたりするときは、GitHubの画面ではなくこのファイルを変えてください。
ファイルにないラベルは消えます。
ただし`main`からの同期では消しません。
`main`の`.github/labels.yml`が`develop`より古い期間に、`develop`で足したラベルを消さないためです。

| ラベル | 用途 | 誰が付けるか |
| ---- | ---- | ---- |
| バグ | 期待どおりに動かない | Issueフォーム |
| 機能追加 | 新しい機能や改善の要望 | Issueフォーム |
| ドキュメント | 文書の追加や修正 | ラベラー、人 |
| 質問 | 使い方や仕様についての質問 | Issueフォーム |
| アクセシビリティ | 障害のある人の利用を妨げるもの | 人 |
| 重複 | すでにあるIssueやPull Requestと同じ内容 | 人 |
| 無効 | 内容が正しくない、または対象外 | 人 |
| 対応しない | 対応しないと判断したもの | 人 |
| 初心者向け | はじめて貢献する人に向く課題 | 人 |
| 助けが必要 | 手を貸してほしい課題 | 人 |
| 依存関係 | 依存パッケージやアクションの更新 | Dependabot、ラベラー |
| npm | npmパッケージの更新 | Dependabot |
| GitHub Actions | GitHub Actionsの更新 | Dependabot、ラベラー |
| リリース | リリースの準備と公開 | リリースのワークフロー |
| セキュリティ | 脆弱性やセキュリティに関わる修正 | 人、ラベラー |
| 破壊的変更 | 後方互換性を壊す変更 | 人 |

GitHubが最初から用意する英語のラベル（`bug`や`enhancement`など）は、付いているIssueを保ったまま日本語のラベルに改名されます。
Dependabotが作る既定のラベル（`dependencies`、`javascript`、`github_actions`）も同じように改名されます。
対応は`.github/labels.yml`の`from_name`にあります。

「初心者向け」と「助けが必要」は、GitHubの「Contribute」ページが英語名の`good first issue`と`help wanted`で判定するため、改名するとそこには載らなくなります。
その機能を使うなら、この2つは英語名のまま残してください。

Pull Requestには、変えたファイルとブランチ名から`.github/labeler.yml`の規則でラベルが自動で付きます。

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
develop ──▶ release/vX.Y.Z ──(Pull Request)──▶ main ──▶ タグ vX.Y.Z と GitHub Release ──▶ develop へ戻す
```

### リリースする

1. Actionsの「リリース」を開き、「Run workflow」を選びます
1. `version`にリリースする版を入れます。`v`は付けません（例: `1.2.0`、`1.2.0-rc.1`）
1. ワークフローが`develop`から`release/vX.Y.Z`ブランチを切り、`package.json`の版を上げ、`main`へのPull Requestを開きます
1. Pull Requestの内容を確かめ、マージコミット（Create a merge commit）でマージします
1. 「リリースを公開する」ワークフローが動き、タグ`vX.Y.Z`を打ち、GitHub Releaseを作り、`main`を`develop`に戻します

版は`package.json`の`version`で管理します。
`develop`と`main`の版、最新のタグのどれよりも大きい版だけを受け付けます。
すでにあるタグや、開いたままの`release/*`ブランチがあると止まります。
`-rc.1`のようなプレリリースの版は、GitHub Releaseでもプレリリースになります。

`auto_merge`を有効にして実行すると、Pull Requestを人手で確かめずにマージし、公開まで一気に進めます。
ただし`main`に必須のチェックや承認のルールがあると、マージで止まります。
ワークフローが開いたPull RequestのCIは承認待ちのままで、ルールを満たせないためです。
その場合は人がPull Requestをマージすれば、公開のワークフローが続きを行います。

`develop`にPull Requestを必須にする規則がある場合、`main`から`develop`への戻しは毎回Pull Requestになります。
ブランチ名は`merge/vX.Y.Z-into-develop`です。
リリースのあとに、このPull Requestもマージコミットでマージしてください。

マージコミットでマージする理由は「使ううえでの注意」にあります。

GitHub Releaseの本文は、マージしたPull Requestのタイトルとラベルから自動で作られます。
分類は`.github/release.yml`にあります。

### 緊急の修正（hotfix）

リリース済みの内容を急いで直すときは、`main`から`hotfix/名前`ブランチを切ります。
そのブランチで修正し、`package.json`の版も上げます。

```bash
npm version patch --no-git-tag-version
```

`main`へのPull Requestをマージコミットでマージすると、「リリースを公開する」ワークフローが`release/*`と同じように動きます。
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
Nodeはワークフローが用意します。
公開リポジトリでセルフホストのランナーを使うと、フォークからのPull Requestで任意のコードが動くため、非公開のリポジトリで使ってください。

## ワークフローの一覧

| ファイル | いつ動くか | 何をするか |
| ---- | ---- | ---- |
| `ci.yml` | `main`と`develop`への`push`、Pull Request、手動 | 日本語の文書、ワークフローの構文（actionlint）、ワークフローの安全性（zizmor）を検査します |
| `codeql.yml` | `main`と`develop`への`push`、Pull Request、毎週月曜、手動 | ワークフローの安全性をCodeQLで走査します。結果は「Security」→「Code scanning」に出ます |
| `labels.yml` | `.github/labels.yml`か`.github/workflows/labels.yml`の変更、手動 | リポジトリのラベルを定義に揃えます。Pull Requestでは差分の表示だけです |
| `labeler.yml` | Pull Requestを開いたとき、更新したとき | 変えたファイルとブランチ名からラベルを付けます |
| `branch-guard.yml` | Pull Requestを開いたとき、更新したとき | headブランチが`main`か`develop`なら失敗します。マージは止めません |
| `release.yml` | 手動 | `develop`からリリースブランチを切り、版を上げ、`main`へのPull Requestを開きます |
| `release-publish.yml` | `release/*`か`hotfix/*`のPull Requestが`main`にマージされたとき | タグを打ち、GitHub Releaseを作り、`main`を`develop`に戻します |

## 権利について

このリポジトリは非公式です。
ゲームの開発元や販売元とは関わりがなく、承認も受けていません。

ゲームに含まれる文、画像、音声などの権利は権利者にあります。
ゲームから取り出したファイルそのものは、このリポジトリに置きません。
配布するのは、訳した文と、それを適用するための仕組みだけです。

権利者から求めがあった場合は、公開を取り下げます。

## ライセンス

Apache License 2.0です。
[LICENSE](LICENSE)を見てください。

このライセンスが対象とするのは、このリポジトリで作ったものだけです。
ゲーム本体のファイルは含みません。
