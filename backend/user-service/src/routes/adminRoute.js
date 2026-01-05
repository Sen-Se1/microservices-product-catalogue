const express = require("express");
const router = express.Router();
const {
  getUserValidator,
  updateUserAdminValidator,
  deleteUserValidator,
} = require("../utils/validators/adminValidator");
const {
  getUser,
  getAllUsers,
  updateUser,
  deleteUser,
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
  "/user/:id",
  protect,
  allowedTo("admin"),
  updateUserAdminValidator,
  isProfileOwner,
  updateUser
);
router.delete(
  "/user/:id",
  protect,
  allowedTo("admin"),
  deleteUserValidator,
  isProfileOwner,
  deleteUser
);

module.exports = router;
