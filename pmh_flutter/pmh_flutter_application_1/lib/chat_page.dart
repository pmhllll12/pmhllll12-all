import 'dart:async';

import 'package:flutter/material.dart';

/// 대화 한 줄. [isMine] 이 참이면 내가 보낸 메시지다.
class _Message {
  const _Message({required this.text, required this.isMine});

  final String text;
  final bool isMine;
}

/// 채팅 화면.
///
/// 아직 서버에 붙지 않았다. 보낸 메시지는 목록에 쌓이고, 응답은 [_replyDelay]
/// 뒤에 돌아오는 고정 문구다. 백엔드를 붙일 때 [_ChatPageState._send] 안의
/// 임시 응답만 실제 호출로 바꾸면 된다.
class ChatPage extends StatefulWidget {
  const ChatPage({super.key});

  @override
  State<ChatPage> createState() => _ChatPageState();
}

const _replyDelay = Duration(milliseconds: 600);

class _ChatPageState extends State<ChatPage> {
  final List<_Message> _messages = <_Message>[
    const _Message(text: '무엇을 도와드릴까요?', isMine: false),
  ];
  final TextEditingController _input = TextEditingController();
  Timer? _replyTimer;

  @override
  void dispose() {
    _replyTimer?.cancel();
    _input.dispose();
    super.dispose();
  }

  void _send() {
    final text = _input.text.trim();
    if (text.isEmpty) return;

    setState(() {
      _messages.add(_Message(text: text, isMine: true));
      _input.clear();
    });

    // 서버 연동 전까지 쓰는 임시 응답.
    _replyTimer?.cancel();
    _replyTimer = Timer(_replyDelay, () {
      if (!mounted) return;
      setState(() {
        _messages.add(
          _Message(
            text: '"$text" 라고 하셨군요. 아직 서버에 연결되지 않았습니다.',
            isMine: false,
          ),
        );
      });
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('채팅')),
      body: Column(
        children: [
          Expanded(
            child: ListView.builder(
              // 아래에서 위로 쌓아 새 메시지가 항상 보이게 한다. 스크롤을
              // 직접 움직일 필요가 없어진다.
              reverse: true,
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
              itemCount: _messages.length,
              itemBuilder: (context, index) =>
                  _Bubble(message: _messages[_messages.length - 1 - index]),
            ),
          ),
          _InputBar(controller: _input, onSend: _send),
        ],
      ),
    );
  }
}

class _Bubble extends StatelessWidget {
  const _Bubble({required this.message});

  final _Message message;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    final mine = message.isMine;

    return Align(
      alignment: mine ? Alignment.centerRight : Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.symmetric(vertical: 4),
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
        constraints: BoxConstraints(
          maxWidth: MediaQuery.sizeOf(context).width * 0.75,
        ),
        decoration: BoxDecoration(
          color: mine ? scheme.primary : scheme.surfaceContainerHighest,
          borderRadius: BorderRadius.circular(18),
        ),
        child: Text(
          message.text,
          style: TextStyle(
            color: mine ? scheme.onPrimary : scheme.onSurface,
            fontSize: 15,
            height: 1.4,
          ),
        ),
      ),
    );
  }
}

class _InputBar extends StatelessWidget {
  const _InputBar({required this.controller, required this.onSend});

  final TextEditingController controller;
  final VoidCallback onSend;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;

    return SafeArea(
      top: false,
      child: Padding(
        padding: const EdgeInsets.fromLTRB(12, 8, 12, 12),
        child: Row(
          children: [
            Expanded(
              child: TextField(
                controller: controller,
                textInputAction: TextInputAction.send,
                onSubmitted: (_) => onSend(),
                minLines: 1,
                maxLines: 4,
                decoration: InputDecoration(
                  hintText: '메시지를 입력하세요',
                  filled: true,
                  fillColor: scheme.surfaceContainerHighest,
                  contentPadding: const EdgeInsets.symmetric(
                    horizontal: 16,
                    vertical: 12,
                  ),
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(24),
                    borderSide: BorderSide.none,
                  ),
                ),
              ),
            ),
            const SizedBox(width: 8),
            IconButton.filled(
              onPressed: onSend,
              icon: const Icon(Icons.arrow_upward),
              tooltip: '보내기',
            ),
          ],
        ),
      ),
    );
  }
}
