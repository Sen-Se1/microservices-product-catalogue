const asyncHandler = require("express-async-handler");
const Email = require("../utils/emailTemplate");
const ApiError = require("../utils/apiError");
const User = require("../models/userModel");

/**
 * @desc    Get all users (Admin only)
 * @route   GET /api/v1/user
 * @access  Private/Admin
 */
exports.getAllUsers = asyncHandler(async (req, res, next) => {
  const page = parseInt(req.query.page, 10) || 1;
  const limit = parseInt(req.query.limit, 10) || 10;
  const skip = (page - 1) * limit;

  const users = await User.find()
    .skip(skip)
    .limit(limit)
    .sort({ createdAt: -1 });

  const totalUsers = await User.countDocuments();
  const totalPages = Math.ceil(totalUsers / limit);

  res.status(200).json({
    status: "success",
    results: users.length,
    pagination: {
      currentPage: page,
      limit,
      totalPages,
      totalUsers,
      hasNextPage: page < totalPages,
      hasPrevPage: page > 1,
    },
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

  if (!user)
    return next(
      new ApiError(`No user found with that ID: ${req.params.id}`, 404)
    );

  res.status(200).json({
    status: "success",
    data: user,
  });
});

/**
 * @desc    Update user (Admin only)
 * @route   Patch /api/v1/user/:id/profile
 * @access  Private/Admin
 */
exports.updateUser = asyncHandler(async (req, res, next) => {
  const user = await User.findById(req.params.id);

  if (!user)
    return next(new ApiError(`No user found with ID: ${req.params.id}`, 404));

  const allowedFields = ["email", "role", "isVerified"];
  const profileFields = ["firstName", "lastName", "phone", "dateOfBirth"];
  const addressFields = ["street", "city", "state", "country", "zipCode"];

  allowedFields.forEach((field) => {
    if (req.body[field] !== undefined) user[field] = req.body[field];
  });

  profileFields.forEach((field) => {
    if (req.body[field] !== undefined) user.profile[field] = req.body[field];
  });

  addressFields.forEach((field) => {
    if (req.body[field] !== undefined) user.address[field] = req.body[field];
  });

  await user.save({ validateBeforeSave: false });

  res.status(200).json({
    status: "success",
    data: user,
  });
});

/**
 * @desc    Reset/Update user password (Admin only)
 * @route   PATCH /api/v1/user/:id/password
 * @access  Private/Admin
 */
exports.updateUserPassword = asyncHandler(async (req, res, next) => {
  const user = await User.findById(req.params.id);
  if (!user)
    return next(new ApiError(`No user found with ID: ${req.params.id}`, 404));

  user.password = req.body.password;
  user.passwordChangedAt = Date.now();
  await user.save({ validateBeforeSave: false });
  user.password = undefined;
  await Email.passwordChanged(user);

  res.status(200).json({
    status: "success",
    message: "Password updated successfully",
  });
});

/**
 * @desc    Toggle user active/inactive status (Admin only)
 * @route   PATCH /api/v1/user/:id/toggle-status
 * @access  Private/Admin
 */
exports.toggleUserStatus = asyncHandler(async (req, res, next) => {
  const user = await User.findById(req.params.id);
  console.log('user', user);
  
  if (!user)
    return next(new ApiError(`No user found with ID: ${req.params.id}`, 404));
  user.isActive = !user.isActive;
  await user.save({ validateBeforeSave: false });

  if (user.isActive) {
    await Email.accountActivated(user);
  } else {
    await Email.accountDeactivated(user);
  }

  res.status(200).json({
    status: "success",
    message: `User account has been ${
      user.isActive ? "activated" : "deactivated"
    } successfully.`,
    data: {
      id: user._id,
      isActive: user.isActive,
    },
  });
});
