const express = require("express");
const router = express.Router();
const {
  getUserValidator,
  updateUserAdminValidator,
  updateUserPasswordValidator,
  toggleUserStatusValidator,
} = require("../utils/validators/adminValidator");
const {
  getUser,
  getAllUsers,
  updateUser,
  updateUserPassword,
  toggleUserStatus,
} = require("../controllers/adminController");
const {
  protect,
  allowedTo,
  isProfileOwner,
} = require("../middleware/authMiddleware");
const { authLimiter } = require("../utils/rateLimiter");

router.get("/user", protect, allowedTo("admin"), getAllUsers);
router.get(
  "/user/:id",
  protect,
  allowedTo("admin"),
  getUserValidator,
  isProfileOwner,
  getUser
);
router.patch(
  "/user/:id/profile",
  protect,
  allowedTo("admin"),
  updateUserAdminValidator,
  isProfileOwner,
  updateUser
);
router.patch(
  "/user/:id/password",
  protect,
  allowedTo("admin"),
  authLimiter,
  updateUserPasswordValidator,
  isProfileOwner,
  updateUserPassword
);
router.patch(
  "/user/:id/toggle-status",
  protect,
  allowedTo("admin"),
  toggleUserStatusValidator,
  isProfileOwner,
  toggleUserStatus
);

module.exports = router;
