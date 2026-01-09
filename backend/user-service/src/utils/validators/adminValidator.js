const { body, param } = require("express-validator");
const validator = require("validator");
const validatorMiddleware = require("../../middleware/validatorMiddleware");

const mongoIdStep = param("id")
  .isMongoId()
  .withMessage("The user ID format is invalid.");

exports.getUserValidator = [mongoIdStep, validatorMiddleware];

exports.updateUserAdminValidator = [
  mongoIdStep,

  body("email")
    .optional()
    .isEmail()
    .withMessage("Invalid email format.")
    .normalizeEmail(),

  body("role").optional().isIn(["admin", "user"]).withMessage("Invalid role."),

  body("isVerified")
    .optional()
    .isBoolean()
    .withMessage("isVerified must be true or false."),

  body(["firstName", "lastName", "city", "state"])
    .optional()
    .trim()
    .notEmpty()
    .escape(),

  body("phone").optional().isMobilePhone("any", { strictMode: true }),

  body("country").optional().isISO31661Alpha2().toUpperCase(),

  body("zipCode")
    .optional()
    .custom((value, { req }) => {
      const country = req.body.country || "any";
      if (!validator.isPostalCode(value, country)) {
        throw new Error(`Invalid zip code for ${country}`);
      }
      return true;
    }),

  validatorMiddleware,
];

exports.updateUserPasswordValidator = [
  mongoIdStep,

  body("password")
    .notEmpty()
    .withMessage("New password is required.")
    .isStrongPassword({
      minLength: 8,
      minLowercase: 1,
      minUppercase: 1,
      minNumbers: 1,
      minSymbols: 1,
    })
    .withMessage("New password is too weak."),

  body("passwordConfirm")
    .notEmpty()
    .withMessage("Password confirmation is required.")
    .custom((val, { req }) => {
      if (val !== req.body.password) {
        throw new Error("Passwords do not match.");
      }
      return true;
    }),

  validatorMiddleware,
];

exports.toggleUserStatusValidator = [mongoIdStep, validatorMiddleware];
