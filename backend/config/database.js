const mongoose = require("mongoose");
require("dotenv").config();

const connectDB = async () => {
  try {
    console.log("🔄 Connecting to MongoDB Atlas...");
    console.log(`📋 Database Name: ${process.env.DB_NAME || "CoPed"}`);

    const conn = await mongoose.connect(process.env.MONGODB_URI, {
      // Removed deprecated options for newer Mongoose versions
      maxPoolSize: 10, // Maintain up to 10 socket connections
      serverSelectionTimeoutMS: 5000, // Keep trying to send operations for 5 seconds
      socketTimeoutMS: 45000, // Close sockets after 45 seconds of inactivity
    });

    console.log(`✅ MongoDB Atlas Connected Successfully!`);
    console.log(`🔗 Host: ${conn.connection.host}`);
    console.log(`📁 Database: ${conn.connection.name}`);
    console.log(`🌐 Ready State: ${conn.connection.readyState}`);

    return conn;
  } catch (error) {
    console.error("❌ MongoDB Atlas Connection Error:");
    console.error(`   Error: ${error.message}`);

    // Common error solutions
    if (error.message.includes("authentication failed")) {
      console.error(
        "   💡 Solution: Check your username and password in connection string"
      );
    } else if (error.message.includes("network")) {
      console.error(
        "   💡 Solution: Check your internet connection and whitelist your IP"
      );
    } else if (error.message.includes("timeout")) {
      console.error(
        "   💡 Solution: Check if your IP is whitelisted in MongoDB Atlas"
      );
    }

    process.exit(1);
  }
};

// Handle connection events
mongoose.connection.on("connected", () => {
  console.log("🟢 Mongoose connected to MongoDB Atlas");
});

mongoose.connection.on("error", (err) => {
  console.error("🔴 Mongoose connection error:", err);
});

mongoose.connection.on("disconnected", () => {
  console.log("🟡 Mongoose disconnected from MongoDB Atlas");
});

// Handle app termination
process.on("SIGINT", async () => {
  await mongoose.connection.close();
  console.log("MongoDB Atlas connection closed due to app termination");
  process.exit(0);
});

module.exports = connectDB;
