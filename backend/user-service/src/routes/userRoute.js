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
} = require("../controllers/userController");
const { protect } = require("../middleware/authMiddleware");

router.post("/register", register);
router.put("/verify-email/:token", verifyEmail);
router.post("/resend-verification-email", resendVerificationEmail);
router.post("/login", login);
router.post('/forgotPassword', forgotPassword);
router.put('/resetPassword/:token', resetPassword);
router.get("/me", protect, getMe);
router.put("/update-me", protect, updateMe);
router.put("/update-my-password", protect, updatePassword);
router.delete("/delete-me", protect, deleteMe);

module.exports = router;
