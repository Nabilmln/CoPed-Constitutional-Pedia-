const mongoose = require("mongoose");

const userSchema = new mongoose.Schema(
  {
    name: {
      type: String,
      required: [true, "Please provide a name"],
      trim: true,
      maxlength: [50, "Name cannot exceed 50 characters"],
    },
    email: {
      type: String,
      required: [true, "Please provide an email"],
      unique: true,
      lowercase: true,
      match: [
        /^\w+([.-]?\w+)*@\w+([.-]?\w+)*(\.\w{2,3})+$/,
        "Please provide a valid email",
      ],
    },
    password: {
      type: String,
      required: [true, "Please provide a password"],
      minlength: [6, "Password must be at least 6 characters"],
      select: false, // Don't include password in queries by default
    },
    role: {
      type: String,
      enum: ["user", "admin", "moderator"],
      default: "user",
    },
    lastLogin: {
      type: Date,
      default: Date.now,
    },
    isActive: {
      type: Boolean,
      default: true,
    },
    profile: {
      avatar: String,
      bio: String,
      preferences: {
        ragSystem: {
          type: String,
          enum: ["native", "langchain"],
          default: "native",
        },
        language: {
          type: String,
          default: "id",
        },
        theme: {
          type: String,
          enum: ["light", "dark"],
          default: "light",
        },
        saveHistory: {
          type: Boolean,
          default: true,
        },
      },
    },
    queryHistory: [
      {
        question: String,
        answer: String,
        ragSystem: String,
        accuracy: Number,
        responseTime: Number,
        sources: [String],
        timestamp: { type: Date, default: Date.now },
        userRating: { type: Number, min: 1, max: 5 },
      },
    ],
  },
  {
    timestamps: true,
  }
);

// Index for better query performance
userSchema.index({ email: 1 });
userSchema.index({ role: 1 });
userSchema.index({ "queryHistory.timestamp": -1 });

module.exports = mongoose.model("User", userSchema);
