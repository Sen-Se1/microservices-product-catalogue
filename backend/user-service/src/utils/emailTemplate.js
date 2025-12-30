const sendEmail = require("./sendEmail");

/**
 * @desc    Email verification
 */
exports.verifyEmail = async (user, verifyUrl, action = null) => {
  const subject =
    action === "resend"
      ? "Resend: Verify your email address"
      : "Verify your email address";
  return sendEmail({
    email: user.email,
    subject: subject,
    message: `
Hello,

Please verify your email address by clicking the link below:

${verifyUrl}

This link will expire in 5 minutes.
`,
  });
};

/**
 * @desc    Forgot password
 */
exports.forgotPassword = async (user, resetUrl) => {
  return sendEmail({
    email: user.email,
    subject: "Password reset request",
    message: `
Hello,

You requested a password reset.

Click the link below to set a new password:

${resetUrl}

If you did not request this, please ignore this email.
`,
  });
};

/**
 * @desc    Password changed (reset or update)
 */
exports.passwordChanged = async (user) => {
  return sendEmail({
    email: user.email,
    subject: "Your password has been changed",
    message: `
Hello,

Your account password was recently changed.

If this was not you, please contact support immediately.
`,
  });
};

/**
 * @desc    New login detected
 */
exports.newLoginDetected = async (user, meta = {}) => {
  const {
    ip = "Unknown IP",
    userAgent = "Unknown device",
    time = new Date().toLocaleString(),
  } = meta;

  return sendEmail({
    email: user.email,
    subject: "New login detected on your account",
    message: `
Hello,

We detected a new login to your account.

Login details:
• Date & Time: ${time}
• IP Address: ${ip}
• Device / Browser: ${userAgent}

If this was you, no action is needed.

If you do NOT recognize this login:
• Change your password immediately
• Contact support as soon as possible

Stay safe,
Security Team
`,
  });
};

/**
 * @desc    Account deactivated (admin or self)
 */
exports.accountDeactivated = async (user) => {
  return sendEmail({
    email: user.email,
    subject: "Your account has been deactivated",
    message: `
Hello,

Your account has been deactivated.

If you believe this is a mistake, please contact support.
`,
  });
};

/**
 * @desc    Account activated (admin)
 */
exports.accountActivated = async (user) => {
  return sendEmail({
    email: user.email,
    subject: "Your account has been activated",
    message: `
Hello,

Your account has been reactivated by an administrator.
You can now log in again.

Welcome back!
`,
  });
};


