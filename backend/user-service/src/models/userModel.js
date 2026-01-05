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
      required: [true, "Password is required."],
      minlength: [8, "Password is too short."],
    },
    role: {
      type: String,
      required: [true, "Role is required."],
      enum: ["admin", "user"],
      default: "user",
      trim: true,
    },
    profile: {
      firstName: {
        type: String,
        required: [true, "First name is required."],
        trim: true,
      },
      lastName: {
        type: String,
        required: [true, "Last name is required."],
        trim: true,
      },
      phone: {
        type: String,
        required: [true, "Phone number is required."],
        trim: true,
      },
      avatar: {
        type: String,
        required: [true, "avatar is required."],
        default: "./media/users/default-avatar.jpg",
        trim: true,
      },
      dateOfBirth: Date,
    },
    address: {
      street: {
        type: String,
        required: [true, "Street is required."],
        trim: true,
      },
      city: {
        type: String,
        required: [true, "City is required."],
        trim: true,
      },
      state: {
        type: String,
        required: [true, "State is required."],
        trim: true,
      },
      country: {
        type: String,
        required: [true, "Country is required."],
        trim: true,
      },
      zipCode: {
        type: String,
        required: [true, "Zip code is required."],
        trim: true,
      },
    },
    isActive: {
      type: Boolean,
      default: true,
    },
    isVerified: {
      type: Boolean,
      default: false,
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
    versionKey: false,
  }
);

userSchema.index({ email: 1 }, { unique: true });
userSchema.index({ role: 1 });
userSchema.index({ isActive: 1 });

// Create model based on the schema
const User = mongoose.model("User", userSchema);

module.exports = User;
