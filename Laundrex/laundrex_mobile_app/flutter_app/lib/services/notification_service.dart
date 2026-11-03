import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter/material.dart';

import '../core/network/api_config.dart';

class NotificationService {
  static bool _initialized = false;

  static Future<String?> init() async {
    if (!ApiConfig.enablePushNotifications) return null;
    try {
      if (ApiConfig.firebaseApiKey.isEmpty ||
          ApiConfig.firebaseAppId.isEmpty ||
          ApiConfig.firebaseMessagingSenderId.isEmpty ||
          ApiConfig.firebaseProjectId.isEmpty) {
        debugPrint('Push notifications are enabled but Firebase configuration is incomplete.');
        return null;
      }
      await Firebase.initializeApp(
        options: const FirebaseOptions(
          apiKey: ApiConfig.firebaseApiKey,
          appId: ApiConfig.firebaseAppId,
          messagingSenderId: ApiConfig.firebaseMessagingSenderId,
          projectId: ApiConfig.firebaseProjectId,
        ),
      );
      _initialized = true;
      final messaging = FirebaseMessaging.instance;
      await messaging.requestPermission();
      final token = await messaging.getToken();
      return token;
    } catch (error, stackTrace) {
      debugPrint('Firebase initialization failed: $error');
      debugPrintStack(stackTrace: stackTrace);
      return null;
    }
  }

  static void listenForegroundMessages(ValueChanged<RemoteMessage> onMessage) {
    if (!_initialized) return;
    FirebaseMessaging.onMessage.listen(onMessage);
  }
}
