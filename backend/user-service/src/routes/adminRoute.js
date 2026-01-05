const express = require("express");
const router = express.Router();
const {
  getUser,
  getAllUsers,
  updateUser,
  deleteUser
} = require("../controllers/adminController");
const { protect, allowedTo, isProfileOwner } = require("../middleware/authMiddleware");

router.get("/user", protect, allowedTo("admin"), getAllUsers);
router.get("/user/:id", protect, allowedTo("admin"), isProfileOwner, getUser);
router.patch("/user/:id", protect, allowedTo("admin"), isProfileOwner, updateUser);
router.delete("/user/:id", protect, allowedTo("admin"), isProfileOwner, deleteUser);

module.exports = router;
