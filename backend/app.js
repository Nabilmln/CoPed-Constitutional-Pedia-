const express = require("express");
const cors = require("cors");
require("dotenv").config();

// Import database connection
const connectDB = require("./config/database");

// Import routes
const authRouter = require("./routes/authRoutes");

const app = express();

// MIDDLEWARE

// CORS configuration
app.use(
  cors({
    origin: process.env.ALLOWED_ORIGINS?.split(",") || [
      "http://localhost:3000",
    ],
    credentials: true,
    methods: ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allowedHeaders: ["Content-Type", "Authorization"],
  })
);

// Body parser middleware
app.use(express.json({ limit: "10mb" }));
app.use(express.urlencoded({ extended: true, limit: "10mb" }));

// Request logging middleware
app.use((req, res, next) => {
  console.log(`${new Date().toISOString()} - ${req.method} ${req.path}`);
  next();
});

// ================================
// ROUTES
// ================================

// Health check route
app.get("/", (req, res) => {
  res.json({
    success: true,
    message: "CoPed Constitutional Pedia API Server",
    version: "1.0.0",
    timestamp: new Date().toISOString(),
    environment: process.env.NODE_ENV || "development",
    endpoints: {
      auth: "/api/auth",
      health: "/api/health",
    },
  });
});

// API routes
app.use("/api/auth", authRouter);

// Health check endpoint
app.get("/api/health", (req, res) => {
  res.json({
    success: true,
    message: "Server is healthy",
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    memory: process.memoryUsage(),
    database: "Connected to MongoDB Atlas",
  });
});

// ================================
// ERROR HANDLING
// ================================

// 404 handler
app.use("*", (req, res) => {
  res.status(404).json({
    success: false,
    message: `Route ${req.originalUrl} not found`,
    availableRoutes: [
      "GET /",
      "GET /api/health",
      "POST /api/auth/register",
      "POST /api/auth/login",
    ],
  });
});

// Global error handler
app.use((err, req, res, next) => {
  console.error("🔴 Error:", err.stack);

  // Mongoose validation error
  if (err.name === "ValidationError") {
    const errors = Object.values(err.errors).map((val) => val.message);
    return res.status(400).json({
      success: false,
      message: "Validation Error",
      errors,
    });
  }

  // Mongoose duplicate key error
  if (err.code === 11000) {
    const field = Object.keys(err.keyValue);
    return res.status(400).json({
      success: false,
      message: `Duplicate field value: ${field}. Please use another value.`,
    });
  }

  // JWT errors
  if (err.name === "JsonWebTokenError") {
    return res.status(401).json({
      success: false,
      message: "Invalid token",
    });
  }

  // Default error
  res.status(err.statusCode || 500).json({
    success: false,
    message: err.message || "Server Error",
    ...(process.env.NODE_ENV === "development" && { stack: err.stack }),
  });
});

// ================================
// SERVER STARTUP
// ================================

const startServer = async () => {
  try {
    // Connect to MongoDB Atlas
    await connectDB();

    // Start server
    const PORT = process.env.PORT || 5000;

    app.listen(PORT, () => {
      console.log("🚀 ================================");
      console.log(`🚀 CoPed Backend Server Started!`);
      console.log(`🌐 Server running on port ${PORT}`);
      console.log(`📍 Local URL: http://localhost:${PORT}`);
      console.log(`🔧 Environment: ${process.env.NODE_ENV || "development"}`);
      console.log(`📊 API Documentation: http://localhost:${PORT}/api/health`);
      console.log("🚀 ================================");
    });
  } catch (error) {
    console.error("❌ Failed to start server:", error.message);
    process.exit(1);
  }
};

// Handle unhandled promise rejections
process.on("unhandledRejection", (err, promise) => {
  console.error("🔴 Unhandled Promise Rejection:", err.message);
  process.exit(1);
});

// Handle uncaught exceptions
process.on("uncaughtException", (err) => {
  console.error("🔴 Uncaught Exception:", err.message);
  process.exit(1);
});

// Start the server
startServer();
