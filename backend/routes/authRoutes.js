const express = require("express");
const authRouter = express.Router();
const authController = require("../controllers/authController");
const { protect, authorize } = require("../middleware/auth");

// Public routes
authRouter.post("/register", authController.register);
authRouter.post("/login", authController.login);

// Protected routes
authRouter.get("/me", protect, authController.getMe);
authRouter.put("/profile", protect, authController.updateProfile);

// Admin only routes (example)
// authRouter.get("/users", protect, authorize('admin'), authController.getAllUsers);

module.exports = authRouter;
