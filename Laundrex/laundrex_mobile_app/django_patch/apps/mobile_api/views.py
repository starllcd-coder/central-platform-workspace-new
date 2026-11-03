import random
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from apps.catalog.models import BranchItemServicePrice
from apps.management.models import Branch
from apps.orders.models import Customer, Order, OrderItem, OrderStatusLog
from apps.payments.models import Payment
from .models import CustomerAccount, SavedAddress, PhoneOTP, DeviceToken, MobileOrderMeta
from .serializers import (
    BranchSerializer, CatalogRowSerializer, LoginSerializer, OtpSendSerializer, OtpVerifySerializer,
    OrderCreateSerializer, OrderSerializer, OrderTrackingLogSerializer, RegisterSerializer,
    SavedAddressSerializer, UserSerializer,
)


class AllowAnyPost(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.method == "POST" or request.user and request.user.is_authenticated


def _tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {"refresh": str(refresh), "access": str(refresh.access_token)}


def _customer_from_request(request):
    account = getattr(request.user, "customer_account", None)
    return account.customer if account else None


def _next_order_no():
    last = Order.objects.order_by("-id").first()
    if not last:
        return "1001"
    try:
        return str(int(last.order_no) + 1)
    except Exception:
        return str(last.id + 1001)


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        phone = data["phone"].strip()
        email = data.get("email", "").strip()
        full_name = data["full_name"].strip()

        if CustomerAccount.objects.filter(phone=phone).exists():
            return Response({"detail": "An account with this phone already exists."}, status=400)

        username_base = phone.replace("+", "").replace(" ", "") or f"cust{random.randint(1000,9999)}"
        username = username_base
        idx = 1
        while User.objects.filter(username=username).exists():
            idx += 1
            username = f"{username_base}{idx}"

        with transaction.atomic():
            customer, _ = Customer.objects.get_or_create(phone=phone, defaults={"name": full_name})
            customer.name = full_name or customer.name
            customer.save(update_fields=["name"])

            user = User.objects.create_user(
                username=username,
                email=email,
                password=data["password"],
                first_name=full_name,
            )
            CustomerAccount.objects.create(user=user, customer=customer, phone=phone)

        return Response({
            "user": UserSerializer(user).data,
            "tokens": _tokens_for_user(user),
        }, status=201)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data["username"].strip()
        password = serializer.validated_data["password"]

        user = authenticate(request, username=username, password=password)
        if user is None:
            account = CustomerAccount.objects.filter(phone=username).select_related("user").first()
            if account:
                user = authenticate(request, username=account.user.username, password=password)

        if user is None or not hasattr(user, "customer_account"):
            return Response({"detail": "Invalid credentials."}, status=400)

        return Response({
            "user": UserSerializer(user).data,
            "tokens": _tokens_for_user(user),
        })


class OtpSendView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = OtpSendSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        code = f"{random.randint(0, 999999):06d}"
        otp = PhoneOTP.objects.create(
            phone=data["phone"].strip(),
            purpose=data["purpose"],
            code=code,
            expires_at=timezone.now() + timedelta(minutes=5),
        )
        return Response({"ok": True, "debug_code": otp.code, "expires_in": 300})


class OtpVerifyView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = OtpVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        otp = PhoneOTP.objects.filter(
            phone=data["phone"].strip(), purpose=data["purpose"], is_used=False
        ).order_by("-created_at").first()

        if not otp or otp.is_expired or otp.code != data["code"]:
            return Response({"detail": "Invalid or expired code."}, status=400)

        otp.is_used = True
        otp.save(update_fields=["is_used"])

        account = CustomerAccount.objects.filter(phone=data["phone"].strip()).select_related("user", "customer").first()
        if not account:
            customer, _ = Customer.objects.get_or_create(phone=data["phone"].strip(), defaults={"name": data["phone"].strip()})
            username_base = data["phone"].replace("+", "").replace(" ", "")
            username = username_base
            idx = 1
            while User.objects.filter(username=username).exists():
                idx += 1
                username = f"{username_base}{idx}"
            user = User.objects.create_user(username=username, password=User.objects.make_random_password(), first_name=customer.name or "Customer")
            account = CustomerAccount.objects.create(user=user, customer=customer, phone=data["phone"].strip())

        return Response({
            "user": UserSerializer(account.user).data,
            "tokens": _tokens_for_user(account.user),
        })


class LaundryListView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    queryset = Branch.objects.filter(active=True).order_by("name")
    serializer_class = BranchSerializer


class LaundryCatalogView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, pk):
        branch = Branch.objects.filter(pk=pk, active=True).first()
        if not branch:
            return Response({"detail": "Laundry not found."}, status=404)
        qs = BranchItemServicePrice.objects.filter(branch=branch).select_related("item", "service").order_by("service__sort_order", "item__sort_order", "item__name")
        return Response(CatalogRowSerializer(qs, many=True).data)


class AddressListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        customer = _customer_from_request(request)
        qs = SavedAddress.objects.filter(customer=customer)
        return Response(SavedAddressSerializer(qs, many=True).data)

    def post(self, request):
        customer = _customer_from_request(request)
        serializer = SavedAddressSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            if serializer.validated_data.get("is_default"):
                SavedAddress.objects.filter(customer=customer, is_default=True).update(is_default=False)
            instance = serializer.save(customer=customer)
        return Response(SavedAddressSerializer(instance).data, status=201)


class AddressDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, request, pk):
        customer = _customer_from_request(request)
        return SavedAddress.objects.filter(customer=customer, pk=pk).first()

    def put(self, request, pk):
        instance = self.get_object(request, pk)
        if not instance:
            return Response({"detail": "Address not found."}, status=404)
        serializer = SavedAddressSerializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            if serializer.validated_data.get("is_default"):
                SavedAddress.objects.filter(customer=instance.customer, is_default=True).exclude(pk=instance.pk).update(is_default=False)
            instance = serializer.save()
        return Response(SavedAddressSerializer(instance).data)

    def delete(self, request, pk):
        instance = self.get_object(request, pk)
        if not instance:
            return Response(status=204)
        instance.delete()
        return Response(status=204)


class DeviceTokenView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        customer = _customer_from_request(request)
        if not customer:
            return Response({"detail": "Unauthorized"}, status=401)
        token = (request.data.get("token") or "").strip()
        platform = (request.data.get("platform") or "").strip()
        if not token:
            return Response({"detail": "Token required."}, status=400)
        DeviceToken.objects.get_or_create(customer=customer, token=token, defaults={"platform": platform})
        return Response({"ok": True})


class OrderListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        customer = _customer_from_request(request)
        qs = Order.objects.filter(customer=customer).prefetch_related("items").order_by("-created_at")
        return Response(OrderSerializer(qs, many=True).data)

    def post(self, request):
        customer = _customer_from_request(request)
        serializer = OrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        branch_id = data.get("laundry_id") or data.get("laundry_shop_id")
        branch = Branch.objects.get(pk=branch_id)
        lines = data.get("items") or data.get("lines") or []

        subtotal = Decimal("0")
        priced_lines = []
        for line in lines:
            price_row = BranchItemServicePrice.objects.filter(
                branch=branch, item_id=line["item_id"], service_id=line["service_id"]
            ).select_related("item", "service").first()
            if not price_row:
                return Response({"detail": "One or more selected items are not available for this branch."}, status=400)
            qty = int(line["qty"])
            line_total = Decimal(qty) * price_row.price
            subtotal += line_total
            priced_lines.append((price_row, qty, line_total))

        urgent_flag = data.get("urgent")
        speed = (data.get("speed") or "").upper()
        if speed == "URGENT":
            urgent_flag = True
        urgent_fee = Decimal("0")
        if urgent_flag:
            urgent_fee = (subtotal * Decimal("0.30")).quantize(Decimal("0.001"))

        promo_discount = Decimal(str(data.get("promo_discount") or "0"))
        if promo_discount < 0:
            promo_discount = Decimal("0")
        if promo_discount > subtotal:
            promo_discount = subtotal

        points_used = int(data.get("points_used") or 0)
        points_value = Decimal(points_used) * Decimal("0.01") if points_used > 0 else Decimal("0")
        if points_value > (subtotal + urgent_fee - promo_discount):
            points_value = subtotal + urgent_fee - promo_discount
            points_used = int((points_value / Decimal("0.01")).to_integral_value())

        tax_rate = Decimal(str(branch.tax_rate or 0))
        tax = (subtotal * tax_rate / Decimal("100")).quantize(Decimal("0.001")) if tax_rate > 0 else Decimal("0")
        total = subtotal + urgent_fee + tax - promo_discount - points_value
        if total < 0:
            total = Decimal("0")

        address = None
        if data.get("address_id"):
            address = SavedAddress.objects.filter(customer=customer, pk=data["address_id"]).first()

        with transaction.atomic():
            order = Order.objects.create(
                branch=branch.code,
                order_no=_next_order_no(),
                status=Order.Status.RECEIVED,
                urgent=bool(urgent_flag),
                customer=customer,
                subtotal=subtotal,
                discount=Decimal("0"),
                tax=tax,
                total=total,
                paid=Decimal("0"),
                balance=total,
                delivery_required=True,
                delivery_status=Order.DeliveryStatus.PENDING,
                delivery_address=(f"{address.address_line_1}, {address.area}, {address.city}" if address else ""),
                delivery_phone=customer.phone,
                delivery_slot=data.get("delivery_slot", ""),
                delivery_fee=Decimal("0"),
                notes=data.get("notes", ""),
            )
            MobileOrderMeta.objects.create(
                order=order,
                payment_method=data.get("payment_method", ""),
                transfer_reference=data.get("transfer_reference", ""),
                receipt_name=data.get("receipt_name", ""),
                promo_code=data.get("promo_code", ""),
                promo_discount=promo_discount,
                points_used=points_used,
                customer_notes=data.get("customer_notes", ""),
                pickup_time_slot=data.get("pickup_time_slot", ""),
                speed=speed or ("URGENT" if urgent_flag else "NORMAL"),
            )
            for price_row, qty, line_total in priced_lines:
                OrderItem.objects.create(
                    order=order,
                    item_name=price_row.item.name,
                    service_name=price_row.service.name,
                    qty=qty,
                    price=price_row.price,
                    line_total=line_total,
                )
            OrderStatusLog.objects.create(order=order, from_status="", to_status=Order.Status.RECEIVED, note="Order placed")
            if data.get("payment_method") in ["BANK", "BANK_TRANSFER"]:
                Payment.objects.create(order=order, method=Payment.Method.BANK, amount=Decimal("0"), note="Awaiting transfer")
            if points_used > 0 and customer.points:
                customer.points = max(0, int(customer.points) - points_used)
                customer.save(update_fields=["points"])

        return Response(OrderSerializer(order).data, status=201)


class OrderDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        customer = _customer_from_request(request)
        order = Order.objects.filter(pk=pk, customer=customer).prefetch_related("items").first()
        if not order:
            return Response({"detail": "Order not found."}, status=404)
        return Response(OrderSerializer(order).data)


class OrderTrackingView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        customer = _customer_from_request(request)
        order = Order.objects.filter(pk=pk, customer=customer).first()
        if not order:
            return Response({"detail": "Order not found."}, status=404)
        logs = order.status_logs.all().order_by("created_at")
        return Response({
            "order_no": order.order_no,
            "status": order.status,
            "delivery_status": order.delivery_status,
            "timeline": OrderTrackingLogSerializer(logs, many=True).data,
            "eta": order.estimated_ready_at.isoformat() if order.estimated_ready_at else "",
        })


class BankTransferProofView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        customer = _customer_from_request(request)
        order = Order.objects.filter(pk=pk, customer=customer).first()
        if not order:
            return Response({"detail": "Order not found."}, status=404)
        meta = getattr(order, "mobile_meta", None)
        if not meta:
            meta = MobileOrderMeta.objects.create(order=order)
        meta.transfer_reference = (request.data.get("transfer_reference") or "").strip()
        meta.receipt_name = (request.data.get("receipt_name") or "").strip()
        meta.payment_method = "BANK"
        meta.save(update_fields=["transfer_reference", "receipt_name", "payment_method"])
        return Response({"ok": True})


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def payment_methods_view(request):
    return Response([
        {"code": "COD", "label": "Cash on delivery"},
        {"code": "BANK", "label": "Bank transfer"},
    ])
