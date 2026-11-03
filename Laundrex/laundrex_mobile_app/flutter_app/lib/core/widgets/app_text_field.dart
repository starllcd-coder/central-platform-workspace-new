import 'package:flutter/material.dart';

class AppTextField extends StatelessWidget {
  const AppTextField({
    super.key,
    required this.hint,
    this.controller,
    this.obscureText = false,
    this.prefixIcon,
    this.suffixIcon,
    this.suffixColor,
    this.onSuffixTap,
    this.keyboardType,
  });

  final String hint;
  final TextEditingController? controller;
  final bool obscureText;
  final IconData? prefixIcon;
  final IconData? suffixIcon;
  final Color? suffixColor;
  final VoidCallback? onSuffixTap;
  final TextInputType? keyboardType;

  @override
  Widget build(BuildContext context) {
    return TextField(
      controller: controller,
      obscureText: obscureText,
      keyboardType: keyboardType,
      decoration: InputDecoration(
        hintText: hint,
        prefixIcon: prefixIcon == null ? null : Icon(prefixIcon),
        suffixIcon: suffixIcon == null
            ? null
            : (onSuffixTap == null
                ? Icon(suffixIcon, color: suffixColor)
                : IconButton(
                    onPressed: onSuffixTap,
                    icon: Icon(suffixIcon, color: suffixColor),
                  )),
      ),
    );
  }
}
