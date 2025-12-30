const asyncHandler = require("express-async-handler");
const bcrypt = require("bcryptjs");
const crypto = require("crypto");
const Email = require("../utils/emailTemplate");
const createToken = require("../utils/createJWT");
const ApiError = require("../utils/apiError");
const User = require("../models/userModel");
const { generateToken, hashToken } = require("../utils/verificationToken");


/**
 * @desc    Register
 * @route   Post /api/v1/auth/register
 * @access  Public
 */
exports.register = asyncHandler(async (req, res, next) => {
  const salt = await bcrypt.genSalt(10);
  const hashedPassword = await bcrypt.hash(req.body.password, salt);

  const user = await User.create({
    email: req.body.email,
    password: hashedPassword,
    profile: {
      firstName: req.body.firstName,
      lastName: req.body.lastName,
      phone: req.body.phone,
      avatar: req.body.avatar,
      dateOfBirth: req.body.dateOfBirth,
    },
    address: {
      street: req.body.street,
      city: req.body.city,
      state: req.body.state,
      country: req.body.country,
      zipCode: req.body.zipCode,
    },
  });

  const { rawToken, hashedToken } = generateToken();

  user.emailVerificationToken = hashedToken;
  user.emailVerificationTokenExpires = Date.now() + 5 * 60 * 1000; // 5 min
  await user.save({ validateBeforeSave: false });

  const verifyUrl = `${process.env.PUBLIC_FRONTEND_URL}/verify-email/${rawToken}`;
  await Email.verifyEmail(user, verifyUrl);

  res.status(201).json({
    message:
      "User registered successfully. Please check your email to verify your account.",
  });
});

/**
 * @desc    Verify email
 * @route   PUT /api/v1/auth/verify-email/:token
 * @access  Public
 */
exports.verifyEmail = asyncHandler(async (req, res, next) => {
  const hashedToken = hashToken(req.params.token);

  const user = await User.findOne({
    emailVerificationToken: hashedToken,
    emailVerificationTokenExpires: { $gt: Date.now() },
  });

  if (!user) {
    return next(new ApiError("Verification token is invalid or expired", 400));
  }

  user.isVerified = true;
  user.emailVerificationToken = undefined;
  user.emailVerificationTokenExpires = undefined;

  await user.save({ validateBeforeSave: false });

  res.status(200).json({
    message: "Email verified successfully",
  });
});

/**
 * @desc    Resend verification email
 * @route   POST /api/v1/auth/resend-verification-email
 * @access  Public
 */
exports.resendVerificationEmail = asyncHandler(async (req, res, next) => {
  const user = await User.findOne({ email: req.body.email });

  if (!user || user.isVerified) {
    return next(new ApiError("Invalid request", 400));
  }

  const { rawToken, hashedToken } = generateToken();

  user.emailVerificationToken = hashedToken;
  user.emailVerificationTokenExpires = Date.now() + 5 * 60 * 1000;

  await user.save({ validateBeforeSave: false });

  const verifyUrl = `${process.env.PUBLIC_FRONTEND_URL}/verify-email/${rawToken}`;
  await Email.verifyEmail(user, verifyUrl, "resend");

  res.status(200).json({
    message: "Verification email resent",
  });
});

/**
 * @desc    Login
 * @route   POST /api/v1/auth/login
 * @access  Public
 */
exports.login = asyncHandler(async (req, res, next) => {
  const user = await User.findOne({
    email: req.body.email,
    role: req.body.role,
  });

  if (!user || !(await bcrypt.compare(req.body.password, user.password))) {
    return next(new ApiError("Incorrect email or password", 401));
  }

  if (!user.isVerified) {
    return next(
      new ApiError("Please verify your email before logging in.", 401)
    );
  }

  if (!user.isActive) {
    return next(
      new ApiError(
        "Your account has been deactivated. Please contact support.",
        403
      )
    );
  }

  user.lastLogin = Date.now();
  await user.save();
  await Email.newLoginDetected(user, {
    ip: req.ip,
    userAgent: req.headers["user-agent"],
  });
  const token = createToken(user._id);
  delete user._doc.password;

  res.status(200).json({ data: user, token });
});

/**
 * @desc    Forgot password
 * @route   POST /api/v1/auth/forgotPassword
 * @access  Public
 */
exports.forgotPassword = asyncHandler(async (req, res, next) => {
  const user = await User.findOne({ email: req.body.email });

  if (!user) {
    return next(
      new ApiError(
        `There is no user with this email address: ${req.body.email}`,
        404
      )
    );
  }

  if (!user.isVerified) {
    return next(
      new ApiError(
        "Please verify your email before resetting your password.",
        403
      )
    );
  }

  if (!user.isActive) {
    return next(
      new ApiError(
        "Your account has been deactivated. Please contact support.",
        403
      )
    );
  }

  const { rawToken, hashedToken } = generateToken();

  user.passwordResetToken = hashedToken;
  user.passwordResetTokenExpires = Date.now() + 5 * 60 * 1000;

  await user.save({ validateBeforeSave: false });

  const client = req.body.client || "public";
  const frontendUrls = {
    admin: process.env.ADMIN_FRONTEND_URL || "http://localhost:4200",
    public: process.env.PUBLIC_FRONTEND_URL || "http://localhost:3000",
  };

  const frontendUrl = frontendUrls[client] || frontendUrls.public;
  const resetUrl = `${frontendUrl}/reset-password/${rawToken}`;

  try {
    await Email.forgotPassword(user, resetUrl);
  } catch (err) {
    user.passwordResetToken = undefined;
    user.passwordResetTokenExpires = undefined;
    await user.save({ validateBeforeSave: false });

    return next(new ApiError("Email sending failed. Try again later!", 500));
  }

  res.status(200).json({
    message: "Password reset link sent to your email",
  });
});

/**
 * @desc    Reset password
 * @route   PUT /auth/resetPassword/:token
 * @access  Public
 */
exports.resetPassword = asyncHandler(async (req, res, next) => {
  const hashedResetToken = hashToken(req.params.token);

  const user = await User.findOne({
    passwordResetToken: hashedResetToken,
    passwordResetTokenExpires: { $gt: Date.now() },
  });

  if (!user) {
    return next(new ApiError("Token is invalid or has expired", 400));
  }

  if (!user.isVerified) {
    return next(
      new ApiError(
        "Please verify your email before resetting your password.",
        403
      )
    );
  }

  if (!user.isActive) {
    return next(
      new ApiError(
        "Your account has been deactivated. Please contact support.",
        403
      )
    );
  }

  const salt = await bcrypt.genSalt(10);
  const hashedPassword = await bcrypt.hash(req.body.password, salt);

  user.password = hashedPassword;
  user.passwordResetToken = undefined;
  user.passwordResetTokenExpires = undefined;
  user.passwordChangedAt = Date.now();
  user.lastLogin = Date.now();

  await user.save({ validateBeforeSave: false });
  await Email.passwordChanged(user);

  const token = createToken(user._id);

  delete user._doc.password;

  res.status(200).json({
    data: user,
    token,
    message: "Your password has been successfully reset",
  });
});

/**
 * @desc    Get current user
 * @route   GET /api/v1/auth/me
 * @access  Private
 */  
exports.getMe = asyncHandler(async (req, res, next) => {
  const user = await User.findById(req.user._id);
  delete user._doc.password;
  res.status(200).json({ data: user });
});

/**
 * @desc    Update current user
 * @route   PUT /api/v1/auth/update-me
 * @access  Private
 */
exports.updateMe = asyncHandler(async (req, res, next) => {
  const filteredBody = {};
  const profileFields = [
    "firstName",
    "lastName",
    "phone",
    "avatar",
    "dateOfBirth",
  ];
  const addressFields = ["street", "city", "state", "country", "zipCode"];

  profileFields.forEach((field) => {
    if (req.body[field] !== undefined) {
      filteredBody[`profile.${field}`] = req.body[field];
    }
  });

  addressFields.forEach((field) => {
    if (req.body[field] !== undefined) {
      filteredBody[`address.${field}`] = req.body[field];
    }
  });

  const updatedUser = await User.findByIdAndUpdate(req.user._id, filteredBody, {
    new: true,
    runValidators: true,
  });

  delete updatedUser._doc.password;

  res.status(200).json({ data: updatedUser });
});

/**
 * @desc    Update logged user password
 * @route   PUT /api/v1/auth/update-my-password
 * @access  Private
 */
exports.updatePassword = asyncHandler(async (req, res, next) => {
  const salt = await bcrypt.genSalt(10);
  const hashedPassword = await bcrypt.hash(req.body.password, salt);

  const newData = {
    password: hashedPassword,
    passwordChangedAt: Date.now(),
  };

  const user = await User.findOneAndUpdate({ _id: req.user._id }, newData, {
    new: true,
  });

  const token = createToken(user._id);
  await Email.passwordChanged(user);

  delete user._doc.password;

  res.status(200).json({ data: user, token });
});

/**
 * @desc    Delete logged user (deactivate)
 * @route   DELETE /api/v1/auth/delete-me
 * @access  Private
 */
exports.deleteMe = asyncHandler(async (req, res, next) => {
  await User.findByIdAndUpdate(req.user._id, { isActive: false });
  await Email.accountDeactivated(req.user);

  res.status(204).json({
    status: "success",
    data: null,
  });
});

/**
 * @desc    Get all users (Admin only)
 * @route   GET /api/v1/user
 * @access  Private/Admin
 */
exports.getAllUsers = asyncHandler(async (req, res, next) => {
  const users = await User.find();

  res.status(200).json({
    results: users.length,
    data: users,
  });
});

/**
 * @desc    Get user by ID (Admin only)
 * @route   GET /api/v1/user/:id
 * @access  Private/Admin
 */
exports.getUser = asyncHandler(async (req, res, next) => {
  const user = await User.findById(req.params.id);

  if (!user) {
    return next(
      new ApiError(`No user found with that ID : ${req.params.id}`, 404)
    );
  }
  delete user._doc.password;
  res.status(200).json({ data: user });
});

/**
 * @desc    Update user (Admin only)
 * @route   Patch /api/v1/user/:id
 * @access  Private/Admin
 */
exports.updateUser = asyncHandler(async (req, res, next) => {
  const user = await User.findById(req.params.id);

  if (!user) {
    return next(
      new ApiError(`No user found with that ID : ${req.params.id}`, 404)
    );
  }
  const wasInactive = !user.isActive;
  const allowedFields = ["email", "role", "isActive", "isVerified"];
  const profileFields = [
    "firstName",
    "lastName",
    "phone",
    "avatar",
    "dateOfBirth",
  ];
  const addressFields = ["street", "city", "state", "country", "zipCode"];

  allowedFields.forEach((field) => {
    if (req.body[field] !== undefined) {
      user[field] = req.body[field];
    }
  });
  profileFields.forEach((field) => {
    if (req.body[field] !== undefined) {
      user.profile[field] = req.body[field];
    }
  });
  addressFields.forEach((field) => {
    if (req.body[field] !== undefined) {
      user.address[field] = req.body[field];
    }
  });

  if (req.body.password) {
    const salt = await bcrypt.genSalt(10);
    user.password = await bcrypt.hash(req.body.password, salt);
    user.passwordChangedAt = Date.now();
  }

  await user.save();

  if (req.body.password) {
    await Email.passwordChanged(user);
  }

  if (wasInactive && user.isActive) {
    await Email.accountActivated(user);
  }

  if (!wasInactive && !user.isActive) {
    await Email.accountDeactivated(user);
  }
  delete user._doc.password;
  res.status(200).json({ data: user });
});

/**
 * @desc    Delete user (Admin only) (deactivate)
 * @route   DELETE /api/v1/user/:id 6924a834fe07c99e95fedb9f
 * @access  Private/Admin
 */
exports.deleteUser = asyncHandler(async (req, res, next) => {
  const user = await User.findByIdAndUpdate(req.params.id, { isActive: false });

  if (!user) {
    return next(
      new ApiError(`No user found with that ID : ${req.params.id}`, 404)
    );
  }

  if (!user.isActive) {
    return next(new ApiError("This user account is already deactivated.", 400));
  }

  await Email.accountDeactivated(user);

  res.status(204).json({
    status: "success",
    data: null,
  });
});
