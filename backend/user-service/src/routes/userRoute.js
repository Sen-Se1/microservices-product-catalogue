const express = require("express");
const router = express.Router();
const {
  register,
  verifyEmail,
  resendVerificationEmail,
  login,
  forgotPassword,
  resetPassword,
  getMe,
  updateMe,
  updatePassword,
  deleteMe,
  getUser,
  getAllUsers,
  updateUser,
  deleteUser
} = require("../controllers/userController");
const { protect, allowedTo, isProfileOwner } = require("../middleware/authMiddleware");

router.post("/auth/register", register);
router.put("/auth/verify-email/:token", verifyEmail);
router.post("/auth/resend-verification-email", resendVerificationEmail);
router.post("/auth/login", login);
router.post('/auth/forgotPassword', forgotPassword);
router.put('/auth/resetPassword/:token', resetPassword);
router.get("/auth/me", protect, getMe);
router.put("/auth/update-me", protect, updateMe);
router.put("/auth/update-my-password", protect, updatePassword);
router.delete("/auth/delete-me", protect, deleteMe);
router.get("/user", protect, allowedTo("admin"), getAllUsers);
router.get("/user/:id", protect, allowedTo("admin"), isProfileOwner, getUser);
router.patch("/user/:id", protect, allowedTo("admin"), isProfileOwner, updateUser);
router.delete("/user/:id", protect, allowedTo("admin"), isProfileOwner, deleteUser);

module.exports = router;
