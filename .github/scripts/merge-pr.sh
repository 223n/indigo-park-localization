#!/usr/bin/env bash
# PR のチェックが済んで通り、マージできる状態になるのを待ってから、マージコミットでマージする。
# release.yml（リリースの PR）と release-publish.yml（main を develop へ戻す PR）が使う。
#
# 環境変数
#   PR_NUMBER           マージする PR の番号
#   EXPECT_BASE         base ブランチ（main か develop）
#   EXPECT_HEAD_PREFIX  head ブランチの接頭辞（release/ や merge/）
#   EXPECT_SHA          head であるはずのコミット。ワークフローが push したもの
#   MERGE_TOKEN         状態を読み、マージするトークン（secret の RELEASE_TOKEN）
#   GH_TOKEN            チェックの結果を読むトークン（GITHUB_TOKEN）
#   GITHUB_REPOSITORY   対象のリポジトリ（Actions が入れる）
#   WAIT_MINUTES        待つ上限（分）。既定は 30
#   MERGE_BODY          マージコミットの本文
#   DRY_RUN             1 なら、マージできる状態になったところで止める（手元で試すとき）
#
# 読み方の決まり
# - フォークから出た PR と、head が EXPECT_SHA でない PR はマージしない。
#   フォークから同じ名前のブランチで出した PR を、ワークフローの PR と取り違えないため。
# - チェックの結果は GITHUB_TOKEN で読む。PAT の用途を、PR の作成と状態の確認とマージに絞るため。
# - mergeStateStatus は PAT で読む。ワークフローのファイルを変える PR は、workflows 権限の無い
#   GITHUB_TOKEN から見ると、規則を満たしていても BLOCKED と返ることがあるため。
# - CLEAN だけを合格にする。UNSTABLE は、必須でないチェックの失敗か実行中を含む。
# - pull_request のイベントで動いたチェックが1件以上あることも条件にする。
#   develop へ戻す PR の head は main のコミットで、push のチェックを最初から持つため、
#   それだけでは PR 側のチェックが登録される前に合格に見えてしまう。
# - 合格を2回続けて見てからマージする。チェックが後から増える隙間を避けるため。
# - 待つあいだに head が変わったら止める。確かめていないコミットをマージしないため。
# - マージコミットの本文は MERGE_BODY にする。PR の本文をそのまま使うと、
#   本文に [skip ci] などが混じったとき、マージ先への push でワークフローが動かなくなる。
set -uo pipefail

: "${PR_NUMBER:?PR_NUMBER がない}"
: "${EXPECT_BASE:?EXPECT_BASE がない}"
: "${EXPECT_HEAD_PREFIX:?EXPECT_HEAD_PREFIX がない}"
: "${EXPECT_SHA:?EXPECT_SHA がない}"
: "${MERGE_TOKEN:?MERGE_TOKEN がない}"
: "${GITHUB_REPOSITORY:?GITHUB_REPOSITORY がない}"
: "${MERGE_BODY:=ワークフローが、チェックの完了を待ってマージした。}"
wait_minutes="${WAIT_MINUTES:-30}"
interval=15
deadline=$((SECONDS + wait_minutes * 60))
repo="${GITHUB_REPOSITORY}"
err_file="$(mktemp)"
trap 'rm -f "${err_file}"' EXIT

# gh pr checks --json は gh 2.50.0 から。古い gh では毎回失敗して空待ちになるため、先に確かめる
if ! gh pr checks --help 2>/dev/null | grep -q -- '--json'; then
  echo "::error::gh pr checks が --json に対応していない。gh 2.50.0 以上を入れる"
  exit 1
fi

# PAT で PR の状態を読む。
# 出力は「state mergeStateStatus base head headRefOid isCrossRepository」をタブで区切ったもの
read_pr() {
  GH_TOKEN="${MERGE_TOKEN}" gh pr view "${PR_NUMBER}" --repo "${repo}" \
    --json state,mergeStateStatus,baseRefName,headRefName,headRefOid,isCrossRepository \
    --jq '[.state, .mergeStateStatus, .baseRefName, .headRefName, .headRefOid, .isCrossRepository] | @tsv'
}

if ! info="$(read_pr)"; then
  echo "::error::PR #${PR_NUMBER} を読めなかった。RELEASE_TOKEN の期限と権限を確かめる"
  exit 1
fi
IFS=$'\t' read -r pr_state _ base head sha cross <<<"${info}"

# 再実行で古い番号を受け取ったときや、取り違えたときに、別の PR をマージしないよう確かめる
if [ "${pr_state}" = 'MERGED' ]; then
  echo "::notice::PR #${PR_NUMBER} はすでにマージされている"
  exit 0
fi
if [ "${pr_state}" != 'OPEN' ]; then
  echo "::error::PR #${PR_NUMBER} は開いていない（${pr_state}）"
  exit 1
fi
if [ "${cross}" != 'false' ]; then
  echo "::error::PR #${PR_NUMBER} はフォークから出ている。自動ではマージしない"
  exit 1
fi
if [ "${base}" != "${EXPECT_BASE}" ] || [ "${head#"${EXPECT_HEAD_PREFIX}"}" = "${head}" ]; then
  echo "::error::PR #${PR_NUMBER} は ${head} → ${base} で、想定（${EXPECT_HEAD_PREFIX}* → ${EXPECT_BASE}）と違う"
  exit 1
fi
if [ "${sha}" != "${EXPECT_SHA}" ]; then
  echo "::error::PR #${PR_NUMBER} の head（${sha:0:7}）が、ワークフローが push したコミット（${EXPECT_SHA:0:7}）と違う。確かめていないコミットはマージしない"
  exit 1
fi
echo "PR #${PR_NUMBER}（${head} → ${base}、${sha:0:7}）のチェックを待つ。上限は ${wait_minutes} 分"

passes=0
check_errors=0
blocked_green=0
hinted=0
status='UNKNOWN'
total=0
pending=0
permission_hint="チェックはすべて通っているのに、RELEASE_TOKEN から見た状態が BLOCKED のままである。ワークフローのファイルを変える PR では、PAT の「Workflows」と「Contents」が Read and write でないとこうなる。PAT の権限を確かめる。PR の画面から人がマージすれば、続きは進む"
while :; do
  if [ "${SECONDS}" -ge "${deadline}" ]; then
    echo "::error::${wait_minutes} 分待っても PR #${PR_NUMBER} をマージできる状態にならなかった（最後の状態: ${status}、チェック ${total} 件のうち実行中 ${pending} 件）。PR の画面でチェックと規則を確かめ、手でマージする"
    if [ "${blocked_green}" -gt 0 ]; then
      echo "::error::${permission_hint}"
    fi
    exit 1
  fi

  # チェックの集計。出力は「件数 実行中の件数 pull_request のチェックの件数 通らなかったチェックの名前」をタブで区切ったもの。
  # 空になりうる名前の欄は最後に置く。タブは連続すると1つにまとめられ、途中の空の欄は詰まってしまうため。
  # --json を付けると、失敗や実行中があっても gh の終了コードは 0 になるため、bucket で判定する
  failed=''
  pending=1
  pr_total=0
  total=0
  checks_read=false
  if summary="$(gh pr checks "${PR_NUMBER}" --repo "${repo}" --json name,bucket,event --jq '[
      length,
      ([.[] | select(.bucket == "pending")] | length),
      ([.[] | select(.event == "pull_request")] | length),
      ([.[] | select(.bucket == "fail" or .bucket == "cancel") | .name] | join("、"))
    ] | @tsv' 2>"${err_file}")"; then
    IFS=$'\t' read -r total pending pr_total failed <<<"${summary}"
    checks_read=true
    check_errors=0
  elif grep -q 'no checks reported' "${err_file}"; then
    # まだチェックが登録されていない。待つ
    check_errors=0
  else
    check_errors=$((check_errors + 1))
    echo "::warning::チェックの結果を読めなかった（${check_errors} 回目）: $(tr '\n' ' ' <"${err_file}")"
    if [ "${check_errors}" -ge 8 ]; then
      echo "::error::チェックの結果を続けて読めなかった。上の警告を見る"
      exit 1
    fi
  fi
  if [ -n "${failed}" ]; then
    echo "::error::PR #${PR_NUMBER} のチェックが通らなかった: ${failed}"
    exit 1
  fi

  status='UNKNOWN'
  if info="$(read_pr)"; then
    IFS=$'\t' read -r pr_state status _ _ now_sha _ <<<"${info}"
    if [ "${pr_state}" = 'MERGED' ]; then
      echo "::notice::待っているあいだに PR #${PR_NUMBER} がマージされた"
      exit 0
    fi
    if [ "${pr_state}" != 'OPEN' ]; then
      echo "::error::待っているあいだに PR #${PR_NUMBER} が閉じられた。マージはしない。リリースの PR なら、${head} ブランチも消してから次のリリースを動かす"
      exit 1
    fi
    if [ "${now_sha}" != "${sha}" ]; then
      echo "::error::待っているあいだに PR #${PR_NUMBER} の head が ${sha:0:7} から ${now_sha:0:7} に変わった。確かめていないコミットはマージしない"
      exit 1
    fi
  fi

  case "${status}" in
    DIRTY)
      echo "::error::PR #${PR_NUMBER} は衝突している。PR の上で衝突を解いてから、手でマージする"
      exit 1
      ;;
    BEHIND)
      echo "::error::PR #${PR_NUMBER} は base より遅れている。手で更新してからマージする"
      exit 1
      ;;
  esac

  green=false
  if [ "${checks_read}" = 'true' ] && [ "${total}" -gt 0 ] && [ "${pr_total}" -gt 0 ] && [ "${pending}" -eq 0 ]; then
    green=true
  fi

  # チェックが通っているのに BLOCKED が続くときは、PAT の権限が足りない疑いがある。
  # 解析の結果が遅れて届くこともあるので、すぐには止めず、約5分続いたら一度だけ知らせる
  if [ "${green}" = 'true' ] && [ "${status}" = 'BLOCKED' ]; then
    blocked_green=$((blocked_green + 1))
    if [ "${blocked_green}" -ge 20 ] && [ "${hinted}" -eq 0 ]; then
      echo "::warning::${permission_hint}"
      hinted=1
    fi
  else
    blocked_green=0
  fi

  if [ "${green}" = 'true' ] && [ "${status}" = 'CLEAN' ]; then
    passes=$((passes + 1))
    if [ "${passes}" -ge 2 ]; then
      break
    fi
  else
    passes=0
  fi
  echo "待っている: 状態 ${status}、チェック ${total} 件のうち実行中 ${pending} 件（pull_request のもの ${pr_total} 件）"
  sleep "${interval}"
done

echo "マージできる状態になった。${sha:0:7} をマージする"
if [ "${DRY_RUN:-}" = '1' ]; then
  echo "DRY_RUN のため、マージせずに終える"
  exit 0
fi
attempt=0
while :; do
  attempt=$((attempt + 1))
  if out="$(GH_TOKEN="${MERGE_TOKEN}" gh pr merge "${PR_NUMBER}" --repo "${repo}" \
    --merge --match-head-commit "${sha}" --body "${MERGE_BODY}" 2>&1)"; then
    printf '%s\n' "${out}"
    echo "PR #${PR_NUMBER} をマージした"
    exit 0
  fi
  printf '%s\n' "${out}" >&2
  case "${out}" in
    *'refusing to allow'*)
      echo "::error::RELEASE_TOKEN にワークフローのファイルを書き換える権限が無い。PAT の「Workflows」を Read and write にする"
      exit 1
      ;;
  esac
  if [ "${attempt}" -ge 3 ]; then
    echo "::error::PR #${PR_NUMBER} をマージできなかった。PR の画面で規則を確かめ、手でマージする"
    exit 1
  fi
  sleep 20
done
