const express = require("express");
const router = express.Router();
const {
  registerValidator,
  verifyEmailValidator,
  resendVerificationValidator,
  loginValidator,
  forgotPasswordValidator,
  resetPasswordValidator,
  updateMeValidator,
  updatePasswordValidator,
} = require("../utils/validators/userValidator");
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

router.post("/register", registerValidator, register);
router.put("/verify-email/:token", verifyEmailValidator, verifyEmail);
router.post(
  "/resend-verification-email",
  resendVerificationValidator,
  resendVerificationEmail
);
router.post("/login", loginValidator, login);
router.post("/forgotPassword", forgotPasswordValidator, forgotPassword);
router.put("/resetPassword/:token", resetPasswordValidator, resetPassword);
router.get("/me", protect, getMe);
router.put("/update-me", protect, updateMeValidator, updateMe);
router.put("/update-my-password", protect, updatePasswordValidator, updatePassword);
router.delete("/delete-me", protect, deleteMe);

module.exports = router;
