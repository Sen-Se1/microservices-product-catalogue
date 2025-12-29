const crypto = require("crypto");

exports.generateToken = () => {
  const rawToken = crypto.randomBytes(32).toString("hex");

  const hashedToken = crypto
    .createHash("sha256")
    .update(rawToken)
    .digest("hex");

  return { rawToken, hashedToken };
};

exports.hashToken = (token) =>
  crypto.createHash("sha256").update(token).digest("hex");
