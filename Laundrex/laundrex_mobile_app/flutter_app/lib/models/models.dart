class Laundry {
  final int id;
  final String name;
  final String city;
  final double rating;
  final String eta;
  final String subtitle;
  final String area;
  final String address;
  final bool supportsUrgent;

  Laundry({
    required this.id,
    required this.name,
    required this.city,
    required this.rating,
    required this.eta,
    required this.subtitle,
    this.area = '',
    this.address = '',
    this.supportsUrgent = true,
  });

  factory Laundry.fromJson(Map<String, dynamic> json) {
    final area = (json['area'] ?? '').toString();
    final city = (json['city'] ?? '').toString();
    return Laundry(
      id: (json['id'] as num).toInt(),
      name: (json['name'] ?? 'Laundry').toString(),
      city: city,
      rating: ((json['rating'] ?? 4.8) as num).toDouble(),
      eta: '${((json['distance_km'] ?? 2.4) as num).toDouble().toStringAsFixed(1)} km',
      subtitle: [area, city].where((e) => e.isNotEmpty).join(' • ').isEmpty
          ? ((json['address'] ?? 'Premium garment care').toString())
          : [area, city].where((e) => e.isNotEmpty).join(' • '),
      area: area,
      address: (json['address'] ?? '').toString(),
      supportsUrgent: json['supports_urgent'] == null ? true : json['supports_urgent'] == true,
    );
  }
}

class CatalogItem {
  final int id;
  final int itemId;
  final String name;
  final String nameAr;
  final double price;
  final String category;
  final int serviceId;
  final String serviceName;
  final String serviceNameAr;

  CatalogItem({
    required this.id,
    int? itemId,
    required this.name,
    this.nameAr = '',
    required this.price,
    required this.category,
    required this.serviceId,
    required this.serviceName,
    this.serviceNameAr = '',
  }) : itemId = itemId ?? id;

  factory CatalogItem.fromJson(Map<String, dynamic> json) {
    final itemId = (json['item_id'] as num).toInt();
    return CatalogItem(
      id: json['id'] == null ? itemId : (json['id'] as num).toInt(),
      itemId: itemId,
      name: (json['item_name'] ?? 'Item').toString(),
      nameAr: (json['item_name_ar'] ?? '').toString(),
      price: double.tryParse(json['price'].toString()) ?? 0,
      category: (json['service_name'] ?? 'Service').toString(),
      serviceId: (json['service_id'] as num).toInt(),
      serviceName: (json['service_name'] ?? '').toString(),
      serviceNameAr: (json['service_name_ar'] ?? '').toString(),
    );
  }
}

class AddressModel {
  final int id;
  final String label;
  final String line1;
  final String line2;
  final bool isDefault;
  final String city;
  final String area;
  final String addressLine1;
  final String addressLine2;
  final double? latitude;
  final double? longitude;

  AddressModel({
    required this.id,
    required this.label,
    required this.line1,
    required this.line2,
    this.isDefault = false,
    this.city = '',
    this.area = '',
    this.addressLine1 = '',
    this.addressLine2 = '',
    this.latitude,
    this.longitude,
  });

  factory AddressModel.fromJson(Map<String, dynamic> json) {
    final line1 = (json['address_line_1'] ?? '').toString();
    final area = (json['area'] ?? '').toString();
    final city = (json['city'] ?? '').toString();
    final line2 = (json['address_line_2'] ?? json['building'] ?? '').toString();
    return AddressModel(
      id: (json['id'] as num).toInt(),
      label: (json['label'] ?? 'Address').toString(),
      line1: [line1, area, city].where((e) => e.isNotEmpty).join(', '),
      line2: line2,
      isDefault: json['is_default'] == true,
      city: city,
      area: area,
      addressLine1: line1,
      addressLine2: line2,
      latitude: json['latitude'] == null ? null : double.tryParse(json['latitude'].toString()),
      longitude: json['longitude'] == null ? null : double.tryParse(json['longitude'].toString()),
    );
  }
}

class OrderModel {
  final int? id;
  final String code;
  final String status;
  final String laundryName;
  final String amount;
  final String placedAt;

  OrderModel({
    this.id,
    required this.code,
    required this.status,
    required this.laundryName,
    required this.amount,
    required this.placedAt,
  });

  factory OrderModel.fromJson(Map<String, dynamic> json) {
    final total = double.tryParse(json['total'].toString()) ?? 0;
    final createdAt = (json['created_at'] ?? '').toString();
    return OrderModel(
      id: json['id'] == null ? null : (json['id'] as num).toInt(),
      code: (json['order_no'] ?? 'LDRX').toString(),
      status: (json['status'] ?? 'RECEIVED').toString(),
      laundryName: ((json['laundry_shop'] ?? const {})['name'] ?? 'Laundrex').toString(),
      amount: 'OMR ${total.toStringAsFixed(3)}',
      placedAt: createdAt.isEmpty ? 'Just now' : createdAt,
    );
  }
}

class PaymentMethod {
  final String code;
  final String label;

  PaymentMethod({
    required this.code,
    required this.label,
  });

  factory PaymentMethod.fromJson(Map<String, dynamic> json) {
    return PaymentMethod(
      code: (json['code'] ?? '').toString(),
      label: (json['label'] ?? '').toString(),
    );
  }
}

class NotificationModel {
  final int id;
  final String title;
  final String message;
  final String eventCode;
  final bool isRead;
  final String createdAt;
  final String orderNo;

  NotificationModel({
    required this.id,
    required this.title,
    required this.message,
    required this.eventCode,
    required this.isRead,
    required this.createdAt,
    required this.orderNo,
  });

  factory NotificationModel.fromJson(Map<String, dynamic> json) {
    return NotificationModel(
      id: (json['id'] as num).toInt(),
      title: (json['title'] ?? '').toString(),
      message: (json['message'] ?? '').toString(),
      eventCode: (json['event_code'] ?? '').toString(),
      isRead: json['is_read'] == true,
      createdAt: (json['created_at'] ?? '').toString(),
      orderNo: (json['order_no'] ?? '').toString(),
    );
  }
}

class ReceiptLine {
  final String itemName;
  final String serviceName;
  final int qty;
  final double unitPrice;
  final double lineTotal;

  ReceiptLine({
    required this.itemName,
    required this.serviceName,
    required this.qty,
    required this.unitPrice,
    required this.lineTotal,
  });
}

class ReceiptData {
  final String orderNo;
  final String placedAt;
  final String laundryName;
  final String paymentMethod;
  final String fulfillmentMode;
  final String timeSlot;
  final String notes;
  final double subtotal;
  final double urgentFee;
  final double promoDiscount;
  final double pointsDiscount;
  final double tax;
  final double total;
  final List<ReceiptLine> lines;

  ReceiptData({
    required this.orderNo,
    required this.placedAt,
    required this.laundryName,
    required this.paymentMethod,
    required this.fulfillmentMode,
    required this.timeSlot,
    required this.notes,
    required this.subtotal,
    required this.urgentFee,
    required this.promoDiscount,
    required this.pointsDiscount,
    required this.tax,
    required this.total,
    required this.lines,
  });
}
