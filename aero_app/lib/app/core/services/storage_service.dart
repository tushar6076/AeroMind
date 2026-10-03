import 'package:sqflite/sqflite.dart';
import 'package:path/path.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../../models/user_model.dart';

class StorageService {
  static Database? _db;
  final _secureStorage = const FlutterSecureStorage();
  static const String _tokenKey = 'auth_token';

  Future<Database> get database async {
    if (_db != null && _db!.isOpen) return _db!;
    _db = await _initDb();
    return _db!;
  }

  Future<Database> _initDb() async {
    final dbPath = await getDatabasesPath();
    final path = join(dbPath, 'aeromind_local.db');

    return await openDatabase(
      path,
      version: 1,
      onCreate: (db, version) async {
        await db.execute('''
          CREATE TABLE user (
            id TEXT PRIMARY KEY,
            email TEXT,
            full_name TEXT,
            role TEXT,
            is_active INTEGER,
            is_verified INTEGER,
            is_approved INTEGER,
            last_active TEXT,
            created_at TEXT
          )
        ''');
      },
    );
  }

  // --- Secure Token Storage ---
  Future<void> saveToken(String token) async {
    await _secureStorage.write(key: _tokenKey, value: token);
  }

  Future<String?> getToken() async {
    return await _secureStorage.read(key: _tokenKey);
  }

  Future<void> clearToken() async {
    await _secureStorage.delete(key: _tokenKey);
  }

  // --- SQLite Local User Cache ---
  Future<void> saveUserToLocalDb(UserModel user) async {
    final db = await database;
    await db.insert(
      'user',
      {
        'id': user.id,
        'email': user.email,
        'full_name': user.fullName,
        'role': user.role,
        'is_active': user.isActive ? 1 : 0,
        'is_verified': user.isVerified ? 1 : 0,
        'is_approved': user.isApproved ? 1 : 0,
        'last_active': user.lastActive?.toIso8601String(),
        'created_at': user.createdAt.toIso8601String(),
      },
      conflictAlgorithm: ConflictAlgorithm.replace,
    );
  }

  Future<UserModel?> getUserFromLocalDb() async {
    final db = await database;
    final maps = await db.query('user', limit: 1);
    if (maps.isNotEmpty) {
      final item = maps.first;
      return UserModel(
        id: item['id'] as String,
        email: item['email'] as String,
        fullName: item['full_name'] as String?,
        role: item['role'] as String? ?? 'user',
        isActive: (item['is_active'] as int?) == 1,
        isVerified: (item['is_verified'] as int?) == 1,
        isApproved: (item['is_approved'] as int?) == 1,
        lastActive: item['last_active'] != null
            ? DateTime.tryParse(item['last_active'] as String)
            : null,
        createdAt: item['created_at'] != null
            ? DateTime.parse(item['created_at'] as String)
            : DateTime.now(),
      );
    }
    return null;
  }

  Future<void> clearUserLocalDb() async {
    final db = await database;
    await db.delete('user');
    await clearToken();
  }

  /// Permanently deletes aeromind_local.db file from the iOS Simulator sandbox
  /// and clears stored JWT tokens.
  Future<void> deleteEntireDatabase() async {
    if (_db != null && _db!.isOpen) {
      await _db!.close();
      _db = null;
    }

    final dbPath = await getDatabasesPath();
    final path = join(dbPath, 'aeromind_local.db');

    await deleteDatabase(path);
    await _secureStorage.deleteAll();
  }
}