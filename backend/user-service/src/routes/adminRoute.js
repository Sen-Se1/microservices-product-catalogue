const express = require("express");
const router = express.Router();
const {
  getUserValidator,
  updateUserAdminValidator,
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
  // updateUserAdminValidator,
  isProfileOwner,
  updateUser
);
router.patch(
  "/user/:id/password",
  protect,
  allowedTo("admin"),
  // updateUserAdminValidator,
  isProfileOwner,
  updateUserPassword
);
router.patch(
  "/user/:id/toggle-status",
  protect,
  allowedTo("admin"),
  // updateUserAdminValidator,
  isProfileOwner,
  toggleUserStatus
);

module.exports = router;
