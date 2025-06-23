import 'dart:async';
import 'dart:math';
import 'package:firebase_database/firebase_database.dart';
import 'package:flutter/material.dart';
import 'package:flutter_compass/flutter_compass.dart';
import 'package:speech_to_text/speech_to_text.dart' as stt;
import 'package:flutter_tts/flutter_tts.dart';
import 'package:permission_handler/permission_handler.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  double _direction = 0;
  late stt.SpeechToText _speech;
  late FlutterTts _tts;
  bool _isListening = false;
  final Set<String> _seenInstructions = {}; // Track announced instructions
  StreamSubscription<DatabaseEvent>? _instructionSub;
  StreamSubscription<DatabaseEvent>? _ocrSub;

  @override
  void initState() {
    super.initState();
    _requestPermissions();
    _speech = stt.SpeechToText();
    _tts = FlutterTts();

    FlutterCompass.events?.listen((event) {
      if (event.heading != null) {
        setState(() {
          _direction =
              (event.heading! + 360) % 360; // convert -180~180 to 0~360
        });
        _updateUserDirection(_direction);
      }
    });

    _startListeningToInstructions();
    _startListeningToOCR();
  }

  Future<void> _requestPermissions() async {
    await Permission.locationWhenInUse.request();
    await Permission.microphone.request();
  }

  void _startListening() async {
    bool available = await _speech.initialize();
    if (available) {
      setState(() => _isListening = true);
      _speech.listen(
        onResult: (result) {
          if (result.finalResult) {
            setState(() => _isListening = false);
            String command = result.recognizedWords;
            _sendToFirebase(command);
          }
        },
      );
    } else {
      print("Speech recognition not available.");
    }
  }

  void _sendToFirebase(String command) async {
    final cmd = command.toLowerCase();
    final ref = FirebaseDatabase.instance.ref("commands");
    final timestamp = DateTime.now().millisecondsSinceEpoch;

    if (cmd == "read") {
      await ref.push().set({
        'command': command,
        'type': 'ocr',
        'timestamp': timestamp,
      });
      await _tts.speak("Sending command to read text.");
    } else if (cmd.startsWith("find my ")) {
      await ref.push().set({
        'command': command,
        'type': 'object',
        'timestamp': timestamp,
      });
      await _tts.speak("You said $command. Sending to system.");
    } else {
      await _tts.speak("Sorry, I didn’t understand.");
      print("⚠️ Ignored invalid command: $command");
    }
  }

  void _updateUserDirection(double direction) async {
    await FirebaseDatabase.instance
        .ref("user_direction")
        .set(direction.toStringAsFixed(0));
  }

  void _startListeningToInstructions() {
    final ref = FirebaseDatabase.instance.ref("navigation_instructions");
    _instructionSub = ref.onValue.listen((event) async {
      final snapshot = event.snapshot;
      if (snapshot.exists && snapshot.value is Map) {
        final map = Map<String, dynamic>.from(snapshot.value as Map);
        final sortedKeys = map.keys.toList()..sort();

        for (String key in sortedKeys) {
          if (!_seenInstructions.contains(key)) {
            final instruction = map[key]?.toString() ?? "";
            if (instruction.isNotEmpty) {
              print("📢 Instruction: $instruction");
              await _tts.speak(instruction);
              _seenInstructions.add(key);
            }
          }
        }
      }
    });
  }

  void _startListeningToOCR() {
    final ref = FirebaseDatabase.instance.ref("ocr_result/text");
    _ocrSub = ref.onValue.listen((event) async {
      final text = event.snapshot.value?.toString() ?? "";
      if (text.isNotEmpty) {
        print("📖 OCR Result: $text");
        await _tts.speak(text);
      }
    });
  }

  @override
  void dispose() {
    _instructionSub?.cancel();
    _ocrSub?.cancel();
    _speech.stop();
    _tts.stop();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0B2545),
      body: GestureDetector(
        onTap: _startListening,
        behavior: HitTestBehavior.opaque,
        child: Center(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              SizedBox(
                width: 250,
                height: 250,
                child: CustomPaint(
                  painter: RotatingCompassPainter(_direction),
                ),
              ),
              const SizedBox(height: 40),
              Icon(
                Icons.mic,
                size: 80,
                color: _isListening ? Colors.red : Colors.white,
              ),
              const SizedBox(height: 20),
              const Text(
                'Tap anywhere to speak',
                style: TextStyle(color: Colors.white54, fontSize: 16),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class RotatingCompassPainter extends CustomPainter {
  final double direction;
  RotatingCompassPainter(this.direction);

  @override
  void paint(Canvas canvas, Size size) {
    final center = size.center(Offset.zero);
    final radius = size.width / 2;

    // Rotate the compass (not the needle)
    canvas.save();
    canvas.translate(center.dx, center.dy);
    canvas.rotate(-direction * pi / 180); // Rotate the compass ring

    final tickPaint = Paint()
      ..color = Colors.white
      ..strokeWidth = 1;

    final circlePaint = Paint()
      ..color = Colors.white
      ..style = PaintingStyle.stroke
      ..strokeWidth = 3;

    canvas.drawCircle(Offset.zero, radius, circlePaint);

    for (int i = 0; i < 360; i += 15) {
      final angle = (i - 90) * pi / 180;
      final outer = Offset(radius * cos(angle), radius * sin(angle));
      final inner =
          Offset((radius - 10) * cos(angle), (radius - 10) * sin(angle));
      canvas.drawLine(inner, outer, tickPaint);
    }

    const textStyle = TextStyle(color: Colors.white, fontSize: 16);
    const directions = {'N': 0, 'E': 90, 'S': 180, 'W': 270};

    directions.forEach((label, deg) {
      final rad = (deg - 90) * pi / 180;
      final offset =
          Offset((radius - 30) * cos(rad) - 8, (radius - 30) * sin(rad) - 8);
      final tp = TextPainter(
        text: TextSpan(text: label, style: textStyle),
        textAlign: TextAlign.center,
        textDirection: TextDirection.ltr,
      )..layout();
      tp.paint(canvas, offset);
    });

    canvas.restore(); // Stop rotating

    // Static needle at 0° (North)
    final redNeedle = Paint()
      ..color = Colors.red
      ..strokeWidth = 4;
    final needleEnd =
        Offset(center.dx, center.dy - (radius - 30)); // pointing up
    canvas.drawLine(center, needleEnd, redNeedle);

    final degreeText = TextPainter(
      text: TextSpan(
        text: '${direction.toStringAsFixed(0)}°',
        style: const TextStyle(color: Colors.white, fontSize: 32),
      ),
      textAlign: TextAlign.center,
      textDirection: TextDirection.ltr,
    )..layout();

    degreeText.paint(
        canvas,
        Offset(center.dx - degreeText.width / 2,
            center.dy - degreeText.height / 2));
  }

  @override
  bool shouldRepaint(CustomPainter oldDelegate) => true;
}
