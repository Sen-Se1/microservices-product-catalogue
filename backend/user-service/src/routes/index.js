const adminRoute = require("./adminRoute");
const userRoute = require("./userRoute");

const mountRoutes = (app) => {
  app.use("/api/v1/admin", adminRoute);
  app.use("/api/v1/auth", userRoute);
};

module.exports = mountRoutes;
