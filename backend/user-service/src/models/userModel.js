const mongoose = require("mongoose");

const userSchema = new mongoose.Schema(
  {
    email: {
      type: String,
      required: [true, "Email address is required."],
      unique: [true, "Email address must be unique."],
      lowercase: true,
      trim: true,
    },
    password: {
      type: String,
      required: [true, 'Password is required.'],
      minlength: [8, 'Password is too short.'],
    },
    role: {
      type: String,
      required: [true, 'Role is required.'],
      enum: ['admin', 'user'],
      default: 'user',
      trim: true,
    },
    profile: {
      firstName: {
        type: String,
        trim: true,
      },
      lastName: {
        type: String,
        trim: true,
      },
      phone: {
        type: String,
        trim: true,
      },
      avatar: String,
      dateOfBirth: Date,
    },
    address: {
      street: {
        type: String,
        trim: true,
      },
      city: {
        type: String,
        trim: true,
      },
      state: {
        type: String,
        trim: true,
      },
      country: {
        type: String,
        trim: true,
      },
      zipCode: {
        type: String,
        trim: true,
      },
    },
    isActive: { 
      type: Boolean, 
      default: true 
    },
    isVerified: { 
      type: Boolean, 
      default: false 
    },
    lastLogin: Date,
    emailVerificationToken: String,
    emailVerificationTokenExpires: Date,
    passwordChangedAt: Date,
    passwordResetToken: String,
    passwordResetTokenExpires: Date,
  },
  {
    timestamps: true,
    versionKey: false
  }
);

userSchema.index({ email: 1 }, { unique: true });
userSchema.index({ role: 1 });
userSchema.index({ isActive: 1 });

// Create model based on the schema
const User = mongoose.model("User", userSchema);

module.exports = User;