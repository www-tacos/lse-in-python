import sys

from pyls_jsonrpc.dispatchers import MethodDispatcher
from pyls_jsonrpc.endpoint import Endpoint
from pyls_jsonrpc.streams import JsonRpcStreamReader, JsonRpcStreamWriter

# 修正機能を試すための小文字判定の正規表現
import re
IS_LOWER = re.compile(r'[a-z]+')

# デスクトップにログ出力
import logging, os
logging.basicConfig(
  handlers = [
    logging.FileHandler(
      filename = f"{os.path.expanduser('~/Desktop')}/lse-in-python.log",
      encoding='utf-8',
      mode='a+'
    )
  ],
  level = logging.DEBUG,
  format = "%(relativeCreated)08d[ms] - %(name)s - %(levelname)s - %(processName)-10s - %(threadName)s -\n*** %(message)s"
)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
log = logging.getLogger("pyls_jsonrpc")
log.addHandler(console)

class SampleLanguageServer(MethodDispatcher):
  def __init__(self):
    self.jsonrpc_stream_reader = JsonRpcStreamReader(sys.stdin.buffer)
    self.jsonrpc_stream_writer = JsonRpcStreamWriter(sys.stdout.buffer)
    self.endpoint = Endpoint(self, self.jsonrpc_stream_writer.write)
    # メソッドによってはリクエストデータにテキスト本体が乗ってこない場合があるのでサーバ側でドキュメントを管理する必要がある
    self.lastDocument = ''

  def start(self):
    self.jsonrpc_stream_reader.listen(self.endpoint.consume)

  # 言語サーバが対応している機能をエディタに伝える処理
  def m_initialize(self, rootUri=None, **kwargs):
    return {"capabilities": {
      'codeActionProvider': True,
      'completionProvider': {
        'resolveProvider': False,  # We know everything ahead of time
        'triggerCharacters': ['.', '#']
      },
      'documentFormattingProvider': True,
      'textDocumentSync': {
        'change': 1,  # 変更後のファイル内容をすべて含める
        'save': {
          'includeText': True,
        },
        'openClose': True,
      },
      'workspace': {
        'workspaceFolders': {
          'supported': True,
          'changeNotifications': True
        }
      }
    }}

  # ファイルを開いたときの処理
  # 無条件に先頭の5行5文字目までをWARNING対象にする
  def m_text_document__did_open(self, textDocument=None, **_kwargs):
    self.lastDocument = textDocument['text']
    method = "textDocument/publishDiagnostics"
    params = {
      'uri': textDocument['uri'],
      'diagnostics': [{
        'source': 'lse-in-python',
        'range': {
          'start': {'line': 0, 'character': 0},
          'end': {'line': 5, 'character': 5}
        },
        'message': '5行目5文字目までのエラー対象',
        'severity': 2,
        'code': 'didOpen時の処理'
      }]
    }
    self.endpoint.notify(method, params=params)

  # ファイルを変更したときの処理
  # 小文字アルファベットをINFORMATION対象にする
  def m_text_document__did_change(self, contentChanges=None, textDocument=None, **_kwargs):
    doc = contentChanges[0]['text']
    self.lastDocument = doc
    lines = doc.split("\n")
    diagnostics = []
    for row,line in enumerate(lines):
      matches = IS_LOWER.finditer(line)
      for m in matches:
        diagnostics.append({
          'source': 'lse-in-python',
          'range': {
            'start': {'line': row, 'character': m.start()},
            'end': {'line': row, 'character': m.end()}
          },
          'message': '小文字のアルファベット',
          'severity': 3,  # 1~4
          'code': 'didChange時の処理',
          'data': m.group().upper()
        })
    method = "textDocument/publishDiagnostics"
    params = {'uri':textDocument['uri'], 'diagnostics': diagnostics}
    self.endpoint.notify(method, params=params)

  # ファイルを保存したときの処理
  # 0件の通知を送ることでWARNING等の表示を消す
  def m_text_document__did_save(self, textDocument=None, **_kwargs):
    method = "textDocument/publishDiagnostics"
    params = {'uri':textDocument['uri'], 'diagnostics': []}
    self.endpoint.notify(method, params=params)

  # ファイルを閉じたときの処理
  def m_text_document__did_close(self, textDocument=None, **_kwargs):
    pass

  # マウスやカーソルがコード上の文字列に接触したときの処理
  # 主にクイックフィックス機能の処理
  def m_text_document__code_action(self, textDocument=None, range=None, context=None, **_kwargs):
    code_actions = []
    changes = []
    for diag in context['diagnostics']:
      if diag['source'] == 'lse-in-python' and diag['message'] == '小文字のアルファベット':
        changes.append({
          'range': diag['range'],
          'newText': diag['data']
        })
    if len(changes) > 0:
      code_actions.append({
        'title': '小文字を大文字に変換する',
        'kind': 'quickfix',
        'diagnostics': [diag],
        'edit': {
          'changes': {
            textDocument['uri'] : changes
          }
        }
      })
    return code_actions

  # Ctrl+Spaceを押したときや補完候補と先頭一致する文字が入力されたときの処理
  def m_text_document__completion(self, context=None, **_kwargs):
    return {
      'isIncomplete': True,
      'items': [{
        'label': "aを入力したときの補完候補",
      },{
        'label': "bを入力したときの補完候補",
        'insertText': "ラベルとは異なる文字列を挿入"
      }]
    }

  # ドキュメントのフォーマットが選択されたときの処理
  # テキスト中の小文字アルファベットをすべて大文字に変換する
  def m_text_document__formatting(self, textDocument=None, _options=None, **_kwargs):
    return [{
      'range': {
        'start': {'line': 0, 'character': 0},
        'end': {'line': len(self.lastDocument.split('\n')), 'character': 0}
      },
      'newText': IS_LOWER.sub(lambda m: m.group().upper(), self.lastDocument)
    }]


if __name__ == "__main__":
  sls = SampleLanguageServer()
  sls.start()

