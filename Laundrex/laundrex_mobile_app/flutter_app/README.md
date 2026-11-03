# Laundrex Flutter Customer App

This package contains the customer mobile app UI plus live API wiring for:
- register
- login
- OTP send / verify
- laundries list
- branch catalog
- saved addresses
- create order
- my orders
- order tracking
- device push token registration (`/api/devices`)

## Important alignment note
The uploaded Django project already has **Customer**, **Order**, **OrderItem**, **Branch**, **Service**, **Item**, and **Payment** models, but it does **not** yet have customer auth accounts or saved addresses.

The included `django_patch/` folder adds the missing mobile API layer and the extra models required for the Flutter app.

## Run
```bash
flutter pub get
flutter run --dart-define=API_BASE_URL=http://10.0.2.2:8000
```

## Native setup required for new features
This app now includes:
- Firebase Cloud Messaging (push notifications)
- Google Maps + GPS location picker
- Bank transfer receipt upload (image picker)

You must add the standard Firebase config files and Google Maps API keys for Android/iOS:
- Android: `google-services.json`, Maps API key in `AndroidManifest.xml`
- iOS: `GoogleService-Info.plist`, Maps API key in `AppDelegate`

You also need to add runtime permissions:
- Android: camera/gallery + location
- iOS: location usage description + photo library usage description
# Laundrex Mobile

## Release configuration

Android uses `com.laundrex.customer`. Release builds require:

```text
LAUNDREX_KEYSTORE_PATH
LAUNDREX_KEYSTORE_PASSWORD
LAUNDREX_KEY_ALIAS
LAUNDREX_KEY_PASSWORD
```

iOS uses `com.laundrex.customer`; configure the Apple development team and
distribution profile in Xcode before archiving.
