# ======================
# Welcome
# ======================
WELCOME_HTML = """
<html>
  <body style="font-family: Arial, sans-serif; background:#f9fafb; padding:20px;">
    <div style="max-width:600px; margin:auto; background:white; padding:30px; border-radius:10px;">
      <h2 style="color:#111827;">Welcome to AeroMind, {username}!</h2>
      <p style="color:#4b5563;">
        Your account has been created successfully. Please wait for admin approval to access full features.
      </p>
      <p style="font-size:13px; color:#9ca3af;">HackSmiths • AeroMind</p>
    </div>
  </body>
</html>
"""

# ======================
# OTP
# ======================
OTP_HTML = """
<html>
  <body style="font-family: Arial, sans-serif; padding:20px;">
    <div style="max-width:500px; margin:auto; border:1px solid #e5e7eb; padding:25px; border-radius:8px;">
      <h2>Verification Code</h2>
      <p>Hi {username}, use the code below:</p>
      <div style="background:#f3f4f6; padding:15px; text-align:center; font-size:28px; font-weight:bold; letter-spacing:4px;">
        {code}
      </div>
      <p style="font-size:13px; color:#6b7280;">This code expires in 10 minutes.</p>
    </div>
  </body>
</html>
"""

# ======================
# Login Alert
# ======================
LOGIN_ALERT_HTML = """
<html>
  <body style="font-family: Arial, sans-serif; padding:20px;">
    <div style="max-width:600px; margin:auto; border:1px solid #fee2e2; padding:25px; border-radius:8px;">
      <h2 style="color:#dc2626;">New Login Detected</h2>
      <p>Hi {username}, a new login was detected at <strong>{time}</strong>.</p>
      <p>If this wasn’t you, please reset your password immediately.</p>
    </div>
  </body>
</html>
"""

# ======================
# Password Reset Success
# ======================
RESET_SUCCESS_HTML = """
<html>
  <body style="font-family: Arial, sans-serif; padding:20px;">
    <div style="max-width:600px; margin:auto; border:1px solid #dcfce7; padding:25px; border-radius:8px;">
      <h2 style="color:#16a34a;">Password Updated</h2>
      <p>Hi {username}, your password has been successfully reset.</p>
    </div>
  </body>
</html>
"""

# ======================
# Account Deleted
# ======================
DELETE_ACCOUNT_HTML = """
<html>
  <body style="font-family: Arial, sans-serif; padding:20px;">
    <div style="max-width:600px; margin:auto; border:1px solid #f3f4f6; padding:25px; border-radius:8px;">
      <h2>Account Deleted</h2>
      <p>Hello {username},</p>
      <p>Your AeroMind account has been permanently deleted.</p>
    </div>
  </body>
</html>
"""

# ======================
# Approval Result (Approved / Rejected)
# ======================
APPROVAL_RESULT_HTML = """
<html>
  <body style="font-family: Arial, sans-serif; padding:20px;">
    <div style="max-width:600px; margin:auto; border:1px solid #e5e7eb; padding:25px; border-radius:8px;">
      <h2>Account {status}</h2>
      <p>Hi {username},</p>
      <p>Your AeroMind account has been <strong>{status}</strong> by the admin.</p>
      <p>{message}</p>
    </div>
  </body>
</html>
"""

# ======================
# New User Request (Admin)
# ======================
NEW_USER_REQUEST_HTML = """
<html>
  <body style="font-family: Arial, sans-serif; padding:20px;">
    <div style="max-width:600px; margin:auto; border:1px solid #e5e7eb; padding:25px; border-radius:8px;">
      <h2>New User Access Request</h2>
      <p>A new user has requested access to AeroMind.</p>
      <p><strong>Name:</strong> {username}</p>
      <p><strong>Email:</strong> {email}</p>
      <p>Please review and approve/reject the request.</p>
    </div>
  </body>
</html>
"""