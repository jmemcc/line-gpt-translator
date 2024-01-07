# LINE GPT Translator

LINE GPT Translatorは、GPT-3 Turbo APIを使用してLINEのメッセージを日本語から英語へ（その逆も同様）に翻訳するPythonアプリです。

> [The English version of this document is available here](https://github.com/jmemcc/line-gpt-translator/blob/master/README.md)

## 必要条件

- Python >= 3.8
- line-bot-sdk >= 3.7.0
- Flask >= 3.0.0
- Gunicorn >= 21.2.0

## インストール

GitHubからリポジトリをプルします。

```bash
gh repo clone jmemcc/line-gpt-translator
```

## 設定
[OpenAI API key](https://platform.openai.com/api-keys) キーと[LINE Developer account](https://developers.line.biz/)アカウントを作成します。LINE Developerコンソールで、[Messaging API](https://developers.line.biz/en/services/messaging-api/)タイプのチャンネルを作成します。

### ローカル/VPSサーバー

以下の変数をサーバーにエクスポートします。

```bash
# OpenAI開発者セクションで見つかる (https://platform.openai.com/api-keys)
export OPENAI_API_KEY=YOUR_KEY_HERE

# LINE Developerページの 『Messaging API』 タブの下で、あなたのボットのチャンネルのために見つかる (https://developers.line.biz/console/channel/YOUR_CHANNEL_ID/messaging-api)
export LINE_CHANNEL_SECRET=YOUR_KEY_HERE
export LINE_CHANNEL_ACCESS_TOKEN=YOUR_KEY_HERE
```

LINEはインターネットに接続されたサーバーを使用してメッセージングAPIチャネルを使用する必要があります。好きなホスティング方法を使用してください。以下に[ngrok](https://ngrok.com/)を例として使用します。


```bash
ngrok http 8000
```

メッセージングAPIタブに移動し、ngrokによって生成されたURLに`/callback`を追加して**Webhook URL**を設定します（例：`https://xxxx-xxx-xxx-xx-xx.ngrok-free.app/callback`）。**Webhookを使用**をオンにして、**検証**をクリックします。『Success』というメッセージが表示されるはずです。

**LINE公式アカウントの機能**は好きなように設定してください。

### Vercel


このリポジトリをあなたのGitHubにフォークし、フォークから新しいVercelプロジェクトを作成します。

**プロジェクトの設定**セクションでは、全て同じにして、`OPENAI_API_KEY`、`LINE_CHANNEL_SECRET`、`LINE_CHANNEL_ACCESS_TOKEN`を**環境変数**として追加します。

プロジェクトをデプロイしたら、デプロイが完了すると:
- **ドメイン**の下のURLをコピーします
- LINEチャネルページのメッセージングAPIタブに移動します
- **Webhook URL**にこのURLを貼り付け、文字列に`/callback`を追加します（例：`https://xxxxxxxxx.vercel.app/callback`）
- **Webhookを使用**をオンにし、**検証**をクリックします。'Success'というメッセージが表示されれば、ボットはサーバーに接続できています。
- **LINE公式アカウントの機能**の下の**自動返信メッセージ**オプションを無効にし、**グループチャットへのボットの参加を許可**を有効にします。


## 使用方法

インターネットに接続されたサーバーを起動した状態でアプリを開始します。

```bash
python app.py
```

LINE上であなたのボットにテキストを送信して翻訳してみてください。

## ライセンス

[Apache License 2.0](https://choosealicense.com/licenses/apache-2.0/)
