import 'package:intl/intl.dart';

class Helpers {
  static String formatAltitude(double altitudeMeters) {
    return '${altitudeMeters.toStringAsFixed(1)} m';
  }

  static String formatSpeed(double speedKmh) {
    return '${speedKmh.toStringAsFixed(1)} km/h';
  }

  static String formatTimestamp(DateTime dateTime) {
    return DateFormat('HH:mm:ss').format(dateTime);
  }
}