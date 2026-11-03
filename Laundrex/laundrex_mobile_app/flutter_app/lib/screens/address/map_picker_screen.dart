import 'package:flutter/material.dart';
import 'package:geolocator/geolocator.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart';

import '../../core/utils/tr.dart';

class MapPickerScreen extends StatefulWidget {
  const MapPickerScreen({super.key, this.initial});
  final LatLng? initial;

  @override
  State<MapPickerScreen> createState() => _MapPickerScreenState();
}

class _MapPickerScreenState extends State<MapPickerScreen> {
  LatLng? selected;
  bool locating = false;

  @override
  void initState() {
    super.initState();
    selected = widget.initial;
  }

  Future<void> _useCurrentLocation() async {
    setState(() => locating = true);
    try {
      final permission = await Geolocator.requestPermission();
      if (permission == LocationPermission.denied || permission == LocationPermission.deniedForever) {
        if (!mounted) return;
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(tr(context, en: 'Location permission denied.', ar: 'تم رفض إذن الموقع.'))));
        return;
      }
      final pos = await Geolocator.getCurrentPosition();
      setState(() => selected = LatLng(pos.latitude, pos.longitude));
    } catch (_) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(tr(context, en: 'Could not get location.', ar: 'تعذر الحصول على الموقع.'))));
    } finally {
      if (mounted) setState(() => locating = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final initial = selected ?? const LatLng(17.0197, 54.0897);
    return Scaffold(
      appBar: AppBar(
        title: Text(tr(context, en: 'Pick location', ar: 'تحديد الموقع')),
        actions: [
          TextButton(
            onPressed: selected == null ? null : () => Navigator.pop(context, selected),
            child: Text(tr(context, en: 'Use', ar: 'استخدام')),
          )
        ],
      ),
      body: Stack(
        children: [
          GoogleMap(
            initialCameraPosition: CameraPosition(target: initial, zoom: 14),
            markers: selected == null ? {} : {Marker(markerId: const MarkerId('selected'), position: selected!)},
            onTap: (pos) => setState(() => selected = pos),
            myLocationEnabled: true,
            myLocationButtonEnabled: false,
          ),
          Positioned(
            right: 16,
            bottom: 24,
            child: FloatingActionButton.extended(
              onPressed: locating ? null : _useCurrentLocation,
              icon: locating ? const SizedBox(width: 18, height: 18, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white)) : const Icon(Icons.my_location_rounded),
              label: Text(tr(context, en: 'Current', ar: 'الموقع الحالي')),
            ),
          ),
        ],
      ),
    );
  }
}
