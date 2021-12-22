// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
import * as vscode from 'vscode';


import * as path from "path";
//@ts-ignore
import { Executable, LanguageClient, LanguageClientOptions, StreamInfo, ServerOptions } from 'vscode-languageclient';

let client: LanguageClient;

// this method is called when your extension is activated
// your extension is activated the very first time the command is executed
export function activate(context: vscode.ExtensionContext) {
  // サーバ側のエントリーポイントファイルの絶対パスを取得する
  const serverPath: string = context.asAbsolutePath(
    path.join("server", "server.py")
  );

  // サーバ側の設定を定義する
  const serverOptions: ServerOptions = {
    command: "python",
    args: [serverPath],
  };

  // クライアント側の設定を定義する
  const clientOptions: LanguageClientOptions = {
    // プレーンテキストファイルとPythonファイルに対して有効にする
    documentSelector: [
      {
        scheme: "file",
        language: "plaintext"
      },
      {
        scheme: "file",
        language: "python"
      }
    ]
  };

  // クライアントを起動する
  client = new LanguageClient(
    "lseInPython",
    "Language Server Extension in Python",
    serverOptions,
    clientOptions
  );
  client.start();
}

// this method is called when your extension is deactivated
export function deactivate() {
  if(!client) {
    return undefined;
  } else {
    return client.stop();
  }
}
