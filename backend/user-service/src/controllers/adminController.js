const asyncHandler = require("express-async-handler");
const bcrypt = require("bcryptjs");
const Email = require("../utils/emailTemplate");
const ApiError = require("../utils/apiError");
const User = require("../models/userModel");

/**
 * @desc    Get all users (Admin only)
 * @route   GET /api/v1/user
 * @access  Private/Admin
 */
exports.getAllUsers = asyncHandler(async (req, res, next) => {
  const users = await User.find().select("-password");

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
  const profileFields = ["firstName", "lastName", "phone", "dateOfBirth"];
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

  await user.save({ validateBeforeSave: false });

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
 * @route   DELETE /api/v1/user/:id
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
