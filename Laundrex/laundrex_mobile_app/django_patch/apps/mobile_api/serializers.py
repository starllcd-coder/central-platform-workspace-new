from decimal import Decimal

from django.contrib.auth.models import User
from rest_framework import serializers

from apps.catalog.models import BranchItemServicePrice
from apps.management.models import Branch
from apps.orders.models import Customer, Order, OrderItem, OrderStatusLog
from apps.payments.models import Payment
from .models import CustomerAccount, SavedAddress, MobileOrderMeta


class BranchSerializer(serializers.ModelSerializer):
    city = serializers.SerializerMethodField()
    area = serializers.SerializerMethodField()
    address = serializers.CharField(source="address")
    supports_urgent = serializers.SerializerMethodField()

    class Meta:
        model = Branch
        fields = ["id", "code", "name", "name_ar", "phone", "address", "city", "area", "tax_rate", "supports_urgent"]

    def get_city(self, obj):
        return "Oman"

    def get_area(self, obj):
        return obj.address or obj.name

    def get_supports_urgent(self, obj):
        return True


class CatalogRowSerializer(serializers.ModelSerializer):
    item_id = serializers.IntegerField(source="item.id")
    item_name = serializers.CharField(source="item.name")
    service_id = serializers.IntegerField(source="service.id")
    service_name = serializers.CharField(source="service.name")

    class Meta:
        model = BranchItemServicePrice
        fields = ["id", "item_id", "item_name", "service_id", "service_name", "price"]


class SavedAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedAddress
        fields = [
            "id", "label", "city", "area", "address_line_1", "address_line_2", "building", "is_default",
            "latitude", "longitude",
            "created_at", "updated_at",
        ]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "email"]


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ["id", "name", "phone", "vip", "points", "preferred_language"]


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ["id", "item_name", "service_name", "qty", "price", "line_total"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    promo_code = serializers.SerializerMethodField()
    promo_discount = serializers.SerializerMethodField()
    points_used = serializers.SerializerMethodField()
    payment_method = serializers.SerializerMethodField()
    transfer_reference = serializers.SerializerMethodField()
    receipt_name = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            "id", "order_no", "branch", "status", "urgent", "subtotal", "discount", "tax", "total",
            "paid", "balance", "delivery_required", "delivery_status", "delivery_address", "delivery_phone",
            "delivery_slot", "delivery_fee", "delivery_driver_name", "delivery_driver_phone", "delivery_notes",
            "notes", "created_at", "updated_at", "items",
            "promo_code", "promo_discount", "points_used", "payment_method", "transfer_reference", "receipt_name",
        ]

    def _meta(self, obj):
        return getattr(obj, "mobile_meta", None)

    def get_promo_code(self, obj):
        meta = self._meta(obj)
        return meta.promo_code if meta else ""

    def get_promo_discount(self, obj):
        meta = self._meta(obj)
        return meta.promo_discount if meta else 0

    def get_points_used(self, obj):
        meta = self._meta(obj)
        return meta.points_used if meta else 0

    def get_payment_method(self, obj):
        meta = self._meta(obj)
        return meta.payment_method if meta else ""

    def get_transfer_reference(self, obj):
        meta = self._meta(obj)
        return meta.transfer_reference if meta else ""

    def get_receipt_name(self, obj):
        meta = self._meta(obj)
        return meta.receipt_name if meta else ""


class OrderTrackingLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderStatusLog
        fields = ["id", "from_status", "to_status", "note", "created_at"]


class RegisterSerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=120)
    phone = serializers.CharField(max_length=40)
    email = serializers.EmailField(required=False, allow_blank=True)
    password = serializers.CharField(min_length=6)


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


class OtpSendSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=40)
    purpose = serializers.ChoiceField(choices=["login", "register"], default="login")


class OtpVerifySerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=40)
    code = serializers.CharField(max_length=6)
    purpose = serializers.ChoiceField(choices=["login", "register"], default="login")


class OrderCreateLineSerializer(serializers.Serializer):
    item_id = serializers.IntegerField()
    service_id = serializers.IntegerField()
    qty = serializers.IntegerField(min_value=1)


class OrderCreateSerializer(serializers.Serializer):
    laundry_id = serializers.IntegerField(required=False)
    laundry_shop_id = serializers.IntegerField(required=False)
    items = OrderCreateLineSerializer(many=True, required=False)
    lines = OrderCreateLineSerializer(many=True, required=False)
    urgent = serializers.BooleanField(default=False)
    speed = serializers.CharField(required=False, allow_blank=True)
    payment_method = serializers.ChoiceField(choices=["COD", "BANK", "BANK_TRANSFER"], default="COD")
    address_id = serializers.IntegerField(required=False, allow_null=True)
    delivery_slot = serializers.CharField(required=False, allow_blank=True)
    pickup_time_slot = serializers.CharField(required=False, allow_blank=True)
    notes = serializers.CharField(required=False, allow_blank=True)
    customer_notes = serializers.CharField(required=False, allow_blank=True)
    promo_code = serializers.CharField(required=False, allow_blank=True)
    promo_discount = serializers.DecimalField(required=False, max_digits=10, decimal_places=3)
    points_used = serializers.IntegerField(required=False)
    transfer_reference = serializers.CharField(required=False, allow_blank=True)
    receipt_name = serializers.CharField(required=False, allow_blank=True)

    def validate_laundry_id(self, value):
        if not Branch.objects.filter(id=value, active=True).exists():
            raise serializers.ValidationError("Invalid laundry branch.")
        return value

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("At least one item is required.")
        return value

    def validate(self, data):
        laundry_id = data.get("laundry_id") or data.get("laundry_shop_id")
        items = data.get("items") or data.get("lines")
        if not laundry_id:
            raise serializers.ValidationError("Laundry ID is required.")
        if not items:
            raise serializers.ValidationError("At least one item is required.")
        return data
