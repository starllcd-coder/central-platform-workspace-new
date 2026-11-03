import 'package:flutter/widgets.dart';

import 'tr.dart';

const Map<String, String> _cityArabicNames = {
  'Muscat': '\u0645\u0633\u0642\u0637',
  'Salalah': '\u0635\u0644\u0627\u0644\u0629',
  'Seeb': '\u0627\u0644\u0633\u064a\u0628',
  'Bawshar': '\u0628\u0648\u0634\u0631',
  'Muttrah': '\u0645\u0637\u0631\u062d',
  'Sohar': '\u0635\u062d\u0627\u0631',
  'Nizwa': '\u0646\u0632\u0648\u0649',
  'Sur': '\u0635\u0648\u0631',
  'Barka': '\u0628\u0631\u0643\u0627\u0621',
  'Rustaq': '\u0627\u0644\u0631\u0633\u062a\u0627\u0642',
  'Ibri': '\u0639\u0628\u0631\u064a',
  'Khasab': '\u062e\u0635\u0628',
  'Buraimi': '\u0627\u0644\u0628\u0631\u064a\u0645\u064a',
  'Duqm': '\u0627\u0644\u062f\u0642\u0645',
  'Ibra': '\u0625\u0628\u0631\u0627\u0621',
  'Bahla': '\u0628\u0647\u0644\u0627\u0621',
  'Samail': '\u0633\u0645\u0627\u0626\u0644',
  'Saham': '\u0635\u062d\u0645',
  'Shinas': '\u0634\u0646\u0627\u0635',
  'Khaburah': '\u0627\u0644\u062e\u0627\u0628\u0648\u0631\u0629',
  'Liwa': '\u0644\u0648\u0649',
  'Adam': '\u0622\u062f\u0645',
  'Thumrait': '\u062b\u0645\u0631\u064a\u062a',
  'Haima': '\u0647\u064a\u0645\u0627\u0621',
};

String cityLabel(BuildContext context, String city) {
  if (!isArabicLocale(context)) return city;
  return _cityArabicNames[city] ?? city;
}
