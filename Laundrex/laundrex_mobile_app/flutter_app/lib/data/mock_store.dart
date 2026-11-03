import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

import '../core/network/api_config.dart';
import '../models/models.dart';

class MockStore extends ChangeNotifier {
  static const _accessTokenKey = 'laundrex_access_token';
  static const _refreshTokenKey = 'laundrex_refresh_token';
  static const _userNameKey = 'laundrex_user_name';
  static const _phoneKey = 'laundrex_phone';
  static const _selectedCityKey = 'laundrex_selected_city';
  static const _emailKey = 'laundrex_email';
  static const _rememberMeKey = 'laundrex_remember_me';
  static const _cartKey = 'laundrex_cart';
  static const _lastOrderKey = 'laundrex_last_order';
  static const _preferredPaymentKey = 'laundrex_preferred_payment';
  static const _preferredFulfillmentKey = 'laundrex_preferred_fulfillment';
  static const _preferredTimeSlotKey = 'laundrex_preferred_time_slot';
  static const _preferredAddressKey = 'laundrex_preferred_address';
  static const _promoCodeKey = 'laundrex_promo_code';
  static const _usePointsKey = 'laundrex_use_points';
  static const _loyaltyPointsKey = 'laundrex_loyalty_points';
  static const _networkTimeout = Duration(seconds: 6);
  static const List<String> _omanCities = [
    'Muscat',
    'Salalah',
    'Seeb',
    'Bawshar',
    'Muttrah',
    'Sohar',
    'Nizwa',
    'Sur',
    'Barka',
    'Rustaq',
    'Ibri',
    'Khasab',
    'Buraimi',
    'Duqm',
    'Ibra',
    'Bahla',
    'Samail',
    'Saham',
    'Shinas',
    'Khaburah',
    'Liwa',
    'Adam',
    'Thumrait',
    'Haima',
  ];

  bool isLoggedIn = false;
  bool initialized = false;
  String userName = 'Guest';
  String phone = '+968 9000 0000';
  String selectedCity = '';
  String? accessToken;
  String? refreshToken;
  String? lastOtpDebugCode;
  String email = '';
  bool rememberMe = true;
  int? selectedLaundryId;
  String selectedLaundryName = 'Laundrex Express';
  String preferredPayment = 'COD';
  String preferredFulfillment = 'DELIVERY';
  String preferredTimeSlot = '10:00 AM - 12:00 PM';
  int? preferredAddressId;
  String promoCode = '';
  bool usePoints = false;
  int loyaltyPoints = 0;
  int loyaltyPointsPerOmr = 1;
  double loyaltyRedeemValuePerPoint = 0.01;
  bool googleEnabled = false;
  bool appleEnabled = false;
  bool analyticsEnabled = false;
  bool bankTransferEnabled = true;
  String bankTransferBankName = '';
  String bankTransferAccountName = '';
  String bankTransferAccountNumber = '';
  String bankTransferIban = '';
  String bankTransferInstructions = '';
  List<PaymentMethod> paymentMethods = [];
  bool laundriesLoading = false;
  bool catalogLoading = false;
  bool addressesLoading = false;
  bool ordersLoading = false;
  bool sessionExpired = false;
  bool _refreshingToken = false;
  bool catalogUsingFallback = false;
  final Map<int, List<CatalogItem>> _catalogCacheByLaundry = {};
  int? _catalogLaundryId;
  int unreadNotifications = 0;
  bool _retryingCatalogResolve = false;
  ReceiptData? lastReceipt;

  final List<CatalogItem> _fallbackCatalog = [
    CatalogItem(id: 1, name: 'Shirt', price: 1.2, category: 'Everyday Wear', serviceId: 1, serviceName: 'Wash & Iron'),
    CatalogItem(id: 2, name: 'Trouser', price: 1.0, category: 'Everyday Wear', serviceId: 1, serviceName: 'Wash & Iron'),
    CatalogItem(id: 3, name: 'T-shirt', price: 0.9, category: 'Everyday Wear', serviceId: 1, serviceName: 'Wash & Fold'),
    CatalogItem(id: 4, name: 'Jeans', price: 1.3, category: 'Everyday Wear', serviceId: 1, serviceName: 'Wash & Iron'),
    CatalogItem(id: 5, name: 'Dishdasha', price: 2.0, category: 'Traditional', serviceId: 2, serviceName: 'Premium Care'),
    CatalogItem(id: 6, name: 'Abaya', price: 2.5, category: 'Traditional', serviceId: 2, serviceName: 'Premium Care'),
    CatalogItem(id: 7, name: 'Saree', price: 3.5, category: 'Traditional', serviceId: 3, serviceName: 'Dry Clean'),
    CatalogItem(id: 8, name: 'Suit', price: 4.8, category: 'Formal', serviceId: 3, serviceName: 'Dry Clean'),
    CatalogItem(id: 9, name: 'Blazer', price: 3.8, category: 'Formal', serviceId: 3, serviceName: 'Dry Clean'),
    CatalogItem(id: 10, name: 'Tie', price: 0.7, category: 'Formal', serviceId: 2, serviceName: 'Press'),
    CatalogItem(id: 11, name: 'Bedsheet', price: 3.0, category: 'Home Linen', serviceId: 4, serviceName: 'Home Care'),
    CatalogItem(id: 12, name: 'Blanket', price: 4.0, category: 'Home Linen', serviceId: 4, serviceName: 'Home Care'),
    CatalogItem(id: 13, name: 'Curtain', price: 5.5, category: 'Home Linen', serviceId: 4, serviceName: 'Home Care'),
    CatalogItem(id: 14, name: 'Silk Dress', price: 4.2, category: 'Delicates', serviceId: 5, serviceName: 'Delicate Wash'),
    CatalogItem(id: 15, name: 'Wool Sweater', price: 3.6, category: 'Delicates', serviceId: 5, serviceName: 'Delicate Wash'),
  ];

  List<Laundry> laundries = [];
  List<CatalogItem> catalog = [];
  List<AddressModel> addresses = [
    AddressModel(id: 1, label: 'Home', line1: 'Awqad, Salalah', line2: 'Street 23, Villa 12', isDefault: true),
  ];
  List<OrderModel> orders = [
    OrderModel(code: 'LDX-1208', status: 'WASHING', laundryName: 'Laundrex Express', amount: 'OMR 8.400', placedAt: 'Today, 11:30 AM'),
  ];
  List<NotificationModel> notifications = [];
  final Map<int, int> cart = {};
  final Map<int, int> _lastOrderCart = {};

  Future<void> init() async {
    if (initialized) return;
    final prefs = await SharedPreferences.getInstance();
    accessToken = prefs.getString(_accessTokenKey);
    refreshToken = prefs.getString(_refreshTokenKey);
    userName = prefs.getString(_userNameKey) ?? userName;
    phone = prefs.getString(_phoneKey) ?? phone;
    selectedCity = prefs.getString(_selectedCityKey) ?? selectedCity;
    email = prefs.getString(_emailKey) ?? email;
    rememberMe = prefs.getBool(_rememberMeKey) ?? true;
    preferredPayment = prefs.getString(_preferredPaymentKey) ?? preferredPayment;
    preferredFulfillment = prefs.getString(_preferredFulfillmentKey) ?? preferredFulfillment;
    preferredTimeSlot = prefs.getString(_preferredTimeSlotKey) ?? preferredTimeSlot;
    preferredAddressId = prefs.getInt(_preferredAddressKey);
    promoCode = prefs.getString(_promoCodeKey) ?? promoCode;
    usePoints = prefs.getBool(_usePointsKey) ?? usePoints;
    loyaltyPoints = prefs.getInt(_loyaltyPointsKey) ?? loyaltyPoints;
    _restoreCart(prefs.getString(_cartKey));
    _restoreLastOrder(prefs.getString(_lastOrderKey));
    isLoggedIn = (accessToken ?? '').isNotEmpty;
    laundries = [];
    catalog = [];
    await fetchAppConfig();
    await fetchPaymentMethods();
    await fetchLaundries();
    if (isLoggedIn) {
      await fetchOrders();
      await fetchNotifications();
      await trackEvent('app_open');
    }
    initialized = true;
  }

  Future<void> login({String? name, String? city}) async {
    sessionExpired = false;
    isLoggedIn = true;
    if (name != null && name.isNotEmpty) userName = name;
    if (city != null && city.isNotEmpty) selectedCity = city;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_userNameKey, userName);
    await prefs.setString(_selectedCityKey, selectedCity);
    notifyListeners();
  }

  Future<void> persistAuth({required String access, required String refresh, required String name, String? phoneNumber, String? city}) async {
    accessToken = access;
    refreshToken = refresh;
    userName = name.isEmpty ? 'Customer' : name;
    if (phoneNumber != null && phoneNumber.isNotEmpty) {
      phone = phoneNumber;
    }
    if (city != null && city.isNotEmpty) {
      selectedCity = city;
    }
    sessionExpired = false;
    isLoggedIn = true;
    final prefs = await SharedPreferences.getInstance();
    if (rememberMe) {
      await prefs.setString(_accessTokenKey, access);
      await prefs.setString(_refreshTokenKey, refresh);
    } else {
      await prefs.remove(_accessTokenKey);
      await prefs.remove(_refreshTokenKey);
    }
    await prefs.setString(_userNameKey, userName);
    await prefs.setString(_phoneKey, phone);
    await prefs.setString(_selectedCityKey, selectedCity);
    notifyListeners();
  }

  Future<void> setRememberMe(bool value) async {
    rememberMe = value;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool(_rememberMeKey, value);
    if (!value) {
      await prefs.remove(_accessTokenKey);
      await prefs.remove(_refreshTokenKey);
    }
    notifyListeners();
  }

  Future<String?> completeProfileAfterOtp({
    required String fullName,
    required String city,
    String emailAddress = '',
  }) async {
    final cleanedName = fullName.trim();
    if (cleanedName.isEmpty) {
      return 'Enter your full name.';
    }
    userName = cleanedName;
    if (city.trim().isNotEmpty) {
      selectedCity = city.trim();
    }
    email = emailAddress.trim();
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_userNameKey, userName);
    await prefs.setString(_selectedCityKey, selectedCity);
    if (email.isEmpty) {
      await prefs.remove(_emailKey);
    } else {
      await prefs.setString(_emailKey, email);
    }
    notifyListeners();
    return null;
  }

  Future<void> logout() async {
    try {
      if (isLoggedIn) {
        await http.post(
          _uri('/api/auth/logout'),
          headers: _headers(auth: true),
          body: jsonEncode({'refresh': refreshToken}),
        );
      }
    } catch (_) {}
    isLoggedIn = false;
    sessionExpired = false;
    accessToken = null;
    refreshToken = null;
    cart.clear();
    notifications.clear();
    unreadNotifications = 0;
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_accessTokenKey);
    await prefs.remove(_refreshTokenKey);
    await prefs.remove(_cartKey);
    await prefs.remove(_promoCodeKey);
    await prefs.remove(_usePointsKey);
    notifyListeners();
  }

  Future<void> _handleUnauthorized() async {
    final refreshed = await _refreshAccessToken();
    if (refreshed) return;
    if (!isLoggedIn && sessionExpired) return;
    isLoggedIn = false;
    sessionExpired = true;
    accessToken = null;
    refreshToken = null;
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_accessTokenKey);
    await prefs.remove(_refreshTokenKey);
    notifyListeners();
  }

  Future<bool> _refreshAccessToken() async {
    if (_refreshingToken) return false;
    final refresh = refreshToken?.trim() ?? '';
    if (refresh.isEmpty) return false;
    _refreshingToken = true;
    try {
      final res = await http.post(
        _uri('/api/auth/token/refresh'),
        headers: _headers(),
        body: jsonEncode({'refresh': refresh}),
      ).timeout(_networkTimeout);
      if (res.statusCode < 200 || res.statusCode >= 300) {
        return false;
      }
      final data = jsonDecode(res.body) as Map<String, dynamic>;
      final newAccess = (data['access'] ?? '').toString();
      final newRefresh = (data['refresh'] ?? refresh).toString();
      if (newAccess.isEmpty) return false;
      accessToken = newAccess;
      refreshToken = newRefresh;
      isLoggedIn = true;
      sessionExpired = false;
      final prefs = await SharedPreferences.getInstance();
      if (rememberMe) {
        await prefs.setString(_accessTokenKey, newAccess);
        await prefs.setString(_refreshTokenKey, newRefresh);
      }
      notifyListeners();
      return true;
    } catch (_) {
      return false;
    } finally {
      _refreshingToken = false;
    }
  }

  void clearSessionExpiredFlag() {
    if (!sessionExpired) return;
    sessionExpired = false;
    notifyListeners();
  }

  Future<bool> retryPublicConnection() async {
    var configOk = false;
    var methodsOk = false;
    try {
      final configRes = await http.get(_uri('/api/app-config'), headers: _headers()).timeout(_networkTimeout);
      if (configRes.statusCode >= 200 && configRes.statusCode < 300) {
        final data = jsonDecode(configRes.body) as Map<String, dynamic>;
        _applyRemoteConfig(data);
        configOk = true;
      }
    } catch (_) {}

    try {
      final methodsRes = await http.get(_uri('/api/payment-methods'), headers: _headers()).timeout(_networkTimeout);
      if (methodsRes.statusCode >= 200 && methodsRes.statusCode < 300) {
        final list = (jsonDecode(methodsRes.body) as List).cast<Map<String, dynamic>>();
        paymentMethods = list.map(PaymentMethod.fromJson).toList();
        methodsOk = true;
      }
    } catch (_) {}

    if (paymentMethods.isEmpty) {
      paymentMethods = [
        PaymentMethod(code: 'COD', label: 'Cash on delivery'),
        PaymentMethod(code: 'BANK', label: 'Bank transfer'),
      ];
    }
    _normalizePaymentMethods();
    if (!paymentMethods.any((m) => m.code == preferredPayment)) {
      preferredPayment = paymentMethods.first.code;
    }
    if (configOk || methodsOk) {
      sessionExpired = false;
    }
    notifyListeners();
    return configOk && methodsOk;
  }

  Future<String?> updateProfileRemote({
    required String fullName,
    required String phoneNumber,
    required String emailAddress,
    String preferredLanguage = 'en',
    String city = '',
  }) async {
    final cleanName = fullName.trim();
    final cleanPhone = phoneNumber.trim();
    final cleanEmail = emailAddress.trim();
    final lang = preferredLanguage.toLowerCase().startsWith('ar') ? 'ar' : 'en';

    if (cleanName.isEmpty) return 'Enter full name.';
    if (cleanPhone.isEmpty) return 'Enter phone number.';

    if (!isLoggedIn) {
      userName = cleanName;
      phone = cleanPhone;
      email = cleanEmail;
      if (city.trim().isNotEmpty) {
        selectedCity = city.trim();
      }
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString(_userNameKey, userName);
      await prefs.setString(_phoneKey, phone);
      await prefs.setString(_emailKey, email);
      await prefs.setString(_selectedCityKey, selectedCity);
      notifyListeners();
      return 'Saved locally in demo mode.';
    }

    try {
      final res = await http.put(
        _uri('/api/auth/profile'),
        headers: _headers(auth: true),
        body: jsonEncode({
          'full_name': cleanName,
          'phone': cleanPhone,
          'email': cleanEmail,
          'preferred_language': lang,
        }),
      ).timeout(_networkTimeout);
      if (res.statusCode == 401) {
        await _handleUnauthorized();
        return 'Session expired. Please login again.';
      }

      if (res.statusCode >= 200 && res.statusCode < 300) {
        final data = jsonDecode(res.body) as Map<String, dynamic>;
        final user = (data['user'] as Map<String, dynamic>? ?? const {});
        final customer = (data['customer'] as Map<String, dynamic>? ?? const {});
        userName = (user['first_name'] ?? customer['name'] ?? cleanName).toString();
        phone = (customer['phone'] ?? cleanPhone).toString();
        email = (user['email'] ?? cleanEmail).toString();
        if (city.trim().isNotEmpty) {
          selectedCity = city.trim();
        }
        final prefs = await SharedPreferences.getInstance();
        await prefs.setString(_userNameKey, userName);
        await prefs.setString(_phoneKey, phone);
        await prefs.setString(_emailKey, email);
        await prefs.setString(_selectedCityKey, selectedCity);
        notifyListeners();
        return null;
      }
      final data = jsonDecode(res.body);
      return (data['detail'] ?? 'Could not update profile.').toString();
    } catch (_) {
      return 'Could not reach the API.';
    }
  }

  Future<String?> deleteAccountRemote() async {
    if (!isLoggedIn) {
      await logout();
      return null;
    }
    try {
      final res = await http.delete(_uri('/api/auth/profile'), headers: _headers(auth: true)).timeout(_networkTimeout);
      if (res.statusCode == 401) {
        await _handleUnauthorized();
        return 'Session expired. Please login again.';
      }
      if (res.statusCode == 204 || (res.statusCode >= 200 && res.statusCode < 300)) {
        await logout();
        final prefs = await SharedPreferences.getInstance();
        await prefs.remove(_userNameKey);
        await prefs.remove(_phoneKey);
        await prefs.remove(_emailKey);
        await prefs.remove(_selectedCityKey);
        userName = 'Guest';
        phone = '+968 9000 0000';
        email = '';
        selectedCity = '';
        notifyListeners();
        return null;
      }
      final data = jsonDecode(res.body);
      return (data['detail'] ?? 'Could not delete account.').toString();
    } catch (_) {
      return 'Could not reach the API.';
    }
  }

  Future<void> fetchNotifications() async {
    if (!isLoggedIn) return;
    try {
      final res = await http.get(_uri('/api/notifications'), headers: _headers(auth: true)).timeout(_networkTimeout);
      if (res.statusCode == 401) {
        await _handleUnauthorized();
        return;
      }
      if (res.statusCode >= 200 && res.statusCode < 300) {
        final data = jsonDecode(res.body) as Map<String, dynamic>;
        unreadNotifications = (data['unread_count'] as num?)?.toInt() ?? 0;
        final raw = data['results'];
        final list = (raw is Map<String, dynamic> ? raw['results'] : raw) as List? ?? const [];
        notifications = list.cast<Map<String, dynamic>>().map(NotificationModel.fromJson).toList();
        notifyListeners();
      }
    } catch (_) {}
  }

  Future<void> markNotificationsRead({int? id}) async {
    if (!isLoggedIn) return;
    try {
      final res = await http.post(
        _uri('/api/notifications/read'),
        headers: _headers(auth: true),
        body: jsonEncode(id == null ? {'all': true} : {'id': id}),
      ).timeout(_networkTimeout);
      if (res.statusCode == 401) {
        await _handleUnauthorized();
        return;
      }
    } catch (_) {}
    if (id == null) {
      notifications = notifications
          .map((n) => NotificationModel(
                id: n.id,
                title: n.title,
                message: n.message,
                eventCode: n.eventCode,
                isRead: true,
                createdAt: n.createdAt,
                orderNo: n.orderNo,
              ))
          .toList();
      unreadNotifications = 0;
    } else {
      notifications = notifications
          .map((n) => n.id == id
              ? NotificationModel(
                  id: n.id,
                  title: n.title,
                  message: n.message,
                  eventCode: n.eventCode,
                  isRead: true,
                  createdAt: n.createdAt,
                  orderNo: n.orderNo,
                )
              : n)
          .toList();
      unreadNotifications = notifications.where((n) => !n.isRead).length;
    }
    notifyListeners();
  }

  Future<String?> applyPromo(String code) async {
    final cleaned = code.trim().toUpperCase();
    if (cleaned.isEmpty) {
      promoCode = '';
      final prefs = await SharedPreferences.getInstance();
      await prefs.remove(_promoCodeKey);
      notifyListeners();
      return 'Promo removed.';
    }
    const allowed = {'FRESH20': 0.20, 'FIRST10': 0.10, 'SAVE5': 0.05};
    if (!allowed.containsKey(cleaned)) {
      return 'Promo code not valid.';
    }
    promoCode = cleaned;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_promoCodeKey, cleaned);
    notifyListeners();
    return 'Promo applied.';
  }

  Future<void> setUsePoints(bool value) async {
    usePoints = value;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool(_usePointsKey, value);
    notifyListeners();
  }

  double get pointsValue => loyaltyPoints * loyaltyRedeemValuePerPoint;

  double redeemablePointsValue(double maximumValue) {
    if (!usePoints || loyaltyRedeemValuePerPoint <= 0 || maximumValue <= 0) return 0;
    final maximumPoints = (maximumValue / loyaltyRedeemValuePerPoint).floor();
    final pointsUsed = loyaltyPoints < maximumPoints ? loyaltyPoints : maximumPoints;
    return pointsUsed * loyaltyRedeemValuePerPoint;
  }

  double promoDiscountAmount(double subtotal) {
    if (promoCode == 'FRESH20') return subtotal * 0.20;
    if (promoCode == 'FIRST10') return subtotal * 0.10;
    if (promoCode == 'SAVE5') return subtotal * 0.05;
    return 0;
  }

  Future<void> saveDeviceToken(String token) async {
    if (token.isEmpty) return;
    if (!isLoggedIn) return;
    try {
      await http.post(
        _uri('/api/devices'),
        headers: _headers(auth: true),
        body: jsonEncode({'token': token, 'platform': 'mobile'}),
      );
    } catch (_) {}
  }

  Future<void> setPreferredPayment(String value) async {
    preferredPayment = value;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_preferredPaymentKey, value);
    notifyListeners();
  }

  Future<void> setPreferredFulfillment(String value) async {
    preferredFulfillment = value;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_preferredFulfillmentKey, value);
    notifyListeners();
  }

  Future<void> setPreferredTimeSlot(String value) async {
    preferredTimeSlot = value;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_preferredTimeSlotKey, value);
    notifyListeners();
  }

  List<String> get availableTimeSlots => const [
        '08:00 AM - 10:00 AM',
        '10:00 AM - 12:00 PM',
        '12:00 PM - 02:00 PM',
        '02:00 PM - 04:00 PM',
        '04:00 PM - 06:00 PM',
        '06:00 PM - 08:00 PM',
      ];

  Future<void> setPreferredAddress(int? addressId) async {
    preferredAddressId = addressId;
    final prefs = await SharedPreferences.getInstance();
    if (addressId == null) {
      await prefs.remove(_preferredAddressKey);
    } else {
      await prefs.setInt(_preferredAddressKey, addressId);
    }
    notifyListeners();
  }

  Future<void> setSelectedCity(String value) async {
    selectedCity = value.trim();
    final prefs = await SharedPreferences.getInstance();
    if (selectedCity.isEmpty) {
      await prefs.remove(_selectedCityKey);
    } else {
      await prefs.setString(_selectedCityKey, selectedCity);
    }
    notifyListeners();
  }

  List<String> get availableCities {
    final source = laundries;
    final set = <String>{..._omanCities};
    for (final laundry in source) {
      if (laundry.city.trim().isNotEmpty) {
        set.add(laundry.city.trim());
      }
    }
    final cities = set.toList()..sort();
    return cities;
  }

  List<Laundry> get visibleLaundries {
    if (selectedCity.trim().isEmpty) return laundries;
    final normalized = selectedCity.trim().toLowerCase();
    return laundries.where((laundry) => laundry.city.trim().toLowerCase() == normalized).toList();
  }

  Map<String, String> _headers({bool auth = false}) {
    final headers = <String, String>{'Content-Type': 'application/json'};
    if (auth && accessToken != null) {
      headers['Authorization'] = 'Bearer $accessToken';
    }
    return headers;
  }

  Uri _uri(String path) => Uri.parse('${ApiConfig.baseUrl}$path');

  Future<void> fetchAppConfig() async {
    try {
      final res = await http.get(_uri('/api/app-config'), headers: _headers()).timeout(_networkTimeout);
      if (res.statusCode >= 200 && res.statusCode < 300) {
        final data = jsonDecode(res.body) as Map<String, dynamic>;
        _applyRemoteConfig(data);
        notifyListeners();
      }
    } catch (_) {}
  }

  void _applyRemoteConfig(Map<String, dynamic> data) {
    googleEnabled = data['google_enabled'] == true;
    appleEnabled = data['apple_enabled'] == true;
    analyticsEnabled = data['analytics_enabled'] == true;
    loyaltyPointsPerOmr = int.tryParse(data['loyalty_points_per_omr']?.toString() ?? '') ?? 1;
    loyaltyRedeemValuePerPoint =
        double.tryParse(data['loyalty_redeem_value_per_point']?.toString() ?? '') ?? 0.01;
    bankTransferEnabled = data['bank_transfer_enabled'] != false;
    bankTransferBankName = (data['bank_transfer_bank_name'] ?? '').toString().trim();
    bankTransferAccountName = (data['bank_transfer_account_name'] ?? '').toString().trim();
    bankTransferAccountNumber = (data['bank_transfer_account_number'] ?? '').toString().trim();
    bankTransferIban = (data['bank_transfer_iban'] ?? '').toString().trim();
    bankTransferInstructions = (data['bank_transfer_instructions'] ?? '').toString().trim();
  }

  Future<void> fetchPaymentMethods() async {
    try {
      final res = await http.get(_uri('/api/payment-methods'), headers: _headers()).timeout(_networkTimeout);
      if (res.statusCode >= 200 && res.statusCode < 300) {
        final list = (jsonDecode(res.body) as List).cast<Map<String, dynamic>>();
        paymentMethods = list.map(PaymentMethod.fromJson).toList();
      }
    } catch (_) {}
    if (paymentMethods.isEmpty) {
      paymentMethods = [
        PaymentMethod(code: 'COD', label: 'Cash on delivery'),
        PaymentMethod(code: 'BANK', label: 'Bank transfer'),
      ];
    }
    _normalizePaymentMethods();
    if (!paymentMethods.any((m) => m.code == preferredPayment)) {
      preferredPayment = paymentMethods.first.code;
    }
    notifyListeners();
  }

  void _normalizePaymentMethods() {
    if (!bankTransferEnabled) {
      paymentMethods = paymentMethods.where((m) => m.code != 'BANK').toList();
    }
    if (paymentMethods.isEmpty) {
      paymentMethods = [PaymentMethod(code: 'COD', label: 'Cash on delivery')];
    }
  }

  Future<void> trackEvent(String name, {Map<String, dynamic>? payload}) async {
    if (!analyticsEnabled || !isLoggedIn) return;
    try {
      final res = await http.post(
        _uri('/api/analytics'),
        headers: _headers(auth: true),
        body: jsonEncode({'name': name, 'payload': payload ?? {}}),
      );
      if (res.statusCode == 401) {
        await _handleUnauthorized();
      }
    } catch (_) {}
  }

  Future<String?> loginRemote({required String username, required String password}) async {
    try {
      final res = await http.post(
        _uri('/api/auth/login'),
        headers: _headers(),
        body: jsonEncode({'username': username, 'password': password}),
      );
      final data = jsonDecode(res.body);
      if (res.statusCode >= 200 && res.statusCode < 300) {
        await persistAuth(
          access: data['tokens']['access'].toString(),
          refresh: data['tokens']['refresh'].toString(),
          name: (data['user']['first_name'] ?? data['user']['username'] ?? 'Customer').toString(),
          phoneNumber: username,
        );
        await fetchLaundries();
        await fetchOrders();
        await fetchNotifications();
        await trackEvent('login', payload: {'method': 'password'});
        return null;
      }
      return (data['detail'] ?? 'Login failed.').toString();
    } catch (_) {
      if (ApiConfig.enableDemoMode) {
        await login(name: username);
        return 'Could not reach the API. Opened in demo mode instead.';
      }
      return 'Could not reach the API. Check your connection and try again.';
    }
  }

  Future<String?> registerRemote({required String fullName, required String phoneNumber, required String email, required String password, String city = ''}) async {
    try {
      final res = await http.post(
        _uri('/api/auth/register'),
        headers: _headers(),
        body: jsonEncode({'full_name': fullName, 'phone': phoneNumber, 'email': email, 'password': password}),
      );
      final data = jsonDecode(res.body);
      if (res.statusCode >= 200 && res.statusCode < 300) {
        await persistAuth(
          access: data['tokens']['access'].toString(),
          refresh: data['tokens']['refresh'].toString(),
          name: (data['user']['first_name'] ?? fullName).toString(),
          phoneNumber: phoneNumber,
          city: city,
        );
        await trackEvent('register', payload: {'method': 'password'});
        return null;
      }
      return data.toString();
    } catch (_) {
      if (ApiConfig.enableDemoMode) {
        await login(name: fullName, city: city);
        phone = phoneNumber;
        return 'Could not reach the API. Opened in demo mode instead.';
      }
      return 'Could not reach the API. Check your connection and try again.';
    }
  }

  Future<String?> sendOtp(String phoneNumber) async {
    final normalizedPhone = normalizePhoneForOtp(phoneNumber);
    if (normalizedPhone == null) {
      return 'Enter a valid phone number for OTP login.';
    }
    try {
      final res = await http.post(
        _uri('/api/auth/otp/send'),
        headers: _headers(),
        body: jsonEncode({'phone': normalizedPhone, 'purpose': 'login'}),
      );
      final data = jsonDecode(res.body);
      if (res.statusCode >= 200 && res.statusCode < 300) {
        phone = normalizedPhone;
        lastOtpDebugCode = data['debug_code']?.toString();
        return null;
      }
      return (data['detail'] ?? 'Could not send OTP.').toString();
    } catch (_) {
      lastOtpDebugCode = null;
      return 'Could not reach the API. Please try again.';
    }
  }

  Future<String?> verifyOtp(String code) async {
    try {
      final res = await http.post(
        _uri('/api/auth/otp/verify'),
        headers: _headers(),
        body: jsonEncode({'phone': phone, 'purpose': 'login', 'code': code}),
      );
      final data = jsonDecode(res.body);
      if (res.statusCode >= 200 && res.statusCode < 300) {
        await persistAuth(
          access: data['tokens']['access'].toString(),
          refresh: data['tokens']['refresh'].toString(),
          name: (data['user']['first_name'] ?? data['user']['username'] ?? 'Customer').toString(),
          phoneNumber: phone,
        );
        await fetchNotifications();
        await trackEvent('login', payload: {'method': 'otp'});
        return null;
      }
      return (data['detail'] ?? 'Invalid code.').toString();
    } catch (_) {
      return 'Could not verify OTP.';
    }
  }

  Future<String?> socialLogin({required String provider, required String email, String fullName = ''}) async {
    if (provider == 'google' && !googleEnabled) return 'Google login is disabled.';
    if (provider == 'apple' && !appleEnabled) return 'Apple login is disabled.';
    try {
      final res = await http.post(
        _uri(provider == 'google' ? '/api/auth/google' : '/api/auth/apple'),
        headers: _headers(),
        body: jsonEncode({'provider': provider, 'email': email, 'full_name': fullName, 'id_token': ''}),
      );
      final data = jsonDecode(res.body);
      if (res.statusCode >= 200 && res.statusCode < 300) {
        await persistAuth(
          access: data['tokens']['access'].toString(),
          refresh: data['tokens']['refresh'].toString(),
          name: (data['user']['first_name'] ?? data['user']['username'] ?? 'Customer').toString(),
          phoneNumber: email,
        );
        await fetchLaundries();
        await fetchOrders();
        await fetchNotifications();
        await trackEvent('login', payload: {'method': provider});
        return null;
      }
      return (data['detail'] ?? 'Social login failed.').toString();
    } catch (_) {
      return 'Could not reach the API for social login.';
    }
  }

  Future<String?> sendResetOtp(String phoneNumber) async {
    final normalizedPhone = normalizePhoneForOtp(phoneNumber);
    if (normalizedPhone == null) {
      return 'Enter a valid phone number.';
    }
    try {
      final res = await http.post(
        _uri('/api/auth/forgot-password'),
        headers: _headers(),
        body: jsonEncode({'phone': normalizedPhone}),
      );
      final data = jsonDecode(res.body);
      if (res.statusCode >= 200 && res.statusCode < 300) {
        lastOtpDebugCode = data['debug_code']?.toString();
        return null;
      }
      return (data['detail'] ?? 'Could not send reset code.').toString();
    } catch (_) {
      lastOtpDebugCode = null;
      return 'Could not reach the API. Please try again.';
    }
  }

  Future<String?> resetPassword({required String phoneNumber, required String code, required String newPassword}) async {
    try {
      final res = await http.post(
        _uri('/api/auth/reset-password'),
        headers: _headers(),
        body: jsonEncode({'phone': phoneNumber, 'code': code, 'new_password': newPassword}),
      );
      if (res.statusCode >= 200 && res.statusCode < 300) {
        return null;
      }
      final data = jsonDecode(res.body);
      return (data['detail'] ?? 'Reset failed.').toString();
    } catch (_) {
      return 'Could not reset password.';
    }
  }

  String? normalizePhoneForOtp(String rawInput) {
    final trimmed = rawInput.trim();
    if (trimmed.isEmpty || trimmed.contains('@')) return null;
    final digits = trimmed.replaceAll(RegExp(r'\D'), '');
    if (digits.length == 8) {
      return '+968$digits';
    }
    if (digits.length == 11 && digits.startsWith('968')) {
      return '+$digits';
    }
    if (digits.length == 12 && digits.startsWith('00968')) {
      return '+${digits.substring(2)}';
    }
    if (trimmed.startsWith('+') && digits.length >= 8) {
      return '+$digits';
    }
    return null;
  }

  Future<void> fetchLaundries() async {
    laundriesLoading = true;
    notifyListeners();
    try {
      final res = await http.get(_uri('/api/laundries'), headers: _headers()).timeout(_networkTimeout);
      if (res.statusCode >= 200 && res.statusCode < 300) {
        final decoded = jsonDecode(res.body);
        final rawList = decoded is List
            ? decoded
            : ((decoded is Map<String, dynamic>) ? (decoded['results'] ?? const []) : const []);
        final list = <Map<String, dynamic>>[];
        if (rawList is List) {
          for (final row in rawList) {
            if (row is Map) {
              list.add(Map<String, dynamic>.from(row));
            }
          }
        }
        laundries = list.map(Laundry.fromJson).toList();
      } else {
        laundries = [];
      }
    } catch (_) {
      laundries = [];
    }
    laundriesLoading = false;
    final normalizedSelected = selectedCity.trim().toLowerCase();
    final hasSelectedInList = laundries.any((laundry) => laundry.city.trim().toLowerCase() == normalizedSelected);
    if (selectedCity.trim().isEmpty || (!hasSelectedInList && laundries.isNotEmpty)) {
      final salalah = laundries.where((laundry) => laundry.city.trim().toLowerCase() == 'salalah').toList();
      selectedCity = (salalah.isNotEmpty ? salalah.first.city : laundries.first.city).trim();
    }
    if (selectedCity.isNotEmpty && !availableCities.contains(selectedCity)) {
      selectedCity = selectedCity.trim();
    }
    // Normalize selected branch against fresh API list to avoid stale fallback ids.
    if (laundries.isNotEmpty) {
      final hasSelectedId = selectedLaundryId != null && laundries.any((l) => l.id == selectedLaundryId);
      if (!hasSelectedId) {
        final byCity = laundries.where((l) => l.city.trim().toLowerCase() == selectedCity.trim().toLowerCase()).toList();
        final picked = byCity.isNotEmpty ? byCity.first : laundries.first;
        selectedLaundryId = picked.id;
        selectedLaundryName = picked.name;
      }
    }
    final prefs = await SharedPreferences.getInstance();
    if (selectedCity.isEmpty) {
      await prefs.remove(_selectedCityKey);
    } else {
      await prefs.setString(_selectedCityKey, selectedCity);
    }
    notifyListeners();
  }

  Future<void> fetchCatalog(int laundryId) async {
    if (selectedLaundryId != null && selectedLaundryId != laundryId && cart.isNotEmpty) {
      cart.clear();
      _persistCart();
    }
    selectedLaundryId = laundryId;
    _catalogLaundryId = laundryId;
    catalogLoading = true;
    catalogUsingFallback = false;
    notifyListeners();
    try {
      final res = await http.get(_uri('/api/laundries/$laundryId/catalog'), headers: _headers()).timeout(_networkTimeout);
      if (res.statusCode >= 200 && res.statusCode < 300) {
        final decoded = jsonDecode(res.body);
        final rawList = decoded is List
            ? decoded
            : ((decoded is Map<String, dynamic>) ? (decoded['results'] ?? const []) : const []);
        final list = <Map<String, dynamic>>[];
        if (rawList is List) {
          for (final row in rawList) {
            if (row is Map) {
              list.add(Map<String, dynamic>.from(row));
            }
          }
        }
        catalog = list.map(CatalogItem.fromJson).toList();
        _catalogCacheByLaundry[laundryId] = List<CatalogItem>.from(catalog);
      } else {
        // If catalog failed for a fallback/stale laundry id, resolve real branch id and retry once.
        if (!_retryingCatalogResolve) {
          _retryingCatalogResolve = true;
          await fetchLaundries();
          final byExactName = laundries.where((l) => l.name.trim().toLowerCase() == selectedLaundryName.trim().toLowerCase()).toList();
          final byCity = laundries.where((l) => l.city.trim().toLowerCase() == selectedCity.trim().toLowerCase()).toList();
          final resolved = byExactName.isNotEmpty ? byExactName.first : (byCity.isNotEmpty ? byCity.first : (laundries.isNotEmpty ? laundries.first : null));
          if (resolved != null && resolved.id != laundryId) {
            selectedLaundryId = resolved.id;
            selectedLaundryName = resolved.name;
            _catalogLaundryId = resolved.id;
            _retryingCatalogResolve = false;
            await fetchCatalog(resolved.id);
            return;
          }
          _retryingCatalogResolve = false;
        }
        final cached = _catalogCacheByLaundry[laundryId];
        if (cached != null && cached.isNotEmpty) {
          catalog = List<CatalogItem>.from(cached);
        } else {
          // Avoid sending invalid demo rows to live APIs for logged-in users.
          catalog = !isLoggedIn && ApiConfig.enableDemoMode
              ? List<CatalogItem>.from(_fallbackCatalog)
              : <CatalogItem>[];
          catalogUsingFallback = ApiConfig.enableDemoMode && !isLoggedIn;
        }
      }
    } catch (_) {
      final cached = _catalogCacheByLaundry[laundryId];
      if (cached != null && cached.isNotEmpty) {
        catalog = List<CatalogItem>.from(cached);
      } else {
        catalog = !isLoggedIn && ApiConfig.enableDemoMode
            ? List<CatalogItem>.from(_fallbackCatalog)
            : <CatalogItem>[];
        catalogUsingFallback = ApiConfig.enableDemoMode && !isLoggedIn;
      }
    }
    catalogLoading = false;
    notifyListeners();
  }

  void setSelectedLaundry(Laundry laundry) {
    if (selectedLaundryId != null && selectedLaundryId != laundry.id && cart.isNotEmpty) {
      cart.clear();
      _persistCart();
    }
    selectedLaundryId = laundry.id;
    selectedLaundryName = laundry.name;
    notifyListeners();
  }

  void addToCart(int itemId) {
    cart[itemId] = (cart[itemId] ?? 0) + 1;
    _persistCart();
    notifyListeners();
  }

  void removeFromCart(int itemId) {
    if (!cart.containsKey(itemId)) return;
    final next = (cart[itemId] ?? 0) - 1;
    if (next <= 0) {
      cart.remove(itemId);
    } else {
      cart[itemId] = next;
    }
    _persistCart();
    notifyListeners();
  }

  double get subtotal {
    double total = 0;
    for (final entry in cart.entries) {
      final matches = catalog.where((e) => e.id == entry.key);
      if (matches.isEmpty) continue;
      total += matches.first.price * entry.value;
    }
    return total;
  }

  Future<int?> _ensureSelectedLaundryId() async {
    if (laundries.isEmpty) {
      await fetchLaundries();
    }
    if (selectedLaundryId != null) {
      final exists = laundries.any((l) => l.id == selectedLaundryId);
      if (exists) return selectedLaundryId;
    }
    if (laundries.isEmpty) return null;
    final normalizedCity = selectedCity.trim().toLowerCase();
    final match = laundries.where((l) => l.city.trim().toLowerCase() == normalizedCity).toList();
    final picked = match.isNotEmpty ? match.first : laundries.first;
    selectedLaundryId = picked.id;
    selectedLaundryName = picked.name;
    notifyListeners();
    return selectedLaundryId;
  }

  List<Map<String, dynamic>> _buildValidOrderLines() {
    final lines = <Map<String, dynamic>>[];
    final staleKeys = <int>[];
    final byItemId = <int, CatalogItem>{};
    for (final item in catalog) {
      byItemId.putIfAbsent(item.id, () => item);
    }
    for (final entry in cart.entries) {
      final item = byItemId[entry.key];
      if (item == null || entry.value <= 0) {
        staleKeys.add(entry.key);
        continue;
      }
      lines.add({'item_id': item.itemId, 'service_id': item.serviceId, 'qty': entry.value});
    }
    if (staleKeys.isNotEmpty) {
      for (final key in staleKeys) {
        cart.remove(key);
      }
      _persistCart();
      notifyListeners();
    }
    return lines;
  }

  Future<List<Map<String, dynamic>>> _buildValidOrderLinesForLaundry(int laundryId) async {
    if (_catalogLaundryId != laundryId || catalog.isEmpty) {
      await fetchCatalog(laundryId);
    }
    return _buildValidOrderLines();
  }

  Future<void> fetchAddresses() async {
    if (!isLoggedIn) return;
    addressesLoading = true;
    notifyListeners();
    try {
      final res = await http.get(_uri('/api/addresses'), headers: _headers(auth: true)).timeout(_networkTimeout);
      if (res.statusCode == 401) {
        await _handleUnauthorized();
        addressesLoading = false;
        notifyListeners();
        return;
      }
      if (res.statusCode >= 200 && res.statusCode < 300) {
        final list = (jsonDecode(res.body) as List).cast<Map<String, dynamic>>();
        addresses = list.map(AddressModel.fromJson).toList();
      }
    } catch (_) {}
    if (addresses.isEmpty) {
      addresses = [AddressModel(id: 1, label: 'Home', line1: 'Awqad, Salalah', line2: 'Street 23, Villa 12', isDefault: true)];
    }
    addressesLoading = false;
    notifyListeners();
  }

  Future<String?> addAddressRemote({
    required String label,
    required String area,
    required String city,
    required String details,
    required bool isDefault,
    double? latitude,
    double? longitude,
  }) async {
    final payload = {
      'label': label,
      'city': city,
      'area': area,
      'address_line_1': details,
      'address_line_2': '',
      'is_default': isDefault,
      'latitude': latitude,
      'longitude': longitude,
    };
    if (!isLoggedIn) {
      addresses.add(AddressModel(
        id: addresses.length + 1,
        label: label,
        line1: '$details, $area, $city',
        line2: '',
        isDefault: isDefault,
        latitude: latitude,
        longitude: longitude,
      ));
      notifyListeners();
      return 'Saved locally in demo mode.';
    }
    try {
      final res = await http.post(_uri('/api/addresses'), headers: _headers(auth: true), body: jsonEncode(payload));
      if (res.statusCode == 401) {
        await _handleUnauthorized();
        return 'Session expired. Please login again.';
      }
      if (res.statusCode >= 200 && res.statusCode < 300) {
        await fetchAddresses();
        return null;
      }
      return res.body;
    } catch (_) {
      addresses.add(AddressModel(
        id: addresses.length + 1,
        label: label,
        line1: '$details, $area, $city',
        line2: '',
        isDefault: isDefault,
        latitude: latitude,
        longitude: longitude,
      ));
      notifyListeners();
      return 'Could not reach the API. Saved locally instead.';
    }
  }

  Future<String?> updateAddressRemote({
    required int addressId,
    required String label,
    required String area,
    required String city,
    required String details,
    required bool isDefault,
    double? latitude,
    double? longitude,
  }) async {
    final payload = {
      'label': label,
      'city': city,
      'area': area,
      'address_line_1': details,
      'address_line_2': '',
      'is_default': isDefault,
      'latitude': latitude,
      'longitude': longitude,
    };

    if (!isLoggedIn) {
      addresses = addresses.map((a) {
        if (a.id != addressId) return a;
        return AddressModel(
          id: a.id,
          label: label,
          line1: '$details, $area, $city',
          line2: '',
          isDefault: isDefault,
          city: city,
          area: area,
          addressLine1: details,
          addressLine2: '',
          latitude: latitude,
          longitude: longitude,
        );
      }).toList();
      if (isDefault) {
        addresses = addresses
            .map((a) => AddressModel(
                  id: a.id,
                  label: a.label,
                  line1: a.line1,
                  line2: a.line2,
                  isDefault: a.id == addressId,
                  city: a.city,
                  area: a.area,
                  addressLine1: a.addressLine1,
                  addressLine2: a.addressLine2,
                  latitude: a.latitude,
                  longitude: a.longitude,
                ))
            .toList();
      }
      notifyListeners();
      return 'Updated locally in demo mode.';
    }

    try {
      final res = await http.put(
        _uri('/api/addresses/$addressId'),
        headers: _headers(auth: true),
        body: jsonEncode(payload),
      ).timeout(_networkTimeout);
      if (res.statusCode == 401) {
        await _handleUnauthorized();
        return 'Session expired. Please login again.';
      }
      if (res.statusCode >= 200 && res.statusCode < 300) {
        await fetchAddresses();
        return null;
      }
      final data = jsonDecode(res.body);
      return (data['detail'] ?? 'Could not update address.').toString();
    } catch (_) {
      return 'Could not reach the API.';
    }
  }

  Future<String?> deleteAddressRemote(int addressId) async {
    if (!isLoggedIn) {
      addresses.removeWhere((a) => a.id == addressId);
      if (addresses.isNotEmpty && !addresses.any((a) => a.isDefault)) {
        final first = addresses.first;
        addresses = addresses
            .map((a) => AddressModel(
                  id: a.id,
                  label: a.label,
                  line1: a.line1,
                  line2: a.line2,
                  isDefault: a.id == first.id,
                  city: a.city,
                  area: a.area,
                  addressLine1: a.addressLine1,
                  addressLine2: a.addressLine2,
                  latitude: a.latitude,
                  longitude: a.longitude,
                ))
            .toList();
      }
      notifyListeners();
      return null;
    }

    try {
      final res = await http.delete(
        _uri('/api/addresses/$addressId'),
        headers: _headers(auth: true),
      ).timeout(_networkTimeout);
      if (res.statusCode == 401) {
        await _handleUnauthorized();
        return 'Session expired. Please login again.';
      }
      if (res.statusCode == 204 || (res.statusCode >= 200 && res.statusCode < 300)) {
        await fetchAddresses();
        return null;
      }
      final data = jsonDecode(res.body);
      return (data['detail'] ?? 'Could not delete address.').toString();
    } catch (_) {
      return 'Could not reach the API.';
    }
  }

  Future<void> fetchOrders() async {
    if (!isLoggedIn) return;
    ordersLoading = true;
    notifyListeners();
    try {
      final res = await http.get(_uri('/api/orders'), headers: _headers(auth: true)).timeout(_networkTimeout);
      if (res.statusCode == 401) {
        await _handleUnauthorized();
        ordersLoading = false;
        notifyListeners();
        return;
      }
      if (res.statusCode >= 200 && res.statusCode < 300) {
        final list = (jsonDecode(res.body) as List).cast<Map<String, dynamic>>();
        orders = list.map(OrderModel.fromJson).toList();
      }
    } catch (_) {}
    ordersLoading = false;
    notifyListeners();
  }

  Future<Map<String, dynamic>?> pricePreview({
    required bool urgent,
    required double promoDiscount,
    required int pointsUsed,
  }) async {
    if (!isLoggedIn) return null;
    final laundryId = await _ensureSelectedLaundryId();
    if (laundryId == null) return null;
    final lines = await _buildValidOrderLinesForLaundry(laundryId);
    if (lines.isEmpty) return null;
    try {
      final res = await http.post(
        _uri('/api/orders/price-preview'),
        headers: _headers(),
        body: jsonEncode({
          'laundry_shop_id': laundryId,
          'speed': urgent ? 'URGENT' : 'NORMAL',
          'promo_discount': promoDiscount,
          'points_used': pointsUsed,
          'lines': lines,
        }),
      );
      if (res.statusCode == 401) {
        await _handleUnauthorized();
        return null;
      }
      if (res.statusCode >= 200 && res.statusCode < 300) {
        return (jsonDecode(res.body) as Map<String, dynamic>);
      }
    } catch (_) {}
    return null;
  }

  Future<String?> cancelOrder(int orderId) async {
    if (!isLoggedIn) return 'Not logged in.';
    try {
      final res = await http.post(_uri('/api/orders/$orderId/cancel'), headers: _headers(auth: true));
      if (res.statusCode == 401) {
        await _handleUnauthorized();
        return 'Session expired. Please login again.';
      }
      if (res.statusCode >= 200 && res.statusCode < 300) {
        await fetchOrders();
        return null;
      }
      final data = jsonDecode(res.body);
      return (data['detail'] ?? 'Could not cancel order.').toString();
    } catch (_) {
      return 'Could not reach the API.';
    }
  }

  Future<String?> placeOrderRemote({
    required bool urgent,
    required String paymentMethod,
    required int? addressId,
    String fulfillmentMode = 'DELIVERY',
    String timeSlot = '10:00 AM - 12:00 PM',
    String notes = '',
    String bankReference = '',
    String? receiptName,
  }) async {
    final laundryId = await _ensureSelectedLaundryId();
    if (laundryId == null) {
      return 'No laundry branch selected.';
    }
    final lines = await _buildValidOrderLinesForLaundry(laundryId);
    if (lines.isEmpty) return 'Your cart is empty.';
    final receiptLines = _snapshotReceiptLines();
    if (!isLoggedIn) {
      placeOrder(
        selectedLaundryName,
        urgent,
        receiptLines: receiptLines,
        paymentMethod: paymentMethod,
        bankReference: bankReference,
        fulfillmentMode: fulfillmentMode,
        timeSlot: timeSlot,
        notes: notes,
      );
      return 'Order placed in demo mode.';
    }
    try {
      await _saveLastOrder();
      final subtotalValue = subtotal;
      final double urgentFee = urgent ? 1.5 : 0.0;
      final promoDiscount = promoDiscountAmount(subtotalValue);
      final double pointsDiscount = redeemablePointsValue(subtotalValue + urgentFee - promoDiscount);
      final res = await http.post(
        _uri('/api/orders'),
        headers: _headers(auth: true),
        body: jsonEncode({
          'laundry_shop_id': laundryId,
          'address_id': addressId,
          'speed': urgent ? 'URGENT' : 'NORMAL',
          'payment_method': _normalizePaymentMethod(paymentMethod),
          'pickup_time_slot': timeSlot,
          'fulfillment_mode': fulfillmentMode,
          'customer_notes': notes,
          'promo_code': promoCode,
          'promo_discount': promoDiscount,
          'points_used': usePoints ? loyaltyPoints : 0,
          'transfer_reference': bankReference,
          'receipt_name': receiptName ?? '',
          'lines': lines,
        }),
      );
      if (res.statusCode == 401) {
        await _handleUnauthorized();
        return 'Session expired. Please login again.';
      }
      if (res.statusCode >= 200 && res.statusCode < 300) {
        final data = jsonDecode(res.body) as Map<String, dynamic>;
        final order = OrderModel.fromJson(data);
        orders.insert(0, order);
        final subtotalApi = double.tryParse(data['subtotal'].toString()) ?? subtotalValue;
        final taxApi = double.tryParse(data['tax'].toString()) ?? 0;
        final totalApi = double.tryParse(data['total'].toString()) ?? (subtotalValue + urgentFee - promoDiscount - pointsDiscount);
        lastReceipt = ReceiptData(
          orderNo: order.code,
          placedAt: (data['created_at'] ?? DateTime.now().toIso8601String()).toString(),
          laundryName: selectedLaundryName,
          paymentMethod: paymentMethod,
          fulfillmentMode: fulfillmentMode,
          timeSlot: timeSlot,
          notes: notes,
          subtotal: subtotalApi,
          urgentFee: urgentFee,
          promoDiscount: promoDiscount,
          pointsDiscount: pointsDiscount,
          tax: taxApi,
          total: totalApi,
          lines: receiptLines,
        );
        cart.clear();
        _persistCart();
        _applyLoyalty(
          subtotalValue + urgentFee - promoDiscount - pointsDiscount,
          redeemedValue: pointsDiscount,
          earnPoints: false,
        );
        notifyListeners();
        await trackEvent('order_placed', payload: {'payment': paymentMethod, 'urgent': urgent});
        return null;
      }
      try {
        final data = jsonDecode(res.body);
        final detail = (data['detail'] ?? '').toString();
        if (detail.toLowerCase().contains('not available for this branch')) {
          await fetchCatalog(laundryId);
          _buildValidOrderLines();
          return 'Some items are no longer available for this branch. Please review your cart.';
        }
        return detail.isEmpty ? res.body : detail;
      } catch (_) {
        return res.body;
      }
    } catch (_) {
      placeOrder(
        selectedLaundryName,
        urgent,
        receiptLines: receiptLines,
        paymentMethod: paymentMethod,
        fulfillmentMode: fulfillmentMode,
        timeSlot: timeSlot,
        notes: notes,
      );
      return 'Could not reach the API. Order saved in demo mode.';
    }
  }

  String _normalizePaymentMethod(String method) {
    if (method == 'BANK') return 'BANK_TRANSFER';
    if (method == 'CARD' || method == 'APPLE_PAY' || method == 'GOOGLE_PAY') return method;
    return 'COD';
  }

  void placeOrder(
    String laundryName,
    bool urgent, {
    List<ReceiptLine>? receiptLines,
    String paymentMethod = 'COD',
    String bankReference = '',
    String fulfillmentMode = 'DELIVERY',
    String timeSlot = '10:00 AM - 12:00 PM',
    String notes = '',
  }) {
    _saveLastOrder();
    final subtotalValue = subtotal;
    final double urgentFee = urgent ? 1.5 : 0.0;
    final promoDiscount = promoDiscountAmount(subtotalValue);
    final double pointsDiscount = redeemablePointsValue(subtotalValue + urgentFee - promoDiscount);
    final total = (subtotalValue + urgentFee - promoDiscount - pointsDiscount).clamp(0, double.infinity).toDouble();
    final orderCode = 'LDX-${1200 + orders.length + 1}';
    orders.insert(
      0,
      OrderModel(
        code: orderCode,
        status: 'RECEIVED',
        laundryName: laundryName,
        amount: 'OMR ${total.toStringAsFixed(3)}',
        placedAt: '$fulfillmentMode - $timeSlot',
      ),
    );
    lastReceipt = ReceiptData(
      orderNo: orderCode,
      placedAt: DateTime.now().toIso8601String(),
      laundryName: laundryName,
      paymentMethod: paymentMethod,
      fulfillmentMode: fulfillmentMode,
      timeSlot: timeSlot,
      notes: notes,
      subtotal: subtotalValue,
      urgentFee: urgentFee,
      promoDiscount: promoDiscount,
      pointsDiscount: pointsDiscount,
      tax: 0,
      total: total,
      lines: receiptLines ?? _snapshotReceiptLines(),
    );
    cart.clear();
    _persistCart();
    _applyLoyalty(total, redeemedValue: pointsDiscount);
    notifyListeners();
  }

  List<ReceiptLine> _snapshotReceiptLines() {
    final rows = <ReceiptLine>[];
    for (final entry in cart.entries) {
      final item = catalog.cast<CatalogItem?>().firstWhere(
            (c) => c?.id == entry.key,
            orElse: () => null,
          );
      if (item == null) continue;
      rows.add(
        ReceiptLine(
          itemName: item.name,
          serviceName: item.serviceName,
          qty: entry.value,
          unitPrice: item.price,
          lineTotal: item.price * entry.value,
        ),
      );
    }
    return rows;
  }

  Future<void> _persistCart() async {
    final prefs = await SharedPreferences.getInstance();
    final payload = cart.entries.map((e) => {'id': e.key, 'qty': e.value}).toList();
    await prefs.setString(_cartKey, jsonEncode(payload));
  }

  void _restoreCart(String? raw) {
    if (raw == null || raw.isEmpty) return;
    try {
      final list = (jsonDecode(raw) as List).cast<Map<String, dynamic>>();
      cart.clear();
      for (final entry in list) {
        final id = (entry['id'] as num).toInt();
        final qty = (entry['qty'] as num).toInt();
        if (qty > 0) cart[id] = qty;
      }
    } catch (_) {}
  }

  Future<void> _saveLastOrder() async {
    _lastOrderCart
      ..clear()
      ..addAll(cart);
    final prefs = await SharedPreferences.getInstance();
    final payload = _lastOrderCart.entries.map((e) => {'id': e.key, 'qty': e.value}).toList();
    await prefs.setString(_lastOrderKey, jsonEncode(payload));
  }

  void _restoreLastOrder(String? raw) {
    if (raw == null || raw.isEmpty) return;
    try {
      final list = (jsonDecode(raw) as List).cast<Map<String, dynamic>>();
      _lastOrderCart.clear();
      for (final entry in list) {
        final id = (entry['id'] as num).toInt();
        final qty = (entry['qty'] as num).toInt();
        if (qty > 0) _lastOrderCart[id] = qty;
      }
    } catch (_) {}
  }

  bool reorderLastOrder() {
    if (_lastOrderCart.isEmpty) return false;
    cart
      ..clear()
      ..addAll(_lastOrderCart);
    _persistCart();
    notifyListeners();
    return true;
  }

  bool get hasLastOrder => _lastOrderCart.isNotEmpty;

  Future<void> _applyLoyalty(
    double total, {
    double redeemedValue = 0,
    bool earnPoints = true,
  }) async {
    if (usePoints && redeemedValue > 0 && loyaltyRedeemValuePerPoint > 0) {
      final pointsUsed = (redeemedValue / loyaltyRedeemValuePerPoint).round();
      loyaltyPoints = (loyaltyPoints - pointsUsed).clamp(0, loyaltyPoints);
      usePoints = false;
    }
    if (earnPoints) {
      final earned = (total * loyaltyPointsPerOmr).floor();
      if (earned > 0) loyaltyPoints += earned;
    }
    final prefs = await SharedPreferences.getInstance();
    await prefs.setInt(_loyaltyPointsKey, loyaltyPoints);
    await prefs.setBool(_usePointsKey, usePoints);
  }

  List<TrackingEvent> getTracking(String orderCode, String status) {
    final flow = [
      'RECEIVED',
      'ACCEPTED',
      'PICKUP_ASSIGNED',
      'PICKED_UP',
      'WASHING',
      'IRONING',
      'READY',
      'OUT_FOR_DELIVERY',
      'DELIVERED'
    ];
    final normalized = _normalizeTrackingStatus(status);
    final currentIndex = flow.indexOf(normalized);
    final base = DateTime.now();
    final events = <TrackingEvent>[];
    for (var i = 0; i < flow.length; i++) {
      final label = _labelForStatus(flow[i]);
      final done = i <= (currentIndex < 0 ? 0 : currentIndex);
      events.add(TrackingEvent(
        status: flow[i],
        label: label,
        time: done ? base.subtract(Duration(hours: (flow.length - i) * 2)) : null,
        completed: done,
      ));
    }
    return events;
  }

  String getEtaLabel(String status) {
    final normalized = _normalizeTrackingStatus(status);
    if (normalized == 'DELIVERED') return 'Delivered';
    if (normalized == 'OUT_FOR_DELIVERY') return 'Out for delivery';
    if (normalized == 'READY') return 'Pickup ready';
    if (normalized == 'PICKUP_ASSIGNED') return 'Pickup assigned';
    return 'Estimated: 2-4 hours';
  }

  String _normalizeTrackingStatus(String status) {
    final normalized = status.toUpperCase().trim();
    if (normalized == 'CONFIRMED') return 'ACCEPTED';
    if (normalized == 'OUT') return 'OUT_FOR_DELIVERY';
    if (normalized == 'PICKUP_ASSIGN' || normalized == 'ASSIGNED') return 'PICKUP_ASSIGNED';
    return normalized;
  }

  String _labelForStatus(String status) {
    switch (status) {
      case 'ACCEPTED':
        return 'Accepted by laundry';
      case 'PICKUP_ASSIGNED':
        return 'Pickup assigned';
      case 'PICKED_UP':
        return 'Picked up';
      case 'WASHING':
        return 'Washing';
      case 'IRONING':
        return 'Ironing';
      case 'READY':
        return 'Ready';
      case 'OUT_FOR_DELIVERY':
        return 'Out for delivery';
      case 'DELIVERED':
        return 'Delivered';
      default:
        return 'Received';
    }
  }

  Future<TrackingSnapshot> fetchOrderTracking({
    required int? orderId,
    required String orderCode,
    required String fallbackStatus,
  }) async {
    var status = fallbackStatus;
    var eta = getEtaLabel(status);
    final events = getTracking(orderCode, status);

    if (!isLoggedIn || orderId == null) {
      return TrackingSnapshot(status: status, eta: eta, events: events);
    }

    try {
      final res = await http.get(_uri('/api/orders/$orderId/tracking'), headers: _headers(auth: true)).timeout(_networkTimeout);
      if (res.statusCode == 401) {
        await _handleUnauthorized();
        return TrackingSnapshot(status: status, eta: eta, events: events);
      }
      if (res.statusCode < 200 || res.statusCode >= 300) {
        return TrackingSnapshot(status: status, eta: eta, events: events);
      }
      final data = jsonDecode(res.body) as Map<String, dynamic>;
      status = (data['status'] ?? fallbackStatus).toString();
      eta = getEtaLabel(status);
      final normalizedStatus = _normalizeTrackingStatus(status);
      var didUpdateOrder = false;
      orders = orders.map((order) {
        final sameOrder = order.id == orderId || order.code == orderCode;
        if (!sameOrder || order.status == normalizedStatus) {
          return order;
        }
        didUpdateOrder = true;
        return OrderModel(
          id: order.id,
          code: order.code,
          status: normalizedStatus,
          laundryName: order.laundryName,
          amount: order.amount,
          placedAt: order.placedAt,
        );
      }).toList();
      if (didUpdateOrder) {
        notifyListeners();
      }
      final baseEvents = getTracking(orderCode, normalizedStatus);
      final logs = (data['timeline'] as List? ?? const []).cast<Map<String, dynamic>>();
      final timeByStatus = <String, DateTime>{};
      for (final log in logs) {
        final toStatus = _normalizeTrackingStatus((log['to_status'] ?? '').toString());
        final created = DateTime.tryParse((log['created_at'] ?? '').toString());
        if (toStatus.isEmpty || created == null) continue;
        timeByStatus[toStatus] = created.toLocal();
      }

      final merged = baseEvents.map((event) {
        final trackedTime = timeByStatus[event.status];
        return TrackingEvent(
          status: event.status,
          label: event.label,
          completed: event.completed,
          time: trackedTime ?? event.time,
        );
      }).toList();

      return TrackingSnapshot(status: status, eta: eta, events: merged);
    } catch (_) {
      return TrackingSnapshot(status: status, eta: eta, events: events);
    }
  }
}

class TrackingEvent {
  TrackingEvent({
    required this.status,
    required this.label,
    required this.completed,
    this.time,
  });

  final String status;
  final String label;
  final bool completed;
  final DateTime? time;
}

class TrackingSnapshot {
  TrackingSnapshot({
    required this.status,
    required this.eta,
    required this.events,
  });

  final String status;
  final String eta;
  final List<TrackingEvent> events;
}

