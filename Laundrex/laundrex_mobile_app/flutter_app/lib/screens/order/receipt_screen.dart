import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart' show rootBundle;
import 'package:pdf/pdf.dart';
import 'package:pdf/widgets.dart' as pw;
import 'package:printing/printing.dart';

import '../../core/utils/tr.dart';
import '../../core/widgets/neo_card.dart';
import '../../main.dart';
import '../../models/models.dart';

class ReceiptScreen extends StatelessWidget {
  const ReceiptScreen({super.key});

  String _t(bool isAr, {required String en, required String ar}) => isAr ? ar : en;

  String _paymentLabel(bool isAr, String raw) {
    final v = raw.trim().toLowerCase();
    if (v == 'cod' || v.contains('cash')) return _t(isAr, en: 'Cash on delivery', ar: 'الدفع عند الاستلام');
    if (v.contains('bank')) return _t(isAr, en: 'Bank transfer', ar: 'تحويل بنكي');
    if (v.contains('card') || v.contains('pos')) return _t(isAr, en: 'Card / POS', ar: 'بطاقة / جهاز نقاط');
    return raw;
  }

  Future<pw.Font?> _tryLoadFont(List<String> assetPaths) async {
    for (final path in assetPaths) {
      try {
        return pw.Font.ttf(await rootBundle.load(path));
      } catch (_) {
        continue;
      }
    }
    return null;
  }

  Future<pw.ThemeData> _pdfTheme() async {
    final base = await _tryLoadFont(['assets/fonts/arial.ttf', 'assets/arial.ttf']);
    if (base == null) {
      throw Exception('Unable to load PDF font asset (assets/fonts/arial.ttf)');
    }
    final bold = await _tryLoadFont(['assets/fonts/arialbd.ttf', 'assets/arialbd.ttf']) ?? base;
    return pw.ThemeData.withFont(base: base, bold: bold);
  }

  Future<Uint8List> _buildPdf(ReceiptData data, {required bool isAr}) async {
    final pdf = pw.Document();
    final payment = _paymentLabel(isAr, data.paymentMethod);
    final theme = await _pdfTheme();

    pdf.addPage(
      pw.Page(
        pageFormat: PdfPageFormat.a4,
        margin: const pw.EdgeInsets.all(24),
        theme: theme,
        build: (_) {
          return pw.Directionality(
            textDirection: isAr ? pw.TextDirection.rtl : pw.TextDirection.ltr,
            child: pw.Column(
              crossAxisAlignment: pw.CrossAxisAlignment.start,
              children: [
                pw.Text(
                  _t(isAr, en: 'Laundrex Receipt', ar: 'إيصال لاندركس'),
                  style: pw.TextStyle(fontSize: 22, fontWeight: pw.FontWeight.bold),
                ),
                pw.SizedBox(height: 8),
                pw.Text('${_t(isAr, en: 'Order', ar: 'الطلب')}: ${data.orderNo}'),
                pw.Text('${_t(isAr, en: 'Laundry', ar: 'المغسلة')}: ${data.laundryName}'),
                pw.Text('${_t(isAr, en: 'Date', ar: 'التاريخ')}: ${data.placedAt}'),
                pw.Text('${_t(isAr, en: 'Payment', ar: 'الدفع')}: $payment'),
                pw.SizedBox(height: 16),
                pw.TableHelper.fromTextArray(
                  headerStyle: pw.TextStyle(fontWeight: pw.FontWeight.bold),
                  headers: [
                    _t(isAr, en: 'Item', ar: 'الصنف'),
                    _t(isAr, en: 'Service', ar: 'الخدمة'),
                    _t(isAr, en: 'Qty', ar: 'الكمية'),
                    _t(isAr, en: 'Unit', ar: 'سعر الوحدة'),
                    _t(isAr, en: 'Total', ar: 'الإجمالي'),
                  ],
                  data: data.lines
                      .map((l) => [
                            l.itemName,
                            l.serviceName,
                            l.qty.toString(),
                            l.unitPrice.toStringAsFixed(3),
                            l.lineTotal.toStringAsFixed(3),
                          ])
                      .toList(),
                ),
                pw.SizedBox(height: 18),
                pw.Align(
                  alignment: isAr ? pw.Alignment.centerLeft : pw.Alignment.centerRight,
                  child: pw.Column(
                    crossAxisAlignment: pw.CrossAxisAlignment.start,
                    children: [
                      pw.Text('${_t(isAr, en: 'Subtotal', ar: 'المجموع الفرعي')}: OMR ${data.subtotal.toStringAsFixed(3)}'),
                      pw.Text('${_t(isAr, en: 'Urgent fee', ar: 'رسوم الاستعجال')}: OMR ${data.urgentFee.toStringAsFixed(3)}'),
                      pw.Text('${_t(isAr, en: 'Promo discount', ar: 'خصم القسيمة')}: - OMR ${data.promoDiscount.toStringAsFixed(3)}'),
                      pw.Text('${_t(isAr, en: 'Points', ar: 'النقاط')}: - OMR ${data.pointsDiscount.toStringAsFixed(3)}'),
                      if (data.tax > 0) pw.Text('${_t(isAr, en: 'Tax', ar: 'الضريبة')}: OMR ${data.tax.toStringAsFixed(3)}'),
                      pw.SizedBox(height: 6),
                      pw.Text(
                        '${_t(isAr, en: 'Total', ar: 'الإجمالي')}: OMR ${data.total.toStringAsFixed(3)}',
                        style: pw.TextStyle(fontWeight: pw.FontWeight.bold),
                      ),
                    ],
                  ),
                ),
                if (data.notes.trim().isNotEmpty) ...[
                  pw.SizedBox(height: 14),
                  pw.Text('${_t(isAr, en: 'Notes', ar: 'ملاحظات')}: ${data.notes.trim()}'),
                ],
              ],
            ),
          );
        },
      ),
    );
    return pdf.save();
  }

  Future<void> _openPdf(Uint8List bytes, {required bool isAr}) async {
    if (kIsWeb) {
      await Printing.layoutPdf(onLayout: (_) async => bytes);
      return;
    }
    await Printing.layoutPdf(onLayout: (_) async => bytes);
  }

  Future<void> _sharePdf(Uint8List bytes, String orderNo, {required bool isAr}) async {
    if (kIsWeb) {
      await Printing.layoutPdf(onLayout: (_) async => bytes);
      return;
    }
    await Printing.sharePdf(bytes: bytes, filename: '${orderNo}_receipt.pdf');
  }

  @override
  Widget build(BuildContext context) {
    final isAr = isArabicLocale(context);
    final store = LaundrexScope.of(context).store;
    final data = store.lastReceipt;

    if (data == null) {
      return Scaffold(
        appBar: AppBar(title: Text(tr(context, en: 'Receipt', ar: 'الإيصال'))),
        body: Center(child: Text(tr(context, en: 'No receipt available yet.', ar: 'لا يوجد إيصال حتى الآن.'))),
      );
    }

    final payment = _paymentLabel(isAr, data.paymentMethod);

    return Scaffold(
      appBar: AppBar(title: Text(tr(context, en: 'Receipt', ar: 'الإيصال'))),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          NeoCard(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(data.orderNo, style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 20)),
                const SizedBox(height: 6),
                Text('${tr(context, en: 'Laundry', ar: 'المغسلة')}: ${data.laundryName}'),
                Text('${tr(context, en: 'Date', ar: 'التاريخ')}: ${data.placedAt}'),
                Text('${tr(context, en: 'Payment', ar: 'الدفع')}: $payment'),
              ],
            ),
          ),
          const SizedBox(height: 12),
          NeoCard(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(tr(context, en: 'Items', ar: 'العناصر'), style: const TextStyle(fontWeight: FontWeight.w800)),
                const SizedBox(height: 10),
                ...data.lines.map(
                  (line) => Padding(
                    padding: const EdgeInsets.only(bottom: 10),
                    child: Row(
                      children: [
                        Expanded(
                          child: Text('${line.itemName} - ${line.serviceName}\n${line.qty} x OMR ${line.unitPrice.toStringAsFixed(3)}'),
                        ),
                        Text('OMR ${line.lineTotal.toStringAsFixed(3)}', style: const TextStyle(fontWeight: FontWeight.w700)),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 12),
          NeoCard(
            child: Column(
              children: [
                _line(tr(context, en: 'Subtotal', ar: 'المجموع الفرعي'), 'OMR ${data.subtotal.toStringAsFixed(3)}'),
                const SizedBox(height: 6),
                _line(tr(context, en: 'Urgent fee', ar: 'رسوم الاستعجال'), 'OMR ${data.urgentFee.toStringAsFixed(3)}'),
                const SizedBox(height: 6),
                _line(tr(context, en: 'Promo discount', ar: 'خصم القسيمة'), '- OMR ${data.promoDiscount.toStringAsFixed(3)}'),
                const SizedBox(height: 6),
                _line(tr(context, en: 'Points', ar: 'النقاط'), '- OMR ${data.pointsDiscount.toStringAsFixed(3)}'),
                if (data.tax > 0) ...[
                  const SizedBox(height: 6),
                  _line(tr(context, en: 'Tax', ar: 'الضريبة'), 'OMR ${data.tax.toStringAsFixed(3)}'),
                ],
                const SizedBox(height: 8),
                _line(tr(context, en: 'Total', ar: 'الإجمالي'), 'OMR ${data.total.toStringAsFixed(3)}', bold: true),
              ],
            ),
          ),
          const SizedBox(height: 14),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton.icon(
              onPressed: () async {
                try {
                  final bytes = await _buildPdf(data, isAr: isAr);
                  await _openPdf(bytes, isAr: isAr);
                } catch (e) {
                  if (context.mounted) {
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(content: Text('${tr(context, en: 'PDF failed', ar: 'فشل إنشاء PDF')}: $e')),
                    );
                  }
                }
              },
              icon: const Icon(Icons.picture_as_pdf_outlined),
              label: Text(tr(context, en: 'Download PDF', ar: 'تنزيل PDF')),
            ),
          ),
          const SizedBox(height: 10),
          SizedBox(
            width: double.infinity,
            child: OutlinedButton.icon(
              onPressed: () async {
                try {
                  final bytes = await _buildPdf(data, isAr: isAr);
                  await _sharePdf(bytes, data.orderNo, isAr: isAr);
                } catch (e) {
                  if (context.mounted) {
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(content: Text('${tr(context, en: 'Share failed', ar: 'فشلت المشاركة')}: $e')),
                    );
                  }
                }
              },
              icon: const Icon(Icons.share_outlined),
              label: Text(tr(context, en: 'Share PDF', ar: 'مشاركة PDF')),
            ),
          ),
        ],
      ),
    );
  }

  Widget _line(String left, String right, {bool bold = false}) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(left),
        Text(
          right,
          style: TextStyle(fontWeight: bold ? FontWeight.w800 : FontWeight.w600, fontSize: bold ? 18 : 15),
        ),
      ],
    );
  }
}
