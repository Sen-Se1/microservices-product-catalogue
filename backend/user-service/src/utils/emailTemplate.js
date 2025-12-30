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
<!DOCTYPE html>
<body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background-color: #f8f9fa; color: #333;">
  <table role="presentation" style="width: 100%; max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);">
    <tr>
      <td style="padding: 40px 30px;">
        <h1 style="margin: 0 0 20px; font-size: 24px; font-weight: 600; color: #1a1a1a; text-align: center;">Verify Your Email Address</h1>
        <p style="margin: 0 0 20px; line-height: 1.6; font-size: 16px; color: #555;">Hello!</p>
        <p style="margin: 0 0 30px; line-height: 1.6; font-size: 16px; color: #555;">Please verify your email address by clicking the button below. This link will expire in 5 minutes.</p>
        <table role="presentation" style="margin: 0 auto;">
          <tr>
            <td style="text-align: center;">
              <a href="${verifyUrl}" style="display: inline-block; padding: 12px 24px; background-color: #007bff; color: #ffffff; text-decoration: none; font-weight: 500; border-radius: 6px; font-size: 16px;">Verify Email</a>
            </td>
          </tr>
        </table>
        <p style="margin: 30px 0 0; font-size: 14px; color: #888; text-align: center; line-height: 1.5;">If the button doesn't work, copy and paste this link into your browser: <br><a href="${verifyUrl}" style="color: #007bff;">${verifyUrl}</a></p>
      </td>
    </tr>
    <tr>
      <td style="background-color: #f8f9fa; padding: 20px 30px; text-align: center; font-size: 12px; color: #6c757d;">
        &copy; 2025 Your App Name. All rights reserved.
      </td>
    </tr>
  </table>
</body>
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
<!DOCTYPE html>
<body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background-color: #f8f9fa; color: #333;">
  <table role="presentation" style="width: 100%; max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);">
    <tr>
      <td style="padding: 40px 30px;">
        <h1 style="margin: 0 0 20px; font-size: 24px; font-weight: 600; color: #1a1a1a; text-align: center;">Reset Your Password</h1>
        <p style="margin: 0 0 20px; line-height: 1.6; font-size: 16px; color: #555;">Hello!</p>
        <p style="margin: 0 0 30px; line-height: 1.6; font-size: 16px; color: #555;">You requested a password reset. Click the button below to set a new password.</p>
        <table role="presentation" style="margin: 0 auto;">
          <tr>
            <td style="text-align: center;">
              <a href="${resetUrl}" style="display: inline-block; padding: 12px 24px; background-color: #007bff; color: #ffffff; text-decoration: none; font-weight: 500; border-radius: 6px; font-size: 16px;">Reset Password</a>
            </td>
          </tr>
        </table>
        <p style="margin: 30px 0 0; font-size: 14px; color: #888; text-align: center; line-height: 1.5;">If you did not request this, please ignore this email. <br><a href="${resetUrl}" style="color: #007bff;">${resetUrl}</a></p>
      </td>
    </tr>
    <tr>
      <td style="background-color: #f8f9fa; padding: 20px 30px; text-align: center; font-size: 12px; color: #6c757d;">
        &copy; 2025 Your App Name. All rights reserved.
      </td>
    </tr>
  </table>
</body>
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
<!DOCTYPE html>
<body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background-color: #f8f9fa; color: #333;">
  <table role="presentation" style="width: 100%; max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);">
    <tr>
      <td style="padding: 40px 30px;">
        <h1 style="margin: 0 0 20px; font-size: 24px; font-weight: 600; color: #1a1a1a; text-align: center;">Password Updated</h1>
        <p style="margin: 0 0 20px; line-height: 1.6; font-size: 16px; color: #555;">Hello!</p>
        <p style="margin: 0 0 30px; line-height: 1.6; font-size: 16px; color: #555;">Your account password was recently changed.</p>
        <p style="margin: 0 0 20px; line-height: 1.6; font-size: 16px; color: #dc3545; font-weight: 500;">If this was not you, please contact support immediately to secure your account.</p>
        <table role="presentation" style="margin: 0 auto;">
          <tr>
            <td style="text-align: center;">
              <a href="mailto:support@yourapp.com" style="display: inline-block; padding: 12px 24px; background-color: #dc3545; color: #ffffff; text-decoration: none; font-weight: 500; border-radius: 6px; font-size: 16px;">Contact Support</a>
            </td>
          </tr>
        </table>
      </td>
    </tr>
    <tr>
      <td style="background-color: #f8f9fa; padding: 20px 30px; text-align: center; font-size: 12px; color: #6c757d;">
        &copy; 2025 Your App Name. All rights reserved.
      </td>
    </tr>
  </table>
</body>
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
<!DOCTYPE html>
<body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background-color: #f8f9fa; color: #333;">
  <table role="presentation" style="width: 100%; max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);">
    <tr>
      <td style="padding: 40px 30px;">
        <h1 style="margin: 0 0 20px; font-size: 24px; font-weight: 600; color: #1a1a1a; text-align: center;">New Login Detected</h1>
        <p style="margin: 0 0 20px; line-height: 1.6; font-size: 16px; color: #555;">Hello!</p>
        <p style="margin: 0 0 30px; line-height: 1.6; font-size: 16px; color: #555;">We detected a new login to your account. If this was you, no action is needed.</p>
        <h2 style="margin: 0 0 15px; font-size: 18px; font-weight: 600; color: #1a1a1a;">Login Details</h2>
        <ul style="margin: 0 0 30px; padding-left: 20px; line-height: 1.6; font-size: 16px; color: #555;">
          <li style="margin-bottom: 10px;">Date & Time: <strong>${time}</strong></li>
          <li style="margin-bottom: 10px;">IP Address: <strong>${ip}</strong></li>
          <li style="margin-bottom: 0;">Device / Browser: <strong>${userAgent}</strong></li>
        </ul>
        <p style="margin: 0 0 20px; line-height: 1.6; font-size: 16px; color: #dc3545; font-weight: 500;">If you do NOT recognize this login:</p>
        <ul style="margin: 0 0 30px; padding-left: 20px; line-height: 1.6; font-size: 16px; color: #555;">
          <li style="margin-bottom: 10px;">Change your password immediately</li>
          <li style="margin-bottom: 0;">Contact support as soon as possible</li>
        </ul>
        <table role="presentation" style="margin: 0 auto;">
          <tr>
            <td style="text-align: center;">
              <a href="mailto:support@yourapp.com" style="display: inline-block; padding: 12px 24px; background-color: #dc3545; color: #ffffff; text-decoration: none; font-weight: 500; border-radius: 6px; font-size: 16px; margin-right: 10px;">Contact Support</a>
              <a href="https://yourapp.com/change-password" style="display: inline-block; padding: 12px 24px; background-color: #007bff; color: #ffffff; text-decoration: none; font-weight: 500; border-radius: 6px; font-size: 16px;">Change Password</a>
            </td>
          </tr>
        </table>
      </td>
    </tr>
    <tr>
      <td style="background-color: #f8f9fa; padding: 20px 30px; text-align: center; font-size: 12px; color: #6c757d;">
        Stay safe,<br>Security Team &copy; 2025 Your App Name. All rights reserved.
      </td>
    </tr>
  </table>
</body>
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
<!DOCTYPE html>
<body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background-color: #f8f9fa; color: #333;">
  <table role="presentation" style="width: 100%; max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);">
    <tr>
      <td style="padding: 40px 30px;">
        <h1 style="margin: 0 0 20px; font-size: 24px; font-weight: 600; color: #dc3545; text-align: center;">Account Deactivated</h1>
        <p style="margin: 0 0 20px; line-height: 1.6; font-size: 16px; color: #555;">Hello!</p>
        <p style="margin: 0 0 30px; line-height: 1.6; font-size: 16px; color: #555;">Your account has been deactivated.</p>
        <p style="margin: 0 0 20px; line-height: 1.6; font-size: 16px; color: #007bff; font-weight: 500;">If you believe this is a mistake, please contact support to resolve this.</p>
        <table role="presentation" style="margin: 0 auto;">
          <tr>
            <td style="text-align: center;">
              <a href="mailto:support@yourapp.com" style="display: inline-block; padding: 12px 24px; background-color: #007bff; color: #ffffff; text-decoration: none; font-weight: 500; border-radius: 6px; font-size: 16px;">Contact Support</a>
            </td>
          </tr>
        </table>
      </td>
    </tr>
    <tr>
      <td style="background-color: #f8f9fa; padding: 20px 30px; text-align: center; font-size: 12px; color: #6c757d;">
        &copy; 2025 Your App Name. All rights reserved.
      </td>
    </tr>
  </table>
</body>
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
<!DOCTYPE html>
<body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background-color: #f8f9fa; color: #333;">
  <table role="presentation" style="width: 100%; max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);">
    <tr>
      <td style="padding: 40px 30px;">
        <h1 style="margin: 0 0 20px; font-size: 24px; font-weight: 600; color: #28a745; text-align: center;">Account Activated</h1>
        <p style="margin: 0 0 20px; line-height: 1.6; font-size: 16px; color: #555;">Hello!</p>
        <p style="margin: 0 0 20px; line-height: 1.6; font-size: 16px; color: #555;">Your account has been reactivated by an administrator. You can now log in again.</p>
        <p style="margin: 0 0 30px; line-height: 1.6; font-size: 16px; color: #28a745; font-weight: 500; text-align: center; font-size: 18px;">Welcome back!</p>
        <table role="presentation" style="margin: 0 auto;">
          <tr>
            <td style="text-align: center;">
              <a href="https://yourapp.com/login" style="display: inline-block; padding: 12px 24px; background-color: #28a745; color: #ffffff; text-decoration: none; font-weight: 500; border-radius: 6px; font-size: 16px;">Log In Now</a>
            </td>
          </tr>
        </table>
      </td>
    </tr>
    <tr>
      <td style="background-color: #f8f9fa; padding: 20px 30px; text-align: center; font-size: 12px; color: #6c757d;">
        &copy; 2025 Your App Name. All rights reserved.
      </td>
    </tr>
  </table>
</body>
    `,
  });
};