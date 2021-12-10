// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
import * as vscode from 'vscode';

// 追加import
import * as path from "path";
//@ts-ignore
import { Executable, LanguageClient, LanguageClientOptions, StreamInfo, ServerOptions } from 'vscode-languageclient';


// this method is called when your extension is activated
// your extension is activated the very first time the command is executed
export function activate(context: vscode.ExtensionContext) {

	// Use the console to output diagnostic information (console.log) and errors (console.error)
	// This line of code will only be executed once when your extension is activated
	console.log('Congratulations, your extension "lse-in-python" is now active!');

	// The command has been defined in the package.json file
	// Now provide the implementation of the command with registerCommand
	// The commandId parameter must match the command field in package.json
	let disposable = vscode.commands.registerCommand('lse-in-python.helloWorld', () => {
		// The code you place here will be executed every time your command is executed
		// Display a message box to the user
		vscode.window.showInformationMessage('Hello World from LSE in Python!');
	});

	context.subscriptions.push(disposable);

  // ここまでテンプレートのまま
  // ここから追加分

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
    // プレーンテキストファイルとPythonファイルに対して有効になる
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
  const client: LanguageClient = new LanguageClient(
    "lseInPython",
    "Language Server Extension in Python",
    serverOptions,
    clientOptions
  );
  client.start();
}

// this method is called when your extension is deactivated
export function deactivate() {}
