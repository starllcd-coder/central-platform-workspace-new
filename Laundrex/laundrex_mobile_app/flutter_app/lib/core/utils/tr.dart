import 'package:flutter/widgets.dart';

import '../../main.dart';

bool isArabicLocale(BuildContext context) {
  return LaundrexScope.of(context).locale.languageCode.toLowerCase().startsWith('ar');
}

String tr(BuildContext context, {required String en, required String ar}) {
  return isArabicLocale(context) ? ar : en;
}
