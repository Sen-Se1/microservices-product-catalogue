const { body, param } = require("express-validator");
const validator = require("validator");
const validatorMiddleware = require("../../middleware/validatorMiddleware");

exports.getUserValidator = [
  param("id").isMongoId().withMessage("The user ID format is invalid."),

  validatorMiddleware,
];

exports.updateUserAdminValidator = [
  param("id").isMongoId().withMessage("The user ID format is invalid."),

  body("email")
    .optional()
    .isEmail()
    .withMessage("Invalid email format.")
    .normalizeEmail(),

  body("role").optional().isIn(["admin", "user"]).withMessage("Invalid role."),

  body("isActive")
    .optional()
    .isBoolean()
    .withMessage("isActive must be true or false."),

  body("isVerified")
    .optional()
    .isBoolean()
    .withMessage("isVerified must be true or false."),

  body("password")
    .optional()
    .isStrongPassword({
      minLength: 8,
      minLowercase: 1,
      minUppercase: 1,
      minNumbers: 1,
      minSymbols: 1,
    })
    .withMessage("New password is too weak."),

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

exports.deleteUserValidator = [
  param("id").isMongoId().withMessage("The user ID format is invalid."),

  validatorMiddleware,
];
