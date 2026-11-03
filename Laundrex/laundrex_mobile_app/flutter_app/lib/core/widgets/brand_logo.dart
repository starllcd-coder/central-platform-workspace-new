import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';

class BrandLogo extends StatelessWidget {
  const BrandLogo({
    super.key,
    this.size = 112,
    this.cropFactor = 1.0,
    this.useSvg = false,
  });

  final double size;
  final double cropFactor;
  final bool useSvg;
  static const String _svgAsset = 'assets/laundrex-logo-icon.svg';
  static const String _pngAsset = 'assets/laundrex-icon-512x512.png';

  @override
  Widget build(BuildContext context) {
    final shouldCrop = cropFactor > 0 && cropFactor < 0.999;
    final Widget logo = useSvg
        ? SvgPicture.asset(
            _svgAsset,
            width: size,
            height: size,
            fit: BoxFit.contain,
            allowDrawingOutsideViewBox: true,
          )
        : Image.asset(
            _pngAsset,
            width: size,
            height: size,
            fit: BoxFit.contain,
            isAntiAlias: true,
            filterQuality: FilterQuality.high,
            gaplessPlayback: true,
          );

    return SizedBox(
      width: size,
      height: size,
      child: shouldCrop
          ? ClipRect(
              clipBehavior: Clip.antiAlias,
              child: Transform.scale(
                scale: 1 / cropFactor,
                child: Center(child: logo),
              ),
            )
          : logo,
    );
  }
}
